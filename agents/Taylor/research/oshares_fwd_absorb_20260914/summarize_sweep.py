"""Tóm tắt sweep trước/sau vá + đánh dấu mã đang nắm giữ (lọc account_no, §12)."""
import json, collections, glob, os
rows = json.load(open("sweep_before_after_20260914.json"))
raw = sorted(glob.glob("/home/trido/thanhdt/WorkingClaude/data/execution_logs/dnse_raw_*.jsonl"))[-1]
ACCTS = {"SpaceX": "0002023347", "ZaloPay": "0001743768"}
held = {}
for label, acct in ACCTS.items():
    last = None
    for l in open(raw):
        r = json.loads(l)
        if r.get("kind") != "positions" or str(r.get("account_no")) != acct: continue
        last = r
    held[label] = {p["symbol"]: p.get("openQuantity") for p in (last or {}).get("payload", {}).get("positions", [])
                   if p.get("status") == "OPEN" and (p.get("openQuantity") or 0) > 0}
out, C = [], collections.Counter()
for r in rows:
    for br in ("live", "pit"):
        o, n = r[f"old_{br}"], r[f"new_{br}"]
        if o["value"] == n["value"] and o["method"] == n["method"]: continue
        ov, nv = o["value"], n["value"]
        fa = n.get("fwd_absorption") or {}
        C[(br, n["method"], fa.get("verdict"))] += 1
        out.append({"branch": br, "ticker": r["ticker"], "row_time": r["row_time"], "asof": r["asof"],
                    "row_value": r["row_value"], "old": ov, "old_method": o["method"], "new": nv,
                    "new_method": n["method"], "verdict": fa.get("verdict"),
                    "pct_old_vs_new": (None if (ov is None or nv is None) else round((ov/nv-1)*100, 3)),
                    "events": [(e["exright_date"], e["issue_volumn"], e["method_vi"]) for e in r["fwd"]],
                    "held": {k: v[r["ticker"]] for k, v in held.items() if r["ticker"] in v},
                    "note": fa.get("note")})
json.dump({"raw_positions_file": os.path.basename(raw), "held": held, "changes": out},
          open("sweep_changes_20260914.json", "w"), ensure_ascii=False, indent=1)
print("raw:", raw, {k: len(v) for k, v in held.items()})
print(C)
unchanged_bad = [r for r in rows if r["old_live"]["value"] != r["new_live"]["value"] and False]
for x in out:
    if x["branch"] == "live":
        print(f"{x['ticker']:4} row={x['row_time']} asof={x['asof']} {x['old_method']:>17}->{x['new_method']:<25} "
              f"old={x['old'] and f'{x['old']:,.0f}'} new={x['new'] and f'{x['new']:,.0f}'} pct={x['pct_old_vs_new']} held={x['held']}")
pit_only = {(x["ticker"], x["row_time"]) for x in out if x["branch"] == "pit"} - {(x["ticker"], x["row_time"]) for x in out if x["branch"] == "live"}
print("PIT-only changes:", sorted(pit_only))
