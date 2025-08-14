#!/usr/bin/env python3
"""
CLI entry: regenerate the status page from saved master state (no fetching).

Usage:
  python scripts/generate_report.py --date 2025-08-13 --base .
"""
import argparse, os, json
from frontpipe.state_store import MasterState
from frontpipe.reporter import write_status

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--date", required=True, help="YYYY-MM-DD")
    p.add_argument("--base", default=".")
    args = p.parse_args()

    state = MasterState(os.path.join(args.base, "runtime", "state"))
    rows = state.load(args.date)
    if not rows:
        raise SystemExit("No state for that date.")
    write_status(os.path.join(args.base, "runtime", "status.html"), rows)
    print("Wrote runtime/status.html")

if __name__ == "__main__":
    main()
