import can
import sys
import os
import numpy as np
import pandas as pd
import time
class Charger:
	def __init__(self):
		self.id_bin = []
		self.History_log = pd.DataFrame(columns=['Name', 'ID_display', 'Data_display', 'Comment'])
	#display
		self.number = ""
		self.ID_display = ""
		self.Data_display = ""
		self.Comment = ""
	#response
		self.error = "0x00"
		self.device_number = "0x00"
		self.Command_number = "0x00"
		self.Target_ads = "0x00"
		self.Source_ads = "0x00"
		
		self.voltageDC_display = "0 V"
		
	def res_update(self,number,message_id,message_data,comment):#message_id,message_data form  can.Message format
		ID_binary = f"{message_id:032b}" # 0 fill 0 before, 32 bit , binary
		ID_binary_list = list(ID_binary)
		self.id_bin = ID_binary_list
	#number
		self.number = f"res{number}"
	#comment
		self.Comment = comment
	#error code
		error_dec = int("".join(self.id_bin[3:6]), 2) #(3,4,5) is 28-26 in datasheet binary to dec
		self.error = f"0x{error_dec:02X}" #0 before 2 bits upper
	#device number
		device_num = int("".join(self.id_bin[6:10]), 2) #(6,7,8,9) is 25-22 in datasheet binary to dec
		self.device_number = f"0x{device_num:02X}" #0 before 2 bits upper
	#Command number
		command_num = int("".join(self.id_bin[10:16]), 2) #(10,11,12,13,14,15) is 21-16 in datasheet binary to dec
		self.Command_number = f"0x{command_num:02X}" #0 before 2 bits upper
	#target address
		target_bin = int("".join(self.id_bin[16:24]), 2) #(16-23) is 15-8 in datasheet binary to dec
		self.Target_ads = f"0x{target_bin:02X}" #0 before 2 bits upper
	#Source address
		source_bin = int("".join(self.id_bin[24:32]), 2) #(24-32) is 7-0 in datasheet binary to dec
		self.Source_ads = f"0x{source_bin:02X}" #0 before 2 bits upper
	#ID display
		ID_padded = f"{message_id:08X}"
		self.ID_display = " ".join([f"{ID_padded}"[i:i+2] for i in range(0,8,2)]) # i is start ,i+2 is stop of slicing(don't count itself i+2) , loop i for slicing (start at 0 , stop less than 8(don't count itself 8) , step +2) 0 2 4 6
	#Data display
		data_byte_list = message_data.hex(' ').split() #Formats the binary into a hex string with spaces, Breaks the string into a List of strings
		self.Data_display = " ".join(data_byte_list).upper() #merge list with " " space
	#Data decode 4 byte
		value_hex = "".join(data_byte_list[4:8]) #merge list with " " space
	#voltage dc side
		value_dec = int(value_hex,16)
		value_voltage = value_dec /1000
		self.voltageDC_display = f"{value_voltage} V"
	#----------------------
	def Print(self):
		print("-"*40)
		print(f"	Number = {self.number}")
		print(f"	ID_display = {self.ID_display}")
		print(f"	Data_display = {self.Data_display}")	
		print(f"	Comment = {self.Comment}")	
		print(f"	error = {self.error}")	
		print(f"	device_number = {self.device_number}")	
		print(f"	Command_number = {self.Command_number}")	
		print(f"	Target_ads = {self.Target_ads}")	
		print(f"	Source_ads = {self.Source_ads}")	
		print(f"	voltageDC_display = {self.voltageDC_display}")	
		print("-"*40)
		print(*self.History_log, sep='\n') # * for unpack, use \n between object
		print("-"*100)
	#--------------------------------------------	
		
	def Build_list(self,number,message_id,message_data,comment): # receive can format in str
		message_id_hex = int(message_id, 16)
		message_data_list = [int(x, 16) for x in message_data.split()]
		request_message = can.Message(arbitration_id=message_id_hex, data=message_data_list, is_extended_id=True) #format
		#ID req dispaly
		ID_padded = f"{request_message.arbitration_id:08X}"
		ID_req = " ".join([f"{ID_padded}"[i:i+2] for i in range(0,8,2)])
		#Data req dispaly
		data_byte_list = request_message.data.hex(' ').split() 
		Data_req = " ".join(data_byte_list).upper()
		
		self.res_update(number,request_message.arbitration_id,request_message.data,comment)
		log_entry_req = [number,ID_req,Data_req,"-",comment]
		log_entry_res = [self.number,self.ID_display,self.Data_display,self.voltageDC_display,self.Comment]
		new_req = pd.DataFrame({
					'Name': [log_entry_req[0]],
					'ID_display': [log_entry_req[1]],
					'Data_display': [log_entry_req[2]],
					'Comment': [log_entry_req[4]]
					})
		new_res = pd.DataFrame({
					'Name': [log_entry_res[0]],
					'ID_display': [log_entry_res[1]],
					'Data_display': [log_entry_res[2]],
					'Comment': [log_entry_res[4]]
					})			
		self.History_log = pd.concat([self.History_log, new_req], ignore_index=True)
		self.History_log = pd.concat([self.History_log, new_res], ignore_index=True)

		#print(*self.History_log, sep='\n') # * for unpack, use \n between object
		print(self.History_log)
		print("Build Suscess!")
		print("-"*30)
		
	def Update_res(self,number,message_id,message_data,comment): #use req number (0, 1, ...)
		self.res_update(number,message_id,message_data,comment)
		log_entry = [number,self.ID_display,self.Command_number,self.voltageDC_display,self.Comment]
		for index, log in enumerate(self.History_log):
			if log[0] == f"res{number}":
				self.History_log[index] = log_entry 
				break
		else:
			print("Please Create First")
	#--------------------------------------------
	#final	
	def request_mode(self,number): #message_id,message_data form  can.Message format
		for index,log in enumerate(self.History_log):
			if log[0] == number :
				message_id_str = log[1]
				message_data_str = log[2]
				comment = log[4]
				break
			else:
				print("Not found!")
				return
		try:
			target_id = int(message_id_str.replace(" ", ""), 16)
			target_data = [int(x, 16) for x in message_data_str.split()]
			request_message = can.Message(arbitration_id=target_id, data=target_data, is_extended_id=True)
			bus.send(request_message)
			print(f"-> Sent Request: Number={number} ID={hex(request_message.arbitration_id)} Data={list(request_message.data)} Comment={comment}")
			self.Print()
			
			response_message = bus.recv(timeout=1.0)
			if response_message:
				print(f"<- Response Received")
				print(f"   ID: {hex(response_message.arbitration_id)}")
				print(f"   Data (List): {list(response_message.data)}")
				print(f"   Data (Hex):  {response_message.data.hex().upper()}")
				print(f"   DLC: {response_message.dlc}")  #length
				self.Update_res(number,response_message.arbitration_id,response_message.data,comment)
				self.Print()
			else: 
				print("Not response!")
		except ValueError:
			print("Error: Invalid Hex format (Ensure characters are in pairs, e.g., 'AA')")
		except KeyboardInterrupt:
			print("\n Stopping operation...")
				
				
