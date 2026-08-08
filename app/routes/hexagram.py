from datetime import date

from flask import Blueprint, abort, render_template, request

from ..kinhdich import data_repo, luc_hao, phan_tich, records

bp = Blueprint("hexagram", __name__)


@bp.route("/que")
def list_hexagrams():
    query = request.args.get("q", "").strip().lower()
    items = data_repo.hexagrams()
    if query:
        items = [
            h for h in items
            if query in h["name"].lower() or query in str(h["number"])
        ]
    return render_template("hexagram_list.html", hexagrams=items, query=query)


@bp.route("/que/<int:number>")
def detail(number):
    try:
        hexagram = data_repo.hexagram_by_number(number)
    except KeyError:
        abort(404)
    upper = data_repo.trigram_by_code(hexagram["upper_trigram"])
    lower = data_repo.trigram_by_code(hexagram["lower_trigram"])
    notes = records.list_notes(hexagram_number=number)
    return render_template(
        "hexagram_detail.html",
        hexagram=hexagram,
        upper=upper,
        lower=lower,
        notes=notes,
        hao_vi=phan_tich.hao_vi(hexagram["lines"]),
        que_ho=phan_tich.que_ho(hexagram["lines"]),
        que_doi=phan_tich.que_doi(hexagram["lines"]),
        que_thac=phan_tich.que_thac(hexagram["lines"]),
        luc_hao=luc_hao.phan_tich(number, date.today()),
    )


@bp.route("/que/<int:number>/ghi-chu", methods=["POST"])
def add_note(number):
    content = request.form.get("content", "").strip()
    if content:
        tags = [t.strip() for t in request.form.get("tags", "").split(",") if t.strip()]
        records.save_note(number, content, tags)
    return render_template(
        "_notes_list.html",
        notes=records.list_notes(hexagram_number=number),
        hexagram_number=number,
    )
