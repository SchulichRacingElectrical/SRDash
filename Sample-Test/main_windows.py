import serial



device = "COM5"
#print(device)
ser = serial.Serial(device, 2000000, timeout=2, xonxoff=False, rtscts=False, dsrdtr=False) #Tried with and without the last 3 parameters, and also at 1Mbps, same happens.
ser.flushInput()
ser.flushOutput()
while True:
    bytesToRead = ser.inWaiting()
    x = ser.read(bytesToRead)
    if (len(x) > 0):
        print(x)


#con = serial.Serial(filtered_devices[7], timeout=10, write_timeout=10)

#print(read_line(con))
#filtered_devices[7]
