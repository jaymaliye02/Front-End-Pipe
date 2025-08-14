#!/usr/bin/env python3
"""
CLI entry: run one orchestrator pass (sufficient for testing).

Usage:
  python scripts/run_frontpipe.py --config config/frontpipe.sample.yaml
"""
import argparse, os
from datetime import datetime, timezone
from frontpipe.orchestrator import run_once

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", default="config/frontpipe.sample.yaml")
    p.add_argument("--base", default=".")
    args = p.parse_args()
    res = run_once(args.config, os.path.abspath(args.base))
    print("Target date:", res["target_date"])
    for row in res["master_rows"]:
        print(row["counterparty"], row["stream"], row["status"], row.get("note",""))

if __name__ == "__main__":
    main()
