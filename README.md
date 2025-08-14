# FrontPipe v2 (full)

Key updates:
- Outlook `.msg` save using **Unicode MSG** first, fallback to classic MSG.
- Hardened `sanitize_subject` (handles `[External]`, slashes, Windows-invalid chars).
- Non-demo orchestrator that dispatches to collectors and moves to `drop/Data Files/<YYYY-MM-DD>`.
- Flexible date helpers.
- **Per-feed mailbox/folder** in YAML.
- Fast feed builder notebook.

## Install
```bash
pip install --no-deps -e ".[dev]"
```

## Run
```bash
python scripts/run_frontpipe.py --config config/frontpipe.sample.yaml
```

Edit `config/frontpipe.sample.yaml` for your mailbox/folder/regex.
