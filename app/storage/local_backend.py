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
        # files into directly. Reject "..", empty, and drive-letter/
        # absolute segments so a key can never resolve outside
        # app_data_dir - nothing in this app passes a user-controlled key
        # here today, but this class is shared by the whole kinhdich-family
        # of apps, and a future caller that does pass one through shouldn't
        # get path traversal for free.
        parts = key.strip("/").split("/")
        for part in parts:
            if part in ("", ".", "..") or os.path.isabs(part) or ":" in part:
                raise ValueError(f"Unsafe blob key: {key!r}")
        return os.path.join(self.app_data_dir, *parts)

    def list_blobs(self, prefix: str) -> list:
        # base.py documents this as "keys whose key starts with prefix" -
        # matches SupabaseBackend's `like.{prefix}*`, including a prefix
        # that's only a partial filename (e.g. "knowledge/Ghi" matching
        # "knowledge/Ghi_chu.txt"), not just a prefix that happens to be a
        # full directory name.
        # Only strip a leading slash - a *trailing* one is meaningful (it
        # means "everything in this directory", i.e. an empty filename
        # prefix) and must survive rpartition below.
        prefix_norm = prefix.lstrip("/")
        if "/" in prefix_norm:
            dir_key, _, filename_prefix = prefix_norm.rpartition("/")
            dir_path = self._full_path(dir_key) if dir_key else self.app_data_dir
            key_prefix = f"{dir_key}/" if dir_key else ""
        else:
            dir_path = self.app_data_dir
            filename_prefix = prefix_norm
            key_prefix = ""

        if not os.path.isdir(dir_path):
            return []
        entries = []
        for fname in sorted(os.listdir(dir_path)):
            if not fname.startswith(filename_prefix):
                continue
            full = os.path.join(dir_path, fname)
            if not os.path.isfile(full):
                continue
            stat = os.stat(full)
            entries.append({
                "key": f"{key_prefix}{fname}",
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
