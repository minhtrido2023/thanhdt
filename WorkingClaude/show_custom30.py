# -*- coding: utf-8 -*-
"""show_custom30.py — list the "8L custom30" parking basket (custompitg) membership per
quarterly rebalance (q2m5: 05-Feb/May/Aug/Nov), PIT, gate 8L rating<=3.
Source = CUSTOM_MEMBERS records in the latest custompitg audit CSV (== what V2.3 live uses).
Usage: python show_custom30.py [since_date=2025-01-01]"""
import pandas as pd, os, sys, glob
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
cands = glob.glob(os.path.join(WORKDIR, "data",
        "v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg*.csv"))
cands = [c for c in cands if "custompitgq" not in c]
f = max(cands, key=os.path.getmtime)   # most recent custompitg audit
print(f"source: {os.path.basename(f)}\n")
df = pd.read_csv(f, low_memory=False)
m = df[df["record_type"] == "CUSTOM_MEMBERS"].copy()
m["ymd"] = pd.to_datetime(m["ymd"])
since = pd.Timestamp(sys.argv[1] if len(sys.argv) > 1 else "2025-01-01")
m = m[m["ymd"] >= since]
m["rating"]   = m["reason"].str.extract(r"rating=([\d.]+)")[0]
m["liq_rank"] = m["reason"].str.extract(r"liq_rank=([\d.]+)")[0].astype(float).astype(int)
m["quarter"]  = m["reason"].str.extract(r"quarter=(\S+)")[0]

prev = set()
for d, g in m.groupby("ymd"):
    g = g.sort_values("liq_rank")
    cur = list(g["ticker"])
    q = g["quarter"].iloc[0]
    entered = [t for t in cur if t not in prev]
    exited  = [t for t in prev if t not in cur]
    names = [f"{t}[{str(r).rstrip('0').rstrip('.')}]" for t, r in zip(g["ticker"], g["rating"])]
    print(f"=== rebal {d.date()}  (BCTC quý {q})  —  {len(cur)} mã ===")
    print("  " + ", ".join(names))
    if prev:
        print(f"   + vào: {', '.join(entered) or '—'}    - ra: {', '.join(exited) or '—'}")
    print()
    prev = set(cur)
print("Ghi chú: [n] = rating 8L tại kỳ đó (gate <=3). Sắp theo thanh khoản (liq_rank).")
