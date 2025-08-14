import argparse, os, json
from frontpipe.reporter import write_status

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD")
    ap.add_argument("--state-dir", default="runtime/state")
    ap.add_argument("--out", default="runtime/status.html")
    args = ap.parse_args()

    p = os.path.join(args.state_dir, f"master_{args.date}.json")
    rows = []
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as f:
            rows = json.load(f)
    write_status(args.out, rows)
    print("Wrote", os.path.abspath(args.out))
