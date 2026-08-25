import os
import sys
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VEHICLE_DIR = os.path.join(BASE_DIR, "Vehicle_Access")
WEB_DIR = os.path.join(BASE_DIR, "Web_Access")


def main():
    vehicle_server = subprocess.Popen(
        [sys.executable, "server_vehicle.py"],
        cwd=VEHICLE_DIR
    )

    web_server = subprocess.Popen(
        [sys.executable, "server_web.py"],
        cwd=WEB_DIR
    )

    try:
        vehicle_server.wait()
        web_server.wait()

    except KeyboardInterrupt:
        print("\nStopping servers...")

    finally:
        vehicle_server.terminate()
        web_server.terminate()

        vehicle_server.wait()
        web_server.wait()


if __name__ == "__main__":
    main()
