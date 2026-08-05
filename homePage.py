import tkinter as tk
from tkinter import ttk

class homePage(tk.Frame):
    lebel_color = "#8056a5"
    button_color = "#573172"

    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        # Track displayed error count to avoid listbox duplication
        self._displayed_error_count = 0

        # --- Top Navigation / Control Bar ---
        top_container = tk.Frame(self, bg="#FFFFFF")
        top_container.pack(side="top", fill="x", pady=10)
        self.create_status_bar(top_container)

        # --- Main 3x3 Grid Screen ---
        grid_container = tk.Frame(self, bg="#FFFFFF")
        grid_container.pack(side="top", fill="both", expand=True, padx=10, pady=5)
        grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        grid_container.grid_rowconfigure((0, 1, 2), weight=1, uniform="equal")

        # Background grid visualization (remove later if not needed)
        for row in range(3):
            for col in range(3):
                cell_frame = tk.Frame(grid_container, bg="#D5B6B6")
                cell_frame.grid(row=row, column=col, sticky="nsew", padx=1, pady=1)

        # ---------------------------------------------------------------------
        # Top-Left Cell (Row 0, Col 0): Welcome & System Stage
        # ---------------------------------------------------------------------
        cell_split_frame_TL = tk.Frame(grid_container, bg="#ffffff")
        cell_split_frame_TL.grid(row=0, column=0, sticky="nsew")
        cell_split_frame_TL.grid_rowconfigure((0, 1), weight=1)
        cell_split_frame_TL.grid_columnconfigure(0, weight=1)

        welcome_label = tk.Label(
            cell_split_frame_TL, 
            text="Welcome", 
            font=("Helvetica", 12, "bold"), 
            bg=self.lebel_color, 
            fg="white", 
            width=30
        )
        welcome_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # System Stage Row
        stage_row_container = tk.Frame(cell_split_frame_TL, bg=self.lebel_color)
        stage_row_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        stage_row_container.grid_rowconfigure(0, weight=1)
        stage_row_container.grid_columnconfigure(0, weight=1)
        stage_row_container.grid_columnconfigure(1, weight=0)
        stage_row_container.grid_columnconfigure(2, weight=0)
        stage_row_container.grid_columnconfigure(3, weight=1)

        lbl_stage_title = tk.Label(
            stage_row_container, 
            text="System stage : ", 
            font=("Helvetica", 12, "bold"), 
            bg=self.lebel_color, 
            fg="white"
        )
        lbl_stage_title.grid(row=0, column=1, sticky="e")

        self.lbl_stage_value = tk.Label(
            stage_row_container, 
            text="--", 
            font=("Helvetica", 12, "bold"), 
            bg=self.lebel_color, 
            fg="#eed2d2"
        )
        self.lbl_stage_value.grid(row=0, column=2, sticky="w")

        # ---------------------------------------------------------------------
        # Mid-Left Cell (Row 1, Col 0): Error Counter & Error Listbox
        # ---------------------------------------------------------------------
        cell_split_frame_ML = tk.Frame(grid_container, bg="#ffffff")
        cell_split_frame_ML.grid(row=1, column=0, sticky="nsew")
        cell_split_frame_ML.grid_rowconfigure((0, 1), weight=2)
        cell_split_frame_ML.grid_columnconfigure(0, weight=1)

        # Error Count Header Bar
        error_row_container = tk.Frame(cell_split_frame_ML, bg=self.button_color)
        error_row_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        error_row_container.grid_rowconfigure(0, weight=1)
        error_row_container.grid_columnconfigure(0, weight=1)
        error_row_container.grid_columnconfigure(1, weight=0)
        error_row_container.grid_columnconfigure(2, weight=0)
        error_row_container.grid_columnconfigure(3, weight=1)

        lbl_error_title = tk.Label(
            error_row_container, 
            text="Error Count : ", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="white"
        )
        lbl_error_title.grid(row=0, column=1, sticky="e")

        self.lbl_error_value = tk.Label(
            error_row_container, 
            text="--", 
            font=("Helvetica", 12, "bold"), 
            bg=self.button_color, 
            fg="#ffffff"
        )
        self.lbl_error_value.grid(row=0, column=2, sticky="w")

        # Bind click event on the entire error header
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

        # ---------------------------------------------------------------------
        # Bottom-Left Cell (Row 2, Col 0): Mode Configuration Area
        # ---------------------------------------------------------------------
        cell_split_frame_BL = tk.Frame(grid_container, bg="#ffffff")
        cell_split_frame_BL.grid(row=2, column=0, sticky="nsew")
        cell_split_frame_BL.grid_rowconfigure(0, weight=1)
        cell_split_frame_BL.grid_columnconfigure(0, weight=1)

        mode_config_container = tk.Frame(cell_split_frame_BL, bg=self.button_color)
        mode_config_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # 1. Header Label on Top (Spans both columns)
        lbl_config_header = tk.Label(
            mode_config_container,
            text="Config/Monitor Mode :",
            font=("Helvetica", 11, "bold"),
            bg=self.button_color,
            fg="#FFFFFF"
        )
        lbl_config_header.pack(side="top", pady=(8, 4))

        # 2. Controls Sub-Frame (Holds dropdown on left, GO on right)
        controls_row_frame = tk.Frame(mode_config_container, bg=self.button_color)
        controls_row_frame.pack(side="top", fill="x", padx=8, pady=(0, 8))

        # Array of mode options
        self.mode_options = [
            "Source Mode",
            "Load Mode",
            "Battery Test",
            "Auto Sequence Mode"
        ]

        self.selected_mode = tk.StringVar()
        self.selected_mode.set(self.mode_options[0])

        # 3. Dropdown Box on the LEFT
        self.mode_dropdown = ttk.Combobox(
            controls_row_frame,
            textvariable=self.selected_mode,
            values=self.mode_options,
            state="readonly",
            font=("Helvetica", 10),
            width=16
        )
        self.mode_dropdown.pack(side="left", padx=(0, 4), expand=True)

        # 4. "GO" Button on the RIGHT
        self.btn_go = tk.Button(
            controls_row_frame,
            text="GO",
            font=("Helvetica", 10, "bold"),
            bg="#ffffff",
            fg=self.button_color,
            activebackground="#e0e0e0",
            relief="groove",
            bd=2,
            padx=10,
            command=self.on_go_click
        )
        self.btn_go.pack(side="right", padx=(4, 0))

        
        # ---------------------------------------------------------------------
        # Top-Right Monitor Container (Matches Left Side Structure)
        # ---------------------------------------------------------------------
        # 1. Outer White Container (covers pink debug cell completely)
        monitor_container = tk.Frame(grid_container, bg="#ffffff")
        monitor_container.grid(row=0, column=1, rowspan=2, columnspan=2, sticky="nsew")

        # 2. Inner Monitor Frame (padded by 5px, revealing WHITE background)
        self.monitor_frame = tk.Frame(monitor_container, bg="#E2D4F0", bd=1, relief="solid")
        self.monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)

        lbl_monitor = tk.Label(self.monitor_frame, text="Monitor", font=("Helvetica", 14, "bold"), bg="#E2D4F0", fg="#573172")
        lbl_monitor.pack(expand=True)


        # ---------------------------------------------------------------------
        # Bottom-Right Log Monitor Container (Matches Left Side Structure)
        # ---------------------------------------------------------------------
        # 1. Outer White Container
        log_container = tk.Frame(grid_container, bg="#ffffff")
        log_container.grid(row=2, column=1, rowspan=1, columnspan=2, sticky="nsew")

        # 2. Inner Log Monitor Frame
        self.log_monitor_frame = tk.Frame(log_container, bg="#C9B3E6", bd=1, relief="solid")
        self.log_monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)

        lbl_log_monitor = tk.Label(self.log_monitor_frame, text="Log Monitor", font=("Helvetica", 12, "bold"), bg="#C9B3E6", fg="#573172")
        lbl_log_monitor.pack(expand=True)


        # Start live background updating loop
        self.poll_value()


    # -------------------------------------------------------------------------
    # Helper Methods
    # -------------------------------------------------------------------------
    def on_go_click(self):
        choice = self.selected_mode.get()
        print(f"[NAV EVENT]: Selected mode -> {choice} (Navigation action pending)")

    def create_status_bar(self, target_frame):
        btn_style = {
            "font": ("Helvetica", 10, "bold"),
            "relief": "groove",
            "bd": 2,
            "padx": 15,
            "pady": 5,
            "activebackground": self.button_color
        }

        # Navigation buttons (Left aligned)
        nav_buttons = [
            ("Home", lambda: self.controller.show_frame(homePage)),
            ("File", lambda: self.open_file_selector())
        ]
        for text, command_action in nav_buttons:
            btn = tk.Button(target_frame, text=text, bg=self.button_color, fg="#FFFFFF",
                            command=command_action, **btn_style)
            btn.pack(side="left", padx=4, pady=5)

        # Control buttons (Right aligned)
        control_buttons = [
            ("Clear", lambda: self.print_click("Dashboard Logs Cleared")),
            ("Stop", lambda: self.print_click("Emergency Output Force OFF")),
            ("Restart", lambda: self.print_click("System Power Loop Restart"))
        ]
        for text, command_action in control_buttons:
            btn = tk.Button(target_frame, text=text, bg=self.button_color, fg="#FFFFFF",
                            command=command_action, **btn_style)
            btn.pack(side="right", padx=4, pady=5)

    def poll_value(self):
        # 1. Update system stage label
        latest_stage = get_current_system_stage()
        self.lbl_stage_value.config(text=latest_stage)

        # 2. Update error count and listbox
        error_log = get_current_error_log()
        latest_error_count = len(error_log)
        self.lbl_error_value.config(text=latest_error_count)

        if latest_error_count > self._displayed_error_count:
            # Append only newly added error messages
            for new_msg in error_log[self._displayed_error_count:]:
                self.error_listbox.insert(tk.END, f"• {new_msg}")

            self._displayed_error_count = latest_error_count
            self.error_listbox.yview_moveto(1.0)

        # 3. Schedule next loop cycle in 250ms
        self.after(250, self.poll_value)

    def open_file_selector(self):
        print("Placeholder for file selection")

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