"""Supabase-backed StorageBackend, for when the app runs online (e.g. on
Vercel) with no persistent local disk between requests. Talks to
Supabase's auto-generated REST API (PostgREST) directly via `requests` -
no extra SDK dependency - against exactly 2 generic tables, defined in
deploy/supabase_schema.sql:

    kv_store(key text primary key, value jsonb, updated_at timestamptz)
    blobs(key text primary key, content text, updated_at timestamptz)

Any future feature that needs to persist a JSON dict or a text blob
reuses these same 2 tables under a new key - no schema migration needed.
"""

import base64

import requests

from .base import StorageBackend

TIMEOUT = 10


class SupabaseBackend(StorageBackend):
    def __init__(self, url: str, service_key: str):
        self.rest_base = url.rstrip("/") + "/rest/v1"
        self.headers = {
            "apikey": service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type": "application/json",
        }
        # Reuse one connection (keep-alive) across calls instead of paying a
        # fresh DNS+TCP+TLS handshake on every single request this backend
        # makes - a page that does 2-3 backend calls otherwise pays that
        # setup cost every time instead of once.
        self.session = requests.Session()

    def get_json(self, key: str, default=None):
        try:
            r = self.session.get(
                f"{self.rest_base}/kv_store",
                params={"key": f"eq.{key}", "select": "value"},
                headers=self.headers,
                timeout=TIMEOUT,
            )
            r.raise_for_status()
            rows = r.json()
            return rows[0]["value"] if rows else default
        except (requests.exceptions.RequestException, ValueError, KeyError, IndexError):
            # Mirrors LocalFileBackend.get_json's own try/except: a read
            # that can't be served (here: Supabase unreachable/erroring,
            # there: file missing/corrupt) degrades to `default` instead of
            # taking down every page that reads this key. Writes (below)
            # deliberately do NOT get this treatment - silently swallowing
            # a failed save would look like data loss, not degradation.
            return default

    def set_json(self, key: str, value) -> None:
        r = self.session.post(
            f"{self.rest_base}/kv_store",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json={"key": key, "value": value},
            timeout=TIMEOUT,
        )
        r.raise_for_status()

    def list_blobs(self, prefix: str) -> list:
        r = self.session.get(
            f"{self.rest_base}/blobs",
            params={"key": f"like.{prefix}*", "select": "key,content,updated_at"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return [
            {
                "key": row["key"],
                "size": len(base64.b64decode(row["content"])),
                "updated_at": row["updated_at"],
            }
            for row in r.json()
        ]

    def read_blob(self, key: str) -> bytes:
        r = self.session.get(
            f"{self.rest_base}/blobs",
            params={"key": f"eq.{key}", "select": "content"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            raise FileNotFoundError(key)
        return base64.b64decode(rows[0]["content"])

    def write_blob(self, key: str, content: bytes) -> None:
        # Stored as base64 (not raw text) so this holds up for genuinely
        # binary content, matching the byte-blob contract base.py documents
        # and LocalFileBackend's "wb"/"rb" file I/O already provides - a
        # plain .decode("utf-8") here would raise on any non-UTF-8 bytes.
        r = self.session.post(
            f"{self.rest_base}/blobs",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json={"key": key, "content": base64.b64encode(content).decode("ascii")},
            timeout=TIMEOUT,
        )
        r.raise_for_status()

    def delete_blob(self, key: str) -> None:
        r = self.session.delete(
            f"{self.rest_base}/blobs",
            params={"key": f"eq.{key}"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
