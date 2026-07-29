# -*- coding: utf-8 -*-
"""
run_macro.py — apply the LIVE DT5G macro layer (macro_state_live.get_macro_state) on top of
each PE-variant v3.4b base, by intercepting the base-state BQ read and substituting the
variant series. Everything else (VNINDEX px, US VIX/SPX, SBV, breadth) is the real live input,
identical across variants — so any output difference is attributable to the PE channel only.

Job Taylor_20260729_132056. Read-only w.r.t. production; writes only into exp_pe2006/out/.
"""
import os, sys, io
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import pandas as pd, numpy as np

E = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pe2006/out"
START, END = "2014-01-01", "2026-07-29"
VARIANTS = ["OLD", "NEW", "M2007", "M2008"]

from simulate_holistic_nav import bq as real_bq
import macro_state_live as msl

def make_bq(variant):
    base = pd.read_csv(f"{E}/v34b_{variant}.csv")
    base["time"] = pd.to_datetime(base["time"])
    def _bq(sql):
        if "vnindex_5state_tam_quan_v34b_clean" in sql:
            lo = pd.Timestamp(sql.split("DATE '")[1][:10])
            hi = pd.Timestamp(sql.split("DATE '")[2][:10])
            d = base[(base.time >= lo) & (base.time <= hi)][["time", "state"]].copy()
            print(f"    [shim] base injected: {variant}  {len(d)} rows {d.time.min().date()}..{d.time.max().date()}")
            return d
        return real_bq(sql)
    return _bq

res = {}
for v in VARIANTS:
    print(f"=== macro layer on base {v} ===")
    m = msl.get_macro_state(START, END, bq=make_bq(v))
    m = m.set_index("time")
    res[v] = m
    m.reset_index().to_csv(f"{E}/dt5g_{v}.csv", index=False)

st = pd.DataFrame({v: res[v]["state"] for v in VARIANTS})
d4 = pd.DataFrame({v: res[v]["state_dt4"] for v in VARIANTS})
st.reset_index().to_csv(f"{E}/dt5g_states_all.csv", index=False)

NAM = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EXBULL"}
W = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
print("\n" + "=" * 72)
print("DT5G (macro-gated, production consumer view) — pairwise diffs")
for label, df in [("state_dt4 (no macro)", d4), ("state DT5G (with macro)", st)]:
    print(f"\n--- {label} (n={len(df)}, {df.index.min().date()}..{df.index.max().date()})")
    for a, b in [("OLD", "NEW"), ("NEW", "M2008"), ("OLD", "M2008"), ("NEW", "M2007")]:
        diff = df[a] != df[b]
        n = int(diff.sum())
        dw = (df[a].map(W) - df[b].map(W)).abs()
        print(f"   {a:6s} vs {b:6s}: {n:4d} sessions ({n/len(df)*100:5.2f}%)  max|Δweight|={dw.max()*100:.0f}pp  Σ|Δw|·d={dw.sum():.1f}")
    print("   dist %:", {v: {NAM[k]: round(x * 100, 1) for k, x in df[v].value_counts(normalize=True).sort_index().items()} for v in VARIANTS})

print("\nLatest 5 sessions, DT5G state:")
print(st.tail(5).to_string())
print("\nDiffering DT5G sessions (NEW vs M2008):")
m = st["NEW"] != st["M2008"]
if m.any():
    print(st[m].assign(dt4_NEW=d4["NEW"][m], dt4_M2008=d4["M2008"][m]).to_string())
else:
    print("  (none)")
