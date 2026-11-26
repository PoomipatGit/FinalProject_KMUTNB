import queue
import threading
import time
import json  # Cleaner and safer than pprint for dictionaries
import importlib.util
import os
import pandas as pd
import can
import re


def load_driver_class(driver_path: str):
	"""Dynamically loads CanbusProtocol from any selected driver .py file."""
	base_dir = os.path.dirname(os.path.abspath(__file__))
	full_path = driver_path if os.path.isabs(driver_path) else os.path.join(base_dir, driver_path)

	spec = importlib.util.spec_from_file_location("active_can_driver", full_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module.CanbusProtocol

def load_driver_class(driver_path: str):
	"""Dynamically loads CanbusProtocol from any selected driver .py file."""
	base_dir = os.path.dirname(os.path.abspath(__file__))
	full_path = driver_path if os.path.isabs(driver_path) else os.path.join(base_dir, driver_path)

	spec = importlib.util.spec_from_file_location("active_can_driver", full_path)
	module = importlib.util.module_from_spec(spec)
	spec.loader.exec_module(module)
	return module.CanbusProtocol
def encode_voltage_to_can_bytes(value):
    # Apply your protocol's scale and byte order here.
    pass

def encode_current_to_can_bytes(value):
    # Apply your protocol's scale and byte order here.
    pass

VALUE_CONFIG = {
    "DCV": {
        "package_key": "target_voltage",
        "encoder": encode_voltage_to_can_bytes,
    },
    "DCA": {
        "package_key": "target_current",
        "encoder": encode_current_to_can_bytes,
    },
}
class ConstantTelemetryWorker:

	def __init__(self, shared_data: dict, data_queue: queue.Queue = None):
		self.shared_data = shared_data
		self.data_queue = data_queue
		self.is_running = False
		self.thread = None
		self._last_printed_signature = None
		self.background_warning = []
		self.shared_data["background_warning"] = self.background_warning

	def start(self):
		if self.is_running:
			return
		self.is_running = True
		self.thread = threading.Thread(target=self._run_loop, daemon=True)
		self.thread.start()
		print("[GATEWAY]: Constant background worker started.")

	def stop(self):
		self.is_running = False

	def _run_loop(self):
		while self.is_running:
			try:
				t_start = time.time()

				# Package keys from GUI
				# 0. Drain any immediate one-off GUI commands (Stop, Restart, Ping, etc.)
				cmd_q = getattr(self, "command_queue", None)
				if cmd_q is not None:
					while not cmd_q.empty():
						try:
							cmd = cmd_q.get_nowait()
							action = cmd.get("action")

							if action in ("LOAD_DRIVER", "REINIT_CAN"):
								cfg = cmd.get("config") or self.shared_data.get("can_config", {})
								drv_file = cmd.get("driver_file") or cfg.get("driver_file", "canbusprotocal_niuera.py")
								try:
									DriverClass = load_driver_class(drv_file)
									if hasattr(self, "can_driver") and self.can_driver:
										self.can_driver.shutdown()
									self.can_driver = DriverClass(
										channel=cfg.get("interface", "can0"),
										bitrate=int(cfg.get("baudrate_kbps", 250)) * 1000,
									)
									self.shared_data["can_config_feedback"] = f"Loaded driver: {os.path.basename(drv_file)}"
								except Exception as e:
									self.shared_data["can_config_feedback"] = f"Driver load failed: {e}"

							elif action == "DISCONNECT_CAN":
								if hasattr(self, "can_driver") and self.can_driver:
									self.can_driver.shutdown()
								self.shared_data["can_status"] = "Disconnected"
								self.shared_data["can_config_feedback"] = f"Disconnected {cmd.get('interface', '')}"

							elif action == "CAN_PING":
								# Send read/ping frame via self.can_driver
								self.shared_data["can_config_feedback"] = f"Ping sent to {cmd.get('target_id')}"

							elif action == "CAN_CUSTOM_FRAME":
								# Send raw frame using cmd["arbitration_id"], cmd["data"], cmd["is_extended"]
								self.shared_data["can_config_feedback"] = f"Sent frame ID 0x{cmd['arbitration_id']:X}"

							elif action == "EMERGENCY_STOP":
								self.shared_data["is_running"] = False
								self.shared_data["system_stage"] = "Standby"

							cmd_q.task_done()
						except queue.Empty:
							break

				# 1. Package keys from GUI
				current_package = {
					"operation_direction": self.shared_data.get("operation_direction"),
					"mode": self.shared_data.get("mode"),
					"Operation_page": self.shared_data.get("Operation_page"),
					"control_sub_mode": self.shared_data.get("control_sub_mode"),
					"system_stage": self.shared_data.get("system_stage"),
					"is_running": self.shared_data.get("is_running"),
					"active_sequence_csv": self.shared_data.get("active_sequence_csv"),
					"sequence_file_exists": self.shared_data.get("sequence_file_exists"),
					"battery_model_file_path": self.shared_data.get("battery_model_file_path"),
					"battery_model_exists": self.shared_data.get("battery_model_exists"),
					"target_voltage": self.shared_data.get("target_voltage"),
					"target_current": self.shared_data.get("target_current"),
					"target_power": self.shared_data.get("target_power"),
					"step_min": self.shared_data.get("step_min"),
					"step_max": self.shared_data.get("step_max"),
					"step_size": self.shared_data.get("step_size"),
					"step_time_sec": self.shared_data.get("step_time_sec"),
					"sim_voltage": self.shared_data.get("sim_voltage"),
					"sim_current": self.shared_data.get("sim_current"),
					"limits": self.shared_data.get("limits"),
					"battery_test_profile": self.shared_data.get("battery_test_profile"),
					"sim_limits": self.shared_data.get("sim_limits"),
					"target_reactive_power": self.shared_data.get("target_reactive_power"),
					"ac_target_voltage": self.shared_data.get("ac_target_voltage"),
					"ac_target_frequency": self.shared_data.get("ac_target_frequency"),
					"step_total_time_sec": self.shared_data.get("step_total_time_sec"),
					"step_v_cap": self.shared_data.get("step_v_cap"),
				}
				# Only keep values that are present (not None)
				filtered_package = {
					k: v for k, v in current_package.items() if v is not None
				}

				# Print only when incoming package changes
				current_signature = str(filtered_package)
				if current_signature != self._last_printed_signature:
					print(
						"\n================= [WORKER RECEIVED PACKAGE] ================="
					)
					print(json.dumps(filtered_package, indent=4))
					print(
						"==============================================================\n"
					)
					self._last_printed_signature = current_signature

				# Fast loop telemetry updates
				"""
				self.shared_data["dc_voltage"] = 48.05
				self.shared_data["dc_current"] = 5.21
				self.shared_data["dc_power"] = round(48.05 * 5.21, 2)
				self.shared_data["can_status"] = "Connected"
				"""
				if filtered_package["Operation_page"] == "OperationPage":
					self.operation_mode(filtered_package)

				#print(f"Running {t_start:.2f} seconds, Current Telemetry: Voltage={self.shared_data['dc_voltage']}, Current={self.shared_data['dc_current']}, Power={self.shared_data['dc_power']}")
				dt = time.time() - t_start
				sleep_time = 0.01 - dt
				time.sleep(sleep_time if sleep_time > 0 else 0.001)


			except Exception as e:
				print(f"[WORKER ERROR]: {e}")
				time.sleep(0.1)

	def operation_mode(self, filtered_package: dict):
		key = (
			filtered_package.get("mode"),
			filtered_package.get("operation_direction"),
			filtered_package.get("control_sub_mode"),
		)
		dispatch_table = {
			("Fixed", "Source", "CV"): self._handle_fixed_source_cv,
			("Fixed", "Source", "CC"): self._handle_fixed_source_cc,
			("Fixed", "Source", "CP"): self._handle_fixed_source_cp,
			#("Fixed", "Sink (On-Grid)", "CV"): self._handle_fixed_sink_ongrid_cv,
		}

		handler = dispatch_table.get(key)
		if handler:
			handler(filtered_package)
		else:
			print(f"[WARNING]: Unsupported operation combination -> {key}")

	def _handle_fixed_source_cv(self, pkg: dict):
		# Implement logic for Fixed CV Source
		#check all active field if i have all required field or not
		#check file first if the sequence file is correct or not, if not reassign the correct one
		#call df_filler_fixed
			#take sequence file, extract to df, fill the blank with value, translate the default command
				#run_duration value = time to repeat the comman above (cut off at run_duration above)
				#total_run_duration = total time to run the ahole command file above (if not found then loop forever) shut down after done
				#fill in the blank with the HEX value in the target_voltage,target_current,target_power
			#run will be control with background logic

		#call
			#actual can command
		base_dir = os.path.dirname(os.path.abspath(__file__))
		expected_file = "Fixed_src_CV.csv"
		expected_path = os.path.join(base_dir, "Required", expected_file)

		seq_path = pkg.get("active_sequence_csv", "")
		if os.path.basename(str(seq_path)) != expected_file:
			if os.path.basename(str(seq_path)) != expected_file:
				warn_msg = f"Expected '{expected_file}', got '{os.path.basename(str(seq_path))}'. Reassigning to '{expected_file}'."
				print(f"[WARNING]: {warn_msg}")
				self.background_warning.append(warn_msg)
				seq_path = expected_path
				pkg["active_sequence_csv"] = seq_path
				self.shared_data["active_sequence_csv"] = seq_path

		if not os.path.exists(seq_path):
			warn_msg = f"Sequence file '{seq_path}' does not exist!"
			print(f"[WARNING]: {warn_msg}")
			self.background_warning.append(warn_msg)
			return

		df_seq = pd.read_csv(seq_path)
	
		
		pass

	def _handle_fixed_source_cc(self, pkg: dict):
		# Implement logic for Fixed CC Source
		pass

	def _handle_fixed_source_cp(self, pkg: dict):
		# Implement logic for Fixed CP Source
		pass

	def df_filler_fixed(self, df: pd.DataFrame, required_columns: list) -> pd.DataFrame:
		"""Fills missing columns in the DataFrame with default values."""
		for col in required_columns:
			if col not in df.columns:
				df[col] = "-"
		#for col in df.rows
	
		return df

	def fill_xx_placeholders(can_data: str, hex_data: str) -> str:
		tokens = can_data.split()
		hex_bytes = hex_data.split()

		# Validate that each supplied item is one byte of hexadecimal data.
		if any(not re.fullmatch(r"[0-9A-Fa-f]{2}", byte) for byte in hex_bytes):
			raise ValueError("hex_data must contain space-separated 2-digit hex bytes")

		placeholder_positions = [
			index for index, token in enumerate(tokens)
			if token.lower() == "xx"
		]

		if not placeholder_positions:
			raise ValueError("No xx placeholders found in CAN Data")
		if len(hex_bytes) > len(placeholder_positions):
			raise ValueError(
				f"{len(hex_bytes)} bytes do not fit in "
				f"{len(placeholder_positions)} xx placeholders"
			)

		for position, byte in zip(placeholder_positions, hex_bytes):
			tokens[position] = byte.upper()

		return " ".join(tokens)