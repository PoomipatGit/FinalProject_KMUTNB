import tkinter as tk
from tkinter import ttk
import time
import pandas as pd
from basePage import BasePage


class canSequencePage(BasePage):
	theme_color = "#135279"  # Dark Teal header
	row_bg = "#DCE2E8"       # Light grey row background

	def __init__(self, parent, controller):
		super().__init__(parent, controller)

		self.is_extended = False
		self._is_running_sequence = False

		# Load command DataFrame
		self.load_command_dataframe()

		# Styling & UI setup
		self.setup_styles()
		self.setup_ui()
		self.setup_debug_console()

	def load_command_dataframe(self):
		"""Loads command DataFrame from CSV or default mock data."""
		data = {
			"name": ["Read_Volt", "Set_Current", "System_Reset", "Read_Temp"],
			"txrx": ["Tx", "Tx", "Tx", "Rx"],
			"identifier": ["02 A3 3F F0", "02 A3 3F F1", "02 A3 F0 3F", "02 A3 3F F2"],
			"can_data": [
				"10 01 00 00 00 00 00 00",
				"10 02 05 00 00 00 00 00",
				"00 00 00 00 00 00 00 00",
				"10 03 00 00 00 00 00 00",
			],
			"comment": ["Read Voltage", "Set 5.0A Limit", "Soft Reset", "Read Internal Temp"],
		}
		self.df_commands = pd.DataFrame(data)

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
		style.map("Custom.Treeview.Heading", background=[("active", "#0d4363")])

		style.configure(
			"Custom.Treeview",
			background=self.row_bg,
			foreground="#000000",
			fieldbackground=self.row_bg,
			rowheight=26,
			font=("Helvetica", 9)
		)

	def setup_ui(self):
		main_container = tk.Frame(self, bg="#ffffff")
		# CHANGE THIS LINE from .pack() to .grid()
		main_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 5))

		# Column indices:
		# #1: Name, #2: TxRx, #3: Identifier, #4: CAN Data, #5: Value, #6: Comment, #7: Action, #8: Result
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

		# Scrollbar
		vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
		self.tree.configure(yscrollcommand=vsb.set)
		vsb.pack(side="right", fill="y")

		# Bindings: Single click for Action execution, Double click for In-place editing
		self.tree.bind("<ButtonRelease-1>", self.on_cell_click)
		self.tree.bind("<Double-1>", self.on_double_click_edit)

		# Initial Rows
		self.tree.insert("", tk.END, values=("Read_Volt", "Tx", "02 A3 3F F0", "10 01 00 00 00 00 00 00", "0.00 V", "Read Voltage", "RUN", "--"))
		self.tree.insert("", tk.END, values=("Set_Current", "Tx", "02 A3 3F F1", "10 02 05 00 00 00 00 00", "5.00 A", "Set 5.0A Limit", "RUN", "--"))
		self.tree.insert("", tk.END, values=("System_Reset", "Tx", "02 A3 F0 3F", "00 00 00 00 00 00 00 00", "--", "Soft Reset", "RUN", "--"))

		# Bottom Frame
		bottom_frame = tk.Frame(main_container, bg=self.theme_color, bd=1, relief="solid")
		bottom_frame.pack(fill="x", pady=(8, 0))

		lbl_add_title = tk.Label(
			bottom_frame,
			text="Add Command (Double-click 'Value' or 'Comment' to edit in-place)",
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
			width=22,
			font=("Helvetica", 9)
		)
		self.combo_cmd_select.pack(side="left", padx=5)
		if cmd_options:
			self.combo_cmd_select.current(0)

		tk.Label(
			input_container,
			text="Init Value:",
			font=("Helvetica", 9, "bold"),
			bg=self.theme_color,
			fg="white"
		).pack(side="left", padx=(15, 6))

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

		btn_add = tk.Button(
			input_container,
			text="Add to Table",
			font=("Helvetica", 8, "bold"),
			bg="#0D3F5E",
			fg="white",
			relief="groove",
			bd=2,
			padx=8,
			command=self.add_command_from_dropdown
		)
		btn_add.pack(side="right", padx=(5, 0))

		btn_remove = tk.Button(
			input_container,
			text="Remove Row",
			font=("Helvetica", 8, "bold"),
			bg="#0D3F5E",
			fg="white",
			relief="groove",
			bd=2,
			padx=8,
			command=self.remove_selected_command
		)
		btn_remove.pack(side="right", padx=5)
	# =========================================================================
	# In-Place Cell Editing Logic
	# =========================================================================
	def on_double_click_edit(self, event):
		"""Spawns an Entry overlay when double-clicking either 'Value' or 'Comment'."""
		region = self.tree.identify_region(event.x, event.y)
		if region != "cell":
			return

		col_id = self.tree.identify_column(event.x)  # e.g., '#5' or '#6'
		item_id = self.tree.identify_row(event.y)

		# 1. Convert #index dynamically to the exact column name in self.tree['columns']
		try:
			col_index = int(col_id.replace("#", "")) - 1
			columns_list = list(self.tree["columns"])
			target_col = columns_list[col_index]
		except (ValueError, IndexError):
			return

		# 2. Only allow inline editing for "Value" and "Comment"
		if target_col not in ["Value", "Comment"]:
			return

		# 3. Get exact bounding box for the clicked cell
		bbox = self.tree.bbox(item_id, column=col_id)
		if not bbox:
			return
		x, y, width, height = bbox

		# 4. Fetch the existing cell value
		current_val = self.tree.set(item_id, column=target_col)

		# 5. Spawn the Entry widget overlay directly over the cell
		entry_edit = tk.Entry(
			self.tree,
			font=("Helvetica", 9),
			justify="center" if target_col == "Value" else "left",
			bg="#FFFFFF",
			fg="#000000",
			relief="solid",
			bd=1,
		)
		entry_edit.insert(0, str(current_val))
		entry_edit.select_range(0, tk.END)
		entry_edit.place(x=x, y=y, width=width, height=height)
		entry_edit.focus_set()

		# Guard flag to prevent double execution (Enter + FocusOut)
		is_saved = False

		def save_and_close(evt=None):
			nonlocal is_saved
			if is_saved:
				return
			is_saved = True

			new_text = entry_edit.get()

			# Update the exact target column
			self.tree.set(item_id, column=target_col, value=new_text)

			cmd_name = self.tree.set(item_id, column="Name")
			self.log_debug(
				f"[UI]: Updated '{cmd_name}' {target_col} -> {new_text}"
			)
			entry_edit.destroy()

		entry_edit.bind("<Return>", save_and_close)
		entry_edit.bind("<FocusOut>", save_and_close)
		entry_edit.bind("<Escape>", lambda evt: entry_edit.destroy())

	# =========================================================================
	# Debug Console & Actions
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
		# CHANGE THIS LINE from .pack() to .grid()
		debug_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))

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

	def add_command_from_dropdown(self):
		selected_name = self.var_selected_cmd.get()
		if not selected_name:
			return

		matched_row = self.df_commands[self.df_commands["name"] == selected_name]
		if matched_row.empty:
			return

		row_data = matched_row.iloc[0]
		val = self.var_init_value.get() or "--"

		self.tree.insert(
			"",
			tk.END,
			values=(
				row_data["name"],
				row_data["txrx"],
				row_data["identifier"],
				row_data["can_data"],
				val,
				row_data["comment"],
				"RUN",
				"--"
			)
		)
		self.log_debug(f"[UI]: Added '{row_data['name']}' (ID: {row_data['identifier']})")

	def remove_selected_command(self):
		selected_items = self.tree.selection()
		if not selected_items:
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

			try:
				col_index = int(col_id.replace("#", "")) - 1
				col_name = self.tree["columns"][col_index]
			except (ValueError, IndexError):
				return

			if col_name == "Action":
				values = self.tree.item(item_id)["values"]
				self.mock_run_single(item_id, values)

	def mock_run_single(self, item_id, values):
		cmd_name, txrx, can_id, can_data, val = values[0], values[1], values[2], values[3], values[4]
		self.tree.set(item_id, column="Result", value="SENDING...")
		self.log_debug(f"[MOCK TX]: {txrx} | Name={cmd_name} | ID={can_id} | Val={val} | DATA=[{can_data}]")

		def finish_single():
			self.tree.set(item_id, column="Result", value="OK")
			self.log_debug(f"[MOCK RX]: Received from ID {can_id} -> Status: PASS")

		self.after(200, finish_single)

	def start_mock_sequence(self):
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
				self.btn_run_seq.config(state="normal", bg="#28A745", text="▶ MOCK RUN ALL SEQUENCE")
				self._is_running_sequence = False
				return

			item_id = all_items[index]
			val = self.tree.item(item_id)["values"]
			self.tree.set(item_id, column="Result", value="SENDING...")
			self.log_debug(f"[STEP {index+1}/{len(all_items)}]: Sending '{val[0]}' (ID: {val[2]}, Value: {val[4]})")

			def step_complete():
				self.tree.set(item_id, column="Result", value="OK")
				self.log_debug(f"[STEP {index+1} RESPONSE]: 0x00 OK")
				self.after(300, lambda: run_step(index + 1))

			self.after(250, step_complete)

		run_step(0)