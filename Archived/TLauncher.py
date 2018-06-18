import asyncio
import json
import threading
import time

import Utilities
from Process import Process
from SocketPusher import Pusher


class TestLauncher:
    root = None
    dash = None
    TIMEOUT = 5
    UPDATE_TIMEOUT = 0.05
    PU_TIMEOUT = 10
    SRServer = None
    data = {}

    def __init__(self):
        # Connection Variables
        self.processor = None
        self.periodic_update = time.time()
        self.last_update = time.time()
        self.connected = False
        self.internetConnected = Utilities.have_internet()
        self.publisher_loop = None
        self.publisher = None
        self.data = {'timestamp': 0, 'interval': 0, 'battery': 0.0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                     'pitch': 0,
                     'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0,
                     'iat': 0,
                     'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0,
                     'rearRight': 0,
                     'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'fuelRate': 0, 'fuelUsage': 0,
                     'baro': 0, 'altitude': 0, 'session': 0, 'lambda': 0}
        self.start_time = 0
        self.connectToDAQ()
        self.connectToSRServer()

        # Setting up Threading
        self.worker_loop = asyncio.new_event_loop()
        worker = threading.Thread(target=self.start_worker, args=(self.worker_loop,))
        worker.start()

        # TODO: ADD CLOUD CAPABILITY
        # self.connectToCloud()


    # TODO: ADD CLOUD CAPABILITY
    # def connectToCloud(self):
    #     try:
    #         self.publisher_loop = asyncio.new_event_loop()
    #         publisher_wrk = threading.Thread(target=self.start_worker_publisher, args=(self.publisher_loop,))
    #         publisher_wrk.start()
    #         self.publisher = Pusher("winged-line-203918", "cardata")
    #     except Exception as e:
    #         print("Unable to connect to Google Cloud")
    #         print(e)

    def connectToDAQ(self):
        try:
            self.processor = Process()
            self.connected = True
        except Exception:
            self.start_time = time.time()
            print("Unable to connect to DAQ")
            self.connected = False

    def connectToSRServer(self):
        host = "schulichracing.ddns.net"
        port = 5000
        self.SRServer = Pusher(host, port)

    def start_worker(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def start_worker_publisher(self, loop):
        """Switch to new event loop and run forever"""
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def update_not_connected(self):
        elapsed_time = time.time() - self.start_time
        if elapsed_time > self.TIMEOUT:
            self.connectToDAQ()
        print(self.data)

    def update_connected(self):
        # Update data dictionary in class
        self.worker_loop.call_soon(self.get_data())
        #print(self.data["rpm"])
        if self.internetConnected:
            self.publish_to_SRServer()
        print(self.data)

    def publish_to_SRServer(self):
        try:
            elapsed_time = time.time() - self.last_update
            if elapsed_time > self.UPDATE_TIMEOUT:
                self.last_update = time.time()
                self.SRServer.publish(json.dumps(self.data).encode("UTF-8"))
        except Exception as e:
            print(e)

    def check_device_status(self):
        elapsed_time = time.time() - self.periodic_update
        if elapsed_time > self.PU_TIMEOUT:
            self.periodic_update = time.time()
            self.internetConnected = Utilities.have_internet()
            if self.processor is None:
                self.connectToDAQ()
            else:
                try:
                    self.processor.get_device()
                except Exception as e:
                    self.connected = False

    def update(self):
        # DAQ is not connected. Continuing trying until connection established
        if not self.connected:
            self.update_not_connected()
        else:
            self.update_connected()
        self.check_device_status()

    def get_data(self):
        self.data = json.loads(self.processor.get_data().decode('utf-8'))
        print(self.data)


if __name__ == '__main__':
    launcher = TestLauncher()
    while True:
        launcher.update()
