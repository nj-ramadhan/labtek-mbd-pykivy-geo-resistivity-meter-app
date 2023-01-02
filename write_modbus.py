import minimalmodbus
import time
import numpy as np

instrument = minimalmodbus.Instrument('COM5', 1)  # port name, slave address (in decimal)

values = [0,0,0,0,0,0,0]
## Read temperature (PV = ProcessValue) ##

class rtu():
    def __init__(self):
        super().__init__()


    def relay(number, states):
        # instrument.write_register(80+int(number), int(state))
        instrument.write_registers(80+int(number), states)



if __name__ == '__main__':
    relay = rtu.relay
    relay(0, values)