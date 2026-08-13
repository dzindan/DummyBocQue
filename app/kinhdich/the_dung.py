"""Thể - Dụng analysis for Mai Hoa Dịch Số readings.

Classical Mai Hoa method: of the two trigrams in a cast hexagram, the one
that does NOT contain the "chủ hào" (governing/moving line) is Thể (the
subject / the person asking), the one that DOES contain it is Dụng (the
matter / the object of the question). The reading is then judged by the
ngũ hành relationship between Thể and Dụng.

Which line counts as "chủ hào" depends on how many lines are moving -
this is the standard textbook rule set (not something inferrable purely
from the hexagram itself, so unlike ngu_hanh.py this one is a compiled
convention, flagged accordingly in the UI):

  0 hào động: không có chủ hào - luận theo ý nghĩa lời Thoán của quẻ
              chính, không phân Thể/Dụng.
  1 hào động: chính hào đó là chủ hào.
  2 hào động: lấy hào động ở trên (số thứ tự lớn hơn) làm chủ hào.
  3 hào động: lấy hào động ở giữa (theo thứ tự) làm chủ hào.
  4 hào động: hai hào còn tĩnh - lấy hào tĩnh ở DƯỚI làm chủ hào (đảo
              vai trò: quái chứa hào tĩnh đó là Thể).
  5 hào động: một hào còn tĩnh duy nhất - lấy hào đó làm chủ hào.
  6 hào động: quẻ Càn dùng lời "Dụng Cửu", quẻ Khôn dùng lời "Dụng Lục";
              các quẻ khác lấy quẻ biến làm chủ - nội quái quẻ biến là
              Thể, ngoại quái quẻ biến là Dụng.
"""

from . import data_repo, ngu_hanh

KET_LUAN = {
    "sinh": "Dụng sinh Thể: được giúp đỡ, thuận lợi, việc dễ thành.",
    "duoc_sinh": "Thể sinh Dụng: hao tổn công sức/của cải cho việc này, vất vả mà ít lợi.",
    "khac": "Dụng khắc Thể: bất lợi, dễ gặp cản trở hoặc tổn hại.",
    "bi_khac": "Thể khắc Dụng: việc có thể thành nhưng phải tốn nhiều công sức.",
    "hoa": "Thể Dụng tỷ hòa (cùng ngũ hành): thuận lợi, hòa hợp, việc suôn sẻ.",
}
assert set(KET_LUAN) == set(ngu_hanh.RELATION_KEYS)


# Càn (乾, all 6 lines dương) and Khôn (坤, all 6 lines âm) get their own
# textbook wording ("Dụng Cửu" / "Dụng Lục") at 6 hào động instead of the
# usual quẻ-biến rule - named here so that special case reads as what it
# is rather than bare numbers 1/2.
CAN_HEXAGRAM_NUMBER = 1
KHON_HEXAGRAM_NUMBER = 2


def _chu_hao(moving_positions, hexagram_main):
    """Returns (chu_hao, note, case). `case` names which branch phan_tich()
    below should take, so it doesn't have to re-derive the same
    n/hexagram-number checks made here just to pick `note`'s wording:

      "no_move"      - 0 hào động, no Thể/Dụng split at all
      "normal"       - 1/2/3/5 hào động, the usual "quái chứa chủ hào = Dụng" rule
      "inverted"     - 4 hào động, role inverted (quái chứa chủ hào = Thể)
      "dung_cuu_luc" - 6 hào động on Càn/Khôn, no Thể/Dụng split
      "quai_bien"    - 6 hào động on any other hexagram, judged from quẻ biến
    """
    n = len(moving_positions)
    positions = sorted(moving_positions)
    if n == 0:
        return None, "Không có hào động: luận theo lời Thoán của quẻ chính, không phân Thể/Dụng.", "no_move"
    if n == 1:
        return positions[0], None, "normal"
    if n == 2:
        return positions[-1], "2 hào động: lấy hào động ở trên làm chủ hào.", "normal"
    if n == 3:
        return positions[1], "3 hào động: lấy hào động ở giữa làm chủ hào.", "normal"
    if n == 4:
        tinh = [p for p in range(1, 7) if p not in positions]
        return tinh[0], "4 hào động: lấy hào tĩnh ở dưới (trong 2 hào còn tĩnh) làm chủ hào - đảo vai trò, quái chứa hào tĩnh đó là Thể.", "inverted"
    if n == 5:
        tinh = [p for p in range(1, 7) if p not in positions]
        return tinh[0], "5 hào động: lấy hào tĩnh duy nhất còn lại làm chủ hào.", "normal"
    # n == 6
    if hexagram_main["number"] == CAN_HEXAGRAM_NUMBER:
        return None, "6 hào động ở quẻ Càn: dùng riêng lời “Dụng Cửu” (kiến quần long vô thủ, cát).", "dung_cuu_luc"
    if hexagram_main["number"] == KHON_HEXAGRAM_NUMBER:
        return None, "6 hào động ở quẻ Khôn: dùng riêng lời “Dụng Lục” (lợi vĩnh trinh).", "dung_cuu_luc"
    return None, "6 hào động: lấy quẻ biến làm chủ - nội quái quẻ biến là Thể, ngoại quái quẻ biến là Dụng.", "quai_bien"


def phan_tich(hexagram_main, hexagram_changed, moving_positions):
    chu_hao, note, case = _chu_hao(moving_positions, hexagram_main)

    if case in ("no_move", "dung_cuu_luc"):
        return {"applicable": False, "note": note}

    if case == "quai_bien":
        # Use quẻ biến's own trigrams: nội (lower) = Thể, ngoại (upper) = Dụng.
        the_code = hexagram_changed["lower_trigram"]
        dung_code = hexagram_changed["upper_trigram"]
    elif case == "inverted":
        # 4 hào động: chu_hao is one of the two still-static lines, and per
        # the module docstring the role is INVERTED for this case - the
        # trigram containing that static chủ hào is Thể here, not Dụng like
        # the "normal" case below.
        if chu_hao <= 3:
            the_code = hexagram_main["lower_trigram"]
            dung_code = hexagram_main["upper_trigram"]
        else:
            the_code = hexagram_main["upper_trigram"]
            dung_code = hexagram_main["lower_trigram"]
    else:  # case == "normal"
        if chu_hao <= 3:
            dung_code = hexagram_main["lower_trigram"]
            the_code = hexagram_main["upper_trigram"]
        else:
            dung_code = hexagram_main["upper_trigram"]
            the_code = hexagram_main["lower_trigram"]

    the = data_repo.trigram_by_code(the_code)
    dung = data_repo.trigram_by_code(dung_code)
    quan_he = ngu_hanh.quan_he(dung["ngu_hanh"], the["ngu_hanh"])  # Dụng tác động lên Thể

    return {
        "applicable": True,
        "chu_hao": chu_hao,
        "note": note,
        "the_trigram": the,
        "dung_trigram": dung,
        "quan_he": quan_he,
        "ket_luan": KET_LUAN[quan_he],
    }
