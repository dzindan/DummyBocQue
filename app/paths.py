import os
import sys


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def get_bundle_dir() -> str:
    """Directory containing bundled read-only assets (templates, static,
    data). When packaged with PyInstaller --onefile, bundled data lives
    under sys._MEIPASS. When running from source, it's the project root
    (parent of this app/ package)."""
    if is_frozen():
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_app_data_dir() -> str:
    """Writable directory for divination history, notes, custom question
    templates. Always outside the exe/bundle so it works even when the exe
    sits in a read-only location like Program Files.

    On Vercel (and other serverless hosts with a read-only filesystem),
    only /tmp is writable, and it's ephemeral - wiped between cold starts,
    not shared across instances. That means history/notes saved on a
    Vercel deployment won't persist reliably; this just keeps the app
    from crashing there. A real deployment needing durable storage should
    swap in a proper StorageBackend (e.g. a hosted DB) instead.
    """
    if os.environ.get("VERCEL"):
        data_dir = "/tmp/kinhdichapp"
    else:
        base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
        data_dir = os.path.join(base, "KinhDichApp")
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_data_dir() -> str:
    """Bundled read-only reference data shipped with the app (64 quẻ, 8
    quẻ đơn, câu hỏi mẫu)."""
    return os.path.join(get_bundle_dir(), "app", "data")
