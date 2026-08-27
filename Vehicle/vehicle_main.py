### Vehicle Main ###

# File Imports
from vehicle_constants import *

# Package Imports
import can
import cantools
import json
import socket
import time

## Classes ##
class Car():
    """
    Interface for reading and decoding CAN bus messages.

    Loads signal definitions from a DBC file and provides methods for
    receiving CAN frames, decoding their signals, and displaying the
    decoded signal values.

    Attributes:
        DBC: The loaded CAN database file containing message and signal definitions.
        bus: The CAN bus interface used to receive messages.
    """
    def __init__(self) -> None:
        """
        Initialise the CAN interface and load the DBC file.

        The DBC file is used to decode CAN messages into their
        corresponding signal names and values.
        """
        # Import the signal info file
        self.DBC = cantools.database.load_file(DBC_File)

        # Open the CAN interface
        self.bus = can.interface.Bus(channel=CAN_CHANNEL, interface=CAN_INTERFACE)

    def close(self):
        """
        Close CAN interface.
        """
        self.bus.shutdown()

    def get_signal_names(self) -> list[str]:
        """
        Return all signal names defined in the DBC.

        Returns a list of signal names in order.
        """
        signal_names = []

        for message in self.DBC.messages:
            for signal in message.signals:
                signal_names.append(signal.name)

        return signal_names

    def read_frame(self) -> can.Message | None:
        """
        Read one CAN frame.

        Returns can.Message object if a frame is received, otherwise None.
        """
        return self.bus.recv(CAN_WAIT_TIMEOUT)

    def decode_frame(self, message: can.Message | None) -> dict | None:
        """
        Decode a CAN frame.

        Returns a dictionary of decoded CAN signals, or None if decoding fails.
        """
        if message is None:
            return None

        try:
            decoded = self.DBC.decode_message(
                message.arbitration_id,
                message.data
            )
            return decoded

        except (KeyError, cantools.DecodeError):
            # CAN ID is not defined in the DBC file
            return None
        
    def print_signal(self, signals: dict | None) -> None:
        """
        Prints the decoded CAN frame.
        """
        if signals is None:
            print("No signals to display.")
            return None

        for signal_name, value in signals.items():
            print(f"{signal_name}: {value}")


class Data_Client():
    """
    Client used to send timestamped data packages to a remote server.

    Attributes:
        connection (socket.socket): Socket connection to the remote server.
        package_id (int): ID of the most recently sent package.
    """
    def __init__(self) -> None:
        """
        Initialise the client and establish a connection to the server and the package ID is initialised to zero.
        """
        self.connection = socket.socket()
        self.connection.connect((SERVER_IP, SERVER_PORT))

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


## Main Program ##
fs_car = Car()
comms = Data_Client()

try:
    while BROADCAST_DATA:
        # Read CAN frame
        message = fs_car.read_frame()

        # No message received
        if message is None:
            continue

        # Decode CAN frame
        data = fs_car.decode_frame(message)

        # Ignore messages that cannot be decoded
        if data is None:
            continue

        # Print decoded signals
        fs_car.print_signal(data)

        # Send decoded data
        comms.send_data(data)

finally:
    fs_car.close()
    comms.connection.close()
