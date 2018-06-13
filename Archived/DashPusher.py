import socket

"""
    DashPusher - Handles pushing data to Dash
    Uses Socket module and a UDP type server which sends data as fast as it 
    gets it
"""


class DashPusher:
    # Fields
    clientSocket = None
    host = None
    port = None
    server_address = None

    # DashPusher constructor - establishes socket connection
    def __init__(self, port):
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = socket.gethostname()
        self.port = port
        self.server_address = (self.host, self.port)

    # Publish method sends binary data to socket
    def publish(self, data):
        self.clientSocket.sendto(data, self.server_address)
