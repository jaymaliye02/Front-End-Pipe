from __future__ import annotations
from typing import List, Dict, Optional
import os
from datetime import datetime, timezone

from .config_schema import validate_config
from .state_store import MasterState
from .logging_event_log import JsonlLogger
from .utils.date_utils import target_date
from .utils.fs_utils import ensure_drop_folder, atomic_move
from .reporter import write_status
from .collectors.email_collector import collect_email

def _load_yaml(path: str) -> Dict:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def _instantiate_master(cfg: Dict, target: str) -> List[Dict]:
    rows = []
    for fd in cfg["feeds"]:
        rows.append({
            "counterparty": fd["counterparty"],
            "stream": fd["stream"],
            "channel": fd["channel"],
            "expected_patterns": fd.get("expected_patterns", {}),
            "date_source": fd.get("date_source", "filename"),
            "report_date_format": fd.get("report_date_format", "%Y%m%d"),
            "arrival_window_local": fd.get("arrival_window_local", "00:00-23:59"),
            "manual": fd.get("manual", False),
            "note": fd.get("note", ""),
            "status": "manual" if fd.get("manual", False) else "pending",
            "saved_path": None,
            "last_event_ts": None,
            "test_ignore_arrival_window": fd.get("test_ignore_arrival_window", False),
            "mailbox": fd.get("mailbox"),
            "folder_path": fd.get("folder_path"),
        })
    return rows

def run_once(cfg_path: str, base_dir: str, now_utc: Optional[datetime] = None) -> Dict:
    now_utc = now_utc or datetime.now(timezone.utc)
    cfg = _load_yaml(cfg_path)
    validate_config(cfg)
    tgt = target_date(cfg.get("target_date_rule", "prev_bizday_NY"), now_utc)

    state = MasterState(os.path.join(base_dir, "runtime", "state"))
    master = state.load(tgt) or _instantiate_master(cfg, tgt)

    logger = JsonlLogger(os.path.join(base_dir, "runtime", "logs", f"events_{tgt}.jsonl"))
    drop_dir = ensure_drop_folder(os.path.join(base_dir, "drop"), tgt)

    for row in master:
        if row["status"] in ("saved","manual","failed"):
            continue
        if row.get("manual"):
            row["status"] = "manual"
            continue

        ch = row["channel"]
        try:
            if ch == "email":
                status, cache_paths, note = collect_email(row, base_dir, tgt)
                row["note"] = note
                if status == "saved" and cache_paths:
                    moved = []
                    for p in cache_paths:
                        final = atomic_move(p, drop_dir); moved.append(final)
                    row["status"] = "saved"
                    row["saved_path"] = ";".join(moved)
                    row["last_event_ts"] = datetime.utcnow().isoformat()
                    logger.write({"counterparty": row["counterparty"], "stream": row["stream"], "event": "saved", "detail": row["saved_path"]})
                elif status == "pending":
                    row["status"] = "pending"
                else:
                    row["status"] = "failed"
            else:
                # TODO: sftp/api/portal collectors
                continue
        except Exception as e:
            row["status"] = "failed"
            row["note"] = f"collector_error:{e}"

    state.save(tgt, master)
    write_status(os.path.join(base_dir, "runtime", "status.html"), master)
    return {"target_date": tgt, "master_rows": master}
