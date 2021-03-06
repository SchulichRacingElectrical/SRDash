import sys

import time
from Utilities import readify_data, string_me
from Process import Process
from DashPusher import DashPusher
from subprocess import call
import threading
import asyncio
import platform


def runDash():
    command = ""
    if platform.system() == "Darwin":
        command = "python3 /Users/hilmi/PycharmProjects1/SchulichRacing-Kivy/Dash.py"
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
        while True:
            displayData = processor.getData()
            dPusher.publish(displayData)

    except (KeyboardInterrupt, SystemExit):
        sys.exit()

