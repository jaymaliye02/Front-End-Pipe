from typing import Dict, Any

def validate_config(cfg: Dict[str, Any]) -> None:
    if not isinstance(cfg, dict):
        raise ValueError("Config must be a dict.")
    if "feeds" not in cfg or not isinstance(cfg["feeds"], list):
        raise ValueError("Config must have a 'feeds' list.")
    for f in cfg["feeds"]:
        if "counterparty" not in f or "stream" not in f or "channel" not in f:
            raise ValueError("Each feed needs counterparty, stream, channel.")
        f.setdefault("expected_patterns", {})
        f.setdefault("date_source", "filename")
        f.setdefault("report_date_format", "%Y%m%d")
        f.setdefault("arrival_window_local", "00:00-23:59")
        f.setdefault("manual", False)
