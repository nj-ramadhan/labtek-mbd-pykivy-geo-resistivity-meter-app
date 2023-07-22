https://microdigisoft.com/rs-485-serial-communication-between-raspberry-pi-and-arduino-uno/


import time
import serial
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT, initial=GPIO.HIGH) // Make DE  RE pin high the write a values.

send = serial.Serial(
    port='/dev/serial0',
    baudrate = 9600,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

i = [0,10,45,90,135,180,225,255,225,180,135,90,45,10,0]

while True:
 for x in i:
     send.write(bytes(x))
     print(x)
     time.sleep(1.5)
