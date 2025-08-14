"""
State persistence for the daily master list.
"""
from __future__ import annotations
from typing import List, Dict
import os, json

class MasterState:
    def __init__(self, state_dir: str):
        self.state_dir = state_dir
        os.makedirs(self.state_dir, exist_ok=True)

    def path_for(self, target_date: str) -> str:
        return os.path.join(self.state_dir, f"master_{target_date}.json")

    def save(self, target_date: str, rows: List[Dict]):
        with open(self.path_for(target_date), "w", encoding="utf-8") as f:
            json.dump(rows, f, indent=2)

    def load(self, target_date: str) -> List[Dict]:
        p = self.path_for(target_date)
        if not os.path.exists(p):
            return []
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
