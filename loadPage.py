import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from basePage import BasePage
import Filemanager


class loadPage(BasePage):
	label_color = "#145374"      # Dark teal/blue
	button_color = "#00334e"
	accent_color = "#5588a3"

	# Supported mode hierarchy
	MODE_HIERARCHY = {
		"Fixed": ["CV", "CC", "CP"],
		"List": ["CV", "CC", "CP"],
		"Step": ["CC", "CV"],
		"Battery Sim": ["CV", "CC", "Ri"]
	}
	AUTO_SEQUENCE_FILES = {
		"Fixed": "Fix_sequence.csv",
		"Step": "Step_sequence.csv",
	}

	def __init__(self, parent, controller=None):
		super().__init__(parent, controller)

		self.active_sequence_path = ""
		self.list_active_sequence_path = ""
		# Battery Sim model file path state
		self.battery_model_file_path = ""
		self.battery_sim_sequence_path = ""

		# Dropdown selection state variables
		self.system_stage_var = tk.StringVar(value="Standby")
		self.category_var = tk.StringVar(value="Fixed")
		self.sub_mode_var = tk.StringVar(value="CV")

		# Fixed & List mode setpoints
		self.set_volt_var = tk.StringVar(value="0.0")
		self.set_curr_var = tk.StringVar(value="-")
		self.set_pwr_var = tk.StringVar(value="-")

		# Step mode setpoints
		self.step_min_var = tk.StringVar(value="0.0")
		self.step_max_var = tk.StringVar(value="10.0")
		self.step_size_var = tk.StringVar(value="1.0")
		self.step_time_var = tk.StringVar(value="1.0")

		# DC & AC Side telemetry display variables
		self.dc_volt_var = tk.StringVar(value="0.00 V")
		self.dc_curr_var = tk.StringVar(value="0.00 A")
		self.dc_pwr_var = tk.StringVar(value="0.00 W")
		self.dc_eff_var  = tk.StringVar(value="0.0 %")
		self.ac_volt_var = tk.StringVar(value="0.00 V")
		self.ac_curr_var = tk.StringVar(value="0.00 A") 
		self.ac_pwr_var  = tk.StringVar(value="0.00 W")
		self.ac_freq_var = tk.StringVar(value="0.00 Hz")

		self.lim_max_volt_var = tk.StringVar(value="60.0")
		self.lim_min_volt_var = tk.StringVar(value="0.0")
		self.lim_src_curr_var = tk.StringVar(value="10.0")
		self.lim_snk_curr_var = tk.StringVar(value="-10.0")
		self.lim_src_pwr_var  = tk.StringVar(value="600.0")
		self.lim_snk_pwr_var  = tk.StringVar(value="-600.0")
		self.lim_max_temp_var = tk.StringVar(value="85.0")
		self.lim_max_energy_var = tk.StringVar(value="1000.0")

		self.time_div_var = tk.StringVar(value="1.0 s")
		self.volt_div_var = tk.StringVar(value="10.0 V")
		self.x_pos_var = tk.StringVar(value="0.0")
		self.y_pos_var = tk.StringVar(value="0.0")
		self.is_plot_frozen = tk.BooleanVar(value=False)

		self.limit_file = Filemanager.get_required_path("limit_sink.json")
		self.load_limits()
		self.ch1_active = tk.BooleanVar(value=True)   
		self.ch2_active = tk.BooleanVar(value=True)   
		self.ch3_active = tk.BooleanVar(value=False)  
		self.ch4_active = tk.BooleanVar(value=False)  

		# Build Main UI Structure
		self.setup_main_containers()
		self.setup_stage_selector()         
		self.setup_control_parameters()    
		self.setup_dc_side_monitor()       
		self.setup_ac_side_monitor()       
		self.setup_limit_parameters()
		self.setup_time_series_plot()
		self.setup_datalogger()            
		self.setup_command_list()         
		self.setup_plot_controls()  
		self.poll_value()        
		# Battery Sim model file path state

		# (At the bottom of sourcePage.__init__)
		self.setup_plot_controls()
		self.load_limits()

		# Ensure default Fix_sequence.csv is resolved & dispatched immediately on boot
		self.update_mode_sequence("Fixed")
		self.apply_parameters()

		self.poll_value()

	def setup_main_containers(self):
			"""Initializes the responsive 5x4 grid container."""
			self.grid_container = tk.Frame(self, bg="#FFFFFF")
			
			# Grid into Row 1 of BasePage (below the Top Status Bar at Row 0)
			self.grid_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

			self.grid_container.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cols")

			# Proportional row heights
			self.grid_container.grid_rowconfigure(0, weight=1, uniform="rows")   # 0.5x height
			self.grid_container.grid_rowconfigure((2, 3, 4), weight=2, uniform="rows")
			self.grid_container.grid_rowconfigure(1, weight=3, uniform="rows")   # 1.5x height

			# Reserved coordinates occupied by custom frames
			reserved_cells = {
				(0, 0), (1, 0),  # Stage selector & Control params
				(0, 1), (1, 1),  # Merged DC Side
				(0, 2), (1, 2),  # Merged AC Side
				(0, 3), (1, 3),
			}

			# Background debug grid
			for row in range(5):
				for col in range(4):
					if (row, col) in reserved_cells:
						continue
					cell_frame = tk.Frame(self.grid_container, bg="#E0E0E0", bd=1, relief="solid")
					cell_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

	def setup_stage_selector(self):
		"""Dropdown selector placed in Row 0, Col 0."""
		self.stage_container = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.stage_container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

		self.stage_container.grid_rowconfigure(0, weight=1)
		self.stage_container.grid_columnconfigure(0, weight=1)
		self.stage_container.grid_columnconfigure(1, weight=0)
		self.stage_container.grid_columnconfigure(2, weight=0)
		self.stage_container.grid_columnconfigure(3, weight=1)

		tk.Label(
			self.stage_container, text="System Stage (src): ",
			font=("Helvetica", 10, "bold"), bg=self.label_color, fg="#FFFFFF"
		).grid(row=0, column=1, sticky="e", padx=(0, 5))

		self.stage_dropdown = ttk.Combobox(
			self.stage_container, textvariable=self.system_stage_var,
			values=["Output", "Ping", "Standby"], state="readonly", width=9, font=("Helvetica", 9, "bold")
		)
		self.stage_dropdown.grid(row=0, column=2, sticky="w")
		self.stage_dropdown.bind("<<ComboboxSelected>>", self.on_stage_change)

	def setup_control_parameters(self):
		"""Control Parameter Box placed in Row 1, Col 0."""
		self.ctrl_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.ctrl_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

		# Header Title
		lbl_title = tk.Label(
			self.ctrl_frame,
			text="Control parameter",
			font=("Helvetica", 9, "bold"),
			bg=self.label_color,
			fg="#FFFFFF"
		)
		lbl_title.pack(side="top", pady=(2, 0))

		# Top Dropdowns Container
		top_sel_frame = tk.Frame(self.ctrl_frame, bg=self.label_color)
		top_sel_frame.pack(side="top", fill="x", padx=6, pady=1)
		top_sel_frame.grid_columnconfigure(0, weight=1)
		top_sel_frame.grid_columnconfigure(1, weight=0)

		# Category Dropdown
		tk.Label(
			top_sel_frame, text="Category :", font=("Helvetica", 8, "bold"),
			bg=self.label_color, fg="#FFFFFF"
		).grid(row=0, column=0, sticky="w", pady=1)

		self.category_dropdown = ttk.Combobox(
			top_sel_frame,
			textvariable=self.category_var,
			values=list(self.MODE_HIERARCHY.keys()),
			state="readonly",
			width=8,
			font=("Helvetica", 8, "bold")
		)
		self.category_dropdown.grid(row=0, column=1, padx=2, pady=1, sticky="w")
		self.category_dropdown.bind("<<ComboboxSelected>>", self.on_category_change)

		# Control Sub-Mode Dropdown
		tk.Label(
			top_sel_frame, text="Control :", font=("Helvetica", 8, "bold"),
			bg=self.label_color, fg="#FFFFFF"
		).grid(row=1, column=0, sticky="w", pady=1)

		self.sub_mode_dropdown = ttk.Combobox(
			top_sel_frame,
			textvariable=self.sub_mode_var,
			values=self.MODE_HIERARCHY["Fixed"],
			state="readonly",
			width=8,
			font=("Helvetica", 8, "bold")
		)
		self.sub_mode_dropdown.grid(row=1, column=1, padx=2, pady=1, sticky="w")
		self.sub_mode_dropdown.bind("<<ComboboxSelected>>", self.on_sub_mode_change)

		# Bottom Sequence Button
		self.btn_seq = tk.Button(
			self.ctrl_frame,
			text="Sequence Config",
			font=("Helvetica", 8, "bold"),
			bg=self.button_color,
			fg="#FFFFFF",
			activebackground=self.accent_color,
			activeforeground="#FFFFFF",
			relief="groove",
			bd=1,
			pady=1,
			cursor="hand2",
			command=self.open_sequence_config
		)
		self.btn_seq.pack(side="bottom", fill="x", padx=6, pady=(1, 3))

		# Dynamic Form Container
		self.form_container = tk.Frame(self.ctrl_frame, bg=self.label_color)
		self.form_container.pack(side="top", fill="both", expand=True, padx=6, pady=0)
		self.render_parameter_inputs()

	# -------------------------------------------------------------------------
	# Merged Display Panels (DC Side & AC Side)
	# -------------------------------------------------------------------------

	def setup_dc_side_monitor(self):
		"""Merged Box (Row 0-1, Col 1) to display DC Side telemetry."""
		self.dc_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.dc_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=2, pady=2)

		# Title Header
		tk.Label(
			self.dc_frame, text="DC Side", font=("Helvetica", 10, "bold"),
			bg=self.label_color, fg="#FFFFFF"
		).pack(side="top", pady=(4, 6))

		# Value Readouts
		readouts_container = tk.Frame(self.dc_frame, bg=self.label_color)
		readouts_container.pack(fill="both", expand=True, padx=8, pady=2)
		readouts_container.grid_columnconfigure((0, 1), weight=1)

		self._build_monitor_row(readouts_container, 0, "Voltage:", self.dc_volt_var)
		self._build_monitor_row(readouts_container, 1, "Current:", self.dc_curr_var)
		self._build_monitor_row(readouts_container, 2, "Power:", self.dc_pwr_var)
		self._build_monitor_row(readouts_container, 3, "Efficiency:", self.dc_eff_var)

	def setup_ac_side_monitor(self):
		"""Merged Box (Row 0-1, Col 2) to display AC Side telemetry."""
		self.ac_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.ac_frame.grid(row=0, column=2, rowspan=2, sticky="nsew", padx=2, pady=2)

		# Title Header
		tk.Label(
			self.ac_frame, text="AC Side", font=("Helvetica", 10, "bold"),
			bg=self.label_color, fg="#FFFFFF"
		).pack(side="top", pady=(4, 6))

		# Value Readouts
		readouts_container = tk.Frame(self.ac_frame, bg=self.label_color)
		readouts_container.pack(fill="both", expand=True, padx=8, pady=2)
		readouts_container.grid_columnconfigure((0, 1), weight=1)

		self._build_monitor_row(readouts_container, 0, "Voltage:", self.ac_volt_var)
		self._build_monitor_row(readouts_container, 1, "Current:", self.ac_curr_var)
		self._build_monitor_row(readouts_container, 2, "Power:",     self.ac_pwr_var)
		self._build_monitor_row(readouts_container, 3, "Frequency:", self.ac_freq_var)

	def _build_monitor_row(self, parent, row_idx, title, var):
		"""Helper to create clean readout rows inside display panels."""
		parent.grid_rowconfigure(row_idx, weight=1)
		tk.Label(
			parent, text=title, font=("Helvetica", 9, "bold"),
			bg=self.label_color, fg="#DCE2E8", anchor="w"
		).grid(row=row_idx, column=0, sticky="w", padx=2, pady=1)

		tk.Label(
			parent, textvariable=var, font=("Helvetica", 9, "bold"),
			bg=self.label_color, fg="#FFFFFF", anchor="e"
		).grid(row=row_idx, column=1, sticky="e", padx=2, pady=1)

	def setup_limit_parameters(self):
		"""Merged Box (Row 0-1, Col 3) for Pos/Neg limits and aligned Temp/Energy with Update button."""
		self.limit_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.limit_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=2, pady=2)

		# Title Header
		tk.Label(
			self.limit_frame, text="Limit parameter", font=("Helvetica", 9, "bold"),
			bg=self.label_color, fg="#FFFFFF"
		).pack(side="top", pady=(2, 1))

		limits_form = tk.Frame(self.limit_frame, bg=self.label_color)
		limits_form.pack(side="top", fill="both", expand=True, padx=4, pady=1)

		# 6-column grid: [Col 0, 1, 2: Left Side (+/Src/Single)] | [Col 3, 4, 5: Right Side (-/Snk/Button)]
		limits_form.grid_columnconfigure((0, 3), weight=1)  # Labels
		limits_form.grid_columnconfigure((1, 4), weight=0)  # Entries
		limits_form.grid_columnconfigure((2, 5), weight=0)  # Units

		# Cell builder for split parameter rows
		def make_cell(row, col_start, label, var, unit):
			tk.Label(limits_form, text=label, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF").grid(row=row, column=col_start, sticky="w", padx=(1, 1), pady=1)
			ent = tk.Entry(limits_form, textvariable=var, width=4, font=("Helvetica", 8, "bold"), justify="center", bd=1)
			ent.grid(row=row, column=col_start + 1, padx=1, pady=1)
			ent.bind("<Return>", lambda e: self.apply_limits())
			ent.bind("<FocusOut>", lambda e: self.apply_limits())
			tk.Label(limits_form, text=unit, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF").grid(row=row, column=col_start + 2, sticky="w", padx=(1, 3), pady=1)

		# Rows 0-4 weights
		for r in range(5):
			limits_form.grid_rowconfigure(r, weight=1)

		# Row 0: Voltage (+ / -)
		make_cell(0, 0, "+V Lim:", self.lim_max_volt_var, "V")
		make_cell(0, 3, "-V Lim:", self.lim_min_volt_var, "V")

		# Row 1: Current (+ / -)
		make_cell(1, 0, "+I Lim:", self.lim_src_curr_var, "A")
		make_cell(1, 3, "-I Lim:", self.lim_snk_curr_var, "A")

		# Row 2: Power (+ / -)
		make_cell(2, 0, "+P Lim:", self.lim_src_pwr_var, "W")
		make_cell(2, 3, "-P Lim:", self.lim_snk_pwr_var, "W")

		# Row 3: Max Temp aligned to the left column (cols 0, 1, 2)
		make_cell(3, 0, "Max Temp:", self.lim_max_temp_var, "°C")

		# Row 4: Max Energy aligned to the left column (cols 0, 1, 2)
		make_cell(4, 0, "Max Engy:", self.lim_max_energy_var, "Wh")

		# Rows 3 & 4 (Right Side): Update Button spanning across columns 3, 4, 5 and rows 3 & 4
		self.btn_update_limits = tk.Button(
			limits_form,
			text="UPDATE",
			font=("Helvetica", 8, "bold"),
			bg=self.button_color,
			fg="#FFFFFF",
			activebackground=self.accent_color,
			activeforeground="#FFFFFF",
			relief="groove",
			bd=2,
			cursor="hand2",
			command=self.update_limits
		)
		self.btn_update_limits.grid(
			row=3, 
			column=3, 
			rowspan=2, 
			columnspan=3, 
			sticky="nsew", 
			padx=(4, 2), 
			pady=(2, 2)
		)

	def apply_limits(self):
		"""Syncs limit thresholds to controller shared data."""
		try:
			limits_data = {
				"max_voltage": float(self.lim_max_volt_var.get()),
				"min_voltage": float(self.lim_min_volt_var.get()),
				"source_current_limit": float(self.lim_src_curr_var.get()),
				"sink_current_limit": float(self.lim_snk_curr_var.get()),
				"source_power_limit": float(self.lim_src_pwr_var.get()),
				"sink_power_limit": float(self.lim_snk_pwr_var.get()),
				"max_temperature": float(self.lim_max_temp_var.get()),
				"max_energy_supplied": float(self.lim_max_energy_var.get())
			}
			print(f"[LIMITS APPLIED]: {limits_data}")
			if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
				self.controller.shared_data.update(limits_data)
		except ValueError:
			print("[ERROR]: Invalid numeric limit entered.")

	def setup_time_series_plot(self):
		# Set bg="#000000" for black background or bg="#FFFFFF" for white background
		self.plot_container = tk.Frame(
			self.grid_container, 
			bg="#000000",          # Black placeholder (change to #FFFFFF if preferred)
			bd=1, 
			relief="solid"
		)
		self.plot_container.grid(
			row=2, 
			column=0, 
			rowspan=3,             # Spans Row 2, Row 3, Row 4 (3 rows)
			columnspan=3,          # Spans Col 0, Col 1, Col 2 (3 columns)
			sticky="nsew", 
			padx=2, 
			pady=2
		)

		# Optional temporary label indicating plot area
		self.plot_placeholder_lbl = tk.Label(
			self.plot_container,
			text="[ Time-Series Plot Area ]",
			font=("Helvetica", 11, "bold"),
			bg="#000000",
			fg="#888888"
		)
		self.plot_placeholder_lbl.pack(expand=True)

	# =========================================================================
	# Grid (2, 3): Log Display (Black Space)
	# =========================================================================
	def setup_datalogger(self):
		"""Container at Row 2, Column 3 for system and telemetry logging."""
		self.log_container = tk.Frame(self.grid_container, bg="#000000", bd=1, relief="solid")
		self.log_container.grid(row=2, column=3, sticky="nsew", padx=2, pady=2)

		# Optional placeholder label inside black space
		tk.Label(
			self.log_container, text="[ System Log Area ]",
			font=("Helvetica", 9, "bold"), bg="#000000", fg="#555555"
		).pack(expand=True)

	# =========================================================================
	# Grid (3, 3): Command List Display (Black Space)
	# =========================================================================
	def setup_command_list(self):
		"""Container at Row 3, Column 3 for displaying active sequence command list."""
		self.cmd_list_container = tk.Frame(self.grid_container, bg="#000000", bd=1, relief="solid")
		self.cmd_list_container.grid(row=3, column=3, sticky="nsew", padx=2, pady=2)

		# Optional placeholder label inside black space
		tk.Label(
			self.cmd_list_container, text="[ Command List Area ]",
			font=("Helvetica", 9, "bold"), bg="#000000", fg="#555555"
		).pack(expand=True)

	# =========================================================================
	# Grid (4, 3): Time-Series Plot Controls & Knobs
	# =========================================================================
	def setup_plot_controls(self):
		self.plot_ctrl_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.plot_ctrl_frame.grid(row=4, column=3, sticky="nsew", padx=2, pady=2)

		# --- Top Control Bar: [CH1] [CH2] [CH3] [CH4] [FREEZE BUTTON] ---
		top_bar = tk.Frame(self.plot_ctrl_frame, bg=self.label_color)
		top_bar.pack(side="top", fill="x", padx=2, pady=(2, 1))

		ch_configs = [
			("CH1", self.ch1_active, "#FFCC00"), # Yellow
			("CH2", self.ch2_active, "#00FFCC"), # Cyan
			("CH3", self.ch3_active, "#FF66CC"), # Pink
			("CH4", self.ch4_active, "#66FF66"), # Green
		]

		# Compact Channel Checkbuttons packed side-by-side
		for label, var, color in ch_configs:
			chk = tk.Checkbutton(
				top_bar, text=label, variable=var, font=("Helvetica", 8, "bold"),
				bg=self.label_color, fg=color, selectcolor="#002233",
				activebackground=self.label_color, activeforeground=color,
				padx=1, pady=0, bd=0, highlightthickness=0,
				command=self.on_channel_toggle
			)
			chk.pack(side="left", padx=1)

		# Freeze Button pinned to the top-right
		self.btn_freeze = tk.Button(
			top_bar, text="❄ Freeze", font=("Helvetica", 7, "bold"),
			bg=self.button_color, fg="#FFFFFF", activebackground="#D9534F",
			activeforeground="#FFFFFF", relief="groove", bd=1, padx=4, pady=0,
			command=self.toggle_freeze
		)
		self.btn_freeze.pack(side="right", padx=(2, 1))

		# --- Interactive Knobs Grid (2x2 Matrix) ---
		knobs_frame = tk.Frame(self.plot_ctrl_frame, bg=self.label_color)
		knobs_frame.pack(side="top", fill="both", expand=True, padx=2, pady=1)
		knobs_frame.grid_columnconfigure((0, 1), weight=1)
		knobs_frame.grid_rowconfigure((0, 1), weight=1)

		# Helper function: Builds side-by-side "Label: Value" scrollable box
		def build_knob(parent, row, col, title, var, on_scroll):
			k_box = tk.Frame(parent, bg="#002233", bd=1, relief="groove")
			k_box.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

			inner = tk.Frame(k_box, bg="#002233")
			inner.pack(expand=True)

			lbl_t = tk.Label(inner, text=f"{title}:", font=("Helvetica", 8, "bold"), bg="#002233", fg="#A0C4DF")
			lbl_t.pack(side="left", padx=(2, 1))

			lbl_v = tk.Label(inner, textvariable=var, font=("Helvetica", 8, "bold"), bg="#002233", fg="#FFFFFF")
			lbl_v.pack(side="left", padx=(1, 2))

			# Mouse-wheel binding for interactive scrolling
			for w in (k_box, inner, lbl_t, lbl_v):
				w.bind("<MouseWheel>", lambda e: on_scroll(1 if e.delta > 0 else -1))
				w.bind("<Button-4>", lambda e: on_scroll(1))
				w.bind("<Button-5>", lambda e: on_scroll(-1))

		self.t_div_steps = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
		self.v_div_steps = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
		self.t_idx = 3  # 1.0 s
		self.v_idx = 4  # 10.0 V

		def scroll_t_div(direction):
			self.t_idx = max(0, min(len(self.t_div_steps) - 1, self.t_idx + direction))
			self.time_div_var.set(f"{self.t_div_steps[self.t_idx]}s")
			self.apply_plot_settings()

		def scroll_v_div(direction):
			self.v_idx = max(0, min(len(self.v_div_steps) - 1, self.v_idx + direction))
			self.volt_div_var.set(f"{self.v_div_steps[self.v_idx]}V")
			self.apply_plot_settings()

		def scroll_x_pos(direction):
			val = round(float(self.x_pos_var.get()) + (direction * 0.5), 1)
			self.x_pos_var.set(str(val))
			self.apply_plot_settings()

		def scroll_y_pos(direction):
			val = round(float(self.y_pos_var.get()) + (direction * 1.0), 1)
			self.y_pos_var.set(str(val))
			self.apply_plot_settings()

		# 4 Knob Boxes: Values positioned directly beside labels
		build_knob(knobs_frame, 0, 0, "T/DIV", self.time_div_var, scroll_t_div)
		build_knob(knobs_frame, 0, 1, "V/DIV", self.volt_div_var, scroll_v_div)
		build_knob(knobs_frame, 1, 0, "X POS", self.x_pos_var, scroll_x_pos)
		build_knob(knobs_frame, 1, 1, "Y POS", self.y_pos_var, scroll_y_pos)

	# =========================================================================
	# Plot Control Logic Handlers
	# =========================================================================
	def toggle_freeze(self):
		"""Toggles plot updating between live streaming and paused/frozen."""
		frozen = not self.is_plot_frozen.get()
		self.is_plot_frozen.set(frozen)
		if frozen:
			self.btn_freeze.config(text="RESUME", bg="#D9534F")
			print("[PLOT]: Stream Frozen")
		else:
			self.btn_freeze.config(text="FREEZE", bg=self.button_color)
			print("[PLOT]: Stream Resumed")

	def on_channel_toggle(self):
		"""Fired when any channel checkbox state changes."""
		channels = {
			"CH1": self.ch1_active.get(),
			"CH2": self.ch2_active.get(),
			"CH3": self.ch3_active.get(),
			"CH4": self.ch4_active.get()
		}
		print(f"[PLOT CHANNELS]: {channels}")

	def apply_plot_settings(self):
		"""Broadcasts scale and position updates to controller/matplotlib renderer."""
		settings = {
			"time_div": self.t_div_steps[self.t_idx],
			"volt_div": self.v_div_steps[self.v_idx],
			"x_pos": float(self.x_pos_var.get()),
			"y_pos": float(self.y_pos_var.get())
		}
		print(f"[PLOT SCALE UPDATED]: {settings}")

	# -------------------------------------------------------------------------
	# Dynamic Input Rendering Logic
	# -------------------------------------------------------------------------

	def render_parameter_inputs(self):
		"""Rebuilds the inner parameter form based on active Category and Sub-Mode."""
		for widget in self.form_container.winfo_children():
			widget.destroy()

		category = self.category_var.get()
		sub_mode = self.sub_mode_var.get()

		if category in ("Fixed", "List", "Battery Sim"):
			self.form_container.grid_columnconfigure(0, weight=1)
			self.form_container.grid_columnconfigure(1, weight=0)
			self.form_container.grid_columnconfigure(2, weight=0)
			for c in (3, 4, 5):
				self.form_container.grid_columnconfigure(c, weight=0)

			self._build_row(self.form_container, 0, "Voltage :", self.set_volt_var, "V")
			self._build_row(self.form_container, 1, "Current :", self.set_curr_var, "A")
			self._build_row(self.form_container, 2, "Power :", self.set_pwr_var, "W")

			if category == "List":
				self._set_field_state(self.entry_v, self.set_volt_var, active=False)
				self._set_field_state(self.entry_i, self.set_curr_var, active=False)
				self._set_field_state(self.entry_p, self.set_pwr_var, active=False)
			else:
				self._set_field_state(self.entry_v, self.set_volt_var, active=(sub_mode in ("CV", "Ri")))
				self._set_field_state(self.entry_i, self.set_curr_var, active=(sub_mode == "CC"))
				self._set_field_state(self.entry_p, self.set_pwr_var, active=(sub_mode == "CP"))

		elif category == "Step":
			self.form_container.grid_columnconfigure((0, 3), weight=1)
			self.form_container.grid_columnconfigure((1, 4), weight=0)
			self.form_container.grid_columnconfigure((2, 5), weight=0)

			unit = "A" if sub_mode == "CC" else "V"

			self._build_step_cell(self.form_container, row=0, col_start=0, label="Min :", var=self.step_min_var, unit=unit)
			self._build_step_cell(self.form_container, row=1, col_start=0, label="Max :", var=self.step_max_var, unit=unit)
			self._build_step_cell(self.form_container, row=0, col_start=3, label="Step :", var=self.step_size_var, unit=unit)
			self._build_step_cell(self.form_container, row=1, col_start=3, label="Time :", var=self.step_time_var, unit="s")

	def _build_step_cell(self, parent, row, col_start, label, var, unit):
		lbl = tk.Label(parent, text=label, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
		lbl.grid(row=row, column=col_start, sticky="w", padx=(2, 1), pady=2)

		entry = tk.Entry(parent, textvariable=var, width=4, font=("Helvetica", 8, "bold"), justify="center", bd=1)
		entry.grid(row=row, column=col_start + 1, padx=1, pady=2)
		entry.bind("<Return>", lambda e: self.apply_parameters())

		unit_lbl = tk.Label(parent, text=unit, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
		unit_lbl.grid(row=row, column=col_start + 2, sticky="w", padx=(1, 4), pady=2)

	def _build_row(self, parent, row_idx, label_text, var, unit_text, is_step=False):
		lbl = tk.Label(parent, text=label_text, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
		lbl.grid(row=row_idx, column=0, sticky="w", pady=0)

		entry = tk.Entry(parent, textvariable=var, width=5, font=("Helvetica", 8, "bold"), justify="center", bd=1)
		entry.grid(row=row_idx, column=1, padx=2, pady=0)
		entry.bind("<Return>", lambda e: self.apply_parameters())

		unit_lbl = tk.Label(parent, text=unit_text, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
		unit_lbl.grid(row=row_idx, column=2, sticky="w", pady=0)

		if not is_step:
			if row_idx == 0:
				self.entry_v = entry
			elif row_idx == 1:
				self.entry_i = entry
			elif row_idx == 2:
				self.entry_p = entry

	def _set_field_state(self, entry_widget, var, active=True, default_val="0.0"):
		if active:
			entry_widget.config(state="normal", bg="#FFFFFF", fg="#000000")
			if var.get() == "-":
				var.set(default_val)
		else:
			entry_widget.config(state="normal")
			var.set("-")
			entry_widget.config(state="disabled", disabledbackground="#90A4AE", disabledforeground="#37474F")

	# -------------------------------------------------------------------------
	# Event Callbacks & Routing
	# -------------------------------------------------------------------------

	def on_category_change(self, event=None):
		category = self.category_var.get()
		available_sub_modes = self.MODE_HIERARCHY.get(category, ["CV"])

		self.sub_mode_dropdown["values"] = available_sub_modes
		self.sub_mode_var.set(available_sub_modes[0])

		button_labels = {
			"Fixed": "Sequence Config",
			"List": "Sequence Config",
			"Step": "Sequence Config",
			"Battery Sim": "Battery Model"
		}
		self.btn_seq.config(text=button_labels.get(category, "Config"))

		self.render_parameter_inputs()
		self.sync_mode_state()

		if category == "List":
			self.open_sequence_config()

	def on_sub_mode_change(self, event=None):
		self.render_parameter_inputs()
		self.sync_mode_state()
	"""
	def apply_parameters(self):
		category = self.category_var.get()
		sub_mode = self.sub_mode_var.get()
		data = {}

		try:
			if category in ("Fixed", "Battery Sim"):
				if sub_mode in ("CV", "Ri"):
					data["target_voltage"] = float(self.set_volt_var.get())
				elif sub_mode == "CC":
					data["target_current"] = float(self.set_curr_var.get())
				elif sub_mode == "CP":
					data["target_power"] = float(self.set_pwr_var.get())

			elif category == "Step":
				data.update({
					"step_min": float(self.step_min_var.get()),
					"step_max": float(self.step_max_var.get()),
					"step_size": float(self.step_size_var.get()),
					"step_time": float(self.step_time_var.get()),
					"step_mode": sub_mode
				})

			print(f"[SETPOINT APPLIED]: Category: {category}, Mode: {sub_mode} -> {data}")
			if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
				self.controller.shared_data.update(data)
		except ValueError:
			print("[ERROR]: Invalid numeric input entered.")
	"""
	def open_sequence_config(self):
		category = self.category_var.get()
		print(f"[CONFIG EVENT]: Opening configuration for {category}")

		if not hasattr(self, "controller") or not self.controller:
			return

		if category == "List":
			# If no active sequence yet, ask user to select it
			if (
				not self.active_sequence_path
				or not os.path.exists(self.active_sequence_path)
			):
				chosen_file = filedialog.askopenfilename(
					parent=self,
					title="Select Active Sequence for List Mode",
					filetypes=[
						("CSV Files (*.csv)", "*.csv"),
						("All Files (*.*)", "*.*"),
					],
				)
				if chosen_file:
					self.set_active_sequence_file(chosen_file)
				return

			# Route to the sequence configuration frame if available
			try:
				self.choose_battery_model_file()
			except Exception:
				self.controller.show_frame("canSequencePage")

		elif category == "Battery Sim":
			self.choose_battery_model_file()

	def choose_battery_model_file(self):
			"""Opens file dialog to select a battery model file (.json) and sends its path."""
			chosen_file = filedialog.askopenfilename(
				parent=self,
				title="Select Battery Model File",
				filetypes=[
					("JSON Files (*.json)", "*.json"),
					("All Files (*.*)", "*.*")
				],
			)
			if chosen_file:
				self.battery_model_file_path = chosen_file
				if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
					self.controller.shared_data["battery_model_file_path"] = chosen_file

				print(f"[BATTERY MODEL SELECTED]: {chosen_file}")
				self.send_battery_sim_mode()

	def sync_mode_state(self):
		cat = self.category_var.get()
		sub = self.sub_mode_var.get()
		if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
			self.controller.shared_data["active_category"] = cat
			self.controller.shared_data["mode"] = cat
			self.controller.shared_data["control_sub_mode"] = sub

	def on_stage_change(self, event=None):
		stage = self.system_stage_var.get()
		if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
			self.controller.shared_data["system_stage"] = stage

	def load_limits(self):
		data = Filemanager.load_json(self.limit_file)
		if data:
			self.lim_max_volt_var.set(str(data.get("max_voltage", "60.0")))
			self.lim_min_volt_var.set(str(data.get("min_voltage", "0.0")))
		self.apply_parameters()

	def update_limits(self):
		"""
		Triggered exclusively by the UPDATE button:
		1. Reads current entries from the screen.
		2. Updates controller shared memory (RAM) for real-time CAN safety.
		3. Writes to Required/limit.json.
		"""

		try:
			limits_data = {
				"pos_voltage_limit": float(self.lim_max_volt_var.get()),
				"neg_voltage_limit": float(self.lim_min_volt_var.get()),
				"pos_current_limit": float(self.lim_src_curr_var.get()),
				"neg_current_limit": float(self.lim_snk_curr_var.get()),
				"pos_power_limit": float(self.lim_src_pwr_var.get()),
				"neg_power_limit": float(self.lim_snk_pwr_var.get()),
				"max_temperature": float(self.lim_max_temp_var.get()),
				"max_energy_supplied": float(self.lim_max_energy_var.get())
			}

			# 1. Update in-memory shared data for the background CAN thread
			if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
				self.controller.shared_data["limits"] = limits_data
				self.controller.shared_data.update(limits_data)

			# 2. Save explicitly to Required/limit.json
			limit_file = Filemanager.get_required_path("limit.json")
			Filemanager.save_json(limit_file, limits_data)

			print(f"[MANUAL LIMIT UPDATE]: Saved to {limit_file.name} -> {limits_data}")

		except ValueError:
			print("[INPUT ERROR]: Please enter valid numeric values for all limit fields.")
		except Exception as e:
			print(f"[ERROR]: Failed to write limit file: {e}")

	def load_limits(self):

		limit_file = Filemanager.get_required_path("limit_source.json")
		data = Filemanager.load_json(limit_file)
		if data:
			self.lim_max_volt_var.set(str(data.get("pos_voltage_limit", "60.0")))
			self.lim_min_volt_var.set(str(data.get("neg_voltage_limit", "0.0")))
			self.lim_src_curr_var.set(str(data.get("pos_current_limit", "10.0")))
			self.lim_snk_curr_var.set(str(data.get("neg_current_limit", "-10.0")))
			self.lim_src_pwr_var.set(str(data.get("pos_power_limit", "600.0")))
			self.lim_snk_pwr_var.set(str(data.get("neg_power_limit", "-600.0")))
			self.lim_max_temp_var.set(str(data.get("max_temperature", "85.0")))
			self.lim_max_energy_var.set(str(data.get("max_energy_supplied", "1000.0")))

			# Push initial values to shared_data so controller has limits on boot
			if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
				self.controller.shared_data["limits"] = data
	def poll_value(self):
		"""Periodically updates the displayed telemetry values from shared_data."""
		if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
			data = self.controller.shared_data

			self.dc_volt_var.set(f"{data.get('dc_voltage', 0.0):.2f}")
			self.dc_curr_var.set(f"{data.get('dc_current', 0.0):.2f}")
			self.dc_pwr_var.set(f"{data.get('dc_power', 0.0):.2f}")
			self.dc_eff_var.set(f"{data.get('dc_efficiency', 0.0):.2f}")

			self.ac_volt_var.set(f"{data.get('ac_voltage', 0.0):.2f}")
			self.ac_curr_var.set(f"{data.get('ac_current', 0.0):.2f}")
			self.ac_pwr_var.set(f"{data.get('ac_power', 0.0):.2f}")
			self.ac_freq_var.set(f"{data.get('ac_frequency', 0.0):.2f}")

		# Schedule the next poll after 500 ms
		self.after(500, self.poll_value)

	def update_mode_sequence(self, category: str):
		if category == "List":
			# 1. First, check if the global app already has an active sequence loaded
			active_path = ""
			if hasattr(self, "controller") and self.controller:
				active_path = self.controller.shared_data.get(
					"active_sequence_path", ""
				)

			# 2. If nothing is set yet, check if sourcePage has a previously opened path
			if not active_path:
				active_path = getattr(self, "list_active_sequence_path", "")

			# 3. If still empty, prompt user or look for a fallback in Required
			if not active_path or not os.path.exists(active_path):
				default_list = os.path.join(
					os.path.dirname(os.path.abspath(__file__)),
					"Required",
					"List_sequence.csv",
				)
				if os.path.exists(default_list):
					active_path = default_list

			self.active_sequence_path = active_path
			print(
				f"[MODE LIST]: Active sequence path set to ->"
				f" '{self.active_sequence_path}'"
			)
			# Retain the user's active sequence path for List mode
			self.active_sequence_path = self.list_active_sequence_path
			print(
				f"[MODE LIST]: Using active sequence -> '{self.active_sequence_path}'"
			)
		elif category == "Battery Sim":
			# Battery Sim Mode: Use manually chosen file if selected; otherwise default
			if (
				self.battery_sim_sequence_path
				and os.path.exists(self.battery_sim_sequence_path)
			):
				self.active_sequence_path = self.battery_sim_sequence_path
			else:
				# Default fallback to Required/Battery_sequence.csv
				filename = self.AUTO_SEQUENCE_FILES.get(
					"Battery Sim", "Battery_sequence.csv"
				)
				base_dir = os.path.dirname(os.path.abspath(__file__))
				self.active_sequence_path = os.path.join(base_dir, "Required", filename)

			print(
				f"From GUI [MODE BATTERY SIM]: Using chosen sequence ->"
				f" '{self.active_sequence_path}'"
			)
		else:
			# Auto-assign from "Required" folder
			filename = self.AUTO_SEQUENCE_FILES.get(category, "")
			if filename:
				if hasattr(Filemanager, "get_required_path"):
					self.active_sequence_path = str(
						Filemanager.get_required_path(filename)
					)
				else:
					base_dir = os.path.dirname(os.path.abspath(__file__))
					self.active_sequence_path = os.path.join(
						base_dir, "Required", filename
					)
			print(
				f"from GUI [MODE {category.upper()}]: Auto-assigned sequence -> '{self.active_sequence_path}'"
			)
	def set_active_sequence_file(self, csv_file_path: str):
		"""Sets active sequence globally and locally, then alerts the worker."""
		self.list_active_sequence_path = csv_file_path
		self.active_sequence_path = csv_file_path

		if hasattr(self, "controller") and self.controller:
			self.controller.shared_data["active_sequence_path"] = csv_file_path

		print(f"[ACTIVE SEQUENCE SET]: {csv_file_path}")
		self.send_list_mode()
	def get_stage_and_sequence(self):
		"""Collects System Stage, Run/Standby state, and Active Sequence file."""
		stage = self.system_stage_var.get()
		return {
			"system_stage": stage,
			"is_running": (stage == "Output"),
			"active_sequence_csv": self.active_sequence_path,
			"sequence_file_exists": bool(
				self.active_sequence_path
				and os.path.exists(self.active_sequence_path)
			),
		}

	# -------------------------------------------------------------------------
	# Mode-Specific Send Functions
	# -------------------------------------------------------------------------
	def send_fixed_mode(self):
		"""Fixed Mode: Sends setpoints + Required/Fix_sequence.csv."""
		base = self.get_stage_and_sequence()
		sub = self.sub_mode_var.get()

		v_val = (
			float(self.set_volt_var.get())
			if sub == "CV" and self.set_volt_var.get() != "-"
			else 0.0
		)
		i_val = (
			float(self.set_curr_var.get())
			if sub == "CC" and self.set_curr_var.get() != "-"
			else 0.0
		)
		p_val = (
			float(self.set_pwr_var.get())
			if sub == "CP" and self.set_pwr_var.get() != "-"
			else 0.0
		)

		payload = {
			**base,
			"mode": "Fixed",
			"control_sub_mode": sub,
			"target_voltage": v_val,
			"target_current": i_val,
			"target_power": p_val,
		}
		self._dispatch_to_worker(payload)

	def send_step_mode(self):

		base = self.get_stage_and_sequence()
		sub = self.sub_mode_var.get()

		payload = {
			**base,
			"mode": "Step",
			"control_sub_mode": sub,
			"step_min": float(self.step_min_var.get()),
			"step_max": float(self.step_max_var.get()),
			"step_size": float(self.step_size_var.get()),
			"step_time_sec": float(self.step_time_var.get()),
			"step_unit": "A" if sub == "CC" else "V",
		}
		self._dispatch_to_worker(payload)

	def send_list_mode(self):
		base = self.get_stage_and_sequence()
		self.update_mode_sequence("List")
		sub = self.sub_mode_var.get()
		payload = {
			**base,
			"mode": "List",
			"control_sub_mode": sub,
			"active_sequence_csv": self.list_active_sequence_path,  # Dynamically loaded active sequence
			"sequence_file_exists": bool(self.active_sequence_path and os.path.exists(self.active_sequence_path)),
		}
		self._dispatch_to_worker(payload)
	
	def send_battery_sim_mode(self):
			"""Sends Battery Sim setpoints, active sequence file, and battery model path."""
			self.update_mode_sequence("Battery Sim")
			base = self.get_stage_and_sequence()
			sub = self.sub_mode_var.get()

			# 1. Pull model path from local variable or global shared_data
			model_path = self.battery_model_file_path
			if not model_path and hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
				model_path = self.controller.shared_data.get("battery_model_file_path", "")
			self.battery_model_file_path = model_path

			# 2. Extract setpoints safely
			v_str = self.set_volt_var.get()
			i_str = self.set_curr_var.get()
			p_str = self.set_pwr_var.get()

			v_val = float(v_str) if sub in ("CV", "Ri") and v_str != "-" else 0.0
			i_val = float(i_str) if sub == "CC" and i_str != "-" else 0.0
			p_val = float(p_str) if sub == "CP" and p_str != "-" else 0.0

			payload = {
				**base,
				"mode": "Battery Sim",
				"active_category": "Battery Sim",
				"control_sub_mode": sub,
				"active_sequence_csv": self.active_sequence_path,
				"battery_model_file_path": model_path,
				"battery_model_exists": bool(model_path and os.path.exists(model_path)),
				"target_voltage": v_val,
				"target_current": i_val,
				"target_power": p_val,
				"sim_voltage": v_val,
				"sim_current": i_val,
			}
			self._dispatch_to_worker(payload)

	def choose_battery_model_file(self):
			"""Opens file dialog to select a battery model file (.json) and sends its path."""
			chosen_file = filedialog.askopenfilename(
				parent=self,
				title="Select Battery Model File",
				filetypes=[
					("JSON Files (*.json)", "*.json"),
					("All Files (*.*)", "*.*")
				],
			)
			if chosen_file:
				self.battery_model_file_path = chosen_file
				if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
					self.controller.shared_data["battery_model_file_path"] = chosen_file
				print(f"[BATTERY MODEL SELECTED]: {chosen_file}")
				self.send_battery_sim_mode()

	# -------------------------------------------------------------------------
	# Dispatch Router & Mode Switch Event
	# -------------------------------------------------------------------------
	def _dispatch_to_worker(self, payload: dict):
		if hasattr(self, "controller") and self.controller:
			self.controller.shared_data.update(payload)
			print(f"FROM GUI : [WORKER DISPATCH]: {payload}")

	def apply_parameters(self):
		category = self.category_var.get()
		dispatch_table = {
			"Fixed": self.send_fixed_mode,
			"Step": self.send_step_mode,
			"List": self.send_list_mode,
			"Battery Sim": self.send_battery_sim_mode,
		}
		func = dispatch_table.get(category)
		if func:
			try:
				func()
			except ValueError as e:
				print(f"[INPUT ERROR]: Invalid numerical input: {e}")

	def on_category_change(self, event=None):
		category = self.category_var.get()
		available_sub_modes = self.MODE_HIERARCHY.get(category, ["CV"])

		self.sub_mode_dropdown["values"] = available_sub_modes
		self.sub_mode_var.set(available_sub_modes[0])

		# Automatically resolve sequence: Fixed/Step get defaults, List keeps active sequence
		self.update_mode_sequence(category)

		button_labels = {
			"Fixed": "Sequence Config",
			"List": "Sequence Config",
			"Step": "Sequence Config",
			"Battery Sim": "Battery Model",
		}
		self.btn_seq.config(text=button_labels.get(category, "Config"))

		self.render_parameter_inputs()
		self.sync_mode_state()
		self.apply_parameters()

		if category == "List":
			self.open_sequence_config()

	def on_stage_change(self, event=None):
		stage = self.system_stage_var.get()
		if hasattr(self, "controller") and self.controller:
			self.controller.shared_data["system_stage"] = stage
		self.apply_parameters()