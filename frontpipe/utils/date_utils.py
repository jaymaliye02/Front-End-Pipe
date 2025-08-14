"""
Date utilities: target date rules, parsing helpers.
"""
from __future__ import annotations
from datetime import datetime, timedelta
from dateutil.tz import gettz
import re

NY = gettz("America/New_York")

def target_date(rule: str, now_utc: datetime) -> str:
    """
    Compute the target report date as YYYY-MM-DD string based on rule.
    Supported: 'today_NY', 'prev_bizday_NY' (simple version excluding weekends).
    """
    now_ny = now_utc.astimezone(NY)
    d = now_ny.date()
    if rule == "today_NY":
        pass
    elif rule == "prev_bizday_NY":
        # naive weekend roll
        if d.weekday() == 0:  # Monday
            d = d - timedelta(days=3)
        elif d.weekday() == 6:  # Sunday
            d = d - timedelta(days=2)
        else:
            d = d - timedelta(days=1)
    else:
        raise ValueError(f"Unsupported target_date_rule: {rule}")
    return d.isoformat()

def extract_date_from_text(text: str, regex_pattern: str, fmt: str) -> tuple[bool, str]:
    """
    Attempt to extract date via named group or overall match.
    Returns (ok, ymd_string) where ymd_string is normalized YYYY-MM-DD if parseable,
    else (False, reason).
    """
    m = re.search(regex_pattern, text)
    if not m:
        return False, "no_match"
    grp = m.groupdict()
    value = None
    if "ymd" in grp:
        value = grp["ymd"]
    else:
        value = m.group(0)
    # Normalize using fmt if possible
    try:
        dt = datetime.strptime(value, fmt)
        return True, dt.strftime("%Y-%m-%d")
    except Exception as e:
        return False, f"parse_failed:{e}"
