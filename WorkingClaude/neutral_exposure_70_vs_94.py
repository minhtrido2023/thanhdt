# -*- coding: utf-8 -*-
"""
neutral_exposure_70_vs_94.py — RIGOR study for dispatch Taylor_20260703_113818.

QUESTION: SpaceX go-live sits at ~94% invested in custom30V at NEUTRAL with 0 active BAL/LAG
picks. The V2.4 engine rule (ETF_PARK={3:0.7}) parks 70% of IDLE cash → with 0 deals, idle=100%
→ engine target = 70% invested / 30% cash. DollarBill's 94% ("custom30V_parking_full_deploy") is
~24pp above the engine-approved level and was never backtested. Is 94 justified vs 70?

METHOD (auditable, no look-ahead used as a live FILTER — this is a forward-OUTCOME study):
 1. Reconstruct the custom30V (yieldcombo) PIT basket daily gross return `rb` via custom_basket.build_pit
    (gate_rating=3, namecap 0.10, q2m5) — the exact production parking vehicle.
 2. DT5G state from tav2_bq.vnindex_5state_dt5g_live.
 3. Cash yield = 0 (engine deposit default). Static exposure e: daily port ret = e*rb (rest cash).
 A. NEUTRAL-day aggregate: ann.return / Sharpe / MaxDD / Calmar at e=0.70 vs e=0.94, FULL/IS/OOS.
 B. Forward-window path from every NEUTRAL day: 3M(63)/6M(126)/1Y(252) cum ret + within-window MaxDD
    at 70 vs 94. Delta = pure exposure-scaling cost/benefit.
 C. Regime reversal: from NEUTRAL days, P(state hits BEAR/CRISIS within 20/40/60 sessions), and the
    realized worst forward DD in reversal episodes — STATIC hold (worst case) vs DT5G-GATED (realistic,
    the gate cuts exposure on the flip so 70/94 converge).
"""
import os, sys, numpy as np, pandas as pd
WORKDIR = os.environ.get("WORKDIR_8L", "/home/trido/thanhdt/WorkingClaude"); sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from simulate_holistic_nav import bq
import custom_basket as cb

E_ENGINE = 0.70          # engine ETF_PARK target with 0 active deals (70% of idle cash)
E_GOLIVE = 0.94          # DollarBill go-live full-deploy
W_STATE = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}   # DT5G production allocation (for gated reversal)
SN = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
SPY = 250.0              # sessions/yr for annualization

# ── 1. custom30V basket gross daily return ──
os.environ["BASKET_SELECT"] = "yieldcombo"
lvl, _, memdf, _ = cb.build_pit(bq, "2014-01-01", "2026-06-19", quality="none",
                                rebal="q2m5", gate_rating=3, weight_scheme="namecap")
s = pd.Series(lvl).sort_index(); s.index = pd.to_datetime(s.index)
rb = s.pct_change().dropna()
idx = rb.index

# ── 2. DT5G state, causal (T-1 state governs today) ──
st = bq("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live s ORDER BY s.time")
st["time"] = pd.to_datetime(st["time"])
SD = pd.Series(st["state"].values, index=st["time"]).reindex(idx).ffill()
state = SD.astype("Int64")
state_lag = state.shift(1)          # yesterday's committed state = today's exposure regime

def block_metrics(r):
    """annualized return, Sharpe, MaxDD, Calmar on a (possibly gappy) daily-return series."""
    r = r.dropna()
    if len(r) < 5: return (np.nan, np.nan, np.nan, np.nan)
    cum = (1 + r).cumprod()
    ann = r.mean() * SPY * 100
    sh = r.mean() / r.std() * np.sqrt(SPY) if r.std() > 0 else 0
    dd = (cum / cum.cummax() - 1).min() * 100
    cal = ann / abs(dd) if dd < 0 else np.nan
    return ann, sh, dd, cal

# =====================================================================
# PART A — NEUTRAL-day aggregate stats at 70 vs 94
# =====================================================================
neu = (state_lag == 3)              # days where yesterday's state = NEUTRAL → parked today
rb_neu = rb[neu]
WINS = [("FULL 2014→now", None, None),
        ("IS   2014-19", None, pd.Timestamp("2019-12-31")),
        ("OOS  2020→now", pd.Timestamp("2020-01-01"), None)]
