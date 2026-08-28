from pathlib import Path
import ipaddress
import shutil
import subprocess
import sys


# ============================================================
# Configuration
# ============================================================

CERT_DIR = Path(__file__).resolve().parent / "Certificates"

CA_KEY = CERT_DIR / "ca-key.pem"
CA_CERT = CERT_DIR / "ca-cert.pem"
CA_SERIAL = CERT_DIR / "ca-cert.srl"

SERVER_KEY = CERT_DIR / "server-key.pem"
SERVER_CSR = CERT_DIR / "server.csr"
SERVER_CERT = CERT_DIR / "server-cert.pem"
SERVER_CONFIG = CERT_DIR / "server-cert.cnf"

CA_VALIDITY_DAYS = 3650
SERVER_VALIDITY_DAYS = 825


# ============================================================
# Utility Functions
# ============================================================

def run_command(command):
    """Run an OpenSSL command and stop if it fails."""

    print()
    print("Running:")
    print(" ".join(str(item) for item in command))
    print()

    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError:
        print("ERROR: OpenSSL command failed.")
        sys.exit(1)


def check_openssl():
    """Check that OpenSSL is installed."""

    if shutil.which("openssl") is None:
        print("ERROR: OpenSSL could not be found.")
        print()
        print("Install OpenSSL and make sure it is available in PATH.")
        sys.exit(1)


def get_server_address():
    """Ask the user for the server IP address or hostname."""

    while True:
        address = input(
            "Enter the server IP address or hostname: "
        ).strip()

        if not address:
            print("Please enter an address.")
            continue

        # localhost gets special treatment
        if address.lower() == "localhost":
            return {
                "dns": ["localhost"],
                "ip": ["127.0.0.1"],
                "common_name": "localhost"
            }

        # Check whether the input is an IP address
        try:
            ipaddress.ip_address(address)

            return {
                "dns": [],
                "ip": [address],
                "common_name": address
            }

        except ValueError:
            pass

        # If it isn't an IP, treat it as a hostname
        if " " in address:
            print("Invalid hostname.")
            continue

        return {
            "dns": [address],
            "ip": [],
            "common_name": address
        }


def create_server_config(address_info):
    """Create the OpenSSL server certificate configuration."""

    san_entries = []

    dns_counter = 1
    ip_counter = 1

    for dns_name in address_info["dns"]:
        san_entries.append(
            f"DNS.{dns_counter} = {dns_name}"
        )
        dns_counter += 1

    for ip_address in address_info["ip"]:
        san_entries.append(
            f"IP.{ip_counter} = {ip_address}"
        )
        ip_counter += 1

    # Create this separately because Python 3.10 does not allow
    # backslashes inside f-string expressions.
    san_text = "\n".join(san_entries)

    config = f"""\
[req]
default_bits = 2048
prompt = no
default_md = sha256
req_extensions = req_ext
distinguished_name = dn

[dn]
C = GB
O = VehicleTelemetry
OU = Server
CN = {address_info["common_name"]}

[req_ext]
subjectAltName = @alt_names

[alt_names]
{san_text}

[server_ext]
subjectAltName = @alt_names
"""

    SERVER_CONFIG.write_text(config, encoding="utf-8")


# ============================================================
# Main Certificate Generation
# ============================================================

def main():

    print("=" * 60)
    print("Vehicle Telemetry Certificate Generator")
    print("=" * 60)
    print()

    check_openssl()

    # --------------------------------------------------------
    # Ask for server address
    # --------------------------------------------------------

    address_info = get_server_address()

    print()
    print("Certificate will be generated for:")

    for dns_name in address_info["dns"]:
        print(f"  DNS: {dns_name}")

    for ip_address in address_info["ip"]:
        print(f"  IP:  {ip_address}")

    print()

    # --------------------------------------------------------
    # Create Certificates directory
    # --------------------------------------------------------

    CERT_DIR.mkdir(parents=True, exist_ok=True)

    # --------------------------------------------------------
    # Generate CA private key
    # --------------------------------------------------------

    print("[1/6] Generating CA private key...")

    run_command([
        "openssl",
        "genrsa",
        "-out",
        str(CA_KEY),
        "4096"
    ])

    # --------------------------------------------------------
    # Generate CA certificate
    # --------------------------------------------------------

    print("[2/6] Generating CA certificate...")

    run_command([
        "openssl",
        "req",
        "-x509",
        "-new",
        "-sha256",
        "-key",
        str(CA_KEY),
        "-out",
        str(CA_CERT),
        "-days",
        str(CA_VALIDITY_DAYS),
        "-subj",
        "/C=GB/O=VehicleTelemetry/OU=CA/CN=VehicleTelemetry-CA"
    ])

    # --------------------------------------------------------
    # Generate server private key
    # --------------------------------------------------------

    print("[3/6] Generating server private key...")

    run_command([
        "openssl",
        "genrsa",
        "-out",
        str(SERVER_KEY),
        "2048"
    ])

    # --------------------------------------------------------
    # Create server certificate configuration
    # --------------------------------------------------------

    print("[4/6] Creating server certificate configuration...")

    create_server_config(address_info)

    # --------------------------------------------------------
    # Generate server CSR
    # --------------------------------------------------------

    print("[5/6] Generating server CSR...")

    run_command([
        "openssl",
        "req",
        "-new",
        "-sha256",
        "-key",
        str(SERVER_KEY),
        "-out",
        str(SERVER_CSR),
        "-config",
        str(SERVER_CONFIG)
    ])

    # --------------------------------------------------------
    # Sign server certificate
    # --------------------------------------------------------

    print("[6/6] Signing server certificate...")

    run_command([
        "openssl",
        "x509",
        "-req",
        "-sha256",
        "-in",
        str(SERVER_CSR),
        "-CA",
        str(CA_CERT),
        "-CAkey",
        str(CA_KEY),
        "-CAcreateserial",
        "-out",
        str(SERVER_CERT),
        "-days",
        str(SERVER_VALIDITY_DAYS),
        "-extensions",
        "server_ext",
        "-extfile",
        str(SERVER_CONFIG)
    ])

    # --------------------------------------------------------
    # Finished
    # --------------------------------------------------------

    print()
    print("=" * 60)
    print("Certificate generation complete!")
    print("=" * 60)
    print()

    print(f"Certificates created in:")
    print(f"  {CERT_DIR}")
    print()

    print("Generated files:")

    for file in [
        CA_CERT,
        CA_KEY,
        CA_SERIAL,
        SERVER_CERT,
        SERVER_KEY,
        SERVER_CSR,
        SERVER_CONFIG
    ]:
        if file.exists():
            print(f"  {file.name}")

    print()


if __name__ == "__main__":
    main()
