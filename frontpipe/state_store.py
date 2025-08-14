import os, json
from typing import List, Dict, Optional

class MasterState:
    def __init__(self, dirpath: str):
        self.dir = dirpath
        os.makedirs(self.dir, exist_ok=True)

    def _path(self, ymd: str) -> str:
        return os.path.join(self.dir, f"master_{ymd}.json")

    def load(self, ymd: str) -> Optional[List[Dict]]:
        p = self._path(ymd)
        if not os.path.exists(p):
            return None
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, ymd: str, rows: List[Dict]) -> None:
        p = self._path(ymd)
        with open(p, "w", encoding="utf-8") as f:
            json.dump(rows, f, ensure_ascii=False, indent=2)
