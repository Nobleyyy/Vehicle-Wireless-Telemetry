from flask import Blueprint, render_template, Response, request
from flask_login import login_required, current_user

from pathlib import Path
import sqlite3
import threading
import queue
import json
import win32event
import win32api


views = Blueprint("views", __name__)


EVENT_NAME = r"Global\VehicleAccessNewRecord"

DATABASE_FILE = (
    Path(__file__).resolve().parents[2]
    / "Data_Archive"
    / "car_data.db"
)


@views.route("/")
@login_required
def home():

    return render_template(
        "home.html",
        user=current_user
    )


@views.route("/live")
@login_required
def live():

    if request.args.get("stream") != "1":

        return render_template(
            "live.html",
            user=current_user
        )

    return live_stream()


def get_latest_entry():

    with sqlite3.connect(
        DATABASE_FILE,
        timeout=30
    ) as connection:

        cursor = connection.execute("""
            SELECT *
            FROM vehicle
            ORDER BY ID DESC
            LIMIT 1
        """)

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            description[0]
            for description in cursor.description
        ]

        return dict(
            zip(columns, row)
        )

def live_stream():
    messages = queue.Queue()
    stop_event = threading.Event()

    def database_listener():
        event = win32event.CreateEvent(
            None,
            True,
            False,
            EVENT_NAME
        )

        try:
            while not stop_event.is_set():
                result = win32event.WaitForSingleObject(
                    event,
                    1000
                )
                if result == win32event.WAIT_OBJECT_0:
                    record = get_latest_entry()
                    if record is not None:
                        messages.put(record)
                    win32event.ResetEvent(event)

        finally:
            win32api.CloseHandle(event)

    thread = threading.Thread(target=database_listener, daemon=True)
    thread.start()

    def generate():
        try:
            while True:
                record = messages.get()
                yield ("data: " + json.dumps(record) + "\n\n")

        finally:
            stop_event.set()

    return Response(generate(), mimetype="text/event-stream")