### Flask Views ###

# Package Imports
from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user

# File Imports
from .page_py import live_graph as lg
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
    # Keep /live?stream=1 as the SSE endpoint
    if request.args.get("stream") == "1":
        return lg.live_stream()

    # /live itself now goes to the dashboard
    return render_template(
        "live-dashboard.html",
        user=current_user
    )


@views.route("/live-dashboard")
@login_required
def live_dashboard():
    # Display live dashboard page
    return render_template(
        "live-dashboard.html",
        user=current_user
    )


@views.route("/live-graph")
@login_required
def live_graph():
    # Display live graph page
    return render_template(
        "live-graph.html",
        user=current_user
    )


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

@views.route("/api/tables")
@login_required
def api_tables():
    # Get current database tables
    tables = d.get_table_names()

    return jsonify({
        "tables": tables
    })

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

@views.route("/api/table/delete", methods=["DELETE"])
@login_required
def delete_table():
    # Only administrators can delete tables
    if not current_user.admin:
        return jsonify({
            "error": "Admin access required"
        }), 403
    # Get requested table
    table_name = request.args.get("name")
    if not table_name:
        return jsonify({
            "error": "No table specified"
        }), 400
    # Delete the table
    if not d.delete_table(table_name):
        return jsonify({
            "error": "Invalid table or unable to delete table"
        }), 400

    return jsonify({
        "success": True,
        "table": table_name
    })
