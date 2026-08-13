"""User-generated data: divination history, personal notes, and custom
question templates. Persisted via the storage backend - see app/storage
(local JSON file per key for desktop/local dev, or Supabase's shared
kv_store table when SUPABASE_URL/SUPABASE_KEY are set, e.g. on Vercel).
Bundled reference data (trigrams, hexagrams, built-in question templates)
lives in data_repo instead.

Keys are prefixed "kinhdich_" because the Supabase project's kv_store
table is shared with Tu Vi App (same generic schema, same project) - the
prefix keeps the two apps' data from colliding.
"""

import threading
import uuid
from datetime import datetime, timezone

from ..storage import get_backend

DIVINATIONS_KEY = "kinhdich_divinations"
NOTES_KEY = "kinhdich_notes"
CUSTOM_QUESTIONS_KEY = "kinhdich_custom_question_templates"

# One lock per key: every read-modify-write against that key goes through
# _mutate() below, which holds the matching lock for the whole read+write
# round trip. This closes the race between two requests handled by the same
# process (the threaded dev server, or two browser tabs against the desktop
# app's LocalFileBackend) interleaving and silently dropping each other's
# change. It does NOT protect against two separate serverless instances
# racing on the same Supabase row - that needs optimistic-concurrency
# support in the storage backend itself, a bigger change than this file.
_LOCKS = {
    DIVINATIONS_KEY: threading.Lock(),
    NOTES_KEY: threading.Lock(),
    CUSTOM_QUESTIONS_KEY: threading.Lock(),
}


def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _new_id():
    return uuid.uuid4().hex


def _sort_by_created_at(items):
    """Newest-first by created_at. Falls back to "" (sorts last) for any
    item missing the field instead of raising - a partial write, a manually
    edited store, or schema drift could otherwise turn one bad item into a
    KeyError that takes down every page that lists these."""
    return sorted(items, key=lambda item: item.get("created_at", ""), reverse=True)


def _mutate(key, mutate_fn):
    """Read the list stored at `key`, hand it to `mutate_fn` (which mutates
    it in place and/or returns a replacement list), then write back
    whatever list results - all under `key`'s lock so the read and write
    happen as one step from this process's point of view."""
    with _LOCKS[key]:
        items = get_backend().get_json(key, default=[])
        result = mutate_fn(items)
        items = items if result is None else result
        get_backend().set_json(key, items)
        return items


# ---- Divination history ----------------------------------------------

def list_divinations():
    records = get_backend().get_json(DIVINATIONS_KEY, default=[])
    return _sort_by_created_at(records)


def get_divination(record_id):
    """Direct scan for one id - list_divinations() sorts the whole history
    first, which is wasted work when the sort order is irrelevant here."""
    records = get_backend().get_json(DIVINATIONS_KEY, default=[])
    return next((r for r in records if r["id"] == record_id), None)


def save_divination(record: dict) -> dict:
    record = dict(record)
    record["id"] = _new_id()
    record["created_at"] = _now_iso()

    def mutate(records):
        records.append(record)

    _mutate(DIVINATIONS_KEY, mutate)
    return record


def update_divination_note(record_id, note_text) -> bool:
    """Returns True if a record matched and was updated, False if
    `record_id` wasn't found (nothing to update)."""
    found = False

    def mutate(records):
        nonlocal found
        for r in records:
            if r["id"] == record_id:
                r["note"] = note_text
                found = True
                break

    _mutate(DIVINATIONS_KEY, mutate)
    return found


def delete_divination(record_id):
    def mutate(records):
        return [r for r in records if r["id"] != record_id]

    _mutate(DIVINATIONS_KEY, mutate)


# ---- Personal notes -----------------------------------------------------

def list_notes(hexagram_number=None):
    notes = get_backend().get_json(NOTES_KEY, default=[])
    if hexagram_number is not None:
        notes = [n for n in notes if n["hexagram_number"] == hexagram_number]
    return _sort_by_created_at(notes)


def save_note(hexagram_number, content, tags=None):
    note = {
        "id": _new_id(),
        "created_at": _now_iso(),
        "hexagram_number": hexagram_number,
        "content": content,
        "tags": tags or [],
    }

    def mutate(notes):
        notes.append(note)

    _mutate(NOTES_KEY, mutate)
    return note


def delete_note(note_id):
    def mutate(notes):
        return [n for n in notes if n["id"] != note_id]

    _mutate(NOTES_KEY, mutate)


# ---- Custom question templates ------------------------------------------

def list_custom_question_templates():
    return get_backend().get_json(CUSTOM_QUESTIONS_KEY, default=[])


def save_custom_question_template(category, text):
    entry = {"category": category, "text": text}

    def mutate(templates):
        if entry not in templates:
            templates.append(entry)

    _mutate(CUSTOM_QUESTIONS_KEY, mutate)
    return entry
