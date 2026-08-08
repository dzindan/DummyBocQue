"""Lục Hào (Kinh Phòng bốc phệ) apparatus: Bát Cung palace classification,
Thế/Ứng, Nạp Giáp (Stem-Branch per line), Lục Thân (six relations), and
Lục Thần (six spirits).

Everything here is DERIVED BY ALGORITHM from a small set of rules, rather
than hand-transcribed per-hexagram/per-line, precisely because a 384-cell
hand-built table is extremely easy to get subtly wrong. The rules
themselves were cross-checked against multiple Chinese-language sources
before being encoded here (see project chat history) - only the base
per-trigram tables (NAP_GIAP, palace order) and the small fixed
generation/spirit-cycle rules are "looked up"; everything else (which
hexagram is in which palace, each line's Can/Chi, mỗi hào's Lục Thân) is
computed, so it is internally consistent by construction across all 64
hexagrams x 6 lines.
"""

from functools import lru_cache

from . import data_repo, ngu_hanh
from .canchi import THIEN_CAN, day_can_chi

# 8 palace trigrams in a fixed order, keyed by trigram code (see
# generate_data.py TRIGRAMS) - order doesn't affect correctness, just
# iteration.
PALACE_TRIGRAMS = ["cAN", "khon", "chan", "ton", "kham", "ly", "can2", "doai"]

STEP_LABELS = {
    "bon_cung": "Bổn cung",
    "nhat_the": "Nhất thế",
    "nhi_the": "Nhị thế",
    "tam_the": "Tam thế",
    "tu_the": "Tứ thế",
    "ngu_the": "Ngũ thế",
    "du_hon": "Du hồn",
    "quy_hon": "Quy hồn",
}
STEP_THE_HAO = {
    "bon_cung": 6, "nhat_the": 1, "nhi_the": 2, "tam_the": 3,
    "tu_the": 4, "ngu_the": 5, "du_hon": 4, "quy_hon": 3,
}


def _generate_palace_lines(bon_cung_lines):
    """8 line-patterns for one palace, per the verified Kinh Phòng rule."""
    bon = list(bon_cung_lines)
    nhat = list(bon); nhat[0] ^= 1
    nhi = list(nhat); nhi[1] ^= 1
    tam = list(nhi); tam[2] ^= 1
    tu = list(tam); tu[3] ^= 1
    ngu = list(tu); ngu[4] ^= 1
    du_hon = list(ngu); du_hon[3] = bon[3]  # revert line 4 to bổn cung value
    quy_hon = list(du_hon); quy_hon[0:3] = bon[0:3]  # revert lower trigram to bổn cung
    return {
        "bon_cung": bon, "nhat_the": nhat, "nhi_the": nhi, "tam_the": tam,
        "tu_the": tu, "ngu_the": ngu, "du_hon": du_hon, "quy_hon": quy_hon,
    }


@lru_cache(maxsize=1)
def _bat_cung_table():
    """hexagram number -> {palace_trigram, palace_ngu_hanh, step, the_hao, ung_hao}."""
    table = {}
    for palace_code in PALACE_TRIGRAMS:
        trigram = data_repo.trigram_by_code(palace_code)
        bon_cung_lines = trigram["lines"] + trigram["lines"]
        for step, lines in _generate_palace_lines(bon_cung_lines).items():
            hexagram = data_repo.hexagram_by_lines(lines)
            the_hao = STEP_THE_HAO[step]
            ung_hao = the_hao + 3 if the_hao <= 3 else the_hao - 3
            table[hexagram["number"]] = {
                "palace_trigram": palace_code,
                "palace_name": trigram["name"],
                "palace_ngu_hanh": trigram["ngu_hanh"],
                "step": step,
                "step_label": STEP_LABELS[step],
                "the_hao": the_hao,
                "ung_hao": ung_hao,
            }
    assert len(table) == 64, f"Bát Cung generation produced {len(table)} hexagrams, expected 64"
    return table


def bat_cung_info(hexagram_number: int) -> dict:
    return _bat_cung_table()[hexagram_number]


