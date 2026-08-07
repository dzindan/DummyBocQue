"""Mai Hoa Dịch Số (Plum Blossom Numerology) time-based hexagram casting.

Given a solar date+hour, converts to the Vietnamese lunar calendar, then
applies the classical numerological formula (based on Chi-index of the
year, lunar month number, lunar day number, and Chi-index of the hour)
to derive the upper trigram, lower trigram, and moving line.

The datetime fed in here is always just "whatever value is in the form" -
the caller decides whether that came from system clock or a manual pick;
this module treats both identically.
"""

from . import data_repo
from .canchi import (
    DIA_CHI,
    THIEN_CAN,
    day_can_chi,
    format_can_chi,
    hour_can_chi,
    hour_chi_index,
    month_can_chi,
    year_can_chi,
)
from .lunar import solar_to_lunar


def _mod_1_to_n(value, n):
    """1-indexed modulo: remainder 0 maps to n instead of 0."""
    r = value % n
    return n if r == 0 else r


def calculate(dd: int, mm: int, yy: int, hour: int) -> dict:
    lunar_day, lunar_month, lunar_year, lunar_leap = solar_to_lunar(dd, mm, yy)

    year_can_idx, year_chi_idx = year_can_chi(lunar_year)
    month_can_idx, month_chi_idx = month_can_chi(lunar_month, year_can_idx)
    day_can_idx, day_chi_idx = day_can_chi(dd, mm, yy)
    hour_can_idx, hour_chi_idx_val = hour_can_chi(hour, day_can_idx)

    # Classical formula: Chi-index of year (Tý=1..Hợi=12) + lunar month
    # number + lunar day number [+ Chi-index of hour] mod 8 / mod 6.
    nam_so = year_chi_idx + 1
    thang_so = lunar_month
    ngay_so = lunar_day
    gio_so = hour_chi_idx_val + 1

    upper_so = _mod_1_to_n(nam_so + thang_so + ngay_so, 8)
    lower_so = _mod_1_to_n(nam_so + thang_so + ngay_so + gio_so, 8)
    dong_hao = _mod_1_to_n(nam_so + thang_so + ngay_so + gio_so, 6)

    upper_trigram = data_repo.trigram_by_nguyen_so(upper_so)
    lower_trigram = data_repo.trigram_by_nguyen_so(lower_so)

    main_lines = lower_trigram["lines"] + upper_trigram["lines"]
    changed_lines = list(main_lines)
    changed_lines[dong_hao - 1] = 1 - changed_lines[dong_hao - 1]

    hexagram_main = data_repo.hexagram_by_trigrams(upper_trigram["code"], lower_trigram["code"])
    hexagram_changed = data_repo.hexagram_by_lines(changed_lines)

    return {
        "input": {"dd": dd, "mm": mm, "yy": yy, "hour": hour},
        "lunar": {
            "day": lunar_day,
            "month": lunar_month,
            "year": lunar_year,
            "is_leap_month": bool(lunar_leap),
        },
        "can_chi": {
            "year": format_can_chi(year_can_idx, year_chi_idx),
            "month": format_can_chi(month_can_idx, month_chi_idx),
            "day": format_can_chi(day_can_idx, day_chi_idx),
            "hour": format_can_chi(hour_can_idx, hour_chi_idx_val),
        },
        "so_hoc": {
            "nam_so": nam_so, "thang_so": thang_so, "ngay_so": ngay_so, "gio_so": gio_so,
            "upper_so": upper_so, "lower_so": lower_so,
        },
        "upper_trigram": upper_trigram,
        "lower_trigram": lower_trigram,
        "dong_hao": dong_hao,
        "hexagram_main": hexagram_main,
        "hexagram_changed": hexagram_changed,
        "main_lines": main_lines,
        "changed_lines": changed_lines,
    }
