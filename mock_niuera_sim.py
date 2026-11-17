import time
import threading
import can


class MockNiueraModule:
    """
    Full NIUERA XEV22KHGEU-FAC Bidirectional Module Simulator (Protocol V1.3).
    Handles all 0x03 write commands, 0x10 read queries, state interlocks,
    hardware protection limits, and 0xF0 (OK) / 0xF2 (Fail) replies.
    """
    def __init__(self, channel="test", res_id=0x061F8000):
        self.bus = can.interface.Bus(interface="virtual", channel=channel)
        self.res_id = res_id
        self.running = False

        # --- Module Configuration & Identity Registers ---
        self.group_num = 0                  # 0x001E (0..7)
        self.addr_alloc_method = 0x00010000 # 0x001F (0=Auto, 0x00010000=DIP/Dial default)
        self.module_addr = 0x00             # 0x0043
        self.altitude_m = 1000              # 0x0017 / 0x004A (1000..5000 m)
        self.sw_version = 130               # 0x0056 (V1.30)
        self.rated_power_mw = 22000000      # 0x0011 (22 kW in 0.001 W)

        # --- Operating State Registers ---
        self.power_on = False               # 0x0030 (False=Shutdown, True=Startup)
        self.work_mode = 0x00000000         # 0x002F (0=Grid, 0x10000=Off-grid, 0x20000=Rectifier)
        self.grid_pwr_ctrl_ac = 0           # 0x0080 high (0=DC side ctrl, 1=AC side ctrl)
        self.reactive_type = 0x00A00000     # 0x0083 (0xA0=None, 0xA1=PF, 0xA2=Var)
        self.phase_err_allowed = 0x00010000 # 0x0085 (default allowed in V1.2+)
        self.island_detect_dis = 0x00000000 # 0x0086 (default enabled)

        # --- Setpoint Registers ---
        self.v_dc_set_mv = 400000           # 0x0077 (mV)
        self.i_dc_set_ma = 0                # 0x0079 (mA, + charge, - discharge)
        self.p_ac_set_w = 0                 # 0x0080 low (W)
        self.q_ac_set_var = 0               # 0x0081 (Var)
        self.pf_set_milli = 1000            # 0x0082 (0.001 units)
        self.rated_vac_01v = 3800           # 0x0084 high (380.0 V)
        self.rated_freq_mhz = 50000         # 0x0084 low (50.000 Hz)

        # --- Protection Threshold Registers ---
        self.dc_uv_prot_01v = 1450          # 0x0087 (145.0 V)
        self.dc_ov_prot_01v = 10300         # 0x0088 (1030.0 V)
        self.ac_uv_prot = (2600, 100)       # 0x0089 (260.0 V, 1.00 s)
        self.ac_ov_prot = (5300, 100)       # 0x008A (530.0 V, 1.00 s)
        self.ac_uf1_prot = (4500, 100)      # 0x008B (45.00 Hz, 1.00 s)
        self.ac_of1_prot = (6500, 100)      # 0x008C (65.00 Hz, 1.00 s)
        self.ac_uf2_prot = (4500, 20)       # 0x008D (45.00 Hz, 0.20 s)
        self.ac_of2_prot = (6500, 20)       # 0x008E (65.00 Hz, 0.20 s)

        # --- Live Simulated Physical Measurements ---
        self.v_dc_actual = 0.0
        self.i_dc_actual = 0.0
        self.v_ac_phase_a = 220.0
        self.v_ac_phase_b = 220.0
        self.v_ac_phase_c = 220.0
        self.freq_hz = 50.000
        self.temp_c = 28.5
        self.alarm_bits = 0x00000000        # 0x0040 (Table 2 bitmask)

    def start(self):
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()

    def stop(self):
        self.running = False
        self.bus.shutdown()

    def _update_physics_and_alarms(self):
        """Simulates DC/AC electrical behavior and checks spec protection thresholds."""
        if not self.power_on:
            self.v_dc_actual += (0.0 - self.v_dc_actual) * 0.35
            self.i_dc_actual += (0.0 - self.i_dc_actual) * 0.35
        else:
            target_v = self.v_dc_set_mv / 1000.0
            # Enforce current sign per manual: Rectifier (+), Grid/Off-grid (-)
            if self.work_mode == 0x00020000:
                target_i = abs(self.i_dc_set_ma) / 1000.0
            else:
                target_i = -abs(self.i_dc_set_ma) / 1000.0

            self.v_dc_actual += (target_v - self.v_dc_actual) * 0.35
            self.i_dc_actual += (target_i - self.i_dc_actual) * 0.35

        # Update Table 2 Status Bits (0x0040)
        bits = 0
        # Bits 12-13: Module working mode (0: Grid, 1: Off-grid, 2: Rectifier)
        mode_code = (self.work_mode >> 16) & 0x03
        bits |= (mode_code << 12)
        # Bits 21 & 22: U1/U2 power status (0 = power on, 1 = power off)
        if not self.power_on:
            bits |= (1 << 21) | (1 << 22)
        # Bit 9: DC Overvoltage (> 1030V or configured limit)
        if self.v_dc_actual * 10 > self.dc_ov_prot_01v:
            bits |= (1 << 9) | (1 << 0)
            self.power_on = False
        # Bit 30: Overtemperature (> 75 C)
        if self.temp_c > 75.0:
            bits |= (1 << 30) | (1 << 1)
            self.power_on = False
        self.alarm_bits = bits

    def _send_reply(self, err_code: int, reg: int, val_bytes: list):
        """Builds standard NIUERA reply: [0x42, err_code, RegH, RegL, B4, B5, B6, B7]."""
        payload = [0x42, err_code, (reg >> 8) & 0xFF, reg & 0xFF] + list(val_bytes[:4])
        self.bus.send(can.Message(arbitration_id=self.res_id, data=payload, is_extended_id=True))

    def _loop(self):
        while self.running:
            self._update_physics_and_alarms()

            msg = self.bus.recv(timeout=0.01)
            if not msg or len(msg.data) < 8:
                continue

            data = list(msg.data)
            func = data[0]
            reg = (data[2] << 8) | data[3]
            val_bytes = data[4:8]

            if func == 0x03:
                self._handle_write(reg, val_bytes)
            elif func == 0x10:
                self._handle_read(reg)

    # -------------------------------------------------------------------------
    # Function 0x03: All Write Commands (with Protocol Interlock Checks)
    # -------------------------------------------------------------------------
    def _handle_write(self, reg: int, val_bytes: list):
        val_u32 = int.from_bytes(bytes(val_bytes), "big", signed=False)
        val_s32 = int.from_bytes(bytes(val_bytes), "big", signed=True)
        val_high = int.from_bytes(bytes(val_bytes[0:2]), "big", signed=False)
        val_low = int.from_bytes(bytes(val_bytes[2:4]), "big", signed=True)

        match reg:
            case 0x0017:  # Operating altitude (1000..5000 m)
                if 1000 <= val_u32 <= 5000:
                    self.altitude_m = val_u32
                    self._send_reply(0xF0, reg, val_bytes)
                else:
                    self._send_reply(0xF2, reg, val_bytes)

            case 0x001E:  # Set Group Number (valid ONLY if addr_alloc_method == DIP/0x00010000)
                if self.addr_alloc_method == 0x00010000:
                    self.group_num = val_bytes[3] & 0x07
                    self._send_reply(0xF0, reg, val_bytes)
                else:
                    # Protocol Section 5: Fails (0xF2) if in Automatic allocation mode
                    self._send_reply(0xF2, reg, val_bytes)

            case 0x001F:  # Address allocation method (0=Auto, 0x00010000=Dial/DIP)
                if val_u32 in (0x00000000, 0x00010000):
                    self.addr_alloc_method = val_u32
                    self._send_reply(0xF0, reg, val_bytes)
                else:
                    self._send_reply(0xF2, reg, val_bytes)

            case 0x0024 | 0x0025 | 0x0031 | 0x0042 | 0x0044:  # Fault & UV/OV/SC Resets
                if val_u32 == 0x00010000:
                    self.alarm_bits = 0x00000000
                self._send_reply(0xF0, reg, val_bytes)

            case 0x002F:  # Working mode (Protocol Sec 7: ONLY allowed when powered OFF)
                if self.power_on or val_u32 not in (0x00000000, 0x00010000, 0x00020000):
                    self._send_reply(0xF2, reg, val_bytes)
                else:
                    self.work_mode = val_u32
                    self._send_reply(0xF0, reg, val_bytes)

            case 0x0030:  # Power ON (0x00000000) / Shutdown (0x00010000)
                if val_u32 == 0x00000000:
                    self.power_on = True
                    self._send_reply(0xF0, reg, val_bytes)
                elif val_u32 == 0x00010000:
                    self.power_on = False
                    self._send_reply(0xF0, reg, val_bytes)
                else:
                    self._send_reply(0xF2, reg, val_bytes)

            case 0x0077:  # Set DC link voltage (mV)
                self.v_dc_set_mv = val_u32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0079:  # Set DC current (mA)
                self.i_dc_set_ma = val_s32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0080:  # Grid power control mode & AC active power (Protocol Sec 8: Shutdown required)
                if self.power_on:
                    self._send_reply(0xF2, reg, val_bytes)
                else:
                    self.grid_pwr_ctrl_ac = val_high
                    self.p_ac_set_w = val_low
                    self._send_reply(0xF0, reg, val_bytes)

            case 0x0081:  # Total reactive power on AC side (Var)
                self.q_ac_set_var = val_s32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0082:  # AC side power factor PF (0.001)
                self.pf_set_milli = val_s32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0083:  # Reactive power control type (0xA0, 0xA1, 0xA2)
                if val_u32 in (0x00A00000, 0x00A10000, 0x00A20000):
                    self.reactive_type = val_u32
                    self._send_reply(0xF0, reg, val_bytes)
                else:
                    self._send_reply(0xF2, reg, val_bytes)

            case 0x0084:  # Rated AC phase voltage (0.1V) & frequency (mHz)
                self.rated_vac_01v = val_high
                self.rated_freq_mhz = int.from_bytes(bytes(val_bytes[2:4]), "big", signed=False)
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0085:  # Phase mismatch allowed
                self.phase_err_allowed = val_u32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0086:  # Island detection function
                self.island_detect_dis = val_u32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0087:  # DC undervoltage protection (0.1V)
                self.dc_uv_prot_01v = val_u32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0088:  # DC overvoltage protection (0.1V)
                self.dc_ov_prot_01v = val_u32
                self._send_reply(0xF0, reg, val_bytes)

            case 0x0089:  # AC UV protection (0.1V, 0.01s)
                self.ac_uv_prot = (val_high, int.from_bytes(bytes(val_bytes[2:4]), "big"))
                self._send_reply(0xF0, reg, val_bytes)

            case 0x008A:  # AC OV protection (0.1V, 0.01s)
                self.ac_ov_prot = (val_high, int.from_bytes(bytes(val_bytes[2:4]), "big"))
                self._send_reply(0xF0, reg, val_bytes)

            case 0x008B:  # First-level AC UF protection
                self.ac_uf1_prot = (val_high, int.from_bytes(bytes(val_bytes[2:4]), "big"))
                self._send_reply(0xF0, reg, val_bytes)

            case 0x008C:  # First-level AC OF protection
                self.ac_of1_prot = (val_high, int.from_bytes(bytes(val_bytes[2:4]), "big"))
                self._send_reply(0xF0, reg, val_bytes)

            case 0x008D:  # Secondary AC UF protection
                self.ac_uf2_prot = (val_high, int.from_bytes(bytes(val_bytes[2:4]), "big"))
                self._send_reply(0xF0, reg, val_bytes)

            case 0x008E:  # Secondary AC OF protection
                self.ac_of2_prot = (val_high, int.from_bytes(bytes(val_bytes[2:4]), "big"))
                self._send_reply(0xF0, reg, val_bytes)

            case _:       # Unknown write register -> Reply Fault 0xF2
                self._send_reply(0xF2, reg, val_bytes)

    # -------------------------------------------------------------------------
    # Function 0x10: All Read Telemetry & Status Queries
    # -------------------------------------------------------------------------
    def _pack_u16_s16(self, high_u16: int, low_s16: int) -> list:
        return list(int(high_u16).to_bytes(2, "big", signed=False)) + list(int(low_s16).to_bytes(2, "big", signed=True))

    def _pack_i32(self, val: int, signed: bool = True) -> list:
        return list(int(val).to_bytes(4, "big", signed=signed))

    def _handle_read(self, reg: int):
        p_dc_total = self.v_dc_actual * self.i_dc_actual
        # Distribute simulated AC phase current & power equally across 3 phases
        i_ac_phase = (abs(p_dc_total) / (3.0 * 220.0)) if self.power_on else 0.0
        if self.work_mode != 0x00020000:
            i_ac_phase = -i_ac_phase
        p_phase_w = int(p_dc_total / 3.0)

        match reg:
            case 0x0001:  # AC Phase A V (0.1V) & I (0.01A)
                self._send_reply(0xF0, reg, self._pack_u16_s16(int(self.v_ac_phase_a * 10), int(i_ac_phase * 100)))
            case 0x0002:  # AC Phase B V (0.1V) & I (0.01A)
                self._send_reply(0xF0, reg, self._pack_u16_s16(int(self.v_ac_phase_b * 10), int(i_ac_phase * 100)))
            case 0x0003:  # AC Phase C V (0.1V) & I (0.01A)
                self._send_reply(0xF0, reg, self._pack_u16_s16(int(self.v_ac_phase_c * 10), int(i_ac_phase * 100)))
            case 0x0004:  # AC AB Line Voltage (0.1V -> 220 * sqrt(3) = 381.0V)
                self._send_reply(0xF0, reg, self._pack_i32(int(self.v_ac_phase_a * 1.732 * 10), signed=False))
            case 0x0005:  # AC BC Line Voltage (0.1V)
                self._send_reply(0xF0, reg, self._pack_i32(int(self.v_ac_phase_b * 1.732 * 10), signed=False))
            case 0x0006:  # AC CA Line Voltage (0.1V)
                self._send_reply(0xF0, reg, self._pack_i32(int(self.v_ac_phase_c * 1.732 * 10), signed=False))
            case 0x0007:  # Phase A Active (W) & Reactive Power (Var)
                self._send_reply(0xF0, reg, list(p_phase_w.to_bytes(2, "big", signed=True)) + [0x00, 0x00])
            case 0x0008:  # Phase B Active (W) & Reactive Power (Var)
                self._send_reply(0xF0, reg, list(p_phase_w.to_bytes(2, "big", signed=True)) + [0x00, 0x00])
            case 0x0009:  # Phase C Active (W) & Reactive Power (Var)
                self._send_reply(0xF0, reg, list(p_phase_w.to_bytes(2, "big", signed=True)) + [0x00, 0x00])
            case 0x000A:  # AC Frequency (mHz)
                self._send_reply(0xF0, reg, self._pack_i32(int(self.freq_hz * 1000), signed=False))
            case 0x000B:  # Ambient / Panel Temp (0.001 C)
                self._send_reply(0xF0, reg, self._pack_i32(int(self.temp_c * 1000), signed=True))
            case 0x000C:  # Total Active Power (W)
                self._send_reply(0xF0, reg, self._pack_i32(int(p_dc_total), signed=True))
            case 0x000D:  # Total Reactive Power (Var)
                self._send_reply(0xF0, reg, self._pack_i32(self.q_ac_set_var if self.power_on else 0, signed=True))
            case 0x000E:  # Total Apparent Power (VA)
                self._send_reply(0xF0, reg, self._pack_i32(int(abs(p_dc_total)), signed=False))
            case 0x000F:  # DC Side Voltage (0.1V) & Current (0.01A)
                self._send_reply(0xF0, reg, self._pack_u16_s16(int(self.v_dc_actual * 10), int(self.i_dc_actual * 100)))
            case 0x0011:  # Rated Output Power (0.001 W)
                self._send_reply(0xF0, reg, self._pack_i32(self.rated_power_mw, signed=False))
            case 0x0040:  # Module Alarm / Status 32-bit Bitmask
                self._send_reply(0xF0, reg, self._pack_i32(self.alarm_bits, signed=False))
            case 0x0043:  # Module Group Number (B4-B5) & Address (B6-B7)
                self._send_reply(0xF0, reg, list(self.group_num.to_bytes(2, "big")) + list(self.module_addr.to_bytes(2, "big")))
            case 0x004A:  # Current Altitude Setting (m)
                self._send_reply(0xF0, reg, self._pack_i32(self.altitude_m, signed=False))
            case 0x0056:  # Software Version Number (lower 16 bits)
                self._send_reply(0xF0, reg, [0x00, 0x00] + list(self.sw_version.to_bytes(2, "big")))
            case _:       # Unknown read register -> Reply Fault 0xF2
                self._send_reply(0xF2, reg, [0x00, 0x00, 0x00, 0x00])


