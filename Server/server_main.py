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
        # Collect commandline commands
        commands(web_server)
    finally:
        # Shutdown server
        print("Stopping servers...")
        vehicle_server.terminate()
        web_server.terminate()

        vehicle_server.wait()
        web_server.wait()
        print("Servers stopped.")


def commands(web_server):
    while True:
        command = input("> ").strip().lower()
        # Show all commands
        if command == "help":
            show_help()
        # Shutdown Server
        elif command in ("quit", "stop", "end", "die", "kill"):
            return
        # Restart Server
        elif command == "restart":
            print("Restarting server...")
            os.execv(sys.executable, [sys.executable] + sys.argv)
        # Enable sign ups
        elif command in ("signup on", "signup true"):
            set_signup_status(True)
        # Disable sign ups
        elif command in ("signup off", "signup false"):
            set_signup_status(False)
        # Show sign up status
        elif command == "signup status":
            show_signup_status()
        # List standard user account emails
        elif command == "users":
            list_users()
        # Delete a user account
        elif command.startswith("deleteuser "):
            email = command[11:].strip()
            if delete_user(email):
                web_server = restart_web_server(web_server)
        # List of admin account emails
        elif command == "admins":
            list_admins()
        # Give admin to an account
        elif command.lower().startswith("admin "):
            email = command[6:].strip()
            if make_admin(email):
                web_server = restart_web_server(web_server)
        # Take away admin from an account
        elif command.lower().startswith("unadmin "):
            email = command[8:].strip()
            if remove_admin(email):
                web_server = restart_web_server(web_server)
        # List all session tables stored
        elif command.lower() == "sessions":
            list_sessions()
        # Delete a session tabble
        elif command.lower().startswith("deletesession "):
            session = command[14:].strip()
            if delete_session(session):
                web_server = restart_web_server(web_server)
        # Capture if a non-existent command is entered
        elif command:
            print("Unknown command.")


def show_help():
    print("""
Available commands:

  help                         Show this help message
  users                        List standard users
  admins                       List admin users
  admin <email>                Give admin privileges
  unadmin <email>              Remove admin privileges
  deleteuser <email>           Delete a user
  signup on                    Enable new account registration
  signup off                   Disable new account registration
  signup status                Show sign-up status
  sessions                     List vehicle sessions
  deletesession <number>       Delete a session
  restart                      Restart the server
  quit / stop / end / die / kill
                               Stop the server
""")
    

def restart_web_server(web_server):
    print("Restarting Flask server...")
    # Stop flask server
    web_server.terminate()
    web_server.wait()
    # Reopen flask server
    web_server = subprocess.Popen(
        [sys.executable, "server_web.py"],
        cwd=WEB_DIR
    )

    print("Flask server restarted.")

    return web_server


def set_signup_status(enabled):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    # Check users database.db exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)
    # Alter signup setting
    cursor.execute("""
        INSERT INTO settings (key, value)
        VALUES ('allow_signups', ?)
        ON CONFLICT(key)
        DO UPDATE SET value = excluded.value
    """, ("1" if enabled else "0",))

    connection.commit()
    connection.close()

    if enabled:
        print("Sign-ups enabled.")
    else:
        print("Sign-ups disabled.")


def show_signup_status():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    # Check state of sign up setting in database.db
    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = 'allow_signups'
    """)

    result = cursor.fetchone()
    connection.close()

    # If no setting exists yet, sign-ups are enabled
    enabled = result is None or result[0] == "1"

    if enabled:
        print("Sign-ups are enabled.")
    else:
        print("Sign-ups are disabled.")


def list_users():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Find all standard users (non-admins)
    cursor.execute(
        "SELECT email FROM user WHERE admin = 0"
    )
    users = cursor.fetchall()

    connection.close()

    print("Standard users:")
    if not users:
        print("No standard users found.")
        return

    for user in users:
        print(f"- {user[0]}")


def delete_user(email):
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()

    # Check email of user exists
    cursor.execute(
        "SELECT email FROM user WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()

    # User does not exist
    if not user:
        print(f"User not found: {email}")
        connection.close()
        return False

    # Delete user
    cursor.execute(
        "DELETE FROM user WHERE email = ?",
        (email,)
    )

    connection.commit()
    connection.close()

    print(f"{email} deleted.")
    return True


def list_admins():
    connection = sqlite3.connect(DATABASE)
    cursor = connection.cursor()
    # Build admin search statment
    cursor.execute(
        "SELECT email FROM user WHERE admin = 1"
    )
    # Search for admin users
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
    # Check email of user exists
    cursor.execute(
        "SELECT email FROM user WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()
    # User does not exist
    if not user:
        print(f"User not found: {email}")
        connection.close()
        return
    # Make user admin
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
    # Check email of user exists
    cursor.execute(
        "SELECT email FROM user WHERE email = ?",
        (email,)
    )
    user = cursor.fetchone()
    # User does not exist
    if not user:
        print(f"User not found: {email}")
        connection.close()
        return
    # Take away admin from user
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
    # Build session search statment
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name LIKE 'session_%'"
    )
    # Search for sessions
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
    # Session list output formatting
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
    # Make sure value is a number
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
    # Build session table search statement
    cursor.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type = 'table' AND name = ?",
        (table_name,)
    )
    # Number does not exist
    table = cursor.fetchone()
    if not table:
        print(f"Session {session} not found.")
        connection.close()
        return
    # Remove session table
    cursor.execute(f'DROP TABLE "{table_name}"')
    connection.commit()
    connection.close()
    print(f"Session {session} deleted.")


## Main Program ##
if __name__ == "__main__":
    main()
