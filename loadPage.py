import tkinter as tk
from tkinter import ttk

import tkinter as tk
from basePage import BasePage

class loadPage(BasePage):
	label_color = "#8056a5"
	button_color = "#573172"

	def __init__(self, parent, controller):
		# Rule 1 & 2: Call BasePage initializer (automatically builds status bar)
		super().__init__(parent, controller)

		# Build page-specific layout
		self.setup_main_containers()

	def setup_main_containers(self):
		"""Creates main grid container directly under the BasePage status bar."""
		# Rule 3: DO NOT create a top_container here!
		self.grid_container = tk.Frame(self, bg="#FFFFFF")
		
		# Pack directly into self with 0 top margin
		self.grid_container.pack(side="top", fill="both", expand=True, padx=10, pady=(0, 5))
		self.grid_container.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="equal")
		self.grid_container.grid_rowconfigure((0, 1, 2, 3, 4), weight=1, uniform="equal")

		for row in range(5):
			for col in range(4):
					cell_frame = tk.Frame(self.grid_container, bg="#E0E0E0", bd=1, relief="solid") # Light grey frame
					cell_frame.grid(
						row=row, 
						column=col, 
						sticky="nsew", 
						padx=2, 
						pady=2
					)
	# -------------------------------------------------------------------------
	# Logic & Event Callbacks
	# -------------------------------------------------------------------------
	

	def open_file_selector(self):
		print("Placeholder for file selection")

	def print_click(self, target_name):
		print(f"[UI EVENT]: User pressed block area linked to -> {target_name}")