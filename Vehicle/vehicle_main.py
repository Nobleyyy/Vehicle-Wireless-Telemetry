### Vehicle Main ###

# File Imports
from vehicle_constants import *

# Package Imports
import can
import cantools
import socket
import time

## Classes ##
class Car():
    def __init__(self) -> None:
        # Import the signal info file
        self.DBC = cantools.database.load_file(DBC_file)

        # Open the CAN interface
        self.bus = can.interface.Bus(channel="can0", interface="socketcan")

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
        return self.bus.recv(CAN_wait_timeout)

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


## Main Program ##

fs_car = Car()

while True:
    pass