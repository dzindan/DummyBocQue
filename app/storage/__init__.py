"""Picks the right StorageBackend based on environment: Supabase when
SUPABASE_URL/SUPABASE_KEY are set (e.g. on Vercel, where the filesystem
is read-only/ephemeral), local files otherwise (desktop app / local dev).
Same generic kv_store/blobs tables and same Supabase project as Tu Vi
App - see records.py for the "kinhdich_" key prefix used to avoid
colliding with Tu Vi App's own keys in that shared project.
"""

import os
import warnings

from ..paths import get_app_data_dir, is_vercel
from .base import StorageBackend
from .local_backend import LocalFileBackend
from .supabase_backend import SupabaseBackend

_backend: StorageBackend = None


def using_supabase() -> bool:
    return bool(os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_KEY"))


def get_backend() -> StorageBackend:
    global _backend
    if _backend is not None:
        return _backend
    if using_supabase():
        _backend = SupabaseBackend(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
    else:
        if is_vercel():
            # /tmp on Vercel is ephemeral and not shared across instances -
            # falling back to LocalFileBackend here means every cold start
            # silently starts from empty history, with nothing telling the
            # operator they forgot to configure Supabase. Loud in the logs
            # beats a deployment that quietly "works" while losing every save.
            warnings.warn(
                "Running on Vercel without SUPABASE_URL/SUPABASE_KEY set - "
                "divination history/notes will NOT persist across cold "
                "starts. Set both env vars to use the Supabase backend.",
                RuntimeWarning,
                stacklevel=2,
            )
        _backend = LocalFileBackend(get_app_data_dir())
    return _backend
