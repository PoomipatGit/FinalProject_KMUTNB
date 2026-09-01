import tkinter as tk
from tkinter import ttk
from basePage import BasePage


class loadPage(BasePage):
	label_color = "#145374"    
	button_color = "#00334e"
	accent_color = "#5588a3"

	# Supported mode hierarchy
	MODE_HIERARCHY = {
		"Fixed": ["CV", "CC", "CP"],
		"List": ["CV", "CC", "CP"],
		"Step": ["CC", "CV"],

	}

	def __init__(self, parent, controller=None):
		super().__init__(parent, controller)

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
		self.ac_volt_var = tk.StringVar(value="0.00 V")
		self.ac_curr_var = tk.StringVar(value="0.00 A") 
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
			self.stage_container, text="System Stage (snk): ",
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
		self._build_monitor_row(readouts_container, 2, "Frequency:", self.ac_freq_var)

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
		"""Merged Box (Row 0-1, Col 3) for Max/Min Voltage and Source/Sink Current/Power Limits."""
		self.limit_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
		self.limit_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=2, pady=2)

		# Title Header
		tk.Label(
			self.limit_frame, text="Limit parameter", font=("Helvetica", 9, "bold"),
			bg=self.label_color, fg="#FFFFFF"
		).pack(side="top", pady=(2, 1))

		limits_form = tk.Frame(self.limit_frame, bg=self.label_color)
		limits_form.pack(side="top", fill="both", expand=True, padx=4, pady=1)

		limits_form.grid_columnconfigure((0, 3), weight=1)  # Labels
		limits_form.grid_columnconfigure((1, 4), weight=0)  # Entries
		limits_form.grid_columnconfigure((2, 5), weight=0)  # Units

		def make_cell(row, col_start, label, var, unit):
			tk.Label(limits_form, text=label, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF").grid(row=row, column=col_start, sticky="w", padx=(1, 0), pady=1)
			ent = tk.Entry(limits_form, textvariable=var, width=7, font=("Helvetica", 8, "bold"), justify="center", bd=1)
			ent.grid(row=row, column=col_start + 1, padx=(1,1), pady=1)
			ent.bind("<Return>", lambda e: self.apply_limits())
			tk.Label(limits_form, text=unit, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF").grid(row=row, column=col_start + 2, sticky="w", padx=(1, 2), pady=1)

		def make_center_row(row, label, var, unit):
			center_frame = tk.Frame(limits_form, bg=self.label_color)
			center_frame.grid(row=row, column=0, columnspan=6, pady=1)
			
			tk.Label(center_frame, text=label, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF").pack(side="left", padx=(0, 1))
			ent = tk.Entry(center_frame, textvariable=var, width=8, font=("Helvetica", 8, "bold"), justify="center", bd=1)
			ent.pack(side="left", padx=1)
			ent.bind("<Return>", lambda e: self.apply_limits())
			tk.Label(center_frame, text=unit, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF").pack(side="left", padx=(1, 0))

		for r in range(5):
			limits_form.grid_rowconfigure(r, weight=1)

		# Row 0: Voltage Range (Max on Left, Min on Right)
		make_cell(0, 0, "Max V:", self.lim_max_volt_var, "V")
		make_cell(0, 3, "Min V:", self.lim_min_volt_var, "V")

		# Row 1: Current Limits (Source on Left, Sink on Right)
		make_cell(1, 0, "Src I:", self.lim_src_curr_var, "A")
		make_cell(1, 3, "Snk I:", self.lim_snk_curr_var, "A")

		# Row 2: Power Limits (Source on Left, Sink on Right)
		make_cell(2, 0, "Src P:", self.lim_src_pwr_var, "W")
		make_cell(2, 3, "Snk P:", self.lim_snk_pwr_var, "W")

		# Rows 3 & 4: Centered Boundaries
		make_center_row(3, "Max Temp :", self.lim_max_temp_var, "°C")
		make_center_row(4, "Max Energy :", self.lim_max_energy_var, "Wh")

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

		if category in ("Fixed", "List"):
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
		}
		self.btn_seq.config(text=button_labels.get(category, "Config"))

		self.render_parameter_inputs()
		self.sync_mode_state()

		if category == "List":
			self.open_sequence_config()

	def on_sub_mode_change(self, event=None):
		self.render_parameter_inputs()
		self.sync_mode_state()

	def apply_parameters(self):
		category = self.category_var.get()
		sub_mode = self.sub_mode_var.get()
		data = {}

		try:
			if category in ("Fixed"):
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

	def open_sequence_config(self):
		category = self.category_var.get()
		print(f"[CONFIG EVENT]: Opening configuration for {category}")

		if not hasattr(self, "controller") or not self.controller:
			return

		if category == "List":
			try:
				from canSequencePage import canSequencePage
				self.controller.show_frame(canSequencePage)
			except (ImportError, KeyError, TypeError):
				self.controller.show_frame("canSequencePage")

	def sync_mode_state(self):
		cat = self.category_var.get()
		sub = self.sub_mode_var.get()
		if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
			self.controller.shared_data["active_category"] = cat
			self.controller.shared_data["control_sub_mode"] = sub

	def on_stage_change(self, event=None):
		stage = self.system_stage_var.get()
		if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
			self.controller.shared_data["system_stage"] = stage