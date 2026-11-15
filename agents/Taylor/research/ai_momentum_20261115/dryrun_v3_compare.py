"""P1-V3: doi chieu SQL su kien (daily.py, nguong v3, dry-run, KHONG ghi ledger) voi events_v3.csv R4 tai cac ngay. Khop = tap (processed + skipped_capacity) == tap events_v3 tai T."""
import sys, tempfile, json, pandas as pd
sys.path.insert(0, "."); import ai_momentum_daily as m
ev = pd.read_csv("events_v3.csv", parse_dates=["time"]); ev = ev[ev.variant == "R4"]
res = []
for T in sys.argv[1:]:
    out = m.run_day(T, "retro", tempfile.mkdtemp(), dry_run=True)
    got = set(out["processed"]) | set(out["skipped_capacity"]); exp = set(ev[ev.time == T].ticker)
    res.append({"T": T, "n_exp": len(exp), "n_sql": len(got), "processed": len(out["processed"]), "skipped_capacity": len(out["skipped_capacity"]),
                "match": got == exp, "only_sql": sorted(got - exp), "only_events": sorted(exp - got)})
    print(json.dumps(res[-1]), flush=True)
print("KHOP", sum(r["match"] for r in res), "/", len(res))
