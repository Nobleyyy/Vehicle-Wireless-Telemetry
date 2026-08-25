from flask import Blueprint, render_template, request, jsonify, Response
from flask_login import login_required, current_user

from .page_py import live as l
from .page_py import database as d

views = Blueprint("views", __name__)

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

    return l.live_stream()

@views.route("/database")
@login_required
def database():

    tables = d.get_table_names()

    return render_template(
        "database.html",
        tables=tables,
        user=current_user
    )


@views.route("/api/table")
@login_required
def api_table():

    table_name = request.args.get("name")

    data = d.get_table_data(table_name)

    if data is None:
        return jsonify({
            "error": "Invalid table"
        }), 400

    return jsonify(data)

@views.route("/api/table/csv")
@login_required
def download_table_csv():

    table_name = request.args.get("name")

    csv_data = d.get_table_csv(table_name)

    if csv_data is None:
        return jsonify({
            "error": "Invalid table"
        }), 400

    response = Response(
        csv_data,
        mimetype="text/csv"
    )

    response.headers["Content-Disposition"] = (
        f'attachment; filename="{table_name}.csv"'
    )

    return response
