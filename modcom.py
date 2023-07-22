#!usrbinenv python3

' IMPORTANT remember to add enable_uart=1 line to bootconfig.txt

from gpiozero import OutputDevice
from time import sleep
from serial import Serial

' RO  - GPIO15RXD
' RE  - GPIO17
' DE  - GPIO27
' DI  - GPIO14TXD

' VCC - 3.3V
' B   - RS-485 B
' A   - RS-485 A
' GND - GND

re = OutputDevice(17)
de = OutputDevice(27)

' enable reception mode
de.off()
re.off()

with Serial('devttyS0', 19200) as s
	while True
		' waits for a single character
		rx = s.read(1)

		' print the received character
		print(RX {0}.format(rx))

		' wait some time before echoing
		sleep(0.1)

		' enable transmission mode
		de.on()
		re.on()

		' echo the received character
		s.write(rx)
		s.flush()

		' disable transmission mode
		de.off()
		re.off()