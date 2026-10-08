### Live Pages Python ###

# Package Imports
from flask import Response
from pathlib import Path
import sqlite3
import threading
import queue
import json
import time
import win32event
import win32api

EVENT_NAME = r"Global\VehicleAccessNewRecord"

DATABASE_FILE = (
    Path(__file__).resolve().parents[3]
    / "Data_Archive"
    / "car_data.db"
)

## Functions ##
def get_latest_entry():
    # Connect to the database with a timeout for locked databases
    with sqlite3.connect(DATABASE_FILE, timeout=30) as connection:
        # Find the latest session table
        cursor = connection.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
              AND name GLOB 'session_[0-9]*'
            ORDER BY CAST(
                SUBSTR(name, 9) AS INTEGER
            ) DESC
            LIMIT 1
        """)
        result = cursor.fetchone()
        if result is None:
            return None
        table_name = result[0]
        # Read the latest record from the latest session table
        cursor = connection.execute(
            f"""
                SELECT *
                FROM "{table_name}"
                ORDER BY id DESC
                LIMIT 1
            """
        )
         # Get the column names and combine them with the row values
        row = cursor.fetchone()
        if row is None:
            return None
        columns = [
            description[0]
            for description in cursor.description
        ]
        record = dict(zip(columns, row))
        # Convert the Unix timestamp into a human-readable date and time
        if record.get("timestamp"):
            try:
                record["timestamp"] = time.strftime(
                    "%Y-%m-%d %H:%M:%S",
                    time.localtime(float(record["timestamp"]))
                )
            except (ValueError, TypeError, OverflowError):
                pass

        return record

def live_stream():
    # Queue used to pass database records from the listener thread
    messages = queue.Queue()
    # Event used to stop the listener thread when the client disconnects
    stop_event = threading.Event()
    
    def database_listener():
        # Create a named Windows event used to detect new database records
        event = win32event.CreateEvent(
            None,
            True,
            False,
            EVENT_NAME
        )
        # Track when data was last received so a waiting message can be sent
        last_data_time = time.time()
        waiting_sent = False

        try:
            while not stop_event.is_set():
                # Wait for a database change or check periodically for a timeout
                result = win32event.WaitForSingleObject(
                    event,
                    1000
                )

                if result == win32event.WAIT_OBJECT_0:
                    # Retrieve the newest record when new data is available
                    record = get_latest_entry()

                    if record is not None:
                        messages.put(record)

                        # Reset the waiting message timer
                        last_data_time = time.time()
                        waiting_sent = False

                    win32event.ResetEvent(event)

                # No new event/data for 30 seconds
                if (
                    not waiting_sent
                    and time.time() - last_data_time >= 30
                ):
                    messages.put({
                        "status": "Waiting for data to recommence..."
                    })

                    waiting_sent = True

        finally:
            # Close the Windows event when the listener thread stops
            win32api.CloseHandle(event)
    # Run the database listener in a background thread
    thread = threading.Thread(target=database_listener, daemon=True)
    thread.start()

    def generate():
        try:
            while True:
                # Wait for the next record or status message
                record = messages.get()
                # Send the record to the browser using Server-Sent Events
                yield ("data: " + json.dumps(record) + "\n\n")
        finally:
            stop_event.set()
    # Return a streaming response using the Server-Sent Events format
    return Response(generate(), mimetype="text/event-stream")