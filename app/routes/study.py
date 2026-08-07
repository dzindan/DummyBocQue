import json

from flask import Blueprint, render_template

from ..kinhdich import data_repo

bp = Blueprint("study", __name__)


@bp.route("/hoc")
def quiz():
    hexagrams = [
        {"number": h["number"], "name": h["name"], "lines": h["lines"]}
        for h in data_repo.hexagrams()
    ]
    return render_template("study.html", hexagrams_json=json.dumps(hexagrams, ensure_ascii=False))
