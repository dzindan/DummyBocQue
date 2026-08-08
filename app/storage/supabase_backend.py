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

    def get_json(self, key: str, default=None):
        r = requests.get(
            f"{self.rest_base}/kv_store",
            params={"key": f"eq.{key}", "select": "value"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        rows = r.json()
        return rows[0]["value"] if rows else default

    def set_json(self, key: str, value) -> None:
        r = requests.post(
            f"{self.rest_base}/kv_store",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json={"key": key, "value": value},
            timeout=TIMEOUT,
        )
        r.raise_for_status()

    def list_blobs(self, prefix: str) -> list:
        r = requests.get(
            f"{self.rest_base}/blobs",
            params={"key": f"like.{prefix}*", "select": "key,content,updated_at"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        return [
            {
                "key": row["key"],
                "size": len(row["content"].encode("utf-8")),
                "updated_at": row["updated_at"],
            }
            for row in r.json()
        ]

    def read_blob(self, key: str) -> bytes:
        r = requests.get(
            f"{self.rest_base}/blobs",
            params={"key": f"eq.{key}", "select": "content"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
        rows = r.json()
        if not rows:
            raise FileNotFoundError(key)
        return rows[0]["content"].encode("utf-8")

    def write_blob(self, key: str, content: bytes) -> None:
        r = requests.post(
            f"{self.rest_base}/blobs",
            headers={**self.headers, "Prefer": "resolution=merge-duplicates"},
            json={"key": key, "content": content.decode("utf-8")},
            timeout=TIMEOUT,
        )
        r.raise_for_status()

    def delete_blob(self, key: str) -> None:
        r = requests.delete(
            f"{self.rest_base}/blobs",
            params={"key": f"eq.{key}"},
            headers=self.headers,
            timeout=TIMEOUT,
        )
        r.raise_for_status()
