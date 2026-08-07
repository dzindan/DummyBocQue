from ..paths import get_app_data_dir
from .base import StorageBackend
from .local_backend import LocalFileBackend

_backend: StorageBackend = None


def get_backend() -> StorageBackend:
    global _backend
    if _backend is None:
        _backend = LocalFileBackend(get_app_data_dir())
    return _backend
