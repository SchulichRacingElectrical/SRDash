import logging
import re
import socket
import requests
import serial
import platform
from serial.tools import list_ports
from Utilities import replace_value_with_definition, readifyData, stringMe
import datetime

class Process:

    device = None
    ser = None

    timeout = 1
    writeTimeout = 3

    INITIAL_DATA = {'timestamp': 0, 'interval': 0, 'battery': 0,
                'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                'pitch': 0, 'roll': 0, 'rpm': 0, 'map': 0,
                'tps': 0, 'oilPress': 0, 'afr': 0, 'temp': 0,
                'iat': 0, 'fts': 0, 'oilTemp': 0, 'gear': 0}
    data = {}
    def __init__(self):
        self.data = self.INITIAL_DATA
        self.device = self.connect()
        self.ser = serial.Serial(self.device,
                                 timeout=self.timeout,
                                 write_timeout=self.writeTimeout)
        self.setRate(50)

    def get_available_devices(self):
        devices = [x[0] for x in list_ports.comports()]
        devices.sort()
        return devices

    def connect(self):
        devices = self.get_available_devices()
        print(devices)
        r = None
        if platform.system() == "Darwin":
            r = re.compile(".*usb")
        elif platform.system() == "Linux":
            r = re.compile(".*ACM")

        filtered_devices = filter(r.match, devices)

        deviceToConnect = next(filtered_devices)
        print("Connected to '" + deviceToConnect + "'.")
        return deviceToConnect

    def setRate(self, rate):
        statement = '{"setTelemetry":{"rate":' + str(rate) + '}}\r\n'
        self.ser.write(statement.encode("utf-8"))

    def getLine(self):
        try:
            row = self.ser.readline()
        except serial.SerialException:
            row = None
        return row


    def parseLine(self):
        row = self.getLine()
        data = self.data
        if row is not None and b"{\"s\":{" in row:
            try:
                raw_data = stringMe(row)['s']['d']
                row_list = [datetime.datetime.now().timestamp()]
                for item in raw_data:
                    row_list.append(item)

                if len(row_list) == 6:
                    # [Timestamp, Interval, ??, TPS, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "tps", row_list[3])
                    return readifyData(data)
                elif len(row_list) == 19:
                    # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM,
                    # TPS, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "accelX", row_list[3])
                    data = replace_value_with_definition(data, "accelY", row_list[4])
                    data = replace_value_with_definition(data, "accelZ", row_list[5])
                    data = replace_value_with_definition(data, "yaw", row_list[6])
                    data = replace_value_with_definition(data, "pitch", row_list[7])
                    data = replace_value_with_definition(data, "roll", row_list[8])
                    data = replace_value_with_definition(data, "rpm", row_list[15])
                    data = replace_value_with_definition(data, "tps", row_list[16])
                    return readifyData(data)
                elif len(row_list) == 33:
                    # [Timestamp, Interval, ??, MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, ??, ??, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "map", row_list[3])
                    data = replace_value_with_definition(data, "tps", row_list[4])
                    data = replace_value_with_definition(data, "oilPress", row_list[7])
                    data = replace_value_with_definition(data, "afr", row_list[10])
                    data = replace_value_with_definition(data, "iat", row_list[11])
                    data = replace_value_with_definition(data, "fts", row_list[12])
                    return readifyData(data)
                elif len(row_list) == 48:
                    # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM,
                    # MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, Gear, idc whats left]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "accelX", row_list[3])
                    data = replace_value_with_definition(data, "accelY", row_list[4])
                    data = replace_value_with_definition(data, "accelZ", row_list[5])
                    data = replace_value_with_definition(data, "yaw", row_list[6])
                    data = replace_value_with_definition(data, "pitch", row_list[7])
                    data = replace_value_with_definition(data, "roll", row_list[8])
                    data = replace_value_with_definition(data, "rpm", row_list[15])
                    data = replace_value_with_definition(data, "map", row_list[16])
                    data = replace_value_with_definition(data, "tps", row_list[17])
                    data = replace_value_with_definition(data, "oilPress", row_list[20])
                    data = replace_value_with_definition(data, "afr", row_list[23])
                    data = replace_value_with_definition(data, "iat", row_list[24])
                    data = replace_value_with_definition(data, "fts", row_list[25])
                    data = replace_value_with_definition(data, "gear", row_list[27])
                    return readifyData(data)
                elif len(row_list) == 54:
                    # [Timestamp, Interval, ??, Battery, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "battery", row_list[3])
                    data = replace_value_with_definition(data, "accelX", row_list[4])
                    data = replace_value_with_definition(data, "accelY", row_list[5])
                    data = replace_value_with_definition(data, "accelZ", row_list[6])
                    data = replace_value_with_definition(data, "yaw", row_list[7])
                    data = replace_value_with_definition(data, "pitch", row_list[8])
                    data = replace_value_with_definition(data, "roll", row_list[9])
                    data = replace_value_with_definition(data, "rpm", row_list[18])
                    data = replace_value_with_definition(data, "map", row_list[19])
                    data = replace_value_with_definition(data, "tps", row_list[20])
                    data = replace_value_with_definition(data, "oilPress", row_list[23])
                    data = replace_value_with_definition(data, "afr", row_list[26])
                    data = replace_value_with_definition(data, "temp", row_list[27])
                    data = replace_value_with_definition(data, "iat", row_list[28])
                    data = replace_value_with_definition(data, "fts", row_list[29])
                    data = replace_value_with_definition(data, "oilTemp", row_list[30])
                    data = replace_value_with_definition(data, "gear", row_list[33])
                    return readifyData(data)

            except Exception as e:
                print(e)
            return None

    def parseLines(self):
        row = self.getLine()
        data = self.data.copy()
        if row is not None and b"{\"s\":{" in row:
            try:
                raw_data = stringMe(row)['s']['d']
                row_list = [datetime.datetime.now().timestamp()]
                for item in raw_data:
                    row_list.append(item)

                if len(row_list) == 6:
                    # [Timestamp, Interval, ??, TPS, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "tps", row_list[3])
                    # db.update(data)
                elif len(row_list) == 19:
                    # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM, TPS, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "accelX", row_list[3])
                    data = replace_value_with_definition(data, "accelY", row_list[4])
                    data = replace_value_with_definition(data, "accelZ", row_list[5])
                    data = replace_value_with_definition(data, "yaw", row_list[6])
                    data = replace_value_with_definition(data, "pitch", row_list[7])
                    data = replace_value_with_definition(data, "roll", row_list[8])
                    data = replace_value_with_definition(data, "rpm", row_list[15])
                    data = replace_value_with_definition(data, "tps", row_list[16])
                    # db.update(data)
                elif len(row_list) == 33:
                    # [Timestamp, Interval, ??, MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, ??, ??, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "map", row_list[3])
                    data = replace_value_with_definition(data, "tps", row_list[4])
                    data = replace_value_with_definition(data, "oilPress", row_list[7])
                    data = replace_value_with_definition(data, "afr", row_list[10])
                    data = replace_value_with_definition(data, "iat", row_list[11])
                    data = replace_value_with_definition(data, "fts", row_list[12])
                    # db.update(data)
                elif len(row_list) == 48:
                    # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM, MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, Gear, idc whats left]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "accelX", row_list[3])
                    data = replace_value_with_definition(data, "accelY", row_list[4])
                    data = replace_value_with_definition(data, "accelZ", row_list[5])
                    data = replace_value_with_definition(data, "yaw", row_list[6])
                    data = replace_value_with_definition(data, "pitch", row_list[7])
                    data = replace_value_with_definition(data, "roll", row_list[8])
                    data = replace_value_with_definition(data, "rpm", row_list[15])
                    data = replace_value_with_definition(data, "map", row_list[16])
                    data = replace_value_with_definition(data, "tps", row_list[17])
                    data = replace_value_with_definition(data, "oilPress", row_list[20])
                    data = replace_value_with_definition(data, "afr", row_list[23])
                    data = replace_value_with_definition(data, "iat", row_list[24])
                    data = replace_value_with_definition(data, "fts", row_list[25])
                    data = replace_value_with_definition(data, "gear", row_list[27])
                    # db.update(data)
                elif len(row_list) == 54:

                    # [Timestamp, Interval, ??, Battery, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "battery", row_list[3])
                    data = replace_value_with_definition(data, "accelX", row_list[4])
                    data = replace_value_with_definition(data, "accelY", row_list[5])
                    data = replace_value_with_definition(data, "accelZ", row_list[6])
                    data = replace_value_with_definition(data, "yaw", row_list[7])
                    data = replace_value_with_definition(data, "pitch", row_list[8])
                    data = replace_value_with_definition(data, "roll", row_list[9])
                    data = replace_value_with_definition(data, "rpm", row_list[18])
                    data = replace_value_with_definition(data, "map", row_list[19])
                    data = replace_value_with_definition(data, "tps", row_list[20])
                    data = replace_value_with_definition(data, "oilPress", row_list[23])
                    data = replace_value_with_definition(data, "afr", row_list[26])
                    data = replace_value_with_definition(data, "temp", row_list[27])
                    data = replace_value_with_definition(data, "iat", row_list[28])
                    data = replace_value_with_definition(data, "fts", row_list[29])
                    data = replace_value_with_definition(data, "oilTemp", row_list[30])
                    data = replace_value_with_definition(data, "gear", row_list[33])
                    # db.update(data)

            except Exception as e:
                print(e)
        cloudData = None
        displayData = readifyData(data)
        #print("Data: " + str(data))
        #print("Old: " + str(self.data))

        if data != self.data:
            cloudData = readifyData(data)
        self.data = data
        return displayData, cloudData