def start_can():
	print("reset can.....")
	os.system("sudo ip link set can0 down")
	os.system("sudo ip link set can0 up type can bitrate 250000")
	print("set up can0,can1 done!")	

def test_interleaved_loop(bus, charger, cmd_id_hex, cmd_reg_hex, cmd_val_hex, duration_sec, interval_sec=0.1):
    """
    :bus: can.Bus instance
    :charger: Initialized Charger class
    :cmd_id_hex: Arbitration ID as hex string or int (e.g., '0x02A43FF0' or '0x0C200780')
    :cmd_reg_hex: Register address as hex string or int (e.g., '0x0077', '0077', or 0x0077)
    :cmd_val_hex: 4-byte raw hex value (e.g., '0x0007A120', '00 07 A1 20', or 0x0007A120)
    :duration_sec: Total duration to loop in seconds
    :interval_sec: Transmission period (default 0.1s / 100ms)
    """
    # 1. Parse CAN ID
    tx_id = int(cmd_id_hex, 16) if isinstance(cmd_id_hex, str) else int(cmd_id_hex)

    # 2. Parse 2-byte Register
    if isinstance(cmd_reg_hex, str):
        clean_reg = cmd_reg_hex.replace("0x", "").replace(" ", "")
        reg_bytes = bytes.fromhex(clean_reg.zfill(4))
    else:
        reg_bytes = cmd_reg_hex.to_bytes(2, byteorder='big')

    # 3. Parse 4-byte Data Value directly as Raw Hex
    if isinstance(cmd_val_hex, str):
        clean_val = cmd_val_hex.replace("0x", "").replace(" ", "")
        val_bytes = bytes.fromhex(clean_val.zfill(8))
    else:
        val_bytes = cmd_val_hex.to_bytes(4, byteorder='big')

    # Build 8-byte write command payload: [0x03, 0x00, RegH, RegL, Val0, Val1, Val2, Val3]
    cmd_data = bytearray([0x03, 0x00]) + bytearray(reg_bytes) + bytearray(val_bytes)
    cmd_msg = can.Message(arbitration_id=tx_id, data=cmd_data, is_extended_id=True)

    # Query command to read DC voltage and current (Reg 0x000F)
    query_data = [0x10, 0x00, 0x00, 0x0F, 0x00, 0x00, 0x00, 0x00]
    query_msg = can.Message(arbitration_id=0x02A33FF0, data=query_data, is_extended_id=True)

    start_time = time.time()
    end_time = start_time + duration_sec
    print(f"Loop running for {duration_sec}s | CMD Frame: ID={hex(tx_id)} Data={cmd_msg.data.hex(' ').upper()}")

    try:
        while time.time() < end_time:
            cycle_start = time.time()

            # Transmit Keep-Alive / Control Command
            bus.send(cmd_msg)

            # Transmit Telemetry Query
            bus.send(query_msg)

            # Receive and decode all incoming frames inside this interval window
            while True:
                time_left = (cycle_start + interval_sec) - time.time()
                if time_left <= 0:
                    break

                rx_msg = bus.recv(timeout=time_left)
                if rx_msg is None:
                    break

                # 0x42 indicates an integer telemetry response frame from the module
                if len(rx_msg.data) >= 8 and rx_msg.data[0] == 0x42:
                    charger.res_update("live", rx_msg.arbitration_id, rx_msg.data, "Live Poll")
                    elapsed = time.time() - start_time
                    print(f"[{elapsed:6.2f}s] DC Voltage: {charger.voltageDC_display} | Error: {charger.error}")

            # Keep consistent cadence
            elapsed_cycle = time.time() - cycle_start
            remaining = interval_sec - elapsed_cycle
            if remaining > 0:
                time.sleep(remaining)

    except KeyboardInterrupt:
        print("\nStopped early by user.")
    finally:
        print("Loop finished.\n")
			
if __name__ == "__main__":
	try:
		try:
			bus = can.interface.Bus('test_channel', interface='virtual') # for virtual test 
			#bus = can.interface.Bus(channel='can0', bustype='socketcan') # for test in lab
		except OSError:
			print("Error: can't open can bus")
		Mycharger = Charger()
		#Arm
		"""
		Mycharger.Build_list("0","0x02A33FF0", "10 01 00 00 00 00 00 00", "Read system voltage on DC side")
		Mycharger.request_mode("0")
		"""
		#loop test function
		test_interleaved_loop(bus=bus,charger=Mycharger,
            cmd_id_hex="0x02A43FF0",
            cmd_reg_hex="0x0077",
            cmd_val_hex="0x0007A120",
            duration_sec=10.0,
            interval_sec=0.1
        )
	finally:
		if 'bus' in locals():
			bus.shutdown()
			print("bus shut down.")
