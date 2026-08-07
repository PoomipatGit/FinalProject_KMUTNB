import tkinter as tk
from datetime import timedelta
class Canconfigpage:
    def __init__(self, can_config):
        self.can_config = can_config
        self.can_config.title("Can Config")
        self.bgcolor1 = "#cba2e7" #สีอ่อน
        self.bgcolor2 = "#8056a5" #สีเข้

        #Run
        self.network_setting()
        self.identifier_setting()
        self.network_safety()
        self.test_connection()
        
		#network setting
    def network_setting(self):
        self.network_setting_container = tk.LabelFrame(
			self.can_config,
			bg=self.bgcolor1, 
			width=460, 
			height=220,
			bd=0,                   
            relief="flat",
		)
        self.network_setting_container.place(x=10, y=58)
        self.network_setting_container.grid_propagate(False)
        self.network_setting_title = tk.Label(
            self.network_setting_container,     
            text="Network Setting",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.network_setting_title.place(x=10, y=20, anchor="w") 
        
        #identifier setting
    def identifier_setting(self):
        self.indentifier_setting_container = tk.LabelFrame(
            self.can_config,
            bg=self.bgcolor1, 
            width=460, 
            height=220,
            bd=0,                   
            relief="flat",
        )
        self.indentifier_setting_container.place(x=480, y=58)
        self.indentifier_setting_container.grid_propagate(False)
        self.indentifier_setting_title = tk.Label(
            self.indentifier_setting_container,     
            text="Indentifier Setting",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
            )
        self.indentifier_setting_title.place(x=10, y=20, anchor="w")
        
        #Network safety​
    def network_safety(self):
        self.Network_safety_container = tk.LabelFrame(
			self.can_config,
			bg=self.bgcolor1, 
			width=930, 
			height=146,
			bd=0,                   
            relief="flat",
		)
        self.Network_safety_container.place(x=10, y=288)
        self.Network_safety_container.grid_propagate(False)
        self.Network_safety_title = tk.Label(
            self.Network_safety_container,     
            text="Indentifier Setting",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.Network_safety_title.place(x=10, y=20, anchor="w")
        
        #Test connection
    def test_connection(self):
        self.test_connection_container = tk.LabelFrame(
			self.can_config,
			bg=self.bgcolor1, 
			width=460, 
			height=116,
			bd=0,                   
            relief="flat",
		)
        self.test_connection_container.place(x=10, y=444)
        self.test_connection_container.grid_propagate(False)
        self.test_connection_title = tk.Label(
            self.test_connection_container,     
            text="Test Connection",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.test_connection_title.place(x=10, y=20, anchor="w") 


if __name__ == "__main__":
    can_config = tk.Tk()
    can_config.geometry("950x570") 
    app =Canconfigpage(can_config) #go to Run in init
    can_config.mainloop()
	
