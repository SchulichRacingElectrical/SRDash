import asyncio
import json
import threading
import time
import traceback
from tkinter import Tk, TclError

from DashGUI import DashGUI, sys
from Process import Process


# from Pusher import Pusher
from SocketPusher import Pusher


class Launcher:
    root = None
    dash = None
    TIMEOUT = 5
    UPDATE_TIMEOUT = 0.2
    SRServer = None

    def __init__(self):
        # Connection Variables
        self.last_update = time.time()
        self.connected = False
        self.publisher_loop = None
        self.publisher = None
        self.data = {'timestamp': 0, 'interval': 0, 'battery': 12.3, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                     'pitch': 0,
                     'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0,
                     'iat': 0,
                     'oilTemperature': 0, 'gear': 0, 'speed': 120, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0,
                     'rearRight': 0,
                     'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'baro': 0, 'altitude': 0,
                     'session': 0,
                     'lambda': 0}
        self.start_time = 0
        self.connectToDAQ()
        self.connectToSRServer()
        self.launchGUI()

        # Setting up Threading
        self.worker_loop = asyncio.new_event_loop()
        worker = threading.Thread(target=self.start_worker, args=(self.worker_loop,))
        worker.start()

        # TODO: ADD CLOUD CAPABILITY
        # self.connectToCloud()

    def launchGUI(self):
        self.root = Tk()
        self.dash = DashGUI(self.root)
        self.dash.init_all_frames(self.root)
        self.dash.init_all_dials(self.root)
        self.dash.init_rpmbar(self.root)
        self.dash.draw_aesthetics(self.root)

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

    def update(self):
        # DAQ is not connected. Continuing trying until connection established
        # TODO: COMMENT BEFORE DEPLOYING ON CAR
        # """ START DEBUGGING """
        if self.data["rpm"] >= 15000:
            self.data["rpm"] = 0
        self.data["rpm"] = self.data["rpm"] + 40
        self.data["coolantTemperature"] = self.data["coolantTemperature"]
        self.data["afr"] = self.data["afr"]
        self.data["speed"] = self.data["speed"]
        self.data["battery"] = self.data["battery"]
        self.data["oilTemperature"] = self.data["oilTemperature"]
        self.data["fuelTemp"] = self.data["fuelTemp"]
        self.dash.update(self.data)
        self.root.update()
        # """" END DEBUGGING """
        if not self.connected:
            elapsed_time = time.time() - self.start_time
            if elapsed_time > self.TIMEOUT:
                self.connectToDAQ()
        else:
            self.worker_loop.call_soon(self.get_data())
            self.dash.update(self.data)
            self.root.update()
            elapsed_time = time.time() - self.last_update
            if elapsed_time > self.UPDATE_TIMEOUT:
                self.last_update = time.time()
                self.SRServer.publish(json.dumps(self.data).encode("UTF-8"))

    def get_data(self):
        self.data = json.loads(self.processor.getData().decode('utf-8'))


if __name__ == '__main__':
    launcher = Launcher()
    while True:
        launcher.update()
