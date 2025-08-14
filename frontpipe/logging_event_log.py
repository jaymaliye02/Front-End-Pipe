"""
JSONL event logger. Each call appends a record; easy to grep and summarize.
"""
from __future__ import annotations
from typing import Dict
from datetime import datetime
import os, json

class JsonlLogger:
    def __init__(self, log_path: str):
        self.log_path = log_path
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)

    def write(self, record: Dict):
        rec = dict(record)
        if "timestamp" not in rec:
            rec["timestamp"] = datetime.utcnow().isoformat()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
