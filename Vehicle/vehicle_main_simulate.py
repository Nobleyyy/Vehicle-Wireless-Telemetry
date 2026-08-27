### Vehicle Main Simulation ###

# File Imports
from vehicle_constants import *

# Package Imports
import csv
import json
import socket
import ssl
import time

## Classes ##
class Data_Client():
    """
    Client used to send timestamped data packages to a remote server.

    Attributes:
        connection (socket.socket): Socket connection to the remote server.
        package_id (int): ID of the most recently sent package.
    """
    def __init__(self) -> None:
        """
        Initialise the client and establish a secure TLS connection
        to the server.
        """
        raw_socket = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        context = ssl.create_default_context(
            ssl.Purpose.SERVER_AUTH,
            cafile=CA_CERTIFICATE
        )

        self.connection = context.wrap_socket(
            raw_socket,
            server_hostname=SERVER_HOSTNAME
        )

        self.connection.connect(
            (SERVER_IP, SERVER_PORT)
        )

        self.package_id = 0

    def send_data(self, data):
        """
        Send data to the connected server.

        Args:
            data: The data to be sent to the server.
        """
        # Send data off
        self.connection.sendall(self.array_to_json(data))

    def array_to_json(self, data_to_encode: dict) -> bytes:
        """
        Convert data into a JSON-encoded package.

        The package contains the data, a timestamp, and a unique
        sequential package ID.

        Args:
            data_to_encode: The dictionary or string to include in the package.

        Returns:
            The encoded package as bytes, terminated with a newline.
        """
        # array of [data, timestamp, id]
        self.package_id += 1
        package = [data_to_encode, time.time(), self.package_id]

        return (json.dumps(package) + "\n").encode()


## Functions ##
def read_csv(filename="ecu_signals.csv"):
    # Simulated data
    if not hasattr(read_csv, "reader"):
        read_csv.file = open(filename, "r", newline="")
        read_csv.reader = csv.DictReader(read_csv.file)

    try:
        return next(read_csv.reader)
    except StopIteration:
        read_csv.file.close()
        del read_csv.reader
        del read_csv.file
        return None

## Main Program ##
comms = Data_Client()

while BROADCAST_DATA:
    # Input data
    data = read_csv()
    time.sleep(0.2)

    # Exit
    if data == None:
        break

    # Send data off
    comms.send_data(data)

comms.connection.close()
