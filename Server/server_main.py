### Server Main ###

# Package Imports
import os
import sys
import subprocess
import sqlite3


# File Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VEHICLE_DIR = os.path.join(BASE_DIR, "Vehicle_Access")
WEB_DIR = os.path.join(BASE_DIR, "Web_Access")
DATABASE = os.path.join(WEB_DIR, "website", "database.db")
CAR_DATABASE = os.path.join(BASE_DIR, "Data_Archive", "car_data.db")



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

    print("Servers started.")

    try:
        commands(web_server)

    finally:
        print("Stopping servers...")

        vehicle_server.terminate()
        web_server.terminate()

        vehicle_server.wait()
        web_server.wait()

        print("Servers stopped.")


def commands(web_server):
    while True:
        command = input("> ").strip().lower()

        if command in ("quit", "stop", "end", "die", "kill"):
            return

        elif command == "restart":
            print("Restarting server...")
            os.execv(sys.executable, [sys.executable] + sys.argv)

        elif command == "admins":
            list_admins()

        elif command.lower().startswith("admin "):
            email = command[6:].strip()
            if make_admin(email):
                web_server = restart_web_server(web_server)

        elif command.lower().startswith("unadmin "):
            email = command[8:].strip()
            if remove_admin(email):
                web_server = restart_web_server(web_server)

        elif command.lower() == "sessions":
            list_sessions()

        elif command.lower().startswith("deletesession "):
            session = command[14:].strip()
            if delete_session(session):
                web_server = restart_web_server(web_server)

        elif command:
            print("Unknown command.")

def restart_web_server(web_server):
    print("Restarting Flask server...")

    web_server.terminate()
    web_server.wait()

    web_server = subprocess.Popen(
        [sys.executable, "server_web.py"],
        cwd=WEB_DIR
    )

    print("Flask server restarted.")

    return web_server


def list_admins():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT email FROM user WHERE admin = 1"
    )

    admins = cursor.fetchall()

    connection.close()

    print("Admin users:")

    if not admins:
        print("No admin users found.")
        return

    for admin in admins:
        print(f"- {admin[0]}")

def make_admin(email):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT email FROM user WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    if not user:
        print(f"User not found: {email}")
        connection.close()
        return

    cursor.execute(
        "UPDATE user SET admin = 1 WHERE email = ?",
        (email,)
    )

    connection.commit()
    connection.close()

    print(f"{email} is now an admin.")


def remove_admin(email):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT email FROM user WHERE email = ?",
        (email,)
    )

    user = cursor.fetchone()

    if not user:
        print(f"User not found: {email}")
        connection.close()
        return

    cursor.execute(
        "UPDATE user SET admin = 0 WHERE email = ?",
        (email,)
    )

    connection.commit()
    connection.close()

    print(f"{email} is no longer an admin.")

def list_sessions():
    connection = sqlite3.connect(CAR_DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name LIKE 'session_%'"
    )

    tables = cursor.fetchall()
    connection.close()

    sessions = []

    for table in tables:
        try:
            session_number = int(table[0].split("_")[1])
            sessions.append(session_number)
        except (IndexError, ValueError):
            continue

    sessions.sort()

    if not sessions:
        print("No sessions found.")
        return

    ranges = []
    start = sessions[0]
    previous = sessions[0]

    for session in sessions[1:]:
        if session == previous + 1:
            previous = session
        else:
            count = previous - start + 1

            if count >= 3:
                ranges.append(f"{start}-{previous}")
            else:
                for number in range(start, previous + 1):
                    ranges.append(str(number))

            start = session
            previous = session

    # Handle final group
    count = previous - start + 1

    if count >= 3:
        ranges.append(f"{start}-{previous}")
    else:
        for number in range(start, previous + 1):
            ranges.append(str(number))

    print("Sessions:")
    print(", ".join(ranges))


def delete_session(session):
    try:
        session = int(session)
    except ValueError:
        print("Invalid session number.")
        return

    table_name = f"session_{session}"

    connection = sqlite3.connect(CAR_DATABASE)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    )

    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name = ?",
        (table_name,)
    )

    table = cursor.fetchone()

    if not table:
        print(f"Session {session} not found.")
        connection.close()
        return

    cursor.execute(f'DROP TABLE "{table_name}"')

    connection.commit()
    connection.close()

    print(f"Session {session} deleted.")


## Main Program ##
if __name__ == "__main__":
    main()
