### Server Vehicle ###

# File Imports
from vehicle_server_constants import *
import store_data as db

# Package Imports
import json
import socket
import ssl
import time
from pathlib import Path
import yaml

## Classes ##
class Vehicle_Server:
    """
    TCP server for communicating with a vehicle client.

    The server manages a socket connection, receives newline-delimited
    JSON messages, assigns message IDs, and provides utilities for
    formatting and displaying received message packages.

    Attributes:
        connection: The server socket used to listen for client connections.
        conn: The active client socket after a connection is established.
        addr: The address of the connected client.
        msg_id: The ID of the most recently received message.
        buffer: Bytes received from the client that have not yet been processed.
    """
    def __init__(self) -> None:
        """Initialize the server socket and message state."""
        self.connection = socket.socket()

        self.connection.setsockopt(
            socket.SOL_SOCKET,
            socket.SO_REUSEADDR,
            1
        )

        self.connection.bind(
            (SERVER_IP, SERVER_PORT)
        )

        self.connection.listen(1)

        # TLS configuration
        self.ssl_context = ssl.SSLContext(
            ssl.PROTOCOL_TLS_SERVER
        )

        self.ssl_context.load_cert_chain(
            certfile=SERVER_CERTIFICATE,
            keyfile=SERVER_PRIVATE_KEY
        )

        self.msg_id = 0
        self.buffer = b""

    def connect(self):
        """Wait for and accept a secure TLS connection."""
        print(
            f"Waiting for vehicle connection on "
            f"{SERVER_IP}:{SERVER_PORT}..."
        )

        raw_conn, self.addr = self.connection.accept()

        self.conn = self.ssl_context.wrap_socket(
            raw_conn,
            server_side=True
        )

        print(
            f"Secure vehicle connection established with "
            f"{self.addr}"
        )

    def disconnect(self):
        """Close the active client connection and reset server state."""
        self.conn.close()
        self.buffer = b""
        print("Vehicle client disconnected")
        self.msg_id = 0

    def receive(self) -> tuple[dict, float, int] | None:
        """
        Receive and decode the next JSON message from the client.

        Waits until a complete newline-delimited message is available.

        Returns:
            dict: The decoded JSON message.
            None: If the connection is lost or reset.
        """
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

    def date_to_string(self, timestamp_to_convert:float) -> list:
        """
        Convert a Unix timestamp into formatted time and date strings.

        Returns:
            A list containing the time in HH:MM:SS format and the
            date in DD/MM/YYYY format.
        """
        dt = time.localtime(timestamp_to_convert)
        return [time.strftime("%H:%M:%S"),time.strftime("%d/%m/%Y")]

    def print_package(self, package_to_print: dict):
        """
        Print a package dictionary with its timestamp converted to a
        human-readable time and date.
        """
        package_to_print = package_to_print.copy()
        package_to_print["timestamp"] = self.date_to_string(package_to_print["timestamp"])
        print(package_to_print)


## Functions ##
def load_config():
    config_path = Path(__file__).resolve().parent.parent / "config.txt"

    with open(config_path, "r") as file:
        return yaml.safe_load(file) or {}

# Run config
config = load_config()

SERVER_IP = config.get("server_ip") or DEFAULT_SERVER_IP

if SERVER_IP.lower() == "localhost":
    SERVER_IP = "127.0.0.1"

SERVER_PORT = int(
    config.get("server_vehicle_port") or DEFAULT_SERVER_PORT
)
    
## Main Program ##
comms = Vehicle_Server()
current_table = None

# Runtime Loop
while True:
    # Wait for a vehicle to connect
    comms.connect()

    # Main Loop
    while True:
        # Recieve data from vehicle
        msg = comms.receive()

        # Exits main loop when communication fails or ends
        if msg is None:
            break

        # Convert recieved message to a dictionary
        database_package = {
            "id": msg[2],
            "timestamp": msg[1],
            **msg[0]
        }

        # Print package for debugging
        #comms.print_package(database_package)

        # ID 1 means a new session has started
        if database_package["id"] == 1:

            current_table = db.create_session_table(
                database_package
            )

        # Insert the package into the current session table
        db.insert_record(
            database_package,
            current_table
        )

    # Closes connection
    comms.disconnect()
