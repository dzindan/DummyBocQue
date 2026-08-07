from flask import Blueprint, redirect, render_template, request, url_for

from ..kinhdich import data_repo, records

bp = Blueprint("notes", __name__)


@bp.route("/ghi-chu")
def list_notes():
    notes = records.list_notes()
    for n in notes:
        n["hexagram"] = data_repo.hexagram_by_number(n["hexagram_number"])
    return render_template("notes_list.html", notes=notes)


@bp.route("/ghi-chu/<note_id>/xoa", methods=["POST"])
def delete(note_id):
    records.delete_note(note_id)
    return redirect(url_for("notes.list_notes"))
