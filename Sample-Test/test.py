import serial
from serial import SerialException
from serial.tools import list_ports

import sys
import glob
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    ports = ['COM%s' % (i + 1) for i in range(256)]
    

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


print(serial_ports())

def get_available_devices():
      #Logger.debug("SerialConnection: getting available devices")
      devices = [x[0] for x in list_ports.comports()]
      devices.sort()
      filtered_devices = filter(lambda device: not device.startswith('/dev/ttyUSB') and not device.startswith('/dev/ttyS') and not device.startswith('/dev/cu.Bluetooth-Incoming-Port'), devices)
      return filtered_devices
