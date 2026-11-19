import json
import os
import tkinter as tk
from tkinter import ttk, filedialog

from matplotlib import category
from basePage import BasePage
import Filemanager


class OperationPage(BasePage):
    label_color = "#145374"      # Dark teal/blue
    button_color = "#00334e"
    accent_color = "#5588a3"

    # Supported mode hierarchy
# Supported mode hierarchy per Power Mode
    MODE_HIERARCHY = {
        "Fixed": ["CV", "CC", "CP"],
        "Step": ["CV", "CC", "CP"],
        "List": ["CV", "CC", "CP"],
    }

    OFF_GRID_HIERARCHY = {
        "Fixed": ["AC Grid-Form"],
        "List": ["AC Grid-Form"],
    }

    DIRECTION_LIMIT_FILES = {
        "Source": "limit_source.json",
        "Sink (On-Grid)": "limit_sink_DC.json",
        "Sink (Off-Grid)": "limit_sink_AC.json",
        "Seamless": "limit_auto.json",
    }

    AUTO_SEQUENCE_FILES = {
        ("Source", "Fixed"): "Fixed_src.csv",
        ("Source", "Step"): "Step_src.csv",
        ("Sink (On-Grid)", "Fixed"): "Fixed_snk.csv",
        ("Sink (On-Grid)", "Step"): "Step_snk.csv",
        ("Sink (Off-Grid)", "Fixed"): "Fixed_snk_offgrid.csv",
        ("Seamless", "Fixed"): "Fixed_auto.csv",
        ("Seamless", "Step"): "Step_auto.csv",
    }

    def __init__(self, parent, controller=None):
        super().__init__(parent, controller)

        self.active_sequence_path = ""
        self.list_active_sequence_path = ""
        self.battery_model_file_path = ""
        self.battery_sim_sequence_path = ""

        # Top-left Stage & Direction state variables
        self.operation_dir_var = tk.StringVar(value="Source")
        self.system_stage_var = tk.StringVar(value="Standby")

        # Control Category & Sub-Mode state variables
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

        # Step CP extra limit & Off-Grid / Reactive setpoints
        self.step_pwr_min_var = tk.StringVar(value="0.0")
        self.step_pwr_max_var = tk.StringVar(value="500.0")
        self.step_vi_lim_var = tk.StringVar(value="400.0")   # Max V or I cap during Step CP

        self.set_ac_volt_var = tk.StringVar(value="380.0")   # Off-Grid AC Voltage (340-420V)
        self.set_ac_freq_var = tk.StringVar(value="50.0")    # Off-Grid AC Frequency (50/60Hz)
        self.set_q_var = tk.StringVar(value="0.0")           # On-Grid Reactive Power (Var)
        self.set_s_var = tk.StringVar(value="0.0")           # Apparent Power readout/cap (VA)

        # DC & AC Side telemetry display variables
        self.dc_volt_var = tk.StringVar(value="0.00 V")
        self.dc_curr_var = tk.StringVar(value="0.00 A")
        self.dc_pwr_var = tk.StringVar(value="0.00 W")
        self.dc_eff_var = tk.StringVar(value="0.0 %")
        self.ac_volt_var = tk.StringVar(value="0.00 V")
        self.ac_curr_var = tk.StringVar(value="0.00 A")
        self.ac_pwr_var = tk.StringVar(value="0.00 W")
        self.ac_freq_var = tk.StringVar(value="0.00 Hz")

        # Limit Variables
        self.lim_max_volt_var = tk.StringVar(value="60.0")
        self.lim_min_volt_var = tk.StringVar(value="0.0")
        self.lim_src_curr_var = tk.StringVar(value="10.0")
        self.lim_snk_curr_var = tk.StringVar(value="-10.0")
        self.lim_src_pwr_var = tk.StringVar(value="600.0")
        self.lim_snk_pwr_var = tk.StringVar(value="-600.0")
        self.lim_max_temp_var = tk.StringVar(value="85.0")
        self.lim_max_energy_var = tk.StringVar(value="1000.0")

        # Plot Control Variables
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
        self.setup_stage_selector()         # Row 0, Col 0 (Direction + Stage)
        self.setup_control_parameters()     # Row 1, Col 0
        self.setup_dc_side_monitor()        # Row 0-1, Col 1
        self.setup_ac_side_monitor()        # Row 0-1, Col 2
        self.setup_limit_parameters()       # Row 0-1, Col 3
        self.setup_time_series_plot()       # Row 2-4, Col 0-2
        self.setup_datalogger()             # Row 2, Col 3
        self.setup_command_list()           # Row 3, Col 3
        self.setup_plot_controls()          # Row 4, Col 3

        # Load initial limits, resolve default sequence, and start single polling loop
        self.load_limits()
        self.update_mode_sequence("Fixed")
        self.apply_parameters()
        self.poll_value()

    def tkraise(self, *args, **kwargs):
        """Reloads latest limit parameters whenever this page is brought to front."""
        super().tkraise(*args, **kwargs)
        self.load_limits()
        if self.category_var.get() == "List":
            self.update_mode_sequence("List")
            self.render_parameter_inputs()
        self.sync_mode_state()
        self.apply_parameters()

    # =========================================================================
    # Grid Layout & Top-Left Combined Selector (Row 0, Col 0)
    # =========================================================================

    def setup_main_containers(self):
        """Initializes the responsive 5x4 grid container."""
        self.grid_container = tk.Frame(self, bg="#FFFFFF")
        self.grid_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

        self.grid_container.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cols")
        self.grid_container.grid_rowconfigure(0, weight=1, uniform="rows")
        self.grid_container.grid_rowconfigure(1, weight=3, uniform="rows")
        self.grid_container.grid_rowconfigure((2, 3, 4), weight=2, uniform="rows")

        reserved_cells = {
            (0, 0), (1, 0),
            (0, 1), (1, 1),
            (0, 2), (1, 2),
            (0, 3), (1, 3),
        }

        for row in range(5):
            for col in range(4):
                if (row, col) in reserved_cells:
                    continue
                cell_frame = tk.Frame(self.grid_container, bg="#E0E0E0", bd=1, relief="solid")
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=2, pady=2)

    def setup_stage_selector(self):
        """Combined Power Mode (Source/Sink/Seamless) & System Stage selector in Row 0, Col 0."""
        self.stage_container = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
        self.stage_container.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        self.stage_container.grid_rowconfigure((0, 1), weight=1)
        self.stage_container.grid_columnconfigure(0, weight=1)  # Left spacer
        self.stage_container.grid_columnconfigure(1, weight=0)  # Labels
        self.stage_container.grid_columnconfigure(2, weight=0)  # Dropdowns
        self.stage_container.grid_columnconfigure(3, weight=1)  # Right spacer

        # Row 0: Power Direction / Operating Quadrant (Source, Sink, Seamless)
        tk.Label(
            self.stage_container, text="Power Mode :",
            font=("Helvetica", 9, "bold"), bg=self.label_color, fg="#FFFFFF"
        ).grid(row=0, column=1, sticky="e", padx=(0, 5), pady=(2, 1))

        self.dir_dropdown = ttk.Combobox(
            self.stage_container, textvariable=self.operation_dir_var,
            values=["Source", "Sink (On-Grid)", "Sink (Off-Grid)", "Seamless"],
            state="readonly", width=13, font=("Helvetica", 8, "bold")
        )
        self.dir_dropdown.grid(row=0, column=2, sticky="w", pady=(2, 1))
        self.dir_dropdown.bind("<<ComboboxSelected>>", self.on_direction_change)

        # Row 1: System Stage (Output, Ping, Standby)
        tk.Label(
            self.stage_container, text="System Stage :",
            font=("Helvetica", 9, "bold"), bg=self.label_color, fg="#FFFFFF"
        ).grid(row=1, column=1, sticky="e", padx=(0, 5), pady=(1, 2))

        self.stage_dropdown = ttk.Combobox(
            self.stage_container, textvariable=self.system_stage_var,
            values=["Output", "Ping", "Standby"], state="readonly",
            width=9, font=("Helvetica", 8, "bold")
        )
        self.stage_dropdown.grid(row=1, column=2, sticky="w", pady=(1, 2))
        self.stage_dropdown.bind("<<ComboboxSelected>>", self.on_stage_change)

    # =========================================================================
    # Control Parameter Box (Row 1, Col 0)
    # =========================================================================

    def setup_control_parameters(self):
        """Control Parameter Box placed in Row 1, Col 0."""
        self.ctrl_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
        self.ctrl_frame.grid(row=1, column=0, sticky="nsew", padx=2, pady=2)

        lbl_title = tk.Label(
            self.ctrl_frame,
            text="Control parameter",
            font=("Helvetica", 9, "bold"),
            bg=self.label_color,
            fg="#FFFFFF"
        )
        lbl_title.pack(side="top", pady=(2, 0))

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

    # =========================================================================
    # Merged Display Panels (DC Side & AC Side)
    # =========================================================================

    def setup_dc_side_monitor(self):
        """Merged Box (Row 0-1, Col 1) to display DC Side telemetry."""
        self.dc_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
        self.dc_frame.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=2, pady=2)

        tk.Label(
            self.dc_frame, text="DC Side", font=("Helvetica", 10, "bold"),
            bg=self.label_color, fg="#FFFFFF"
        ).pack(side="top", pady=(4, 6))

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

        tk.Label(
            self.ac_frame, text="AC Side", font=("Helvetica", 10, "bold"),
            bg=self.label_color, fg="#FFFFFF"
        ).pack(side="top", pady=(4, 6))

        readouts_container = tk.Frame(self.ac_frame, bg=self.label_color)
        readouts_container.pack(fill="both", expand=True, padx=8, pady=2)
        readouts_container.grid_columnconfigure((0, 1), weight=1)

        self._build_monitor_row(readouts_container, 0, "Voltage:", self.ac_volt_var)
        self._build_monitor_row(readouts_container, 1, "Current:", self.ac_curr_var)
        self._build_monitor_row(readouts_container, 2, "Power:", self.ac_pwr_var)
        self._build_monitor_row(readouts_container, 3, "Frequency:", self.ac_freq_var)

    def _build_monitor_row(self, parent, row_idx, title, var):
        parent.grid_rowconfigure(row_idx, weight=1)
        tk.Label(
            parent, text=title, font=("Helvetica", 9, "bold"),
            bg=self.label_color, fg="#DCE2E8", anchor="w"
        ).grid(row=row_idx, column=0, sticky="w", padx=2, pady=1)

        tk.Label(
            parent, textvariable=var, font=("Helvetica", 9, "bold"),
            bg=self.label_color, fg="#FFFFFF", anchor="e"
        ).grid(row=row_idx, column=1, sticky="e", padx=2, pady=1)

    # =========================================================================
    # Limit Parameter Box (Row 0-1, Col 3)
    # =========================================================================

    def setup_limit_parameters(self):
        """Merged Box (Row 0-1, Col 3) for Pos/Neg limits with manual UPDATE button."""
        self.limit_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
        self.limit_frame.grid(row=0, column=3, rowspan=2, sticky="nsew", padx=2, pady=2)

        tk.Label(
            self.limit_frame, text="Limit parameter", font=("Helvetica", 9, "bold"),
            bg=self.label_color, fg="#FFFFFF"
        ).pack(side="top", pady=(2, 1))

        limits_form = tk.Frame(self.limit_frame, bg=self.label_color)
        limits_form.pack(side="top", fill="both", expand=True, padx=4, pady=1)

        limits_form.grid_columnconfigure((0, 3), weight=1)
        limits_form.grid_columnconfigure((1, 4), weight=0)
        limits_form.grid_columnconfigure((2, 5), weight=0)

        def make_cell(row, col_start, label, var, unit):
            tk.Label(
                limits_form, text=label, font=("Helvetica", 8, "bold"),
                bg=self.label_color, fg="#FFFFFF"
            ).grid(row=row, column=col_start, sticky="w", padx=(1, 1), pady=1)

            ent = tk.Entry(
                limits_form, textvariable=var, width=4, font=("Helvetica", 8, "bold"),
                justify="center", bd=1
            )
            ent.grid(row=row, column=col_start + 1, padx=1, pady=1)

            tk.Label(
                limits_form, text=unit, font=("Helvetica", 8, "bold"),
                bg=self.label_color, fg="#FFFFFF"
            ).grid(row=row, column=col_start + 2, sticky="w", padx=(1, 3), pady=1)

        for r in range(5):
            limits_form.grid_rowconfigure(r, weight=1)

        make_cell(0, 0, "+V Lim:", self.lim_max_volt_var, "V")
        make_cell(0, 3, "-V Lim:", self.lim_min_volt_var, "V")
        make_cell(1, 0, "+I Lim:", self.lim_src_curr_var, "A")
        make_cell(1, 3, "-I Lim:", self.lim_snk_curr_var, "A")
        make_cell(2, 0, "+P Lim:", self.lim_src_pwr_var, "W")
        make_cell(2, 3, "-P Lim:", self.lim_snk_pwr_var, "W")
        make_cell(3, 0, "Max Temp:", self.lim_max_temp_var, "°C")
        make_cell(4, 0, "Max Engy:", self.lim_max_energy_var, "Wh")

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
            row=3, column=3, rowspan=2, columnspan=3,
            sticky="nsew", padx=(4, 2), pady=(2, 2)
        )

    # =========================================================================
    # Plot, Log, Command List & Plot Controls (Rows 2-4)
    # =========================================================================

    def setup_time_series_plot(self):
        self.plot_container = tk.Frame(self.grid_container, bg="#000000", bd=1, relief="solid")
        self.plot_container.grid(row=2, column=0, rowspan=3, columnspan=3, sticky="nsew", padx=2, pady=2)

        self.plot_placeholder_lbl = tk.Label(
            self.plot_container,
            text="[ Time-Series Plot Area ]",
            font=("Helvetica", 11, "bold"),
            bg="#000000",
            fg="#888888"
        )
        self.plot_placeholder_lbl.pack(expand=True)

    def setup_datalogger(self):
        self.log_container = tk.Frame(self.grid_container, bg="#000000", bd=1, relief="solid")
        self.log_container.grid(row=2, column=3, sticky="nsew", padx=2, pady=2)

        tk.Label(
            self.log_container, text="[ System Log Area ]",
            font=("Helvetica", 9, "bold"), bg="#000000", fg="#555555"
        ).pack(expand=True)

    def setup_command_list(self):
        self.cmd_list_container = tk.Frame(self.grid_container, bg="#000000", bd=1, relief="solid")
        self.cmd_list_container.grid(row=3, column=3, sticky="nsew", padx=2, pady=2)

        tk.Label(
            self.cmd_list_container, text="[ Command List Area ]",
            font=("Helvetica", 9, "bold"), bg="#000000", fg="#555555"
        ).pack(expand=True)

    def setup_plot_controls(self):
        self.plot_ctrl_frame = tk.Frame(self.grid_container, bg=self.label_color, bd=1, relief="solid")
        self.plot_ctrl_frame.grid(row=4, column=3, sticky="nsew", padx=2, pady=2)

        top_bar = tk.Frame(self.plot_ctrl_frame, bg=self.label_color)
        top_bar.pack(side="top", fill="x", padx=2, pady=(2, 1))

        ch_configs = [
            ("CH1", self.ch1_active, "#FFCC00"),
            ("CH2", self.ch2_active, "#00FFCC"),
            ("CH3", self.ch3_active, "#FF66CC"),
            ("CH4", self.ch4_active, "#66FF66"),
        ]

        for label, var, color in ch_configs:
            chk = tk.Checkbutton(
                top_bar, text=label, variable=var, font=("Helvetica", 8, "bold"),
                bg=self.label_color, fg=color, selectcolor="#002233",
                activebackground=self.label_color, activeforeground=color,
                padx=1, pady=0, bd=0, highlightthickness=0,
                command=self.on_channel_toggle
            )
            chk.pack(side="left", padx=1)

        self.btn_freeze = tk.Button(
            top_bar, text="❄ Freeze", font=("Helvetica", 7, "bold"),
            bg=self.button_color, fg="#FFFFFF", activebackground="#D9534F",
            activeforeground="#FFFFFF", relief="groove", bd=1, padx=4, pady=0,
            command=self.toggle_freeze
        )
        self.btn_freeze.pack(side="right", padx=(2, 1))

        knobs_frame = tk.Frame(self.plot_ctrl_frame, bg=self.label_color)
        knobs_frame.pack(side="top", fill="both", expand=True, padx=2, pady=1)
        knobs_frame.grid_columnconfigure((0, 1), weight=1)
        knobs_frame.grid_rowconfigure((0, 1), weight=1)

        def build_knob(parent, row, col, title, var, on_scroll):
            k_box = tk.Frame(parent, bg="#002233", bd=1, relief="groove")
            k_box.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

            inner = tk.Frame(k_box, bg="#002233")
            inner.pack(expand=True)

            lbl_t = tk.Label(inner, text=f"{title}:", font=("Helvetica", 8, "bold"), bg="#002233", fg="#A0C4DF")
            lbl_t.pack(side="left", padx=(2, 1))

            lbl_v = tk.Label(inner, textvariable=var, font=("Helvetica", 8, "bold"), bg="#002233", fg="#FFFFFF")
            lbl_v.pack(side="left", padx=(1, 2))

            for w in (k_box, inner, lbl_t, lbl_v):
                w.bind("<MouseWheel>", lambda e: on_scroll(1 if e.delta > 0 else -1))
                w.bind("<Button-4>", lambda e: on_scroll(1))
                w.bind("<Button-5>", lambda e: on_scroll(-1))

        self.t_div_steps = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0, 10.0]
        self.v_div_steps = [0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
        self.t_idx = 3
        self.v_idx = 4

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

        build_knob(knobs_frame, 0, 0, "T/DIV", self.time_div_var, scroll_t_div)
        build_knob(knobs_frame, 0, 1, "V/DIV", self.volt_div_var, scroll_v_div)
        build_knob(knobs_frame, 1, 0, "X POS", self.x_pos_var, scroll_x_pos)
        build_knob(knobs_frame, 1, 1, "Y POS", self.y_pos_var, scroll_y_pos)

    def toggle_freeze(self):
        frozen = not self.is_plot_frozen.get()
        self.is_plot_frozen.set(frozen)
        if frozen:
            self.btn_freeze.config(text="RESUME", bg="#D9534F")
            print("[PLOT]: Stream Frozen")
        else:
            self.btn_freeze.config(text="FREEZE", bg=self.button_color)
            print("[PLOT]: Stream Resumed")

    def on_channel_toggle(self):
        channels = {
            "CH1": self.ch1_active.get(),
            "CH2": self.ch2_active.get(),
            "CH3": self.ch3_active.get(),
            "CH4": self.ch4_active.get()
        }
        print(f"[PLOT CHANNELS]: {channels}")

    def apply_plot_settings(self):
        settings = {
            "time_div": self.t_div_steps[self.t_idx],
            "volt_div": self.v_div_steps[self.v_idx],
            "x_pos": float(self.x_pos_var.get()),
            "y_pos": float(self.y_pos_var.get())
        }
        print(f"[PLOT SCALE UPDATED]: {settings}")

    # =========================================================================
    # Dynamic Input Rendering Logic
    # =========================================================================

    def _bind_scrollable(self, widget, var: tk.StringVar, step: float, min_val: float, max_val: float):
        """Scroll up to increase, scroll down to decrease, and auto-sync to shared_data."""
        def _on_scroll(event):
            try:
                curr = float(var.get())
            except ValueError:
                curr = 0.0

            if getattr(event, "num", None) == 4 or getattr(event, "delta", 0) > 0:
                new_val = min(max_val, round(curr + step, 3))
            elif getattr(event, "num", None) == 5 or getattr(event, "delta", 0) < 0:
                new_val = max(min_val, round(curr - step, 3))
            else:
                return

            var.set(str(new_val))
            self.apply_parameters()

        widget.bind("<MouseWheel>", _on_scroll)
        widget.bind("<Button-4>", _on_scroll)
        widget.bind("<Button-5>", _on_scroll)

    def _build_scroll_row(self, parent, row_idx, label_text, var, unit_text, step=1.0, min_v=-1000.0, max_v=1000.0):
        """Creates a single active, mouse-wheel scrollable parameter row."""
        parent.grid_rowconfigure(row_idx, weight=1)
        tk.Label(
            parent, text=label_text, font=("Helvetica", 8, "bold"),
            bg=self.label_color, fg="#FFFFFF"
        ).grid(row=row_idx, column=0, sticky="w", pady=1)

        entry = tk.Entry(
            parent, textvariable=var, width=7, font=("Helvetica", 9, "bold"),
            justify="center", bd=1, bg="#FFFFFF", fg="#000000"
        )
        entry.grid(row=row_idx, column=1, padx=3, pady=1)
        entry.bind("<Return>", lambda e: self.apply_parameters())
        self._bind_scrollable(entry, var, step=step, min_val=min_v, max_val=max_v)

        tk.Label(
            parent, text=unit_text, font=("Helvetica", 8, "bold"),
            bg=self.label_color, fg="#DCE2E8"
        ).grid(row=row_idx, column=2, sticky="w", pady=1)
        return entry

    def _build_step_cell(self, parent, row, col_start, label, var, unit, step=1.0, min_v=0.0, max_v=1000.0):
        lbl = tk.Label(parent, text=label, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
        lbl.grid(row=row, column=col_start, sticky="w", padx=(2, 1), pady=1)

        entry = tk.Entry(parent, textvariable=var, width=5, font=("Helvetica", 8, "bold"), justify="center", bd=1)
        entry.grid(row=row, column=col_start + 1, padx=1, pady=1)
        entry.bind("<Return>", lambda e: self.apply_parameters())
        self._bind_scrollable(entry, var, step=step, min_val=min_v, max_val=max_v)

        unit_lbl = tk.Label(parent, text=unit, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#DCE2E8")
        unit_lbl.grid(row=row, column=col_start + 2, sticky="w", padx=(1, 3), pady=1)

    def render_parameter_inputs(self):
        """Shows ONLY the relevant scrollable blocks for the active Power Mode, Category, and Control."""
        for widget in self.form_container.winfo_children():
            widget.destroy()

        direction = self.operation_dir_var.get()
        category = self.category_var.get()
        sub_mode = self.sub_mode_var.get()

        # ---------------------------------------------------------------------
        # CASE 1: LIST MODE (Controlled by CSV Sequence)
        # ---------------------------------------------------------------------
        if category == "List":
            file_display = (
                os.path.basename(self.active_sequence_path)
                if self.active_sequence_path
                else "No file selected"
            )
            tk.Label(
                self.form_container,
                text="Active Sequence File:",
                font=("Helvetica", 8, "bold"),
                bg=self.label_color,
                fg="#DCE2E8",
            ).pack(pady=(4, 1))

            tk.Label(
                self.form_container,
                text=file_display,
                font=("Helvetica", 9, "bold"),
                bg="#002233",
                fg="#00FFCC",
                padx=8,
                pady=3,
                relief="groove",
                bd=1,
            ).pack(fill="x", padx=6, pady=2)
            return

        # ---------------------------------------------------------------------
        # CASE 2: SINK (OFF-GRID) -> AC Grid-Forming Voltage & Frequency
        # ---------------------------------------------------------------------
        if direction == "Sink (Off-Grid)":
            self.form_container.grid_columnconfigure(0, weight=1)
            self.form_container.grid_columnconfigure((1, 2), weight=0)
            self._build_scroll_row(self.form_container, 0, "AC Volt :", self.set_ac_volt_var, "V", step=1.0, min_v=340.0, max_v=420.0)
            self._build_scroll_row(self.form_container, 1, "AC Freq :", self.set_ac_freq_var, "Hz", step=0.5, min_v=50.0, max_v=60.0)
            tk.Label(
                self.form_container, text="⚠ Disconnect utility grid in Off-Grid!",
                font=("Helvetica", 7, "bold"), bg=self.label_color, fg="#FFCC00"
            ).grid(row=2, column=0, columnspan=3, pady=(2, 0))
            return

        # ---------------------------------------------------------------------
        # CASE 3: FIXED MODE (Source, Sink On-Grid, Seamless)
        # ---------------------------------------------------------------------
        if category == "Fixed":
            self.form_container.grid_columnconfigure(0, weight=1)
            self.form_container.grid_columnconfigure((1, 2), weight=0)

            i_min = -78.0 if direction in ("Sink (On-Grid)", "Seamless") else 0.0
            i_max = 0.0 if direction == "Sink (On-Grid)" else 73.5

            if sub_mode == "CV":
                if self.set_volt_var.get() == "-":
                    self.set_volt_var.set("0.0")
                self._build_scroll_row(self.form_container, 0, "Voltage :", self.set_volt_var, "V", step=1.0, min_v=0.0, max_v=1000.0)

            elif sub_mode == "CC":
                if self.set_curr_var.get() == "-":
                    self.set_curr_var.set("0.0")
                self._build_scroll_row(self.form_container, 0, "Current :", self.set_curr_var, "A", step=0.5, min_v=i_min, max_v=i_max)

            elif sub_mode == "CP":
                if self.set_pwr_var.get() == "-":
                    self.set_pwr_var.set("0.0")
                if self.set_volt_var.get() == "-":
                    self.set_volt_var.set("400.0")
                self._build_scroll_row(self.form_container, 0, "Power (P) :", self.set_pwr_var, "W", step=50.0, min_v=-22000.0, max_v=22000.0)
                self._build_scroll_row(self.form_container, 1, "Voltage :", self.set_volt_var, "V", step=5.0, min_v=150.0, max_v=1000.0)
                if direction in ("Sink (On-Grid)", "Seamless"):
                    self._build_scroll_row(self.form_container, 2, "Reactive (Q):", self.set_q_var, "Var", step=50.0, min_v=-10500.0, max_v=10500.0)

        # ---------------------------------------------------------------------
        # CASE 4: STEP MODE (CV, CC, and CP)
        # ---------------------------------------------------------------------
        elif category == "Step":
            self.form_container.grid_columnconfigure((0, 3), weight=1)
            self.form_container.grid_columnconfigure((1, 2, 4, 5), weight=0)

            if sub_mode in ("CV", "CC"):
                unit = "A" if sub_mode == "CC" else "V"
                self._build_step_cell(self.form_container, 0, 0, "Min :", self.step_min_var, unit, step=1.0, min_v=-1000.0, max_v=1000.0)
                self._build_step_cell(self.form_container, 1, 0, "Max :", self.step_max_var, unit, step=1.0, min_v=-1000.0, max_v=1000.0)
                self._build_step_cell(self.form_container, 0, 3, "Step :", self.step_size_var, unit, step=0.5, min_v=0.1, max_v=500.0)
                self._build_step_cell(self.form_container, 1, 3, "Total T:", self.step_time_var, "s", step=1.0, min_v=0.5, max_v=3600.0)

            elif sub_mode == "CP":
                self._build_step_cell(self.form_container, 0, 0, "Min P:", self.step_pwr_min_var, "W", step=50.0, min_v=-22000.0, max_v=22000.0)
                self._build_step_cell(self.form_container, 1, 0, "Max P:", self.step_pwr_max_var, "W", step=50.0, min_v=-22000.0, max_v=22000.0)
                self._build_step_cell(self.form_container, 2, 0, "V Cap:", self.step_vi_lim_var, "V", step=5.0, min_v=150.0, max_v=1000.0)
                self._build_step_cell(self.form_container, 0, 3, "Step :", self.step_size_var, "W", step=10.0, min_v=1.0, max_v=5000.0)
                self._build_step_cell(self.form_container, 1, 3, "Total T:", self.step_time_var, "s", step=1.0, min_v=0.5, max_v=3600.0)

    # =========================================================================
    # Event Callbacks & Routing
    # =========================================================================

    def on_direction_change(self, event=None):
        """Handles switching between Source, Sink (On-Grid), Sink (Off-Grid), and Seamless."""
        direction = self.operation_dir_var.get()
        print(f"[POWER MODE EVENT]: Switched to -> {direction}")

        hierarchy = self.OFF_GRID_HIERARCHY if direction == "Sink (Off-Grid)" else self.MODE_HIERARCHY
        self.category_dropdown["values"] = list(hierarchy.keys())
        if self.category_var.get() not in hierarchy:
            self.category_var.set("Fixed")

        avail_sub = hierarchy[self.category_var.get()]
        self.sub_mode_dropdown["values"] = avail_sub
        if self.sub_mode_var.get() not in avail_sub:
            self.sub_mode_var.set(avail_sub[0])
        self.update_mode_sequence(self.category_var.get())
        self.render_parameter_inputs()
        self.sync_mode_state()
        self.load_limits()
        self.apply_parameters()
        

    def send_fixed_mode(self):
        base = self.get_stage_and_sequence()
        direction = base["operation_direction"]
        sub = self.sub_mode_var.get()

        if direction == "Sink (Off-Grid)":
            payload = {
                **base,
                "mode": "Fixed",
                "control_sub_mode": "AC_OFF_GRID",
                "ac_target_voltage": float(self.set_ac_volt_var.get()),
                "ac_target_frequency": float(self.set_ac_freq_var.get()),
                "target_voltage": 0.0,
                "target_current": 0.0,
                "target_power": 0.0,
            }
        else:
            v_val = float(self.set_volt_var.get()) if sub in ("CV", "CP") else 0.0
            i_val = float(self.set_curr_var.get()) if sub == "CC" else 0.0
            p_val = float(self.set_pwr_var.get()) if sub == "CP" else 0.0
            q_val = float(self.set_q_var.get()) if (sub == "CP" and direction in ("Sink (On-Grid)", "Seamless")) else 0.0

            payload = {
                **base,
                "mode": "Fixed",
                "control_sub_mode": sub,
                "target_voltage": v_val,
                "target_current": i_val,
                "target_power": p_val,
                "target_reactive_power": q_val,
            }
        self._dispatch_to_worker(payload)

    def send_step_mode(self):
        base = self.get_stage_and_sequence()
        sub = self.sub_mode_var.get()

        if sub == "CP":
            s_min = float(self.step_pwr_min_var.get())
            s_max = float(self.step_pwr_max_var.get())
            v_cap = float(self.step_vi_lim_var.get())
            unit = "W"
        else:
            s_min = float(self.step_min_var.get())
            s_max = float(self.step_max_var.get())
            v_cap = 0.0
            unit = "A" if sub == "CC" else "V"

        s_size = max(0.01, abs(float(self.step_size_var.get())))
        total_time = max(0.1, float(self.step_time_var.get()))
        num_steps = max(1.0, (abs(s_max - s_min) / s_size))
        per_step_sec = round(total_time / num_steps, 4)

        payload = {
            **base,
            "mode": "Step",
            "control_sub_mode": sub,
            "step_min": s_min,
            "step_max": s_max,
            "step_size": s_size,
            "step_total_time_sec": total_time,
            "step_time_sec": per_step_sec,
            "step_v_cap": v_cap,
            "step_unit": unit,
        }
        self._dispatch_to_worker(payload)

    def on_stage_change(self, event=None):
        stage = self.system_stage_var.get()
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            self.controller.shared_data["system_stage"] = stage
        self.apply_parameters()

    def on_category_change(self, event=None):
        category = self.category_var.get()
        available_sub_modes = self.MODE_HIERARCHY.get(category, ["CV"])

        self.sub_mode_dropdown["values"] = available_sub_modes
        self.sub_mode_var.set(available_sub_modes[0])

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

    def on_sub_mode_change(self, event=None):
        self.render_parameter_inputs()
        self.sync_mode_state()
        self.apply_parameters()

    def sync_mode_state(self):
        cat = self.category_var.get()
        sub = self.sub_mode_var.get()
        direction = self.operation_dir_var.get()
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            self.controller.shared_data["operation_direction"] = direction
            self.controller.shared_data["active_category"] = cat
            self.controller.shared_data["mode"] = cat
            self.controller.shared_data["control_sub_mode"] = sub

    def open_sequence_config(self):
        category = self.category_var.get()
        print(f"[CONFIG EVENT]: Opening configuration for {category}")

        if not hasattr(self, "controller") or not self.controller:
            return

        if category == "List":
            if not self.active_sequence_path or not os.path.exists(self.active_sequence_path):
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

            self.controller.show_frame("canSequencePage")

        elif category == "Battery Sim":
            self.choose_battery_model_file()

        else:
            self.controller.show_frame("canSequencePage")

    def choose_battery_model_file(self):
        """Opens file dialog to select a battery model file (.json) and pushes it to controller."""
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
            model_data = {}
            try:
                with open(chosen_file, "r", encoding="utf-8") as f:
                    model_data = json.load(f)
            except Exception as e:
                print(f"[ERROR]: Failed to parse battery model file: {e}")

            if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
                self.controller.shared_data["battery_model_file_path"] = chosen_file
                self.controller.shared_data["battery_model"] = model_data
                self.controller.shared_data["model_file_exists"] = True

            print(f"[BATTERY MODEL SELECTED]: {chosen_file}")
            self.send_battery_sim_mode()

    # =========================================================================
    # Limit Management (Manual UPDATE & Direction-Aware Loading)
    # =========================================================================

    def _get_active_limit_file(self):
        direction = self.operation_dir_var.get()
        filename = self.DIRECTION_LIMIT_FILES.get(direction, "limit_source.json")
        return Filemanager.get_required_path(filename)

    def load_limits(self):
        """Loads limit thresholds matching the selected Power Mode (Source/Sink/Seamless)."""
        limit_file = self._get_active_limit_file()
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

            if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
                self.controller.shared_data["limits"] = data
                self.controller.shared_data.update(data)

    def update_limits(self):
        """Triggered exclusively by the UPDATE button to save limits to disk & RAM."""
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

            if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
                self.controller.shared_data["limits"] = limits_data
                self.controller.shared_data.update(limits_data)

            limit_file = self._get_active_limit_file()
            Filemanager.save_json(limit_file, limits_data)

            print(f"[MANUAL LIMIT UPDATE]: Saved to {limit_file.name} -> {limits_data}")

        except ValueError:
            print("[INPUT ERROR]: Please enter valid numeric values for all limit fields.")
        except Exception as e:
            print(f"[ERROR]: Failed to write limit file: {e}")

    # =========================================================================
    # Telemetry Polling & Worker Dispatch
    # =========================================================================

    def poll_value(self):
        """Periodically updates the displayed telemetry values from shared_data."""
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            data = self.controller.shared_data

            self.dc_volt_var.set(f"{data.get('dc_voltage', 0.0):.2f} V")
            self.dc_curr_var.set(f"{data.get('dc_current', 0.0):.2f} A")
            self.dc_pwr_var.set(f"{data.get('dc_power', 0.0):.2f} W")
            self.dc_eff_var.set(f"{data.get('dc_efficiency', 0.0):.1f} %")

            self.ac_volt_var.set(f"{data.get('ac_voltage', 0.0):.2f} V")
            self.ac_curr_var.set(f"{data.get('ac_current', 0.0):.2f} A")
            self.ac_pwr_var.set(f"{data.get('ac_power', 0.0):.2f} W")
            self.ac_freq_var.set(f"{data.get('ac_frequency', 0.0):.2f} Hz")

        self.after(500, self.poll_value)

    def update_mode_sequence(self, category: str):
        direction = self.operation_dir_var.get()

        if category == "List":
            active_path = ""
            if hasattr(self, "controller") and self.controller:
                active_path = self.controller.shared_data.get("active_sequence_path", "")

            if not active_path:
                active_path = getattr(self, "list_active_sequence_path", "")

            if not active_path or not os.path.exists(active_path):
                default_list = str(Filemanager.get_required_path("List_sequence.csv"))
                if os.path.exists(default_list):
                    active_path = default_list

            self.active_sequence_path = active_path
            print(f"[MODE LIST]: Using active sequence -> '{self.active_sequence_path}'")
        else:
            filename = self.AUTO_SEQUENCE_FILES.get((direction, category), "")
            if filename:
                self.active_sequence_path = str(Filemanager.get_required_path(filename))
            print(f"[MODE {direction.upper()} / {category.upper()}]: Assigned sequence -> '{self.active_sequence_path}'")


    def set_active_sequence_file(self, csv_file_path: str):
        self.list_active_sequence_path = csv_file_path
        self.active_sequence_path = csv_file_path

        if hasattr(self, "controller") and self.controller:
            self.controller.shared_data["active_sequence_path"] = csv_file_path
            self.controller.shared_data["active_sequence_csv"] = csv_file_path

        self.render_parameter_inputs()
        self.send_list_mode()

    def get_stage_and_sequence(self):
        stage = self.system_stage_var.get()
        direction = self.operation_dir_var.get()
        return {
            "operation_direction": direction,
            "system_stage": stage,
            "is_running": (stage == "Output"),
            "active_sequence_csv": self.active_sequence_path,
            "sequence_file_exists": bool(
                self.active_sequence_path and os.path.exists(self.active_sequence_path)
            ),
        }


    def send_list_mode(self):
        base = self.get_stage_and_sequence()
        self.update_mode_sequence("List")
        sub = self.sub_mode_var.get()
        payload = {
            **base,
            "mode": "List",
            "control_sub_mode": sub,
            "active_sequence_csv": self.active_sequence_path,
            "sequence_file_exists": bool(self.active_sequence_path and os.path.exists(self.active_sequence_path)),
        }
        self._dispatch_to_worker(payload)

    def send_battery_sim_mode(self):
        self.update_mode_sequence("Battery Sim")
        base = self.get_stage_and_sequence()
        sub = self.sub_mode_var.get()

        model_path = self.battery_model_file_path
        if not model_path and hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            model_path = self.controller.shared_data.get("battery_model_file_path", "")
        self.battery_model_file_path = model_path

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