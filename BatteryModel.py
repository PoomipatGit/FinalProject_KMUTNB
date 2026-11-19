import json

class BatteryModel:
    def __init__(self):
        self.capacity_ah = 0.0
        self.full_voltage_v = 0.0
        self.empty_voltage_v = 0.0
        self.parallel = 0
        self.series = 0
        self.inner_resistance_mohm = 0.0
        self.soc_high_pct = 0
        self.soc_low_pct = 0
        self.charge_current_max_a = 0.0
        self.discharge_current_max_a = 0.0
        self.init_soc_pct = 0
        self.init_voc_v = 0.0
        self.init_cap_ah = 0.0
        self.battery_data = {
            "Ah": self.capacity_ah,
            "Full_Volt": self.full_voltage_v,
            "Empty_Volt": self.empty_voltage_v,
            "Parallel": self.parallel,
            "Series": self.series,
            "Inner_Resistance_mohm": self.inner_resistance_mohm,
            "SOC_High_pct": self.soc_high_pct,
            "SOC_Low_pct": self.soc_low_pct,
            "Charge_Current_Max_A": self.charge_current_max_a,
            "Discharge_Current_Max_A": self.discharge_current_max_a,
            "Init_SOC_pct": self.init_soc_pct,
            "Init_VOC_V": self.init_voc_v,
            "Init_Cap_Ah": self.init_cap_ah
        }
    def read_battery_prm(self, file_path):
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
                
            self.capacity_ah = data["capacity_ah"]
            self.full_voltage_v = data["full_voltage_v"]
            self.empty_voltage_v = data["empty_voltage_v"]
            self.parallel = data["parallel"]
            self.series = data["series"]
            self.inner_resistance_mohm = data["inner_resistance_mohm"]
            self.soc_high_pct = data["soc_high_pct"]
            self.soc_low_pct = data["soc_low_pct"]
            self.charge_current_max_a = data["charge_current_max_a"]
            self.discharge_current_max_a = data["discharge_current_max_a"]
            self.init_soc_pct = data["init_soc_pct"]
            self.init_voc_v = data["init_voc_v"]
            self.init_cap_ah = data["init_cap_ah"]
            
            self.battery_data = {
                "Ah": self.capacity_ah,
                "Full_Volt": self.full_voltage_v,
                "Empty_Volt": self.empty_voltage_v,
                "Parallel": self.parallel,
                "Series": self.series,
                "Inner_Resistance_mohm": self.inner_resistance_mohm,
                "SOC_High_pct": self.soc_high_pct,
                "SOC_Low_pct": self.soc_low_pct,
                "Charge_Current_Max_A": self.charge_current_max_a,
                "Discharge_Current_Max_A": self.discharge_current_max_a,
                "Init_SOC_pct": self.init_soc_pct,
                "Init_VOC_V": self.init_voc_v,
                "Init_Cap_Ah": self.init_cap_ah
            }
            print(self.battery_data)
        except Exception as e:
            print(f"Error reading battery parameters: {e}")
            return None
        
        
        
        
Battery = BatteryModel()
Battery.read_battery_prm(r"C:\Users\nutta\OneDrive\เดสก์ท็อป\ARM\year 3.2\CAN BUS\FinalProject_KMUTNB\ถ่านตรากบ.json")