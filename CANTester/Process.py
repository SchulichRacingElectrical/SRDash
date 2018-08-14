import serial
import platform
from serial.tools import list_ports
import re


class Process:

    timeout = 1
    writeTimeout = 3
    ser = None
    device = None

    def __init__(self):
        self.device = self.connect()
        self.ser = serial.Serial(self.device, timeout=None, baudrate=115200)

    def get_available_devices(self):
        devices = [x[0] for x in list_ports.comports()]
        devices.sort()
        return devices

    def get_device(self):
        devices = self.get_available_devices()
        print(devices)
        r = None
        if platform.system() == "Darwin":
            r = re.compile(".*usb")
        elif platform.system() == "Linux":
            r = re.compile(".*USB")
        else:
            r = re.compile(".*COM")

        filtered_devices = filter(r.match, devices)

        return next(filtered_devices)

    def connect(self):
        device_to_connect = self.get_device()
        print("Connected to '" + device_to_connect + "'.")
        return device_to_connect

    def get_line(self):
        try:
            row = self.ser.readline()
        except serial.SerialException:
            row = None
        return row

    def get_data(self):
        row = self.get_line()
        if row is not None:
            try:

                self.process_data(row)
                return(row)
            except Exception as e:
                print(e)

    def process_data(self, row):
        dict = {}
        row_array = row.split(",")
        for entry in row_array:
            if entry != "\n":
                pair = entry.split(":")
                dict[pair[0]] = pair[1]
        return dict


if __name__ == '__main__':
    p = Process()
    while True:
        p.get_line()
# "b'rpm:2000,tps:50, fuel open time:25,ignition angle:-20,\n'"
