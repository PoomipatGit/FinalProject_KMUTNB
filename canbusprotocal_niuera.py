import time
import can
import sys
import os
import numpy as np
import pandas as pd
import threading

class CanbusProtocol:
    def __init__(self):
        #ตั้งค่า bus
        print(f"Setting up CAN bus...")
        """
        os.system(f"sudo ip link set can0 down")
        os.system(f"sudo ip link set can0 type can bitrate 125000")
        os.system(f"sudo ip link set can0 up")
        self.bus = can.interface.Bus(channel='can0', bustype='socketcan')
        """
        self.bus = can.interface.Bus(interface='virtual', channel='test', receive_own_messages=True)
        print(f"CAN bus setup complete.")
        
        self.is_running = False

    def set_filter(self,can_id): # can id ของ send ที่ต้องการรับ response เช่น 0x06180780
        bin_str = f"{can_id:029b}"
        protno = bin_str[0:9]
        ptp = bin_str[9]
        dstaddr = bin_str[10:18]
        srcaddr = bin_str[18:26]
        group = bin_str[26:29]
        res_id_str = protno + ptp + srcaddr + dstaddr + group
        res_id_int = int(res_id_str, 2)
        my_filters = [
            {"can_id": res_id_int, "can_mask": 0x1FFFFFFF, "extended": True}
        ]
        self.bus.set_filters(my_filters)
        return res_id_int
    def message_pack(self,protno_hex,ptp,dstaddr_hex,srcaddr_hex,group_oct,func_code,reg_adds_high,reg_adds_low):
        #Pack message Identifier
        can_id = (
            (protno_hex << 20) |
            (ptp << 19) |
            (dstaddr_hex << 11) |
            (srcaddr_hex << 3) |
            group_oct
        )    
        #Pack message payload
        payload = [0x00] * 8
        payload[0] = func_code
        payload[2] = reg_adds_high
        payload[3] = reg_adds_low
        return can_id, payload # เลขฐาน10ของ can_id และ list ของ payload
    def conv_hextodec(self,can_id_hex,payload_hex):
        can_id_dec = int.from_bytes(bytes.fromhex(can_id_hex), byteorder="big")
        payload_dec = [int(x, 16) for x in payload_hex.split()]
        return can_id_dec , payload_dec
    
    def send_raw_frame(self, can_id, data):
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=True)
        self.bus.send(msg)
        
    def read_once_frombits(self, protno_hex, ptp, dstaddr_hex, srcaddr_hex, group_oct, func_code, reg_adds_high, reg_adds_low, timeout=1.0):
        can_id, payload = self.message_pack(protno_hex,ptp,dstaddr_hex,srcaddr_hex,group_oct,func_code,reg_adds_high,reg_adds_low)
        self.set_filter(can_id)
        try: 
            while self.bus.recv(timeout=0) is not None:
                pass
            self.send_raw_frame(can_id, payload)
            data_hex_str = " ".join(f"{b:02X}" for b in payload)
            print(f"-> Sent Request: ID: {hex(can_id)} Data: {data_hex_str}")
            # ==========================================
            # ส่วนจำลอง (MOCK RESPONSE): หลอกว่ามีอุปกรณ์ตอบกลับ
            # ==========================================
            if can_id == 0x06180780 and func_code == 0x10 and reg_adds_high == 0x00 and reg_adds_low == 0x01: 
                mock_data = [0x41, 0xF0, 0x00, 0x01, 0x08, 0xE8, 0x00, 0x00] 
                mock_msg = can.Message(
                    arbitration_id=0x061F8000,
                    data=mock_data,
                    is_extended_id=True
                )
                self.bus.send(mock_msg)
            # ==========================================
            
            response_message = self.bus.recv(timeout=timeout) #เวลารอ
            if response_message:
                print(f"<- Response Received")
                print(f"   ID: {hex(response_message.arbitration_id)}")
                print(f"   Data (Hex):  {response_message.data.hex().upper()}")
                self.decoder_response(response_message.data)
                return response_message
            else: print("<- Timeout: No response")
        except can.CanError as e:
            print(f"Failed to send: {e}")
            
    def read_loop_frombits(self, protno_hex, ptp, dstaddr_hex, srcaddr_hex, group_oct,func_code, reg_adds_high, reg_adds_low, interval, timeout):
        self.is_running = True
        params = (protno_hex, ptp, dstaddr_hex, srcaddr_hex, group_oct, func_code, reg_adds_high, reg_adds_low)
        def _running():
            while self.is_running:
                self.read_once_frombits(*params, timeout=timeout)
                time.sleep(interval)
        #สั่งให้งานเบื้องหลัง
        thread = threading.Thread(target=_running, daemon=True)
        thread.start()
        print("System running... (Press Ctrl+C to stop)")
        try:
            while True:
                time.sleep(1) ##เอาออกตอนกับ gui
        except KeyboardInterrupt:
            print("\n_detected Ctrl+C, shutting down...")
            self.is_running = False
            self.close()
            print("System closed successfully")
            
    def read_once_fromgui(self,can_id,payload,timeout=1.0): #0C 20 07 80 , 03 00 00 77 00 00 00 00
        can_id, payload = self.conv_hextodec(can_id,payload)
        self.set_filter(can_id)
        try: 
            while self.bus.recv(timeout=0) is not None:
                pass
            self.send_raw_frame(can_id, payload)
            data_hex_str = " ".join(f"{b:02X}" for b in payload)
            print(f"-> Sent Request: ID: {hex(can_id)} Data: {data_hex_str}")
            
            response_message = self.bus.recv(timeout=timeout) #เวลารอ
            if response_message:
                res_id_hex = f"0x{response_message.arbitration_id:08X}"
                res_data_hex = response_message.data.hex(" ").upper()
                print(f"<- Response Received")
                print(f"   ID: {res_id_hex}")
                print(f"   Data (Hex):  {res_data_hex}")
                
                self.decoder_response(response_message.data)
                return res_id_hex,res_data_hex
            else: print("<- Timeout: No response")
        except can.CanError as e:
            print(f"Failed to send: {e}")      
                
    def decoder_response(self, response_data):
        hex_list = [f"{b:02X}" for b in response_data]
        print(f"{hex_list}")
        register_number = int.from_bytes(response_data[2:4], byteorder='big')
        val_data_bytes = int.from_bytes(response_data[4:8], byteorder='big')
        val_data_high = int.from_bytes(response_data[4:6], byteorder='big')
        val_data_low = int.from_bytes(response_data[6:8], byteorder='big')
        # ถอดรหัส Signed (สำหรับ Current, Active/Reactive Power, Power Factor, Temperature)
        val_data_bytes_s = int.from_bytes(response_data[4:8], byteorder='big', signed=True)
        val_data_high_s = int.from_bytes(response_data[4:6], byteorder='big', signed=True)
        val_data_low_s = int.from_bytes(response_data[6:8], byteorder='big', signed=True)
        match register_number:
            case 0x0001:
                print("Register Address: 0x0001 - Read AC A Phase Voltage and phase current")
                print(f"A Phase Voltage: {val_data_high * 0.1:.1f} V")
                print(f"A Phase Current: {val_data_low_s * 0.01:.2f} A")

            case 0x0002:
                print("Register Address: 0x0002 - Read AC B Phase Voltage and phase current")
                print(f"B Phase Voltage: {val_data_high * 0.1:.1f} V")
                print(f"B Phase Current: {val_data_low_s * 0.01:.2f} A")

            case 0x0003:
                print("Register Address: 0x0003 - Read AC C Phase Voltage and phase current")
                print(f"C Phase Voltage: {val_data_high * 0.1:.1f} V")
                print(f"C Phase Current: {val_data_low_s * 0.01:.2f} A")

            case 0x0004:
                print("Register Address: 0x0004 - Read AC AB line Voltage")
                print(f"Voltage AB: {val_data_bytes * 0.1:.1f} V")

            case 0x0005:
                print("Register Address: 0x0005 - Reading AC BC Line Voltage")
                print(f"Voltage BC: {val_data_bytes * 0.1:.1f} V")

            case 0x0006:
                print("Register Address: 0x0006 - Read AC CA line voltage")
                print(f"Voltage CA: {val_data_bytes * 0.1:.1f} V")

            case 0x0007:
                print("Register Address: 0x0007 - Read phase A, active power and reactive power")
                print(f"Phase A Active Power: {val_data_high_s} W")
                print(f"Phase A Reactive Power: {val_data_low_s} Var")

            case 0x0008:
                print("Register Address: 0x0008 - Read phase B, active power and reactive power")
                print(f"Phase B Active Power: {val_data_high_s} W")
                print(f"Phase B Reactive Power: {val_data_low_s} Var")

            case 0x0009:
                print("Register Address: 0x0009 - Read phase C, active power and reactive power")
                print(f"Phase C Active Power: {val_data_high_s} W")
                print(f"Phase C Reactive Power: {val_data_low_s} Var")

            case 0x000A:
                print("Register Address: 0x000A - Read AC frequency")
                print(f"AC Frequency: {val_data_bytes * 0.001:.3f} Hz")

            case 0x000B:
                print("Register Address: 0x000B - Read module panel (ambient) temperature")
                print(f"Ambient Temperature: {val_data_bytes_s * 0.001:.3f} °C")

            case 0x000C:
                print("Register Address: 0x000C - Read total active power")
                print(f"Total Active Power: {val_data_bytes_s} W")

            case 0x000D:
                print("Register Address: 0x000D - Read total reactive power")
                print(f"Total Reactive Power: {val_data_bytes_s} Var")

            case 0x000E:
                print("Register Address: 0x000E - Read total apparent power")
                print(f"Total Apparent Power: {val_data_bytes} VA")

            case 0x000F:
                print("Register Address: 0x000F - Read DC side, voltage and current")
                print(f"DC Side Voltage: {val_data_high * 0.1:.1f} V")
                mode_desc = "Rectifier (Charge)" if val_data_low_s >= 0 else "Inverter (Discharge)"
                print(f"DC Side Current: {val_data_low_s * 0.01:.2f} A ({mode_desc})")

            case 0x0011:
                print("Register Address: 0x0011 - Read the rated output power")
                print(f"Rated Output Power: {val_data_bytes * 0.001:.3f} W")

            case 0x0017:
                print("Register Address: 0x0017 - Set the module's operating altitude")
                print(f"Altitude Setting: {val_data_bytes} m")

            case 0x001E:
                print("Register Address: 0x001E - Set Group Number")
                group_num = response_data[7] & 0x07
                print(f"Group Number: {group_num}")

            case 0x001F:
                print("Register Address: 0x001F - Set the module address allocation method")
                desc = "Automatic allocation" if val_data_bytes == 0x00000000 else "Dial setting"
                print(f"Allocation Method: {desc} (0x{val_data_bytes:08X})")

            case 0x0024:
                print("Register Address: 0x0024 - Set the AC side undervoltage reset in off-grid mode")
                print(f"Reset Status: {'Reset' if val_data_bytes == 0x00010000 else 'Disable'}")

            case 0x0025:
                print("Register Address: 0x0025 - Set the DC side undervoltage reset in rectification mode")
                print(f"Reset Status: {'Reset' if val_data_bytes == 0x00010000 else 'Disable'}")

            case 0x002F:
                print("Register Address: 0x002F - Set the module working mode")
                modes = {
                    0x00000000: "Grid-connected mode",
                    0x00010000: "Off-grid mode",
                    0x00020000: "Rectification mode"
                }
                print(f"Working Mode: {modes.get(val_data_bytes, f'Unknown (0x{val_data_bytes:08X})')}")

            case 0x0030:
                print("Register Address: 0x0030 - Set the module to power on or off")
                print(f"Power Status: {'Shutdown' if val_data_bytes == 0x00010000 else 'Startup'}")

            case 0x0031:
                print("Register Address: 0x0031 - Set the module DC side overvoltage reset")
                print(f"Reset Status: {'Reset' if val_data_bytes == 0x00010000 else 'Disable'}")

            case 0x0040:
                print("Register Address: 0x0040 - Read the current alarm/status of the module")
                print(f"Status Raw Bitmask: 0x{val_data_bytes:08X}")