# Nạp Giáp base table: for each trigram, Thiên Can when used as inner
# (lower/nội) vs outer (ngoại/thượng) trigram, and the 3 Địa Chi (bottom
# to top) for each position.
NAP_GIAP = {
    "cAN":  {"can_noi": "Giáp", "can_ngoai": "Nhâm", "chi_noi": ["Tý", "Dần", "Thìn"], "chi_ngoai": ["Ngọ", "Thân", "Tuất"]},
    "khon": {"can_noi": "Ất",   "can_ngoai": "Quý",  "chi_noi": ["Mùi", "Tị", "Mão"],  "chi_ngoai": ["Sửu", "Hợi", "Dậu"]},
    "chan": {"can_noi": "Canh", "can_ngoai": "Canh", "chi_noi": ["Tý", "Dần", "Thìn"], "chi_ngoai": ["Ngọ", "Thân", "Tuất"]},
    "ton":  {"can_noi": "Tân",  "can_ngoai": "Tân",  "chi_noi": ["Sửu", "Hợi", "Dậu"], "chi_ngoai": ["Mùi", "Tị", "Mão"]},
    "kham": {"can_noi": "Mậu",  "can_ngoai": "Mậu",  "chi_noi": ["Dần", "Thìn", "Ngọ"], "chi_ngoai": ["Thân", "Tuất", "Tý"]},
    "ly":   {"can_noi": "Kỷ",   "can_ngoai": "Kỷ",   "chi_noi": ["Mão", "Sửu", "Hợi"], "chi_ngoai": ["Dậu", "Mùi", "Tị"]},
    "can2": {"can_noi": "Bính", "can_ngoai": "Bính", "chi_noi": ["Thìn", "Ngọ", "Thân"], "chi_ngoai": ["Tuất", "Tý", "Dần"]},
    "doai": {"can_noi": "Đinh", "can_ngoai": "Đinh", "chi_noi": ["Tị", "Mão", "Sửu"], "chi_ngoai": ["Hợi", "Dậu", "Mùi"]},
}

CHI_NGU_HANH = {
    "Tý": "Thủy", "Sửu": "Thổ", "Dần": "Mộc", "Mão": "Mộc", "Thìn": "Thổ", "Tị": "Hỏa",
    "Ngọ": "Hỏa", "Mùi": "Thổ", "Thân": "Kim", "Dậu": "Kim", "Tuất": "Thổ", "Hợi": "Thủy",
}

SIX_RELATIONS = {
    "sinh": "Phụ Mẫu",       # cái sinh ta
    "duoc_sinh": "Tử Tôn",   # ta sinh ra nó
    "khac": "Quan Quỷ",      # cái khắc ta
    "bi_khac": "Thê Tài",    # ta khắc nó
    "hoa": "Huynh Đệ",       # cùng ngũ hành với ta
}

SIX_SPIRITS = ["Thanh Long", "Chu Tước", "Câu Trần", "Đằng Xà", "Bạch Hổ", "Huyền Vũ"]
# day Can index (0=Giáp..9=Quý) -> starting spirit index for line 1
_SPIRIT_START = {0: 0, 1: 0, 2: 1, 3: 1, 4: 2, 5: 3, 6: 4, 7: 4, 8: 5, 9: 5}


def nap_giap(lower_code: str, upper_code: str) -> list:
    """6 lines (bottom to top), each {can, chi, chi_ngu_hanh}."""
    lower = NAP_GIAP[lower_code]
    upper = NAP_GIAP[upper_code]
    lines = []
    for i in range(3):
        chi = lower["chi_noi"][i]
        lines.append({"can": lower["can_noi"], "chi": chi, "ngu_hanh": CHI_NGU_HANH[chi]})
    for i in range(3):
        chi = upper["chi_ngoai"][i]
        lines.append({"can": upper["can_ngoai"], "chi": chi, "ngu_hanh": CHI_NGU_HANH[chi]})
    return lines


def luc_than_spirits(ngay_can_idx: int) -> list:
    """6 spirits (bottom to top) for the given day-Can index (0=Giáp..9=Quý)."""
    start = _SPIRIT_START[ngay_can_idx]
    return [SIX_SPIRITS[(start + i) % 6] for i in range(6)]


def phan_tich(hexagram_number: int, cast_date) -> dict:
    """Full Lục Hào analysis for a hexagram cast on `cast_date` (a
    datetime.date/datetime), used to derive the day-Can that seeds Lục
    Thần placement (Nạp Giáp and Lục Thân don't depend on the date)."""
    hexagram = data_repo.hexagram_by_number(hexagram_number)
    palace = bat_cung_info(hexagram_number)
    giap = nap_giap(hexagram["lower_trigram"], hexagram["upper_trigram"])

    day_can_idx, _ = day_can_chi(cast_date.day, cast_date.month, cast_date.year)
    spirits = luc_than_spirits(day_can_idx)

    lines = []
    for i in range(6):
        pos = i + 1
        quan_he = ngu_hanh.quan_he(giap[i]["ngu_hanh"], palace["palace_ngu_hanh"])
        lines.append({
            "position": pos,
            "can": giap[i]["can"],
            "chi": giap[i]["chi"],
            "chi_ngu_hanh": giap[i]["ngu_hanh"],
            "luc_than": SIX_RELATIONS[quan_he],
            "luc_than_spirit": spirits[i],
            "la_the": pos == palace["the_hao"],
            "la_ung": pos == palace["ung_hao"],
        })

    return {
        "hexagram": hexagram,
        "palace": palace,
        "ngay_can": THIEN_CAN[day_can_idx],
        "lines": lines,
    }
