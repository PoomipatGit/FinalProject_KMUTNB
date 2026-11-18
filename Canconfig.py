import os
import glob
import tkinter as tk
from tkinter import ttk, filedialog
from basePage import BasePage
import Filemanager


class Canconfigpage(BasePage):
    # Matches your purple theme while using OperationPage's responsive grid architecture
    panel_color = "#8056a5"      # Primary card background
    button_color = "#573172"     # Dark purple action buttons
    accent_color = "#a67dc9"     # Lighter purple highlights

    def __init__(self, parent, controller=None):
        super().__init__(parent, controller)
        self.controller = controller
        self.config_file = Filemanager.get_required_path("CAN_config.json")

        # --- 1. Network, Driver & Interface Variables ---
        self.driver_file_var = tk.StringVar(value="canbusprotocal_niuera.py")
        self.interface_var = tk.StringVar(value="can0")
        self.protocol_var = tk.StringVar(value="CANopen")
        self.baudrate_var = tk.StringVar(value="250")
        self.canmsgtype_var = tk.StringVar(value="29-Bit")

        # --- 2. Identifier & Safety Variables ---
        self.supplyid_val = tk.StringVar(value="0x10")
        self.commandid_val = tk.StringVar(value="0x0C200780")
        self.listenerid_val = tk.StringVar(value="0x0C200781")
        self.timeout_val = tk.StringVar(value="300")
        self.timeout_action_var = tk.StringVar(value="off")
        self.retry_count_var = tk.StringVar(value="3")

        # --- 3. Byte-Level Frame Builder Variables ---
        self.tx_frame_type_var = tk.StringVar(value="29-Bit")
        self.tx_id_var = tk.StringVar(value="0x0C200780")
        self.tx_dlc_var = tk.StringVar(value="8")
        self.byte_vars = [tk.StringVar(value="00") for _ in range(8)]
        self.byte_entries = []
        self.frame_preview_var = tk.StringVar(value="ID: 0x0C200780 [EXT] | DLC: 8 | DATA: 00 00 00 00 00 00 00 00")
        self.bus_status_var = tk.StringVar(value="Status: Ready (Not Connected)")

        # --- 4. Build Responsive Grid UI ---
        self.setup_main_containers()
        self.setup_network_panel()       # Row 0, Col 0
        self.setup_identifier_safety()   # Row 0, Col 1
        self.setup_byte_builder_panel()  # Row 1, Col 0..1

        # Load saved settings & wire live preview updates
        self.load_can_settings()
        self._bind_preview_traces()
        self.update_byte_states()
        self.poll_can_status()

    # =========================================================================
    # Responsive Grid Container (Matches OperationPage)
    # =========================================================================

    def setup_main_containers(self):
        self.grid_container = tk.Frame(self, bg="#FFFFFF")
        self.grid_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(2, 6))

        self.grid_container.grid_columnconfigure((0, 1), weight=1, uniform="cfg_cols")
        self.grid_container.grid_rowconfigure(0, weight=3, uniform="cfg_rows")
        self.grid_container.grid_rowconfigure(1, weight=4, uniform="cfg_rows")

    # =========================================================================
    # Top-Left Card (Row 0, Col 0): Network, Driver & Interface Setting
    # =========================================================================

    def _discover_driver_files(self) -> list:
        """Scans the project directory for available CAN driver python files."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        patterns = ["canbusprotocal_*.py", "*driver*.py", "mock_*.py"]
        found = set()
        for pat in patterns:
            for path in glob.glob(os.path.join(base_dir, pat)):
                found.add(os.path.basename(path))

        # Ensure standard driver options appear even before files are created
        defaults = [
            "canbusprotocal_niuera.py",
            "canbusprotocal_phoenix.py",
            "mock_can_library.py",
        ]
        for d in defaults:
            found.add(d)
        return sorted(found)

    def setup_network_panel(self):
        card = tk.Frame(self.grid_container, bg=self.panel_color, bd=1, relief="solid")
        card.grid(row=0, column=0, sticky="nsew", padx=3, pady=3)
        card.grid_columnconfigure(0, weight=0)
        card.grid_columnconfigure(1, weight=1)
        for r in range(6):
            card.grid_rowconfigure(r, weight=1)

        tk.Label(
            card, text="Network & Interface Setting",
            font=("Helvetica", 10, "bold"), bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 2))

        # Row 1: Hardware Driver File Selector
        tk.Label(
            card, text="Driver File :", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=1, column=0, sticky="w", padx=8, pady=2)

        drv_frame = tk.Frame(card, bg=self.panel_color)
        drv_frame.grid(row=1, column=1, sticky="ew", padx=6, pady=2)
        drv_frame.grid_columnconfigure(0, weight=1)

        self.driver_box = ttk.Combobox(
            drv_frame, textvariable=self.driver_file_var,
            values=self._discover_driver_files(),
            font=("Helvetica", 9, "bold")
        )
        self.driver_box.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        self.driver_box.bind("<<ComboboxSelected>>", lambda e: self.on_driver_selected())

        tk.Button(
            drv_frame, text="Browse...", font=("Helvetica", 8, "bold"),
            bg=self.button_color, fg="#FFFFFF", relief="groove", bd=1, padx=6,
            cursor="hand2", command=self.browse_driver_file
        ).grid(row=0, column=1, sticky="e")

        # Row 2: Hardware Interface / Channel
        tk.Label(
            card, text="CAN Channel :", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=2, column=0, sticky="w", padx=8, pady=2)

        iface_box = ttk.Combobox(
            card, textvariable=self.interface_var,
            values=["can0", "can1", "vcan0", "virtual"],
            state="readonly", width=12, font=("Helvetica", 9, "bold")
        )
        iface_box.grid(row=2, column=1, sticky="w", padx=6, pady=2)

        # Row 3: Protocol
        tk.Label(
            card, text="Protocol :", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=3, column=0, sticky="w", padx=8, pady=2)

        proto_frame = tk.Frame(card, bg=self.panel_color)
        proto_frame.grid(row=3, column=1, sticky="w", padx=4)
        for p in ("CANopen", "CAN FD", "J1979"):
            tk.Radiobutton(
                proto_frame, text=p, variable=self.protocol_var, value=p,
                bg=self.panel_color, fg="#FFFFFF", selectcolor=self.button_color,
                activebackground=self.panel_color, activeforeground="#FFFFFF",
                font=("Helvetica", 9, "bold")
            ).pack(side="left", padx=4)

        # Row 4: Baud Rate
        tk.Label(
            card, text="Baud Rate :", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=4, column=0, sticky="w", padx=8, pady=2)

        baud_frame = tk.Frame(card, bg=self.panel_color)
        baud_frame.grid(row=4, column=1, sticky="w", padx=6)
        ttk.Combobox(
            baud_frame, textvariable=self.baudrate_var,
            values=["125", "250", "500", "1000"],
            width=10, font=("Helvetica", 9, "bold")
        ).pack(side="left")
        tk.Label(
            baud_frame, text="kbps", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).pack(side="left", padx=5)

        # Row 5: Default Bus Frame Type
        tk.Label(
            card, text="Default Frame :", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=5, column=0, sticky="w", padx=8, pady=2)

        type_frame = tk.Frame(card, bg=self.panel_color)
        type_frame.grid(row=5, column=1, sticky="w", padx=4)
        for t in ("11-Bit", "29-Bit"):
            tk.Radiobutton(
                type_frame, text=t, variable=self.canmsgtype_var, value=t,
                command=self.sync_default_frame_type,
                bg=self.panel_color, fg="#FFFFFF", selectcolor=self.button_color,
                activebackground=self.panel_color, activeforeground="#FFFFFF",
                font=("Helvetica", 9, "bold")
            ).pack(side="left", padx=6)

    def browse_driver_file(self):
        """Opens file dialog to select an external Python CAN driver module."""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        chosen = filedialog.askopenfilename(
            parent=self,
            initialdir=base_dir,
            title="Select CAN Protocol Driver File",
            filetypes=[("Python Driver (*.py)", "*.py"), ("All Files (*.*)", "*.*")],
        )
        if chosen:
            # Store relative filename if inside project folder, otherwise full path
            rel_path = os.path.relpath(chosen, base_dir)
            display_val = rel_path if not rel_path.startswith("..") else chosen
            self.driver_file_var.set(display_val)

            # Add to dropdown choices if not already listed
            current_vals = list(self.driver_box["values"])
            if display_val not in current_vals:
                self.driver_box["values"] = current_vals + [display_val]

            self.on_driver_selected()

    def on_driver_selected(self):
        """Logs driver switch and notifies controller/worker immediately."""
        drv = self.driver_file_var.get().strip()
        if not drv:
            return
        self.log_terminal(f"[DRIVER]: Selected protocol driver -> {drv}")
        if hasattr(self, "controller") and self.controller:
            if hasattr(self.controller, "shared_data"):
                self.controller.shared_data["active_driver_file"] = drv
            if hasattr(self.controller, "command_queue"):
                self.controller.command_queue.put({
                    "action": "LOAD_DRIVER",
                    "driver_file": drv,
                })

    # =========================================================================
    # Top-Right Card (Row 0, Col 1): Identifier & Watchdog Safety
    # =========================================================================

    def setup_identifier_safety(self):
        card = tk.Frame(self.grid_container, bg=self.panel_color, bd=1, relief="solid")
        card.grid(row=0, column=1, sticky="nsew", padx=3, pady=3)
        card.grid_columnconfigure((0, 1, 2, 3), weight=1)
        for r in range(5):
            card.grid_rowconfigure(r, weight=1)

        tk.Label(
            card, text="Identifier & Watchdog Safety",
            font=("Helvetica", 10, "bold"), bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=0, column=0, columnspan=4, sticky="w", padx=8, pady=(4, 2))

        # Row 1: Supply ID & Command ID
        self._add_id_cell(card, 1, 0, "Supply ID :", self.supplyid_val)
        self._add_id_cell(card, 1, 2, "Command ID :", self.commandid_val)

        # Row 2: Listener ID & Timeout
        self._add_id_cell(card, 2, 0, "Listener ID :", self.listenerid_val)

        tk.Label(
            card, text="Timeout (ms) :", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=2, column=2, sticky="e", padx=4, pady=2)
        tk.Entry(
            card, textvariable=self.timeout_val, width=10,
            font=("Helvetica", 9, "bold"), justify="center"
        ).grid(row=2, column=3, sticky="w", padx=4, pady=2)

        # Row 3: Timeout Action
        act_frame = tk.Frame(card, bg=self.panel_color)
        act_frame.grid(row=3, column=0, columnspan=4, sticky="w", padx=8)

        tk.Radiobutton(
            act_frame, text="Force OFF output",
            variable=self.timeout_action_var, value="off",
            bg=self.panel_color, fg="#FFFFFF", selectcolor=self.button_color,
            activebackground=self.panel_color, activeforeground="#FFFFFF",
            font=("Helvetica", 8, "bold")
        ).pack(side="left", padx=(0, 8))

        tk.Radiobutton(
            act_frame, text="Auto reconnect:",
            variable=self.timeout_action_var, value="reconnect",
            bg=self.panel_color, fg="#FFFFFF", selectcolor=self.button_color,
            activebackground=self.panel_color, activeforeground="#FFFFFF",
            font=("Helvetica", 8, "bold")
        ).pack(side="left")

        tk.Entry(
            act_frame, textvariable=self.retry_count_var, width=3,
            font=("Helvetica", 8, "bold"), justify="center"
        ).pack(side="left", padx=2)
        tk.Label(
            act_frame, text="times", font=("Helvetica", 8, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).pack(side="left")

        # Row 4: Terminal / Interface Action Buttons
        btn_bar = tk.Frame(card, bg=self.panel_color)
        btn_bar.grid(row=4, column=0, columnspan=4, sticky="ew", padx=8, pady=(2, 4))

        tk.Button(
            btn_bar, text="Apply & Bring UP", font=("Helvetica", 8, "bold"),
            bg="#28A745", fg="#FFFFFF", relief="groove", bd=2, padx=8,
            cursor="hand2", command=self.apply_can_config
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_bar, text="Bring DOWN", font=("Helvetica", 8, "bold"),
            bg="#D9534F", fg="#FFFFFF", relief="groove", bd=2, padx=8,
            cursor="hand2", command=self.disconnect_can
        ).pack(side="left", padx=(0, 6))

        tk.Button(
            btn_bar, text="Ping Supply", font=("Helvetica", 8, "bold"),
            bg=self.button_color, fg="#FFFFFF", relief="groove", bd=2, padx=8,
            cursor="hand2", command=self.func_ping
        ).pack(side="right")

    def _add_id_cell(self, parent, row, col, label_text, var):
        tk.Label(
            parent, text=label_text, font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).grid(row=row, column=col, sticky="e", padx=4, pady=2)
        tk.Entry(
            parent, textvariable=var, width=12,
            font=("Helvetica", 9, "bold"), justify="center"
        ).grid(row=row, column=col + 1, sticky="w", padx=4, pady=2)

    # =========================================================================
    # Bottom Card (Row 1, Col 0..1): Per-Byte CAN Frame Builder (11-Bit / 29-Bit)
    # =========================================================================

    def setup_byte_builder_panel(self):
        card = tk.Frame(self.grid_container, bg=self.panel_color, bd=1, relief="solid")
        card.grid(row=1, column=0, columnspan=2, sticky="nsew", padx=3, pady=3)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(3, weight=1)

        # Header Row
        hdr = tk.Frame(card, bg=self.panel_color)
        hdr.grid(row=0, column=0, sticky="ew", padx=8, pady=(4, 2))
        tk.Label(
            hdr, text="Custom CAN Frame Builder (Per-Byte Editor & Terminal Test)",
            font=("Helvetica", 10, "bold"), bg=self.panel_color, fg="#FFFFFF"
        ).pack(side="left")

        tk.Label(
            hdr, textvariable=self.bus_status_var,
            font=("Helvetica", 9, "bold"), bg=self.button_color, fg="#FFCC00",
            padx=8, pady=1
        ).pack(side="right")

        # Row 1: Frame Type (11-Bit / 29-Bit), Arbitration ID, DLC, Quick Presets
        ctrl_row = tk.Frame(card, bg=self.panel_color)
        ctrl_row.grid(row=1, column=0, sticky="ew", padx=8, pady=3)

        tk.Label(
            ctrl_row, text="Frame Format:", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).pack(side="left", padx=(0, 4))

        for mode_label in ("11-Bit", "29-Bit"):
            tk.Radiobutton(
                ctrl_row, text=mode_label, variable=self.tx_frame_type_var, value=mode_label,
                command=self.on_tx_frame_type_change,
                bg=self.panel_color, fg="#FFFFFF", selectcolor=self.button_color,
                activebackground=self.panel_color, activeforeground="#FFFFFF",
                font=("Helvetica", 9, "bold")
            ).pack(side="left", padx=3)

        tk.Label(
            ctrl_row, text="Arbitration ID (Hex):", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).pack(side="left", padx=(14, 4))

        self.ent_tx_id = tk.Entry(
            ctrl_row, textvariable=self.tx_id_var, width=13,
            font=("Consolas", 10, "bold"), justify="center"
        )
        self.ent_tx_id.pack(side="left", padx=2)

        tk.Label(
            ctrl_row, text="DLC (Bytes):", font=("Helvetica", 9, "bold"),
            bg=self.panel_color, fg="#FFFFFF"
        ).pack(side="left", padx=(14, 4))

        dlc_combo = ttk.Combobox(
            ctrl_row, textvariable=self.tx_dlc_var,
            values=[str(i) for i in range(9)], state="readonly",
            width=3, font=("Helvetica", 9, "bold")
        )
        dlc_combo.pack(side="left")
        dlc_combo.bind("<<ComboboxSelected>>", lambda e: self.update_byte_states())

        # Quick Preset Buttons (NIUERA Example)
        tk.Button(
            ctrl_row, text="Preset: Read V/I", font=("Helvetica", 8, "bold"),
            bg=self.button_color, fg="#FFFFFF", relief="groove", bd=1, padx=6,
            command=lambda: self.load_byte_preset("29-Bit", "0x0C200780", ["10", "00", "00", "0F", "00", "00", "00", "00"])
        ).pack(side="right", padx=2)

        tk.Button(
            ctrl_row, text="Clear Bytes", font=("Helvetica", 8, "bold"),
            bg=self.button_color, fg="#FFFFFF", relief="groove", bd=1, padx=6,
            command=lambda: self.load_byte_preset(self.tx_frame_type_var.get(), self.tx_id_var.get(), ["00"] * 8)
        ).pack(side="right", padx=2)

        # Row 2: 8-Byte Grid (Byte 0 .. Byte 7)
        byte_table = tk.Frame(card, bg="#2B193D", bd=1, relief="solid")
        byte_table.grid(row=2, column=0, sticky="ew", padx=8, pady=4)
        for col in range(8):
            byte_table.grid_columnconfigure(col, weight=1, uniform="bytes")

        self.byte_entries.clear()
        for idx in range(8):
            tk.Label(
                byte_table, text=f"Byte {idx}", font=("Helvetica", 8, "bold"),
                bg=self.button_color, fg="#FFFFFF", bd=1, relief="ridge"
            ).grid(row=0, column=idx, sticky="ew", padx=1, pady=(1, 0))

            ent = tk.Entry(
                byte_table, textvariable=self.byte_vars[idx], width=5,
                font=("Consolas", 11, "bold"), justify="center",
                bg="#FFFFFF", fg="#000000"
            )
            ent.grid(row=1, column=idx, sticky="ew", padx=2, pady=3, ipady=2)
            ent.bind("<FocusOut>", lambda e, i=idx: self._normalize_byte(i))
            self.byte_entries.append(ent)

        # Row 3: Live Frame Preview + Send Action + Mini Terminal Log
        bottom_split = tk.Frame(card, bg=self.panel_color)
        bottom_split.grid(row=3, column=0, sticky="nsew", padx=8, pady=(2, 6))
        bottom_split.grid_columnconfigure(0, weight=1)
        bottom_split.grid_rowconfigure(1, weight=1)

        preview_bar = tk.Frame(bottom_split, bg="#1E1E1E", bd=1, relief="solid")
        preview_bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        tk.Label(
            preview_bar, textvariable=self.frame_preview_var,
            font=("Consolas", 9, "bold"), bg="#1E1E1E", fg="#00FF66", anchor="w"
        ).pack(side="left", padx=8, pady=4)

        tk.Button(
            preview_bar, text="▶ SEND CAN FRAME", font=("Helvetica", 9, "bold"),
            bg="#28A745", fg="#FFFFFF", activebackground="#1E7E34",
            relief="groove", bd=2, padx=12, cursor="hand2",
            command=self.send_custom_frame
        ).pack(side="right", padx=4, pady=2)

        # Terminal Output Box
        log_box = tk.Frame(bottom_split, bg="#1E1E1E")
        log_box.grid(row=1, column=0, sticky="nsew")

        self.txt_terminal = tk.Text(
            log_box, height=4, bg="#121212", fg="#DCE2E8",
            font=("Consolas", 9), relief="flat", wrap="word"
        )
        self.txt_terminal.pack(side="left", fill="both", expand=True)

        sb = ttk.Scrollbar(log_box, orient="vertical", command=self.txt_terminal.yview)
        self.txt_terminal.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

    # =========================================================================
    # Byte Validation, Frame Formatting & Preview Logic
    # =========================================================================

    def _bind_preview_traces(self):
        self.tx_frame_type_var.trace_add("write", lambda *_: self.update_frame_preview())
        self.tx_id_var.trace_add("write", lambda *_: self.update_frame_preview())
        self.tx_dlc_var.trace_add("write", lambda *_: self.update_frame_preview())
        for var in self.byte_vars:
            var.trace_add("write", lambda *_: self.update_frame_preview())

    def sync_default_frame_type(self):
        """Syncs the builder's frame type when the global default frame type changes."""
        self.tx_frame_type_var.set(self.canmsgtype_var.get())
        self.on_tx_frame_type_change()

    def on_tx_frame_type_change(self):
        """Clamps or updates example ID when switching between 11-Bit and 29-Bit."""
        is_ext = (self.tx_frame_type_var.get() == "29-Bit")
        raw_id = self.tx_id_var.get().strip()
        try:
            val = int(raw_id, 16)
            if not is_ext and val > 0x7FF:
                self.tx_id_var.set("0x200")
            elif is_ext and val <= 0x7FF:
                self.tx_id_var.set("0x0C200780")
        except ValueError:
            self.tx_id_var.set("0x0C200780" if is_ext else "0x200")
        self.update_frame_preview()

    def update_byte_states(self):
        """Enables/disables Byte 0..7 entries based on selected DLC (0..8)."""
        dlc = int(self.tx_dlc_var.get() or 8)
        for idx, ent in enumerate(self.byte_entries):
            if idx < dlc:
                ent.config(state="normal", bg="#FFFFFF", fg="#000000")
            else:
                ent.config(state="disabled", disabledbackground="#5A4A6A", disabledforeground="#B0A0C0")
        self.update_frame_preview()

    def _normalize_byte(self, idx):
        raw = self.byte_vars[idx].get().strip().replace("0x", "").replace("0X", "")
        try:
            val = int(raw, 16) & 0xFF
            self.byte_vars[idx].set(f"{val:02X}")
        except ValueError:
            self.byte_vars[idx].set("00")

    def load_byte_preset(self, frame_type: str, arb_id: str, byte_list: list):
        self.tx_frame_type_var.set(frame_type)
        self.tx_id_var.set(arb_id)
        self.tx_dlc_var.set(str(len(byte_list)))
        for i in range(8):
            self.byte_vars[i].set(byte_list[i] if i < len(byte_list) else "00")
        self.update_byte_states()

    def parse_frame_payload(self):
        """Validates ID (11-bit max 0x7FF, 29-bit max 0x1FFFFFFF) and extracts active bytes."""
        is_extended = (self.tx_frame_type_var.get() == "29-Bit")
        max_id = 0x1FFFFFFF if is_extended else 0x7FF

        arb_id = int(self.tx_id_var.get().strip(), 16)
        if not (0 <= arb_id <= max_id):
            raise ValueError(f"ID 0x{arb_id:X} exceeds {'29-bit (0x1FFFFFFF)' if is_extended else '11-bit (0x7FF)'} limit.")

        dlc = int(self.tx_dlc_var.get())
        data_bytes = []
        for i in range(dlc):
            b_str = self.byte_vars[i].get().strip().replace("0x", "")
            b_val = int(b_str or "0", 16)
            if not (0 <= b_val <= 0xFF):
                raise ValueError(f"Byte {i} ('{b_str}') must be between 00 and FF.")
            data_bytes.append(b_val)

        return is_extended, arb_id, data_bytes

    def update_frame_preview(self):
        try:
            is_ext, arb_id, data_bytes = self.parse_frame_payload()
            fmt_tag = "29-Bit EXT" if is_ext else "11-Bit STD"
            id_fmt = f"0x{arb_id:08X}" if is_ext else f"0x{arb_id:03X}"
            hex_str = " ".join(f"{b:02X}" for b in data_bytes) or "(No Data)"
            self.frame_preview_var.set(f"ID: {id_fmt} [{fmt_tag}] | DLC: {len(data_bytes)} | DATA: {hex_str}")
        except ValueError as err:
            self.frame_preview_var.set(f"[INVALID FRAME]: {err}")

    def log_terminal(self, msg: str):
        self.txt_terminal.insert(tk.END, f"{msg}\n")
        self.txt_terminal.see(tk.END)

    # =========================================================================
    # Backend Worker & Config Persistence Wiring
    # =========================================================================

    def get_config_data(self) -> dict:
        return {
            "driver_file": self.driver_file_var.get().strip(),
            "interface": self.interface_var.get(),
            "protocol": self.protocol_var.get(),
            "baudrate_kbps": int(self.baudrate_var.get() or 250),
            "can_msg_type": self.canmsgtype_var.get(),
            "supply_id": self.supplyid_val.get().strip(),
            "command_id": self.commandid_val.get().strip(),
            "listener_id": self.listenerid_val.get().strip(),
            "timeout_ms": int(self.timeout_val.get() or 300),
            "timeout_action": self.timeout_action_var.get(),
            "reconnect_retries": int(self.retry_count_var.get() or 3),
        }

    def load_can_settings(self):
        data = Filemanager.load_json(self.config_file)
        if data:
            saved_drv = data.get("driver_file", "canbusprotocal_niuera.py")
            self.driver_file_var.set(saved_drv)
            if saved_drv and saved_drv not in self.driver_box["values"]:
                self.driver_box["values"] = list(self.driver_box["values"]) + [saved_drv]

            self.interface_var.set(data.get("interface", "can0"))
            self.protocol_var.set(data.get("protocol", "CANopen"))
            self.baudrate_var.set(str(data.get("baudrate_kbps", 250)))
            self.canmsgtype_var.set(data.get("can_msg_type", "29-Bit"))
            self.tx_frame_type_var.set(self.canmsgtype_var.get())
            self.supplyid_val.set(data.get("supply_id", "0x10"))
            self.commandid_val.set(data.get("command_id", "0x0C200780"))
            self.listenerid_val.set(data.get("listener_id", "0x0C200781"))
            self.timeout_val.set(str(data.get("timeout_ms", 300)))
            self.timeout_action_var.set(data.get("timeout_action", "off"))
            self.retry_count_var.set(str(data.get("reconnect_retries", 3)))

    def apply_can_config(self):
        try:
            cfg = self.get_config_data()
            Filemanager.save_json(self.config_file, cfg)
            self.bus_status_var.set(f"Status: {cfg['interface']} @ {cfg['baudrate_kbps']} kbps ({os.path.basename(cfg['driver_file'])})")
            self.log_terminal(
                f"[CONFIG]: Saved & applying driver '{cfg['driver_file']}' on "
                f"{cfg['interface']} ({cfg['baudrate_kbps']} kbps, {cfg['can_msg_type']})"
            )

            if hasattr(self, "controller") and self.controller:
                self.controller.shared_data["can_config"] = cfg
                self.controller.shared_data["active_driver_file"] = cfg["driver_file"]
                if hasattr(self.controller, "command_queue"):
                    self.controller.command_queue.put({"action": "REINIT_CAN", "config": cfg})
        except ValueError as e:
            self.log_terminal(f"[ERROR]: Invalid config input -> {e}")

    def disconnect_can(self):
        iface = self.interface_var.get()
        self.bus_status_var.set(f"Status: {iface} DOWN")
        self.log_terminal(f"[CONFIG]: Bringing interface {iface} DOWN.")
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "command_queue"):
            self.controller.command_queue.put({"action": "DISCONNECT_CAN", "interface": iface})

    def func_ping(self):
        target = self.supplyid_val.get().strip()
        is_ext = (self.canmsgtype_var.get() == "29-Bit")
        self.log_terminal(f"[PING]: Pinging Supply ID {target} ({'29-Bit' if is_ext else '11-Bit'})...")
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "command_queue"):
            self.controller.command_queue.put({
                "action": "CAN_PING",
                "target_id": target,
                "is_extended": is_ext,
            })

    def send_custom_frame(self):
        try:
            is_ext, arb_id, data_bytes = self.parse_frame_payload()
            id_fmt = f"0x{arb_id:08X}" if is_ext else f"0x{arb_id:03X}"
            hex_str = " ".join(f"{b:02X}" for b in data_bytes)
            self.log_terminal(f"[TX {'EXT' if is_ext else 'STD'}]: ID={id_fmt} DLC={len(data_bytes)} DATA=[{hex_str}]")

            if hasattr(self, "controller") and self.controller and hasattr(self.controller, "command_queue"):
                self.controller.command_queue.put({
                    "action": "CAN_CUSTOM_FRAME",
                    "arbitration_id": arb_id,
                    "is_extended": is_ext,
                    "data": data_bytes,
                })
        except ValueError as e:
            self.log_terminal(f"[TX ERROR]: {e}")

    def poll_can_status(self):
        """Polls worker feedback from shared_data if available."""
        if hasattr(self, "controller") and self.controller and hasattr(self.controller, "shared_data"):
            status_msg = self.controller.shared_data.pop("can_config_feedback", None)
            if status_msg:
                self.log_terminal(f"[RX/BUS]: {status_msg}")
        self.after(300, self.poll_can_status)