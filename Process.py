import re

import serial
import platform
from serial.tools import list_ports
from Utilities import replace_value_with_definition, readifyData, stringMe
import datetime


CHANNEL_TYPE_UNKNOWN = 0
CHANNEL_TYPE_SENSOR = 1
CHANNEL_TYPE_IMU = 2
CHANNEL_TYPE_GPS = 3
CHANNEL_TYPE_TIME = 4
CHANNEL_TYPE_STATS = 5

class SampleMetaException(Exception):
    pass

class SampleValue(object):
    def __init__(self, value, channelMeta):
        self.value = value
        self.channelMeta = channelMeta

STARTING_BITMAP = 1

class ChannelMeta(object):
    DEFAULT_NAME = ''
    DEFAULT_UNITS = ''
    DEFAULT_MIN = 0
    DEFAULT_MAX = 100
    DEFAULT_SAMPLE_RATE = 1
    DEFAULT_PRECISION = 0
    DEFAULT_TYPE = 0

    def __init__(self, **kwargs):
        self.name = kwargs.get('name', ChannelMeta.DEFAULT_NAME)
        self.units = kwargs.get('units', ChannelMeta.DEFAULT_UNITS)
        self.min = kwargs.get('min', ChannelMeta.DEFAULT_MIN)
        self.max = kwargs.get('max', ChannelMeta.DEFAULT_MAX)
        self.precision = kwargs.get('prec', ChannelMeta.DEFAULT_PRECISION)
        self.sampleRate = kwargs.get(
            'sampleRate', ChannelMeta.DEFAULT_SAMPLE_RATE)
        self.type = kwargs.get('type', ChannelMeta.DEFAULT_TYPE)

    @staticmethod
    def filter_name(name):
        return ''.join([char for char in name if char.isalnum() or char == ' ' or char == '_'])

    def fromJson(self, json):
        self.name = json.get('nm', self.name)
        self.units = json.get('ut', self.units)
        self.min = json.get('min', self.min)
        self.max = json.get('max', self.max)
        self.precision = json.get('prec', self.precision)
        self.sampleRate = int(json.get('sr', self.sampleRate))
        self.type = int(json.get('type', self.type))


class ChannelMetaCollection(object):
    channel_metas = []

    def fromJson(self, metaJson):
        channel_metas = self.channel_metas
        del channel_metas[:]
        for ch in metaJson:
            channel_meta = ChannelMeta()
            channel_meta.fromJson(ch)
            channel_metas.append(channel_meta)

