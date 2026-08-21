import tkinter as tk
from tkinter import ttk
import time
from basePage import BasePage


class canSequencePage(BasePage):
    theme_color = "#135279"  # Dark Teal header matching the template
    row_bg = "#DCE2E8"       # Light grey row background

    def __init__(self, parent, controller):
        # 1. Inherit status bar & container setup from BasePage
        super().__init__(parent, controller)

        self.is_extended = False
        self._is_running_sequence = False

        # 2. Apply styling & build UI components
        self.setup_styles()
        self.setup_ui()
        self.setup_debug_console()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Table Header Styling
        style.configure(
            "Custom.Treeview.Heading",
            background=self.theme_color,
            foreground="white",
            font=("Helvetica", 10, "bold"),
            relief="flat"
        )
        style.map("Custom.Treeview.Heading", background=[("active", "#0d4363")])

        # Table Body Styling
        style.configure(
            "Custom.Treeview",
            background=self.row_bg,
            foreground="#000000",
            fieldbackground=self.row_bg,
            rowheight=26,
            font=("Helvetica", 9)
        )

    def setup_ui(self):
        # Main container with 0 top margin to snap directly below BasePage top bar
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # =====================================================================
        # 1. Main Data Table (Treeview)
        # =====================================================================
        columns = ["Name", "TxRx", "Identifier", "CAN Data", "Comment", "Action", "Result"]

        table_frame = tk.Frame(main_container, bg="#ffffff")
        table_frame.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            height=6
        )
        self.tree.pack(side="left", fill="both", expand=True)

        col_widths = {
            "Name": 90,
            "TxRx": 50,
            "Identifier": 100,
            "CAN Data": 160,
            "Comment": 130,
            "Action": 70,
            "Result": 90
        }

        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        # Vertical Scrollbar
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Cell Click Event Binding
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)

        # Initial Mock Rows
        self.tree.insert("", tk.END, values=("Read_Volt", "Tx", "02 A3 3F F0", "10 01 00 00 00 00 00 00", "Read Voltage", "RUN", "--"))
        self.tree.insert("", tk.END, values=("Set_Current", "Tx", "02 A3 3F F1", "10 02 05 00 00 00 00 00", "Set 5.0A Limit", "RUN", "--"))
        self.tree.insert("", tk.END, values=("System_Reset", "Tx", "02 A3 F0 3F", "00 00 00 00 00 00 00 00", "Soft Reset", "RUN", "--"))

        # =====================================================================
        # 2. Bottom "Add new command" Frame
        # =====================================================================
        bottom_frame = tk.Frame(main_container, bg=self.theme_color, bd=1, relief="solid")
        bottom_frame.pack(fill="x", pady=(8, 0))

        lbl_add_title = tk.Label(
            bottom_frame,
            text="Add new command",
            font=("Helvetica", 11, "bold"),
            bg=self.theme_color,
            fg="white",
            anchor="w"
        )
        lbl_add_title.pack(fill="x", padx=10, pady=(4, 2))

        input_container = tk.Frame(bottom_frame, bg=self.theme_color)
        input_container.pack(fill="x", padx=10, pady=(0, 6))

        fields_frame = tk.Frame(input_container, bg=self.theme_color)
        fields_frame.pack(side="left", fill="x", expand=True)

        self.var_name = tk.StringVar()
        self.var_txrx = tk.StringVar(value="Tx")
        self.var_id = tk.StringVar()
        self.var_data = tk.StringVar()
        self.var_comment = tk.StringVar()
        self.var_action = tk.StringVar(value="RUN")

        input_cols = ["Name", "TxRx", "Identifier", "CAN Data", "Comment", "Action"]
        vars_dict = {
            "Name": self.var_name,
            "TxRx": self.var_txrx,
            "Identifier": self.var_id,
            "CAN Data": self.var_data,
            "Comment": self.var_comment,
            "Action": self.var_action
        }

        for idx, col_name in enumerate(input_cols):
            fields_frame.columnconfigure(idx, weight=1)

            lbl_header = tk.Label(
                fields_frame,
                text=col_name,
                font=("Helvetica", 9, "bold"),
                bg=self.theme_color,
                fg="white",
                bd=1,
                relief="solid",
                anchor="center"
            )
            lbl_header.grid(row=0, column=idx, sticky="ew", padx=1, pady=(0, 2))

            if col_name == "TxRx":
                widget = ttk.Combobox(
                    fields_frame,
                    textvariable=self.var_txrx,
                    values=["Tx", "Rx"],
                    state="readonly",
                    width=4,
                    justify="center"
                )
            elif col_name == "Action":
                widget = ttk.Combobox(
                    fields_frame,
                    textvariable=self.var_action,
                    values=["RUN", "SEND", "READ"],
                    state="readonly",
                    width=5,
                    justify="center"
                )
            else:
                widget = tk.Entry(
                    fields_frame,
                    textvariable=vars_dict[col_name],
                    bg=self.row_bg,
                    fg="#000000",
                    justify="center",
                    relief="flat"
                )

            widget.grid(row=1, column=idx, sticky="ew", padx=1, ipady=2)

        # Right Stacked Action Buttons (Remove & Add)
        buttons_frame = tk.Frame(input_container, bg=self.theme_color)
        buttons_frame.pack(side="right", padx=(10, 0))

        btn_remove = tk.Button(
            buttons_frame,
            text="Remove",
            font=("Helvetica", 8, "bold"),
            bg="#0D3F5E",
            fg="white",
            activebackground="#082A3F",
            activeforeground="white",
            relief="groove",
            bd=2,
            width=9,
            command=self.remove_selected_command
        )
        btn_remove.pack(side="top", pady=(0, 2))

        btn_add = tk.Button(
            buttons_frame,
            text="Add",
            font=("Helvetica", 8, "bold"),
            bg="#0D3F5E",
            fg="white",
            activebackground="#082A3F",
            activeforeground="white",
            relief="groove",
            bd=2,
            width=9,
            command=self.add_new_command
        )
        btn_add.pack(side="bottom")

    # =========================================================================
    # 3. Debug Console & Mock Execution Toolbar
    # =========================================================================
    def setup_debug_console(self):
        debug_container = tk.LabelFrame(
            self,
            text=" Debug / Mock CAN Console ",
            font=("Helvetica", 10, "bold"),
            bg="#ffffff",
            fg=self.theme_color,
            padx=5,
            pady=5
        )
        debug_container.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Toolbar Frame
        toolbar = tk.Frame(debug_container, bg="#ffffff")
        toolbar.pack(fill="x", pady=(0, 5))

        self.btn_run_seq = tk.Button(
            toolbar,
            text="▶ MOCK RUN ALL SEQUENCE",
            font=("Helvetica", 9, "bold"),
            bg="#28A745",
            fg="white",
            activebackground="#1E7E34",
            activeforeground="white",
            relief="groove",
            bd=2,
            padx=10,
            command=self.start_mock_sequence
        )
        self.btn_run_seq.pack(side="left", padx=2)

        btn_clear_log = tk.Button(
            toolbar,
            text="Clear Log",
            font=("Helvetica", 9),
            bg="#6C757D",
            fg="white",
            relief="groove",
            bd=2,
            command=self.clear_debug_log
        )
        btn_clear_log.pack(side="left", padx=5)

        # Log Output Window
        log_frame = tk.Frame(debug_container, bg="#ffffff")
        log_frame.pack(fill="both", expand=True)

        self.txt_debug = tk.Text(
            log_frame,
            height=6,
            bg="#1E1E1E",
            fg="#00FF66",
            font=("Consolas", 9),
            bd=1,
            relief="solid",
            wrap="word"
        )
        self.txt_debug.pack(side="left", fill="both", expand=True)

        log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_debug.yview)
        self.txt_debug.configure(yscrollcommand=log_vsb.set)
        log_vsb.pack(side="right", fill="y")

        self.log_debug("--- Debug CAN Engine Initialized. Ready for Mock Execution ---")

    def log_debug(self, message):
        t_stamp = time.strftime("[%H:%M:%S]")
        self.txt_debug.insert(tk.END, f"{t_stamp} {message}\n")
        self.txt_debug.see(tk.END)

    def clear_debug_log(self):
        self.txt_debug.delete("1.0", tk.END)
        self.log_debug("Console log cleared.")

    # =========================================================================
    # Action Handlers & Logic
    # =========================================================================
    def add_new_command(self):
        name = self.var_name.get() or "Cmd_New"
        txrx = self.var_txrx.get() or "Tx"
        can_id = self.var_id.get() or "02 A3 00 00"
        can_data = self.var_data.get() or "00 00 00 00 00 00 00 00"
        comment = self.var_comment.get() or "Custom Command"
        action = self.var_action.get() or "RUN"

        self.tree.insert("", tk.END, values=(name, txrx, can_id, can_data, comment, action, "--"))
        self.log_debug(f"[UI]: Added new command entry -> {name} ({can_id})")

        self.var_name.set("")
        self.var_id.set("")
        self.var_data.set("")
        self.var_comment.set("")

    def remove_selected_command(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.log_debug("[WARN]: Select a table row to remove.")
            return
        for item in selected_items:
            val = self.tree.item(item)["values"]
            self.log_debug(f"[UI]: Removed command -> {val[0]}")
            self.tree.delete(item)

    def on_cell_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            col_id = self.tree.identify_column(event.x)
            item_id = self.tree.identify_row(event.y)
            values = self.tree.item(item_id)["values"]

            # Column #6 is Action column
            if col_id == "#6":
                self.mock_run_single(item_id, values)

    def mock_run_single(self, item_id, values):
        """Simulates individual row execution"""
        cmd_name, txrx, can_id, can_data = values[0], values[1], values[2], values[3]
        
        self.tree.set(item_id, column="Result", value="SENDING...")
        self.log_debug(f"[MOCK TX]: {txrx} | Name={cmd_name} | ID={can_id} | DATA=[{can_data}]")

        def finish_single():
            self.tree.set(item_id, column="Result", value="OK")
            self.log_debug(f"[MOCK RX]: Received from ID {can_id} -> Status: PASS")

        self.after(200, finish_single)

    def start_mock_sequence(self):
        """Sequential Execution Runner"""
        if self._is_running_sequence:
            return

        all_items = self.tree.get_children()
        if not all_items:
            self.log_debug("[WARN]: No sequence items to run.")
            return

        self._is_running_sequence = True
        self.btn_run_seq.config(state="disabled", bg="#6C757D", text="RUNNING...")
        self.log_debug("--- [START MOCK SEQUENCE EXECUTION] ---")

        for item in all_items:
            self.tree.set(item, column="Result", value="PENDING")

        def run_step(index):
            if index >= len(all_items):
                self.log_debug("--- [SEQUENCE COMPLETED SUCCESSFULLY] ---")
                self.btn_run_seq.config(state="normal", bg="#28A745", text="RUN ALL SEQUENCE")
                self._is_running_sequence = False
                return

            item_id = all_items[index]
            val = self.tree.item(item_id)["values"]
            
            self.tree.set(item_id, column="Result", value="SENDING...")
            self.log_debug(f"[STEP {index+1}/{len(all_items)}]: Sending '{val[0]}' (ID: {val[2]})")

            def step_complete():
                self.tree.set(item_id, column="Result", value="OK ")
                self.log_debug(f"[STEP {index+1} RESPONSE]: 0x00 OK")
                self.after(300, lambda: run_step(index + 1))

            self.after(250, step_complete)

        run_step(0)