#--------------------------------------------------------------------------------------------------------------------
            case 0x0042:
                print("Register Address: 0x0042 - Set the DC side undervoltage reset in inverter mode")
                print(f"Reset Status: {'Reset' if val_data_bytes == 0x00010000 else 'Disable'}")

            case 0x0043:
                print("Register Address: 0x0043 - Read module group address")
                print(f"Module Group Number: {val_data_high}")
                print(f"Module Address: {val_data_low}")

            case 0x0044:
                print("Register Address: 0x0044 - Set module short circuit reset")
                print(f"Reset Status: {'Reset' if val_data_bytes == 0x00010000 else 'Disable'}")

            case 0x004A:
                print("Register Address: 0x004A - Read the current altitude setting")
                print(f"Current Altitude: {val_data_bytes} m")

            case 0x0056:
                print("Register Address: 0x0056 - Read module software version number")
                print(f"Software Version: {val_data_low}")

            case 0x0077:
                print("Register Address: 0x0077 - Setting the DC link voltage")
                print(f"DC Link Voltage: {val_data_bytes * 0.001:.3f} V")

            case 0x0079:
                print("Register Address: 0x0079 - Set the DC current")
                print(f"DC Current Setpoint: {val_data_bytes_s * 0.001:.3f} A")

            case 0x0080:
                print("Register Address: 0x0080 - Set total active power on the AC side")
                ctrl_str = "Control DC side power" if val_data_high == 0x0000 else "Control AC side power"
                print(f"Power Control Mode: {ctrl_str}")
                print(f"Total Active Power Setpoint: {val_data_low_s} W")

            case 0x0081:
                print("Register Address: 0x0081 - Set total reactive power on the AC side")
                print(f"Reactive Power Setpoint: {val_data_bytes_s} Var")

            case 0x0082:
                print("Register Address: 0x0082 - Set AC side power factor PF")
                print(f"AC Side PF: {val_data_bytes_s * 0.001:.3f}")

            case 0x0083:
                print("Register Address: 0x0083 - Set the reactive power type on the AC side")
                types = {
                    0x00A00000: "Do not set reactive power output function",
                    0x00A10000: "Use the PF setting command",
                    0x00A20000: "Use the reactive power setting command"
                }
                print(f"Type: {types.get(val_data_bytes, f'0x{val_data_bytes:08X}')}")

            case 0x0084:
                print("Register Address: 0x0084 - Set the rated phase voltage and AC frequency")
                print(f"Rated Phase Voltage: {val_data_high * 0.1:.1f} V")
                print(f"AC Frequency: {val_data_low * 0.001:.3f} Hz")

            case 0x0085:
                print("Register Address: 0x0085 - Set whether the phase is wrong")
                print(f"Phase Error Setting: {'Allowed' if val_data_bytes == 0x00010000 else 'Not allowed'}")

            case 0x0086:
                print("Register Address: 0x0086 - Setting up the island detection function")
                print(f"Island Detection: {'Disable' if val_data_bytes == 0x00010000 else 'Enable'}")

            case 0x0087:
                print("Register Address: 0x0087 - Set the DC undervoltage protection voltage")
                print(f"DC Undervoltage Protection: {val_data_bytes * 0.1:.1f} V")

            case 0x0088:
                print("Register Address: 0x0088 - Set the DC overvoltage protection voltage")
                print(f"DC Overvoltage Protection: {val_data_bytes * 0.1:.1f} V")

            case 0x0089:
                print("Register Address: 0x0089 - Set AC undervoltage protection voltage and time")
                print(f"AC Undervoltage Voltage: {val_data_high * 0.1:.1f} V")
                print(f"Protection Time: {val_data_low * 0.01:.2f} s")

            case 0x008A:
                print("Register Address: 0x008A - Set AC overvoltage protection voltage and time")
                print(f"AC Overvoltage Voltage: {val_data_high * 0.1:.1f} V")
                print(f"Protection Time: {val_data_low * 0.01:.2f} s")

            case 0x008B:
                print("Register Address: 0x008B - Set the frequency and time of the first-level AC underfrequency protection")
                print(f"Protection Frequency: {val_data_high * 0.01:.2f} Hz")
                print(f"Protection Time: {val_data_low * 0.01:.2f} s")

            case 0x008C:
                print("Register Address: 0x008C - Set the first-level AC overfrequency protection frequency and time")
                print(f"Protection Frequency: {val_data_high * 0.01:.2f} Hz")
                print(f"Protection Time: {val_data_low * 0.01:.2f} s")

            case 0x008D:
                print("Register Address: 0x008D - Set the secondary AC underfrequency protection frequency and time")
                print(f"Protection Frequency: {val_data_high * 0.01:.2f} Hz")
                print(f"Protection Time: {val_data_low * 0.01:.2f} s")

            case 0x008E:
                print("Register Address: 0x008E - Set the secondary AC over-frequency protection frequency and time")
                print(f"Protection Frequency: {val_data_high * 0.01:.2f} Hz")
                print(f"Protection Time: {val_data_low * 0.01:.2f} s")

            case _:
                print(f"Unknown Register Address: 0x{register_number:04X}")

    def build_set_command(self, reg_address, decimal_value, sub_mode=0): #sub mode เป็นค่า 0 หรือ 1 สำหรับบาง register ที่ต้องการกำหนดค่า high/low
        # พื้นฐานของคำสั่ง Set: Function Code 03 และ Reserve Byte 1 (0x00)
        can_data = [0x03, 0x00]
    
        # แปลง Register Address เป็น 2 ไบต์ (Byte 2 และ Byte 3)
        reg_bytes = reg_address.to_bytes(2, byteorder='big')
        can_data.extend(reg_bytes)
    
        match reg_address:
            # -------------------------------------------------------------------------------------------------
            # กลุ่มที่ 1: Byte 4-5 เป็นค่านึง (sub_mode/high) และ Byte 6-7 เป็นอีกค่านึง (decimal_value/low)
            # -------------------------------------------------------------------------------------------------
            case 0x0080:
                print(f"Building Set Command: 0x0080 - Set total active power on the AC side") # sub mode 0 ,1
                val_high = int(sub_mode).to_bytes(2, byteorder='big')
                val_low = int(decimal_value).to_bytes(2, byteorder='big', signed=True)
                can_data.extend(list(val_high) + list(val_low))

            case 0x0084 | 0x0089 | 0x008A | 0x008B | 0x008C | 0x008D | 0x008E: # sub mode เป็นค่าฐาน 10 (เอาไปคูณ unit เป็นค่าจริง)
                print(f"Building Set Command: 0x{reg_address:04X} - Set Voltage/Frequency & Time protection")
                val_high = int(sub_mode).to_bytes(2, byteorder='big', signed=True)
                val_low = int(decimal_value).to_bytes(2, byteorder='big', signed=True)
                can_data.extend(list(val_high) + list(val_low))

            # -------------------------------------------------------------------------------------------------
            # กลุ่มที่ 2: Byte 4-7 เป็นค่าตัวเลขต่อเนื่อง Integer เดียว (32-bit รองรับค่าบวก/ลบ)
            # -------------------------------------------------------------------------------------------------
            case 0x0017:
                print("Building Set Command: 0x0017 - Set module's operating altitude")
                val_bytes = int(decimal_value).to_bytes(4, byteorder='big')
                can_data.extend(list(val_bytes))

            case 0x0077 | 0x0079 | 0x0081 | 0x0082 | 0x0087 | 0x0088:
                print(f"Building Set Command: 0x{reg_address:04X} - Set electrical parameters (DC link, Current, Power, PF)")
                val_bytes = int(decimal_value).to_bytes(4, byteorder='big', signed=True)
                can_data.extend(list(val_bytes))

            # -------------------------------------------------------------------------------------------------
            # กลุ่มที่ 3: Fixed / Preset values (เลือกโหมดหรือสถานะตายตัวตามเงื่อนไข)
            # -------------------------------------------------------------------------------------------------
            case 0x001F:
                print("Building Set Command: 0x001F - Set address allocation method")
                # decimal_value: 0 = Automatic allocation, 1 = Dial setting
                target_val = 0x00000000 if decimal_value == 0 else 0x00010000
                can_data.extend(list(target_val.to_bytes(4, byteorder='big')))

            case 0x0024 | 0x0025 | 0x0031 | 0x0042 | 0x0044 | 0x0085 | 0x0086:
                print(f"Building Set Command: 0x{reg_address:04X} - Set Reset / Protection configurations")
                # decimal_value: 0 = Disable, 1 = Reset / Allow
                target_val = 0x00000000 if decimal_value == 0 else 0x00010000
                can_data.extend(list(target_val.to_bytes(4, byteorder='big')))

            case 0x002F:
                print("Building Set Command: 0x002F - Set module working mode")
                # decimal_value: 0 = Grid-connected, 1 = Off-grid, 2 = Rectification
                modes = {0: 0x00000000, 1: 0x00010000, 2: 0x00020000}
                target_val = modes.get(decimal_value, 0x00000000)
                can_data.extend(list(target_val.to_bytes(4, byteorder='big')))

            case 0x0030:
                print("Building Set Command: 0x0030 - Set power on or off")
                # decimal_value: 0 = Startup, 1 = Shutdown
                states = {0: 0x00000000, 1: 0x00010000}
                target_val = states.get(decimal_value, 0x00000000)
                can_data.extend(list(target_val.to_bytes(4, byteorder='big')))

            case 0x0083:
                print("Building Set Command: 0x0083 - Set reactive power type on AC side")
                # decimal_value: 0 = Do not set, 1 = Use PF, 2 = Use Reactive power
                types_map = {0: 0x00A00000, 1: 0x00A10000, 2: 0x00A20000}
                target_val = types_map.get(decimal_value, 0x00A00000)
                can_data.extend(list(target_val.to_bytes(4, byteorder='big')))

            # -------------------------------------------------------------------------------------------------
            # กลุ่มที่ 4: อื่นๆ (โครงสร้างบิตพิเศษ)
            # -------------------------------------------------------------------------------------------------
            case 0x001E:
                print("Building Set Command: 0x001E - Set Group Number")
                group_val = int(decimal_value) & 0x07  # ใช้ 3 บิตล่างของ Byte 7
                can_data.extend([0x00, 0x00, 0x00, group_val])

            case _:
                print(f"Warning: Unknown Register Address 0x{reg_address:04X}, defaulting to 32-bit integer.")
                val_bytes = int(decimal_value).to_bytes(4, byteorder='big', signed=True)
                can_data.extend(list(val_bytes))
            
        # แปลงผลลัพธ์เป็น Hex string สำหรับตรวจสอบหรือส่งต่อ
        hex_list = [f"{b:02X}" for b in can_data]
        print(f"Generated TX Data: {hex_list}\n")
        return can_data
        
    def close(self):
        self.bus.shutdown()
    
if __name__ == "__main__":
    protocol = CanbusProtocol()
    protocol.message_sendandres_loop_frombits(protno_hex=0x061, ptp=1, dstaddr_hex=0x00, srcaddr_hex=0xF0, group_oct=0o0, 
                                    func_code=0x10,reg_adds_high=0x00, reg_adds_low=0x01, interval=0.5, timeout=1.0)#data