### Vehicle Server Constants ###

# Server Info
SERVER_IP = "localhost"
SERVER_PORT = 5001

# TLS
from pathlib import Path

CERT_DIR = Path(__file__).resolve().parent / "Certificates"

SERVER_CERTIFICATE = CERT_DIR / "server-cert.pem"
SERVER_PRIVATE_KEY = CERT_DIR / "server-key.pem"
CA_CERTIFICATE = CERT_DIR / "ca-cert.pem"


# Database Info
EVENT_NAME = r"Global\VehicleAccessNewRecord"