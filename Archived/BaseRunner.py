import sys
from time import sleep
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


if __name__ == '__main__':

    try:
        worker_loop = asyncio.new_event_loop()
        worker = threading.Thread(target=start_worker, args=(worker_loop,))
        worker.start()
        worker_loop.call_soon_threadsafe(runDash)

        dPusher = DashPusher(5002)
        processor = Process()
        while True:
            dash_data = processor.get_data()
            print(dash_data)
            dPusher.publish(dash_data)
    except (KeyboardInterrupt, SystemExit):
        sys.exit()

