#!/usr/bin/python3
import serial
import time

#The following line is for serial over GPIO
ard = serial.Serial(port='COM3', baudrate=9600, timeout=.1)

while (True):
    # Serial write section

    code_stop = 0
    code_fwd = 1
    code_rev = 2
    code_volt = 3
    code_curr = 4
    ard.flush()
    write_stop = str(code_stop).encode("utf-8")
    write_forward = str(code_fwd).encode("utf-8")
    write_reverse = str(code_rev).encode("utf-8")
    read_volt = str(code_volt).encode("utf-8")
    read_curr = str(code_curr).encode("utf-8")

    ard.write(write_forward)
    print ("Python sent: ", write_forward)
    time.sleep(1)

    ard.write(write_stop)
    print ("Python sent: ", write_stop)
    time.sleep(1)

    ard.write(write_reverse)
    print ("Python sent: ", write_reverse)
    time.sleep(1)
    
    ard.write(write_stop)
    print ("Python sent: ", write_stop)
    time.sleep(1)

    ard.write(read_volt)
    print ("Python sent: ", read_volt)
    time.sleep(0.2)
    msg = ard.read(ard.inWaiting()).decode("utf-8") # read all characters in buffer
    # msg = ard.read().decode("utf-8")
    print ("Volt value: ")
    print (msg)
    time.sleep(1)

    ard.write(read_curr)
    print ("Python sent: ", read_curr)
    time.sleep(0.2)
    msg = ard.read(ard.inWaiting()).decode("utf-8") # read all characters in buffer
    # msg = ard.read().decode("utf-8")
    print ("Current value: ")
    print (msg)
