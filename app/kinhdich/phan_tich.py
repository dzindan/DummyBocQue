"""Structural analysis of a hexagram's 6 lines and its related
hexagrams - hào vị (line position quality), quẻ Hỗ/Đối/Thác. Everything
here is derived purely by computation from the `lines` array (bottom to
top, 1=dương/0=âm), not looked up from any external source, so it carries
no sourcing/accuracy risk the way textual content does.
"""

from . import data_repo

HAO_LABELS_DUONG = ["Sơ Cửu", "Cửu Nhị", "Cửu Tam", "Cửu Tứ", "Cửu Ngũ", "Thượng Cửu"]
HAO_LABELS_AM = ["Sơ Lục", "Lục Nhị", "Lục Tam", "Lục Tứ", "Lục Ngũ", "Thượng Lục"]


def hao_label(position: int, value: int) -> str:
    idx = position - 1
    return HAO_LABELS_DUONG[idx] if value == 1 else HAO_LABELS_AM[idx]


def hao_vi(lines: list) -> list:
    """Per-line position analysis, position 1..6 (bottom to top).

    - dac_vi: vị trí lẻ (1,3,5) nên là hào dương, vị trí chẵn (2,4,6) nên
      là hào âm - đúng thì "đắc vị/đắc chính", sai thì "thất vị".
    - trung: hào 2 và hào 5 (giữa mỗi quái đơn) luôn "đắc trung".
    - ung_voi / chinh_ung: hào 1-4, 2-5, 3-6 là cặp ứng; khác âm dương
      (1 âm 1 dương) thì "chính ứng" (hô ứng tốt), cùng tính thì "bất ứng".
    """
    out = []
    for i in range(6):
        pos = i + 1
        val = lines[i]
        is_odd_pos = pos in (1, 3, 5)
        dac_vi = (is_odd_pos and val == 1) or (not is_odd_pos and val == 0)
        trung = pos in (2, 5)
        ung_pos = pos + 3 if pos <= 3 else pos - 3
        chinh_ung = lines[ung_pos - 1] != val
        out.append({
            "position": pos,
            "label": hao_label(pos, val),
            "value": val,
            "dac_vi": dac_vi,
            "trung": trung,
            "trung_chinh": trung and dac_vi,
            "ung_voi": ung_pos,
            "chinh_ung": chinh_ung,
        })
    return out


def que_ho(lines: list) -> dict:
    """Quẻ Hỗ (nuclear/interlocking hexagram): lower trigram = lines
    2-3-4, upper trigram = lines 3-4-5 of the original hexagram."""
    ho_lines = [lines[1], lines[2], lines[3], lines[2], lines[3], lines[4]]
    return data_repo.hexagram_by_lines(ho_lines)


def que_doi(lines: list) -> dict:
    """Quẻ Đối/Tổng (nghịch - the hexagram read upside down: reverse the
    line order top-to-bottom)."""
    return data_repo.hexagram_by_lines(list(reversed(lines)))


def que_thac(lines: list) -> dict:
    """Quẻ Thác/Thố (the complementary hexagram: every line's yin/yang
    flipped)."""
    return data_repo.hexagram_by_lines([1 - v for v in lines])
