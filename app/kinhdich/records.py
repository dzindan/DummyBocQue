"""User-generated data: divination history, personal notes, and custom
question templates. Persisted via the storage backend (local JSON file
per key) - see app/storage. Bundled reference data (trigrams, hexagrams,
built-in question templates) lives in data_repo instead.
"""

import uuid
from datetime import datetime, timezone

from ..storage import get_backend

DIVINATIONS_KEY = "divinations"
NOTES_KEY = "notes"
CUSTOM_QUESTIONS_KEY = "custom_question_templates"


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _new_id():
    return uuid.uuid4().hex


# ---- Divination history ----------------------------------------------

def list_divinations():
    records = get_backend().get_json(DIVINATIONS_KEY, default=[])
    return sorted(records, key=lambda r: r["created_at"], reverse=True)


def get_divination(record_id):
    for r in list_divinations():
        if r["id"] == record_id:
            return r
    return None


def save_divination(record: dict) -> dict:
    record = dict(record)
    record["id"] = _new_id()
    record["created_at"] = _now_iso()
    records = get_backend().get_json(DIVINATIONS_KEY, default=[])
    records.append(record)
    get_backend().set_json(DIVINATIONS_KEY, records)
    return record


def update_divination_note(record_id, note_text):
    records = get_backend().get_json(DIVINATIONS_KEY, default=[])
    for r in records:
        if r["id"] == record_id:
            r["note"] = note_text
    get_backend().set_json(DIVINATIONS_KEY, records)


def delete_divination(record_id):
    records = get_backend().get_json(DIVINATIONS_KEY, default=[])
    records = [r for r in records if r["id"] != record_id]
    get_backend().set_json(DIVINATIONS_KEY, records)


# ---- Personal notes -----------------------------------------------------

def list_notes(hexagram_number=None):
    notes = get_backend().get_json(NOTES_KEY, default=[])
    if hexagram_number is not None:
        notes = [n for n in notes if n["hexagram_number"] == hexagram_number]
    return sorted(notes, key=lambda n: n["created_at"], reverse=True)


def save_note(hexagram_number, content, tags=None):
    notes = get_backend().get_json(NOTES_KEY, default=[])
    note = {
        "id": _new_id(),
        "created_at": _now_iso(),
        "hexagram_number": hexagram_number,
        "content": content,
        "tags": tags or [],
    }
    notes.append(note)
    get_backend().set_json(NOTES_KEY, notes)
    return note


def delete_note(note_id):
    notes = get_backend().get_json(NOTES_KEY, default=[])
    notes = [n for n in notes if n["id"] != note_id]
    get_backend().set_json(NOTES_KEY, notes)


# ---- Custom question templates ------------------------------------------

def list_custom_question_templates():
    return get_backend().get_json(CUSTOM_QUESTIONS_KEY, default=[])


def save_custom_question_template(category, text):
    templates = list_custom_question_templates()
    entry = {"category": category, "text": text}
    if entry not in templates:
        templates.append(entry)
        get_backend().set_json(CUSTOM_QUESTIONS_KEY, templates)
    return entry
