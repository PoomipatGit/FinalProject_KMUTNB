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
        #columns: กำหนด Identifier (ID อ้างอิง) ประจำแต่ละคอลัมน์ ใช้สำหรับเขียนโค้ด
        #headers: กำหนดข้อความที่แสดงจริงบนหน้าจอให้ผู้ใช้เห็น
        columns = ("type", "detail", "action")
        headers = ("Type", "Detail", "Action taken")

        # ใส่ style="Custom.Treeview" เพื่อดึงค่าสีที่ตั้งไว้มาใช้
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style="Custom.Treeview")

        for col, text in zip(columns, headers):
            self.tree.heading(col, text=text, anchor=tk.W)
            self.tree.column(col, anchor=tk.W, stretch=True)
            
        data = [
            ("Communication", "CAN Message cannot send/receive", "Reconnecting......."),
            ("Power", "Input power not sufficient", "None, please manual check"),
            ("Parameter warning", "Under/Over Output Voltage", ""),
            ("Parameter warning", "Under/Over Output Current", ""),
            ("Parameter warning", "Under/Over Output Power", ""),
            ("Parameter warning", "Under/Over Temperature", ""),
            ("Fault", "Current spiked to X A", "Shutdown output"),
        ]
        # --- 2. วนลูปเพิ่มข้อมูลลงในตาราง ---
        for row in data:
            self.tree.insert("", tk.END, values=row)

        self.tree.pack(fill=tk.BOTH, expand=True)
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("950x570")
    app = WarningmessagePage(root)
    root.mainloop()
