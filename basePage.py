import tkinter as tk
from tkinter import ttk


class BasePage(tk.Frame):
    button_color = "#573172"
    label_color = "#8056a5"

    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        # --- Top Status Bar Container ---
        self.top_container = tk.Frame(self, bg="#FFFFFF")
        self.top_container.pack(side="top", fill="x", pady=0, padx=0)
        self.setup_status_bar()

    @property
    def PAGES_MAP(self):
        """Lazy-loads page classes when accessed to prevent circular import loops."""
        from batterytest import BatteryTestpage
        from canMessageSetup import canMessageSetup
        from homePage import homePage
        from loadPage import loadPage
        from sourcePage import sourcePage

        return {
            "CAN Setup": canMessageSetup,
            "Home": homePage,
            "Source": sourcePage,
            "Load": loadPage,
            "Battery Test": BatteryTestpage,
        }

    def setup_status_bar(self):
        btn_style = {
            "font": ("Helvetica", 9, "bold"),
            "relief": "groove",
            "bd": 2,
            "padx": 12,
            "pady": 1,
            "activebackground": self.button_color,
        }

        # 1. Left Nav Buttons
        for text, cmd in [
            ("Home", self.go_home),
            ("File", self.open_file_selector),
        ]:
            tk.Button(
                self.top_container,
                text=text,
                bg=self.button_color,
                fg="#FFFFFF",
                command=cmd,
                **btn_style,
            ).pack(side="left", padx=4, pady=2)

        # 2. Navigation Dropdown Box
        tk.Label(
            self.top_container,
            text="Navigate:",
            font=("Helvetica", 9, "bold"),
            bg="#FFFFFF",
            fg=self.button_color,
        ).pack(side="left", padx=(10, 2), pady=2)

        # self.PAGES_MAP.keys() now dynamically executes without circular import
        self.nav_dropdown = ttk.Combobox(
            self.top_container,
            values=list(self.PAGES_MAP.keys()),
            state="readonly",
            width=15,
            font=("Helvetica", 9),
        )
        self.nav_dropdown.set("Select Page...")
        self.nav_dropdown.pack(side="left", padx=4, pady=2)

        # Bind combobox selection event
        self.nav_dropdown.bind("<<ComboboxSelected>>", self.on_nav_select)

        # 3. Right Control Buttons
        for text, cmd in [
            ("Clear", lambda: print("Clear")),
            ("Stop", lambda: print("Stop")),
            ("Restart", lambda: print("Restart")),
        ]:
            tk.Button(
                self.top_container,
                text=text,
                bg=self.button_color,
                fg="#FFFFFF",
                command=cmd,
                **btn_style,
            ).pack(side="right", padx=4, pady=2)

    def on_nav_select(self, event):
        """Triggered when the user selects a page from the dropdown."""
        selected_name = self.nav_dropdown.get()
        target_page = self.PAGES_MAP.get(selected_name)

        if target_page:
            self.navigate_to(target_page)

        # Reset dropdown label
        self.nav_dropdown.set("Select Page...")

    def navigate_to(self, page_input):
        """Routes to the requested page class via controller."""
        if self.controller:
            try:
                self.controller.show_frame(page_input)
            except Exception as e:
                print(f"[NAV ERROR]: Failed to route to '{page_input}': {e}")

    def go_home(self):
        # Fetch the actual homePage class object from PAGES_MAP
        home_class = self.PAGES_MAP.get("Home")
        if home_class:
            self.navigate_to(home_class)

    def open_file_selector(self):
        print("[UI EVENT]: Open File Selector")