import tkinter as tk
from datetime import timedelta
from tkinter import ttk
from basePage import BasePage
from warningmessagePage import WarningmessagePage
class CanlogPage(BasePage):
    def __init__(self, parent, controller):
        # 1. Mount as a tk.Frame child inside master container
        super().__init__(parent, controller)
        self.controller = controller
    
        self.grid(row=0, column=0, sticky="nsew")
        
        self.bgcolor1 = "#a67dc9" #สีอ่อน
        self.bgcolor2 = "#573172" #สีเข้ม
        
        self.apply_table_style()
        self.create_table()
        self.poll_can_log()  # Start polling for CAN log updates

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
        columns = ("timestamp", "txrx", "can_id", "can_data", "translation")
        headers = ("Time stamp", "TxRx", "CAN ID","CAN DATA","Translation")

        # ใส่ style="Custom.Treeview" เพื่อดึงค่าสีที่ตั้งไว้มาใช้
        self.tree = ttk.Treeview(self, columns=columns, show="headings", style="Custom.Treeview")

        for col, text in zip(columns, headers):
            self.tree.heading(col, text=text, anchor=tk.W)
            self.tree.column(col, anchor=tk.W, stretch=True)
            
        data = [
        ]
        # --- 2. วนลูปเพิ่มข้อมูลลงในตาราง ---
        for row in data:
            self.tree.insert("", tk.END, values=row)

        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    def poll_can_log(self):
        """Drains live CAN frames from controller.can_log_queue into the table."""
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "can_log_queue"):
            q = self.controller.can_log_queue
            while not q.empty():
                try:
                    entry = q.get_nowait()
                    # Supports either a tuple/list of 5 items or a dict
                    if isinstance(entry, dict):
                        row = (
                            entry.get("timestamp", ""),
                            entry.get("txrx", ""),
                            entry.get("can_id", ""),
                            entry.get("can_data", ""),
                            entry.get("translation", ""),
                        )
                    else:
                        row = tuple(entry)

                    self.tree.insert("", tk.END, values=row)
                    # Keep max 500 rows in memory & auto-scroll to latest
                    children = self.tree.get_children()
                    if len(children) > 500:
                        self.tree.delete(children[0])
                    self.tree.yview_moveto(1.0)
                except Exception:
                    break

        self.after(150, self.poll_can_log)
"""
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("950x570")
    app = WarningmessagePage(root)
    root.mainloop()
"""