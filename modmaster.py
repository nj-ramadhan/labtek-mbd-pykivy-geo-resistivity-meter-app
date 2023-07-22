#https://microdigisoft.com/rs-485-serial-communication-between-raspberry-pi-and-arduino-uno/


import time
import serial
import RPi.GPIO as GPIO
from time import sleep

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.OUT, initial=GPIO.HIGH) # Make DE  RE pin high the write a values.
GPIO.setup(27, GPIO.OUT, initial=GPIO.HIGH)

send = serial.Serial(
    port='/dev/S0',
    baudrate = 19200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

i = [0,10,45,90,135,180,225,255,225,180,135,90,45,10,0]

while True:
 for x in i:
     send.write(bytes(x))
     print(x)
     time.sleep(1.5)