print("=" * 92)
print("PART A — custom30V held ONLY on NEUTRAL days; static exposure 70% vs 94% (cash@0%)")
print(f"  NEUTRAL sessions in sample: {int(neu.sum())} / {len(rb)}  ({neu.mean()*100:.1f}%)")
print("=" * 92)
print(f"  {'window':<14}{'exp':>5}{'annRet%':>9}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}")
rowsA = []
for tag, a, b in WINS:
    seg = rb_neu.copy()
    if a is not None: seg = seg[seg.index >= a]
    if b is not None: seg = seg[seg.index <= b]
    for e in (E_ENGINE, E_GOLIVE):
        annr, sh, dd, cal = block_metrics(e * seg)
        print(f"  {tag:<14}{int(e*100):>4}%{annr:>9.2f}{sh:>8.2f}{dd:>9.1f}{cal:>8.2f}")
        rowsA.append({"part": "A", "window": tag, "exposure": e, "annRet": annr,
                      "sharpe": sh, "maxDD": dd, "calmar": cal, "n_days": len(seg)})
    print("  " + "-" * 46)

# =====================================================================
# PART B — forward-window path from EVERY NEUTRAL day (static hold)
# =====================================================================
def fwd_path_stats(start_pos, horizon, e):
    """static exposure e held for `horizon` sessions from start_pos; cum ret & within-window MaxDD."""
    seg = rb.iloc[start_pos + 1: start_pos + 1 + horizon]
    if len(seg) < horizon * 0.6: return (np.nan, np.nan)
    path = (1 + e * seg).cumprod()
    cum = path.iloc[-1] - 1
    dd = (path / path.cummax() - 1).min()
    return cum * 100, dd * 100

neu_pos = [i for i in range(len(idx) - 5)
           if pd.notna(state_lag.iloc[i]) and int(state_lag.iloc[i]) == 3]
print("\n" + "=" * 92)
print("PART B — forward-window outcome from EVERY NEUTRAL day (static hold, no gate) — MEDIANS")
print("=" * 92)
print(f"  {'horizon':<10}{'n':>6}{'  med cumRet% 70 / 94':>24}{'  med withinDD% 70 / 94':>26}{'  Δret/ΔDD':>14}")
rowsB = []
for hname, H in [("3M(63)", 63), ("6M(126)", 126), ("1Y(252)", 252)]:
    r70 = [fwd_path_stats(p, H, E_ENGINE) for p in neu_pos]
    r94 = [fwd_path_stats(p, H, E_GOLIVE) for p in neu_pos]
    c70 = np.array([x[0] for x in r70]); d70 = np.array([x[1] for x in r70])
    c94 = np.array([x[0] for x in r94]); d94 = np.array([x[1] for x in r94])
    m = ~np.isnan(c70)
    mc70, mc94 = np.nanmedian(c70), np.nanmedian(c94)
    md70, md94 = np.nanmedian(d70), np.nanmedian(d94)
    p05_70, p05_94 = np.nanpercentile(c70, 5), np.nanpercentile(c94, 5)   # 5th-pct forward ret (tail)
    ddp5_70, ddp5_94 = np.nanpercentile(d70, 5), np.nanpercentile(d94, 5) # 5th-pct within-window DD
    print(f"  {hname:<10}{m.sum():>6}   {mc70:>7.1f} / {mc94:>6.1f}        {md70:>7.1f} / {md94:>6.1f}"
          f"      {mc94-mc70:>+5.1f}/{md94-md70:>+5.1f}")
    rowsB.append({"part": "B", "horizon": hname, "n": int(m.sum()),
                  "medRet70": mc70, "medRet94": mc94, "medDD70": md70, "medDD94": md94,
                  "p05Ret70": p05_70, "p05Ret94": p05_94, "p05DD70": ddp5_70, "p05DD94": ddp5_94})
print("  tail (5th-pct of forward outcomes across the same NEUTRAL starts):")
for row in rowsB:
    print(f"    {row['horizon']:<10} 5pct cumRet 70/94 = {row['p05Ret70']:>6.1f}/{row['p05Ret94']:>6.1f}%"
          f"   5pct withinDD 70/94 = {row['p05DD70']:>6.1f}/{row['p05DD94']:>6.1f}%")

