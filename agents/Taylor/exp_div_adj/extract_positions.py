"""Extract daily end-of-day positions per account from dnse_raw_*.jsonl.

Per coding_guidelines §12: filter by accountNo on EVERY record read.
"""
import json, glob, os, sys, csv

ACCOUNTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
LOGDIR = "/home/trido/thanhdt/WorkingClaude/data/execution_logs"

def daily_positions(account_no):
    """Return {date: {ticker: (qty, costPrice)}} using the LAST positions snapshot of each day."""
    out = {}
    for p in sorted(glob.glob(os.path.join(LOGDIR, "dnse_raw_2026-*.jsonl"))):
        d = os.path.basename(p)[9:19]
        best_ts, best = None, None
        for line in open(p):
            try:
                r = json.loads(line)
            except Exception:
                continue
            if r.get("kind") != "positions":
                continue
            items = r.get("payload", {}).get("positions") or []
            # §12 account filter FIRST
            items = [it for it in items if str(it.get("accountNo")) == str(account_no)]
            if not items:
                continue
            ts = r.get("ts") or ""
            if best_ts is None or ts >= best_ts:
                best_ts, best = ts, {
                    it["symbol"]: (it.get("openQuantity"), it.get("costPrice"))
                    for it in items
                }
        if best:
            out[d] = best
    return out

if __name__ == "__main__":
    for lab, acc in ACCOUNTS.items():
        dp = daily_positions(acc)
        w = csv.writer(open(f"/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_div_adj/pos_{lab}.csv", "w", newline=""))
        w.writerow(["date", "ticker", "qty", "cost_price"])
        for d in sorted(dp):
            for t, (q, c) in sorted(dp[d].items()):
                w.writerow([d, t, q, c])
        print(lab, acc, "days:", len(dp), "range:", min(dp), "->", max(dp))
