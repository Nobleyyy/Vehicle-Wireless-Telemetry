### Vehicle Constants ###

# Package Imports
from pathlib import Path

# CAN Signals Information
DBC_File = "Vehicle/CAN.dbc"
CAN_CHANNEL = "can0"
CAN_INTERFACE = "socketcan"

# Wait time for each frame read check
CAN_WAIT_TIMEOUT = 1.0

# Send data to server
BROADCAST_DATA = True

# Server Info
SERVER_IP = "localhost"
SERVER_PORT = 5001

# TLS
SERVER_HOSTNAME = SERVER_IP
BASE_DIR = Path(__file__).resolve().parent
CA_CERTIFICATE = str(BASE_DIR / "Certificates" / "ca-cert.pem")

