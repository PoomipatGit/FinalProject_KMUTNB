import tkinter as tk
from tkinter import ttk
from homePage import homePage
from sourcePage import sourcePage


class bidirectional_DC_supply_app(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Power Supply Control System")
        self.geometry("950x570")

        self.shared_data = {
            "voltage_set": tk.StringVar(value="0.0"),
            "current_live": tk.StringVar(value="0.00"),
            "system_stage": tk.StringVar(value="Standby")
        }

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        self.frames = {}
#       GUI_page = [homePage, sourcePage, loadPage, batteryTestPage, warningPage, canlogPage, canConfigPage,
#                     canCommandPage, canSequencePage]
        GUI_page = [homePage, sourcePage]
        for F in GUI_page:
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame(homePage)
        
    def show_frame(self, cont):
        self.frames[cont].tkraise()


if __name__ == "__main__":
    app = bidirectional_DC_supply_app()
    app.mainloop()