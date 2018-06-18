import random
import re
import time

import serial
import platform
from serial.tools import list_ports
from Utilities import replace_value_with_definition, readify_data, string_me
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
    INITIAL_DATA = {'timestamp': 0, 'interval': 0, 'battery': 0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                    'pitch': 0,
                    'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0,
                    'iat': 0,
                    'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0,
                    'rearRight': 0,
                    'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelRate': 0, 'fuelUsage': 0, 'fuelTemp': 0, 'baro': 0, 'altitude': 0,
                    'session': 0, 'lambda': 0}

    I_D = {'timestamp': 0, 'interval': 0, 'battery': 0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0, 'pitch': 0,
           'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0, 'iat': 0,
           'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0, 'rearRight': 0,
           'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'fuelRate': 0, 'fuelUsage': 0, 'baro': 0,
           'altitude': 0, 'session': 0, 'lambda': 0}
    data = {}
    last_called = None
    cumulative_fuel_usage = 0
    def __init__(self):
        self.data = self.INITIAL_DATA
        self.device = self.connect()
        self.ser = serial.Serial(self.device,
                                 timeout=self.timeout,
                                 write_timeout=self.writeTimeout)
        self.last_called = time.time()
        self.updateMeta()
        self.set_rate(50)

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
            r = re.compile(".*ACM")
        else:
            r = re.compile(".*COM")

        filtered_devices = filter(r.match, devices)

        return next(filtered_devices)

    def connect(self):
        device_to_connect = self.get_device()
        print("Connected to '" + device_to_connect + "'.")
        return device_to_connect

    def updateMeta(self):
        statement = '{"getMeta":null}\r\n'
        self.ser.write(statement.encode("utf-8"))
        while True:
            meta = self.get_line()
            if meta is not None and b'{"meta"' in meta:
                try:
                    raw_data = string_me(meta)
                    self.metas = ChannelMetaCollection()
                    self.metas.fromJson(raw_data["meta"])
                except Exception as e:
                    print(e)
                finally:
                    print("Updated Channel Metadata")
                    break

    def processData(self, data_json):
        metas = self.metas.channel_metas
        # print(metas)
        channel_config_count = len(metas)
        bitmask_field_count = max(0, int((channel_config_count - 1) / 32)) + 1

        max_field_count = channel_config_count + bitmask_field_count

        field_data = data_json
        field_data_size = len(field_data)
        if field_data_size > max_field_count or field_data_size < bitmask_field_count:
            raise Exception(
                'Unexpected data packet count {}; channel meta expects between {} and {} channels'.format(field_data_size,
                                                                                                          bitmask_field_count,
                                                                                                          max_field_count))

        bitmask_fields = []
        for i in range(field_data_size - bitmask_field_count, field_data_size):
            bitmask_fields.append(int(field_data[i]))

        samples = self.samples
        del samples[:]

        channel_config_index = 0
        bitmap_index = 0
        field_index = 0
        mask_index = 0
        channel_config_count = len(metas)
        while channel_config_index < channel_config_count:
            if mask_index >= 32:
                mask_index = 0
                bitmap_index += 1
                if bitmap_index > len(bitmask_fields):
                    print("channel count overflowed number of bitmap fields available")

            mask = 1 << mask_index
            if (bitmask_fields[bitmap_index] & mask) != 0:
                value = float(field_data[field_index])
                field_index += 1
                sample = SampleValue(value, metas[channel_config_index])
                samples.append(sample)
            channel_config_index += 1
            mask_index += 1

    def set_rate(self, rate):
        statement = '{"setTelemetry":{"rate":' + str(rate) + '}}\r\n'
        self.ser.write(statement.encode("utf-8"))

    def get_line(self):
        try:
            row = self.ser.readline()
        except serial.SerialException:
            row = None
        return row

    def readify_samples(self):
        d = self.I_D
        samples = self.samples
        for sample in samples:
            sample_meta = sample.channelMeta

            if sample_meta.name.lower() == "rpm":
                # self.test_rpm = self.test_rpm + 100
                # if self.test_rpm >= 12500:
                #     self.test_rpm = 0
                #self.test_rpm = random.randint(1, 12500)
                d = replace_value_with_definition(d, "rpm", sample.value)
                #d = replace_value_with_definition(d, "rpm", 1337)
            elif sample_meta.name.lower() == "gear":
                d = replace_value_with_definition(d, "gear", sample.value)
            elif sample_meta.name.lower() == "enginetemp":
                d = replace_value_with_definition(d, "coolantTemperature", sample.value)
            elif sample_meta.name.lower() == "iat":
                d = replace_value_with_definition(d, "iat", sample.value)
            elif sample_meta.name.lower() == "accelx":
                d = replace_value_with_definition(d, "accelX", sample.value)
            elif sample_meta.name.lower() == "accely":
                d = replace_value_with_definition(d, "accelY", sample.value)
            elif sample_meta.name.lower() == "accelz":
                d = replace_value_with_definition(d, "accelZ", sample.value)
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
            elif sample_meta.name.lower() == "fueltemp":
                d = replace_value_with_definition(d, "fuelTemp", sample.value)
            elif sample_meta.name.lower() == "fuelrate":
                d = replace_value_with_definition(d, "fuelRate", sample.value)

            elif sample_meta.name.lower() == "tps":
                d = replace_value_with_definition(d, "tps", sample.value)
        # Add timestamp
        d = replace_value_with_definition(d, "timestamp", datetime.datetime.now().timestamp())
        # Convert into JSON Object and convert into bytes
        data = self.calculate_fuel_usage(d)
        data = readify_data(data)
        return data

    def get_data(self):
        row = self.get_line()
        if row is not None and b"{\"s\":{" in row:
            try:
                raw_data = string_me(row)['s']['d']
                self.processData(raw_data)
            except Exception as e:
                print(e)

        display_data = self.readify_samples()
        return display_data

    def calculate_fuel_usage(self, data):
        time_elapsed = time.time() - self.last_called
        self.last_called = time.time()
        correction = 1
        x = ((correction * (data["injectorPW"] - 0.5) * data["rpm"]) / 120)
        self.cumulative_fuel_usage = (self.cumulative_fuel_usage + x * (time_elapsed / 60 / 1000))
        data = replace_value_with_definition(data, "fuelRate", x)

        data = replace_value_with_definition(data, "fuelUsage", self.cumulative_fuel_usage)
        return data
