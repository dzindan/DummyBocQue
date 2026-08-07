from flask import Blueprint, render_template

from ..kinhdich import records

bp = Blueprint("home", __name__)


@bp.route("/")
def index():
    recent = records.list_divinations()[:5]
    return render_template("index.html", recent=recent)
