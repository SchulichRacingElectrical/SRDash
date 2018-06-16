import json
from time import sleep

from SocketPusher import Pusher

host = "schulichracing.ddns.net"
port = 5000

dp = Pusher(host, port)
data = {'timestamp': 0, 'interval': 0, 'battery': 12.3, 'accelX': 0, 'accelY': 0, 'accelZ': 0, 'yaw': 0,
        'pitch': 0,
        'roll': 0, 'rpm': 0, 'map': 0, 'tps': 0, 'oilPressure': 0, 'afr': 0, 'coolantTemperature': 51,
        'iat': 0,
        'oilTemperature': 0, 'gear': 0, 'speed': 120, 'frontLeft': 0, 'frontRight': 0, 'rearLeft': 0,
        'rearRight': 0,
        'latitude': 0, 'longitude': 0, 'injectorPW': 0, 'fuelTemp': 0, 'baro': 0, 'altitude': 0,
        'session': 0,
        'lambda': 0}
while True:
    data["rpm"] = data["rpm"] + 150
    if data["rpm"] >= 12500:
        data["rpm"] = 0
    dp.publish(json.dumps(data).encode("UTF-8"))
    sleep(0.05)
