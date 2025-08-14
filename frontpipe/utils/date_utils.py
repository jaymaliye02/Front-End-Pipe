import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from calendar import month_abbr

def target_date(rule: str, now_utc: datetime) -> str:
    ny = now_utc.astimezone(ZoneInfo("America/New_York"))
    d = ny.date()
    if rule == "prev_bizday_NY":
        dow = d.weekday()  # Mon=0..Sun=6
        if dow == 0:  # Monday
            d = d - timedelta(days=3)
        elif dow == 6:  # Sunday
            d = d - timedelta(days=2)
        elif dow == 5:  # Saturday
            d = d - timedelta(days=1)
        else:
            d = d - timedelta(days=1)
        return d.isoformat()
    return d.isoformat()

def extract_date_from_text(text: str, pattern: str, fmt: str):
    m = re.search(pattern, text)
    if not m:
        return False, "no_match"
    val = m.groupdict().get("ymd", m.group(0))
    try:
        dt = datetime.strptime(val, fmt).date()
        return True, dt.isoformat()
    except Exception as e:
        return False, f"parse_failed:{e}"

_MONTH_MAP = {abbr.lower(): i for i, abbr in enumerate(month_abbr) if abbr}

def parse_flexible_subject_date(text: str, pattern: str, date_order: str = "dmy"):
    m = re.search(pattern, text)
    if not m:
        return False, "no_match"
    d = int(m.group("d"))
    mg = m.group("m")
    y = int(m.group("y"))
    if mg.isalpha():
        month = _MONTH_MAP[mg[:3].lower()]
        day = d
    else:
        mnum = int(mg)
        if date_order.lower() == "mdy":
            month, day = mnum, d
        else:
            month, day = mnum, d
    try:
        return True, f"{y:04d}-{month:02d}-{day:02d}"
    except Exception as e:
        return False, f"normalize_failed:{e}"
