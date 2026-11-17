import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

root = tk.Tk()
root.geometry("800x480")

CAN_STORAGE = [
    ["0", "02 A3 3F F0", "10 01 00 00 00 00 00 00"," ", "Read Voltage"],["Res0","02 A3 3F 1","10 01 00 00 00 00 00 00","V" , "Read Voltage"],
    ["1", "02 A3 F0 3F", "00 00 00 00 00 00 00 00"," ", "Reset System"],["Res1","02 A3 3F F2","10 01 00 00 00 00 00 00"," " , "Reset"]
]







def run_instant_logic(row_values,is_extended):
	"""Function to handle the individual row execution"""
	can_id = row_values[1]
	can_data = row_values[2]
	
	mode = "29-bit" if is_extended else "11-bit"
    
	print(f"Instant RUN")
	print(f"Direct Run: Sending ID {can_id} with Data {can_data} .......implement later by P'ARM")
	"""put function here"""
	
def run_setup_sequence(commands, is_extended):
	print(f"--- Starting Setup Sequence (Total: {len(commands)} steps) ---")
    
	for row in commands:
		run_instant_logic(row, is_extended)       
	print("--- Setup Sequence Finished ---")


class CAN_GUI :
	def __init__(self,master,run_func):
		self.master=master
		self.run_command = run_func
		master.title("CAN Bus Tool")
	
		self.bottom_controls = ttk.Frame(master)
		self.bottom_controls.pack(side="top", fill="x", padx=10, pady=5)
		
		self.is_extended = False
		
		self.address_btn = ttk.Button(self.bottom_controls, text="Simple Address", command=self.set_address_mode)
		self.address_btn.pack(side="right", padx=5)
		
		self.SetSave_btn = ttk.Button(self.bottom_controls, text="Save", command=self.set_save)
		self.SetSave_btn.pack(side="left", padx=10)
		self.Setload_btn = ttk.Button(self.bottom_controls, text="Load", command=self.set_load)
		self.Setload_btn.pack(side="left", padx=10)
		
	#create tab notebook
		self.notebook = ttk.Notebook(master)
		self.notebook.pack(pady=10, padx=10, expand=True, fill="both")
		
	#create each tap
		self.tab_instant1 = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_instant1, text="Instant")
		"""
		self.tab_instant2 = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_instant2, text="Tap 2 : Instant2")
        """
		self.tab_setup = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_setup, text="Setup")
        
		self.tab_loop = ttk.Frame(self.notebook)
		self.notebook.add(self.tab_loop, text="Loop")
	
	#setup root
		#create table
		self.create_setup_table(self.tab_setup)
		self.create_instant_table(self.tab_instant1)
	
	def set_address_mode(self):
		"""Toggle between Simple and Extended modes"""
		self.is_extended = not self.is_extended # Flip the state
		
		if self.is_extended:
			# Change to Extended Mode
			self.address_btn.config(
				text="Mode: Extended Address (29-bit)"
			)
			print("Global Setting: Extended Addressing Active")
		else:
			# Change to Simple Mode
			self.address_btn.config(
				text="Mode: Simple Address (11-bit)"
			)
			print("Global Setting: Simple Addressing Active")
	def set_save(self):
		print("Saving setting")
	
	
	def set_load(self):
		print("Load setting")
		
	
			
			
        
	def create_instant_table(self, tab_frame):
   
		columns = ["No.", "Identifier", "Data", "Value", "Comment", "Action"]
    
    
		self.tree_instant = ttk.Treeview(tab_frame, columns=columns, show='headings')
    
		for col in columns:
			self.tree_instant.heading(col, text=col, anchor=tk.W)
			if col == "No.": self.tree_instant.column(col, width=40)
			elif col == "Action": self.tree_instant.column(col, width=60, anchor="center")
			else: self.tree_instant.column(col, width=120)


		vsb = ttk.Scrollbar(tab_frame, orient="vertical", command=self.tree_instant.yview)
		self.tree_instant.configure(yscrollcommand=vsb.set)
		vsb.pack(side="right", fill="y")
		"""self.tree_instant.pack(side="left", expand=True, fill="both")"""
		
		input_frame = ttk.LabelFrame(tab_frame, text="Add New Command")
		input_frame.pack(side="bottom", fill="x", padx=10, pady=10)
   
		self.new_id_var = tk.StringVar()
		self.new_data_var = tk.StringVar()
		self.new_comment_var = tk.StringVar()
        
		ttk.Label(input_frame, text="ID:").grid(row=0, column=0, padx=5)
		ttk.Entry(input_frame, textvariable=self.new_id_var, width=15).grid(row=0, column=1, padx=5)
        
		ttk.Label(input_frame, text="Data:").grid(row=0, column=2, padx=5)
		ttk.Entry(input_frame, textvariable=self.new_data_var, width=25).grid(row=0, column=3, padx=5)
        
		ttk.Label(input_frame, text="Comment:").grid(row=0, column=4, padx=5)
		ttk.Entry(input_frame, textvariable=self.new_comment_var, width=18).grid(row=0, column=5, padx=5)
        
		add_btn = ttk.Button(input_frame, text="Add Row", command=self.add_new_command)
		add_btn.grid(row=0, column=6, padx=10, pady=5)
		
		delete_btn = ttk.Button(input_frame, text="Delete Selected", command=self.delete_selected_row)
		delete_btn.grid(row=0, column=7, padx=10, pady=5)
       
		self.tree_instant.pack(side="top", expand=True, fill="both")
		
		

   
		
		for row in CAN_STORAGE:
			row_no = row[0]
			if row_no.isdigit():
				display_values = list(row) + ["RUN"]
			else:
				display_values = list(row) + [""]
			self.tree_instant.insert('', tk.END, values=display_values)
			
		self.refresh_table()
		self.tree_instant.bind("<ButtonRelease-1>", self.on_instant_click)
			

	def on_instant_click(self, event):
		"""Detects if the user clicked the 'Action' column"""
		region = self.tree_instant.identify_region(event.x, event.y)
		if region == "cell":
			# Identify which column was clicked
			column = self.tree_instant.identify_column(event.x)
			item_id = self.tree_instant.identify_row(event.y)
        
			# Column #6 is the 'Action' column
			if column == "#6":
				values = self.tree_instant.item(item_id)['values']
				if values[5] == "RUN": # Only execute if it's a Run row
					self.run_command(values, self.is_extended)
	
        
	def add_new_command(self):
		existing_numbers = [int(r[0]) for r in CAN_STORAGE if r[0].isdigit()]
		next_no = max(existing_numbers) + 1 if existing_numbers else 0
        

		new_id = self.new_id_var.get() or "00 00 00 00"
		new_data = self.new_data_var.get() or "00 00 00 00 00 00 00 00"
		new_comment = self.new_comment_var.get() or "New Command"
        

		CAN_STORAGE.append([str(next_no), new_id, new_data, " ", new_comment])
		CAN_STORAGE.append([f"Res{next_no}"])
        

		self.new_id_var.set("")
		self.new_data_var.set("")
		self.new_comment_var.set("")
		self.refresh_table()
		self.update_setup_dropdown()
	
	def delete_selected_row(self):
		selected_item = self.tree_instant.selection()
        
		if not selected_item:
			print("Please select a row to delete")
			return

		idx = self.tree_instant.index(selected_item[0])
        
		row_values = self.tree_instant.item(selected_item[0])['values']
		row_no = str(row_values[0])
        
		if "Res" in row_no:
			start_idx = idx - 1
		else:
			start_idx = idx

		if start_idx >= 0 and start_idx < len(CAN_STORAGE):
			del CAN_STORAGE[start_idx : start_idx + 2]
			print(f"Deleted rows at index {start_idx} and {start_idx + 1}")
		self.refresh_table()
		self.update_setup_dropdown()
 
	def refresh_table(self):

		for item in self.tree_instant.get_children():
			self.tree_instant.delete(item)
            

		for row in CAN_STORAGE:
			row_no = str(row[0])
			if row_no.isdigit():
				display_values = list(row) + ["RUN"]
			else:
				display_values = list(row) + [""]
			self.tree_instant.insert('', tk.END, values=display_values)
			
	def run_setup_logic(self):
		print("Running commands from ODD rows only...")
		all_items = self.tree_setup.get_children()
		sequence_data = []
		for i in range(0, len(all_items), 2):
			item_id = all_items[i]
			values = self.tree_setup.item(item_id)['values']
            
			if values[1] and str(values[1]).strip():
				sequence_data.append(values)

		if sequence_data:
			run_setup_sequence(sequence_data, self.is_extended)
		else:
			print("Setup sequence is empty. No commands to run.")
	
		

		
	def create_setup_table(self, tab_frame):
		columns = ["No.", "Identifier", "Data", "Value", "Comment"]
        
		self.tree_setup = ttk.Treeview(tab_frame, columns=columns, show='headings')
		self.tree_setup.pack(side="top", expand=True, fill="both")
		
		for col in columns:
			self.tree_setup.heading(col, text=col, anchor=tk.W)
			if col == "No.": self.tree_setup.column(col, width=40)
			elif col == "Action": self.tree_setup.column(col, width=60, anchor="center")
			else: self.tree_setup.column(col, width=120)
			
		# Control Frame for Dropdown and Buttons
		setup_ctrl_frame = ttk.LabelFrame(tab_frame, text="Configure Setup Sequence")
		setup_ctrl_frame.pack(side="bottom", fill="x", padx=10, pady=10)

		ttk.Label(setup_ctrl_frame, text="Select Command:").grid(row=0, column=0, padx=5, pady=5)
        
		# The Dropdown (Combobox)
		self.cmd_dropdown = ttk.Combobox(setup_ctrl_frame, state="readonly", width=30)
		self.cmd_dropdown.grid(row=0, column=1, padx=5, pady=5)
		self.update_setup_dropdown() # Fill it initially

		# Buttons
		add_btn = ttk.Button(setup_ctrl_frame, text="Add to Sequence", command=self.add_from_dropdown)
		add_btn.grid(row=0, column=2, padx=5)

		del_btn = ttk.Button(setup_ctrl_frame, text="Remove Selected", command=self.delete_setup_row)
		del_btn.grid(row=0, column=3, padx=5)

		run_btn = ttk.Button(setup_ctrl_frame, text="Run Sequence", command=self.run_setup_logic)
		run_btn.grid(row=0, column=4, padx=20)

	def update_setup_dropdown(self):
		choices = [row[4] for row in CAN_STORAGE if str(row[0]).isdigit() and len(row) > 4]
		self.cmd_dropdown['values'] = choices
		if choices:
			self.cmd_dropdown.current(0)

	def add_from_dropdown(self):
		selected_comment = self.cmd_dropdown.get()
		if not selected_comment:
			return
		source_row = next((r for r in CAN_STORAGE if len(r) > 4 and r[4] == selected_comment), None)
        
		if source_row:
			selected_items = self.tree_setup.selection()
			if not selected_items:
				insert_pos = tk.END
				
			else:
				selected_item = selected_items[0]
				current_idx = self.tree_setup.index(selected_item)
                
				if current_idx % 2 == 0:
					insert_pos = current_idx + 2
				else:
					insert_pos = current_idx + 1
			new_cmd = self.tree_setup.insert('', insert_pos, values=("TEMP", source_row[1], source_row[2], "", source_row[4]))
			cmd_idx = self.tree_setup.index(new_cmd)
			self.tree_setup.insert('', cmd_idx + 1, values=("TEMP", "", "", "", f"Response for {source_row[4]}"))
			self.reorder_setup_numbers()
	def delete_setup_row(self):
		selected_item = self.tree_setup.selection()
		idx = self.tree_setup.index(selected_item[0])
		
		row_values = self.tree_setup.item(selected_item[0])['values']
		row_no = str(row_values[0])
		
		if "Res" in row_no:
			parent_idx = idx - 1
		else:
			parent_idx = idx
            
		all_items = self.tree_setup.get_children()
        
		if parent_idx >= 0 and parent_idx + 1 < len(all_items):
			self.tree_setup.delete(all_items[parent_idx + 1])
			self.tree_setup.delete(all_items[parent_idx])
			
		self.reorder_setup_numbers()
		
	def reorder_setup_numbers(self):
		for i, item in enumerate(self.tree_setup.get_children()):
			real_idx = i // 2
			if i % 2 == 0:
				self.tree_setup.set(item, "No.", str(real_idx))
			else:
				self.tree_setup.set(item, "No.", f"Res{real_idx}")        
        
		
        
		
				
		

app = CAN_GUI(root,run_instant_logic)
root.mainloop()
