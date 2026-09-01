import tkinter as tk
from tkinter import ttk, messagebox
import time
import pandas as pd
from basePage import BasePage


class canMessageCommand(BasePage):
    theme_color = "#135279"  # Dark Teal header matching the template[cite: 1]
    row_bg = "#DCE2E8"       # Light grey row background[cite: 1]

    # Standard registered command schema
    CMD_COLUMNS = ["name", "txrx", "identifier", "can_data", "comment", "action", "result"]

    def __init__(self, parent, controller=None):
        super().__init__(parent, controller)

        self.is_extended = False
        self._is_running_sequence = False

        # 2. Single Source of Truth (SSOT): Empty DataFrame (No initial hardcoded rows)
        self.df_commands = pd.DataFrame(columns=self.CMD_COLUMNS)

        # 3. Apply styling & build UI components via .grid()[cite: 1]
        self.setup_styles()
        self.setup_ui()
        self.setup_debug_console()

        # 4. Render initial view
        self.render_dataframe_to_tree()

    def render_dataframe_to_tree(self):
        """Synchronizes the Treeview visual rows from self.df_commands."""
        self.tree.delete(*self.tree.get_children())
        for idx, row in self.df_commands.iterrows():
            # iid is bound directly to DataFrame integer index for direct O(1) row access
            self.tree.insert("", tk.END, iid=str(idx), values=list(row))

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Table Header Styling[cite: 1]
        style.configure(
            "Custom.Treeview.Heading",
            background=self.theme_color,
            foreground="white",
            font=("Helvetica", 10, "bold"),
            relief="flat"
        )
        style.map("Custom.Treeview.Heading", background=[("active", "#0d4363")])

        # Table Body Styling[cite: 1]
        style.configure(
            "Custom.Treeview",
            background=self.row_bg,
            foreground="#000000",
            fieldbackground=self.row_bg,
            rowheight=26,
            font=("Helvetica", 9)
        )

    def setup_ui(self):
        # Main container placed at row=1 (directly below BasePage top status bar at row=0)[cite: 1]
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

        # Ensure row 1 expands inside self[cite: 1]
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # =====================================================================
        # 1. Main Data Table (Treeview)[cite: 1]
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

        # Vertical Scrollbar[cite: 1]
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Cell Click Event Binding[cite: 1]
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)

        # =====================================================================
        # 2. Bottom "Add new command" Frame[cite: 1]
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

        # Right Stacked Action Buttons (Remove & Add)[cite: 1]
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
    # 3. Debug Console & Execution Toolbar[cite: 1]
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
        debug_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        self.grid_rowconfigure(2, weight=1)

        # Toolbar Frame[cite: 1]
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

        # Log Output Window[cite: 1]
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

        self.log_debug("--- Debug CAN Engine Initialized. Ready for Execution ---")

    def log_debug(self, message):
        t_stamp = time.strftime("[%H:%M:%S]")
        self.txt_debug.insert(tk.END, f"{t_stamp} {message}\n")
        self.txt_debug.see(tk.END)

    def clear_debug_log(self):
        self.txt_debug.delete("1.0", tk.END)
        self.log_debug("Console log cleared.")

    # =========================================================================
    # DataFrame CRUD Operations
    # =========================================================================
    def add_new_command(self):
        name = self.var_name.get().strip() or "Cmd_New"
        txrx = self.var_txrx.get() or "Tx"
        can_id = self.var_id.get().strip() or "02 A3 00 00"
        can_data = self.var_data.get().strip() or "00 00 00 00 00 00 00 00"
        comment = self.var_comment.get().strip() or "Custom Command"
        action = self.var_action.get() or "RUN"

        new_row = {
            "name": name,
            "txrx": txrx,
            "identifier": can_id,
            "can_data": can_data,
            "comment": comment,
            "action": action,
            "result": "--"
        }

        # Append directly to DataFrame and sync to Treeview
        self.df_commands = pd.concat([self.df_commands, pd.DataFrame([new_row])], ignore_index=True)
        self.render_dataframe_to_tree()
        self.log_debug(f"[DF]: Added command '{name}' (ID: {can_id})")

        # Clear input boxes
        self.var_name.set("")
        self.var_id.set("")
        self.var_data.set("")
        self.var_comment.set("")

    def remove_selected_command(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.log_debug("[WARN]: Select a table row to remove.")
            return

        indices_to_drop = [int(item_id) for item_id in selected_items if item_id.isdigit()]
        self.df_commands = self.df_commands.drop(index=indices_to_drop).reset_index(drop=True)
        self.render_dataframe_to_tree()
        self.log_debug(f"[DF]: Removed command index(es) {indices_to_drop}")

    # =========================================================================
    # Execution Logic (Operating on DataFrame Records)
    # =========================================================================
    def on_cell_click(self, event):
        region = self.tree.identify_region(event.x, event.y)
        if region == "cell":
            col_id = self.tree.identify_column(event.x)
            item_id = self.tree.identify_row(event.y)

            # Column #6 corresponds to the Action ("RUN") column
            if col_id == "#6" and item_id.isdigit():
                idx = int(item_id)
                self.mock_run_single(idx)

    def mock_run_single(self, idx):
        """Simulates individual row execution using DataFrame lookup."""
        row_data = self.df_commands.iloc[idx]
        cmd_name, txrx, can_id, can_data = row_data["name"], row_data["txrx"], row_data["identifier"], row_data["can_data"]

        self.df_commands.at[idx, "result"] = "SENDING..."
        self.tree.set(str(idx), column="Result", value="SENDING...")
        self.log_debug(f"[MOCK TX]: {txrx} | Name={cmd_name} | ID={can_id} | DATA=[{can_data}]")

        def finish_single():
            self.df_commands.at[idx, "result"] = "OK"
            self.tree.set(str(idx), column="Result", value="OK")
            self.log_debug(f"[MOCK RX]: Received response from ID {can_id} -> Status: PASS")

        self.after(200, finish_single)

    def start_mock_sequence(self):
        """Sequential Execution Runner iterating through self.df_commands."""
        if self._is_running_sequence or self.df_commands.empty:
            if self.df_commands.empty:
                self.log_debug("[WARN]: No commands loaded to run.")
            return

        self._is_running_sequence = True
        self.btn_run_seq.config(state="disabled", bg="#6C757D", text="RUNNING...")
        self.log_debug("--- [START MOCK SEQUENCE EXECUTION] ---")

        for i in range(len(self.df_commands)):
            self.df_commands.at[i, "result"] = "PENDING"
            self.tree.set(str(i), column="Result", value="PENDING")

        def run_step(index):
            if index >= len(self.df_commands):
                self.log_debug("--- [SEQUENCE COMPLETED SUCCESSFULLY] ---")
                self.btn_run_seq.config(state="normal", bg="#28A745", text="▶ MOCK RUN ALL SEQUENCE")
                self._is_running_sequence = False
                return

            row = self.df_commands.iloc[index]
            self.df_commands.at[index, "result"] = "SENDING..."
            self.tree.set(str(index), column="Result", value="SENDING...")
            self.log_debug(f"[STEP {index+1}/{len(self.df_commands)}]: Sending '{row['name']}' (ID: {row['identifier']})")

            def step_complete():
                self.df_commands.at[index, "result"] = "OK"
                self.tree.set(str(index), column="Result", value="OK")
                self.log_debug(f"[STEP {index+1} RESPONSE]: 0x00 OK")
                self.after(300, lambda: run_step(index + 1))

            self.after(250, step_complete)

        run_step(0)

    # =========================================================================
    # BasePage File Hooks (DataFrame Native)
    # =========================================================================
    def get_dataframe(self) -> pd.DataFrame:
        """Pulls the current command list as a DataFrame for BasePage to save."""
        # 1. If DataFrame has records, return it directly
        if hasattr(self, "df_commands") and not self.df_commands.empty:
            return self.df_commands

        # 2. Fallback: Rebuild DataFrame directly from Treeview rows
        if hasattr(self, "tree"):
            rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
            if rows:
                cols = [c.lower() for c in self.CMD_COLUMNS]
                self.df_commands = pd.DataFrame(rows, columns=cols[:len(rows[0])])
                return self.df_commands

        return pd.DataFrame(columns=self.CMD_COLUMNS)

    def load_dataframe(self, new_df: pd.DataFrame):
        """Called automatically by BasePage to load a command list CSV into memory."""
        self.df_commands = new_df.reset_index(drop=True)
        for col in self.CMD_COLUMNS:
            if col not in self.df_commands.columns:
                self.df_commands[col] = "RUN" if col == "action" else "--"
        self.render_dataframe_to_tree()
        self.log_debug(f"[FILE]: Loaded {len(self.df_commands)} commands from CSV")