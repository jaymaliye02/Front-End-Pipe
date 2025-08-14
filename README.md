# FrontPipe (lean data ingestion)

A minimal, **config-first**, idempotent ingestion runner that pulls files from email / (S)FTP / API,
validates report dates, and drops them into `drop/Data Files/<YYYY-MM-DD>`.

**Key ideas**
- One YAML config drives everything (add feeds without writing code).
- Cache → validate → atomic move to final folder.
- Dynamic **master list** per target date + JSONL event log.
- 05:25 AM HTML report email + local `runtime/status.html` dashboard.
- Works from CLI **and** Jupyter (debug notebook included).

> This repo ships *system skeleton + test harness*. Wire Outlook/FTP/API creds at work and extend collectors as needed.
