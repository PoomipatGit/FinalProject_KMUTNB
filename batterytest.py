import tkinter as tk
from datetime import timedelta
class BatteryTestpage:
	def __init__(self, battery_test):
		self.battery_test = battery_test
		self.battery_test.title("Battery Test")
		self.bgcolor1 = "#9476FF"
		self.bgcolor2 = "#2e0771"
        #Variables capacity
		self.ah_current = 0.0
		self.wh_current = 0.0
		self.capacity_text = tk.StringVar()
		#Variables VAW
		self.volt = 0.0
		self.amp = 0.0
		self.watt = 0.0
		self.vaw_text = tk.StringVar()
		#limit
		self.discharge_amp = tk.StringVar()
		self.discharge_watt = tk.StringVar()
		self.charge_amp = tk.StringVar()
		self.charge_watt = tk.StringVar()
		self.set_volt = tk.StringVar()
  
		self.run_sec = 0.0
		self.run_time_sec = tk.StringVar()	
		
  		#Set up
		#mode test
		self.selected_mode = tk.StringVar(value="Mode: Charge")
		#charge voltage
		self.set_chrg_volt = tk.StringVar()
		#charge current
		self.set_chrg_amp = tk.StringVar()
		#cut-off capacity
		self.set_cutoff_cap = tk.StringVar()
		#cut-off Time
		self.set_cutoff_time = tk.StringVar()
		#cut-off Voltage
		self.set_cutoff_voltage = tk.StringVar()
		#cut-off Current
		self.set_cutoff_current = tk.StringVar()
		#cut-off Current
		self.set_cutoff_energy = tk.StringVar()
		#run button
		self.run_button = tk.StringVar()
		#save button
		self.save_button = tk.StringVar()
  
        #Run
		self.monitor_battery()
		self.update_loop()
		self.limit()
		self.discharge_current_limit()
		self.discharge_power_limit()
		self.charge_current_limit()
		self.charge_power_limit()
		self.setting_voltage_limit()
		self.runtime()
		self.setup()
		self.mode_batttest()
		self.charge_voltage()
		self.charge_current()
		self.cutoffcap()
		self.cutofftime()
		self.cutoffvolt()
		self.cutoffcurr()
		self.cutoffengy()
		self.button_run()
		self.button_save()
  
	def update_loop(self):
		#Value format & update

		self.capacity_text.set(f"{self.ah_current} Ah\n {self.wh_current} Wh")
		self.vaw_text.set(f"{self.volt} V\n{self.amp} A\n {self.watt} W")
		self.battery_test.after(100, self.update_loop)
		
	def monitor_battery(self):
		#capacity
		self.monitor_capacity = tk.Label(
			self.battery_test, 
			textvariable=self.capacity_text,   
			justify="center",       #Aligns each individual line of text 
			anchor="center",        #Positions the entire block of text "n" (top), "s" (bottom), "e" (right), "w" (left), "nw" (top-left), etc.       
			bg=self.bgcolor2,              
			fg="white",                
			font=("Arial", 40),         
			width=10,                   
			height=4                   
		)
		self.monitor_capacity.place(x=10, y=58)

		#VAW
		self.monitor_VAW = tk.Label(
			self.battery_test, 
			textvariable=self.vaw_text,   
			justify="center",            
			anchor="center",            
			bg=self.bgcolor2,              
			fg="white",                
			font=("Arial", 20),         
			width=15,                   
			height=4                    
		)
		self.monitor_VAW.place(x=336, y=58)
		
		#frame limit
	def limit(self):
		self.limit_container = tk.LabelFrame(
			self.battery_test,
			bg=self.bgcolor1, 
			width=348, 
			height=246,
			bd=0,                   
            relief="flat",
		)
		self.limit_container.place(x=592, y=58) 
		self.limit_container.grid_propagate(False)
		self.limit_title = tk.Label(
            self.battery_test,     
            text="Limit",
            font=("Arial", 18),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.limit_title.place(x=766, y=84, anchor="center")
	
	# limit discharge current
	def discharge_current_limit(self):
		self.dischrg_amp = tk.Entry(
            self.limit_container, 
            textvariable=self.discharge_amp,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.dischrg_amp.bind("<Return>", lambda event: self.limit_dischrg_current())
		self.dischrg_amp.place(x=20, y=72, width=120, height=30)
		self.dischrg_amp_unit = tk.Label(
            self.limit_container, 
            text="A",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.dischrg_amp_unit.place(x=130, y=72, width=30, height=30)
		self.dischrg_amp_title = tk.Label(
            self.limit_container,     
            text="Discharge Current",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.dischrg_amp_title.place(x=85, y=57, anchor="center")
	def limit_dischrg_current(self):
		raw_data = self.discharge_amp.get()
		try:
			target_value = float(raw_data)
			print(f"Limit Discharge Current: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

		# limit discharge power
	def discharge_power_limit(self):
		self.dischrg_watt = tk.Entry(
            self.limit_container, 
            textvariable=self.discharge_watt,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.dischrg_watt.bind("<Return>", lambda event: self.limit_dischrg_power())
		self.dischrg_watt.place(x=190, y=72, width=120, height=30)
		self.dischrg_watt_unit = tk.Label(
            self.limit_container, 
            text="W",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.dischrg_watt_unit.place(x=300, y=72, width=30, height=30)
		self.dischrg_watt_title = tk.Label(
            self.limit_container,     
            text="Discharge Power",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.dischrg_watt_title.place(x=255, y=57, anchor="center")
	def limit_dischrg_power(self):
		raw_data = self.discharge_watt.get()
		try:
			target_value = float(raw_data)
			print(f"Limit Discharge Power: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
   
   # limit charge current
	def charge_current_limit(self):
		self.chrg_amp = tk.Entry(
            self.limit_container, 
            textvariable=self.charge_amp,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.chrg_amp.bind("<Return>", lambda event: self.limit_chrg_current())
		self.chrg_amp.place(x=20, y=142, width=120, height=30)
		self.chrg_amp_unit = tk.Label(
            self.limit_container, 
            text="A",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.chrg_amp_unit.place(x=130, y=142, width=30, height=30)
		self.chrg_amp_title = tk.Label(
            self.limit_container,     
            text="Charge Current",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.chrg_amp_title.place(x=85, y=127, anchor="center")
	def limit_chrg_current(self):
		raw_data = self.charge_amp.get()
		try:
			target_value = float(raw_data)
			print(f"Limit Charge Current: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

	# limit charge power
	def charge_power_limit(self):
		self.chrg_watt = tk.Entry(
            self.limit_container, 
            textvariable=self.charge_watt,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.chrg_watt.bind("<Return>", lambda event: self.limit_chrg_power())
		self.chrg_watt.place(x=190, y=142, width=120, height=30)
		self.chrg_watt_unit = tk.Label(
            self.limit_container, 
            text="W",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.chrg_watt_unit.place(x=300, y=142, width=30, height=30)
		self.chrg_watt_title = tk.Label(
            self.limit_container,     
            text="Charge Power",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.chrg_watt_title.place(x=255, y=127, anchor="center")
	def limit_chrg_power(self):
		raw_data = self.charge_watt.get()
		try:
			target_value = float(raw_data)
			print(f"Limit Charge Power: {target_value}")
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
   
   # limit setting voltage
	def setting_voltage_limit(self):
		self.set_volt = tk.Entry(
            self.limit_container, 
            textvariable=self.set_volt,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.set_volt.bind("<Return>", lambda event: self.limit_setting_voltage())
		self.set_volt.place(x=20, y=202, width=290, height=30)
		self.set_volt_unit = tk.Label(
            self.limit_container, 
            text="V",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.set_volt_unit.place(x=300, y=202, width=30, height=30)
		self.set_volt_title = tk.Label(
            self.limit_container,     
            text="Setting Voltage",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.set_volt_title.place(x=85, y=187, anchor="center")
	def limit_setting_voltage(self):
		raw_data = self.set_volt.get()
		try:
			target_value = float(raw_data)
			print(f"Limit Setting Voltage: {target_value}")
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")  
   
	def runtime(self):
		#frame run time
		self.runtime_container = tk.LabelFrame(
			self.battery_test,
			bg=self.bgcolor1, 
			padx=30, 
			pady=10, 
			width=246, 
			height=102,
			bd=0,                   
            relief="flat",
		)
		self.runtime_container.place(x=336, y=202) 
		self.runtime_container.grid_propagate(False)
		
		#run time
		self.runtime_title = tk.Label(
            self.battery_test,     
            text="Run Time",
            font=("Arial", 16),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.runtime_title.place(x=459, y=220, anchor="center")
		self.runtime = tk.Label(
			self.battery_test, 
			textvariable=self.run_time_sec,   
			justify="center",            
			anchor="center",            
			bg=self.bgcolor2,              
			fg="white",                
			font=("Arial", 14),         
			width=14,                   
			height=2                    
		)
		self.runtime.place(x=459, y=263, anchor="center")

	def setup(self):
		#frame set up 
		self.setup_container = tk.LabelFrame(
			self.battery_test,
			bg=self.bgcolor1, 
			#padx=30, 
			#pady=10, 
			width=930, 
			height=246,
			bd=0,                   
            relief="flat",
		)
		self.setup_container.place(x=10, y=314) 
		self.setup_container.grid_propagate(False)
		self.setup_title = tk.Label(
            self.battery_test,     
            text="Set up",
            font=("Arial", 18),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.setup_title.place(x=475, y=334, anchor="center")

		#self.battery_test.update_idletasks()
		#print(f"height: {self.monitor_capacity.winfo_height()} ")
		#print(f"width: {self.monitor_VAW.winfo_width()} ")

	# mode charge/discharge
	def mode_batttest(self):
     	#create button
		self.mode_batt = tk.Menubutton(
            self.setup_container, 
            textvariable=self.selected_mode,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2, 
            fg="white",
            highlightthickness=1,          
            highlightbackground="#ffffff",   
            activebackground="#210047",       
            activeforeground="white",
            relief="flat"
        )
		self.mode_batt.place(x=25, y=86, width=200, height=50)
  		#create dropdown
		self.mode_menu = tk.Menu(
            self.mode_batt, 
            tearoff=0, 
            font=("Arial", 12), 
            bg=self.bgcolor2,                      
            fg="white", 
            activebackground="#210047",        
            activeforeground="white",
            bd=0
        )
		#operator
		self.mode_batt["menu"] = self.mode_menu
		self.mode_menu.add_command(label="Charge", command=lambda: self.change_mode("Charge"))
		self.mode_menu.add_command(label="Discharge", command=lambda: self.change_mode("Discharge"))
	# mode charge/discharge
	def change_mode(self, mode):
		if mode == "Charge":
			self.selected_mode.set(f"Mode: Charge")
			print(f"Mode: Charge")
		elif mode == "Discharge":
			self.selected_mode.set(f"Mode: Discharge")
			print(f"Mode: Discharge")
   
	#Charge voltage
	def charge_voltage(self):
		self.chrg_volt = tk.Entry(
            self.setup_container, 
            textvariable=self.set_chrg_volt,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.chrg_volt.bind("<Return>", lambda event: self.setup_chrg_voltage())
		self.chrg_volt.place(x=250, y=86, width=130, height=50)
		self.chrgvolt_unit = tk.Label(
            self.setup_container, 
            text="V",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.chrgvolt_unit.place(x=380, y=86, width=30, height=50)
		self.chrgvolt_title = tk.Label(
            self.setup_container,     
            text="Charge Voltage",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.chrgvolt_title.place(x=310, y=71, anchor="center")
	def setup_chrg_voltage(self):
		raw_data = self.set_chrg_volt.get()
		try:
			target_value = float(raw_data)
			print(f"Charge Voltage: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
	def charge_current(self):
		self.chrg_curr = tk.Entry(
            self.setup_container, 
            textvariable=self.set_chrg_amp,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.chrg_curr.bind("<Return>", lambda event: self.setup_chrg_current())
		self.chrg_curr.place(x=435, y=86, width=130, height=50)
		self.chrgamp_unit = tk.Label(
            self.setup_container, 
            text="A",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.chrgamp_unit.place(x=565, y=86, width=30, height=50)
		self.chrgamp_title = tk.Label(
            self.setup_container,     
            text="Charge Current",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.chrgamp_title.place(x=495, y=71, anchor="center")
	def setup_chrg_current(self):
		raw_data = self.set_chrg_amp.get()
		try:
			target_value = float(raw_data)
			print(f"Charge current: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

	#Cut-off Capacity
	def cutoffcap(self):
		self.cutoff_cap= tk.Entry(
            self.setup_container, 
            textvariable=self.set_cutoff_cap,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.cutoff_cap.bind("<Return>", lambda event: self.setup_cutoff_cap())
		self.cutoff_cap.place(x=620, y=86, width=130, height=50)
		self.cutoffcap_unit = tk.Label(
            self.setup_container, 
            text="Ah",                          
            font=("Arial", 12, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.cutoffcap_unit.place(x=750, y=86, width=30, height=50)
		self.cutoffcap_title = tk.Label(
            self.setup_container,     
            text="Cut-off Capacity",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.cutoffcap_title.place(x=680, y=71, anchor="center")
	def setup_cutoff_cap(self):
		raw_data = self.set_cutoff_cap.get()
		try:
			target_value = float(raw_data)
			print(f"Cut-off Capacity: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
   
	#Cut-off time
	def cutofftime(self):
		self.cutoff_time= tk.Entry(
            self.setup_container, 
            textvariable=self.set_cutoff_time,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.cutoff_time.bind("<Return>", lambda event: self.setup_cutoff_time())
		self.cutoff_time.place(x=45, y=176, width=130, height=50)
		self.cutofftime_unit = tk.Label(
            self.setup_container, 
            text="s",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.cutofftime_unit.place(x=175, y=176, width=30, height=50)
		self.cutofftime_title = tk.Label(
            self.setup_container,     
            text="Cut-off Time",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.cutofftime_title.place(x=95, y=161, anchor="center")
	def setup_cutoff_time(self):
		raw_data = self.set_cutoff_time.get()
		try:
			target_value = float(raw_data)
			print(f"Cut-off Time: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
	
		#Cut-off Voltage
	def cutoffvolt(self):
		self.cutoff_volt= tk.Entry(
            self.setup_container, 
            textvariable=self.set_cutoff_voltage,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.cutoff_volt.bind("<Return>", lambda event: self.setup_cutoff_voltage())
		self.cutoff_volt.place(x=250, y=176, width=130, height=50)
		self.cutoffvolt_unit = tk.Label(
            self.setup_container, 
            text="V",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.cutoffvolt_unit.place(x=380, y=176, width=30, height=50)
		self.cutoffvolt_title = tk.Label(
            self.setup_container,     
            text="Cut-off Voltage",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.cutoffvolt_title.place(x=310, y=161, anchor="center")
	def setup_cutoff_voltage(self):
		raw_data = self.set_cutoff_voltage.get()
		try:
			target_value = float(raw_data)
			print(f"Cut-off Voltage: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")  
   
	#Cut-off Current
	def cutoffcurr(self):
		self.cutoff_curr= tk.Entry(
            self.setup_container, 
            textvariable=self.set_cutoff_current,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.cutoff_curr.bind("<Return>", lambda event: self.setup_cutoff_current())
		self.cutoff_curr.place(x=435, y=176, width=130, height=50)
		self.cutoffcurr_unit = tk.Label(
            self.setup_container, 
            text="A",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.cutoffcurr_unit.place(x=565, y=176, width=30, height=50)
		self.cutoffcurr_title = tk.Label(
            self.setup_container,     
            text="Cut-off Current",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.cutoffcurr_title.place(x=495, y=161, anchor="center")
	def setup_cutoff_current(self):
		raw_data = self.set_cutoff_current.get()
		try:
			target_value = float(raw_data)
			print(f"Cut-off Current: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!") 
   
   #Cut-off energy
	def cutoffengy(self):
		self.cutoff_engy= tk.Entry(
            self.setup_container, 
            textvariable=self.set_cutoff_energy,
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,     
            fg="white",    
            insertbackground="white", 
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",
            justify="center"  
        )
		self.cutoff_engy.bind("<Return>", lambda event: self.setup_cutoff_energy())
		self.cutoff_engy.place(x=620, y=176, width=130, height=50)
		self.cutoffengy_unit = tk.Label(
            self.setup_container, 
            text="Wh",                          
            font=("Arial", 12, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                 
            fg="white"                        
        )
		self.cutoffengy_unit.place(x=750, y=176, width=30, height=50)
		self.cutoffengy_title = tk.Label(
            self.setup_container,     
            text="Cut-off Energy",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
		self.cutoffengy_title.place(x=680, y=161, anchor="center")
	def setup_cutoff_energy(self):
		raw_data = self.set_cutoff_energy.get()
		try:
			target_value = float(raw_data)
			print(f"Cut-off Energy: {target_value}")
            
		except ValueError:
			print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!") 
   
	def button_run(self):
		self.run_button = tk.Button(
			self.setup_container,
			command=self.run_setup,
			text="RUN",
			font=("Arial", 14, "bold"), # ฟอนต์, ขนาด, น้ำหนัก
			bg=self.bgcolor2,               # สีพื้นหลัง (Background)
			fg="white",                 # สีตัวอักษร (Foreground)
			activebackground="#17033b", # สีพื้นหลังตอนกำลังกดปุ่มลงไป
			activeforeground="white",   # สีตัวอักษรตอนกำลังกดปุ่มลงไป
			width=10,                   # ความกว้าง (หน่วย: จำนวนตัวอักษร)
			height=2,                   # ความสูง (หน่วย: บรรทัดตัวอักษร)
    		highlightthickness=1,          
            highlightbackground="#ffffff",
			relief="flat",              # สไตล์ขอบ ("flat", "raised", "sunken", "ridge", "groove")
			cursor="hand2"              # เปลี่ยนรูปเม้าส์เมื่อชี้ปุ่ม (เช่น รูปมือ)
		)
		self.run_button.place(x=855, y=200, anchor="center")
	def run_setup(self):
		print("Run!")
		#run time
		self.run_sec+=0.1
		td = timedelta(seconds=self.run_sec)
		run_time = str(td)[:-5]
		self.run_time_sec.set(f"{run_time}")
		self.battery_test.after(100, self.update_loop)
	
	def button_save(self):
		self.save_button = tk.Button(
			self.setup_container,
			command=self.save_setup,
			text="SAVE",
			font=("Arial", 14, "bold"), # ฟอนต์, ขนาด, น้ำหนัก
			bg=self.bgcolor2,               # สีพื้นหลัง (Background)
			fg="white",                 # สีตัวอักษร (Foreground)
			activebackground="#17033b", # สีพื้นหลังตอนกำลังกดปุ่มลงไป
			activeforeground="white",   # สีตัวอักษรตอนกำลังกดปุ่มลงไป
			width=10,                   # ความกว้าง (หน่วย: จำนวนตัวอักษร)
			height=2,                   # ความสูง (หน่วย: บรรทัดตัวอักษร)
    		highlightthickness=1,          
            highlightbackground="#ffffff",
			relief="flat",              # สไตล์ขอบ ("flat", "raised", "sunken", "ridge", "groove")
			cursor="hand2"              # เปลี่ยนรูปเม้าส์เมื่อชี้ปุ่ม (เช่น รูปมือ)
		)
		self.save_button.place(x=855, y=130, anchor="center")
	def save_setup(self):
		
		print("Save!")


if __name__ == "__main__":
    battery_test = tk.Tk()
    battery_test.geometry("950x570") 
    app = BatteryTestpage(battery_test) #go to Run in init
    battery_test.mainloop()
	
