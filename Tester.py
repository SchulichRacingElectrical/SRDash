import sys

import time
from Pusher import Pusher
from Utilities import readifyData, stringMe
from Process import Process
from DashPusher import DashPusher
from subprocess import call
import threading
import asyncio
import platform


def runDash():
    command = ""
    if platform.system() == "Darwin":
        command = "kivy /Users/hilmi/PycharmProjects/SR3/Production/Dash/Dash.py"
    elif platform.system() == "Linux":
        command = "kivy /home/sysop/Production/Dash/Dash.py"

    call(command, shell=True)


def start_worker(loop):
    """Switch to new event loop and run forever"""
    asyncio.set_event_loop(loop)
    loop.run_forever()


if __name__ == '__main__':
    try:
        worker_loop = asyncio.new_event_loop()
        worker = threading.Thread(target=start_worker, args=(worker_loop,))
        worker.start()
        worker_loop.call_soon_threadsafe(runDash)
        #time.sleep(5)
        dPusher = DashPusher(5001)

        processor = Process()
        publisher = Pusher("winged-line-203918", "data")
        while True:
            displayData, cloudData = processor.parseLines()
            dPusher.publish(displayData)
            if cloudData is not None:
                publisher.publish(cloudData)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

