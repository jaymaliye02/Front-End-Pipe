"""
Dataclasses for master list entries and event records.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict
from datetime import datetime

@dataclass
class MasterEntry:
    counterparty: str
    stream: str
    channel: str
    expected_patterns: Dict
    date_source: str
    report_date_format: str
    arrival_window_local: str
    manual: bool = False
    note: str = ""
    status: str = "pending"  # pending|found|wrong_date|saved|failed|manual
    saved_path: Optional[str] = None
    last_event_ts: Optional[str] = None

@dataclass
class EventRecord:
    timestamp: str
    counterparty: str
    stream: str
    event: str    # found|saved|wrong_date|error|manual
    detail: str = ""
