# Importing Libraries 
import serial 
import time 
import numpy as np

arr_electrode = np.array([[1,2,3,4,5,6,7],
                          [2,3,4,5,6,7,8],
                          [3,4,5,6,7,8,9],
                          [11,12,13,14,15,16,17]]                      
                          )

arduino = serial.Serial(port='COM3', baudrate=9600, timeout=.1) 

def write_read(x): 
    arduino.write(bytes(x, 'utf-8')) 
    print(bytes(x, 'utf-8'))
    time.sleep(0.1) 
    data = arduino.readline() 
    return data 

for step in range(5):
    serial_text = f"*{arr_electrode[0, step]},{arr_electrode[1, step]},{arr_electrode[2, step]},{arr_electrode[3, step]}"
    print(serial_text)
    value = write_read(serial_text) 
    print(value) # printing the value
    time.sleep(0.5)

while True: 
    num = input("Enter a text: ") # Taking input from user 
    value = write_read(num) 
    print(value) # printing the value 
