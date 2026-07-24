import tkinter as tk
class sourcePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        label = tk.Label(self, text="Source Page", font=("Helvetica", 16))
        label.pack(pady=10, padx=10)