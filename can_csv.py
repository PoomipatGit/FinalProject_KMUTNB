from concurrent.futures import thread
import csv
import os
from socket import timeout
import threading
import time
import pandas as pd  
import re
from canbusprotocal_niuera import CanbusProtocol

# ไฟล์ csv 1 ไฟล์คือการส่งข้อมูลที่ต้องการเป็น set 1 set โดยจะต้องกำหนดเวลาเท่ากันทั้งไฟล์ เช่นจะ set V ต้อง 1.set v 2. ปล่อย v 3. อ่าน v รวม 3 ขั้นตอนใน 1 ไฟล์ เวลาค่าเดียวกัน
class CSVLogger:
    def __init__(self, file_path=None):
        self.filepath = file_path
        self.canprotocal = CanbusProtocol()
    def check_filepath(self, file_path):
        print(f"--- กำลังเปิดอ่านไฟล์จาก Path: {file_path} ---")
        # เช็กก่อนว่ามีไฟล์นี้อยู่จริงไหม
        if not os.path.exists(file_path):
            print(f"❌ ไม่พบไฟล์ที่ระบุ: {file_path}")
            return False
        return True
    def readcsv_to_df(self, file_path=None): #จะใช้ file_path ที่ส่งเข้ามาเป็น argument หรือใช้ self.filepath ถ้าไม่มีการส่งเข้ามา
        target_path = file_path if file_path is not None else self.filepath
        if self.check_filepath(target_path) == False:
            return
        data_list = []
        # เปิดไฟล์เพื่ออ่าน (Read mode)
        with open(target_path, mode="r", encoding="utf-8") as f:
            csv_reader = csv.DictReader(f)
            row_count = 0
            for row in csv_reader:
                row_count += 1
                # 1. กรองและดึงข้อมูลใส่ตัวแปรแต่ละตัว
                Name_csv = row.get("name") if row.get("name") and row.get("name").strip() != "" else "-"
                TxRx_csv = row.get("txrx") if row.get("txrx") and row.get("txrx").strip() != "" else "-"
                ID_csv = row.get("identifier") if row.get("identifier") and row.get("identifier").strip() != "" else "-"
                Data_csv = row.get("can_data") if row.get("can_data") and row.get("can_data").strip() != "" else "-"
                Value_csv = row.get("value") if row.get("value") and row.get("value").strip() != "" else "-"
                Comment_csv = row.get("comment") if row.get("comment") and row.get("comment").strip() != "" else "-"
                Action_csv = row.get("action") if row.get("action") and row.get("action").strip() != "" else "-"
                Result_csv = row.get("result") if row.get("result") and row.get("result").strip() != "" else "-"
                # 2. ปริ้นท์โชว์ทีละแถว
                print(f"Name: {Name_csv}, TxRx: {TxRx_csv}, Identifier: {ID_csv}, CAN Data: {Data_csv}, Value: {Value_csv}, Comment: {Comment_csv}, Action: {Action_csv}, Result: {Result_csv}")
                # 3. เก็บข้อมูลลงใน list ของ dict เพื่อสร้าง DataFrame 
                data_list.append({
                    "Name": Name_csv,
                    "TxRx": TxRx_csv,
                    "Identifier": ID_csv,
                    "CAN Data": Data_csv,
                    "Value": Value_csv,
                    "Comment": Comment_csv,
                    "Action": Action_csv,
                    "Result": Result_csv
                })
            # 4. สร้าง DataFrame จาก list ของ dict
            df = pd.DataFrame(data_list)
            print(df)
            print(f"--- อ่านข้อมูลเสร็จสิ้น (รวมทั้งหมด {row_count} แถว) ---\n")
        return df
    
    def split_timeandvalue(self, df):
        value = []
        sec = []
        for index, row in df.iterrows():
            value_str = row['Value']  # หรือ row['value']
            # 1. ป้องกันกรณีค่าว่าง (NaN)
            if pd.isna(value_str):
                value.append("-")
                sec.append(0.0)
                continue
            # 2. แยกข้อความอย่างปลอดภัย
            raw_str = str(value_str).strip()
            value_time = [x for x in re.split(r'[_sS]', raw_str) if x != '']
            
            # 3. เช็คความยาวป้องกัน Error การ Unpack
            if len(value_time) == 2:
                val = value_time[0]
                sec_val = float(value_time[1]) if value_time[1] else 0.0
            elif len(value_time) == 1:
                if raw_str.lower().endswith('s'):
                    val = "-"
                    sec_val = float(value_time[0])
                else:
                    val = value_time[0]
                    sec_val = 0.0
            else:
                print(f"Error: Unexpected format in 'Value' column: {value_str}")
                value.append("-")
                sec.append(0.0)
                continue
            value.append(val)
            sec.append(sec_val)
        # สร้างคอลัมน์ใหม่ใส่กลับเข้าไปใน DataFrame
        df['Value'] = value
        df['Sec'] = sec
        return df
    
    #อ่านค่าจากเวลาตัวแรกของ csv เพื่อใช้เป็นเวลารวมในการวนลูปส่ง can message ทั้งหมด
    def loop_all_can_commands_from_df(self,df,interval=0.1, timeout=1.0): #df จาก split_timeandvalue
        self.is_running = True
        self.loop_log = []
        
        if 'Sec' in df.columns and not df.empty:
            total_time = float(df['Sec'].iloc[0])
        else:
            total_time = 1.0  # ค่าสำรองหากไม่มีคอลัมน์ Sec หรือ DataFrame ว่าง
        def _running():
            start_time = time.time()

            while self.is_running and (time.time() - start_time) < total_time:
                for index, row in df.iterrows():
                    if not self.is_running or (time.time() - start_time) >= total_time:
                            break
                    # ดึงข้อมูลจากคอลัมน์ต่างๆ ในแถวปัจจุบันมาเก็บใส่ตัวแปร เพื่อแสดงผล และส่ง can message
                    name = row['Name']
                    tx_rx = row['TxRx']
                    identifier = row['Identifier']
                    raw_can_data = row['CAN Data']
                    value = row['Value']
                    sec_val = row['Sec']
                    comment = row['Comment']
                    action = row['Action']
                    result = row['Result']

                    print(f"\n=== Run row {index}: {name} ===")
                    if str(tx_rx).strip().upper() != "TX":
                        print(f"Skip {name}: Not Tx")
                        continue
                    if identifier == "-" or raw_can_data == "-":
                        print(f"Skip {name}: Missing Identifier or CAN Data")
                        continue
                    can_data = raw_can_data  # ค่าเริ่มต้น
                    try:
                        if raw_can_data != "-":
                            # แยกชุดข้อมูล CAN Data ออกมาเป็น List ของไบต์ (รองรับทั้งแบบช่องว่างคั่นหรือติดกัน)
                            parts = str(raw_can_data).strip().split()
                            if len(parts) == 1 and len(parts[0]) >= 2:
                                # กรณีเขียนติดกัน เช่น "03000079..." ให้ตัดแบ่งทีละ 2 ตัวอักษร
                                hex_bytes = [parts[0][i:i+2] for i in range(0, len(parts[0]), 2)]
                            else:
                                hex_bytes = parts

                            # ตรวจสอบว่า Byte ที่ 0 (index 0) มีค่าเป็น '03' และมีค่า Value ครบถ้วน
                            if len(hex_bytes) > 0 and hex_bytes[0].upper() == "03" and value != "-":
                                reg_address = int(hex_bytes[2] + hex_bytes[3], 16)
                                decimal_val = float(value)
                                sub_mode_val = int(row.get("SubMode", 0))

                                # เรียกใช้ build_set_command เพื่อสร้างคำสั่งใหม่
                                generated_can_data = self.canprotocal.build_set_command(
                                    reg_address, decimal_val, sub_mode=sub_mode_val
                                )

                                # แปลงผลลัพธ์เป็น Hex string สำหรับส่งออก
                                can_data = " ".join(
                                    [f"{b:02X}" for b in generated_can_data]
                                )
                    except Exception as e:
                        print(
                            f"Error building set command for row {index}: {e}"
                        )
                        continue
                    # ส่งข้อมูล CAN และรอรับ Response
                    response = self.canprotocal.read_once_fromgui(
                        can_id=identifier,
                        payload=can_data,
                        timeout=timeout
                    )
                    if response is not None:
                        res_id_hex, res_data_hex = response
                        print("Success!")
                    else:
                        res_id_hex = "-"
                        res_data_hex = "-"
                        print("Timeout!")
                        
                    self.loop_log.append({
                        "Time": round(time.time() - start_time, 3),
                        "Name": name,
                        "TxRx": tx_rx,
                        "Identifier": identifier,
                        "CAN Data": can_data,
                        "Response ID": res_id_hex,
                        "Response Data": res_data_hex,
                        "Value": value,
                        "Sec": sec_val,
                        "Comment": comment,
                        "Action": action,
                        "Result": result
                    })
                    time.sleep(interval)
            self.is_running = False
            self.result_df = pd.DataFrame(self.loop_log)
            print("\n--- CAN DataFrame loop finished ---")
        thread = threading.Thread(target=_running, daemon=True)
        thread.start()
        return thread
    def complete_loop_all_fromgui(self,file_path=None, interval=0.1, timeout=1.0): #วนลูปทั้งไฟล์ csv และส่ง can message ตามลำดับ
        df = self.split_timeandvalue(self.readcsv_to_df(file_path))
        return self.loop_all_can_commands_from_df(df, interval=interval, timeout=timeout)
    
    def loop_read_commands_from_df(self,df,interval=0.1, timeout=1.0): #df จาก split_timeandvalue # ส่งคำสั่ง Set (0x03) แค่รอบแรกครั้งเดียว แล้ววนลูปส่งเฉพาะคำสั่ง Read จนครบเวลา
        self.is_running = True                                          #ถใส่ data เป็น xx xx xx xx ได้เลย
        self.loop_log = []
        # เปลี่ยนจาก iloc[0] เป็น .max() เพื่อดึงเวลาไม่ว่าจะอยู่แถวไหนของไฟล์ CSV
        if 'Sec' in df.columns and not df.empty and df['Sec'].max() > 0:
            total_time = float(df['Sec'].max())
        else:
            total_time = 1.0  # ค่าสำรองหากไม่มีคอลัมน์ Sec หรือ DataFrame ว่าง
        def _running():
            start_time = time.time()
            loop_count = 0
            try:
                while self.is_running and (time.time() - start_time) < total_time: #ลูปเวลา
                    for index, row in df.iterrows(): #ลูปแต่ละแถวของ DataFrame
                        if not self.is_running or (time.time() - start_time) >= total_time:
                                break
                        # ดึงข้อมูลจากคอลัมน์ต่างๆ ในแถวปัจจุบันมาเก็บใส่ตัวแปร เพื่อแสดงผล และส่ง can message
                        name = row['Name']
                        tx_rx = row['TxRx']
                        identifier = row['Identifier']
                        raw_can_data = str(row['CAN Data']).replace('xx', '00').replace('XX', '00')
                        value = row['Value']
                        sec_val = row['Sec']
                        comment = row['Comment']
                        action = row['Action']
                        result = row['Result']

                        print(f"\n=== Run row {index}: {name} ===")
                        if str(tx_rx).strip().upper() != "TX":
                            print(f"Skip {name}: Not Tx")
                            continue
                        if identifier == "-" or raw_can_data == "-":
                            print(f"Skip {name}: Missing Identifier or CAN Data")
                            continue
                        can_data = raw_can_data  # ค่าเริ่มต้น
                        try:
                            if raw_can_data != "-":
                                # แยกชุดข้อมูล CAN Data ออกมาเป็น List ของไบต์ (รองรับทั้งแบบช่องว่างคั่นหรือติดกัน)
                                parts = str(raw_can_data).strip().split()
                                if len(parts) == 1 and len(parts[0]) >= 2:
                                    # กรณีเขียนติดกัน เช่น "03000079..." ให้ตัดแบ่งทีละ 2 ตัวอักษร
                                    hex_bytes = [parts[0][i:i+2] for i in range(0, len(parts[0]), 2)]
                                else:
                                    hex_bytes = parts
                                    
                                #ส่วนข้าม set
                                if len(hex_bytes) > 0 and hex_bytes[0].upper() == "03" and loop_count > 0:
                                    print(f"Skip {name}: Set command (0x03) already executed")
                                    continue  # กระโดดไปแถวถัดไปทันที ไม่ต้องสร้างคำสั่งและไม่ต้องส่งซ้ำ
                                
                                # ตรวจสอบว่า Byte ที่ 0 (index 0) มีค่าเป็น '03' และมีค่า Value ครบถ้วน
                                if len(hex_bytes) >= 4 and hex_bytes[0].upper() == "03" and value != "-":
                                    reg_address = int(hex_bytes[2] + hex_bytes[3], 16)
                                    decimal_val = float(value)
                                    sub_mode_val = int(row.get("SubMode", 0))

                                    # เรียกใช้ build_set_command เพื่อสร้างคำสั่งใหม่
                                    generated_can_data = self.canprotocal.build_set_command(
                                        reg_address, decimal_val, sub_mode=sub_mode_val
                                    )
                                    # แปลงผลลัพธ์เป็น Hex string สำหรับส่งออก
                                    can_data = " ".join([f"{b:02X}" for b in generated_can_data])
                                    
                        except Exception as e:
                            print(
                                f"Error building set command for row {index}: {e}"
                            )
                            continue
                        
                        # ส่งข้อมูล CAN และรอรับ Response
                        response = self.canprotocal.read_once_fromgui(
                            can_id=identifier,
                            payload=can_data,
                            timeout=timeout
                        )
                        if response is not None:
                            res_id_hex, res_data_hex = response
                            print("Success!")
                        else:
                            res_id_hex = "-"
                            res_data_hex = "-"
                            print("Timeout!")
                            
                        self.loop_log.append({
                            "Time": round(time.time() - start_time, 3),
                            "Name": name,
                            "TxRx": tx_rx,
                            "Identifier": identifier,
                            "CAN Data": can_data,
                            "Response ID": res_id_hex,
                            "Response Data": res_data_hex,
                            "Value": value,
                            "Sec": sec_val,
                            "Comment": comment,
                            "Action": action,
                            "Result": result
                        })
                        time.sleep(interval)
                    loop_count += 1
            finally:
                try:
                    print("\n=== Sending shutdown command... ===")

                    response = self.canprotocal.read_once_fromgui(
                        can_id=identifier,
                        payload="03 00 00 30 00 01 00 00",
                        timeout=timeout
                    )

                    if response is not None:
                        print("Shutdown response received")
                    else:
                        print("Warning: Shutdown not confirmed")

                except Exception as shutdown_err:
                    print(f"Shutdown error: {shutdown_err}")

                finally:
                    self.is_running = False
                    self.result_df = pd.DataFrame(self.loop_log)
                    print("\n--- CAN DataFrame loop finished ---")
        thread = threading.Thread(target=_running, daemon=True)
        thread.start()
        return thread
    
    def complete_loop_read_fromgui(self,file_path=None, interval=0.1, timeout=1.0): #วนลูปทั้งไฟล์ csv และส่ง can message ตามลำดับ
            df = self.split_timeandvalue(self.readcsv_to_df(file_path))
            return self.loop_read_commands_from_df(df, interval=interval, timeout=timeout)
    #--------แก้ไข--------------------------------------------------------------------------------------------
    def save_row(self, data_dict):
        # เปิดไฟล์เพื่อสร้างหัวตาราง (Header) ไว้ตั้งแต่เริ่มต้นโปรแกรม
        with open(self.filepath, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Timestamp", "Identifier", "Data_hex", "Data_dec", "Comment"]
            )
        """ฟังก์ชันสำหรับเขียนข้อมูลลงไฟล์ CSV ทีละ 1 แถว (Append mode)"""
        with open(self.filepath, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                data_dict.get("timestamp", time.strftime("%Y-%m-%d %H:%M:%S")),
                data_dict.get("identifier", ""),
                data_dict.get("data_hex", ""),
                data_dict.get("data_dec", 0.0),
                data_dict.get("comment", ""),
            ])
        print("บันทึกข้อมูลลงไฟล์ CSV เรียบร้อยแล้วครับ!")

# ==========================================
# ตัวอย่างวิธีเรียกใช้งาน
# ==========================================
if __name__ == "__main__":

    logger = CSVLogger(r"C:\Users\nutta\OneDrive\เดสก์ท็อป\ARM\year 3.2\CAN BUS\Set and read DC Volt list.csv") #ตัวแปรของ init

    # 2. เรียกใช้งานโดยใช้ self.filepath จากตัว logger ได้เลย (เพราะอยู่ในโฟลเดอร์เดียวกัน)
    #
    #logger.readcsv_to_df()
    t = logger.complete_loop_read_fromgui(file_path=logger.filepath, interval=0.1, timeout=0.1)
    t.join()