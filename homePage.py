import tkinter as tk
from tkinter import ttk
from basePage import BasePage
from basePage import BasePage
import tkinter as tk

class homePage(BasePage):
	import tkinter as tk
from basePage import BasePage

class homePage(BasePage):
	lebel_color = "#8056a5"
	button_color = "#573172"

	def __init__(self, parent, controller):
		# 1. Initialize parent BasePage frame
		super().__init__(parent, controller)

		# =====================================================================
		# 2. DEFINE ALL VARIABLES FIRST (MUST BE BEFORE UI SETUP METHODS!)
		# =====================================================================
		self._displayed_error_count = 0

		# Mode selection variables
		self.mode_options = [
			"Source Mode",
			"Load Mode",
			"Battery Test",
			"Auto Sequence Mode"
		]
		self.selected_mode = tk.StringVar(value=self.mode_options[0])
		self.current_mode_var = tk.StringVar(value="Source Mode (CV)")

		# System status & stage variables
		self.system_stage_var = tk.StringVar(value="Standby")  # <--- Fixes AttributeError!
		self.error_count_var = tk.StringVar(value="2")

		# =====================================================================
		# 3. CALL SETUP METHODS
		# =====================================================================
		self.setup_main_containers()
		self.setup_welcome_and_stage()
		self.setup_error_warning_panel()
		self.setup_mode_config_panel()
		self.setup_monitor_panel()
		self.setup_log_monitor_panel()

		# =====================================================================
		# 4. START BACKGROUND POLLING / UPDATE LOOPS (if present)
		# =====================================================================
		self.poll_value()  # Uncomment if you have background updates
	# -------------------------------------------------------------------------
	# Layout Builders
	# -------------------------------------------------------------------------
	def setup_main_containers(self):
	
		self.grid_container = tk.Frame(self, bg="#FFFFFF")
		
		# pady=(0, 0) removes vertical gaps above and below the grid
		# Change padx to 5 or 0 if you want to remove the side red borders too
		self.grid_container.pack(side="top", fill="both", expand=True, padx=5, pady=0)

		self.grid_container.grid_columnconfigure((0, 1, 2), weight=1, uniform="equal")
		self.grid_container.grid_rowconfigure((0, 1, 2), weight=1, uniform="equal")


	def setup_welcome_and_stage(self):
		"""Builds Top-Left cell (Row 0, Col 0): Welcome & System Stage."""
		cell_split_frame_TL = tk.Frame(self.grid_container, bg="#ffffff")
		cell_split_frame_TL.grid(row=0, column=0, sticky="nsew")
		cell_split_frame_TL.grid_rowconfigure((0, 1), weight=1)
		cell_split_frame_TL.grid_columnconfigure(0, weight=1)

		welcome_label = tk.Label(
			cell_split_frame_TL,
			text="Welcome",
			font=("Helvetica", 12, "bold"),
			bg=self.label_color,
			fg="white",
			width=30
		)
		welcome_label.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

		stage_row_container = tk.Frame(cell_split_frame_TL, bg=self.label_color)
		stage_row_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
		stage_row_container.grid_rowconfigure(0, weight=1)
		stage_row_container.grid_columnconfigure((0, 3), weight=1)
		stage_row_container.grid_columnconfigure((1, 2), weight=0)

		lbl_stage_title = tk.Label(
			stage_row_container,
			text="System stage : ",
			font=("Helvetica", 12, "bold"),
			bg=self.label_color,
			fg="white"
		)
		lbl_stage_title.grid(row=0, column=1, sticky="e")

		self.lbl_stage_value = tk.Label(
			stage_row_container,
			textvariable=self.system_stage_var,
			font=("Helvetica", 12, "bold"),
			bg=self.label_color,
			fg="#eed2d2"
		)
		self.lbl_stage_value.grid(row=0, column=2, sticky="w")

	def setup_error_warning_panel(self):
		"""Builds Mid-Left cell (Row 1, Col 0): Error Counter & Listbox."""
		cell_split_frame_ML = tk.Frame(self.grid_container, bg="#ffffff")
		cell_split_frame_ML.grid(row=1, column=0, sticky="nsew")
		cell_split_frame_ML.grid_rowconfigure((0, 1), weight=2)
		cell_split_frame_ML.grid_columnconfigure(0, weight=1)

		error_row_container = tk.Frame(cell_split_frame_ML, bg=self.button_color)
		error_row_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
		error_row_container.grid_rowconfigure(0, weight=1)
		error_row_container.grid_columnconfigure((0, 3), weight=1)
		error_row_container.grid_columnconfigure((1, 2), weight=0)

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
			textvariable=self.error_count_var,
			font=("Helvetica", 12, "bold"),
			bg=self.button_color,
			fg="#ffffff"
		)
		self.lbl_error_value.grid(row=0, column=2, sticky="w")

		# Click event binding
		trigger_error_event = lambda event: self.print_click("Entire Error Warning Block Area")
		error_row_container.bind("<Button-1>", trigger_error_event)
		lbl_error_title.bind("<Button-1>", trigger_error_event)
		self.lbl_error_value.bind("<Button-1>", trigger_error_event)

		# Listbox Container
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

	def setup_mode_config_panel(self):
		"""Builds Bottom-Left cell (Row 2, Col 0): 3-Row Mode Config Panel."""
		cell_split_frame_BL = tk.Frame(self.grid_container, bg="#ffffff")
		cell_split_frame_BL.grid(row=2, column=0, sticky="nsew")
		cell_split_frame_BL.grid_rowconfigure(0, weight=1)
		cell_split_frame_BL.grid_columnconfigure(0, weight=1)

		mode_config_container = tk.Frame(cell_split_frame_BL, bg=self.button_color)
		mode_config_container.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
		mode_config_container.grid_rowconfigure((0, 1, 2), weight=1)
		mode_config_container.grid_columnconfigure(0, weight=1)

		# ROW 0: Header
		lbl_config_header = tk.Label(
			mode_config_container,
			text="Config/Monitor Mode :",
			font=("Helvetica", 11, "bold"),
			bg=self.button_color,
			fg="#FFFFFF"
		)
		lbl_config_header.grid(row=0, column=0, pady=(8, 2), sticky="n")

		# ROW 1: Current Mode Readout
		current_mode_frame = tk.Frame(mode_config_container, bg=self.button_color)
		current_mode_frame.grid(row=2, column=0, pady=2)

		lbl_mode_title = tk.Label(
			current_mode_frame,
			text="Current Mode : ",
			font=("Helvetica", 10, "bold"),
			bg=self.button_color,
			fg="#FFFFFF"
		)
		lbl_mode_title.grid(row=0, column=0, sticky="e")

		self.lbl_current_mode_val = tk.Label(
			current_mode_frame,
			textvariable=self.current_mode_var,
			font=("Helvetica", 10, "bold"),
			bg=self.button_color,
			fg="#EED2D2"
		)
		self.lbl_current_mode_val.grid(row=0, column=1, sticky="w")

		# ROW 2: Dropdown (Left) & GO Button (Right)
		controls_row_frame = tk.Frame(mode_config_container, bg=self.button_color)
		controls_row_frame.grid(row=1, column=0, pady=(2, 8), padx=10, sticky="ew")
		controls_row_frame.grid_columnconfigure(0, weight=1)
		controls_row_frame.grid_columnconfigure(1, weight=0)

		self.mode_dropdown = ttk.Combobox(
			controls_row_frame,
			textvariable=self.selected_mode,
			values=self.mode_options,
			state="readonly",
			font=("Helvetica", 9),
			width=15
		)
		self.mode_dropdown.grid(row=0, column=0, padx=(0, 6), sticky="ew")

		self.btn_go = tk.Button(
			controls_row_frame,
			text="GO",
			font=("Helvetica", 9, "bold"),
			bg="#ffffff",
			fg=self.button_color,
			activebackground="#e0e0e0",
			relief="groove",
			bd=2,
			padx=12,
			command=self.on_go_click
		)
		self.btn_go.grid(row=0, column=1, sticky="e")

	def setup_monitor_panel(self):
		"""Builds Top-Right 2x2 Merged Monitor Area."""
		monitor_container = tk.Frame(self.grid_container, bg="#ffffff")
		monitor_container.grid(row=0, column=1, rowspan=2, columnspan=2, sticky="nsew")

		self.monitor_frame = tk.Frame(monitor_container, bg="#E2D4F0", bd=1, relief="solid")
		self.monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)

		lbl_monitor = tk.Label(
			self.monitor_frame, text="Monitor", font=("Helvetica", 14, "bold"),
			bg="#E2D4F0", fg="#573172"
		)
		lbl_monitor.pack(expand=True)

	def setup_log_monitor_panel(self):
		"""Builds Bottom-Right 1x2 Merged Log Monitor Area."""
		log_container = tk.Frame(self.grid_container, bg="#ffffff")
		log_container.grid(row=2, column=1, rowspan=1, columnspan=2, sticky="nsew")

		self.log_monitor_frame = tk.Frame(log_container, bg="#C9B3E6", bd=1, relief="solid")
		self.log_monitor_frame.pack(fill="both", expand=True, padx=5, pady=5)

		lbl_log_monitor = tk.Label(
			self.log_monitor_frame, text="Log Monitor", font=("Helvetica", 12, "bold"),
			bg="#C9B3E6", fg="#573172"
		)
		lbl_log_monitor.pack(expand=True)

	# -------------------------------------------------------------------------
	# Logic & Event Callbacks
	# -------------------------------------------------------------------------
	def poll_value(self):
		"""Live background loop querying backend state."""
		# 1. Update stage
		latest_stage = get_current_system_stage()
		self.system_stage_var.set(latest_stage)

		# 2. Update error count & listbox
		error_log = get_current_error_log()
		latest_error_count = len(error_log)
		self.error_count_var.set(str(latest_error_count))

		if latest_error_count > self._displayed_error_count:
			for new_msg in error_log[self._displayed_error_count:]:
				self.error_listbox.insert(tk.END, f"• {new_msg}")

			self._displayed_error_count = latest_error_count
			self.error_listbox.yview_moveto(1.0)

		# 3. Update current operating mode
		active_mode = get_mode()
		self.current_mode_var.set(active_mode)

		# 4. Schedule next loop cycle in 250ms
		self.after(250, self.poll_value)

	def on_go_click(self):
		from sourcePage import sourcePage
		from batterytest import BatteryTestpage
		from loadPage import loadPage

		choice = self.selected_mode.get()
		print(f"[NAV EVENT]: Navigating to -> {choice}")

		# Map dropdown strings to frame class references
		page_map = {
			"Source Mode": sourcePage,
			"Battery Test": BatteryTestpage,
			"Load Mode": loadPage
		}

		if choice in page_map:
			self.controller.show_frame(page_map[choice])
		else:
			print(f"[NAV WARNING]: No frame defined for '{choice}'")

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

def get_mode():
	return "Source Mode (CV)"