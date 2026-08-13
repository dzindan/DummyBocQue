from datetime import date, datetime

from flask import Blueprint, abort, redirect, render_template, request, url_for

from ..kinhdich import data_repo, luc_hao, maihoa, manual_cast, nap_am, ngu_hanh, phan_tich, records, the_dung, vn_time

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
    now = vn_time.now()
    return render_template(
        "divination_form.html",
        now_value=now.strftime("%Y-%m-%dT%H:%M"),
        templates=_all_question_templates(),
        line_state_labels=LINE_STATE_LABELS,
    )


def _nguoi_xem_from_form():
    ho_ten = request.form.get("ho_ten", "").strip()
    ngay_sinh_raw = request.form.get("ngay_sinh", "").strip()
    ngay_sinh = None
    if ngay_sinh_raw:
        try:
            ngay_sinh = datetime.strptime(ngay_sinh_raw, "%Y-%m-%d").date().isoformat()
        except ValueError:
            abort(400)
    return {"ho_ten": ho_ten, "ngay_sinh": ngay_sinh}


def _parse_form_datetime(raw: str) -> datetime:
    try:
        return datetime.strptime(raw, "%Y-%m-%dT%H:%M")
    except ValueError:
        abort(400)


def _save_cast(method, dt, is_manual, question, category, nguoi_xem,
                hexagram_main, hexagram_changed, main_lines, changed_lines,
                moving_positions, extra=None):
    """Common shape shared by cast_mai_hoa/cast_manual below, so a field
    added to one isn't silently missing from the other - each used to
    hand-build its own near-identical dict, and had already drifted on how
    moving_positions was represented (mai_hoa: a single int wrapped in a
    list; manual: a real list) before being unified into one shape here."""
    record = {
        "method": method,
        "question": question,
        "category_tag": category,
        "input_datetime": dt.isoformat(),
        "is_manual_datetime": is_manual,
        "hexagram_main_number": hexagram_main["number"],
        "hexagram_changed_number": hexagram_changed["number"] if hexagram_changed else None,
        "main_lines": main_lines,
        "changed_lines": changed_lines,
        "moving_positions": moving_positions,
        "nguoi_xem": nguoi_xem,
    }
    if extra:
        record.update(extra)
    return records.save_divination(record)


@bp.route("/gieo-que/mai-hoa", methods=["POST"])
def cast_mai_hoa():
    dt = _parse_form_datetime(request.form["datetime"])
    is_manual = request.form.get("is_manual_datetime") == "on"
    question = request.form.get("question", "").strip()
    category = request.form.get("category") or None
    nguoi_xem = _nguoi_xem_from_form()

    # "Giờ động tâm" isn't a different formula - it's this same Mai Hoa
    # cast, just insisting on the unedited current moment. So: leave the
    # datetime field untouched and it counts as động tâm automatically;
    # edit it (is_manual) and it's an ordinary chosen-time cast.
    result = maihoa.calculate(dt.day, dt.month, dt.year, dt.hour)
    record = _save_cast(
        "mai_hoa", dt, is_manual, question, category, nguoi_xem,
        result["hexagram_main"], result["hexagram_changed"],
        result["main_lines"], result["changed_lines"], [result["dong_hao"]],
        extra={"la_dong_tam": not is_manual, "lunar": result["lunar"], "can_chi": result["can_chi"]},
    )
    return redirect(url_for("divination.detail", record_id=record["id"]))


