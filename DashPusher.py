import socket
import requests


class DashPusher:
    session = None
    clientSocket = None
    host = None
    port = None
    server_address = None
    STATS_CHANNEL = 'system_stats'
    PUB_ENDPOINT = 'http://localhost:8081/pub'

    def __init__(self, port):
        self.session = requests.Session()
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = socket.gethostname()
        self.port = port
        self.server_address = (self.host, self.port)


    def publish(self, data):
        self.clientSocket.sendto(data, self.server_address)

