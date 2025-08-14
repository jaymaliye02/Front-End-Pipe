"""
SLA report + local status page generator.
"""
from __future__ import annotations
from typing import List, Dict
from .utils.fs_utils import write_status_html

def compose_counts(rows: List[Dict]) -> Dict[str, int]:
    counts = {}
    for r in rows:
        s = r.get("status","pending")
        counts[s] = counts.get(s,0)+1
    return counts

def build_html_email(rows: List[Dict]) -> str:
    """Return a basic HTML for emailing via Outlook (send step left to user)."""
    counts = compose_counts(rows)
    summary = " | ".join(f"{k}: {v}" for k,v in counts.items())
    # Simple HTML table (reuse of status page possible)
    body = ["<h3>FrontPipe SLA Summary</h3>", f"<p>{summary}</p>", "<table border='1' cellpadding='6' cellspacing='0'>"]
    body.append("<thead><tr><th>Counterparty</th><th>Stream</th><th>Channel</th><th>Status</th><th>Note</th></tr></thead><tbody>")
    for r in rows:
        body.append("<tr>" +
                    f"<td>{r.get('counterparty')}</td>" +
                    f"<td>{r.get('stream')}</td>" +
                    f"<td>{r.get('channel')}</td>" +
                    f"<td>{r.get('status')}</td>" +
                    f"<td>{r.get('note','')}</td>" +
                    "</tr>")
    body.append("</tbody></table>")
    return "".join(body)

def write_status(path: str, rows: List[Dict]):
    """Write/refresh local status dashboard."""
    write_status_html(path, rows)
