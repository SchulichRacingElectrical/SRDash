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
    INITIAL_DATA = {'timestamp': 0, 'interval': 0, 'battery': 0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0, 'pitch': 0,
           'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0, 'iat': 0,
           'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0, 'rearRight': 0,
           'latitude': 0,  'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'baro': 0, 'altitude': 0, 'session': 0, 'lambda': 0}

    I_D = {'timestamp': 0, 'interval': 0, 'battery': 0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0, 'pitch': 0,
           'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0, 'iat': 0,
           'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0, 'rearRight': 0,
           'latitude': 0,  'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'baro': 0, 'altitude': 0, 'session': 0, 'lambda': 0}
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
            # {'timestamp': 0, 'interval': 0, 'battery': 0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0, 'pitch': 0,
            #  'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0, 'iat': 0,
            #  'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0, 'rearRight': 0,
            #  'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'baro': 0, 'altitude': 0, 'session': 0}

            if sample_meta.name.lower() == "rpm":
                d = replace_value_with_definition(d, "rpm", sample.value)
                #d = replace_value_with_definition(d, "rpm", self.test_rpm)
                # self.test_rpm = self.test_rpm + 200
                # if self.test_rpm > 13000:
                #     self.test_rpm = 0
            elif sample_meta.name.lower() == "gear":
                d = replace_value_with_definition(d, "gear", sample.value)
            elif sample_meta.name.lower() == "enginetemp":
                d = replace_value_with_definition(d, "coolantTemperature", sample.value)
            elif sample_meta.name.lower() == "iat":
                d = replace_value_with_definition(d, "iat", sample.value)
            elif sample_meta.name.lower() == "accelx":
                d = replace_value_with_definition(d, "accelX", sample.value)
            elif sample_meta.name.lower() == "accely":
                d = replace_value_with_definition(d, "accely", sample.value)
            elif sample_meta.name.lower() == "accelz":
                d = replace_value_with_definition(d, "accelz", sample.value)
            elif sample_meta.name.lower() == "yaw":
                d = replace_value_with_definition(d, "yaw", sample.value)
            elif sample_meta.name.lower() == "pitch":
                d = replace_value_with_definition(d, "pitch", sample.value)
            elif sample_meta.name.lower() == "latitude":
                d = replace_value_with_definition(d, "latitude", sample.value)
            elif sample_meta.name.lower() == "longitude":
                d = replace_value_with_definition(d, "longitude", sample.value)
            elif sample_meta.name.lower() == "altitude":
                d = replace_value_with_definition(d, "altitude", sample.value)
            elif sample_meta.name.lower() == "baro":
                d = replace_value_with_definition(d, "baro", sample.value)
            elif sample_meta.name.lower() == "altitude":
                d = replace_value_with_definition(d, "altitude", sample.value)
            elif sample_meta.name.lower() == "map":
                d = replace_value_with_definition(d, "map", sample.value)
            elif sample_meta.name.lower() == "injectorpw":
                d = replace_value_with_definition(d, "injectorPW", sample.value)
            elif sample_meta.name.lower() == "roll":
                d = replace_value_with_definition(d, "roll", sample.value)
            elif sample_meta.name.lower() == "frontleft":
                d = replace_value_with_definition(d, "frontLeft", sample.value)
            elif sample_meta.name.lower() == "frontright":
                d = replace_value_with_definition(d, "frontRight", sample.value)
            elif sample_meta.name.lower() == "rearright":
                d = replace_value_with_definition(d, "rearRight", sample.value)
            elif sample_meta.name.lower() == "rearleft":
                d = replace_value_with_definition(d, "rearLeft", sample.value)
            elif sample_meta.name.lower() == "afr":
                d = replace_value_with_definition(d, "afr", sample.value)
            elif sample_meta.name.lower() == "oilpressure":
                d = replace_value_with_definition(d, "oilPressure", sample.value)
            elif sample_meta.name.lower() == "oiltemp":
                d = replace_value_with_definition(d, "oilTemperature", sample.value)
            elif sample_meta.name.lower() == "battery":
                d = replace_value_with_definition(d, "battery", sample.value)
        d = replace_value_with_definition(d, "timestamp", datetime.datetime.now().timestamp())
        data = readifyData(d)
        #print(data)
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
