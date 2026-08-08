"""One-off generator for app/data/trigrams.json and app/data/hexagrams.json.

Run manually (`python scripts/generate_data.py`) whenever the base
trigram/hexagram list changes. Not run at app startup - the app reads the
committed JSON output, this script is just how that JSON was produced.

Line encoding: each hexagram/trigram stores `lines`, a list of 3 or 6
ints, bottom-to-top, 1 = dương (unbroken), 0 = âm (broken). Rendering
(bars/unicode) is a template concern, not stored here.
"""

import json
import os

TRIGRAMS = [
    # code, name, lines (bottom->top), nguyen_so (Tien Thien so for Mai Hoa), nguhanh, direction, weather
    ("cAN", "Càn", [1, 1, 1], 1, "Kim", "Tây Bắc", "Trời quang, nắng ráo"),
    ("doai", "Đoài", [1, 1, 0], 2, "Kim", "Tây", "Mưa nhỏ, ẩm ướt"),
    ("ly", "Ly", [1, 0, 1], 3, "Hỏa", "Nam", "Nắng nóng, oi bức"),
    ("chan", "Chấn", [1, 0, 0], 4, "Mộc", "Đông", "Sấm động, giông gió"),
    ("ton", "Tốn", [0, 1, 1], 5, "Mộc", "Đông Nam", "Có gió, gió mạnh"),
    ("kham", "Khảm", [0, 1, 0], 6, "Thủy", "Bắc", "Mưa, sương mù, ẩm ướt"),
    ("can2", "Cấn", [0, 0, 1], 7, "Thổ", "Đông Bắc", "Mây che, có lúc tạnh ráo"),
    ("khon", "Khôn", [0, 0, 0], 8, "Thổ", "Tây Nam", "Âm u, nhiều mây"),
]

# King Wen order: (number, Han-Viet name, upper trigram code, lower trigram code)
HEXAGRAMS = [
    (1, "Thuần Càn", "cAN", "cAN"),
    (2, "Thuần Khôn", "khon", "khon"),
    (3, "Thủy Lôi Truân", "kham", "chan"),
    (4, "Sơn Thủy Mông", "can2", "kham"),
    (5, "Thủy Thiên Nhu", "kham", "cAN"),
    (6, "Thiên Thủy Tụng", "cAN", "kham"),
    (7, "Địa Thủy Sư", "khon", "kham"),
    (8, "Thủy Địa Tỷ", "kham", "khon"),
    (9, "Phong Thiên Tiểu Súc", "ton", "cAN"),
    (10, "Thiên Trạch Lý", "cAN", "doai"),
    (11, "Địa Thiên Thái", "khon", "cAN"),
    (12, "Thiên Địa Bĩ", "cAN", "khon"),
    (13, "Thiên Hỏa Đồng Nhân", "cAN", "ly"),
    (14, "Hỏa Thiên Đại Hữu", "ly", "cAN"),
    (15, "Địa Sơn Khiêm", "khon", "can2"),
    (16, "Lôi Địa Dự", "chan", "khon"),
    (17, "Trạch Lôi Tùy", "doai", "chan"),
    (18, "Sơn Phong Cổ", "can2", "ton"),
    (19, "Địa Trạch Lâm", "khon", "doai"),
    (20, "Phong Địa Quán", "ton", "khon"),
    (21, "Hỏa Lôi Phệ Hạp", "ly", "chan"),
    (22, "Sơn Hỏa Bí", "can2", "ly"),
    (23, "Sơn Địa Bác", "can2", "khon"),
    (24, "Địa Lôi Phục", "khon", "chan"),
    (25, "Thiên Lôi Vô Vọng", "cAN", "chan"),
    (26, "Sơn Thiên Đại Súc", "can2", "cAN"),
    (27, "Sơn Lôi Di", "can2", "chan"),
    (28, "Trạch Phong Đại Quá", "doai", "ton"),
    (29, "Thuần Khảm", "kham", "kham"),
    (30, "Thuần Ly", "ly", "ly"),
    (31, "Trạch Sơn Hàm", "doai", "can2"),
    (32, "Lôi Phong Hằng", "chan", "ton"),
    (33, "Thiên Sơn Độn", "cAN", "can2"),
    (34, "Lôi Thiên Đại Tráng", "chan", "cAN"),
    (35, "Hỏa Địa Tấn", "ly", "khon"),
    (36, "Địa Hỏa Minh Di", "khon", "ly"),
    (37, "Phong Hỏa Gia Nhân", "ton", "ly"),
    (38, "Hỏa Trạch Khuê", "ly", "doai"),
    (39, "Thủy Sơn Kiển", "kham", "can2"),
    (40, "Lôi Thủy Giải", "chan", "kham"),
    (41, "Sơn Trạch Tổn", "can2", "doai"),
    (42, "Phong Lôi Ích", "ton", "chan"),
    (43, "Trạch Thiên Quải", "doai", "cAN"),
    (44, "Thiên Phong Cấu", "cAN", "ton"),
    (45, "Trạch Địa Tụy", "doai", "khon"),
    (46, "Địa Phong Thăng", "khon", "ton"),
    (47, "Trạch Thủy Khốn", "doai", "kham"),
    (48, "Thủy Phong Tỉnh", "kham", "ton"),
    (49, "Trạch Hỏa Cách", "doai", "ly"),
    (50, "Hỏa Phong Đỉnh", "ly", "ton"),
    (51, "Thuần Chấn", "chan", "chan"),
    (52, "Thuần Cấn", "can2", "can2"),
    (53, "Phong Sơn Tiệm", "ton", "can2"),
    (54, "Lôi Trạch Quy Muội", "chan", "doai"),
    (55, "Lôi Hỏa Phong", "chan", "ly"),
    (56, "Hỏa Sơn Lữ", "ly", "can2"),
    (57, "Thuần Tốn", "ton", "ton"),
    (58, "Thuần Đoài", "doai", "doai"),
    (59, "Phong Thủy Hoán", "ton", "kham"),
    (60, "Thủy Trạch Tiết", "kham", "doai"),
    (61, "Phong Trạch Trung Phu", "ton", "doai"),
    (62, "Lôi Sơn Tiểu Quá", "chan", "can2"),
    (63, "Thủy Hỏa Ký Tế", "kham", "ly"),
    (64, "Hỏa Thủy Vị Tế", "ly", "kham"),
]

