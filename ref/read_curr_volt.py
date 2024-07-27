import serial
import numpy as np
import time

DEBUG = False

BAUDRATE = 9600
BYTESIZE = 8
PARITY = serial.PARITY_NONE
STOPBIT = 1
TIMEOUT = 1

dt_current = np.zeros(10)
dt_voltage = np.zeros(10)

serial_obj = serial.Serial("COM8")  # COM to Microcontroller, checked manually
serial_obj.baudrate = BAUDRATE
serial_obj.parity = PARITY
serial_obj.bytesize = BYTESIZE
serial_obj.stopbits = STOPBIT
serial_obj.timeout = TIMEOUT

while(1): 
    time.sleep(0.1)
    dt_voltage_temp = np.zeros_like(dt_voltage)
    dt_current_temp = np.zeros_like(dt_current)

    print("read current and voltage")
    if (not DEBUG):
        try:
            serial_obj.write(b"a")
            data_current = serial_obj.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
            print("data curr from serial", data_current)
            if data_current != "":
                curr = float(data_current)
                realtime_current = curr
            else:
                realtime_current = np.random.randint(0, 500)
            # print("Realtime Curr:", realtime_current)
            dt_current_temp[:1] = realtime_current
        except Exception as e:
            print("Error read Current", e)
        
        try:
            serial_obj.write(b"v")
            data_millivoltage = serial_obj.readline().decode("utf-8").strip()  # read the incoming data and remove newline character
            print("data volt from serial", data_millivoltage)
            if data_millivoltage != "":
                millivolt = float(data_millivoltage)
                volt = millivolt / 1000
                realtime_voltage = volt
            else:
                realtime_voltage = np.random.randint(0, 200)
            # print("Realtime Volt:", realtime_voltage)
            dt_voltage_temp[:1] = realtime_voltage
        except Exception as e:
            print("Error read voltage", e)

    dt_voltage_temp[1:] = dt_voltage[:-1]
    dt_voltage = dt_voltage_temp

    dt_current_temp[1:] = dt_current[:-1]
    dt_current = dt_current_temp       

    print("Data Volt:", dt_voltage, "Data Curr:", dt_current)

                
