import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import json
import pandas as pd


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

        # Back & Home Buttons
        tk.Button(
            left_box, text="Back", bg=self.button_color, fg="#FFFFFF",
            command=self.handle_back, **btn_style
        ).pack(side="left", padx=2)

        tk.Button(
            left_box, text="Home", bg=self.button_color, fg="#FFFFFF",
            command=self.go_home, **btn_style
        ).pack(side="left", padx=2)

        # Dynamic File Menubutton
        self.file_btn = tk.Menubutton(
            left_box,
            text="File ▾",
            bg=self.button_color,
            fg="#FFFFFF",
            font=("Helvetica", 9, "bold"),
            relief="groove",
            bd=2,
            padx=10,
            pady=1,
            activebackground=self.button_color,
            activeforeground="#FFFFFF"
        )
        self.file_btn.pack(side="left", padx=2)

        self.file_menu = tk.Menu(self.file_btn, tearoff=0, font=("Helvetica", 9))
        self.file_btn["menu"] = self.file_menu

        # Re-populate dropdown items based on active page right before opening
        self.file_btn.bind("<Button-1>", lambda e: self.rebuild_file_menu())

        # Navigation Combobox
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

    # -------------------------------------------------------------------------
    # Context-Aware File Menu Generation
    # -------------------------------------------------------------------------

    def rebuild_file_menu(self):
        """Builds page-specific options inside the File dropdown."""
        self.file_menu.delete(0, tk.END)
        cls_name = self.__class__.__name__

        if cls_name == "canMessageCommand":
            # Saved Command Page
            self.file_menu.add_command(label="Open Command List...", command=self.open_command_list)
            self.file_menu.add_command(label="Save Command List...", command=self.save_command_list)

        elif cls_name == "canSequencePage":
            # Sequence Config Page
            self.file_menu.add_command(label="Open Sequence...", command=self.open_sequence_file)
            self.file_menu.add_command(label="Save Sequence...", command=self.save_sequence_file)

        else:
            # General Pages (Home, Source, Load, Battery Test, etc.)
            self.file_menu.add_command(label="Open Config...", command=self.open_config_file)
            self.file_menu.add_command(label="Save Config...", command=self.save_config_file)

    # -------------------------------------------------------------------------
    # 1. Config Actions (General Pages)
    # -------------------------------------------------------------------------

    def open_config_file(self):
        """Loads configuration JSON."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Open Configuration",
            filetypes=[("JSON Files (*.json)", "*.json"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        print(f"[CONFIG]: Opening -> {file_path}")
        if hasattr(self, "load_config_data"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    config = json.load(f)
                self.load_config_data(config)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load config: {e}")
        else:
            messagebox.showinfo("Open Config", f"Opened: {file_path}\n(Placeholder handler)")

    def save_config_file(self):
        """Saves configuration to JSON."""
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Configuration",
            defaultextension=".json",
            filetypes=[("JSON Files (*.json)", "*.json"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        print(f"[CONFIG]: Saving to -> {file_path}")
        if hasattr(self, "get_config_data"):
            try:
                data = self.get_config_data()
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Saved", f"Configuration saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to write config: {e}")
        else:
            messagebox.showinfo("Save Config", f"Saved: {file_path}\n(Placeholder handler)")

    # -------------------------------------------------------------------------
    # 2. Command List Actions (canMessageCommand)
    # -------------------------------------------------------------------------

    def open_command_list(self):
        """Loads a CSV file into the active page DataFrame."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Open Command List (.csv)",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        try:
            df = pd.read_csv(file_path)
            if hasattr(self, "load_dataframe"):
                self.load_dataframe(df)
            elif hasattr(self, "load_command_csv"):
                self.load_command_csv(file_path)
            messagebox.showinfo("Loaded", f"Command list loaded successfully from:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load command list: {e}")

    def save_command_list(self):
        """Saves registered commands from DataFrame/Tree to a CSV file."""
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Command List (.csv)",
            defaultextension=".csv",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        try:
            df = None
            # Option A: Get DataFrame via page hook
            if hasattr(self, "get_dataframe"):
                df = self.get_dataframe()

            # Option B: Fallback to reading active Treeview rows
            elif hasattr(self, "tree"):
                rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]
                headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                if rows:
                    df = pd.DataFrame(rows, columns=headers)

            if df is None or df.empty:
                messagebox.showwarning("Warning", "No commands in table to save.")
                return

            # Save DataFrame to CSV
            df.to_csv(file_path, index=False)
            messagebox.showinfo("Saved", f"Command list saved successfully to:\n{file_path}")

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save CSV: {e}")

    # -------------------------------------------------------------------------
    # 3. Sequence Actions (canSequencePage)
    # -------------------------------------------------------------------------

    def open_sequence_file(self):
        """Loads CSV sequence into Treeview table."""
        file_path = filedialog.askopenfilename(
            parent=self,
            title="Open Sequence Table",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        if hasattr(self, "load_sequence_csv"):
            self.load_sequence_csv(file_path)
        elif hasattr(self, "tree"):
            try:
                with open(file_path, mode="r", encoding="utf-8") as f:
                    reader = csv.reader(f)
                    _ = next(reader, None)  # Skip header
                    self.tree.delete(*self.tree.get_children())
                    for row in reader:
                        if row:
                            self.tree.insert("", tk.END, values=row)
                messagebox.showinfo("Loaded", f"Sequence loaded from:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load sequence: {e}")

    def save_sequence_file(self):
        """Exports active Treeview sequence table to CSV."""
        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Save Active Sequence Table",
            defaultextension=".csv",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if not file_path:
            return

        if hasattr(self, "tree"):
            try:
                headers = [self.tree.heading(col)["text"] for col in self.tree["columns"]]
                rows = [self.tree.item(item)["values"] for item in self.tree.get_children()]

                with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    writer.writerows(rows)
                messagebox.showinfo("Saved", f"Sequence saved to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save sequence: {e}")

    # -------------------------------------------------------------------------
    # Navigation Handlers
    # -------------------------------------------------------------------------

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