# Thoán từ / Đại Tượng / Hào từ for all 64 hexagrams, compiled from the
# public-domain James Legge 1899 translation (Sacred Books of the East
# vol. 16) for meaning, with the Vietnamese wording independently
# composed (not copied from any copyrighted Vietnamese or English
# translation) - see app/data/content.json. Keyed by hexagram number as a
# string in the JSON file; converted to int here.
def _load_content():
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "data")
    content_path = os.path.join(data_dir, "content.json")
    if not os.path.exists(content_path):
        return {}
    with open(content_path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return {int(k): v for k, v in raw.items()}


SAMPLE_CONTENT = _load_content()


def build_trigrams():
    return [
        {
            "code": code,
            "name": name,
            "lines": lines,
            "nguyen_so": so,
            "ngu_hanh": nh,
            "direction": direction,
            "weather_meaning": weather,
        }
        for code, name, lines, so, nh, direction, weather in TRIGRAMS
    ]


def build_hexagrams(trigrams_by_code):
    out = []
    for number, name, upper_code, lower_code in HEXAGRAMS:
        upper = trigrams_by_code[upper_code]
        lower = trigrams_by_code[lower_code]
        lines = lower["lines"] + upper["lines"]  # bottom->top: lower trigram first
        content = SAMPLE_CONTENT.get(number, {})
        out.append({
            "number": number,
            "name": name,
            "upper_trigram": upper_code,
            "lower_trigram": lower_code,
            "lines": lines,
            "thoan_tu": content.get("thoan_tu", ""),
            "dai_tuong": content.get("dai_tuong", ""),
            "hao_tu": content.get("hao_tu", []),
            # Thoán Truyện / Tiểu Tượng: unlike thoan_tu/dai_tuong/hao_tu
            # above (grounded in the public-domain Legge translation),
            # these are AI-composed analysis from classical trigram
            # theory - the source commentary pages weren't reachable, so
            # this is not verified classical wording. Flagged separately
            # in the UI (see hexagram_detail.html) rather than presented
            # as translated kinh văn.
            "thoan_truyen": content.get("thoan_truyen", ""),
            "tieu_tuong": content.get("tieu_tuong", []),
            "content_status": "aggregated" if content else "pending",
        })
    return out


def main():
    trigrams = build_trigrams()
    trigrams_by_code = {t["code"]: t for t in trigrams}
    hexagrams = build_hexagrams(trigrams_by_code)

    assert len(hexagrams) == 64
    assert len({h["number"] for h in hexagrams}) == 64

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "app", "data")
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "trigrams.json"), "w", encoding="utf-8") as f:
        json.dump(trigrams, f, ensure_ascii=False, indent=2)

    with open(os.path.join(data_dir, "hexagrams.json"), "w", encoding="utf-8") as f:
        json.dump(hexagrams, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(trigrams)} trigrams and {len(hexagrams)} hexagrams to {data_dir}")


if __name__ == "__main__":
    main()
