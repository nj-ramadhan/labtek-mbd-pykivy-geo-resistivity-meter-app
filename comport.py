import serial
import minimalmodbus
import numpy as np
from serial.tools import list_ports

data_rtu1 = np.zeros(36, dtype=int)
# data_rtu1 = np.random.randint(2, size=36)
data_rtu2 = np.zeros(36, dtype=int)
data_rtu3 = np.zeros(36, dtype=int)
data_rtu4 = np.zeros(36, dtype=int)
data_rtu5 = np.zeros(36, dtype=int)
data_rtu6 = np.zeros(36, dtype=int)

# try:
ports = list_ports.comports(include_links=False)
for port in ports :
    com_port = port.device
    print("switching box is connected to " + com_port)

rtu1 = minimalmodbus.Instrument(com_port, 1 ,mode=minimalmodbus.MODE_RTU)
rtu2 = minimalmodbus.Instrument(com_port, 2 ,mode=minimalmodbus.MODE_RTU)
rtu3 = minimalmodbus.Instrument(com_port, 3 ,mode=minimalmodbus.MODE_RTU)
rtu4 = minimalmodbus.Instrument(com_port, 4 ,mode=minimalmodbus.MODE_RTU)
rtu5 = minimalmodbus.Instrument(com_port, 5 ,mode=minimalmodbus.MODE_RTU)
rtu6 = minimalmodbus.Instrument(com_port, 6 ,mode=minimalmodbus.MODE_RTU)

rtu1.write_bits(80, data_rtu1.tolist()) 
rtu2.write_bits(80, data_rtu2.tolist()) 
rtu3.write_bits(80, data_rtu3.tolist()) 
rtu4.write_bits(80, data_rtu4.tolist()) 
rtu5.write_bits(80, data_rtu5.tolist()) 
rtu6.write_bits(80, data_rtu6.tolist()) 
# except:
#     toast("no switching box connected")
#     print("no switching box connected")