class CanbusProtocol:
    """
    Drop-in PC simulator matching canbusprotocal_niuera.CanbusProtocol.
    When deploying to Raspberry Pi, simply swap the import to the real driver.
    """
    ALARM_DESCRIPTIONS = {
        0: "Module failure (Red LED)",
        1: "Module protection (Yellow LED)",
        2: "AC input phase loss",
        3: "Module internal SCI comm failure",
        4: "AC side wiring wrong phase",
        5: "Islanding alarm",
        6: "Internal busbar OV/UV",
        7: "AC side undervoltage",
        8: "AC side overvoltage",
        9: "DC side overvoltage",
        10: "DC side undervoltage",
        11: "Phase lock error",
        14: "U1 Overcurrent protection",
        15: "Fan failure",
        16: "CAN communication failure",
        17: "Unbalanced current between modules",
        18: "Duplicate address",
        19: "N line connected incorrectly",
        20: "Discharge failure",
        23: "Module power limit",
        24: "Temperature limit power",
        25: "AC power limit",
        26: "AC side underfrequency",
        27: "AC side overfrequency",
        28: "DC side short circuit",
        29: "Air duct overheating",
        30: "Module over temperature",
        31: "Ambient over temperature",
    }

    def __init__(self, channel="test", bitrate=125000):
        print(f"[SIMULATOR]: Starting full NIUERA V1.3 virtual CAN bus on '{channel}'...")
        self.sim = MockNiueraModule(channel=channel)
        self.sim.start()
        time.sleep(0.05)

        self.bus = can.interface.Bus(interface="virtual", channel=channel, receive_own_messages=False)
        self.is_running = False

    def build_set_command(self, reg_address, decimal_value, sub_mode=0):
        can_data = [0x03, 0x00] + list(reg_address.to_bytes(2, "big"))
        if reg_address in (0x0080, 0x0084, 0x0089, 0x008A, 0x008B, 0x008C, 0x008D, 0x008E):
            can_data += list(int(sub_mode).to_bytes(2, "big", signed=True)) + list(int(decimal_value).to_bytes(2, "big", signed=True))
        elif reg_address in (0x001F, 0x0024, 0x0025, 0x0031, 0x0042, 0x0044, 0x0085, 0x0086):
            target_val = 0x00000000 if decimal_value == 0 else 0x00010000
            can_data += list(target_val.to_bytes(4, "big"))
        elif reg_address == 0x002F:
            modes = {0: 0x00000000, 1: 0x00010000, 2: 0x00020000}
            can_data += list(modes.get(decimal_value, 0).to_bytes(4, "big"))
        elif reg_address == 0x0030:
            states = {0: 0x00000000, 1: 0x00010000}
            can_data += list(states.get(decimal_value, 0).to_bytes(4, "big"))
        elif reg_address == 0x0083:
            types_map = {0: 0x00A00000, 1: 0x00A10000, 2: 0x00A20000}
            can_data += list(types_map.get(decimal_value, 0x00A00000).to_bytes(4, "big"))
        elif reg_address == 0x001E:
            can_data += [0x00, 0x00, 0x00, int(decimal_value) & 0x07]
        else:
            can_data += list(int(decimal_value).to_bytes(4, "big", signed=True))
        return can_data

    def build_read_command(self, reg_address: int) -> list:
        return [0x10, 0x00] + list(reg_address.to_bytes(2, "big")) + [0x00, 0x00, 0x00, 0x00]

    def decode_response_dict(self, response_data) -> dict:
        """Decodes any NIUERA 0x42 reply frame into a structured dictionary for shared_data."""
        if len(response_data) < 8:
            return {}
        err_code = response_data[1]
        reg = int.from_bytes(response_data[2:4], "big")
        val_u32 = int.from_bytes(response_data[4:8], "big", signed=False)
        val_s32 = int.from_bytes(response_data[4:8], "big", signed=True)
        val_high = int.from_bytes(response_data[4:6], "big", signed=False)
        val_high_s = int.from_bytes(response_data[4:6], "big", signed=True)
        val_low = int.from_bytes(response_data[6:8], "big", signed=False)
        val_low_s = int.from_bytes(response_data[6:8], "big", signed=True)

        if err_code != 0xF0:
            return {"command_failed": True, "register": reg, "error_code": err_code}

        match reg:
            case 0x0001:
                return {"ac_voltage": round(val_high * 0.1, 2), "ac_current": round(val_low_s * 0.01, 2)}
            case 0x0004:
                return {"ac_line_ab_v": round(val_u32 * 0.1, 2)}
            case 0x000A:
                return {"ac_frequency": round(val_u32 * 0.001, 3)}
            case 0x000B:
                return {"temperature": round(val_s32 * 0.001, 2)}
            case 0x000C:
                return {"ac_power": float(val_s32)}
            case 0x000F:
                v_dc = round(val_high * 0.1, 2)
                i_dc = round(val_low_s * 0.01, 2)
                return {"dc_voltage": v_dc, "dc_current": i_dc, "dc_power": round(v_dc * i_dc, 2)}
            case 0x0040:
                active_faults = [
                    desc for bit, desc in self.ALARM_DESCRIPTIONS.items()
                    if (val_u32 >> bit) & 1
                ]
                return {"alarm_bitmask": val_u32, "error_log": active_faults}
            case _:
                return {"ack_register": reg, "raw_u32": val_u32}

    def send_and_decode(self, can_id: int, payload: list, timeout=0.05) -> dict:
        """Transmits a frame, waits for reply, and returns decoded telemetry/ACK dict."""
        self.bus.send(can.Message(arbitration_id=can_id, data=payload, is_extended_id=True))
        rx = self.bus.recv(timeout=timeout)
        if not rx:
            return {"timeout": True}
        parsed = self.decode_response_dict(rx.data)
        parsed["rx_msg"] = rx
        return parsed

    def close(self):
        self.bus.shutdown()
        self.sim.stop()