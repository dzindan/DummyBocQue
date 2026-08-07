from datetime import datetime

from flask import Blueprint, abort, redirect, render_template, request, url_for

from ..kinhdich import data_repo, maihoa, manual_cast, records

bp = Blueprint("divination", __name__)

LINE_STATE_LABELS = [
    ("duong_tinh", "Dương tĩnh (⚊)"),
    ("am_tinh", "Âm tĩnh (⚋)"),
    ("duong_dong", "Dương động - Lão dương (⚊ động)"),
    ("am_dong", "Âm động - Lão âm (⚋ động)"),
]


def _all_question_templates():
    return list(data_repo.question_templates()) + records.list_custom_question_templates()


@bp.route("/gieo-que")
def form():
    now = datetime.now()
    return render_template(
        "divination_form.html",
        now_value=now.strftime("%Y-%m-%dT%H:%M"),
        templates=_all_question_templates(),
        line_state_labels=LINE_STATE_LABELS,
    )


@bp.route("/gieo-que/mai-hoa", methods=["POST"])
def cast_mai_hoa():
    dt_raw = request.form["datetime"]
    is_manual = request.form.get("is_manual_datetime") == "on"
    question = request.form.get("question", "").strip()
    category = request.form.get("category") or None

    dt = datetime.strptime(dt_raw, "%Y-%m-%dT%H:%M")
    result = maihoa.calculate(dt.day, dt.month, dt.year, dt.hour)

    record = records.save_divination({
        "method": "mai_hoa",
        "question": question,
        "category_tag": category,
        "input_datetime": dt.isoformat(),
        "is_manual_datetime": is_manual,
        "lunar": result["lunar"],
        "can_chi": result["can_chi"],
        "hexagram_main_number": result["hexagram_main"]["number"],
        "hexagram_changed_number": result["hexagram_changed"]["number"],
        "main_lines": result["main_lines"],
        "changed_lines": result["changed_lines"],
        "moving_positions": [result["dong_hao"]],
    })
    return redirect(url_for("divination.detail", record_id=record["id"]))


@bp.route("/gieo-que/tay", methods=["POST"])
def cast_manual():
    dt_raw = request.form["datetime"]
    is_manual = request.form.get("is_manual_datetime") == "on"
    question = request.form.get("question", "").strip()
    category = request.form.get("category") or None
    states = [request.form.get(f"hao_{i}") for i in range(1, 7)]

    dt = datetime.strptime(dt_raw, "%Y-%m-%dT%H:%M")
    try:
        result = manual_cast.resolve(states)
    except ValueError:
        abort(400)

    record = records.save_divination({
        "method": "manual_6_hao",
        "question": question,
        "category_tag": category,
        "input_datetime": dt.isoformat(),
        "is_manual_datetime": is_manual,
        "lunar": None,
        "can_chi": None,
        "hexagram_main_number": result["hexagram_main"]["number"],
        "hexagram_changed_number": result["hexagram_changed"]["number"] if result["hexagram_changed"] else None,
        "main_lines": result["main_lines"],
        "changed_lines": result["changed_lines"],
        "moving_positions": result["moving_positions"],
    })
    return redirect(url_for("divination.detail", record_id=record["id"]))


def _enrich(record):
    """Attach full hexagram/trigram objects to a stored record for display."""
    record = dict(record)
    record["hexagram_main"] = data_repo.hexagram_by_number(record["hexagram_main_number"])
    record["hexagram_changed"] = (
        data_repo.hexagram_by_number(record["hexagram_changed_number"])
        if record.get("hexagram_changed_number") else None
    )
    upper_code = record["hexagram_main"]["upper_trigram"]
    record["upper_trigram"] = data_repo.trigram_by_code(upper_code)
    record["show_weather_direction"] = record.get("category_tag") in ("Thời tiết", "Xuất hành")
    return record


@bp.route("/lich-su")
def history():
    items = [_enrich(r) for r in records.list_divinations()]
    return render_template("history_list.html", items=items)


@bp.route("/lich-su/<record_id>")
def detail(record_id):
    record = records.get_divination(record_id)
    if not record:
        abort(404)
    return render_template("divination_detail.html", record=_enrich(record))


@bp.route("/lich-su/<record_id>/ghi-chu", methods=["POST"])
def update_note(record_id):
    note = request.form.get("note", "")
    records.update_divination_note(record_id, note)
    return redirect(url_for("divination.detail", record_id=record_id))


@bp.route("/lich-su/<record_id>/xoa", methods=["POST"])
def delete(record_id):
    records.delete_divination(record_id)
    return redirect(url_for("divination.history"))
