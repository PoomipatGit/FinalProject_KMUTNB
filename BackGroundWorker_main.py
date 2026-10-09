import queue
import threading
import time
import json  # Cleaner and safer than pprint for dictionaries


class ConstantTelemetryWorker:

	def __init__(self, shared_data: dict, data_queue: queue.Queue = None):
		self.shared_data = shared_data
		self.data_queue = data_queue
		self.is_running = False
		self.thread = None
		self._last_printed_signature = None

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
				current_package = {
					"mode": self.shared_data.get("mode"),
					"control_sub_mode": self.shared_data.get(
						"control_sub_mode"
					),
					"system_stage": self.shared_data.get("system_stage"),
					"is_running": self.shared_data.get("is_running"),
					"active_sequence_csv": self.shared_data.get(
						"active_sequence_csv"
					),
					"battery_model_file_path": self.shared_data.get(
						"battery_model_file_path"
					),
					"sequence_file_exists": self.shared_data.get(
						"sequence_file_exists"
					),
					"target_voltage": self.shared_data.get("target_voltage"),
					"target_current": self.shared_data.get("target_current"),
					"target_power": self.shared_data.get("target_power"),
					"step_min": self.shared_data.get("step_min"),
					"step_max": self.shared_data.get("step_max"),
					"step_size": self.shared_data.get("step_size"),
					"step_time_sec": self.shared_data.get("step_time_sec"),
					"sim_voltage": self.shared_data.get("sim_voltage"),
					"sim_current": self.shared_data.get("sim_current"),
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
				self.shared_data["dc_voltage"] = 48.05
				self.shared_data["dc_current"] = 5.21
				self.shared_data["dc_power"] = round(48.05 * 5.21, 2)
				self.shared_data["can_status"] = "Connected"
				print(f"Running {t_start:.2f} seconds, Current Telemetry: Voltage={self.shared_data['dc_voltage']}, Current={self.shared_data['dc_current']}, Power={self.shared_data['dc_power']}")
				dt = time.time() - t_start
				sleep_time = 0.01 - dt
				time.sleep(sleep_time if sleep_time > 0 else 0.001)


			except Exception as e:
				print(f"[WORKER ERROR]: {e}")
				time.sleep(0.1)