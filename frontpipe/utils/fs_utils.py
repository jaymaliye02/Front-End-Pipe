"""
Filesystem helpers: atomic moves, sanitizer, and writing status pages.
"""
from __future__ import annotations
import os, shutil, re, html
from typing import List, Dict
from datetime import datetime

INVALID = r'[<>:"/\\|?*]'
INVALID_RE = re.compile(INVALID)

def sanitize_subject(subject: str, maxlen: int = 120) -> str:
    """Sanitize subject for Windows filenames; trims length."""
    cleaned = INVALID_RE.sub("_", subject).strip().rstrip(".")
    return cleaned[:maxlen] if len(cleaned) > maxlen else cleaned

def ensure_drop_folder(base_drop: str, target_date: str) -> str:
    """Create drop/Data Files/<YYYY-MM-DD> if missing and return path."""
    p = os.path.join(base_drop, "Data Files", target_date)
    os.makedirs(p, exist_ok=True)
    return p

def atomic_move(src: str, dst_dir: str) -> str:
    """Move src file into dst_dir with best-effort atomicity; returns final path."""
    os.makedirs(dst_dir, exist_ok=True)
    base = os.path.basename(src)
    dst = os.path.join(dst_dir, base)
    # Simple collision policy: if exists, append (2), (3), ...
    i = 2
    name, ext = os.path.splitext(base)
    while os.path.exists(dst):
        dst = os.path.join(dst_dir, f"{name}({i}){ext}")
        i += 1
    shutil.move(src, dst)
    return dst

def write_status_html(path: str, rows: List[Dict]):
    """Render a tiny status HTML table to path."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    def badge(status: str) -> str:
        colors = {
            "saved": "#2e7d32",
            "pending": "#616161",
            "found": "#0277bd",
            "wrong_date": "#c62828",
            "failed": "#c62828",
            "manual": "#6a1b9a",
        }
        c = colors.get(status, "#424242")
        return f'<span style="background:{c};color:white;padding:2px 6px;border-radius:6px">{html.escape(status)}</span>'

    trs = []
    for r in rows:
        trs.append(
            "<tr>" +
            f"<td>{html.escape(r.get('counterparty',''))}</td>" +
            f"<td>{html.escape(r.get('stream',''))}</td>" +
            f"<td>{html.escape(r.get('channel',''))}</td>" +
            f"<td>{badge(r.get('status',''))}</td>" +
            f"<td>{html.escape(r.get('note',''))}</td>" +
            f"<td>{html.escape(r.get('saved_path','') or '')}</td>" +
            "</tr>"
        )
    html_doc = f"""
<!doctype html>
<html><head><meta charset="utf-8"><title>FrontPipe Status</title></head>
<body style="font-family:Arial,Helvetica,sans-serif">
<h2>FrontPipe Status — {now}</h2>
<table border="1" cellpadding="6" cellspacing="0">
<thead><tr><th>Counterparty</th><th>Stream</th><th>Channel</th><th>Status</th><th>Note</th><th>Saved Path</th></tr></thead>
<tbody>
{''.join(trs)}
</tbody></table>
</body></html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html_doc)
