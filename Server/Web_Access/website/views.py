### Flask Views ###

# Package Imports
from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user

# File Imports
from .page_py import live as l
from .page_py import database as d

views = Blueprint("views", __name__)

## Functions ##
@views.route("/")
@login_required
def home():
    # Display home page
    return render_template(
        "home.html",
        user=current_user
    )


@views.route("/live")
@login_required
def live():
    # Display live data page
    if request.args.get("stream") != "1":
        return render_template(
            "live.html",
            user=current_user
        )
    # Start live data stream thread
    return l.live_stream()


@views.route("/database")
@login_required
def database():
    # Get available database tables
    tables = d.get_table_names()
    # Display database page
    return render_template(
        "database.html",
        tables=tables,
        user=current_user
    )


@views.route("/api/table")
@login_required
def api_table():
    # Get requested table
    table_name = request.args.get("name")
    # Retrieve data from the requested table
    data = d.get_table_data(table_name)
    # Return error if table does not exist
    if data is None:
        return jsonify({
            "error": "Invalid table"
        }), 400

    return jsonify(data)


@views.route("/api/table/csv")
@login_required
def download_table_csv():
    # Get requested table
    table_name = request.args.get("name")
    # Generate CSV of requested table
    csv_data = d.get_table_csv(table_name)
    # Return error if table does not exist
    if csv_data is None:
        return jsonify({
            "error": "Invalid table"
        }), 400
    # Build response of CSV data
    response = Response(
        csv_data,
        mimetype="text/csv"
    )
    # Inform the browser to download CSV file
    response.headers["Content-Disposition"] = (
        f'attachment; filename="{table_name}.csv"'
    )

    return response
