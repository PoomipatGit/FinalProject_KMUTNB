import tkinter as tk
from datetime import timedelta
from tkinter import ttk
from basePage import BasePage
class WarningmessagePage(BasePage):
    def __init__(self, parent, controller):
        # 1. Mount as a tk.Frame child inside master container
        super().__init__(parent, controller)
        self.controller = controller
    
        self.grid(row=0, column=0, sticky="nsew")
        
        self.bgcolor1 = "#a67dc9" #สีอ่อน
        self.bgcolor2 = "#573172" #สีเข้ม
        
        self.apply_table_style()
        self.create_table()

    def apply_table_style(self):
        """
        กำหนดสีพื้นหลัง สีตัวอักษร และสีหัวตาราง
        """
        style = ttk.Style()
        style.theme_use("clam")  # ต้องใช้ clam theme เพื่อให้เปลี่ยนสี Header ได้สมบูรณ์
        
        # --- 1. สั่งให้ Treeview วาดเส้นรอบแต่ละเซลล์ ---
        # --- ปรับแต่งส่วนเนื้อหาตาราง (Rows) ---
        style.configure(
            "Custom.Treeview",
            background=self.bgcolor1,         # สีพื้นหลังแถว
            foreground="black",               # สีข้อความในแถว
            fieldbackground=self.bgcolor1,    # สีพื้นหลังพื้นที่ว่างของตาราง
            rowheight=30,                     # ความสูงของแต่ละแถว (ปรับให้อ่านง่ายขึ้น)
            font=("Segoe UI", 14),
            relief="solid",
            borderwidth=1,
            lightcolor="#ffffff",
            darkcolor="#ffffff"
        )
        

        # --- ปรับแต่งส่วนหัวตาราง (Headings) ---
        style.configure(
            "Custom.Treeview.Heading",
            background=self.bgcolor2,         # สีพื้นหลังหัวตาราง
            foreground="white",               # สีข้อความหัวตาราง
            font=("Segoe UI", 14, "bold"),
            relief="flat"
        )
        
        # ป้องกันไม่ให้สี Header เปลี่ยนเมื่อเอาเมาส์ไปชี้ (Hover)
        style.map("Custom.Treeview.Heading", background=[("active", self.bgcolor2)])
        style.map("Custom.Treeview", background=[("active", self.bgcolor1)])

    def create_table(self):
        # Container frame at Row 1 of BasePage
        table_container = tk.Frame(self, bg=self.bgcolor1)
        table_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)

        columns = ("type", "detail", "action")
        headers = ("Type", "Detail", "Action taken")

        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")

        for col, text in zip(columns, headers):
            self.tree.heading(col, text=text, anchor=tk.W)
            self.tree.column(col, anchor=tk.W, stretch=True)

        # Scrollbar inside the table_container
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        data = [
            ("Communication", "CAN Message cannot send/receive", "Reconnecting......."),
            ("Power", "Input power not sufficient", "None, please manual check"),
            ("Parameter warning", "Under/Over Output Voltage", ""),
            ("Parameter warning", "Under/Over Output Current", ""),
            ("Parameter warning", "Under/Over Output Power", ""),
            ("Parameter warning", "Under/Over Temperature", ""),
            ("Fault", "Current spiked to X A", "Shutdown output"),
        ]

        for row in data:
            self.tree.insert("", tk.END, values=row)
