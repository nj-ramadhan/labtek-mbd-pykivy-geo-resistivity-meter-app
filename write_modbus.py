import minimalmodbus
import time
import numpy as np

instrument = minimalmodbus.Instrument('COM5', 1)  # port name, slave address (in decimal)

values = [0,0,0,0,0,0,0]
## Read temperature (PV = ProcessValue) ##
def relay(number, states):
    # instrument.write_register(80+int(number), int(state))
    instrument.write_registers(80+int(number), states)

relay(0, values)