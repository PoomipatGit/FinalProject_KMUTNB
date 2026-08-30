import tkinter as tk
import threading
from datetime import timedelta
from basePage import BasePage

class Batterysimulationpage(BasePage):
    def __init__(self, parent):
        # 1. Mount as a tk.Frame child inside master container
        super().__init__(parent)
        #self.controller = controller

        # Color Palette
        self.bgcolor1 = "#a67dc9" # สีอ่อน
        self.bgcolor2 = "#573172" # สีเข้ม
        self.bgpopup = "white"
        # Variables capacity
        self.ah_current = 0.0
        self.wh_current = 0.0
        self.capacity_text = tk.StringVar()

        # Variables VAW
        self.volt = 0.0
        self.amp = 0.0
        self.watt = 0.0
        self.vaw_text = tk.StringVar()

        # Limits
        self.discharge_amp = tk.StringVar()
        self.discharge_watt = tk.StringVar()
        self.charge_amp = tk.StringVar()
        self.charge_watt = tk.StringVar()
        self.set_volt = tk.StringVar()
        
        # Run Time
        self.running_time = False
        self.run_sec = 0.0
        self.run_time_sec = tk.StringVar()  
        
        self.draw_casing()  # Draw the battery casing
        self.run_button = None  # Will hold the tk.Button widget
        self.save_button = None # Will hold the tk.Button widget
        self.edit_button = None # Will hold the tk.Button widget

        #monitor init
        self.init_voc_val = 0.00
        self.init_soc_val = 0
        self.init_cap_val = 0.00
        self.init_voc_text = tk.StringVar()
        self.init_soc_text = tk.StringVar()
        self.init_cap_text = tk.StringVar()
        
        #monitor parameter
        self.full_volt_val = 0.00
        self.empty_volt_val = 0.00
        self.edit_capacity_val = 0.00
        
        self.parallel = 0
        self.series = 0
        self.inner_resist_val = 0.00
        
        self.soc_high_val=0
        self.soc_low_val=0
        self.chrg_amp_max_val = 0.00
        self.dischrg_amp_max_val = -0.00
        
        self.soc_now_val = self.init_soc_val
        self.full_volt_text = tk.StringVar()
        self.empty_volt_text = tk.StringVar()
        self.inner_resist_text = tk.StringVar()
        self.edit_capacity_text = tk.StringVar()
        self.soc_high_text = tk.StringVar()
        self.soc_low_text = tk.StringVar()
        self.parallel_series_text = tk.StringVar()
        self.soc_now_text = tk.StringVar()
        # --- 3. Build UI Widgets ---
        self.monitor_battery()
        self.limit()
        self.discharge_current_limit()
        self.discharge_power_limit()
        self.charge_current_limit()
        self.charge_power_limit()
        self.setting_voltage_limit()
        self.runtime()
        self.monitor_init()
        self.Init_voc()
        self.Init_soc()
        self.Init_cap()
        self.monitor_parameter()
        self.full_volt()
        self.capacity()
        self.empty_voltage()
        self.soc_high()
        self.inner_resis()
        self.soc_low()
        self.parallel_series()
        self.soc_now()
        self.button_run()
        self.button_save()
        self.button_edit()
        # --- 4. Start Single Unified Loop ---
        self.update_loop()
        self.update_battery_level()


    # -------------------------------------------------------------------------
    # Unified Live Update Loop
    # -------------------------------------------------------------------------
    def update_loop(self):
        # 1. Update text variables for capacity & VAW
        self.capacity_text.set(f"{self.ah_current} Ah\n {self.wh_current} Wh")
        self.vaw_text.set(f"{self.volt} V\n{self.amp} A\n {self.watt} W")
        self.init_voc_text.set(f"{self.init_voc_val} V")
        self.init_soc_text.set(f"{self.init_soc_val} %")
        self.init_cap_text.set(f"{self.init_cap_val} Ah")
        
        self.full_volt_text.set(f"{self.full_volt_val} V")
        self.empty_volt_text.set(f"{self.empty_volt_val} V")
        self.inner_resist_text.set(f"{self.inner_resist_val} mΩ")
        self.edit_capacity_text.set(f"{self.edit_capacity_val} Ah")
        self.soc_high_text.set(f"{self.soc_high_val} %")
        self.soc_low_text.set(f"{self.soc_low_val} %")
        self.parallel_series_text.set(f"{self.parallel}P / {self.series}S")
        self.soc_now_text.set(f"{int(max(0, min(100, round(int(self.soc_now_val)))))}%")
        
        # 2. Timer counter logic
        if self.running_time :
            self.run_sec += 0.1
            total_secs = int(self.run_sec)
            hours = total_secs // 3600
            mins = (total_secs % 3600) // 60
            secs = total_secs % 60
            tenths = int((self.run_sec * 10) % 10)  # ดึงเศษ 0.1 ออกมา 1 หลัก
            self.run_time_sec.set(f"{hours:02d}:{mins:02d}:{secs:02d}.{tenths}")
            self.soc_now_val = min(100.0, self.soc_now_val + 1)
            self.soc_now_val = self.soc_now_val+1

        # 3. Schedule ONLY ONE next cycle in 100ms
        self.after(100, self.update_loop)

    # -------------------------------------------------------------------------
    # UI Component Construction Methods
    # -------------------------------------------------------------------------
    def monitor_battery(self):
        self.monitor_capacity = tk.Label(
            self, 
            textvariable=self.capacity_text,   
            justify="center", 
            anchor="center",       
            bg=self.bgcolor1,              
            fg="white",                
            font=("Arial", 40),         
            width=10,                   
            height=4                  
        )
        self.monitor_capacity.place(x=10, y=40)

        self.monitor_VAW = tk.Label(
            self, 
            textvariable=self.vaw_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor1,              
            fg="white",                
            font=("Arial", 20),         
            width=15,                   
            height=4                    
        )
        self.monitor_VAW.place(x=336, y=40)

    def limit(self):
        self.limit_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            width=348, 
            height=246,
            bd=0,                   
            relief="flat",
        )
        self.limit_container.place(x=592, y=40) 
        self.limit_container.grid_propagate(False)
        
        self.limit_title = tk.Label(
            self.limit_container,     
            text="Limit",
            font=("Arial", 18),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.limit_title.place(x=174, y=26, anchor="center")

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
        self.dischrg_amp.bind("<Return>", lambda event:(self.func_limit_dischrg_current(), self.focus_set()))
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

    def func_limit_dischrg_current(self):
        raw_data = self.discharge_amp.get()
        try:
            target_value = float(raw_data)
            print(f"Limit Discharge Current: {target_value}")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

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
        self.dischrg_watt.bind("<Return>", lambda event: (self.func_limit_dischrg_power(), self.focus_set()))
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

    def func_limit_dischrg_power(self):
        raw_data = self.discharge_watt.get()
        try:
            target_value = float(raw_data)
            print(f"Limit Discharge Power: {target_value}")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

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
        self.chrg_amp.bind("<Return>", lambda event: (self.func_limit_chrg_current(), self.focus_set()))
        self.chrg_amp.place(x=20, y=137, width=120, height=30)
        
        self.chrg_amp_unit = tk.Label(
            self.limit_container, 
            text="A",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                
            fg="white"                        
        )
        self.chrg_amp_unit.place(x=130, y=137, width=30, height=30)
        
        self.chrg_amp_title = tk.Label(
            self.limit_container,     
            text="Charge Current",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.chrg_amp_title.place(x=85, y=122, anchor="center")

    def func_limit_chrg_current(self):
        raw_data = self.charge_amp.get()
        try:
            target_value = float(raw_data)
            print(f"Limit Charge Current: {target_value}")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

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
        self.chrg_watt.bind("<Return>", lambda event: (self.func_limit_chrg_power(), self.focus_set()))
        self.chrg_watt.place(x=190, y=137, width=120, height=30)
        
        self.chrg_watt_unit = tk.Label(
            self.limit_container, 
            text="W",                          
            font=("Arial", 14, "bold"), 
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",                
            fg="white"                        
        )
        self.chrg_watt_unit.place(x=300, y=137, width=30, height=30)
        
        self.chrg_watt_title = tk.Label(
            self.limit_container,     
            text="Charge Power",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.chrg_watt_title.place(x=255, y=122, anchor="center")

    def func_limit_chrg_power(self):
        raw_data = self.charge_watt.get()
        try:
            target_value = float(raw_data)
            print(f"Limit Charge Power: {target_value}")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   

    def setting_voltage_limit(self):
        self.set_volt_entry = tk.Entry(
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
        self.set_volt_entry.bind("<Return>", lambda event: (self.func_limit_setting_voltage(), self.focus_set()))
        self.set_volt_entry.place(x=20, y=202, width=290, height=30)
        
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

    def func_limit_setting_voltage(self):
        raw_data = self.set_volt.get()
        try:
            target_value = float(raw_data)
            print(f"Limit Setting Voltage: {target_value}")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")  

    def runtime(self):
        self.runtime_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            padx=30, 
            pady=10, 
            width=246, 
            height=102,
            bd=0,                   
            relief="flat",
        )
        self.runtime_container.place(x=336, y=184) 
        self.runtime_container.grid_propagate(False)
        
        self.runtime_title = tk.Label(
            self.runtime_container,     
            text="Run Time",
            font=("Arial", 16),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.runtime_title.place(x=95, y=10, anchor="center")
        
        self.lbl_runtime_val = tk.Label(
            self.runtime_container, 
            textvariable=self.run_time_sec,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,              
            fg="white",                
            font=("Arial", 14),         
            width=14,                   
            height=2                    
        )
        self.lbl_runtime_val.place(x=15, y=50, anchor="w")
        
    def monitor_init(self):
            self.moni_init_container = tk.LabelFrame(
                self,
                bg=self.bgcolor1, 
                width=200, 
                height=225,
                bd=0,                   
                relief="flat",
            )
            self.moni_init_container.place(x=120, y=300) 
            self.moni_init_container.grid_propagate(False)
            
    def Init_voc(self):
        self.init_voc = tk.Label(
            self.moni_init_container, 
            textvariable=self.init_voc_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,              
            fg="white",                
            font=("Arial", 16),                           
        )
        self.init_voc.place(x=100, y=50, width=120, height=30,anchor="center")
        self.init_voc_title = tk.Label(
            self.moni_init_container,     
            text="Initial VOC",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.init_voc_title.place(x=100, y=20, anchor="center")
        
    def Init_soc(self):
        self.init_soc = tk.Label(
            self.moni_init_container, 
            textvariable=self.init_soc_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,              
            fg="white",                
            font=("Arial", 16),                           
        )
        self.init_soc.place(x=100, y=120, width=120, height=30,anchor="center")
        self.init_soc_title = tk.Label(
            self.moni_init_container,     
            text="Initial SOC",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.init_soc_title.place(x=100, y=90, anchor="center")

    def Init_cap(self):
        self.init_cap = tk.Label(
            self.moni_init_container, 
            textvariable=self.init_cap_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,              
            fg="white",                
            font=("Arial", 16),                           
        )
        self.init_cap.place(x=100, y=190, width=120, height=30,anchor="center")
        self.init_cap_title = tk.Label(
            self.moni_init_container,     
            text="Initial Capacity",
            font=("Arial", 12),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.init_cap_title.place(x=100, y=160, anchor="center")
        
    def monitor_parameter(self):
        self.moni_prm_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            width=460, 
            height=200,
            bd=0,                   
            relief="flat",
        )
        self.moni_prm_container.place(x=330, y=300) 
        self.moni_prm_container.grid_propagate(False)
    
    def full_volt(self):
        self.full_volt = tk.Label(
            self.moni_prm_container, 
            textvariable=self.full_volt_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.full_volt.place(x=130, y=40, width=95, height=30,anchor="w")
        self.full_volt_title = tk.Label(
            self.moni_prm_container,     
            text="Full Voltage",
            font=("Arial", 12),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.full_volt_title.place(x=10, y=40,width=120, height=30, anchor="w")
            
    def capacity(self):
        self.cap = tk.Label(
            self.moni_prm_container, 
            textvariable=self.edit_capacity_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.cap.place(x=355, y=40, width=95, height=30,anchor="w")
        self.capacity_title = tk.Label(
            self.moni_prm_container,     
            text="Capacity",
            font=("Arial", 12),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.capacity_title.place(x=235, y=40,width=120, height=30, anchor="w")
        
    def empty_voltage(self):
        self.empty_volt = tk.Label(
            self.moni_prm_container, 
            textvariable=self.empty_volt_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.empty_volt.place(x=130, y=80, width=95, height=30,anchor="w")
        self.empty_volt_title = tk.Label(
            self.moni_prm_container,     
            text="Empty Voltage",
            font=("Arial", 12),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.empty_volt_title.place(x=10, y=80,width=120, height=30, anchor="w")
        
    def soc_high(self):
        self.SOC_high = tk.Label(
            self.moni_prm_container, 
            textvariable=self.soc_high_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.SOC_high.place(x=355, y=80, width=95, height=30,anchor="w")
        self.SOC_high_title = tk.Label(
            self.moni_prm_container,     
            text="SOC High",
            font=("Arial", 12),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.SOC_high_title.place(x=235, y=80,width=120, height=30, anchor="w")
        
    def inner_resis(self):
        self.inner_r = tk.Label(
            self.moni_prm_container, 
            textvariable=self.inner_resist_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.inner_r.place(x=130, y=120, width=95, height=30,anchor="w")
        self.inner_r_title = tk.Label(
            self.moni_prm_container,     
            text="Inner Resistance",
            font=("Arial", 10),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.inner_r_title.place(x=10, y=120,width=120, height=30, anchor="w")
        
    def soc_low(self):
        self.SOC_low = tk.Label(
            self.moni_prm_container, 
            textvariable=self.soc_low_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.SOC_low.place(x=355, y=120, width=95, height=30,anchor="w")
        self.SOC_low_title = tk.Label(
            self.moni_prm_container,     
            text="SOC Low",
            font=("Arial", 12),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.SOC_low_title.place(x=235, y=120,width=120, height=30, anchor="w")
        
    def parallel_series(self):
        self.p_r= tk.Label(
            self.moni_prm_container, 
            textvariable=self.parallel_series_text,   
            justify="center",            
            anchor="center",            
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",              
            fg="white",                
            font=("Arial", 14),                           
        )
        self.p_r.place(x=230, y=160, width=150, height=30,anchor="w")
        self.p_r_title = tk.Label(
            self.moni_prm_container,     
            text="Parallel / Series",
            font=("Arial", 12),    
            bg=self.bgcolor2,
            highlightthickness=1,          
            highlightbackground="#ffffff",
            fg="white"           
        )
        self.p_r_title.place(x=80, y=160,width=150, height=30, anchor="w")
        
    
    # -------------------------------------------------------------------------
    # Battery Canvas Graphic
    # -------------------------------------------------------------------------
    def draw_casing(self):
        self.battery_w = 80
        self.battery_h = 200
        # สร้าง Canvas มารองรับการวาด
        self.battery_canvas = tk.Canvas(
            self,
            width=self.battery_w,
            height=self.battery_h,
            bg="white",
            highlightthickness=0
        )
        self.battery_canvas.place(x=20, y=310)
        points = [
            25, 3,       # 1. มุมบนซ้ายของขั้ว
            self.battery_w - 25, 3,       # 2. มุมบนขวาของขั้ว
            self.battery_w - 25, 14,       # 3. มุมล่างขวาของขั้ว
            self.battery_w - 5, 14,   # 4. มุมบนขวาของตัวถัง
            self.battery_w - 5, self.battery_h - 5,# 5. มุมล่างขวาของตัวถัง
            5, self.battery_h - 5,   # 6. มุมล่างซ้ายของตัวถัง
            5, 14,       # 7. มุมบนซ้ายของตัวถัง
            25, 14        # 8. มุมล่างซ้ายของขั้ว
        ]
        # วาด Polygon เชื่อมกันหมด ไร้รอยต่อ
        self.battery_canvas.create_polygon(
            points, 
            outline="black", 
            fill="",        # fill="" คือข้างในโปร่งใส
            width=3,
            joinstyle="miter"     # เชื่อมมุมแบบเหลี่ยมคม
        )
        self.battery_canvas.create_rectangle(
            9, 192, self.battery_w - 8, self.battery_h - 8,
            fill="#2ecc71", width=0, tags="battery_bar"
        )
    def update_battery_level(self):
        val = max(0.0, min(100.0, int(self.soc_now_val)))
        self.battery_scale = 192 - (172 * val / 100)
        
        # ปรับเฉพาะพิกัดของแท่งเดิมที่มี tag "battery_bar" โดยไม่ต้องลบแล้ววาดใหม่
        self.battery_canvas.coords(
            "battery_bar",
            9, self.battery_scale, self.battery_w - 8, self.battery_h - 8
        )
        self.battery_canvas.after(100, self.update_battery_level)
    def soc_now(self):
        self.soc_Now= tk.Label(
            self, 
            textvariable=self.soc_now_text,   
            justify="center",            
            anchor="center",            
            bg="white",
            fg="black",                
            font=("Arial", 16),                           
        )
        self.soc_Now.place(x=60, y=525, width=80, height=30,anchor="center")
    
    # -------------------------------------------------------------------------
    def button_edit(self):
                self.edit_button = tk.Button(
                    self,
                    command=self.edit_parameter,
                    text="EDIT",
                    font=("Arial", 14, "bold"),
                    bg=self.bgcolor2,              
                    fg="white",                
                    activebackground="#17033b",
                    activeforeground="white",  
                    width=10,                  
                    height=2,                  
                    highlightthickness=1,          
                    highlightbackground="#ffffff",
                    relief="flat",             
                    cursor="hand2"             
                )
                self.edit_button.place(x=865, y=358, anchor="center")
    def edit_parameter(self):
        print("Edit parameter!")
        self.edit_popup()

    def button_run(self):
            self.run_button = tk.Button(
                self,
                command=self.run_stop_setup,
                text="RUN",
                font=("Arial", 14, "bold"),
                bg=self.bgcolor2,              
                fg="white",                
                activebackground="#17033b",
                activeforeground="white",  
                width=10,                  
                height=2,                  
                highlightthickness=1,          
                highlightbackground="#ffffff",
                relief="flat",             
                cursor="hand2"             
            )
            self.run_button.place(x=865, y=498, anchor="center")
    
    def run_stop_setup(self):
        if self.run_button.cget("text") == "RUN":
            print("Run!")
            self.run_button.config(
                text="STOP", 
                bg="#FF4D4D",              
                activebackground="#CC0000"
            )
            self.running_time = True
        else:
            self.run_button.config(
                text="RUN",
                bg=self.bgcolor2,              
                activebackground="#17033b"
            )
            self.running_time = False

    def button_save(self):
        self.save_button = tk.Button(
            self,
            command=self.save_setup,
            text="SAVE",
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,              
            fg="white",                
            activebackground="#17033b",
            activeforeground="white",  
            width=10,                  
            height=2,                  
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",             
            cursor="hand2"             
        )
        self.save_button.place(x=865, y=428, anchor="center")
    
    def save_setup(self):
        print("Save!")
    # -------------------------------------------------------------------------
        # pop up edit parameter
    #-------------------------------------------------------------------------
    def edit_popup(self):
        popup = tk.Toplevel(self)
        popup.title("Edit Parameter")
        popup.geometry("800x530")
        popup.config(bg=self.bgpopup)
        popup.transient(self) #ผูกสถานะให้ Pop-up เป็นหน้าต่างลูกของ self (หน้าต่างจะลอยอยู่ด้านบนเสมอ)
        popup.resizable(False, False) # ปิดไม่ให้ปรับขนาด
        # รอให้หน้าต่างถูกวาดขึ้นมาบนหน้าจอก่อน แล้วจึงสั่งล็อก
        popup.wait_visibility()
        popup.grab_set()
        # สร้าง Canvas และ Scrollbar (กำหนด scrollregion ลึก 850)
        canvas = tk.Canvas(popup, bg=self.bgpopup, highlightthickness=0, scrollregion=(0, 0, 800, 850))
        scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        # จัดวาง Canvas และ Scrollbar ให้อยู่ข้างกัน
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame ด้านในที่มีขนาด กว้าง 870 ยาว 1000
        content_frame = tk.Frame(canvas, bg=self.bgpopup, width=870, height=1000)
        canvas.create_window((0, 0), window=content_frame, anchor="nw")

        # ฟังก์ชันรองรับการเลื่อนด้วยลูกกลิ้งเมาส์ (MouseWheel)
        def on_mousewheel(event):
            if event.delta:
                canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)
        canvas.bind_all("<Button-4>", on_mousewheel)
        canvas.bind_all("<Button-5>", on_mousewheel)
        def on_close():
            canvas.unbind_all("<MouseWheel>")
            canvas.unbind_all("<Button-4>")
            canvas.unbind_all("<Button-5>")
            popup.destroy()

        popup.protocol("WM_DELETE_WINDOW", on_close)

        # -----------------------------------------------------------------------------------
        #------------------------------------Single cell title-------------------------------
        singlecell_title = tk.Label(
            content_frame, 
            text="Single Cell Settings",                          
            font=("Arial", 16), 
            bg=self.bgpopup,            
            fg="black"                      
        )
        singlecell_title.place(x=110, y=20)
        singlecell_border_frame = tk.Frame(
            content_frame,
            bg=self.bgpopup,
            highlightthickness=1,
            highlightbackground="black", # สีกรอบเส้นขอบ
        )
        singlecell_border_frame.place(x=80, y=35, width=630, height=145)
        # สั่งให้กรอบลงไปอยู่ชั้นล่างสุด
        singlecell_border_frame.lower()
        #------------------------------capacity edit-----------------------------------------
        def func_edit_capacity(event=None):
            raw_data = capacity_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Edited Capacity: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        capacity_edit = tk.Entry(
            singlecell_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        capacity_edit.insert(0, str(self.edit_capacity_val))
        capacity_edit.bind("<Return>", lambda event: (func_edit_capacity(), popup.focus_set()))
        capacity_edit.place(x=150, y=25, width=80, height=40)
        capacity_unit = tk.Label(
            singlecell_border_frame, 
            text="Ah",                          
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                      
        )
        capacity_unit.place(x=230, y=25, width=50, height=40)
        capacity_title = tk.Label(
            singlecell_border_frame,     
            text="Capacity",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        capacity_title.place(x=10, y=25,width=140, height=40)
        #------------------------------full voltage edit-----------------------------------------
        def func_full_voltage(event=None):
            raw_data = fullvolt_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Edited Full Voltage: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        fullvolt_edit = tk.Entry(
            singlecell_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        fullvolt_edit.insert(0, str(self.full_volt_val))
        fullvolt_edit.bind("<Return>", lambda event: (func_full_voltage(), popup.focus_set()))
        fullvolt_edit.place(x=150, y=85, width=80, height=40)
        fullvolt_unit = tk.Label(
            singlecell_border_frame, 
            text="V",                          
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        fullvolt_unit.place(x=230, y=85, width=50, height=40)
        fullvolt_title = tk.Label(
            singlecell_border_frame,     
            text="Full Voltage",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        fullvolt_title.place(x=10, y=85,width=140, height=40)
        #------------------------------empty voltage edit-----------------------------------------
        def func_empty_voltage(event=None):
            raw_data = emptyvolt_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Edited Empty Voltage: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        emptyvolt_edit = tk.Entry(
            singlecell_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        emptyvolt_edit.insert(0, str(self.empty_volt_val))
        emptyvolt_edit.bind("<Return>", lambda event: (func_empty_voltage(), popup.focus_set()))
        emptyvolt_edit.place(x=490, y=85, width=80, height=40)
        emptyvolt_unit = tk.Label(
            singlecell_border_frame, 
            text="V",                          
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        emptyvolt_unit.place(x=570, y=85, width=50, height=40)
        emptyvolt_title = tk.Label(
            singlecell_border_frame,     
            text="Empty Voltage",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        emptyvolt_title.place(x=350, y=85,width=140, height=40)
        #------------------------------------Battery pack title-------------------------------
        battpack_title = tk.Label(
            content_frame, 
            text="Battery Pack Settings",                          
            font=("Arial", 16), 
            bg=self.bgpopup,            
            fg="black"                      
        )
        battpack_title.place(x=110, y=200)
        battpack_border_frame = tk.Frame(
            content_frame,
            bg=self.bgpopup,
            highlightthickness=1,
            highlightbackground="black", # สีกรอบเส้นขอบ
        )
        battpack_border_frame.place(x=80, y=215, width=630, height=145)
        # สั่งให้กรอบลงไปอยู่ชั้นล่างสุด
        battpack_border_frame.lower()
        #------------------------------parallel edit-----------------------------------------
        def func_edit_parallel(event=None):
            raw_data = parallel_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set Parallel: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        parallel_edit = tk.Entry(
            battpack_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        parallel_edit.insert(0, str(self.parallel))
        parallel_edit.bind("<Return>", lambda event: (func_edit_parallel(), popup.focus_set()))
        parallel_edit.place(x=150, y=25, width=80, height=40)
        parallel_title = tk.Label(
            battpack_border_frame,     
            text="Parallel",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        parallel_title.place(x=10, y=25,width=140, height=40)
        #------------------------------inner resist edit-----------------------------------------
        def func_inner_resist(event=None):
            raw_data = inner_r_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set Inner Resistance: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        inner_r_edit = tk.Entry(
            battpack_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        inner_r_edit.insert(0, str(self.full_volt_val))
        inner_r_edit.bind("<Return>", lambda event: (func_inner_resist(), popup.focus_set()))
        inner_r_edit.place(x=190, y=85, width=80, height=40)
        inner_r_unit = tk.Label(
            battpack_border_frame, 
            text="mΩ",
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        inner_r_unit.place(x=270, y=85, width=50, height=40)
        inner_r_title = tk.Label(
            battpack_border_frame,     
            text="Inner Resistance",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        inner_r_title.place(x=10, y=85,width=180, height=40)
        #------------------------------series edit-----------------------------------------
        def func_series(event=None):
            raw_data = series_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set Series: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        series_edit = tk.Entry(
            battpack_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        series_edit.insert(0, str(self.series))
        series_edit.bind("<Return>", lambda event: (func_series(), popup.focus_set()))
        series_edit.place(x=490, y=25, width=80, height=40)
        series_title = tk.Label(
            battpack_border_frame,     
            text="Series",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        series_title.place(x=350, y=25,width=140, height=40)
        #------------------------------------Protection title-------------------------------
        protection_title = tk.Label(
            content_frame, 
            text="Protection Settings",                          
            font=("Arial", 16), 
            bg=self.bgpopup,            
            fg="black"                      
        )
        protection_title.place(x=110, y=380)
        protection_border_frame = tk.Frame(
            content_frame,
            bg=self.bgpopup,
            highlightthickness=1,
            highlightbackground="black", # สีกรอบเส้นขอบ
        )
        protection_border_frame.place(x=80, y=395, width=630, height=145)
        # สั่งให้กรอบลงไปอยู่ชั้นล่างสุด
        protection_border_frame.lower()
        #------------------------------soc high edit-----------------------------------------
        def func_edit_soc_high(event=None):
            raw_data = soc_high_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set SOC High: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        soc_high_edit = tk.Entry(
            protection_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        soc_high_edit.insert(0, str(self.soc_high_val))
        soc_high_edit.bind("<Return>", lambda event: (func_edit_soc_high(), popup.focus_set()))
        soc_high_edit.place(x=150, y=25, width=80, height=40)
        soc_high_unit = tk.Label(
            protection_border_frame, 
            text="%",                          
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        soc_high_unit.place(x=230, y=25, width=50, height=40)
        soc_high_title = tk.Label(
            protection_border_frame,     
            text="SOC High",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        soc_high_title.place(x=10, y=25,width=140, height=40)
        #------------------------------soc low edit-----------------------------------------
        def func_edit_soc_low(event=None):
            raw_data = soc_low_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set SOC Low: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        soc_low_edit = tk.Entry(
            protection_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        soc_low_edit.insert(0, str(self.soc_low_val))
        soc_low_edit.bind("<Return>", lambda event: (func_edit_soc_low(), popup.focus_set()))
        soc_low_edit.place(x=490, y=25, width=80, height=40)
        soc_low_unit = tk.Label(
            protection_border_frame, 
            text="%",
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        soc_low_unit.place(x=570, y=25, width=50, height=40)
        soc_low_title = tk.Label(
            protection_border_frame,     
            text="SOC Low",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        soc_low_title.place(x=350, y=25,width=140, height=40)
        #------------------------------charge current max edit-----------------------------------------
        def func_edit_chrg_amp_max(event=None):
            raw_data = chrg_amp_max_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set Charge Current Max: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        chrg_amp_max_edit = tk.Entry(
            protection_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        chrg_amp_max_edit.insert(0, str(self.chrg_amp_max_val))
        chrg_amp_max_edit.bind("<Return>", lambda event: (func_edit_chrg_amp_max(), popup.focus_set()))
        chrg_amp_max_edit.place(x=180, y=85, width=80, height=40)
        chrg_amp_max_unit = tk.Label(
            protection_border_frame, 
            text="A",
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        chrg_amp_max_unit.place(x=260, y=85, width=50, height=40)
        chrg_amp_max_title = tk.Label(
            protection_border_frame,     
            text="Charge Current Max",
            font=("Arial", 12),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        chrg_amp_max_title.place(x=10, y=85,width=170, height=40)
        #------------------------------discharge current max edit-----------------------------------------
        def func_edit_dischrg_amp_max(event=None):
            raw_data = dischrg_amp_max_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set Discharge Current Max: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        dischrg_amp_max_edit = tk.Entry(
            protection_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        dischrg_amp_max_edit.insert(0, str(self.dischrg_amp_max_val))
        dischrg_amp_max_edit.bind("<Return>", lambda event: (func_edit_dischrg_amp_max(), popup.focus_set()))
        dischrg_amp_max_edit.place(x=490, y=85, width=80, height=40)
        dischrg_amp_max_unit = tk.Label(
            protection_border_frame, 
            text="A",
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        dischrg_amp_max_unit.place(x=570, y=85, width=50, height=40)
        dischrg_amp_max_title = tk.Label(
            protection_border_frame,     
            text="Discharge Curr Max",
            font=("Arial", 12),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        dischrg_amp_max_title.place(x=320, y=85,width=170, height=40)
        
        #------------------------------------Running title----------------------------------
        running_title = tk.Label(
            content_frame, 
            text="Running Settings",                          
            font=("Arial", 16), 
            bg=self.bgpopup,            
            fg="black"                      
        )
        running_title.place(x=110, y=560)
        running_border_frame = tk.Frame(
            content_frame,
            bg=self.bgpopup,
            highlightthickness=1,
            highlightbackground="black", # สีกรอบเส้นขอบ
        )
        running_border_frame.place(x=80, y=575, width=630, height=145)
        # สั่งให้กรอบลงไปอยู่ชั้นล่างสุด
        running_border_frame.lower()
        #------------------------------Initial soc edit-----------------------------------------
        def func_edit_soc_init(event=None):
            raw_data = soc_init_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set SOC Init: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        soc_init_edit = tk.Entry(
            running_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        soc_init_edit.insert(0, str(self.init_soc_val))
        soc_init_edit.bind("<Return>", lambda event: (func_edit_soc_init(), popup.focus_set()))
        soc_init_edit.place(x=150, y=25, width=80, height=40)
        soc_init_unit = tk.Label(
            running_border_frame, 
            text="%",                          
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        soc_init_unit.place(x=230, y=25, width=50, height=40)
        soc_init_title = tk.Label(
            running_border_frame,     
            text="SOC Init",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        soc_init_title.place(x=10, y=25,width=140, height=40)
        #------------------------------voc init edit-----------------------------------------
        def func_edit_voc_init(event=None):
            raw_data = voc_init_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set VOC Init: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        voc_init_edit = tk.Entry(
            running_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        voc_init_edit.insert(0, str(self.init_voc_val))
        voc_init_edit.bind("<Return>", lambda event: (func_edit_voc_init(), popup.focus_set()))
        voc_init_edit.place(x=490, y=25, width=80, height=40)
        voc_init_unit = tk.Label(
            running_border_frame, 
            text="V",
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        voc_init_unit.place(x=570, y=25, width=50, height=40)
        voc_init_title = tk.Label(
            running_border_frame,     
            text="VOC Init",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        voc_init_title.place(x=350, y=25,width=140, height=40)
        #------------------------------Init CAP edit-----------------------------------------
        def func_edit_cap_init(event=None):
            raw_data = cap_init_edit.get()
            try:
                target_value = float(raw_data)
                print(f"Set Init CAP: {target_value}")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
        cap_init_edit = tk.Entry(
            running_border_frame, 
            font=("Arial", 14),
            bg="#dce2e8",     
            fg="black",    
            insertbackground=self.bgpopup, 
            relief="flat",
            justify="center"  
        )
        cap_init_edit.insert(0, str(self.init_cap_val))
        cap_init_edit.bind("<Return>", lambda event: (func_edit_cap_init(), popup.focus_set()))
        cap_init_edit.place(x=150, y=85, width=80, height=40)
        cap_init_unit = tk.Label(
            running_border_frame, 
            text="Ah",
            font=("Arial", 14), 
            bg=self.bgpopup,            
            fg="black"                        
        )
        cap_init_unit.place(x=230, y=85, width=50, height=40)
        cap_init_title = tk.Label(
            running_border_frame,     
            text="Init CAP",
            font=("Arial", 14),    
            bg=self.bgpopup,
            highlightthickness=1,          
            highlightbackground="#ffffff", 
            fg="black"           
        )
        cap_init_title.place(x=10, y=85,width=140, height=40)
    
        #--------------------------------save button----------------------------------------
        def save_edit():
            try :
                self.edit_capacity_val = float(capacity_edit.get())
                self.full_volt_val = float(fullvolt_edit.get())
                self.empty_volt_val = float(emptyvolt_edit.get())
                self.parallel = int(parallel_edit.get())
                self.series = int(series_edit.get())
                self.inner_resist_val = float(inner_r_edit.get())
                self.soc_high_val = int(soc_high_edit.get())
                self.soc_low_val = int(soc_low_edit.get())
                self.chrg_amp_max_val = float(chrg_amp_max_edit.get())
                self.dischrg_amp_max_val = float(dischrg_amp_max_edit.get())
                self.init_soc_val = int(soc_init_edit.get())
                self.init_voc_val = float(voc_init_edit.get())
                self.init_cap_val = float(cap_init_edit.get())
                if not self.running_time:
                    self.soc_now_val = int(soc_init_edit.get())
                print("Save!")
            except ValueError:
                print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลข!")
        save_button = tk.Button(
            content_frame,
            command=save_edit,
            text="SAVE",
            font=("Arial", 14, "bold"),
            bg=self.bgcolor2,              
            fg=self.bgpopup,                
            activebackground="#17033b",
            activeforeground=self.bgpopup,  
            width=10,                  
            height=2,                  
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",             
            cursor="hand2"             
        )
        save_button.place(x=700, y=800, anchor="center")
        #--------------------------------------------------------------------------

        #-------------------------------------------------------------------------
        popup.wait_window(popup) # บล็อกการทำงานจนกว่าหน้าต่าง popup จะถูกปิด
        #-------------------------------------------------------------------------
        
        
if __name__ == "__main__":
    # 1. สร้าง Root Window ขึ้นมาเป็น Parent ชั่วคราว
    root = tk.Tk()
    root.title("Test: Batterysimulationpage")
    root.geometry("950x570")

    # 2. นำหน้านี้มาวางลงใน Root
    app = Batterysimulationpage(parent=root)
    app.pack(fill="both", expand=True)
    
    #def terminal_input():
    #    while True:
    #       try:
    #           app.soc_now_val = float(input("Enter SOC (%): "))
    #       except ValueError:
    #           pass

    #threading.Thread(target=terminal_input, daemon=True).start()
    # 3. เริ่ม Event Loop
    root.mainloop()
    