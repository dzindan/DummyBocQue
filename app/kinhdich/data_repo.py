"""Loads the bundled reference JSON (trigrams, hexagrams, question
templates) once per process and exposes small lookup helpers. Read-only,
bundled data - not to be confused with user data (divination history,
notes), which lives in the storage backend instead.
"""

import json
import os
from functools import lru_cache

from ..paths import get_data_dir


def _load(filename):
    path = os.path.join(get_data_dir(), filename)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def trigrams():
    return _load("trigrams.json")


@lru_cache(maxsize=1)
def hexagrams():
    return _load("hexagrams.json")


@lru_cache(maxsize=1)
def question_templates():
    return _load("question_templates.json")


@lru_cache(maxsize=1)
def _trigrams_by_code():
    return {t["code"]: t for t in trigrams()}


@lru_cache(maxsize=1)
def _trigrams_by_nguyen_so():
    return {t["nguyen_so"]: t for t in trigrams()}


@lru_cache(maxsize=1)
def _trigrams_by_lines():
    return {tuple(t["lines"]): t for t in trigrams()}


@lru_cache(maxsize=1)
def _hexagrams_by_trigram_pair():
    return {(h["upper_trigram"], h["lower_trigram"]): h for h in hexagrams()}


@lru_cache(maxsize=1)
def _hexagrams_by_number():
    return {h["number"]: h for h in hexagrams()}


def trigram_by_code(code):
    return _trigrams_by_code()[code]


def trigram_by_nguyen_so(so):
    return _trigrams_by_nguyen_so()[so]


def trigram_by_lines(lines):
    return _trigrams_by_lines()[tuple(lines)]


def hexagram_by_trigrams(upper_code, lower_code):
    return _hexagrams_by_trigram_pair()[(upper_code, lower_code)]


def hexagram_by_number(number):
    return _hexagrams_by_number()[number]


def hexagram_by_lines(lines):
    lines = tuple(lines)
    lower_code = trigram_by_lines(lines[:3])["code"]
    upper_code = trigram_by_lines(lines[3:])["code"]
    return hexagram_by_trigrams(upper_code, lower_code)
