import argparse, os
from datetime import datetime, timezone
from frontpipe.orchestrator import run_once

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=False, default="config/frontpipe.sample.yaml")
    ap.add_argument("--base", required=False, default=".")
    args = ap.parse_args()
    res = run_once(args.config, args.base, now_utc=datetime.now(timezone.utc))
    print("Target date:", res["target_date"])
    for r in res["master_rows"]:
        print(r["counterparty"], r["stream"], r["status"], r.get("note",""), r.get("saved_path",""))
    print("Status page:", os.path.abspath(os.path.join(args.base, "runtime", "status.html")))
