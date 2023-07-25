#!/usr/bin/env python3
import minimalmodbus
import serial

BAUDRATE = 19200
BYTESIZE = 8
PARITY = serial.PARITY_NONE
STOPBIT = 2
TIMEOUT = 0.05

rtu1 = minimalmodbus.Instrument('COM4', 1 ,mode=minimalmodbus.MODE_RTU)
rtu2 = minimalmodbus.Instrument('COM4', 2 ,mode=minimalmodbus.MODE_RTU)
rtu3 = minimalmodbus.Instrument('COM4', 3 ,mode=minimalmodbus.MODE_RTU)
rtu4 = minimalmodbus.Instrument('COM4', 4 ,mode=minimalmodbus.MODE_RTU)
rtu5 = minimalmodbus.Instrument('COM4', 5 ,mode=minimalmodbus.MODE_RTU)
rtu6 = minimalmodbus.Instrument('COM4', 6 ,mode=minimalmodbus.MODE_RTU)

# rtu1.serial.stopbits = rtu2.serial.stopbits = rtu3.serial.stopbits = rtu4.serial.stopbits = rtu5.serial.stopbits = rtu6.serial.stopbits = STOPBIT
# rtu1.serial.baudrate = rtu2.serial.baudrate = rtu3.serial.baudrate = rtu4.serial.baudrate = rtu5.serial.baudrate = rtu6.serial.baudrate = BAUDRATE
# rtu1.serial.bytesize = rtu2.serial.bytesize = rtu3.serial.bytesize = rtu4.serial.bytesize = rtu5.serial.bytesize = rtu6.serial.bytesize = BYTESIZE
# rtu1.serial.parity = rtu2.serial.parity = rtu3.serial.parity = rtu4.serial.parity = rtu5.serial.parity = rtu6.serial.parity = PARITY
# rtu1.serial.stopbits = rtu2.serial.stopbits = rtu3.serial.stopbits = rtu4.serial.stopbits = rtu5.serial.stopbits = rtu6.serial.stopbits = STOPBIT

data1 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
data2 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
data3 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
data4 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
data5 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
data6 = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

rtu1.write_bits(80, data1) 
rtu2.write_bits(80, data2) 
rtu3.write_bits(80, data3) 
rtu4.write_bits(80, data4) 
rtu5.write_bits(80, data5) 
rtu6.write_bits(80, data6) 

rtu1.serial.close()
rtu2.serial.close()
rtu3.serial.close()
rtu4.serial.close()
rtu5.serial.close()
rtu6.serial.close()