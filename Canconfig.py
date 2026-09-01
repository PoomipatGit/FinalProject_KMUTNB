import tkinter as tk
from datetime import timedelta
from basePage import BasePage
class Canconfigpage(BasePage):
    def __init__(self, parent, controller):
        # 1. Mount as a tk.Frame child inside master container
        super().__init__(parent, controller)
        self.controller = controller
#self.can_config.title("Can Config")
        self.bgcolor1 = "#a67dc9" #สีอ่อน
        self.bgcolor2 = "#573172" #สีเข้ม
        self.protocol_var = tk.StringVar(value="CANopen")
        self.baudrate_val = tk.StringVar()
        self.canmsgtype_var = tk.StringVar(value="29-Bit")
        self.supplyid_val = tk.StringVar(value= "0x10")
        self.commandid_val = tk.StringVar(value= "0x200")
        self.listenerid_val = tk.StringVar(value= "0x201")
        self.timeout_val = tk.StringVar()
        #Run
        self.network_frame()
        self.protocal_frame()
        self.baudrate_frame()
        self.baudrate_button()
        self.can_msg_type_frame()
        self.identifier_frame()
        self.supplyID_frame()
        self.supplyID_button()
        self.commandID_frame()
        self.commandID_button()
        self.lisenerID_frame()
        self.listenerID_button()
        self.network_safety()
        self.timeout_frame()
        self.timeout_button()
        self.timeoutaction_frame()
        self.test_connection()
        self.button_ping()
        self.button_test()
        #network setting
    def network_frame(self):
        self.network_setting_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            width=460, 
            height=220,
            bd=0,                   
            relief="flat",
        )
        self.network_setting_container.place(x=10, y=40)
        self.network_setting_container.grid_propagate(False)
        self.network_setting_title = tk.Label(
            self.network_setting_container,     
            text="Network Setting",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.network_setting_title.place(x=10, y=20, anchor="w") 
        
        # Protocal
    def protocal_frame(self):
        self.protocal_box = tk.Frame(
            self.network_setting_container,
            bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
            highlightbackground="black",  # สีเส้นกรอบ
            highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
            bd=0
        )
        self.protocal_box.place(x=10, y=40, width=440, height=50)
        self.protocal_label = tk.Label(
            self.protocal_box,
            text="Protocal :",
            font=("Arial", 14),
            bg=self.bgcolor1,     # สีพื้นข้างใน
            fg="black",     # สีตัวอักษร
            anchor="center"
        )
        self.protocal_label.place(x=0, y=0, width=100, height=48)
        tk.Radiobutton(
            self.protocal_box,
            text="CANopen",
            variable=self.protocol_var,
            value="CANopen",
            command=self.protocol_changed,
            bg=self.bgcolor1,
            font=("Arial", 14),
        ).place(x=100, y=8)
        tk.Radiobutton(
            self.protocal_box,
            text="CAN FD",
            variable=self.protocol_var,
            value="CAN FD",
            command=self.protocol_changed,
            bg=self.bgcolor1,
            font=("Arial", 14),
        ).place(x=220, y=8)
        tk.Radiobutton(
            self.protocal_box,
            text="J1979",
            variable=self.protocol_var,
            value="J1979",
            command=self.protocol_changed,
            bg=self.bgcolor1,
            font=("Arial", 14),
        ).place(x=340, y=8)
    def protocol_changed(self):
        selected = self.protocol_var.get()
        print("Selected Protocol =", selected)
        # ตรงนี้ใส่คำสั่งที่อยากให้รันทันที
        if selected == "CANopen":
            print("Run CANopen setting")
        elif selected == "CAN FD":
            print("Run CAN FD setting")
        elif selected == "J1979":
            print("Run J1979 setting")
        #Baudrate
    def baudrate_frame(self):
        # Baud rate
        self.baudrate_box = tk.Frame(
            self.network_setting_container,
            bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
            highlightbackground="black",  # สีเส้นกรอบ
            highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
            bd=0
        )
        self.baudrate_box.place(x=10, y=100, width=440, height=50)
        self.baudrate_label = tk.Label(
            self.baudrate_box,
            text="Baud Rate :",
            font=("Arial", 14),
            bg=self.bgcolor1,     # สีพื้นข้างใน
            fg="black",     # สีตัวอักษร
            anchor="center"
        )
        self.baudrate_label.place(x=10, y=0, width=100, height=48)
    def baudrate_button(self):
        self.baudrate_key = tk.Entry(
            self.baudrate_box, 
            textvariable=self.baudrate_val,
            font=("Arial", 14),
            bg=self.bgcolor1,     
            fg="Black",    
            relief="flat",
            justify="center"  
        )
        self.baudrate_key.bind("<Return>", lambda event: self.func_baudrate())
        self.baudrate_key.place(x=120, y=4, width=130, height=40)
        self.baudrate_unit = tk.Label(
            self.baudrate_box, 
            text="kbps",                          
            font=("Arial", 14), 
            bg=self.bgcolor1,              
            fg="Black"                        
        )
        self.baudrate_unit.place(x=250, y=4, width=60, height=40)
    def func_baudrate(self):
        raw_data = self.baudrate_val.get()
        try:
            target_value = float(raw_data)
            print(f"Baud rate: {target_value} kbps")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
            
    #can message type
    def can_msg_type_frame(self):
        # Baud rate
        self.can_msg_type_box = tk.Frame(
            self.network_setting_container,
            bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
            highlightbackground="black",  # สีเส้นกรอบ
            highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
            bd=0
        )
        self.can_msg_type_box.place(x=10, y=160, width=440, height=50)
        self.can_msg_type_label = tk.Label(
            self.can_msg_type_box,
            text="CAN Message Type :",
            font=("Arial", 14),
            bg=self.bgcolor1,     # สีพื้นข้างใน
            fg="black",     # สีตัวอักษร
            anchor="center"
        )
        self.can_msg_type_label.place(x=0, y=4, width=200, height=40)
        tk.Radiobutton(
            self.can_msg_type_box,
            text="11-Bit",
            variable=self.canmsgtype_var,
            value="11-Bit",
            command=self.canmsgtype_changed,
            bg=self.bgcolor1,
            font=("Arial", 14),
        ).place(x=210, y=8)
        tk.Radiobutton(
            self.can_msg_type_box,
            text="29-Bit",
            variable=self.canmsgtype_var,
            value="29-Bit",
            command=self.canmsgtype_changed,
            bg=self.bgcolor1,
            font=("Arial", 14),
        ).place(x=300, y=8)
    def canmsgtype_changed(self):
        selected = self.canmsgtype_var.get()
        print("Selected CAN message type =", selected)
        # ตรงนี้ใส่คำสั่งที่อยากให้รันทันที
        if selected == "11-Bit":
            print("Can message type : 11 Bit")
        elif selected == "29-Bit":
            print("Can message type : 29 Bit")
            
        #identifier frame
    def identifier_frame(self):
        self.indentifier_setting_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            width=460, 
            height=220,
            bd=0,                   
            relief="flat",
        )
        self.indentifier_setting_container.place(x=480, y=40)
        self.indentifier_setting_container.grid_propagate(False)
        self.indentifier_setting_title = tk.Label(
            self.indentifier_setting_container,     
            text="Indentifier Setting",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
            )
        self.indentifier_setting_title.place(x=10, y=20, anchor="w")
    def supplyID_frame(self):
        self.supplyID_box = tk.Frame(
                    self.indentifier_setting_container,
                    bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
                    highlightbackground="black",  # สีเส้นกรอบ
                    highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
                    bd=0
                )
        self.supplyID_box.place(x=10, y=40, width=440, height=50)
        self.supplyID_label = tk.Label(
                    self.supplyID_box,
                    text="Supply ID :",
                    font=("Arial", 14),
                    bg=self.bgcolor1,     # สีพื้นข้างใน
                    fg="black",     # สีตัวอักษร
                    anchor="center"
                )
        self.supplyID_label.place(x=10, y=0, width=100, height=48)
    def supplyID_button(self):
        self.supplyid_key = tk.Entry(
            self.supplyID_box, 
            textvariable=self.supplyid_val,
            font=("Arial", 14),
            bg=self.bgcolor1,     
            fg="Black",    
            relief="flat",
            justify="left"  
        )
        self.supplyid_key.bind("<Return>", lambda event: self.func_supplyid())
        self.supplyid_key.place(x=110, y=4, width=100, height=40)
    def func_supplyid(self):
            raw_data = self.supplyid_val.get()
            #try:
            target_value = raw_data
            print(f"Supply ID: {target_value}")
            # except ValueError:
            #print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
            
    def commandID_frame(self):
        self.commandID_box = tk.Frame(
                    self.indentifier_setting_container,
                    bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
                    highlightbackground="black",  # สีเส้นกรอบ
                    highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
                    bd=0
                )
        self.commandID_box.place(x=10, y=100, width=440, height=50)
        self.commandID_label = tk.Label(
                    self.commandID_box,
                    text="Command ID :",
                    font=("Arial", 14),
                    bg=self.bgcolor1,     # สีพื้นข้างใน
                    fg="black",     # สีตัวอักษร
                    anchor="center"
                )
        self.commandID_label.place(x=10, y=0, width=120, height=48)
    def commandID_button(self):
            self.commandid_key = tk.Entry(
                self.commandID_box, 
                textvariable=self.commandid_val,
                font=("Arial", 14),
                bg=self.bgcolor1,     
                fg="Black",    
                relief="flat",
                justify="left"  
            )
            self.commandid_key.bind("<Return>", lambda event: self.func_commandid())
            self.commandid_key.place(x=135, y=4, width=100, height=40)
    def func_commandid(self):
                raw_data = self.commandid_val.get()
                #try:
                target_value = raw_data
                print(f"Command ID: {target_value}")
                # except ValueError:
                #print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")  
                
                            
    def lisenerID_frame(self):
        self.lisenerID_box = tk.Frame(
                    self.indentifier_setting_container,
                    bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
                    highlightbackground="black",  # สีเส้นกรอบ
                    highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
                    bd=0
                )
        self.lisenerID_box.place(x=10, y=160, width=440, height=50)
        self.lisenerID_label = tk.Label(
                    self.lisenerID_box,
                    text="Listener ID :",
                    font=("Arial", 14),
                    bg=self.bgcolor1,     # สีพื้นข้างใน
                    fg="black",     # สีตัวอักษร
                    anchor="center"
                )
        self.lisenerID_label.place(x=10, y=0, width=110, height=48)
    def listenerID_button(self):
                self.listenerid_key = tk.Entry(
                    self.lisenerID_box, 
                    textvariable=self.listenerid_val,
                    font=("Arial", 14),
                    bg=self.bgcolor1,     
                    fg="Black",    
                    relief="flat",
                    justify="left"  
                )
                self.listenerid_key.bind("<Return>", lambda event: self.func_listenerid())
                self.listenerid_key.place(x=120, y=4, width=100, height=40)
    def func_listenerid(self):
                    raw_data = self.listenerid_val.get()
                    #try:
                    target_value = raw_data
                    print(f"Listener ID: {target_value}")
                    # except ValueError:
                    #print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!") 
                    
        #Network safety​
    def network_safety(self):
        self.Network_safety_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            width=930, 
            height=130,
            bd=0,                   
            relief="flat",
        )
        self.Network_safety_container.place(x=10, y=270)
        self.Network_safety_container.grid_propagate(False)
        self.Network_safety_title = tk.Label(
            self.Network_safety_container,     
            text="Indentifier Setting",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.Network_safety_title.place(x=10, y=20, anchor="w")
    def timeout_frame(self):
        self.timeout_box = tk.Frame(
                            self.Network_safety_container,
                            bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
                            highlightbackground="black",  # สีเส้นกรอบ
                            highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
                            bd=0
                        )
        self.timeout_box.place(x=10, y=50, width=220, height=50)
        self.timeout_label = tk.Label(
                            self.timeout_box,
                            text="Time out :",
                            font=("Arial", 14),
                            bg=self.bgcolor1,     # สีพื้นข้างใน
                            fg="black",     # สีตัวอักษร
                            anchor="center"
                        )
        self.timeout_label.place(x=0, y=4, width=100, height=40)
    def timeout_button(self):
        self.timeout_key = tk.Entry(
            self.timeout_box, 
            textvariable=self.timeout_val,
            font=("Arial", 14),
            bg=self.bgcolor1,     
            fg="Black",    
            relief="flat",
            justify="center"  
        )
        self.timeout_key.bind("<Return>", lambda event: self.func_timeout())
        self.timeout_key.place(x=100, y=4, width=80, height=40)
        self.timeout_unit = tk.Label(
            self.timeout_box, 
            text="ms",                          
            font=("Arial", 14), 
            bg=self.bgcolor1,              
            fg="Black"                        
        )
        self.timeout_unit.place(x=180, y=4, width=30, height=40)
    def func_timeout(self):
        raw_data = self.timeout_val.get()
        try:
            target_value = float(raw_data)
            print(f"Timeout: {target_value} ms")
        except ValueError:
            print("ข้อผิดพลาด: กรุณากรอกเฉพาะตัวเลขเท่านั้น!")   
                
    def timeoutaction_frame(self):
        self.timeoutaction_box = tk.Frame(
            self.Network_safety_container,
            bg=self.bgcolor1,                 # สีพื้นด้านในกล่อง
            highlightbackground="black",  # สีเส้นกรอบ
            highlightthickness=1,         # ความหนาเส้นกรอบ 1 px
            bd=0
        )
        self.timeoutaction_box.place(x=240, y=50, width=680, height=50)
        self.timeoutaction_label = tk.Label(
            self.timeoutaction_box,
            text="Time out Action :",
            font=("Arial", 14),
            bg=self.bgcolor1,     # สีพื้นข้างใน
            fg="black",     # สีตัวอักษร
            anchor="center"
        )
        self.timeoutaction_label.place(x=0, y=4, width=160, height=40)
        tk.Radiobutton(
            self.timeoutaction_box,
            text="Reset command/Force OFF output",
            variable=self.canmsgtype_var,
            value="off",
            command=self.timeoutaction_changed,
            bg=self.bgcolor1,
            font=("Arial", 13),
        ).place(x=165, y=12)
        tk.Radiobutton(
            self.timeoutaction_box,
            text="Auto reconnect [x] times​",
            variable=self.canmsgtype_var,
            value="reconnect",
            command=self.timeoutaction_changed,
            bg=self.bgcolor1,
            font=("Arial", 13),
        ).place(x=455, y=12)
    def timeoutaction_changed(self):
        selected = self.canmsgtype_var.get()
        print("Time out action =", selected)
        # ตรงนี้ใส่คำสั่งที่อยากให้รันทันที
        if selected == "off":
            print("Time out action : Reset Command/Force OFF output")
        elif selected == "reconnect":
            print("Time out action : Auto Reconnect [x] times")

        #Test connection
    def test_connection(self):
        self.test_connection_container = tk.LabelFrame(
            self,
            bg=self.bgcolor1, 
            width=460, 
            height=140,
            bd=0,                   
            relief="flat",
        )
        self.test_connection_container.place(x=10, y=411)
        self.test_connection_container.grid_propagate(False)
        self.test_connection_title = tk.Label(
            self.test_connection_container,     
            text="Test Connection",
            font=("Arial", 14),    
            bg=self.bgcolor1,
            fg="white"           
        )
        self.test_connection_title.place(x=10, y=20, anchor="w") 
    def button_ping(self):
        self.ping_button = tk.Button(
            self.test_connection_container,
            command=self.func_ping,
            text="Ping",
            font=("Arial", 12, "bold"),
            bg=self.bgcolor2,              
            fg="white",                
            activebackground="#17033b",
            activeforeground="white",  
            width=8,                  
            height=2,                  
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",             
            cursor="hand2"             
        )
        self.ping_button.place(x=30, y=80, anchor="w")
    def func_ping(self):
            print("Ping")
            
    def button_test(self):
        self.test_button = tk.Button(
            self.test_connection_container,
            command=self.func_test,
            text='Send "Test Message"',
            font=("Arial", 12, "bold"),
            bg=self.bgcolor2,              
            fg="white",                
            activebackground="#17033b",
            activeforeground="white",  
            width=18,                  
            height=2,                  
            highlightthickness=1,          
            highlightbackground="#ffffff",
            relief="flat",             
            cursor="hand2"             
        )
        self.test_button.place(x=140, y=80, anchor="w")
    def func_test(self):
        print("Test Message")
    #def test_message
if __name__ == "__main__":
    can_config = tk.Tk()
    can_config.geometry("950x570") 
    app =Canconfigpage(can_config) #go to Run in init
    can_config.mainloop()
    
