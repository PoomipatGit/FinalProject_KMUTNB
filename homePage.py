import tkinter as tk
from tkinter import ttk
from basePage import BasePage


class homePage(BasePage):
	label_color = "#8056a5"
	button_color = "#573172"

	def __init__(self, parent, controller=None):
		# 1. Initialize parent BasePage frame
		super().__init__(parent, controller)

		# =====================================================================
		# 2. DEFINE ALL VARIABLES FIRST
		# =====================================================================
		self._displayed_error_count = 0

		# Mode selection variables
		self.mode_options = [
			"Source Mode",
			"Load Mode",
			"Battery Test",
			"Auto Sequence Mode"
		]
		self.selected_mode = tk.StringVar(value=self.mode_options[0])
		self.current_mode_var = tk.StringVar(value="Source Mode (CV)")

		# System status & stage variables
		self.system_stage_var = tk.StringVar(value="Standby")
		self.error_count_var = tk.StringVar(value="2")

		# --- CAN Connection State Variables ---
		self.can_status_var = tk.StringVar(value="Connected")
		self.can_node_name_var = tk.StringVar(value="Bidir_Supply_01")
		self.can_addr_mode_var = tk.StringVar(value="Simple (11-bit)")
		self.can_conn_addr_var = tk.StringVar(value="0x02A3")

		# --- Bidirectional Supply Telemetry Variables ---
		self.supply_op_mode_var = tk.StringVar(value="Sourcing (CV)")
		self.temp_var = tk.StringVar(value="25.0 °C")

		# DC Side Telemetry
		self.dc_volt_var = tk.StringVar(value="0.00 V")
		self.dc_curr_var = tk.StringVar(value="0.00 A")
		self.dc_pwr_var  = tk.StringVar(value="0.00 W")

		# AC Side Telemetry
		self.ac_volt_var = tk.StringVar(value="0.00 V")
		self.ac_curr_var = tk.StringVar(value="0.00 A")
		self.ac_freq_var = tk.StringVar(value="50.00 Hz")

		# =====================================================================
		# 3. CALL SETUP METHODS
		# =====================================================================
		self.setup_main_containers()
		self.setup_welcome_and_stage()
		self.setup_error_warning_panel()
		self.setup_mode_config_panel()
		self.setup_monitor_panel()
		self.setup_log_monitor_panel()

		# =====================================================================
		# 4. START BACKGROUND POLLING LOOP
		# =====================================================================
		self.poll_value()

	# -------------------------------------------------------------------------
	# Layout Builders
	# -------------------------------------------------------------------------

	def setup_main_containers(self):
		self.grid_container = tk.Frame(self, bg="#FFFFFF")
		
		# Place into Row 1 (under the BasePage status bar at Row 0) using .grid()
		self.grid_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=0)

		self.grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
		self.grid_container.grid_rowconfigure((0, 1, 2), weight=1, uniform="equal")

	def setup_welcome_and_stage(self):
		"""Top-Left cell (Row 0, Col 0): Welcome & System Stage."""
		cell_split_frame_TL = tk.Frame(self.grid_container, bg="#ffffff")
		cell_split_frame_TL.grid(row=0, column=0, sticky="nsew")
		cell_split_frame_TL.grid_rowconfigure((0, 1), weight=1)
		cell_split_frame_TL.grid_columnconfigure(0, weight=1)

		welcome_label = tk.Label(
			cell_split_frame_TL,
			text="Welcome",
			font=("Helvetica", 12, "bold"),
			bg=self.label_color,
			fg="white",
			width=30
		)
		welcome_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

		stage_row_container = tk.Frame(cell_split_frame_TL, bg=self.label_color)
		stage_row_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
		stage_row_container.grid_rowconfigure(0, weight=1)
		stage_row_container.grid_columnconfigure((0, 3), weight=1)
		stage_row_container.grid_columnconfigure((1, 2), weight=0)

		lbl_stage_title = tk.Label(
			stage_row_container,
			text="System stage  : ",
			font=("Helvetica", 12, "bold"),
			bg=self.label_color,
			fg="white"
		)
		lbl_stage_title.grid(row=0, column=1, sticky="e")

		self.lbl_stage_value = tk.Label(
			stage_row_container,
			textvariable=self.system_stage_var,
			font=("Helvetica", 12, "bold"),
			bg=self.label_color,
			fg="#eed2d2"
		)
		self.lbl_stage_value.grid(row=0, column=2, sticky="w")

	def setup_error_warning_panel(self):
		"""Mid-Left cell (Row 1, Col 0): Error Counter & Listbox with Click Event."""
		cell_split_frame_ML = tk.Frame(self.grid_container, bg="#ffffff")
		cell_split_frame_ML.grid(row=1, column=0, sticky="nsew")
		cell_split_frame_ML.grid_rowconfigure((0, 1), weight=2)
		cell_split_frame_ML.grid_columnconfigure(0, weight=1)

		error_row_container = tk.Frame(cell_split_frame_ML, bg=self.button_color, cursor="hand2")
		error_row_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
		error_row_container.grid_rowconfigure(0, weight=1)
		error_row_container.grid_columnconfigure((0, 3), weight=1)
		error_row_container.grid_columnconfigure((1, 2), weight=0)

		lbl_error_title = tk.Label(
			error_row_container,
			text="Error Count : ",
			font=("Helvetica", 12, "bold"),
			bg=self.button_color,
			fg="white",
			cursor="hand2"
		)
		lbl_error_title.grid(row=0, column=1, sticky="e")

		self.lbl_error_value = tk.Label(
			error_row_container,
			textvariable=self.error_count_var,
			font=("Helvetica", 12, "bold"),
			bg=self.button_color,
			fg="#ffffff",
			cursor="hand2"
		)
		self.lbl_error_value.grid(row=0, column=2, sticky="w")

		# Click event binding on Error Container and Labels
		trigger_error_event = lambda event: self.print_click("Entire Error Warning Block Area")
		error_row_container.bind("<Button-1>", trigger_error_event)
		lbl_error_title.bind("<Button-1>", trigger_error_event)
		self.lbl_error_value.bind("<Button-1>", trigger_error_event)

		# Error Listbox Container
		list_container = tk.Frame(cell_split_frame_ML, bg="#ffffff")
		list_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=(2, 5))

		scrollbar = tk.Scrollbar(list_container, orient="vertical")
		scrollbar.pack(side="right", fill="y")

		self.error_listbox = tk.Listbox(
			list_container,
			height=3,
			bg="#FFF0F0",
			fg="#CC0000",
			font=("Helvetica", 10),
			bd=1,
			relief="solid",
			yscrollcommand=scrollbar.set,
			selectbackground="#E52222"
		)
		self.error_listbox.pack(side="left", fill="both", expand=True)
		scrollbar.config(command=self.error_listbox.yview)

	def setup_mode_config_panel(self):
		"""Bottom-Left cell (Row 2, Col 0): Mode Navigation."""
		cell_split_frame_BL = tk.Frame(self.grid_container, bg="#ffffff")
		cell_split_frame_BL.grid(row=2, column=0, sticky="nsew")
		cell_split_frame_BL.grid_rowconfigure(0, weight=1)
		cell_split_frame_BL.grid_columnconfigure(0, weight=1)

		mode_config_container = tk.Frame(cell_split_frame_BL, bg=self.button_color)
		mode_config_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
		mode_config_container.grid_rowconfigure((0, 1, 2), weight=1)
		mode_config_container.grid_columnconfigure(0, weight=1)

		# Header
		lbl_config_header = tk.Label(
			mode_config_container,
			text="Config/Monitor Mode :",
			font=("Helvetica", 11, "bold"),
			bg=self.button_color,
			fg="#FFFFFF"
		)
		lbl_config_header.grid(row=0, column=0, pady=(8, 2), sticky="n")

		# Controls Row
		controls_row_frame = tk.Frame(mode_config_container, bg=self.button_color)
		controls_row_frame.grid(row=1, column=0, pady=(2, 8), padx=10, sticky="ew")
		controls_row_frame.grid_columnconfigure(0, weight=1)
		controls_row_frame.grid_columnconfigure(1, weight=0)

		self.mode_dropdown = ttk.Combobox(
			controls_row_frame,
			textvariable=self.selected_mode,
			values=self.mode_options,
			state="readonly",
			font=("Helvetica", 9),
			width=15
		)
		self.mode_dropdown.grid(row=0, column=0, padx=(0, 6), sticky="ew")

		self.btn_go = tk.Button(
			controls_row_frame,
			text="GO",
			font=("Helvetica", 9, "bold"),
			bg="#ffffff",
			fg=self.button_color,
			activebackground="#e0e0e0",
			relief="groove",
			bd=2,
			padx=12,
			command=self.on_go_click
		)
		self.btn_go.grid(row=0, column=1, sticky="e")

		# Current Mode Readout
		current_mode_frame = tk.Frame(mode_config_container, bg=self.button_color)
		current_mode_frame.grid(row=2, column=0, pady=2)

		lbl_mode_title = tk.Label(
			current_mode_frame,
			text="Current Mode : ",
			font=("Helvetica", 10, "bold"),
			bg=self.button_color,
			fg="#FFFFFF"
		)
		lbl_mode_title.grid(row=0, column=0, sticky="e")

		self.lbl_current_mode_val = tk.Label(
			current_mode_frame,
			textvariable=self.current_mode_var,
			font=("Helvetica", 10, "bold"),
			bg=self.button_color,
			fg="#EED2D2"
		)
		self.lbl_current_mode_val.grid(row=0, column=1, sticky="w")

	# =========================================================================
	# System Monitor Panel (Merged Row 0..1, Col 1..2)
	# =========================================================================

	def setup_monitor_panel(self):
		"""Top-Right 2x2 Merged Monitor Area showing CAN Status & Telemetry."""
		monitor_container = tk.Frame(self.grid_container, bg="#ffffff")
		monitor_container.grid(row=0, column=1, rowspan=2, columnspan=2, sticky="nsew")

		self.monitor_frame = tk.Frame(monitor_container, bg="#E2D4F0", bd=1, relief="solid")
		self.monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)

		# Header Title
		lbl_monitor = tk.Label(
			self.monitor_frame,
			text="System Telemetry & CAN Bus Monitor",
			font=("Helvetica", 12, "bold"),
			bg=self.button_color,
			fg="#FFFFFF",
			pady=3
		)
		lbl_monitor.pack(side="top", fill="x")

		# Content Layout
		content_box = tk.Frame(self.monitor_frame, bg="#E2D4F0")
		content_box.pack(fill="both", expand=True, padx=6, pady=6)
		content_box.grid_columnconfigure((0, 1), weight=1, uniform="subcards")
		content_box.grid_rowconfigure(0, weight=1)

		# ---------------------------------------------------------------------
		# Card 1: CAN Connection Status
		# ---------------------------------------------------------------------
		can_card = tk.LabelFrame(
			content_box,
			text=" CAN Communication Status ",
			font=("Helvetica", 10, "bold"),
			bg="#FFFFFF",
			fg=self.button_color,
			bd=1,
			relief="solid",
			padx=6,
			pady=4
		)
		can_card.grid(row=0, column=0, sticky="nsew", padx=(0, 3))
		for r in range(4):
			can_card.grid_rowconfigure(r, weight=1)
		can_card.grid_columnconfigure(0, weight=1)
		can_card.grid_columnconfigure(1, weight=1)

		self._build_field(can_card, 0, "Node Name:", self.can_node_name_var)
		self._build_field(can_card, 1, "Address Mode:", self.can_addr_mode_var)
		self._build_field(can_card, 2, "Conn Address:", self.can_conn_addr_var)

		tk.Label(
			can_card, text="Status:", font=("Helvetica", 9, "bold"),
			bg="#FFFFFF", fg="#573172", anchor="w"
		).grid(row=3, column=0, sticky="w", padx=2, pady=2)

		self.lbl_can_status = tk.Label(
			can_card, textvariable=self.can_status_var, font=("Helvetica", 9, "bold"),
			bg="#28A745", fg="#FFFFFF", padx=6, pady=1
		)
		self.lbl_can_status.grid(row=3, column=1, sticky="w", padx=2, pady=2)

		# ---------------------------------------------------------------------
		# Card 2: Bidirectional Power Supply Telemetry (DC, AC, Temp)
		# ---------------------------------------------------------------------
		supply_card = tk.LabelFrame(
			content_box,
			text=" Bidirectional Supply Data ",
			font=("Helvetica", 10, "bold"),
			bg="#FFFFFF",
			fg=self.button_color,
			bd=1,
			relief="solid",
			padx=6,
			pady=4
		)
		supply_card.grid(row=0, column=1, sticky="nsew", padx=(3, 0))
		supply_card.grid_rowconfigure((0, 1, 2), weight=1)
		supply_card.grid_columnconfigure(0, weight=1)

		# Mode & Temperature Header Sub-row
		mode_box = tk.Frame(supply_card, bg="#F3EEF9")
		mode_box.grid(row=0, column=0, sticky="ew", pady=(0, 3))

		tk.Label(
			mode_box, text="Mode: ", font=("Helvetica", 9, "bold"),
			bg="#F3EEF9", fg=self.button_color
		).pack(side="left", padx=(4, 1))

		tk.Label(
			mode_box, textvariable=self.supply_op_mode_var, font=("Helvetica", 9, "bold"),
			bg="#F3EEF9", fg="#1E7E34"
		).pack(side="left")

		tk.Label(
			mode_box, textvariable=self.temp_var, font=("Helvetica", 9, "bold"),
			bg="#F3EEF9", fg="#D9534F"
		).pack(side="right", padx=(0, 4))

		tk.Label(
			mode_box, text="Temp: ", font=("Helvetica", 9, "bold"),
			bg="#F3EEF9", fg=self.button_color
		).pack(side="right")

		# Split Container: DC Side vs AC Side Readouts
		split_telemetry = tk.Frame(supply_card, bg="#FFFFFF")
		split_telemetry.grid(row=1, column=0, rowspan=2, sticky="nsew")
		split_telemetry.grid_columnconfigure((0, 1), weight=1)
		split_telemetry.grid_rowconfigure(0, weight=1)

		# DC Side Column
		dc_box = tk.Frame(split_telemetry, bg="#F7F9FA", bd=1, relief="groove", padx=4, pady=2)
		dc_box.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
		tk.Label(
			dc_box, text="[ DC Side ]", font=("Helvetica", 8, "bold"),
			bg="#F7F9FA", fg="#145374"
		).pack(side="top", pady=1)

		self._build_readout(dc_box, "V_dc:", self.dc_volt_var)
		self._build_readout(dc_box, "I_dc:", self.dc_curr_var)
		self._build_readout(dc_box, "P_dc:", self.dc_pwr_var)

		# AC Side Column
		ac_box = tk.Frame(split_telemetry, bg="#F7F9FA", bd=1, relief="groove", padx=4, pady=2)
		ac_box.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
		tk.Label(
			ac_box, text="[ AC Side ]", font=("Helvetica", 8, "bold"),
			bg="#F7F9FA", fg="#145374"
		).pack(side="top", pady=1)

		self._build_readout(ac_box, "V_ac:", self.ac_volt_var)
		self._build_readout(ac_box, "I_ac:", self.ac_curr_var)
		self._build_readout(ac_box, "Freq:", self.ac_freq_var)

	def _build_field(self, parent, row_idx, title, var):
		"""Helper to create standardized key-value rows in CAN card."""
		tk.Label(
			parent, text=title, font=("Helvetica", 9, "bold"),
			bg="#FFFFFF", fg="#573172", anchor="w"
		).grid(row=row_idx, column=0, sticky="w", padx=2, pady=1)

		tk.Label(
			parent, textvariable=var, font=("Helvetica", 9),
			bg="#FFFFFF", fg="#000000", anchor="w"
		).grid(row=row_idx, column=1, sticky="w", padx=2, pady=1)

	def _build_readout(self, parent, label_text, var):
		"""Helper to create compact telemetry readouts."""
		row_frame = tk.Frame(parent, bg="#F7F9FA")
		row_frame.pack(fill="x", expand=True, pady=1)
		tk.Label(
			row_frame, text=label_text, font=("Helvetica", 8, "bold"),
			bg="#F7F9FA", fg="#555555"
		).pack(side="left")
		tk.Label(
			row_frame, textvariable=var, font=("Helvetica", 8, "bold"),
			bg="#F7F9FA", fg="#000000"
		).pack(side="right")

	def setup_log_monitor_panel(self):
		"""Bottom-Right 1x2 Merged Log Monitor Area."""
		log_container = tk.Frame(self.grid_container, bg="#ffffff")
		log_container.grid(row=2, column=1, rowspan=1, columnspan=2, sticky="nsew")

		self.log_monitor_frame = tk.Frame(log_container, bg="#C9B3E6", bd=1, relief="solid")
		self.log_monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)

		lbl_log_monitor = tk.Label(
			self.log_monitor_frame, text="Log Monitor", font=("Helvetica", 12, "bold"),
			bg="#C9B3E6", fg="#573172"
		)
		lbl_log_monitor.pack(expand=True)

	# -------------------------------------------------------------------------
	# Logic & Background Polling Loop
	# -------------------------------------------------------------------------

	def poll_value(self):
		"""Queries shared controller dictionary / mock backend periodically."""
		# 1. Update System Stage
		self.system_stage_var.set(get_current_system_stage())

		# 2. Update Error Count & Populate Listbox
		error_log = get_current_error_log()
		latest_error_count = len(error_log)
		self.error_count_var.set(str(latest_error_count))

		if latest_error_count > self._displayed_error_count:
			for new_msg in error_log[self._displayed_error_count:]:
				self.error_listbox.insert(tk.END, f"• {new_msg}")
			self._displayed_error_count = latest_error_count
			self.error_listbox.yview_moveto(1.0)

		# 3. Update Active Mode
		self.current_mode_var.set(get_mode())

		# 4. Pull Shared Data from Controller (if connected)
		if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
			data = self.controller.shared_data
			if "can_status" in data:
				status = data["can_status"]
				self.can_status_var.set(status)
				self.lbl_can_status.config(bg="#28A745" if status == "Connected" else "#DC3545")

			if "can_node_name" in data:
				self.can_node_name_var.set(data["can_node_name"])
			if "can_address" in data:
				self.can_conn_addr_var.set(data["can_address"])

			# Sync Module Temperature
			if "temperature" in data:
				self.temp_var.set(f"{data['temperature']:.1f} °C")

			# Sync DC Telemetry
			if "dc_voltage" in data:
				self.dc_volt_var.set(f"{data['dc_voltage']:.2f} V")
			if "dc_current" in data:
				self.dc_curr_var.set(f"{data['dc_current']:.2f} A")
			if "dc_power" in data:
				self.dc_pwr_var.set(f"{data['dc_power']:.2f} W")

			# Sync AC Telemetry
			if "ac_voltage" in data:
				self.ac_volt_var.set(f"{data['ac_voltage']:.2f} V")
			if "ac_current" in data:
				self.ac_curr_var.set(f"{data['ac_current']:.2f} A")
			if "ac_frequency" in data:
				self.ac_freq_var.set(f"{data['ac_frequency']:.2f} Hz")

		# Repeat every 250ms
		self.after(250, self.poll_value)

	def on_go_click(self):
		from sourcePage import sourcePage
		from batterytest import BatteryTestpage
		from loadPage import loadPage

		choice = self.selected_mode.get()
		print(f"[NAV EVENT]: Navigating to -> {choice}")

		page_map = {
			"Source Mode": sourcePage,
			"Battery Test": BatteryTestpage,
			"Load Mode": loadPage
		}

		if choice in page_map and self.controller:
			self.controller.show_frame(page_map[choice])

	def print_click(self, target_name):
		print(f"[UI EVENT]: User pressed block area linked to -> {target_name}")


# -----------------------------------------------------------------------------
# Standalone Backend Mock Functions
# -----------------------------------------------------------------------------
def get_current_system_stage():
	return "Standby"

def get_current_error_log():
	return [
		"Overcurrent detected",
		"Temperature too high"
	]

def get_mode():
	return "Source Mode (CV)"