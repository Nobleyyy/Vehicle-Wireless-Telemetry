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


def create_session_table(data):

    with connect() as connection:

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

        numbers = []

        for table in tables:

            try:
                number = int(table.removeprefix("session_"))
                numbers.append(number)

            except ValueError:
                pass

        next_number = max(numbers, default=0) + 1

        table_name = f"session_{next_number}"

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
            CREATE TABLE "{table_name}" (
                {", ".join(columns)}
            )
        """

        connection.execute(sql)

        return table_name




def insert_record(
    data: dict,
    table_name: str,
    event_msg: bool = True
):

    columns = ", ".join(
        f'"{key}"'
        for key in data
    )

    placeholders = ", ".join(
        "?"
        for _ in data
    )

    sql = f"""
        INSERT INTO "{table_name}"
        ({columns})
        VALUES ({placeholders})
    """

    with connect() as connection:

        cursor = connection.execute(
            sql,
            tuple(data.values())
        )

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

