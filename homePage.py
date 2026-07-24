import tkinter as tk
from tkinter import ttk
class homePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        #Grid layout =================================================================================================

        #Top bar======================================================================================================
        top_container = tk.Frame(self, bg="#FFFFFF")
        top_container.pack(side="top", fill="x", pady=10)
        self.create_status_bar(top_container)

        #Grid screen==================================================================================================
        grid_container = tk.Frame(self, bg="#FFFFFF")
        grid_container.pack(side="top", fill="both", expand=True, padx=10, pady=5)
        grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
        grid_container.grid_rowconfigure((0, 1, 2), weight=1, uniform="equal")
        #remove this later 
        for row in range(3):
            for col in range(3):
                cell_frame = tk.Frame(grid_container, bg="#E52222") # White background for the cell
                cell_frame.grid(
                    row=row, 
                    column=col, 
                    sticky="nsew", 
                    padx=1,
                    pady=1 )
        #Grid layout =================================================================================================
        
        #left cell====================================================================================================

        cell_split_frame_TL = tk.Frame(grid_container, bg="#ffffff")
        cell_split_frame_TL.grid(row=0, column=0, sticky="nsew")
        cell_split_frame_TL.grid_rowconfigure((0, 1), weight=1)
        cell_split_frame_TL.grid_columnconfigure(0, weight=1)

        #Welcome label================================================================================================

        Welcome_label = tk.Label(cell_split_frame_TL, text="Welcome", 
                                font=("Helvetica", 12, "bold"), bg="#4e56b8", fg="white",width=30)
        Welcome_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        #Welcome label================================================================================================
              
        #system stage=================================================================================================

        stage_row_container = tk.Frame(cell_split_frame_TL, bg="#5862c0")
        stage_row_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        stage_row_container.grid_rowconfigure(0, weight=1)
        stage_row_container.grid_columnconfigure(0, weight=1)  # Space to the left
        stage_row_container.grid_columnconfigure(1, weight=0)  # Title column
        stage_row_container.grid_columnconfigure(2, weight=0)  # Value column
        stage_row_container.grid_columnconfigure(3, weight=1)

        lbl_title = tk.Label(stage_row_container, text="System stage : ", 
                             font=("Helvetica", 12, "bold"), bg="#5862c0", fg="white")
        lbl_title.grid(row=0, column=1, sticky="e")

        self.lbl_stage_value = tk.Label(stage_row_container, text="--", 
                                        font=("Helvetica", 12, "bold"), bg="#5862c0", fg="#ff3333")
        self.lbl_stage_value.grid(row=0, column=2, sticky="w")

       
        #system stage=================================================================================================

        cell_split_frame_ML = tk.Frame(grid_container, bg="#ffffff")
        cell_split_frame_ML.grid(row=1, column=0, sticky="nsew")
        cell_split_frame_ML.grid_rowconfigure((0, 1), weight=2)
        cell_split_frame_ML.grid_columnconfigure(0, weight=1)
        #Error warning=================================================================================================
        error_row_container = tk.Frame(cell_split_frame_ML, bg="#5862c0")
        error_row_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        error_row_container.grid_rowconfigure(0, weight=1)
        error_row_container.grid_columnconfigure(0, weight=1)  # Space to the left
        error_row_container.grid_columnconfigure(1, weight=0)  # Title column
        error_row_container.grid_columnconfigure(2, weight=0)  # Value column
        error_row_container.grid_columnconfigure(3, weight=1)

        lbl_error_title = tk.Label(error_row_container, text="Error Count : ", 
                                   font=("Helvetica", 12, "bold"), bg="#5862c0", fg="white")
        lbl_error_title.grid(row=0, column=1, sticky="e")

        self.lbl_error_value = tk.Label(error_row_container, text="--", 
                                        font=("Helvetica", 12, "bold"), bg="#5862c0", fg="#ff3333")
        self.lbl_error_value.grid(row=0, column=2, sticky="w")

        def trigger_error_event(event):
            self.print_click("Entire Error Warning Block Area")

        error_row_container.bind("<Button-1>", trigger_error_event)
        lbl_error_title.bind("<Button-1>", trigger_error_event)
        self.lbl_error_value.bind("<Button-1>", trigger_error_event)
        #Error warning=================================================================================================

        #Button for mode===============================================================================================
        cell_split_frame_BL = tk.Frame(grid_container, bg="#ffffff")
        cell_split_frame_BL.grid(row=2, column=0, sticky="nsew")
        cell_split_frame_BL.grid_rowconfigure(0, weight=2)
        cell_split_frame_BL.grid_columnconfigure(0, weight=1)

        mode_config_container = tk.Frame(cell_split_frame_BL, bg="#5862c0")
        mode_config_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        mode_config_container.grid_rowconfigure(0, weight=1) #empty gap
        mode_config_container.grid_rowconfigure(0, weight=1) 
        mode_config_container.grid_columnconfigure(1, weight=0)
        mode_config_container.grid_columnconfigure(2, weight=0)
        mode_config_container.grid_columnconfigure(3, weight=1)

        self.poll_value()

    def create_status_bar(self, target_frame):       
        btn_style = {
            "font": ("Helvetica", 10, "bold"),
            "relief": "groove",
            "bd": 2,
            "padx": 15,
            "pady": 5,
            "activebackground": "#2e0771"
        }

        nav_buttons = [
            ("Home", lambda: self.controller.show_frame(homePage)),
            ("File", lambda: self.open_file_selector())
        ]
        
        for text, command_action in nav_buttons:
            btn = tk.Button(target_frame, text=text, bg="#2e0771", fg="#FFFFFF", 
                            command=command_action, **btn_style)
            btn.pack(side="left", padx=4, pady=5)

        control_buttons = [
            ("Clear", lambda: self.print_click("Dashboard Logs Cleared")),
            ("Stop", lambda: self.print_click("Emergency Output Force OFF")),
            ("Restart", lambda: self.print_click("System Power Loop Restart"))
        ]
        
        for text, command_action in control_buttons:
            btn = tk.Button(target_frame, text=text, bg="#2e0771", fg="#FFFFFF", 
                                command=command_action, **btn_style)
            
            # Packing to the right pins them to the East wall
            btn.pack(side="right", padx=4, pady=5)
    def poll_value(self):
        latest_stage = get_current_system_stage()
        self.lbl_stage_value.config(text=latest_stage)
        latest_error_count = get_current_error_log()
        self.lbl_error_value.config(text=latest_error_count)
        self.after(250, self.poll_value)

        

    def open_file_selector(self):
        print("Place holder for file selection")

    def print_click(self, target_name):
        print(f"[UI EVENT]: User pressed block area linked to -> {target_name}")

    
def get_current_system_stage():
    """
    Placeholder Function.
    Right now: Returns a static mockup status.
    In the future: Will return the active state read from the hardware.
    """
    return "Standby"
def get_current_error_log():
    """
    Placeholder Function.
    Right now: Returns a static mockup error log.
    In the future: Will return the active error log read from the hardware.
    """
    error_log = [
        "Error 1: Overcurrent detected",
        "Error 2: Temperature too high"
    ]
    return len(error_log)