class Process:
    device = None
    ser = None
    samples = []
    timeout = 1
    metas = ChannelMetaCollection()
    writeTimeout = 3
    test_rpm = 0
    INITIAL_DATA = {'timestamp': 0, 'interval': 0, 'battery': 0,
                    'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                    'pitch': 0, 'roll': 0, 'rpm': 0, 'map': 0,
                    'tps': 0, 'oilPress': 0, 'afr': 0, 'temp': 0,
                    'iat': 0, 'fts': 0, 'oilTemp': 0, 'gear': 0}

    I_D = {'timestamp': 0, 'interval': 0, 'battery': 0,
                    'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                    'pitch': 0, 'roll': 0, 'rpm': 0, 'map': 0,
                    'tps': 0, 'oilPress': 0, 'temp': 0,
                    'iat': 0, 'fts': 0, 'oilTemp': 0, 'gear': 0, 'speed': 0,
                    'frontleft': 0, 'lambda': 0}
    data = {}

    def __init__(self):
        self.data = self.INITIAL_DATA
        self.device = self.connect()
        self.ser = serial.Serial(self.device,
                                 timeout=self.timeout,
                                 write_timeout=self.writeTimeout)
        self.updateMeta()
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

    def updateMeta(self):
        statement = '{"getMeta":null}\r\n'
        self.ser.write(statement.encode("utf-8"))
        while True:
            meta = self.getLine()
            if meta is not None and b'{"meta"' in meta:
                try:
                    raw_data = stringMe(meta)
                    self.metas = ChannelMetaCollection()
                    self.metas.fromJson(raw_data["meta"])
                except Exception as e:
                    print(e)
                finally:
                    print("Updated Channel Metadata")
                    break

    def processData(self, dataJson):
        metas = self.metas.channel_metas
        #print(metas)
        channelConfigCount = len(metas)
        bitmaskFieldCount = max(0, int((channelConfigCount - 1) / 32)) + 1

        maxFieldCount = channelConfigCount + bitmaskFieldCount

        fieldData = dataJson
        fieldDataSize = len(fieldData)
        if fieldDataSize > maxFieldCount or fieldDataSize < bitmaskFieldCount:
            raise Exception(
                'Unexpected data packet count {}; channel meta expects between {} and {} channels'.format(fieldDataSize,
                                                                                                          bitmaskFieldCount,
                                                                                                          maxFieldCount))

        bitmaskFields = []
        for i in range(fieldDataSize - bitmaskFieldCount, fieldDataSize):
            bitmaskFields.append(int(fieldData[i]))

        samples = self.samples
        del samples[:]

        channelConfigIndex = 0
        bitmapIndex = 0
        fieldIndex = 0
        mask_index = 0
        channelConfigCount = len(metas)
        while channelConfigIndex < channelConfigCount:
            if mask_index >= 32:
                mask_index = 0;
                bitmapIndex += 1
                if bitmapIndex > len(bitmaskFields):
                    print("channel count overflowed number of bitmap fields available")

            mask = 1 << mask_index
            if (bitmaskFields[bitmapIndex] & mask) != 0:
                value = float(fieldData[fieldIndex])
                fieldIndex += 1
                sample = SampleValue(value, metas[channelConfigIndex])
                samples.append(sample)
            channelConfigIndex += 1
            mask_index += 1

    def setRate(self, rate):
        statement = '{"setTelemetry":{"rate":' + str(rate) + '}}\r\n'
        self.ser.write(statement.encode("utf-8"))

    def getLine(self):
        try:
            row = self.ser.readline()
        except serial.SerialException:
            row = None
        return row

    def readifySamples(self):
        d = self.I_D
        samples = self.samples
        for sample in samples:
            sample_meta = sample.channelMeta
            if sample_meta.name.lower() == "rpm":
                d = replace_value_with_definition(d, "rpm", sample.value)
                #d = replace_value_with_definition(d, "rpm", self.test_rpm)
                # self.test_rpm = self.test_rpm + 200
                # if self.test_rpm > 13000:
                #     self.test_rpm = 0
            elif sample_meta.name.lower() == "gear":
                d = replace_value_with_definition(d, "gear", sample.value)
            elif sample_meta.name.lower() == "enginetemp":
                d = replace_value_with_definition(d, "temp", sample.value)
            elif sample_meta.name.lower() == "iat":
                d = replace_value_with_definition(d, "iat", sample.value)
            elif sample_meta.name.lower() == "speed":
                d = replace_value_with_definition(d, "speed", sample.value)
            elif sample_meta.name.lower() == "frontleft":
                d = replace_value_with_definition(d, "frontleft", sample.value)
            elif sample_meta.name.lower() == "lambda":
                d = replace_value_with_definition(d, "lambda", sample.value)
            elif sample_meta.name.lower() == "oilpressure":
                d = replace_value_with_definition(d, "oilPress", sample.value)
            elif sample_meta.name.lower() == "oiltemp":
                d = replace_value_with_definition(d, "oilTemp", sample.value)
        d = replace_value_with_definition(d, "timestamp", datetime.datetime.now().timestamp())
        data = readifyData(d)
        return data

    def getData(self):
        row = self.getLine()
        #print(row)
        if row is not None and b"{\"s\":{" in row:
            try:
                raw_data = stringMe(row)['s']['d']
                self.processData(raw_data)
            except Exception as e:
                print(e)

        display_data = self.readifySamples()
        return display_data

    def parseLines(self):
        row = self.getLine()
        data = self.data.copy()
        if row is not None and b"{\"s\":{" in row:
            try:
                raw_data = stringMe(row)['s']['d']
                print(raw_data)
                self.processData(raw_data)
                print(self.samples)
                row_list = [datetime.datetime.now().timestamp()]
                for item in raw_data:
                    row_list.append(item)
                #print(len(row_list))
                #print(row_list)
                if len(row_list) == 6:
                    # [Timestamp, Interval, ??, TPS, ??, ??]
                    # [1526765864.419865, 54071, 0, 1702, 8.1, 1539]

                    ##print(6)
                    #print(row_list)

                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    #data = replace_value_with_definition(data, "tps", row_list[3])
                    data = replace_value_with_definition(data, "rpm", row_list[3])

                    # db.update(data)
                elif len(row_list) == 16:
                    # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM, TPS, ??, ??]
                    # [1526760054.950772, 10363, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 7.68, 10, 1.52, 19, 61435]
                    # [1526760370.622412, 24403, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 5.95, 10, 1.52, 272, 61435]
                    # [1526760713.003912, 8728, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 67.5, 7.67, 10, 1.52, 20, 61435]
                    # [1526761635.890105, 27883, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 7.67, 10, 1.52, 20, 61435]
                    # [1526761635.806587, 27803, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 7.67, 10, 1.52, 20, 61435]
                    # [1526765864.532865, 54171, 0, 0.08, -0.01, -0.98, -1, 3, 1, 1687, 8.1, 4.38, 92, 6.803, 21, 61435]

                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "accelX", row_list[3])
                    data = replace_value_with_definition(data, "accelY", row_list[4])
                    data = replace_value_with_definition(data, "accelZ", row_list[5])
                    data = replace_value_with_definition(data, "yaw", row_list[6])
                    data = replace_value_with_definition(data, "pitch", row_list[7])
                    data = replace_value_with_definition(data, "roll", row_list[8])
                    data = replace_value_with_definition(data, "rpm", row_list[9])
                    data = replace_value_with_definition(data, "tps", row_list[10])
                    data = replace_value_with_definition(data, "map", row_list[12])
                    data = replace_value_with_definition(data, "afr", row_list[13])
                    data = replace_value_with_definition(data, "iat", row_list[14])

                elif len(row_list) == 20:
                    # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM, TPS, ??, ??]
                    # [1526760370.767097, 24543, 0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0, 3757966851]
                    # [1526760713.02968, 8748, 0, 0, 67.5, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0, 3757966851]
                    # [1526765864.514711, 54151, 0, 1610, 7.9, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0, 3757966851]

                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "rpm", row_list[3])
                    data = replace_value_with_definition(data, "tps", row_list[4])


                    # db.update(data)
                elif len(row_list) == 31:
                    # [Timestamp, Interval, ??, MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, ??, ??, ??, ??]
                    # [1526760371.274628, 25043, 0, 12.8, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 5.95, 70, 10, 1.52, 272,
                    # 19, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294967295]
                    # [1526760714.552279, 10248, 0, -0.02, 0.08, -0.97, -1, 3, 1,       0, 97.2, 7.67, 10, 1.52,   20,
                    # 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294897659]
                    # [1526760713.332052, 9048 , 0, 12.71,-0.02,  0.08, -0.97,-1, 3, 1, 0, 69.4, 7.67, 70,   10, 1.52, 20,
                    # 19, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294967295]
                    # [1526761635.85367, 27843, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 7.67, 10, 1.52, 20, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294897659]
                    # [1526765865.219541, 54851, 0, 0.08, -0.02, -0.97, -1, 2, 1, 1823, 6.5, 4.43, 91, 6.803, 21, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294897659]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "accelX", row_list[3])
                    data = replace_value_with_definition(data, "accelY", row_list[4])
                    data = replace_value_with_definition(data, "accelZ", row_list[5])
                    data = replace_value_with_definition(data, "yaw", row_list[6])
                    data = replace_value_with_definition(data, "pitch", row_list[7])
                    data = replace_value_with_definition(data, "roll", row_list[8])
                    data = replace_value_with_definition(data, "rpm", row_list[9])

                    data = replace_value_with_definition(data, "tps", row_list[11])
                    data = replace_value_with_definition(data, "map", row_list[14])
                    data = replace_value_with_definition(data, "afr", row_list[15])
                    data = replace_value_with_definition(data, "iat", row_list[16])
                    #data = replace_value_with_definition(data, "temp", row_list[17])

                    # db.update(data)
                elif len(row_list) == 34:
                    # [Timestamp, Interval, ??, MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, ??, ??, ??, ??]
                    # [1526761385.822547, 32043, 0, 12.4, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 7.69, 70, 10, 1.52, 20,
                    # 19, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294967295]
                    data = replace_value_with_definition(data, "timestamp", row_list[0])
                    data = replace_value_with_definition(data, "interval", row_list[1])
                    data = replace_value_with_definition(data, "battery", row_list[3])
                    data = replace_value_with_definition(data, "accelX", row_list[4])
                    data = replace_value_with_definition(data, "accelY", row_list[5])
                    data = replace_value_with_definition(data, "accelZ", row_list[6])
                    data = replace_value_with_definition(data, "yaw", row_list[7])
                    data = replace_value_with_definition(data, "pitch", row_list[8])
                    data = replace_value_with_definition(data, "roll", row_list[9])
                    data = replace_value_with_definition(data, "tps", row_list[11])
                    data = replace_value_with_definition(data, "map", row_list[14])
                    data = replace_value_with_definition(data, "afr", row_list[15])
                    data = replace_value_with_definition(data, "iat", row_list[16])
                    data = replace_value_with_definition(data, "temp", row_list[17])

                # if data["iat"] == 0:
                #     print(len(row_list))
                #     print(row_list)

                # elif len(row_list) == 48:
                #     # [Timestamp, Interval, ??, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??, ??, RPM, MAP, TPS, ??, ??, OilPress, ??, ??, AFR, IAT, FTS, ??, Gear, idc whats left]
                #     # [1526759730.619736, 8644, 0, -0.02, 0.08, -0.97, -1, 3, 1, 0, 0.0, 7.67, 10, 1.52, 19, 0.0, 0.0, 0.0, 0.0, 0, 0, 0.0, 0.0, 0, 0.0, -1, 0.0, 0.0, 0.0, 0, 4294897659]
                #     data = replace_value_with_definition(data, "timestamp", row_list[0])
                #     data = replace_value_with_definition(data, "interval", row_list[1])
                #     data = replace_value_with_definition(data, "accelX", row_list[3])
                #     data = replace_value_with_definition(data, "accelY", row_list[4])
                #     data = replace_value_with_definition(data, "accelZ", row_list[5])
                #     data = replace_value_with_definition(data, "yaw", row_list[6])
                #     data = replace_value_with_definition(data, "pitch", row_list[7])
                #     data = replace_value_with_definition(data, "roll", row_list[8])
                #     data = replace_value_with_definition(data, "rpm", row_list[15])
                #     data = replace_value_with_definition(data, "map", row_list[16])
                #     data = replace_value_with_definition(data, "tps", row_list[17])
                #     data = replace_value_with_definition(data, "oilPress", row_list[20])
                #     data = replace_value_with_definition(data, "afr", row_list[23])
                #     data = replace_value_with_definition(data, "iat", row_list[24])
                #     data = replace_value_with_definition(data, "fts", row_list[25])
                #     data = replace_value_with_definition(data, "gear", row_list[27])
                #     # db.update(data)
                # elif len(row_list) == 54:
                #
                #     # [Timestamp, Interval, ??, Battery, AccelX, AccelY, AccelZ, Yaw, Pitch, Roll, ??, ??, ??, ??, ??]
                #     data = replace_value_with_definition(data, "timestamp", row_list[0])
                #     data = replace_value_with_definition(data, "interval", row_list[1])
                #     data = replace_value_with_definition(data, "battery", row_list[3])
                #     data = replace_value_with_definition(data, "accelX", row_list[4])
                #     data = replace_value_with_definition(data, "accelY", row_list[5])
                #     data = replace_value_with_definition(data, "accelZ", row_list[6])
                #     data = replace_value_with_definition(data, "yaw", row_list[7])
                #     data = replace_value_with_definition(data, "pitch", row_list[8])
                #     data = replace_value_with_definition(data, "roll", row_list[9])
                #     data = replace_value_with_definition(data, "rpm", row_list[18])
                #     data = replace_value_with_definition(data, "map", row_list[19])
                #     data = replace_value_with_definition(data, "tps", row_list[20])
                #     data = replace_value_with_definition(data, "oilPress", row_list[23])
                #     data = replace_value_with_definition(data, "afr", row_list[26])
                #     data = replace_value_with_definition(data, "temp", row_list[27])
                #     data = replace_value_with_definition(data, "iat", row_list[28])
                #     data = replace_value_with_definition(data, "fts", row_list[29])
                #     data = replace_value_with_definition(data, "oilTemp", row_list[30])
                #     data = replace_value_with_definition(data, "gear", row_list[33])
                    # db.update(data)

            except Exception as e:
                print(e)
        cloudData = None
        displayData = readifyData(data)
        # print("Data: " + str(data))
        # print("Old: " + str(self.data))

        if data != self.data:
            cloudData = readifyData(data)
        self.data = data
        return displayData, cloudData