# =====================================================================
# PART C — regime reversal from NEUTRAL
# =====================================================================
sarr = state.values.astype(float)
print("\n" + "=" * 92)
print("PART C — reversal risk from NEUTRAL days: P(hit BEAR/CRISIS within N sessions)")
print("=" * 92)
n_neu = len(neu_pos)
rowsC = []
for H in (20, 40, 60):
    hits = 0
    for p in neu_pos:
        window = sarr[p + 1: p + 1 + H]
        if len(window) and np.any((window == 1) | (window == 2)):
            hits += 1
    frac = hits / n_neu * 100
    print(f"  within {H:>2} sessions: {hits}/{n_neu} = {frac:.1f}% of NEUTRAL days precede a BEAR/CRISIS touch")
    rowsC.append({"part": "C", "horizon_sessions": H, "hit_frac_pct": frac, "n_neu": n_neu})

# reversal-subset forward DD: STATIC hold (worst case) vs DT5G-GATED (realistic)
print("\n  Reversal episodes (NEUTRAL day that DOES hit BEAR/CRISIS within 60 sess):")
w_lag_state = state_lag.map(lambda x: W_STATE.get(int(x), 0.7) if pd.notna(x) else 0.7)
rev_static70, rev_static94, rev_gated70, rev_gated94 = [], [], [], []
H = 60
for p in neu_pos:
    window = sarr[p + 1: p + 1 + H]
    if not (len(window) and np.any((window == 1) | (window == 2))):
        continue
    seg = rb.iloc[p + 1: p + 1 + H]
    if len(seg) < 20: continue
    # static: freeze exposure at e through the reversal (no gate) — upper bound on extra risk
    for e, bucket in ((E_ENGINE, rev_static70), (E_GOLIVE, rev_static94)):
        path = (1 + e * seg).cumprod()
        bucket.append((path / path.cummax() - 1).min() * 100)
    # gated: start at e0 today, then exposure follows DT5G W_STATE (lagged) — gate cuts on flip
    wg = w_lag_state.iloc[p + 1: p + 1 + H].values
    for e0, bucket in ((E_ENGINE, rev_gated70), (E_GOLIVE, rev_gated94)):
        w = wg.copy(); w[0] = e0                      # day-1 still at parked level, then gate governs
        path = np.cumprod(1 + w * seg.values)
        path = pd.Series(path)
        bucket.append((path / path.cummax() - 1).min() * 100)
def med(x): return float(np.nanmedian(x)) if x else float("nan")
def p05(x): return float(np.nanpercentile(x, 5)) if x else float("nan")
print(f"    n reversal episodes = {len(rev_static70)}")
print(f"    STATIC hold  worst-DD median  70={med(rev_static70):.1f}%  94={med(rev_static94):.1f}%  "
      f"Δ={med(rev_static94)-med(rev_static70):+.1f}pp")
print(f"    STATIC hold  worst-DD 5th-pct 70={p05(rev_static70):.1f}%  94={p05(rev_static94):.1f}%  "
      f"Δ={p05(rev_static94)-p05(rev_static70):+.1f}pp")
print(f"    DT5G-GATED   worst-DD median  70={med(rev_gated70):.1f}%  94={med(rev_gated94):.1f}%  "
      f"Δ={med(rev_gated94)-med(rev_gated70):+.1f}pp  (gate converges 70/94 after flip)")
print(f"    DT5G-GATED   worst-DD 5th-pct 70={p05(rev_gated70):.1f}%  94={p05(rev_gated94):.1f}%  "
      f"Δ={p05(rev_gated94)-p05(rev_gated70):+.1f}pp")
rowsC.append({"part": "C-reversal", "n_episodes": len(rev_static70),
              "static_medDD70": med(rev_static70), "static_medDD94": med(rev_static94),
              "static_p05DD70": p05(rev_static70), "static_p05DD94": p05(rev_static94),
              "gated_medDD70": med(rev_gated70), "gated_medDD94": med(rev_gated94),
              "gated_p05DD70": p05(rev_gated70), "gated_p05DD94": p05(rev_gated94)})

# ── dump audit CSV ──
out = pd.DataFrame(rowsA + rowsB + rowsC)
outp = os.path.join(WORKDIR, "data", "neutral_exposure_70_vs_94.csv")
out.to_csv(outp, index=False)
print(f"\n  [audit CSV] {outp}")
print("  DONE.")
