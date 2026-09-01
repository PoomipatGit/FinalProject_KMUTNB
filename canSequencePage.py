import tkinter as tk
from tkinter import ttk
import time
import pandas as pd
from basePage import BasePage


class canSequencePage(BasePage):
    theme_color = "#135279"
    row_bg = "#DCE2E8"

    # Standard columns matching the DataFrame and Treeview architecture
    SEQ_COLUMNS = ["name", "txrx", "identifier", "can_data", "value", "comment", "action", "result"]

    def __init__(self, parent, controller=None):
        super().__init__(parent, controller)

        self.is_extended = False
        self._is_running_sequence = False

        # 1. Single Source of Truth (SSOT): Empty Sequence DataFrame
        self.df_sequence = pd.DataFrame(columns=self.SEQ_COLUMNS)

        # 2. Registered commands database (lookup schema)
        self.load_command_database()

        # 3. Build UI Layout using .grid to avoid geometry manager conflicts with BasePage
        self.setup_styles()
        self.setup_ui()
        self.setup_debug_console()

        # 4. Render initial empty view
        self.render_dataframe_to_tree()

    def load_command_database(self):
        """Initializes the empty registered commands DataFrame."""
        self.df_commands = pd.DataFrame(columns=["name", "txrx", "identifier", "can_data", "comment"])

    def update_command_dataframe(self, new_df: pd.DataFrame):
        """Refreshes available options in the dropdown when a new database is loaded."""
        self.df_commands = new_df
        options = self.df_commands["name"].tolist() if not self.df_commands.empty else []
        self.combo_cmd_select["values"] = options
        if options:
            self.combo_cmd_select.current(0)
            self.var_selected_cmd.set(options[0])
        else:
            self.var_selected_cmd.set("")

    def render_dataframe_to_tree(self):
        """Synchronizes the Treeview visual rows from the DataFrame."""
        self.tree.delete(*self.tree.get_children())
        for idx, row in self.df_sequence.iterrows():
            # iid is bound directly to the DataFrame index for direct O(1) row access
            self.tree.insert("", tk.END, iid=str(idx), values=list(row))

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Custom.Treeview.Heading",
            background=self.theme_color,
            foreground="white",
            font=("Helvetica", 10, "bold"),
            relief="flat"
        )
        style.configure(
            "Custom.Treeview",
            background=self.row_bg,
            foreground="#000000",
            fieldbackground=self.row_bg,
            rowheight=26,
            font=("Helvetica", 9)
        )

    def setup_ui(self):
        # Mounted at row 1 via .grid() to sit right below the BasePage status bar at row 0
        main_container = tk.Frame(self, bg="#ffffff")
        main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        columns = ["Name", "TxRx", "Identifier", "CAN Data", "Value", "Comment", "Action", "Result"]

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
            "Identifier": 90,
            "CAN Data": 150,
            "Value": 80,
            "Comment": 130,
            "Action": 60,
            "Result": 80
        }
        for col in columns:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=col_widths.get(col, 100), anchor="center")

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")

        # Single-click executes RUN; Double-click opens inline cell editor for Value & Comment
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)
        self.tree.bind("<Double-1>", self.on_double_click_edit)

        # Bottom Add Step Frame
        bottom_frame = tk.Frame(main_container, bg=self.theme_color, bd=1, relief="solid")
        bottom_frame.pack(fill="x", pady=(8, 0))

        lbl_add_title = tk.Label(
            bottom_frame,
            text="Add Sequence Step (Double-click 'Value' or 'Comment' to edit in-place)",
            font=("Helvetica", 10, "bold"),
            bg=self.theme_color,
            fg="white",
            anchor="w"
        )
        lbl_add_title.pack(fill="x", padx=10, pady=(4, 2))

        input_container = tk.Frame(bottom_frame, bg=self.theme_color)
        input_container.pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(
            input_container,
            text="Select Command:",
            font=("Helvetica", 9, "bold"),
            bg=self.theme_color,
            fg="white"
        ).pack(side="left", padx=(0, 6))

        self.var_selected_cmd = tk.StringVar()
        cmd_options = self.df_commands["name"].tolist() if not self.df_commands.empty else []
        self.combo_cmd_select = ttk.Combobox(
            input_container,
            textvariable=self.var_selected_cmd,
            values=cmd_options,
            state="readonly",
            width=20,
            font=("Helvetica", 9)
        )
        self.combo_cmd_select.pack(side="left", padx=5)
        if cmd_options:
            self.combo_cmd_select.current(0)

        tk.Label(
            input_container,
            text="Value:",
            font=("Helvetica", 9, "bold"),
            bg=self.theme_color,
            fg="white"
        ).pack(side="left", padx=(10, 4))

        self.var_init_value = tk.StringVar(value="--")
        self.ent_value = tk.Entry(
            input_container,
            textvariable=self.var_init_value,
            bg=self.row_bg,
            fg="#000000",
            width=10,
            justify="center",
            relief="flat"
        )
        self.ent_value.pack(side="left", padx=5, ipady=2)

        tk.Button(
            input_container,
            text="Add Step",
            font=("Helvetica", 8, "bold"),
            bg="#0D3F5E",
            fg="white",
            relief="groove",
            bd=2,
            padx=8,
            command=self.add_step_to_dataframe
        ).pack(side="right", padx=(5, 0))

        tk.Button(
            input_container,
            text="Remove Step",
            font=("Helvetica", 8, "bold"),
            bg="#0D3F5E",
            fg="white",
            relief="groove",
            bd=2,
            padx=8,
            command=self.remove_step_from_dataframe
        ).pack(side="right", padx=5)

    def setup_debug_console(self):
        # Mounted at row 2 via .grid()
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

        toolbar = tk.Frame(debug_container, bg="#ffffff")
        toolbar.pack(fill="x", pady=(0, 5))

        self.btn_run_seq = tk.Button(
            toolbar,
            text="▶ RUN DATAFRAME SEQUENCE",
            font=("Helvetica", 9, "bold"),
            bg="#28A745",
            fg="white",
            relief="groove",
            bd=2,
            padx=10,
            command=self.start_dataframe_sequence
        )
        self.btn_run_seq.pack(side="left", padx=2)

        tk.Button(
            toolbar,
            text="Clear Log",
            font=("Helvetica", 9),
            bg="#6C757D",
            fg="white",
            relief="groove",
            bd=2,
            command=lambda: self.txt_debug.delete("1.0", tk.END)
        ).pack(side="left", padx=5)

        log_frame = tk.Frame(debug_container, bg="#ffffff")
        log_frame.pack(fill="both", expand=True)

        self.txt_debug = tk.Text(
            log_frame,
            height=5,
            bg="#1E1E1E",
            fg="#00FF66",
            font=("Consolas", 9),
            relief="solid",
            wrap="word"
        )
        self.txt_debug.pack(side="left", fill="both", expand=True)

        log_vsb = ttk.Scrollbar(log_frame, orient="vertical", command=self.txt_debug.yview)
        self.txt_debug.configure(yscrollcommand=log_vsb.set)
        log_vsb.pack(side="right", fill="y")

    def log_debug(self, msg):
        self.txt_debug.insert(tk.END, f"{time.strftime('[%H:%M:%S]')} {msg}\n")
        self.txt_debug.see(tk.END)

    # -------------------------------------------------------------------------
    # DataFrame CRUD Operations
    # -------------------------------------------------------------------------

    def add_step_to_dataframe(self):
        selected_name = self.var_selected_cmd.get()
        if not selected_name:
            self.log_debug("[WARN]: No command selected to add.")
            return

        matched = self.df_commands[self.df_commands["name"] == selected_name]
        if matched.empty:
            self.log_debug(f"[WARN]: Command '{selected_name}' not found in registry.")
            return

        cmd = matched.iloc[0]
        new_row = {
            "name": cmd["name"],
            "txrx": cmd["txrx"],
            "identifier": cmd["identifier"],
            "can_data": cmd["can_data"],
            "value": self.var_init_value.get() or "--",
            "comment": cmd["comment"],
            "action": "RUN",
            "result": "--"
        }
        self.df_sequence = pd.concat([self.df_sequence, pd.DataFrame([new_row])], ignore_index=True)
        self.render_dataframe_to_tree()
        self.log_debug(f"[DF]: Added step '{selected_name}' (Total steps: {len(self.df_sequence)})")

    def remove_step_from_dataframe(self):
        selected_items = self.tree.selection()
        if not selected_items:
            self.log_debug("[WARN]: Select a step in the table to remove.")
            return

        indices_to_drop = [int(item_id) for item_id in selected_items if item_id.isdigit()]
        self.df_sequence = self.df_sequence.drop(index=indices_to_drop).reset_index(drop=True)
        self.render_dataframe_to_tree()
        self.log_debug(f"[DF]: Removed sequence step(s) {indices_to_drop}")

    def on_double_click_edit(self, event):
        """In-place cell editing that updates both the DataFrame and Treeview."""
        if self.tree.identify_region(event.x, event.y) != "cell":
            return

        col_id = self.tree.identify_column(event.x)
        item_id = self.tree.identify_row(event.y)

        col_map = {"#5": "value", "#6": "comment"}
        if col_id not in col_map or not item_id.isdigit():
            return

        target_col = col_map[col_id]
        idx = int(item_id)
        x, y, w, h = self.tree.bbox(item_id, column=col_id)
        current_val = str(self.df_sequence.at[idx, target_col])

        entry_edit = tk.Entry(
            self.tree,
            font=("Helvetica", 9),
            justify="center" if target_col == "value" else "left",
            bg="#FFFFFF",
            relief="solid",
            bd=1
        )
        entry_edit.insert(0, current_val)
        entry_edit.select_range(0, tk.END)
        entry_edit.place(x=x, y=y, width=w, height=h)
        entry_edit.focus_set()

        def save_edit(evt=None):
            new_text = entry_edit.get()
            self.df_sequence.at[idx, target_col] = new_text
            self.tree.set(item_id, column=target_col.capitalize(), value=new_text)
            self.log_debug(f"[DF UPDATE]: Step {idx} [{target_col}] -> {new_text}")
            entry_edit.destroy()

        entry_edit.bind("<Return>", save_edit)
        entry_edit.bind("<FocusOut>", save_edit)
        entry_edit.bind("<Escape>", lambda e: entry_edit.destroy())

    # -------------------------------------------------------------------------
    # Execution Logic directly from DataFrame
    # -------------------------------------------------------------------------

    def on_cell_click(self, event):
        if self.tree.identify_region(event.x, event.y) == "cell" and self.tree.identify_column(event.x) == "#7":
            item_id = self.tree.identify_row(event.y)
            if item_id.isdigit():
                idx = int(item_id)
                row_data = self.df_sequence.iloc[idx]
                self.log_debug(f"[EXEC SINGLE]: Sending ID={row_data['identifier']} DATA={row_data['can_data']}")
                self.df_sequence.at[idx, "result"] = "OK"
                self.tree.set(item_id, column="Result", value="OK")

    def start_dataframe_sequence(self):
        if self._is_running_sequence or self.df_sequence.empty:
            if self.df_sequence.empty:
                self.log_debug("[WARN]: No sequence steps loaded to run.")
            return

        self._is_running_sequence = True
        self.btn_run_seq.config(state="disabled", text="RUNNING...")
        self.log_debug("--- [STARTING DATAFRAME SEQUENCE EXECUTION] ---")

        for idx in range(len(self.df_sequence)):
            self.df_sequence.at[idx, "result"] = "PENDING"
            self.tree.set(str(idx), column="Result", value="PENDING")

        def run_step(idx):
            if idx >= len(self.df_sequence):
                self.log_debug("--- [DATAFRAME SEQUENCE FINISHED] ---")
                self.btn_run_seq.config(state="normal", text="▶ RUN DATAFRAME SEQUENCE")
                self._is_running_sequence = False
                return

            row = self.df_sequence.iloc[idx]
            self.df_sequence.at[idx, "result"] = "SENDING..."
            self.tree.set(str(idx), column="Result", value="SENDING...")
            self.log_debug(f"[STEP {idx+1}/{len(self.df_sequence)}]: {row['name']} -> ID: {row['identifier']} Val: {row['value']}")

            def step_done():
                self.df_sequence.at[idx, "result"] = "OK"
                self.tree.set(str(idx), column="Result", value="OK")
                self.after(250, lambda: run_step(idx + 1))

            self.after(200, step_done)

        run_step(0)

    # -------------------------------------------------------------------------
    # BasePage File Hooks (DataFrame Native)
    # -------------------------------------------------------------------------

    def get_dataframe(self) -> pd.DataFrame:
        """Called by BasePage to save the sequence to CSV."""
        return self.df_sequence

    def load_dataframe(self, new_df: pd.DataFrame):
        """Called by BasePage to load an external sequence CSV into memory."""
        self.df_sequence = new_df.reset_index(drop=True)
        self.render_dataframe_to_tree()
        self.log_debug(f"[FILE]: Loaded sequence from CSV ({len(self.df_sequence)} steps)")