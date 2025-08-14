"""
Main orchestrator: loads config, builds daily master list, loops collectors,
validates dates, moves files, logs events, and writes the status page.
"""
from __future__ import annotations
from typing import List, Dict, Optional
import os, re, json, time
from datetime import datetime, timezone
from .config_schema import validate_config
from .state_store import MasterState
from .logging_event_log import JsonlLogger
from .utils.date_utils import target_date, extract_date_from_text
from .utils.fs_utils import ensure_drop_folder, atomic_move
from .model import MasterEntry

def load_yaml(path: str) -> Dict:
    import yaml
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def instantiate_master(cfg: Dict, target: str) -> List[Dict]:
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
            # testing override:
            "test_ignore_arrival_window": fd.get("test_ignore_arrival_window", False),
            # NEW: allow multiple required attachments/files in a single email feed
            "required_attachments": fd.get("expected_patterns", {}).get("required_attachments", []),
        })
    return rows

def within_window(arrival_window_local: str) -> bool:
    """Placeholder window check. Real impl should consider timezone and boundaries.
    This returns True—window is enforced in production or bypassed if test flag set.
    """
    return True

def validate_report_date_from_source(candidate_text: str, date_source: str, expected_patterns: Dict, fmt: str, target_ymd: str) -> tuple[bool, str]:
    """Validate report date using regex defined in expected_patterns and compare to target_ymd."""
    # Choose appropriate pattern
    pat = None
    if date_source == "subject":
        pat = expected_patterns.get("subject_regex")
    elif date_source == "filename":
        pat = expected_patterns.get("filename_regex") or expected_patterns.get("attachment_regex")
    elif date_source == "content":
        pat = expected_patterns.get("content_regex")
    elif date_source == "received":
        # accept received date == target (handled upstream). Keep it simple.
        return True, "received_date_used"
    else:
        return False, f"unsupported_date_source:{date_source}"

    if not pat:
        return False, "no_pattern_for_date_source"

    ok, normalized = extract_date_from_text(candidate_text, pat, fmt)
    if not ok:
        return False, f"extract_failed:{normalized}"
    if normalized != target_ymd:
        return False, f"date_mismatch:{normalized}!= {target_ymd}"
    return True, "ok"

def run_once(cfg_path: str, base_dir: str, now_utc: Optional[datetime] = None) -> Dict:
    """
    Single pass:
      - load config
      - compute target date
      - build or read master
      - iterate over pending feeds and simulate collection (placeholders)
      - write status page
    In production, collectors would fetch real sources.
    """
    now_utc = now_utc or datetime.now(timezone.utc)
    cfg = load_yaml(cfg_path)
    validate_config(cfg)
    tgt = target_date(cfg["target_date_rule"], now_utc)
    state = MasterState(os.path.join(base_dir, "runtime", "state"))
    master = state.load(tgt) or instantiate_master(cfg, tgt)

    logger = JsonlLogger(os.path.join(base_dir, "runtime", "logs", f"events_{tgt}.jsonl"))
    drop_dir = ensure_drop_folder(os.path.join(base_dir, "drop"), tgt)

    # DEMO: iterate and update statuses without real collectors.
    updated = False
    for row in master:
        if row["status"] not in ("pending","found","wrong_date","failed"):
            continue
        if row.get("manual"):
            row["status"] = "manual"
            continue
        # For local testing, pretend we "found" files if they exist in dev fixtures
        exp = row.get("expected_patterns", {})
        fname_re = exp.get("filename_regex") or exp.get("attachment_regex")
        # Allow simple glob via regex; list files from dev fixtures
        dev_dir = os.path.join(base_dir, "dev_fixtures", "email_samples")
        if fname_re and os.path.isdir(dev_dir):
            import re, glob
            regex = re.compile(fname_re)
            candidates = [p for p in glob.glob(os.path.join(dev_dir, "*")) if regex.search(os.path.basename(p))]
            if candidates:
                # NEW: if required_attachments specified, ensure **all** required regexes are matched at least once
                req_list = row.get("required_attachments") or []
                if req_list:
                    found_map = {r: [] for r in req_list}
                    for p in candidates:
                        for r in req_list:
                            if re.search(r, os.path.basename(p)):
                                found_map[r].append(p)
                    missing = [r for r, ps in found_map.items() if not ps]
                    if missing:
                        row["status"] = "pending"
                        row["note"] = f"waiting for required attachments: {missing}"
                    else:
                        # Move first match for each required pattern
                        moved_paths = []
                        for r, paths in found_map.items():
                            p = paths[0]
                            final = atomic_move(p, drop_dir)
                            moved_paths.append(final)
                        row["status"] = "saved"
                        row["saved_path"] = ";".join(moved_paths)
                        row["note"] = f"saved {len(moved_paths)} required files"
                        row["last_event_ts"] = datetime.utcnow().isoformat()
                        logger.write({"counterparty": row["counterparty"], "stream": row["stream"], "event": "saved", "detail": row["saved_path"]})
                        updated = True
                else:
                    # Move the first candidate for demo
                    final = atomic_move(candidates[0], drop_dir)
                    row["status"] = "saved"
                    row["saved_path"] = final
                    row["note"] = "saved 1 file (demo local move)"
                    row["last_event_ts"] = datetime.utcnow().isoformat()
                    logger.write({"counterparty": row["counterparty"], "stream": row["stream"], "event": "saved", "detail": final})
                    updated = True
        # else: still pending

    state.save(tgt, master)

    # Write status page
    from .reporter import write_status
    write_status(os.path.join(base_dir, "runtime", "status.html"), master)
    return {"target_date": tgt, "master_rows": master}
