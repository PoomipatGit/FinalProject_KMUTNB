import json

class BatteryModel:
    def __init__(self, battery_page=None):
        self.battery_page = battery_page
        self.capacity_ah = self.battery_page.edit_capacity_val
        self.full_voltage_v = self.battery_page.full_volt_val
        self.empty_voltage_v = self.battery_page.empty_volt_val
        self.parallel = self.battery_page.parallel
        self.series = self.battery_page.series
        self.inner_resistance_mohm = self.battery_page.inner_resist_val
        self.soc_high_pct = self.battery_page.soc_high_val
        self.soc_low_pct = self.battery_page.soc_low_val
        self.charge_current_max_a = self.battery_page.chrg_amp_max_val
        self.discharge_current_max_a = self.battery_page.dischrg_amp_max_val
        self.init_soc_pct = self.battery_page.init_soc_val
        self.init_voc_v = self.battery_page.init_voc_val
        self.init_cap_ah = self.battery_page.init_cap_val

        self.fullchrgvolt_val = self.battery_page.fullchrgvolt_val
        self.fullchrg_ah_val = self.battery_page.fullchrg_dischrg_ah_val
        self.expovolt_val = self.battery_page.expovolt_val
        self.expo_ah_val = self.battery_page.expo_dischrg_ah_val
        self.nomvolt_val = self.battery_page.nomvolt_val
        self.nom_ah_val = self.battery_page.nom_dischrg_ah_val

        self.battery_dict = {
            #AH ,Volt
            "Ah": self.capacity_ah,
            "Full_Volt": self.full_voltage_v,
            "Empty_Volt": self.empty_voltage_v,
            #cell
            "Parallel": self.parallel,
            "Series": self.series,
            "Inner_Resistance_mohm": self.inner_resistance_mohm,
            #protection
            "SOC_High_pct": self.soc_high_pct,
            "SOC_Low_pct": self.soc_low_pct,
            "Charge_Current_Max_A": self.charge_current_max_a,
            "Discharge_Current_Max_A": self.discharge_current_max_a,
            #init
            "Init_SOC_pct": self.init_soc_pct,
            "Init_VOC_V": self.init_voc_v,
            "Init_Cap_Ah": self.init_cap_ah,
            "Full_Charge_Voltage": float(self.fullchrgvolt_val),
            "Full_Charge_Ah": float(self.fullchrg_ah_val),
            "Exponential_Zone_Voltage": float(self.expovolt_val),
            "Exponential_Zone_Ah": float(self.expo_ah_val),
            "Nominal_Voltage": float(self.nomvolt_val),
            "Nominal_Ah": float(self.nom_ah_val)
        }
    def readnget_battery_prm(self, file_path):
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
            
            self.fullchrgvolt_val = data["full_charge_voltage_v"]
            self.fullchrg_ah_val = data["full_charge_discharge_capacity_ah"]
            self.expovolt_val = data["exponential_zone_voltage_v"]
            self.expo_ah_val = data["exponential_zone_discharge_capacity_ah"]
            self.nomvolt_val = data["nominal_voltage_v"]
            self.nom_ah_val = data["nominal_discharge_capacity_ah"]
            self.battery_dict = {
                "Ah": float(self.edit_capacity_val),
                "Full_Volt": float(self.full_volt_val),
                "Empty_Volt": float(self.empty_volt_val),
                "Parallel": int(self.parallel),
                "Series": int(self.series),
                "Inner_Resistance_mohm": float(self.inner_resist_val),
                "SOC_High_pct": int(self.soc_high_val),
                "SOC_Low_pct": int(self.soc_low_val),
                "Charge_Current_Max_A": float(self.chrg_amp_max_val),
                "Discharge_Current_Max_A": float(self.dischrg_amp_max_val),
                "Init_SOC_pct": int(self.init_soc_val),
                "Init_VOC_V": float(self.init_voc_val),
                "Init_Cap_Ah": float(self.init_cap_val),
                "Full_Charge_Voltage": float(self.fullchrgvolt_val),
                "Full_Charge_Ah": float(self.fullchrg_ah_val),
                "Exponential_Zone_Voltage": float(self.expovolt_val),
                "Exponential_Zone_Ah": float(self.expo_ah_val),
                "Nominal_Voltage": float(self.nomvolt_val),
                "Nominal_Ah": float(self.nom_ah_val)
            }
            print(self.battery_dict)
            return self.battery_dict
        except Exception as e:
            print(f"Error reading battery parameters: {e}")
            return None
        
        
if __name__ == "__main__":     
    Battery = BatteryModel()
    Battery.readnget_battery_prm(r"C:\Users\nutta\OneDrive\เดสก์ท็อป\ARM\year 3.2\CAN BUS\FinalProject_KMUTNB\ถ่านตรากบ.json")