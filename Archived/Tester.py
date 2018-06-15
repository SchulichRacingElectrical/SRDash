import sys

import time
from CloudPusher import Pusher
from Utilities import readifyData, stringMe
from Process import Process
from SocketPusher import DashPusher
from subprocess import call
import threading
import asyncio
import platform


def runDash():
    command = ""
    if platform.system() == "Darwin":
        command = "kivy /Users/hilmi/PycharmProjects1/SchulichRacing/Dash/Dash.py"
    elif platform.system() == "Linux":
        command = "python3 /home/pi/Production/Dash/Dash.py"

    call(command, shell=True)


def start_worker(loop):
    """Switch to new event loop and run forever"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def start_worker_publisher(loop):
    """Switch to new event loop and run forever"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def publish(publisher, data):
    publisher.publish(data)


if __name__ == '__main__':
    try:
        worker_loop = asyncio.new_event_loop()
        worker = threading.Thread(target=start_worker, args=(worker_loop,))
        worker.start()
        worker_loop.call_soon_threadsafe(runDash)

        publisher_loop = asyncio.new_event_loop()
        publisher_wrk = threading.Thread(target=start_worker_publisher, args=(publisher_loop,))
        publisher_wrk.start()

        dPusher = DashPusher(5002)

        processor = Process()
        publisher = Pusher("winged-line-203918", "data")
        while True:
            displayData, cloudData = processor.parseLines()
            dPusher.publish(displayData)
            if cloudData is not None:
                publisher_loop.call_soon_threadsafe(publish, publisher, cloudData)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

