from pathlib import Path
DISK_ADDRESS = Path("/media/pi/RESDONGLE")
SERIAL_NUMBER = "2301212112233412"

serial_file = str(DISK_ADDRESS) + "/serial.key"
print(serial_file)
with open(serial_file,"r") as f:
    serial_number = f.readline()
    if serial_number == SERIAL_NUMBER:
        print("success, serial number is valid")
    else:
        print("fail, serial number is invalid")
