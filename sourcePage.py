import tkinter as tk
from tkinter import ttk
from basePage import BasePage


class sourcePage(BasePage):
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

        # Build Main UI Structure
        self.setup_main_containers()
        self.setup_stage_selector()        # Grid (0, 0)
        self.setup_control_parameters()    # Grid (1, 0)

    def setup_main_containers(self):
        """Initializes the responsive 5x4 grid container."""
        self.grid_container = tk.Frame(self, bg="#FFFFFF")
        self.grid_container.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5))

        self.grid_container.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="cols")

        # Proportional row heights
        self.grid_container.grid_rowconfigure(0, weight=1, uniform="rows")   # 0.5x height
        self.grid_container.grid_rowconfigure((2, 3, 4), weight=2, uniform="rows")
        self.grid_container.grid_rowconfigure(1, weight=3, uniform="rows")   # 1.5x height

        # Background debug grid
        for row in range(5):
            for col in range(4):
                if (row == 0 and col == 0) or (row == 1 and col == 0):
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
            self.stage_container, text="System Stage: ",
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

        # Top Dropdowns Container (Category & Control Mode)
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

        # Bottom Action / Sequence Config Button
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

        # Dynamic Form Container (Swaps depending on Category & Sub-mode)
        self.form_container = tk.Frame(self.ctrl_frame, bg=self.label_color)
        self.form_container.pack(side="top", fill="both", expand=True, padx=6, pady=0)

        # Render initial input layout
        self.render_parameter_inputs()

    # -------------------------------------------------------------------------
    # Dynamic Input Rendering Logic
    # -------------------------------------------------------------------------

    def render_parameter_inputs(self):
        """Rebuilds the inner parameter form based on active Category and Sub-Mode."""
        # Clear existing fields
        for widget in self.form_container.winfo_children():
            widget.destroy()

        category = self.category_var.get()
        sub_mode = self.sub_mode_var.get()

        if category in ("Fixed", "List", "Battery Sim"):
            # Single-column layout for V, I, P
            self.form_container.grid_columnconfigure(0, weight=1)
            self.form_container.grid_columnconfigure(1, weight=0)
            self.form_container.grid_columnconfigure(2, weight=0)
            for c in (3, 4, 5):
                self.form_container.grid_columnconfigure(c, weight=0)

            self._build_row(self.form_container, 0, "Voltage :", self.set_volt_var, "V")
            self._build_row(self.form_container, 1, "Current :", self.set_curr_var, "A")
            self._build_row(self.form_container, 2, "Power :", self.set_pwr_var, "W")

            # Apply state permissions
            if category == "List":
                self._set_field_state(self.entry_v, self.set_volt_var, active=False)
                self._set_field_state(self.entry_i, self.set_curr_var, active=False)
                self._set_field_state(self.entry_p, self.set_pwr_var, active=False)
            else:
                self._set_field_state(self.entry_v, self.set_volt_var, active=(sub_mode in ("CV", "Ri")))
                self._set_field_state(self.entry_i, self.set_curr_var, active=(sub_mode == "CC"))
                self._set_field_state(self.entry_p, self.set_pwr_var, active=(sub_mode == "CP"))

        elif category == "Step":
            # 2-Column Grid Layout: (Left: Min/Max | Right: Step Size/Time Interval)
            self.form_container.grid_columnconfigure((0, 3), weight=1)  # Labels
            self.form_container.grid_columnconfigure((1, 4), weight=0)  # Entries
            self.form_container.grid_columnconfigure((2, 5), weight=0)  # Units

            unit = "A" if sub_mode == "CC" else "V"

            # Column 1 (Left Side): Min & Max
            self._build_step_cell(self.form_container, row=0, col_start=0, label="Min :", var=self.step_min_var, unit=unit)
            self._build_step_cell(self.form_container, row=1, col_start=0, label="Max :", var=self.step_max_var, unit=unit)

            # Column 2 (Right Side): Step Size & Interval Time
            self._build_step_cell(self.form_container, row=0, col_start=3, label="Step :", var=self.step_size_var, unit=unit)
            self._build_step_cell(self.form_container, row=1, col_start=3, label="Time :", var=self.step_time_var, unit="s")

    def _build_step_cell(self, parent, row, col_start, label, var, unit):
        """Helper to construct a compact step-mode input cell inside the 2-column grid."""
        lbl = tk.Label(parent, text=label, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
        lbl.grid(row=row, column=col_start, sticky="w", padx=(2, 1), pady=2)

        entry = tk.Entry(parent, textvariable=var, width=4, font=("Helvetica", 8, "bold"), justify="center", bd=1)
        entry.grid(row=row, column=col_start + 1, padx=1, pady=2)
        entry.bind("<Return>", lambda e: self.apply_parameters())

        unit_lbl = tk.Label(parent, text=unit, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
        unit_lbl.grid(row=row, column=col_start + 2, sticky="w", padx=(1, 4), pady=2)

    def _build_row(self, parent, row_idx, label_text, var, unit_text, is_step=False):
        """Helper to construct a compact parameter input row."""
        lbl = tk.Label(parent, text=label_text, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
        lbl.grid(row=row_idx, column=0, sticky="w", pady=0)

        entry = tk.Entry(parent, textvariable=var, width=5, font=("Helvetica", 8, "bold"), justify="center", bd=1)
        entry.grid(row=row_idx, column=1, padx=2, pady=0)
        entry.bind("<Return>", lambda e: self.apply_parameters())

        unit_lbl = tk.Label(parent, text=unit_text, font=("Helvetica", 8, "bold"), bg=self.label_color, fg="#FFFFFF")
        unit_lbl.grid(row=row_idx, column=2, sticky="w", pady=0)

        # Store entry references for state management
        if not is_step:
            if row_idx == 0:
                self.entry_v = entry
            elif row_idx == 1:
                self.entry_i = entry
            elif row_idx == 2:
                self.entry_p = entry

    def _set_field_state(self, entry_widget, var, active=True, default_val="0.0"):
        """Toggles entry state and styling between active and disabled/grayed-out."""
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
        """Updates available sub-modes, button text, and redraws input form."""
        category = self.category_var.get()
        available_sub_modes = self.MODE_HIERARCHY.get(category, ["CV"])

        # Update sub-mode dropdown values
        self.sub_mode_dropdown["values"] = available_sub_modes
        self.sub_mode_var.set(available_sub_modes[0])

        # Adapt button label
        button_labels = {
            "Fixed": "Sequence Config",
            "List": "Sequence Config",
            "Step": "Sequence Config",
            "Battery Sim": "Battery Model"
        }
        self.btn_seq.config(text=button_labels.get(category, "Config"))

        self.render_parameter_inputs()
        self.sync_mode_state()

        # Open Sequence Config page directly when List mode is selected
        if category == "List":
            self.open_sequence_config()

    def on_sub_mode_change(self, event=None):
        """Fires when control sub-mode changes (e.g. CV -> CC)."""
        self.render_parameter_inputs()
        self.sync_mode_state()

    def apply_parameters(self):
        """Validates and syncs programmed parameters to controller shared data."""
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

    def open_sequence_config(self):
        """Handles navigation to sequence configuration page."""
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
        """Broadcasts mode settings to shared controller data."""
        cat = self.category_var.get()
        sub = self.sub_mode_var.get()
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            self.controller.shared_data["active_category"] = cat
            self.controller.shared_data["control_sub_mode"] = sub

    def on_stage_change(self, event=None):
        stage = self.system_stage_var.get()
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            self.controller.shared_data["system_stage"] = stage