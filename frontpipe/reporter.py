import os, html

def write_status(path: str, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    def esc(x): return html.escape(str(x or ""))
    html_rows = []
    for r in rows:
        html_rows.append(f"<tr><td>{esc(r.get('counterparty'))}</td>"
                         f"<td>{esc(r.get('stream'))}</td>"
                         f"<td>{esc(r.get('channel'))}</td>"
                         f"<td>{esc(r.get('status'))}</td>"
                         f"<td>{esc(r.get('note'))}</td>"
                         f"<td>{esc(r.get('saved_path'))}</td></tr>")
    body = f"""<!doctype html><html><head><meta charset="utf-8">
<title>FrontPipe Status</title>
<style>body{{font-family:sans-serif}} table{{border-collapse:collapse}} td,th{{border:1px solid #ccc;padding:6px}}</style>
</head><body>
<h2>FrontPipe Status</h2>
<table>
<tr><th>Counterparty</th><th>Stream</th><th>Channel</th><th>Status</th><th>Note</th><th>Saved Path</th></tr>
{''.join(html_rows)}
</table>
</body></html>"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
