"""Abstract storage interface so settings.py / knowledge_base.py don't
care whether they're running against local files (desktop app / local
dev) or Supabase (online deployment with no persistent local disk).

Deliberately just two generic capabilities - a JSON value keyed by name,
and a byte blob keyed by a path-like string - rather than one bespoke
method per feature. Every piece of state the app persists today (app
settings, user-added knowledge notes) fits one of these two shapes, and
so will most anything added later (e.g. a future "saved charts" list is
just another JSON key) - meaning a new feature needs zero new backend
methods and zero new Supabase tables/migrations, in either backend.
"""

from abc import ABC, abstractmethod


class StorageBackend(ABC):
    @abstractmethod
    def get_json(self, key: str, default=None):
        """Load the JSON-serializable value stored under `key`, or
        `default` if nothing is stored there yet."""

    @abstractmethod
    def set_json(self, key: str, value) -> None:
        """Persist a JSON-serializable value under `key`."""

    @abstractmethod
    def list_blobs(self, prefix: str) -> list:
        """List blobs whose key starts with `prefix`. Returns a list of
        dicts: {"key": str, "size": int, "updated_at": float-or-str}."""

    @abstractmethod
    def read_blob(self, key: str) -> bytes:
        """Raises FileNotFoundError if `key` doesn't exist."""

    @abstractmethod
    def write_blob(self, key: str, content: bytes) -> None:
        """Create or overwrite the blob at `key`."""

    @abstractmethod
    def delete_blob(self, key: str) -> None:
        """No-op if `key` doesn't exist."""
