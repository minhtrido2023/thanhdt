# -*- coding: utf-8 -*-
"""
run_nav_sensitivity.py — economic sensitivity of the DT5G risk gate to the PE-history floor.
Reuses the team-canonical VNINDEX fixed-allocation simulator (sim_dt4g_2000_now.simulate/metrics),
NOT a re-implementation. Window 2014+ (DT deployment scope), plus IS 2014-19 / OOS 2020+ split
and per-year breakdown per team convention.  Job Taylor_20260729_132056.
"""
import os, sys, io
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
# (sim_dt4g_2000_now wraps stdout itself on import)
import pandas as pd, numpy as np
from sim_dt4g_2000_now import simulate, metrics, STATE_ALLOC

E = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_pe2006/out"
V = ["OLD", "NEW", "M2007", "M2008"]

# VNINDEX close — from the same cached VNI pull the state chain used (no new data source)
vni = pd.read_pickle("/home/trido/thanhdt/WorkingClaude/data/_cache_vnindex_2000_now.pkl")
vni["time"] = pd.to_datetime(vni["time"])
vni = vni[["time", "Close"]].sort_values("time")

st = pd.read_csv(f"{E}/dt5g_states_all.csv"); st["time"] = pd.to_datetime(st["time"])

rows, navs = [], {}
for v in V:
    d = vni.merge(st[["time", v]].rename(columns={v: "state"}), on="time", how="inner")
    out, spy, years = simulate(d)
    navs[v] = out.set_index("time")["nav"]
    m = metrics(out["nav"].values, out["time"], out["ret"].values, spy=spy)
    rows.append(dict(variant=v, **{k: m[k] for k in ["cagr", "sharpe", "sortino", "mdd", "calmar", "dd_dur", "final"]}))
    for lbl, lo, hi in [("IS 2014-19", "2014-01-01", "2019-12-31"), ("OOS 2020+", "2020-01-01", "2026-12-31")]:
        s = out[(out.time >= lo) & (out.time <= hi)]
        ms = metrics(s["nav"].values, s["time"], s["ret"].values, spy=spy)
        rows.append(dict(variant=f"{v} [{lbl}]", **{k: ms[k] for k in ["cagr", "sharpe", "sortino", "mdd", "calmar", "dd_dur", "final"]}))

r = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print("=" * 100)
print("DT5G risk-gate NAV sensitivity to PE-history floor (VNINDEX fixed-alloc sim, alloc=%s)" % STATE_ALLOC)
print("=" * 100)
print(r.assign(cagr=lambda x: (x.cagr * 100).round(3), sharpe=lambda x: x.sharpe.round(3),
               sortino=lambda x: x.sortino.round(3), mdd=lambda x: (x.mdd * 100).round(2),
               calmar=lambda x: x.calmar.round(3), final=lambda x: (x.final / 1e9).round(4)).to_string(index=False))

print("\n--- per-year total return (%) ---")
nv = pd.DataFrame(navs)
yr = nv.resample("YE").last()
yr = pd.concat([nv.iloc[[0]], yr])
per = (yr / yr.shift(1) - 1).dropna() * 100
per.index = per.index.year
print(per.round(3).to_string())
print("\nper-year Δ vs NEW (pp):")
print((per.sub(per["NEW"], axis=0)).round(3).to_string())

# self-check: identical state series must give identical NAV to the cent
print("\n--- SELF-CHECK ---")
for a, b in [("NEW", "M2007")]:
    same = int((st[a] != st[b]).sum())
    dv = abs(navs[a].iloc[-1] - navs[b].iloc[-1])
    print(f"  {a} vs {b}: {same} state diffs -> final NAV delta = {dv:,.2f} VND  (expect 0 VND if 0 diffs)")
print(f"  NAV series length {len(nv)} rows, {nv.index.min().date()}..{nv.index.max().date()}")
nv.to_csv(f"{E}/nav_by_variant.csv")
