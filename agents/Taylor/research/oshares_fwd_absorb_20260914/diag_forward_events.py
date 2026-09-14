"""Chẩn đoán: dòng ticker_financial làm neo (12 tháng gần nhất) × ISS có exright SAU ngày dòng quý.
Chỉ ĐỌC. Import oshares_live từ OSH_ROOT (mặc định worktree) để so trước/sau vá."""
import importlib.util, json, os, sys
from datetime import date, timedelta
MAIN = "/home/trido/thanhdt/WorkingClaude"
WT = os.environ.get("OSH_WT", "/home/trido/thanhdt-wt-oshares-finfb-dblcount/WorkingClaude")
sys.path.insert(0, MAIN)
from corp_action_lib import bq, dilutes_share_count, TABLE  # noqa

def load(name, root):
    spec = importlib.util.spec_from_file_location(name, os.path.join(root, "oshares_live.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m); return m

old = load("osh_old", MAIN)
new = load("osh_new", WT) if os.environ.get("OSH_COMPARE") else None
END = os.environ.get("OSH_END", "2026-09-14")
START = (date.fromisoformat(END) - timedelta(days=365)).isoformat()

tks = [r["ticker"] for r in bq(f"""
  SELECT DISTINCT ticker FROM `{TABLE}` WHERE event_status="executed" AND event_code="ISS"
  AND exright_date > DATE "{START}" AND exright_date <= DATE "{END}" ORDER BY ticker""")]
print("tickers with ISS in window:", len(tks), file=sys.stderr)
quarters, corp = [], []
for i in range(0, len(tks), 80):
    q, c = old._fetch(tks[i:i+80], END); quarters += q; corp += c
cache = (quarters, corp)
rows = []
for tk in tks:
    qs = sorted([q for q in quarters if q["ticker"] == tk], key=lambda r: r["time"])
    iss = [c for c in corp if c["ticker"] == tk and c["event_code"] == "ISS" and c["exright_date"]
           and dilutes_share_count(c)]
    for j, q in enumerate(qs):
        nxt = qs[j+1]["time"] if j+1 < len(qs) else None
        if nxt and nxt <= START: continue
        hi = END if not nxt else min(END, (date.fromisoformat(nxt) - timedelta(days=1)).isoformat())
        if hi < q["time"]: continue
        fwd = old._dedup_iss([e for e in iss if q["time"] < e["exright_date"] <= hi])
        lst = [e for e in iss if e["exright_date"] <= q["time"] and (e.get("listing_date") or "") > q["time"]]
        if not fwd and not lst: continue
        asof = hi
        prev = qs[j-1] if j > 0 else None
        rec = {"ticker": tk, "row_time": q["time"], "row_value": float(q["OShares"]),
               "prev_time": prev["time"] if prev else None,
               "prev_value": float(prev["OShares"]) if prev else None, "asof": asof,
               "fwd": [old._event_dict(e) for e in fwd],
               "listing_after_only": [old._event_dict(e) for e in lst]}
        for lbl, mod in (("old", old), ("new", new)):
            if mod is None: continue
            for live in (True, False):
                r = mod.oshares_at([tk], asof, _cache=cache, live=live)[tk]
                rec[f"{lbl}_{'live' if live else 'pit'}"] = {
                    "value": r["value"], "method": r["method"], "anchor_date": r["anchor_date"],
                    "anchor_source": r["anchor_source"],
                    "applied": [(e["exright_date"], e.get("applied_size")) for e in r.get("events_applied", [])],
                    "fwd_absorption": r.get("forward_absorption")}
        rows.append(rec)
out = os.environ.get("OSH_OUT", "diag_forward_events.json")
json.dump(rows, open(out, "w"), ensure_ascii=False, indent=1, default=str)
print("rows:", len(rows), "->", out, file=sys.stderr)
