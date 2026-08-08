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


def _chu_hao(moving_positions, hexagram_main):
    n = len(moving_positions)
    positions = sorted(moving_positions)
    if n == 0:
        return None, "Không có hào động: luận theo lời Thoán của quẻ chính, không phân Thể/Dụng."
    if n == 1:
        return positions[0], None
    if n == 2:
        return positions[-1], "2 hào động: lấy hào động ở trên làm chủ hào."
    if n == 3:
        return positions[1], "3 hào động: lấy hào động ở giữa làm chủ hào."
    if n == 4:
        tinh = [p for p in range(1, 7) if p not in positions]
        return tinh[0], "4 hào động: lấy hào tĩnh ở dưới (trong 2 hào còn tĩnh) làm chủ hào."
    if n == 5:
        tinh = [p for p in range(1, 7) if p not in positions]
        return tinh[0], "5 hào động: lấy hào tĩnh duy nhất còn lại làm chủ hào."
    # n == 6
    if hexagram_main["number"] == 1:
        return None, "6 hào động ở quẻ Càn: dùng riêng lời “Dụng Cửu” (kiến quần long vô thủ, cát)."
    if hexagram_main["number"] == 2:
        return None, "6 hào động ở quẻ Khôn: dùng riêng lời “Dụng Lục” (lợi vĩnh trinh)."
    return None, "6 hào động: lấy quẻ biến làm chủ - nội quái quẻ biến là Thể, ngoại quái quẻ biến là Dụng."


def phan_tich(hexagram_main, hexagram_changed, moving_positions):
    chu_hao, note = _chu_hao(moving_positions, hexagram_main)

    if chu_hao is None and hexagram_main["number"] in (1, 2) and len(moving_positions) == 6:
        return {"applicable": False, "note": note}
    if chu_hao is None and not moving_positions:
        return {"applicable": False, "note": note}
    if chu_hao is None and len(moving_positions) == 6:
        # Use quẻ biến's own trigrams: nội (lower) = Thể, ngoại (upper) = Dụng.
        the_code = hexagram_changed["lower_trigram"]
        dung_code = hexagram_changed["upper_trigram"]
    else:
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
