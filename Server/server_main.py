### Server Main ###
import sys
import os
import threading
import runpy

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

VEHICLE_DIR = os.path.join(BASE_DIR, "Vehicle_Access")
WEB_DIR = os.path.join(BASE_DIR, "Web_Access")


def run_vehicle():
    sys.path.insert(0, VEHICLE_DIR)
    runpy.run_path(
        os.path.join(VEHICLE_DIR, "server_vehicle.py"),
        run_name="__main__"
    )


def run_web():
    sys.path.insert(0, WEB_DIR)
    runpy.run_path(
        os.path.join(WEB_DIR, "server_web.py"),
        run_name="__main__"
    )


def main():
    vehicle_thread = threading.Thread(
        target=run_vehicle,
        name="VehicleServer"
    )

    web_thread = threading.Thread(
        target=run_web,
        name="WebServer"
    )

    vehicle_thread.start()
    web_thread.start()

    vehicle_thread.join()
    web_thread.join()


if __name__ == "__main__":
    main()
