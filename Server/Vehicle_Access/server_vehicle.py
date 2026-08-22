### Server Vehicle ###

# File Imports
from vehicle_server_constants import *
import Web_Access.server_web as web

# Package Imports
import json
import socket
import struct
import time

## Classes ##
class Data_Server:
    def __init__(self) -> None:
        self.connection = socket.socket()
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.connection.bind((SERVER_IP, SERVER_PORT))
        self.connection.listen(1)

        self.msg_id = 0

    def connect(self):
        print(f"Waiting for connection on {SERVER_IP}:{SERVER_PORT}...")

        self.conn, self.addr = self.connection.accept()

        print(f"Connected to {self.addr}")

    def disconnect(self):
        self.conn.close()
        print("Client disconnected")
        self.msg_id = 0

    def receive(self) -> tuple[dict|str, float, int]:
        # array of [data, timestamp, id]
        data = self.conn.recv(1024)

        if not data:
            return None

        self.msg_id += 1

        return json.loads(data.decode())

    def date_to_string(self, timestamp_to_convert:float ) -> list:
        dt = time.localtime(timestamp_to_convert)
        return [time.strftime("%H:%M:%S"),time.strftime("%d/%m/%Y")]


## Main Program ##
comms = Data_Server()

while True:
    comms.connect()

    while True:
        msg = comms.receive()

        if msg is None:
            break

        package = {
            "ID": msg[2],
            "timestamp": msg[1],
            "msg": msg[0]
        }

        print("Received   ID: ", package["ID"],
            "\nTime: ", comms.date_to_string(package["timestamp"])[0],
            "\nMsg: ", package["msg"])

        if package["msg"] == "quit":
            break

    comms.disconnect()