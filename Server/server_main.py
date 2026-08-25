### Server Main ###

# Package Imports
import os
import sys
import subprocess

# File Imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VEHICLE_DIR = os.path.join(BASE_DIR, "Vehicle_Access")
WEB_DIR = os.path.join(BASE_DIR, "Web_Access")

## Functions ##
def main():
    # Start vehicle connection server
    vehicle_server = subprocess.Popen(
        [sys.executable, "server_vehicle.py"],
        cwd=VEHICLE_DIR
    )
    # Start Flask web server
    web_server = subprocess.Popen(
        [sys.executable, "server_web.py"],
        cwd=WEB_DIR
    )
    # Keep servers running
    try:
        vehicle_server.wait()
        web_server.wait()
    # Stop servers
    except KeyboardInterrupt:
        print("\nStopping servers...")
    finally:
        vehicle_server.terminate()
        web_server.terminate()

        vehicle_server.wait()
        web_server.wait()

# Only run if this file is run, not as imported
if __name__ == "__main__":
    main()
