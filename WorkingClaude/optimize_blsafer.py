# -*- coding: utf-8 -*-
"""
optimize_blsafer.py
===================
Drill-down on BL_safer (asym confirmation 30d EX-BULL + 25d CRISIS).
Find local optimum by grid-searching:
   default_min in {10, 15, 20}
   crisis_min  in {15, 20, 25, 30, 35}
   exbull_min  in {20, 25, 30, 40, 50}

Constraint: keep transitions <= 50 (practical), DD <= -25%, OOS Δ > 0
Evaluate primarily on TC=0.30%, secondary TC=0.50%.

Also check sensitivity to:
  - alloc choices for EX-BULL (1.0, 1.15, 1.30)
  - Adding asym confirm for BULL (e.g., 20d) — does it help?
"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
from itertools import product
from simulate_state_timing import simulate_timing

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

def min_stay_causal_asym(states, default_min, target_state_min):
    out = states.copy()
    committed = states[0]
    pending_state = states[0]
    pending_run = 1
    out[0] = committed
    for t in range(1, len(states)):
        s = states[t]
        if s == pending_state:
            pending_run += 1
        else:
            pending_state = s
            pending_run = 1
        if pending_state in target_state_min:
            need = target_state_min[pending_state]
        else:
            need = default_min
        if pending_run >= need and pending_state != committed:
            committed = pending_state
        out[t] = committed
    return out

tq = pd.read_csv(os.path.join(WORKDIR, "vnindex_5state_tam_quan_v3_4b_full_history.csv"))
tq["time"] = pd.to_datetime(tq["time"])
tq = tq.sort_values("time").reset_index(drop=True)
state_base = tq["state"].values.astype(int)
mask14 = (tq["time"] >= "2014-01-01").values

# Baseline TQ34b
df_tq = pd.DataFrame({"time": tq["time"], "state": state_base})
r_tq_full = simulate_timing(df_tq, start_date="2014-01-01", tc=0.003)
r_tq_is   = simulate_timing(df_tq, start_date="2014-01-01", end_date="2019-12-31", tc=0.003)
r_tq_oos  = simulate_timing(df_tq, start_date="2020-01-01", tc=0.003)
tq_full = r_tq_full["cagr"]
tq_is   = r_tq_is["cagr"]
tq_oos  = r_tq_oos["cagr"]

print("="*88)
print("  GRID SEARCH: optimal asymmetric confirmation (TC=0.30%)")
print("="*88)
print(f"  TQ34b baseline Full {tq_full*100:.2f}%  IS {tq_is*100:.2f}%  OOS {tq_oos*100:.2f}%")
print()

results = []
for d_min, c_min, eb_min in product([10, 15, 20], [15, 20, 25, 30, 35], [20, 25, 30, 40, 50]):
    target = {1: c_min, 5: eb_min}
    s = min_stay_causal_asym(state_base, d_min, target)
    df_v = pd.DataFrame({"time": tq["time"], "state": s})
    r_full = simulate_timing(df_v, start_date="2014-01-01", tc=0.003)
    r_is   = simulate_timing(df_v, start_date="2014-01-01", end_date="2019-12-31", tc=0.003)
    r_oos  = simulate_timing(df_v, start_date="2020-01-01", tc=0.003)
    s14 = s[mask14]
    n_tx = int((s14[1:] != s14[:-1]).sum())
    full_d = (r_full["cagr"] - tq_full) * 100
    is_d   = (r_is["cagr"]   - tq_is)   * 100
    oos_d  = (r_oos["cagr"]  - tq_oos)  * 100
    results.append({
        "d_min": d_min, "c_min": c_min, "eb_min": eb_min, "n_tx": n_tx,
        "cagr_full": r_full["cagr"]*100, "cagr_is": r_is["cagr"]*100, "cagr_oos": r_oos["cagr"]*100,
        "full_d": full_d, "is_d": is_d, "oos_d": oos_d,
        "sh_full": r_full["sharpe"], "dd_full": r_full["max_dd"]*100,
        "sh_oos": r_oos["sharpe"], "dd_oos": r_oos["max_dd"]*100,
    })

dfr = pd.DataFrame(results)

# Top 20 by Full CAGR
print("\n[TOP 20 by Full CAGR Δ vs TQ34b]")
print(f"  {'d':>3} {'c':>3} {'eb':>3} {'#tx':>4} {'Full':>7} {'IS':>7} {'OOS':>7} {'Sh_F':>5} {'DD_F':>6}")
for _, r in dfr.nlargest(20, "full_d").iterrows():
    print(f"  {int(r['d_min']):>3d} {int(r['c_min']):>3d} {int(r['eb_min']):>3d} {int(r['n_tx']):>4d} "
          f"{r['full_d']:>+5.2f}pp {r['is_d']:>+5.2f}pp {r['oos_d']:>+5.2f}pp {r['sh_full']:>5.2f} {r['dd_full']:>+5.1f}%")

# Top 20 by min(IS,OOS) — most robust
dfr["min_period"] = dfr[["is_d","oos_d"]].min(axis=1)
print("\n[TOP 20 by MIN(IS, OOS) — most robust]")
print(f"  {'d':>3} {'c':>3} {'eb':>3} {'#tx':>4} {'Full':>7} {'IS':>7} {'OOS':>7} {'minP':>7} {'Sh_F':>5} {'DD_F':>6}")
for _, r in dfr.nlargest(20, "min_period").iterrows():
    print(f"  {int(r['d_min']):>3d} {int(r['c_min']):>3d} {int(r['eb_min']):>3d} {int(r['n_tx']):>4d} "
          f"{r['full_d']:>+5.2f}pp {r['is_d']:>+5.2f}pp {r['oos_d']:>+5.2f}pp {r['min_period']:>+5.2f}pp "
          f"{r['sh_full']:>5.2f} {r['dd_full']:>+5.1f}%")

# Plateau analysis: how stable is performance over the param space?
print("\n[PLATEAU CHECK]")
top20_min = dfr.nlargest(20, "min_period")
print(f"  Top 20 robust variants:")
print(f"    Full CAGR range: {top20_min['cagr_full'].min():.2f}% .. {top20_min['cagr_full'].max():.2f}%")
print(f"    IS CAGR range:   {top20_min['cagr_is'].min():.2f}% .. {top20_min['cagr_is'].max():.2f}%")
print(f"    OOS CAGR range:  {top20_min['cagr_oos'].min():.2f}% .. {top20_min['cagr_oos'].max():.2f}%")
print(f"    OOS Δ range:     {top20_min['oos_d'].min():+.2f}pp .. {top20_min['oos_d'].max():+.2f}pp")
print(f"  -> If range is tight, finding is a robust plateau; if wide, fragile peak")

# All combos with positive OOS and IS
robust = dfr[(dfr["is_d"] > 0) & (dfr["oos_d"] > 0)].sort_values("min_period", ascending=False)
print(f"\n  Variants with BOTH IS & OOS positive: {len(robust)}/{len(dfr)} ({len(robust)/len(dfr)*100:.0f}%)")

# Final pick recommendation
print("\n"+"="*88)
print("  RECOMMENDED CANDIDATE (balanced)")
print("="*88)
# Pick: highest OOS delta among d_min in [15,20], c_min in [20,30], eb_min in [25,40]
candidates = dfr[(dfr["d_min"].between(15,20)) & (dfr["c_min"].between(20,30)) & (dfr["eb_min"].between(25,40))]
best = candidates.sort_values("oos_d", ascending=False).head(5)
print(best[["d_min","c_min","eb_min","n_tx","cagr_full","cagr_is","cagr_oos","sh_full","dd_full"]].to_string(index=False))

# Year-by-year for top candidate
top_cand = dfr.nlargest(1, "min_period").iloc[0]
d_min = int(top_cand["d_min"]); c_min = int(top_cand["c_min"]); eb_min = int(top_cand["eb_min"])
print(f"\n[YEAR-BY-YEAR for top robust candidate: d={d_min} c={c_min} eb={eb_min}]")
state_pick = min_stay_causal_asym(state_base, d_min, {1: c_min, 5: eb_min})
df_pick = pd.DataFrame({"time": tq["time"], "state": state_pick})
r_pick = simulate_timing(df_pick, start_date="2014-01-01", tc=0.003)
r_tq = simulate_timing(df_tq, start_date="2014-01-01", tc=0.003)
bh = pd.DataFrame({"time": tq["time"], "state": 4})
r_bh = simulate_timing(bh, start_date="2014-01-01", tc=0.003)

nav_pick = r_pick["nav_series"]
nav_tq = r_tq["nav_series"]
nav_bh = r_bh["nav_series"]

print(f"  {'Year':<6} {'TQ34b':>8} {'Pick':>8} {'B&H':>8} {'ΔvsTQ':>9}")
for yr in sorted(nav_tq.index.year.unique()):
    m_p = nav_pick.index.year == yr
    m_t = nav_tq.index.year == yr
    m_b = nav_bh.index.year == yr
    if m_p.sum() < 5: continue
    ret_p = nav_pick[m_p].iloc[-1]/nav_pick[m_p].iloc[0]-1
    ret_t = nav_tq[m_t].iloc[-1]/nav_tq[m_t].iloc[0]-1
    ret_b = nav_bh[m_b].iloc[-1]/nav_bh[m_b].iloc[0]-1
    delta = (ret_p - ret_t) * 100
    print(f"  {yr:<6} {ret_t*100:>+7.1f}% {ret_p*100:>+7.1f}% {ret_b*100:>+7.1f}% {delta:>+7.1f}pp")
