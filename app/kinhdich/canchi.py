"""Can-Chi (Heavenly Stems / Earthly Branches) helpers."""

from .lunar import jd_from_date

THIEN_CAN = [
    "Giáp", "Ất", "Bính", "Đinh", "Mậu",
    "Kỷ", "Canh", "Tân", "Nhâm", "Quý",
]

DIA_CHI = [
    "Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
    "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi",
]

# ASCII-safe keys, same order as DIA_CHI - used for CSS grid-area names.
DIA_CHI_ASCII = [
    "ty", "suu", "dan", "mao", "thin", "ti",
    "ngo", "mui", "than", "dau", "tuat", "hoi",
]

# Fixed Chi for each lunar month, regardless of year (tháng Giêng luôn là Dần).
MONTH_CHI_INDEX = {
    1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7,
    7: 8, 8: 9, 9: 10, 10: 11, 11: 0, 12: 1,
}

# Ngu Ho Don: Can cua thang Gieng (Dan) theo Can cua nam.
# index = Can nam (0=Giap...9=Quy) -> Can cua thang Dan (index vao THIEN_CAN)
NGU_HO_DON = {
    0: 2, 5: 2,   # Giap, Ky -> Binh Dan
    1: 4, 6: 4,   # At, Canh -> Mau Dan
    2: 6, 7: 6,   # Binh, Tan -> Canh Dan
    3: 8, 8: 8,   # Dinh, Nham -> Nham Dan
    4: 0, 9: 0,   # Mau, Quy -> Giap Dan
}

# Ngu Thu Don: Can cua gio Ty theo Can cua ngay.
NGU_THU_DON = {
    0: 0, 5: 0,   # Giap, Ky -> Giap Ty
    1: 2, 6: 2,   # At, Canh -> Binh Ty
    2: 4, 7: 4,   # Binh, Tan -> Mau Ty
    3: 6, 8: 6,   # Dinh, Nham -> Canh Ty
    4: 8, 9: 8,   # Mau, Quy -> Nham Ty
}

# 12 double-hour blocks (gio Chi), start hour inclusive, in 24h clock.
# Gio Ty spans 23:00-00:59.
HOUR_TO_CHI = [
    (23, 0), (1, 2), (3, 4), (5, 6), (7, 8), (9, 10),
    (11, 12), (13, 14), (15, 16), (17, 18), (19, 20), (21, 22),
]


def year_can_chi(year: int):
    can = (year + 6) % 10
    chi = (year + 8) % 12
    return can, chi


def month_can_chi(lunar_month: int, year_can_idx: int):
    dan_can = NGU_HO_DON[year_can_idx]
    steps = lunar_month - 1  # thang Gieng = 0 buoc tu Dan
    can = (dan_can + steps) % 10
    chi = MONTH_CHI_INDEX[lunar_month]
    return can, chi


def day_can_chi(dd: int, mm: int, yy: int):
    jd = jd_from_date(dd, mm, yy)
    can = (jd + 9) % 10
    chi = (jd + 1) % 12
    return can, chi


def hour_chi_index(hour: int) -> int:
    """Map a 24h-clock hour (0-23) to its Chi index (0=Ty ... 11=Hoi)."""
    if hour == 23:
        return 0
    return (hour + 1) // 2


def hour_can_chi(hour: int, day_can_idx: int):
    chi = hour_chi_index(hour)
    ty_can = NGU_THU_DON[day_can_idx]
    can = (ty_can + chi) % 10
    return can, chi


def format_can_chi(can_idx: int, chi_idx: int) -> str:
    return f"{THIEN_CAN[can_idx]} {DIA_CHI[chi_idx]}"
