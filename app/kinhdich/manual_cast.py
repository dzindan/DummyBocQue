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
