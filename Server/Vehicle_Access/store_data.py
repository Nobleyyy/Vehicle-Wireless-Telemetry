### Store Data ###

# Package Imports
from pathlib import Path
import sqlite3
import win32event


EVENT_NAME = r"Global\VehicleAccessNewRecord"

DATABASE_FILE = (
    Path(__file__).resolve().parent.parent
    / "Data_Archive"
    / "car_data.db"
)


def connect():

    DATABASE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(
        DATABASE_FILE,
        timeout=30
    )


def create_table(data):

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

    sql = f"""
        CREATE TABLE IF NOT EXISTS vehicle (
            {", ".join(columns)}
        )
    """

    with connect() as connection:

        connection.execute(sql)



def insert_record(data:dict, event_msg:bool = True):

    columns = ", ".join(
        f'"{key}"'
        for key in data
    )

    placeholders = ", ".join(
        "?"
        for _ in data
    )

    sql = f"""
        INSERT INTO vehicle
        ({columns})
        VALUES ({placeholders})
    """

    with connect() as connection:

        cursor = connection.execute(sql,tuple(data.values()))
        record_id = cursor.lastrowid

    if event_msg:
        send_event()

    return record_id

def send_event():

    try:

        event = win32event.OpenEvent(
            win32event.EVENT_MODIFY_STATE,
            False,
            EVENT_NAME
        )

        win32event.SetEvent(event)

        win32event.CloseHandle(event)

    except Exception:
        # Website isn't running.
        pass

