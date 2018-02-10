import collections
import datetime
import json
import logging
import re
import time

import requests
import serial

from serial.tools import list_ports

PUB_ENDPOINT = 'http://localhost:8081/pub'
STATS_CHANNEL = 'system_stats'

SystemInfo = collections.namedtuple(
    'SystemInfo',
    ['measurement_date', 'x', 'y'])



def get_available_devices():
    devices = [x[0] for x in list_ports.comports()]
    devices.sort()
    return devices







# def top(sort_by='cpu_percent', top_n_procs=15):
#     """
#     A function that simulates the unix top command
#     :return:
#     """
#     logger = logging.getLogger('PYTOP')
#     #db = Database()
#
#     return SystemInfo(
#         measurement_date=db.get_top()[0][0],
#         x=db.get_top()[0][1],
#         y=db.get_top()[0][2]
#     )



def main():
    # create a session to enable persistent http connection
    s = requests.Session()

    logger = logging.getLogger('PYTOP')
    filtered_devices = get_available_devices()
    # print(filtered_devices)
    r = re.compile(".*usbmodem")
    filtered_devices = filter(r.match, filtered_devices)

    device = next(filtered_devices)
    print("Connected to '" + device + "'.")

    DEFAULT_WRITE_TIMEOUT = 3
    DEFAULT_READ_TIMEOUT = 1
    timeout = DEFAULT_READ_TIMEOUT
    writeTimeout = DEFAULT_WRITE_TIMEOUT

    ser = serial.Serial(device, timeout=timeout, write_timeout=writeTimeout)

    f = open("Data Grabber/sample_units.json")
    contents = f.read()

    j = json.loads(contents)

    columns = []
    for l in j['meta']:
        columns.append(l['nm'])

    # '"{"setTelemetry":{"rate":1}}'
    ser.write(b'{"setTelemetry":{"rate":10}}\r\n')
    #ser.write(b'{"setTelemetry":{"rc":1}}\r\n')


    while True:
        # TODO: Add nchan to MySQL
        #db = Database()
        # pub.register(Database)

        row = ser.readline()
        print(row)
        if row is not None and b"{\"s\":{" in row:
            row_json = json.loads(row)
            raw_data = row_json['s']['d']
            row_list = []
            row_list.append(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%m"))
            for item in raw_data:
                row_list.append(item)
            # print(row_list)
            #db.update(row_list)
            stats = SystemInfo(measurement_date=row_list[0],
                        x=row_list[7],
                        y=row_list[3]
                    )
            # publish to Nginx-Nchan broker
            s.post(PUB_ENDPOINT, params={'id': STATS_CHANNEL}, json=stats._asdict())
            logger.debug('Posted stats:{}'.format(stats))
            time.sleep(0.1)






if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    main()


