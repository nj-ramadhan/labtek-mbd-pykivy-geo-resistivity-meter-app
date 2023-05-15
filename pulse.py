import sys
import time
import RPi.GPIO as GPIO

mode=GPIO.getmode()

GPIO.cleanup()

Forward=33
Backward=36
sleeptime=1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Forward,  GPIO.OUT)
GPIO.setup(Backward, GPIO.OUT)

def forward(x):
    GPIO.output(Forward, GPIO.HIGH)
    print("Forward")
    time.sleep(x)
    GPIO.output(Forward, GPIO.LOW)

def reverse(x):
    GPIO.output(Backward, GPIO.HIGH)
    print("Backward")
    time.sleep(x)
    GPIO.output(Backward, GPIO.LOW)

def stop(x):
    GPIO.output(Forward, GPIO.LOW)
    GPIO.output(Backward, GPIO.LOW)
    print("Stop")
    time.sleep(x)

while(1):
    forward(5)    
    stop(1)
    reverse(5)
    stop(1)
