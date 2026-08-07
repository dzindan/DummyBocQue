"""Local-filesystem StorageBackend - the exact same on-disk layout the
app has always used (settings.json directly in the app-data dir, and a
plain knowledge/ folder you can drop .txt/.md files into by hand), just
wrapped behind the generic StorageBackend interface. Existing user data
(e.g. notes already sitting in %LOCALAPPDATA%\\TuViApp\\knowledge) keeps
working with zero migration.
"""

import json
import os

from .base import StorageBackend


class LocalFileBackend(StorageBackend):
    def __init__(self, app_data_dir: str):
        self.app_data_dir = app_data_dir

    def _json_path(self, key: str) -> str:
        return os.path.join(self.app_data_dir, f"{key}.json")

    def get_json(self, key: str, default=None):
        path = self._json_path(key)
        if not os.path.exists(path):
            return default
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError):
            return default

    def set_json(self, key: str, value) -> None:
        os.makedirs(self.app_data_dir, exist_ok=True)
        with open(self._json_path(key), "w", encoding="utf-8") as f:
            json.dump(value, f, ensure_ascii=False, indent=2)

    def _full_path(self, key: str) -> str:
        # Blob keys are path-like, e.g. "knowledge/Ghi_chu.txt" - map
        # straight onto a real subdirectory under the app-data dir, so a
        # prefix like "knowledge/" IS the real folder users can drop
        # files into directly.
        return os.path.join(self.app_data_dir, *key.strip("/").split("/"))

    def list_blobs(self, prefix: str) -> list:
        dir_path = self._full_path(prefix)
        if not os.path.isdir(dir_path):
            return []
        entries = []
        prefix_norm = prefix.rstrip("/")
        for fname in sorted(os.listdir(dir_path)):
            full = os.path.join(dir_path, fname)
            if not os.path.isfile(full):
                continue
            stat = os.stat(full)
            entries.append({
                "key": f"{prefix_norm}/{fname}",
                "size": stat.st_size,
                "updated_at": stat.st_mtime,
            })
        return entries

    def read_blob(self, key: str) -> bytes:
        full = self._full_path(key)
        if not os.path.isfile(full):
            raise FileNotFoundError(key)
        with open(full, "rb") as f:
            return f.read()

    def write_blob(self, key: str, content: bytes) -> None:
        full = self._full_path(key)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "wb") as f:
            f.write(content)

    def delete_blob(self, key: str) -> None:
        full = self._full_path(key)
        if os.path.isfile(full):
            os.remove(full)
