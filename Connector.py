import asyncio
import json
import threading
import time

from Process import Process
from SocketPusher import Pusher


class Connector:

    #FIELDS
    data = {}
    daq_connected = False

    #CLASSES
    processor = None
    SRServer = None

    # LOOPS
    worker_loop = None
    srserver_worker_loop = None

    # TIMERS
    daq_timer = time.time()
    srserver_timer = time.time()

    # CONSTANTS
    DAQ_CONNECTION_THRESHOLD = 5
    SRSERVER_POLL_RATE = .05

    def __init__(self, daq_connected, processor):
        """ Constructor. """
        self.data = {'timestamp': 0, 'interval': 0, 'battery': 0.0, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
                     'pitch': 0,
                     'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 0,
                     'iat': 0,
                     'oilTemperature': 0, 'gear': 0, 'speed': 0, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0,
                     'rearRight': 0,
                     'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'fuelRate': 0, 'fuelUsage': 0,
                     'baro': 0, 'altitude': 0, 'session': 0, 'lambda': 0}

        if daq_connected:
            self.daq_connected = daq_connected
            self.processor = processor
            self.initialize_data_worker()
            #self.connectToSRServer()
        else:
            self.connect_to_daq()

    def initialize_data_worker(self):
        self.worker_loop = asyncio.new_event_loop()
        worker = threading.Thread(target=self.start_worker, args=(self.worker_loop,))
        worker.start()

        # self.srserver_worker_loop = asyncio.new_event_loop()
        # srserver_worker = threading.Thread(target=self.start_srserver_worker, args=(self.srserver_worker_loop,))
        # srserver_worker.start()

    def connect_to_daq(self):
        print("Attempting to connect to DAQ...")
        elapsed_time = time.time() - self.daq_timer
        if elapsed_time >= self.DAQ_CONNECTION_THRESHOLD and self.processor is None:
            try:
                self.processor = Process()
                self.daq_connected = True
                #self.initialize_data_worker()
                #self.connectToSRServer()
            except Exception as e:
                self.daq_timer = time.time()
                print("Unable to connect to DAQ")
                print(e)
                self.daq_connected = False
                pass

    # def connectToSRServer(self):
    #     host = "schulichracing.ddns.net"
    #     port = 5000
    #     self.SRServer = Pusher(host, port)

    def start_worker(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def start_srserver_worker(self, loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()

    def update(self):
        if self.daq_connected:
            self.worker_loop.call_soon(self.get_data())
            #self.srserver_worker_loop.call_soon(self.publish_to_SRServer())
        else:
            self.connect_to_daq()
        return self.data

    """ASYNC METHODS"""

    def get_data(self):
        print(self.data)
        self.data = json.loads(self.processor.get_data().decode('utf-8'))

    # def publish_to_SRServer(self):
    #     try:
    #         elapsed_time = time.time() - self.srserver_timer
    #         if elapsed_time > self.SRSERVER_POLL_RATE:
    #             self.srserver_timer = time.time()
    #             self.SRServer.publish(json.dumps(self.data).encode("UTF-8"))
    #             print("Dumped data to SRServer")
    #     except Exception as e:
    #         print(e)
    #        pass

    """HELPER METHODS"""

    def return_data(self):
        return self.data
