"""Đo tác động quy tắc chain-order: oshares_at canonical (OLD) vs worktree (NEW), mọi mã có AIS.
Một lần fetch BQ (chỉ ĐỌC), cache chia theo mã, gọi từng mã. Ghi CSV mọi ô khác nhau."""
import csv, importlib.util, json, sys, os
from datetime import date
CANON = "/home/trido/thanhdt/WorkingClaude"
WT = "/home/trido/thanhdt/wt-Taylor_20261019_052148/WorkingClaude"
OUT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CANON)                       # corp_action_lib (giống nhau 2 bản)
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path); m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m); return m
OLD = load("osl_old", f"{CANON}/oshares_live.py"); NEW = load("osl_new", f"{WT}/oshares_live.py")
from corp_action_lib import bq
tks = [r["ticker"] for r in bq("""SELECT DISTINCT ticker FROM tav2_bq.corporate_action
  WHERE event_code='AIS' AND event_status='executed' AND shares_total_after IS NOT NULL ORDER BY 1""")]
TODAY = "2026-10-19"
quarters, corp = NEW._fetch(tks, TODAY)
byq, byc = {}, {}
for q in quarters: byq.setdefault(q["ticker"], []).append(q)
for c in corp: byc.setdefault(c["ticker"], []).append(c)
dates = [(TODAY, True), (TODAY, False)]
for y in range(2014, 2027):
    for m in range(1, 13):
        d = date(y, m, 1).isoformat()
        if d <= TODAY: dates.append((d, False))
rows, stat = [], {}
for d, live in dates:
    key = f"{d}|{'live' if live else 'pit'}"
    s = stat.setdefault(key, {"none_to_num": 0, "num_to_none": 0, "num_changed": 0, "none_both": 0, "num_same": 0, "fired": 0})
    for tk in tks:
        cache = (byq.get(tk, []), byc.get(tk, []))
        o = OLD.oshares_at([tk], d, _cache=cache, live=live)[tk]
        n = NEW.oshares_at([tk], d, _cache=cache, live=live)[tk]
        if n.get("ais_chain_redated"): s["fired"] += 1
        ov, nv = o["value"], n["value"]
        if ov is None and nv is None: s["none_both"] += 1; k = None
        elif ov is None: s["none_to_num"] += 1; k = "none_to_num"
        elif nv is None: s["num_to_none"] += 1; k = "num_to_none"
        elif abs(ov - nv) > 0.5: s["num_changed"] += 1; k = "num_changed"
        else: s["num_same"] += 1; k = None
        if k:
            rows.append({"asof": d, "branch": "live" if live else "pit", "ticker": tk, "kind": k,
                         "old_value": ov, "old_method": o["method"], "new_value": nv, "new_method": n["method"],
                         "old_uncertified": o.get("uncertified_value"), "new_anchor": f'{n["anchor_date"]}:{n["anchor_value"]}',
                         "redated": json.dumps(n.get("ais_chain_redated"))})
with open(f"{OUT}/diff_cells.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()) if rows else ["asof"]); w.writeheader(); w.writerows(rows)
json.dump({"n_tickers": len(tks), "stat": stat}, open(f"{OUT}/stat.json", "w"), indent=1)
print("n_tickers", len(tks))
for k in (f"{TODAY}|live", f"{TODAY}|pit"): print(k, stat[k])
agg = {}
for k, v in stat.items():
    if k.endswith("|pit") and not k.startswith(TODAY):
        for kk, vv in v.items(): agg[kk] = agg.get(kk, 0) + vv
print("PIT monthly 2014-01..2026-10 tổng ô:", agg)
