"""Solar <-> Vietnamese lunar calendar conversion.

Implementation of the standard astronomical algorithm for the Vietnamese
lunar calendar (new moon / sun longitude computations per Jean Meeus'
"Astronomical Algorithms"), the same method used by Ho Ngoc Duc's widely
used public-domain "amlich" calculator that most Vietnamese calendar tools
are built on. Vietnam has used UTC+7 for calendar purposes since 1967; this
module assumes +7 throughout (dates before 1967 may be off by one day
against historical records, which alternated between +7 and +8).
"""

import math


def jd_from_date(dd: int, mm: int, yy: int) -> int:
    a = (14 - mm) // 12
    y = yy + 4800 - a
    m = mm + 12 * a - 3
    jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    if jd < 2299161:
        jd = dd + (153 * m + 2) // 5 + 365 * y + y // 4 - 32083
    return jd


def jd_to_date(jd: int):
    if jd > 2299160:
        a = jd + 32044
        b = (4 * a + 3) // 146097
        c = a - (146097 * b) // 4
    else:
        b = 0
        c = jd + 32082
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return day, month, year


def _new_moon(k: float) -> float:
    T = k / 1236.85
    T2 = T * T
    T3 = T2 * T
    dr = math.pi / 180
    Jd1 = 2415020.75933 + 29.53058868 * k + 0.0001178 * T2 - 0.000000155 * T3
    Jd1 += 0.00033 * math.sin((166.56 + 132.87 * T - 0.009173 * T2) * dr)
    M = 359.2242 + 29.10535608 * k - 0.0000333 * T2 - 0.00000347 * T3
    Mpr = 306.0253 + 385.81691806 * k + 0.0107306 * T2 + 0.00001236 * T3
    F = 21.2964 + 390.67050646 * k - 0.0016528 * T2 - 0.00000239 * T3
    C1 = (0.1734 - 0.000393 * T) * math.sin(M * dr) + 0.0021 * math.sin(2 * dr * M)
    C1 -= 0.4068 * math.sin(Mpr * dr) - 0.0161 * math.sin(dr * 2 * Mpr)
    C1 -= 0.0004 * math.sin(dr * 3 * Mpr)
    C1 += 0.0104 * math.sin(dr * 2 * F) - 0.0051 * math.sin(dr * (M + Mpr))
    C1 -= 0.0074 * math.sin(dr * (M - Mpr)) - 0.0004 * math.sin(dr * (2 * F + M))
    C1 -= 0.0004 * math.sin(dr * (2 * F - M)) - 0.0006 * math.sin(dr * (2 * F + Mpr))
    C1 += 0.0010 * math.sin(dr * (2 * F - Mpr)) + 0.0005 * math.sin(dr * (2 * Mpr + M))
    if T < -11:
        deltat = (
            0.001
            + 0.000839 * T
            + 0.0002261 * T2
            - 0.00000845 * T3
            - 0.000000081 * T * T3
        )
    else:
        deltat = -0.000278 + 0.000265 * T + 0.000262 * T2
    return Jd1 + C1 - deltat


def _sun_longitude(jdn: float) -> float:
    T = (jdn - 2451545.0) / 36525
    T2 = T * T
    dr = math.pi / 180
    M = 357.52910 + 35999.05030 * T - 0.0001559 * T2 - 0.00000048 * T * T2
    L0 = 280.46645 + 36000.76983 * T + 0.0003032 * T2
    DL = (1.914600 - 0.004817 * T - 0.000014 * T2) * math.sin(dr * M)
    DL += (0.019993 - 0.000101 * T) * math.sin(dr * 2 * M) + 0.000290 * math.sin(dr * 3 * M)
    L = L0 + DL
    L = L * dr
    L -= math.pi * 2 * math.floor(L / (math.pi * 2))
    return L


def _get_sun_longitude(day_number: float, time_zone: float) -> int:
    return math.floor(_sun_longitude(day_number - 0.5 - time_zone / 24.0) / math.pi * 6)


def _get_new_moon_day(k: float, time_zone: float) -> int:
    return math.floor(_new_moon(k) + 0.5 + time_zone / 24.0)


def _get_lunar_month_11(yy: int, time_zone: float) -> int:
    off = jd_from_date(31, 12, yy) - 2415021.076998695
    k = math.floor(off / 29.530588853)
    nm = _get_new_moon_day(k, time_zone)
    sun_long = _get_sun_longitude(nm, time_zone)
    if sun_long >= 9:
        nm = _get_new_moon_day(k - 1, time_zone)
    return nm


def _get_leap_month_offset(a11: int, time_zone: float) -> int:
    k = math.floor((a11 - 2415021.076998695) / 29.530588853 + 0.5)
    i = 1
    arc = _get_sun_longitude(_get_new_moon_day(k + i, time_zone), time_zone)
    last = arc
    while True:
        last = arc
        i += 1
        arc = _get_sun_longitude(_get_new_moon_day(k + i, time_zone), time_zone)
        if arc == last or i >= 14:
            break
    return i - 1


def solar_to_lunar(dd: int, mm: int, yy: int, time_zone: float = 7.0):
    """Returns (lunar_day, lunar_month, lunar_year, is_leap_month)."""
    day_number = jd_from_date(dd, mm, yy)
    k = math.floor((day_number - 2415021.076998695) / 29.530588853)
    month_start = _get_new_moon_day(k + 1, time_zone)
    if month_start > day_number:
        month_start = _get_new_moon_day(k, time_zone)
    a11 = _get_lunar_month_11(yy, time_zone)
    b11 = a11
    if a11 >= month_start:
        lunar_year = yy
        a11 = _get_lunar_month_11(yy - 1, time_zone)
    else:
        lunar_year = yy + 1
        b11 = _get_lunar_month_11(yy + 1, time_zone)
    lunar_day = day_number - month_start + 1
    diff = math.floor((month_start - a11) / 29)
    lunar_leap = 0
    lunar_month = diff + 11
    if b11 - a11 > 365:
        leap_month_diff = _get_leap_month_offset(a11, time_zone)
        if diff >= leap_month_diff:
            lunar_month = diff + 10
            if diff == leap_month_diff:
                lunar_leap = 1
    if lunar_month > 12:
        lunar_month -= 12
    if lunar_month >= 11 and diff < 4:
        lunar_year -= 1
    return int(lunar_day), int(lunar_month), int(lunar_year), int(lunar_leap)


def lunar_to_solar(lunar_day: int, lunar_month: int, lunar_year: int, lunar_leap: int = 0, time_zone: float = 7.0):
    """Returns (dd, mm, yy)."""
    if lunar_month < 11:
        a11 = _get_lunar_month_11(lunar_year - 1, time_zone)
        b11 = _get_lunar_month_11(lunar_year, time_zone)
    else:
        a11 = _get_lunar_month_11(lunar_year, time_zone)
        b11 = _get_lunar_month_11(lunar_year + 1, time_zone)
    k = math.floor(0.5 + (a11 - 2415021.076998695) / 29.530588853)
    off = lunar_month - 11
    if off < 0:
        off += 12
    if b11 - a11 > 365:
        leap_off = _get_leap_month_offset(a11, time_zone)
        leap_month = leap_off - 2
        if leap_month < 0:
            leap_month += 12
        if lunar_leap and lunar_month != leap_month:
            return None
        if lunar_leap or off >= leap_off:
            off += 1
    month_start = _get_new_moon_day(k + off, time_zone)
    jd = month_start + lunar_day - 1
    return jd_to_date(int(jd))
