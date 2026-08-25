from pathlib import Path
import sqlite3
import time
import csv
from io import StringIO

DATABASE_FILE = (
    Path(__file__).resolve().parents[3]
    / "Data_Archive"
    / "car_data.db"
)


def get_db():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def get_table_names():
    conn = get_db()

    tables = conn.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name NOT LIKE 'sqlite_%'
        ORDER BY name
    """).fetchall()

    conn.close()

    return [table["name"] for table in tables]

def get_table_data(table_name):

    # Make sure the table exists before using it
    if table_name not in get_table_names():
        return None

    conn = get_db()

    rows = conn.execute(
        f'SELECT * FROM "{table_name}"'
    ).fetchall()

    conn.close()

    columns = list(rows[0].keys()) if rows else []

    formatted_rows = []

    for row in rows:

        record = dict(row)

        if record.get("timestamp"):
            try:
                record["timestamp"] = time.strftime(
                    "%d/%m/%y %H:%M:%S",
                    time.localtime(float(record["timestamp"]))
                )
            except (ValueError, TypeError, OverflowError):
                pass

        formatted_rows.append([
            record[column]
            for column in columns
        ])

    return {
        "table": table_name,
        "columns": columns,
        "rows": formatted_rows
    }

def get_table_csv(table_name):

    data = get_table_data(table_name)

    if data is None:
        return None

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow(data["columns"])
    writer.writerows(data["rows"])

    return output.getvalue()
