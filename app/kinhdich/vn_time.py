"""Vietnam is fixed UTC+7 year-round, no DST (same assumption lunar.py
uses for calendar conversion). Servers can run anywhere - Vercel's
default region is a US datacenter on UTC - so plain `datetime.now()` or
`date.today()` silently returns the wrong wall-clock time for
Vietnamese users depending on where the process happens to run. Use
these instead anywhere the app means "right now, Vietnam time".
"""

from datetime import datetime, timedelta, timezone

VN_TZ = timezone(timedelta(hours=7))


def now() -> datetime:
    return datetime.now(VN_TZ)


def today():
    return now().date()


def to_vn(dt: datetime) -> datetime:
    """Converts an aware UTC datetime (e.g. parsed from a stored UTC ISO
    timestamp) to Vietnam local time for display."""
    return dt.astimezone(VN_TZ)
