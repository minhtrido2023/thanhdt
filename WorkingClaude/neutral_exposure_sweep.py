# -*- coding: utf-8 -*-
"""
neutral_exposure_sweep.py — CÂU A for dispatch Taylor_20260703_120555.

Extends neutral_exposure_70_vs_94.py from a 2-point (70 vs 94) comparison to a full grid
{70,80,85,90,94,100}% NEUTRAL exposure, SAME method (static hold on NEUTRAL days, cash@0%,
custom30V yieldcombo PIT basket, DT5G state). Goal: is 94% a special risk/return CEILING, or
just an arbitrary point on a smooth Sharpe-neutral / sub-linear-DD curve?

Reports per exposure level: annRet, Sharpe, MaxDD, Calmar (FULL/IS/OOS) + marginal ΔMaxDD per
+step (inflection detector) + 5th-pct forward-window DD tail (6M horizon).
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

GRID = [0.70, 0.80, 0.85, 0.90, 0.94, 1.00]
SN = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
SPY = 250.0

os.environ["BASKET_SELECT"] = "yieldcombo"
lvl, _, memdf, _ = cb.build_pit(bq, "2014-01-01", "2026-06-19", quality="none",
                                rebal="q2m5", gate_rating=3, weight_scheme="namecap")
s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
rb = s.pct_change().dropna()
idx = rb.index

st = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s ORDER BY s.time")
st["time"] = pd.to_datetime(st["time"])
SD = pd.Series(st["state"].values, index=st["time"]).reindex(idx).ffill()
state = SD.astype("Int64")
state_lag = state.shift(1)

def block_metrics(r):
    r = r.dropna()
    if len(r) < 5: return (np.nan, np.nan, np.nan, np.nan)
    cum = (1 + r).cumprod()
    ann = r.mean() * SPY * 100
    sh = r.mean() / r.std() * np.sqrt(SPY) if r.std() > 0 else 0
    dd = (cum / cum.cummax() - 1).min() * 100
    cal = ann / abs(dd) if dd < 0 else np.nan
    return ann, sh, dd, cal

neu = (state_lag == 3)
rb_neu = rb[neu]
WINS = [("FULL 2014->now", None, None),
        ("IS   2014-19", None, pd.Timestamp("2019-12-31")),
        ("OOS  2020->now", pd.Timestamp("2020-01-01"), None)]

print("=" * 100)
print("CÂU A — NEUTRAL exposure sweep {70,80,85,90,94,100}%  (custom30V held only on NEUTRAL days, cash@0%)")
print(f"  NEUTRAL sessions: {int(neu.sum())} / {len(rb)}  ({neu.mean()*100:.1f}%)")
print("=" * 100)
rows = []
for tag, a, b in WINS:
    seg = rb_neu.copy()
    if a is not None: seg = seg[seg.index >= a]
    if b is not None: seg = seg[seg.index <= b]
    print(f"\n  [{tag}]  n_days={len(seg)}")
    print(f"    {'exp':>5}{'annRet%':>9}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'  ΔDD/+step':>12}{'  DD/exp ratio':>15}")
    prev_dd = None
    for e in GRID:
        annr, sh, dd, cal = block_metrics(e * seg)
        ddstep = "" if prev_dd is None else f"{dd - prev_dd:+.2f}pp"
        ratio = dd / e   # MaxDD normalized by exposure — flat ratio => linear; steepening => super-linear
        print(f"    {int(e*100):>4}%{annr:>9.2f}{sh:>8.2f}{dd:>9.2f}{cal:>8.3f}{ddstep:>12}{ratio:>15.2f}")
        rows.append({"window": tag, "exposure": e, "annRet": annr, "sharpe": sh,
                     "maxDD": dd, "calmar": cal, "dd_per_exp": ratio, "n_days": len(seg)})
        prev_dd = dd

# forward-window 5th-pct DD tail per exposure (6M/126) — the tail-risk view
def fwd_dd(start_pos, horizon, e):
    seg = rb.iloc[start_pos + 1: start_pos + 1 + horizon]
    if len(seg) < horizon * 0.6: return np.nan
    path = (1 + e * seg).cumprod()
    return (path / path.cummax() - 1).min() * 100
neu_pos = [i for i in range(len(idx) - 5)
           if pd.notna(state_lag.iloc[i]) and int(state_lag.iloc[i]) == 3]
print("\n" + "=" * 100)
print("  Forward-window (6M/126 sess) within-window DD from EVERY NEUTRAL day — tail per exposure")
print("=" * 100)
print(f"    {'exp':>5}{'medDD%':>10}{'5th-pct DD%':>14}{'  Δ5pctDD/+step':>17}")
prev_p5 = None
for e in GRID:
    dds = np.array([fwd_dd(p, 126, e) for p in neu_pos])
    med = np.nanmedian(dds); p5 = np.nanpercentile(dds, 5)
    step = "" if prev_p5 is None else f"{p5 - prev_p5:+.2f}pp"
    print(f"    {int(e*100):>4}%{med:>10.2f}{p5:>14.2f}{step:>17}")
    rows.append({"window": "fwd6M_tail", "exposure": e, "medDD_6M": med, "p05DD_6M": p5})
    prev_p5 = p5

out = pd.DataFrame(rows)
outp = os.path.join(WORKDIR, "data", "neutral_exposure_sweep.csv")
out.to_csv(outp, index=False)
print(f"\n  [audit CSV] {outp}")
print("  DONE.")
