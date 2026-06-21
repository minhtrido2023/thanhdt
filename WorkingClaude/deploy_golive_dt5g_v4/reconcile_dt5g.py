# -*- coding: utf-8 -*-
"""
reconcile_dt5g.py  —  localize the divergence between two DT5G daily series
===========================================================================
Dev tool: pinpoints EXACTLY where a deploy run diverges from the reference
(dt5g_daily_reference.csv), so the ~1% gap can be diagnosed fast.

USAGE:
    python reconcile_dt5g.py YOUR_daily.csv [reference.csv]
    (reference defaults to dt5g_daily_reference.csv next to this script)

YOUR_daily.csv only needs a date column + as many of these as you produce:
    state (the DT5G/published state), weight, nav.
Column names are auto-detected (date|time ; state|dt5g_state ; weight|w ; nav).
The script aligns on date and reports:
  1. date-coverage mismatch,
  2. FIRST state mismatch + total count + sample,
  3. FIRST weight mismatch + count,
  4. NAV reconciliation: CAGR of each (rebased 1B on common start), the gap, and the
     TOP-10 dates by |daily-return difference| — that is where the gap accumulates.
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

HERE = os.path.dirname(os.path.abspath(__file__))

def _find(cols, *cands):
    low = {c.lower(): c for c in cols}
    for c in cands:
        if c in low: return low[c]
    for c in cands:                      # substring fallback
        for lc, orig in low.items():
            if c in lc: return orig
    return None

def load(path):
    df = pd.read_csv(path)
    tc = _find(df.columns, "time", "date")
    sc = _find(df.columns, "dt5g_state", "macro_state", "state")
    wc = _find(df.columns, "weight", "w_macro", "w")
    nc = _find(df.columns, "nav_rebased_1b", "nav")
    if tc is None: raise SystemExit(f"{path}: no date/time column found")
    out = pd.DataFrame({"time": pd.to_datetime(df[tc])})
    if sc is not None: out["state"] = pd.to_numeric(df[sc], errors="coerce")
    if wc is not None: out["weight"] = pd.to_numeric(df[wc], errors="coerce")
    if nc is not None: out["nav"] = pd.to_numeric(df[nc], errors="coerce")
    return out.dropna(subset=["time"]).sort_values("time").reset_index(drop=True), dict(time=tc, state=sc, weight=wc, nav=nc)

cand_path = sys.argv[1] if len(sys.argv) > 1 else None
ref_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "dt5g_daily_reference.csv")
if not cand_path:
    print("USAGE: python reconcile_dt5g.py YOUR_daily.csv [reference.csv]"); raise SystemExit(1)
if not os.path.exists(ref_path):
    ref_path = os.path.join(HERE, "data", "dt5g_daily_reference.csv")

ref, rmap = load(ref_path); cand, cmap = load(cand_path)
print("="*78)
print(f"REFERENCE : {ref_path}\n            cols={rmap}\n            {len(ref)} rows {ref['time'].min().date()}->{ref['time'].max().date()}")
print(f"CANDIDATE : {cand_path}\n            cols={cmap}\n            {len(cand)} rows {cand['time'].min().date()}->{cand['time'].max().date()}")
print("="*78)

# 1. coverage
only_ref = set(ref["time"]) - set(cand["time"]); only_cand = set(cand["time"]) - set(ref["time"])
if only_ref or only_cand:
    print(f"[COVERAGE] dates only in reference: {len(only_ref)} (e.g. {sorted(only_ref)[:3]})")
    print(f"           dates only in candidate: {len(only_cand)} (e.g. {sorted(only_cand)[:3]})")
else:
    print("[COVERAGE] identical date sets ✓")
m = ref.merge(cand, on="time", suffixes=("_ref", "_cand")).sort_values("time").reset_index(drop=True)
print(f"[ALIGNED]  {len(m)} common dates\n")

# 2. state
if "state_ref" in m and "state_cand" in m:
    sd = m[m["state_ref"] != m["state_cand"]]
    if len(sd):
        f = sd.iloc[0]
        print(f"[STATE]    {len(sd)} mismatches. FIRST: {f['time'].date()}  ref={int(f['state_ref'])} cand={int(f['state_cand'])}")
        print(sd.head(10)[["time","state_ref","state_cand"]].to_string(index=False))
    else:
        print("[STATE]    identical ✓")
else:
    print("[STATE]    (one side lacks a state column — skipped)")

# 3. weight
if "weight_ref" in m and "weight_cand" in m:
    wd = m[(m["weight_ref"] - m["weight_cand"]).abs() > 1e-6]
    if len(wd):
        f = wd.iloc[0]
        print(f"\n[WEIGHT]   {len(wd)} mismatches. FIRST: {f['time'].date()}  ref={f['weight_ref']:.4f} cand={f['weight_cand']:.4f}")
        print(wd.head(10)[["time","weight_ref","weight_cand"]].to_string(index=False))
    else:
        print("\n[WEIGHT]   identical ✓")

# 4. NAV reconciliation — where the % gap accumulates
if "nav_ref" in m and "nav_cand" in m:
    mm = m.dropna(subset=["nav_ref","nav_cand"]).reset_index(drop=True)
    nr = mm["nav_ref"].values / mm["nav_ref"].values[0]
    nc = mm["nav_cand"].values / mm["nav_cand"].values[0]
    yrs = (mm["time"].iloc[-1]-mm["time"].iloc[0]).days/365.25
    cr = (nr[-1])**(1/yrs)-1; cc = (nc[-1])**(1/yrs)-1
    print(f"\n[NAV]      rebased 1.0 on {mm['time'].iloc[0].date()}")
    print(f"           reference final {nr[-1]:.4f}  CAGR {cr*100:.2f}%")
    print(f"           candidate final {nc[-1]:.4f}  CAGR {cc*100:.2f}%")
    print(f"           >>> GAP: final {(nc[-1]/nr[-1]-1)*100:+.2f}%   CAGR {(cc-cr)*100:+.2f}pp")
    rr = np.zeros(len(mm)); rr[1:] = nr[1:]/nr[:-1]-1
    rc = np.zeros(len(mm)); rc[1:] = nc[1:]/nc[:-1]-1
    mm = mm.assign(ret_diff=rc-rr)
    top = mm.reindex(mm["ret_diff"].abs().sort_values(ascending=False).index).head(10)
    print("           TOP-10 dates by |daily-return difference| (where the gap is born):")
    cols = ["time","ret_diff"] + [c for c in ["state_ref","state_cand","weight_ref","weight_cand"] if c in mm]
    print(top[cols].to_string(index=False))
print("="*78)
print("Tip: if STATE matches but NAV diverges -> it's the NAV mechanics (deposit rate,")
print("     TC/tax, T+1 lag, weight ceiling). If STATE diverges first -> upstream state")
print("     source differs (DT4 base table/CSV vintage, breadth feed, US/SBV inputs).")