@bp.route("/gieo-que/tay", methods=["POST"])
def cast_manual():
    dt_raw = request.form["datetime"]
    is_manual = request.form.get("is_manual_datetime") == "on"
    question = request.form.get("question", "").strip()
    category = request.form.get("category") or None
    nguoi_xem = _nguoi_xem_from_form()
    coin_tosses = [
        [request.form.get(f"xu_{hao}_{xu}") for xu in range(1, 4)]
        for hao in range(1, 7)
    ]

    dt = _parse_form_datetime(dt_raw)
    try:
        result = manual_cast.resolve_from_coins(coin_tosses)
    except ValueError:
        abort(400)

    record = _save_cast(
        "manual_6_hao", dt, is_manual, question, category, nguoi_xem,
        result["hexagram_main"], result["hexagram_changed"],
        result["main_lines"], result["changed_lines"], result["moving_positions"],
        extra={"lunar": None, "can_chi": None, "coin_tosses": coin_tosses},
    )
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
    record["show_weather_direction"] = data_repo.category_needs_direction(record.get("category_tag"))
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
    record = _enrich(record)
    the_dung_result = the_dung.phan_tich(
        record["hexagram_main"], record["hexagram_changed"], record["moving_positions"]
    )
    cast_date = datetime.fromisoformat(record["input_datetime"])
    luc_hao_result = luc_hao.phan_tich(record["hexagram_main"]["number"], cast_date)
    hao_vi = phan_tich.hao_vi(record["hexagram_main"]["lines"])
    ban_menh = _ban_menh_analysis(record, luc_hao_result, the_dung_result)
    return render_template(
        "divination_detail.html",
        record=record, the_dung=the_dung_result, luc_hao=luc_hao_result, hao_vi=hao_vi, ban_menh=ban_menh,
    )


def _ban_menh_analysis(record, luc_hao_result, the_dung_result):
    """Compares the querent's birth-year Nạp Âm element against the
    hexagram, when a birth date was given. None if no birth date, or if
    the Nạp Âm table hasn't been compiled yet."""
    ngay_sinh = record.get("nguoi_xem", {}).get("ngay_sinh")
    if not ngay_sinh:
        return None

    try:
        # ngay_sinh is stored exactly as date.isoformat() produced it (see
        # _nguoi_xem_from_form) - fromisoformat is its precise inverse, no
        # need to redeclare the format string a second time here.
        d = date.fromisoformat(ngay_sinh)
    except ValueError:
        # Stored ngay_sinh isn't a clean ISO date string (hand-edited data,
        # schema drift...) - treat like no birth date given rather than
        # taking down the whole detail page for this record.
        return None

    menh = nap_am.for_year(d.day, d.month, d.year)
    if menh is None:
        # Nạp Âm table hasn't been compiled yet - check for_year()'s own
        # return value directly rather than a separate is_available() call,
        # so this can't drift out of sync with what for_year() actually did.
        return None

    # Compare against Thể quái when Thể-Dụng is applicable (it represents
    # the querent), else fall back to the hexagram's own palace element.
    if the_dung_result.get("applicable"):
        doi_chieu_voi = the_dung_result["the_trigram"]["ngu_hanh"]
        doi_chieu_nhan = f"Thể quái ({the_dung_result['the_trigram']['name']})"
    else:
        doi_chieu_voi = luc_hao_result["palace"]["palace_ngu_hanh"]
        doi_chieu_nhan = f"cung của quẻ ({luc_hao_result['palace']['palace_name']})"

    quan_he = ngu_hanh.quan_he(doi_chieu_voi, menh["ngu_hanh"])
    KET_LUAN = {
        "sinh": f"{doi_chieu_nhan} sinh cho bản mệnh: thuận lợi, được trợ giúp.",
        "duoc_sinh": f"Bản mệnh sinh cho {doi_chieu_nhan}: hao tổn, phải bỏ công sức.",
        "khac": f"{doi_chieu_nhan} khắc bản mệnh: bất lợi, cần thận trọng.",
        "bi_khac": f"Bản mệnh khắc {doi_chieu_nhan}: việc thành nhưng vất vả.",
        "hoa": f"Bản mệnh cùng ngũ hành với {doi_chieu_nhan}: hòa hợp, thuận lợi.",
    }
    assert set(KET_LUAN) == set(ngu_hanh.RELATION_KEYS)
    return {
        "menh": menh,
        "doi_chieu_voi": doi_chieu_voi,
        "doi_chieu_nhan": doi_chieu_nhan,
        "quan_he": quan_he,
        "ket_luan": KET_LUAN[quan_he],
    }


@bp.route("/lich-su/<record_id>/ghi-chu", methods=["POST"])
def update_note(record_id):
    note = request.form.get("note", "")
    records.update_divination_note(record_id, note)
    return redirect(url_for("divination.detail", record_id=record_id))


@bp.route("/lich-su/<record_id>/xoa", methods=["POST"])
def delete(record_id):
    records.delete_divination(record_id)
    return redirect(url_for("divination.history"))
