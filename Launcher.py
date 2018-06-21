import asyncio
import json
import time
from tkinter import Tk

from Connector import Connector
from DashGUI import DashGUI
from Process import Process
from SocketPusher import Pusher


class Launcher:
    root = None
    dash = None
    data = {}
    connector = None

    def __init__(self):
        # Connection Variables
        self.processor = None
        self.launch_gui()
        daq_connected = self.connect_to_daq()
        self.connector = Connector(daq_connected, self.processor)
        self.data = self.connector.return_data()

    def launch_gui(self):
        self.root = Tk()
        self.dash = DashGUI(self.root)
        self.dash.init_all_frames(self.root)
        self.dash.init_all_dials(self.root)
        self.dash.init_rpmbar(self.root)
        self.dash.draw_aesthetics(self.root)

    def connect_to_daq(self):
        try:
            self.processor = Process()
            return True
        except Exception as e:
            print("Unable to connect to DAQ")
            print(e)
            return False

    def update(self):
        # DAQ is not connected. Continuing trying until connection established
        self.data = self.connector.update()

        self.dash.update(self.data)
        self.root.update()


if __name__ == '__main__':
    launcher = Launcher()
    while True:
        launcher.update()
