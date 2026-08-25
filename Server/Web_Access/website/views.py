from flask import Blueprint, render_template, request
from flask_login import login_required, current_user

from .page_py import live as l

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