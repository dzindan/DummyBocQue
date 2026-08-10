"""Nạp Âm Lục Thập Hoa Giáp: derives a person's "bản mệnh ngũ hành" (fate
element) from their birth year's Can-Chi.

The 60-term Can-Chi sequence itself is generated algorithmically (Can
cycles every 10, Chi every 12 - see _CAN_CHI_SEQUENCE below), so no risk
of transcription error there. What genuinely has to be looked up is the
Nạp Âm element assigned to each of the 30 pairs (2 consecutive terms
share one Nạp Âm) - that table is loaded from app/data/nap_am.json,
compiled from cross-checked sources rather than hand-typed here, for the
same reason the Lục Hào tables are verified rather than guessed.
"""

import json
import os
from functools import lru_cache

from .canchi import THIEN_CAN, DIA_CHI, year_can_chi
from .lunar import solar_to_lunar
from ..paths import get_data_dir

_CAN_CHI_SEQUENCE = [(n % 10, n % 12) for n in range(60)]
_INDEX_BY_CAN_CHI = {pair: n for n, pair in enumerate(_CAN_CHI_SEQUENCE)}


@lru_cache(maxsize=1)
def _table():
    path = os.path.join(get_data_dir(), "nap_am.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def is_available() -> bool:
    return _table() is not None


def for_year(dd: int, mm: int, yy: int) -> dict:
    """Bản mệnh ngũ hành for a solar birth date, using its lunar year's
    Can-Chi (consistent with how mai_hoa.py treats "năm" elsewhere in the
    app). Returns None if the Nạp Âm table hasn't been compiled yet."""
    table = _table()
    if table is None:
        return None

    _, _, lunar_year, _ = solar_to_lunar(dd, mm, yy)
    can_idx, chi_idx = year_can_chi(lunar_year)
    n = _INDEX_BY_CAN_CHI[(can_idx, chi_idx)]
    pair = table[n // 2]

    return {
        "can_chi": f"{THIEN_CAN[can_idx]} {DIA_CHI[chi_idx]}",
        "nap_am": pair["nap_am"],
        "ngu_hanh": pair["ngu_hanh"],
    }
