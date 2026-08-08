"""Ngũ hành sinh khắc (Five Elements generation/overcoming cycle) - the
same fixed cycle regardless of context, used by both Thể-Dụng analysis
and (later) Lục Hào lục thân derivation.
"""

SINH_CYCLE = {"Kim": "Thủy", "Thủy": "Mộc", "Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim"}
KHAC_CYCLE = {"Kim": "Mộc", "Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim"}


def quan_he(a: str, b: str) -> str:
    """Ngũ hành relationship of a -> b, from a's perspective.

    Returns one of: "sinh" (a sinh b), "khac" (a khắc b), "duoc_sinh" (b
    sinh a), "bi_khac" (b khắc a), "hoa" (cùng ngũ hành, tỷ hòa).
    """
    if a == b:
        return "hoa"
    if SINH_CYCLE[a] == b:
        return "sinh"
    if KHAC_CYCLE[a] == b:
        return "khac"
    if SINH_CYCLE[b] == a:
        return "duoc_sinh"
    if KHAC_CYCLE[b] == a:
        return "bi_khac"
    raise ValueError(f"Unreachable ngũ hành pair: {a}, {b}")
