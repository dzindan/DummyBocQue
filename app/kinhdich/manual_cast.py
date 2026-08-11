"""Resolves a hexagram from 6 hand-entered line states (the result of a
physical coin toss / yarrow-stalk cast done outside the app).

Each line, bottom (hào 1) to top (hào 6), is one of:
  duong_tinh  - dương tĩnh (young yang)
  am_tinh     - âm tĩnh (young yin)
  duong_dong  - dương động / Lão dương (old yang, changes to yin)
  am_dong     - âm động / Lão âm (old yin, changes to yang)
"""

from . import data_repo

VALID_STATES = {"duong_tinh", "am_tinh", "duong_dong", "am_dong"}
IS_YANG = {"duong_tinh": True, "duong_dong": True, "am_tinh": False, "am_dong": False}
IS_MOVING = {"duong_tinh": False, "am_tinh": False, "duong_dong": True, "am_dong": True}

# 3-coin toss rule (Sấp/Ngửa), cross-checked against multiple Vietnamese
# sources describing the classical "tam đồng tiền" method - note this
# assigns Sấp (not Ngửa) to the yang/dương count, the opposite of what
# might be guessed from "Ngửa = mặt trên = dương":
#   3 Sấp          -> Lão Dương (dương động)
#   2 Sấp, 1 Ngửa  -> Thiếu Dương (dương tĩnh)
#   1 Sấp, 2 Ngửa  -> Thiếu Âm (âm tĩnh)
#   3 Ngửa         -> Lão Âm (âm động)
_COIN_RULE_BY_SAP_COUNT = {
    3: "duong_dong",
    2: "duong_tinh",
    1: "am_tinh",
    0: "am_dong",
}


def state_from_coins(coin_faces: list) -> str:
    """coin_faces: list of 3 strings, each "sap" or "ngua"."""
    if len(coin_faces) != 3 or any(f not in ("sap", "ngua") for f in coin_faces):
        raise ValueError(f"Cần đúng 3 mặt xu (sap/ngua): {coin_faces}")
    sap_count = coin_faces.count("sap")
    return _COIN_RULE_BY_SAP_COUNT[sap_count]


def resolve_from_coins(coin_tosses: list) -> dict:
    """coin_tosses: list of 6 lists (bottom to top), each 3 "sap"/"ngua"
    strings - the raw result of 6 real 3-coin tosses."""
    if len(coin_tosses) != 6:
        raise ValueError("Cần đúng 6 lần gieo xu")
    states = [state_from_coins(faces) for faces in coin_tosses]
    result = resolve(states)
    result["coin_tosses"] = coin_tosses
    return result


def resolve(states: list) -> dict:
    if len(states) != 6:
        raise ValueError("Cần đúng 6 hào")
    for s in states:
        if s not in VALID_STATES:
            raise ValueError(f"Trạng thái hào không hợp lệ: {s}")

    main_lines = [1 if IS_YANG[s] else 0 for s in states]
    moving_positions = [i + 1 for i, s in enumerate(states) if IS_MOVING[s]]  # 1-indexed

    changed_lines = list(main_lines)
    for pos in moving_positions:
        changed_lines[pos - 1] = 1 - changed_lines[pos - 1]

    hexagram_main = data_repo.hexagram_by_lines(main_lines)
    hexagram_changed = data_repo.hexagram_by_lines(changed_lines) if moving_positions else None

    return {
        "states": states,
        "main_lines": main_lines,
        "changed_lines": changed_lines if moving_positions else None,
        "moving_positions": moving_positions,
        "hexagram_main": hexagram_main,
        "hexagram_changed": hexagram_changed,
    }
