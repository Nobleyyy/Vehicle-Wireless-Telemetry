### Server Vehicle ###

# File Imports
from vehicle_server_constants import *
import store_data as db

# Package Imports
import json
import socket
import time

## Classes ##
class Vehicle_Server:
    def __init__(self) -> None:
        self.connection = socket.socket()
        self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.connection.bind((SERVER_IP, SERVER_PORT))
        self.connection.listen(1)

        self.msg_id = 0
        self.buffer = b""

    def connect(self):
        print(f"Waiting for connection on {SERVER_IP}:{SERVER_PORT}...")

        self.conn, self.addr = self.connection.accept()

        print(f"Connected to {self.addr}")

    def disconnect(self):
        self.conn.close()
        self.buffer = b""
        print("Client disconnected")
        self.msg_id = 0

    def receive(self) -> tuple[dict | str, float, int] | None:
        while b"\n" not in self.buffer:
            try:
                data = self.conn.recv(1024)

            except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
                return None

            if not data:
                return None

            self.buffer += data

        message, self.buffer = self.buffer.split(b"\n", 1)
        self.msg_id += 1

        return json.loads(message.decode())

    def date_to_string(self, timestamp_to_convert:float ) -> list:
        dt = time.localtime(timestamp_to_convert)
        return [time.strftime("%H:%M:%S"),time.strftime("%d/%m/%Y")]


## Main Program ##
comms = Vehicle_Server()

current_table = None

while True:
    comms.connect()

    while True:
        msg = comms.receive()

        if msg is None:
            break

        package = {
            "id": msg[2],
            "timestamp": msg[1],
            "msg": msg[0]
        }

        """
        print("Received   ID: ", package["id"],
            "\nTime: ", comms.date_to_string(package["timestamp"])[0],
            "\nMsg: ", package["msg"])
        """

        database_package = {
            "id": package["id"],
            "timestamp": package["timestamp"],
            **package["msg"]
        }

        # ID 1 means a new session has started
        if package["id"] == 1:

            current_table = db.create_session_table(
                database_package
            )

        # Insert the package into the current session
        db.insert_record(
            database_package,
            current_table
        )


    comms.disconnect()
