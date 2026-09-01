import tkinter as tk
from tkinter import ttk

# Import all page classes
from homePage import homePage
from sourcePage import sourcePage
from batterytest import BatteryTestpage
from loadPage import loadPage
from Canconfig import Canconfigpage
from warningmessagePage import WarningmessagePage
from canlogPage import CanlogPage
from batterysimulationPage import Batterysimulationpage
from canMessageSetup import canMessageSetup
from canSequencePage import canSequencePage
from canMessageCommand import canMessageCommand


class bidirectional_DC_supply_app(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Power Supply Control System")
        self.geometry("950x570")

        # --- 1. Global Shared Data Dictionary ---
        self.shared_data = {
            "system_stage": "Standby",
            "active_category": "Fixed",
            "control_sub_mode": "CV",
            "set_voltage": 0.0,
            "set_current": 0.0,
            "set_power": 0.0,
        }

        # --- 2. Navigation History Tracking ---
        self.page_history = []       # Stack storing visited page references
        self.current_page = None     # Reference to the active page on screen

        # --- 3. Master Page Container Frame ---
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # --- 4. Instantiate & Stack All Pages ---
        self.frames = {}
#       GUI_page = [homePage, sourcePage, loadPage, batteryTestPage, warningPage, canlogPage, canConfigPage,
#                     canCommandPage, canSequencePage]
        GUI_page = [homePage, sourcePage, loadPage, BatteryTestpage,Batterysimulationpage, WarningmessagePage, CanlogPage, Canconfigpage]
        for F in GUI_page:
        pages = (
            homePage,
            sourcePage,
            BatteryTestpage,
            loadPage,
            canMessageSetup,
            canSequencePage,
            canMessageCommand
        )

        for F in pages:
            frame = F(parent=container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Load initial landing page without recording it in history
        self.show_frame(homePage, record_history=False)

    # -------------------------------------------------------------------------
    # Navigation & Page Tracking Methods
    # -------------------------------------------------------------------------

    def show_frame(self, cont, record_history=True):
        """
        Raises the target frame to the front and pushes the previous 
        page onto the history stack.
        """
        # Resolve string names (e.g. "sourcePage") to actual class references
        if isinstance(cont, str):
            for page_class in self.frames:
                if page_class.__name__ == cont:
                    cont = page_class
                    break

        if cont not in self.frames:
            print(f"[NAV ERROR]: Frame '{cont}' not found in registered pages.")
            return

        # Record the current page to history before switching
        if record_history and self.current_page is not None and self.current_page != cont:
            self.page_history.append(self.current_page)

        # Update active pointer and raise frame
        self.current_page = cont
        self.frames[cont].tkraise()

    def go_back(self):
        """Pops the most recent page from history and raises it."""
        if self.page_history:
            prev_page = self.page_history.pop()
            # Navigate back without pushing to the stack again
            self.show_frame(prev_page, record_history=False)
            print(f"[NAV INFO]: Returned to -> {prev_page.__name__}")
        else:
            print("[NAV INFO]: History stack is empty. Already at initial page.")


if __name__ == "__main__":
    app = bidirectional_DC_supply_app()
    app.mainloop()