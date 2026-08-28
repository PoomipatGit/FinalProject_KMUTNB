import tkinter as tk
from tkinter import ttk, filedialog, messagebox


class BasePage(tk.Frame):
    button_color = "#573172"
    label_color = "#8056a5"

    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#ffffff")
        self.controller = controller

        # Grid configuration for the entire page frame
        self.grid_rowconfigure(0, weight=0)  # Row 0: Top bar (Fixed height)
        self.grid_rowconfigure(1, weight=1)  # Row 1: Main content area (Expands)
        self.grid_columnconfigure(0, weight=1)

        # 1. Top Status Bar Container placed at Row 0
        self.top_container = tk.Frame(self, bg="#FFFFFF")
        self.top_container.grid(row=0, column=0, sticky="ew", padx=0, pady=(0, 2))
        
        self.setup_status_bar()

    @property
    def PAGES_MAP(self):
        """Lazy-loads page classes when accessed to prevent circular import loops."""
        from batterytest import BatteryTestpage
        from canMessageSetup import canMessageSetup
        from homePage import homePage
        from loadPage import loadPage
        from sourcePage import sourcePage
        from canMessageCommand import canMessageCommand
        from canSequencePage import canSequencePage


        return {
            "Home": homePage,
            "Source": sourcePage,
            "Load": loadPage,
            "Battery Test": BatteryTestpage,
            "saved Command": canMessageCommand,
            "Sequence Config": canSequencePage,
  
        }

    def _get_page_display_name(self):
        cls_name = self.__class__.__name__
        name_lookup = {
            "homePage": "HOME",
            "sourcePage": "SOURCE",
            "loadPage": "LOAD",
            "BatteryTestpage": "BATTERY TEST",
            "canMessageCommand": "SAVED COMMAND",
            "canSequencePage": "SEQUENCE CONFIG"
        }
        return name_lookup.get(cls_name, cls_name.upper())

    def setup_status_bar(self):
        btn_style = {
            "font": ("Helvetica", 9, "bold"),
            "relief": "groove",
            "bd": 2,
            "padx": 10,
            "pady": 1,
            "activebackground": self.button_color,
        }

        # Divide top_container using 3 balanced sections (Left, Center, Right)
        self.top_container.grid_columnconfigure(0, weight=0)  # Left Nav
        self.top_container.grid_columnconfigure(1, weight=1)  # Center Title
        self.top_container.grid_columnconfigure(2, weight=0)  # Right Controls

        # --- Section 1: Left Navigation ---
        left_box = tk.Frame(self.top_container, bg="#FFFFFF")
        left_box.grid(row=0, column=0, sticky="w", padx=4, pady=2)

        for text, cmd in [
            ("Back", self.handle_back),
            ("Home", self.go_home),
            ("File", self.open_file_selector),
        ]:
            tk.Button(
                left_box, text=text, bg=self.button_color, fg="#FFFFFF",
                command=cmd, **btn_style
            ).pack(side="left", padx=2)

        tk.Label(
            left_box, text="Navigate:", font=("Helvetica", 9, "bold"),
            bg="#FFFFFF", fg=self.button_color
        ).pack(side="left", padx=(6, 2))

        self.nav_dropdown = ttk.Combobox(
            left_box, values=list(self.PAGES_MAP.keys()),
            state="readonly", width=12, font=("Helvetica", 9)
        )
        self.nav_dropdown.set("Select Page...")
        self.nav_dropdown.pack(side="left", padx=2)
        self.nav_dropdown.bind("<<ComboboxSelected>>", self.on_nav_select)

        # --- Section 2: Center Active Page Title ---
        page_name = self._get_page_display_name()
        self.current_page_lbl = tk.Label(
            self.top_container,
            text=f"• {page_name} •",
            font=("Helvetica", 11, "bold"),
            bg="#FFFFFF",
            fg=self.button_color
        )
        self.current_page_lbl.grid(row=0, column=1, sticky="nsew", padx=10)

        # --- Section 3: Right Control Buttons ---
        right_box = tk.Frame(self.top_container, bg="#FFFFFF")
        right_box.grid(row=0, column=2, sticky="e", padx=4, pady=2)

        for text, cmd in [
            ("Restart", lambda: print("Restart")),
            ("Stop", lambda: print("Stop")),
            ("Clear", lambda: print("Clear")),
        ]:
            tk.Button(
                right_box, text=text, bg=self.button_color, fg="#FFFFFF",
                command=cmd, **btn_style
            ).pack(side="left", padx=2)

    def handle_back(self):
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "go_back"):
            self.controller.go_back()

    def on_nav_select(self, event):
        selected_name = self.nav_dropdown.get()
        target_page = self.PAGES_MAP.get(selected_name)
        if target_page:
            self.navigate_to(target_page)
        self.nav_dropdown.set("Select Page...")

    def navigate_to(self, page_input):
        if self.controller:
            try:
                self.controller.show_frame(page_input)
            except Exception as e:
                print(f"[NAV ERROR]: Failed to route to '{page_input}': {e}")

    def go_home(self):
        home_class = self.PAGES_MAP.get("Home")
        if home_class:
            self.navigate_to(home_class)

    def open_file_selector(self):
        print("[UI EVENT]: Open File Selector")