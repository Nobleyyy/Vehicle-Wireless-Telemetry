### Store Data ###

# File Imports
from vehicle_server_constants import *

# Package Imports
from pathlib import Path
import sqlite3
import win32event

DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "Data_Archive"
    / "car_data.db"
)

## Functions ##
def connect():
    # Ensure directory exists
    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    # Create database if it does not already exist
    return sqlite3.connect(
        DATABASE_FILE,
        timeout=30
    )


def create_session_table(data):
    # Connect to the database only while creating session table
    with connect() as connection:

        # Find all existing tables
        cursor = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name LIKE 'session_%'
        """)

        tables = [
            row[0]
            for row in cursor.fetchall()
        ]

        # Extract numeric suffix from each table
        numbers = []

        for table in tables:
            try:
                number = int(table.removeprefix("session_"))
                numbers.append(number)
            except ValueError:
                pass

        # Create the next available session table name
        next_number = max(numbers, default=0) + 1

        table_name = f"session_{next_number}"

        # Build table colums from supplied dict keys
        columns = []

        for key in data:
            if key == "id":
                columns.append(
                    '"id" INTEGER PRIMARY KEY'
                )
            else:
                columns.append(
                    f'"{key}" TEXT'
                )

        # Creates table in the database
        sql = f"""
            CREATE TABLE "{table_name}" (
                {", ".join(columns)}
            )
        """
        connection.execute(sql)
        # Returns newly created table name
        return table_name


def insert_record(data: dict, table_name: str, event_msg: bool = True):
    # Account for unordered dictionary not matching with table columns
    columns = ", ".join(f'"{key}"'for key in data)
    placeholders = ", ".join("?"for _ in data)

    # SQL insert statement
    sql = f"""
        INSERT INTO "{table_name}"
        ({columns})
        VALUES ({placeholders})
    """

    # Execute insert statement
    with connect() as connection:
        cursor = connection.execute(
            sql,
            tuple(data.values())
        )
        record_id = cursor.lastrowid

    # Send windows event message
    if event_msg:
        send_event()

    return record_id


def send_event():
    try:
        # Open windows event
        event = win32event.OpenEvent(
            win32event.EVENT_MODIFY_STATE,
            False,
            EVENT_NAME
        )
        # Broadcast event to notify
        win32event.SetEvent(event)
        # Close event
        win32event.CloseHandle(event)
    except Exception:
        # Website isn't running.
        pass

