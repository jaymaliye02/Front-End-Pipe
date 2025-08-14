from __future__ import annotations
import os, re, zipfile
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
from win32com.client import gencache, constants

from frontpipe.utils.fs_utils import sanitize_subject
from frontpipe.utils.date_utils import extract_date_from_text, parse_flexible_subject_date

def _get_folder(mailbox: str, folder_path: List[str]):
    app = gencache.EnsureDispatch("Outlook.Application")
    ns = app.GetNamespace("MAPI")
    root = None
    for store in ns.Folders:
        if store.Name.lower() == mailbox.lower():
            root = store; break
    if root is None:
        raise RuntimeError(f"Mailbox not found: {mailbox}")
    cur = root
    for name in folder_path:
        found = None
        for f in cur.Folders:
            if f.Name.lower() == name.lower():
                found = f; break
        if not found:
            raise RuntimeError(f"Folder not found under {cur.Name}: {name}")
        cur = found
    return cur

def _within_arrival(items, ignore_window: bool):
    items.Sort("[ReceivedTime]", True)
    if ignore_window:
        cutoff = datetime.now() - timedelta(days=2)
        try:
            return items.Restrict(f"[ReceivedTime] >= '{cutoff:%m/%d/%Y %I:%M %p}'")
        except Exception:
            return items
    return items

def collect_email(feed: Dict, base_dir: str, target_ymd: str) -> Tuple[str, List[str], str]:
    if feed.get("manual"):
        return "manual", [], "manual feed"

    mailbox = feed.get("mailbox")
    folder_path = feed.get("folder_path") or ["Inbox"]
    ignore_window = bool(feed.get("test_ignore_arrival_window", False))
    patt = feed.get("expected_patterns", {})
    subj_re = patt.get("subject_regex")
    att_re = patt.get("attachment_regex")
    req_atts = patt.get("required_attachments") or []
    extract_only = patt.get("extract_only")
    date_source = feed.get("date_source", "filename")
    fmt = feed.get("report_date_format", "%Y%m%d")
    date_order = patt.get("date_order", "dmy")

    folder = _get_folder(mailbox, folder_path) if mailbox else _get_folder("Inbox", [])
    items = _within_arrival(folder.Items, ignore_window)

    cache_dir = os.path.join(base_dir, "runtime", "inbox_email_cache"); os.makedirs(cache_dir, exist_ok=True)

    matched = 0
    saved = []

    for m in list(items):
        sub = str(getattr(m, "Subject", "") or "")
        if subj_re and not re.search(subj_re, sub):
            continue
        matched += 1

        # Date validation (subject) if configured
        if date_source == "subject" and subj_re:
            if isinstance(fmt, str) and fmt.startswith("auto"):
                order = (fmt.split(":",1)[1] if ":" in fmt else "dmy")
                ok, ymd = parse_flexible_subject_date(sub, subj_re, order)
            else:
                ok, ymd = extract_date_from_text(sub, subj_re, fmt)
            if not ok or ymd != target_ymd:
                continue

        # Save .msg (Unicode first, fallback to classic)
        if patt.get("save_msg"):
            out = os.path.join(cache_dir, sanitize_subject(sub) + ".msg")
            try:
                try:
                    m.SaveAs(out, getattr(constants, "olMSGUnicode", 9))
                except Exception:
                    m.SaveAs(out, getattr(constants, "olMSG", 3))
                saved.append(out)
            except Exception as e:
                return "failed", saved, f"save_msg_error:{e}"

        # Save attachments
        have_names = []
        attachments = list(getattr(m, "Attachments", []) or [])
        for att in attachments:
            name = str(getattr(att, "FileName", "") or "")
            keep = False
            if req_atts:
                keep = any(re.search(r, name) for r in req_atts)
            elif att_re and re.search(att_re, name):
                keep = True

            if keep:
                out = os.path.join(cache_dir, name)
                att.SaveAsFile(out)
                saved.append(out); have_names.append(name)

                # If zip and extract_only configured
                if extract_only and name.lower().endswith(".zip"):
                    try:
                        import zipfile
                        with zipfile.ZipFile(out, "r") as zf:
                            for nm in zf.namelist():
                                if re.search(extract_only, os.path.basename(nm)):
                                    zf.extract(nm, cache_dir)
                                    saved.append(os.path.join(cache_dir, os.path.basename(nm)))
                    except Exception as e:
                        return "failed", saved, f"zip_extract_error:{e}"

        if req_atts:
            ok_all = all(any(re.search(r, n) for n in have_names) for r in req_atts)
            if not ok_all:
                continue

        break

    if matched == 0:
        return "pending", saved, "no_matching_email"
    return ("saved" if saved else "pending"), saved, "email saved to cache"
