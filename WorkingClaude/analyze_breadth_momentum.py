# -*- coding: utf-8 -*-
"""
P1 follow-up: breadth MOMENTUM (direction of bleed) vs breadth LEVEL.

Hypothesis from the level-matrix result: the 2025-08 grind damage happens while
breadth drains STRONG->WEAK, so the informative axis is the CHANGE in breadth,
not its level. Also test the speed discriminator: fast washout (capitulation,
2025-04) vs slow bleed (2022-08, 2025H2 grind).
"""
import pandas as pd
import numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

df = pd.read_csv(f"{WORKDIR}/data/breadth_compass_panel.csv", parse_dates=["time"])

# breadth momentum: 40-session change of smoothed breadth (causal)
df["b_mom40"] = df["breadth_s"] - df["breadth_s"].shift(40)
df["b_mom10"] = df["breadth_s"] - df["breadth_s"].shift(10)

def mom_bucket(x):
    if np.isnan(x): return np.nan
    if x < -0.10: return "BLEED"      # lost >10pp of breadth in ~2 months
    if x > 0.10: return "HEAL"
    return "FLAT"
df["m_state"] = df["b_mom40"].apply(mom_bucket)

def fmt(x): return "   na" if pd.isna(x) else f"{100*x:+5.1f}"

print("=== EW basket fwd60 — median, by (DT5G state x breadth MOMENTUM 40d) ===")
print(f"{'state':<9}" + "".join(f"{b:>16}" for b in ["BLEED", "FLAT", "HEAL"]))
for s in [1, 2, 3, 4, 5]:
    row = f"{STATE_NAMES[s]:<9}"
    for b in ["BLEED", "FLAT", "HEAL"]:
        g = df[(df.state == s) & (df.m_state == b)]["ew_f60"].dropna()
        row += f"{fmt(g.median()):>9} n={len(g):<5}" if len(g) else f"{'—':>9}      "
    print(row)

print("\n=== same, win% ===")
for s in [1, 2, 3, 4, 5]:
    row = f"{STATE_NAMES[s]:<9}"
    for b in ["BLEED", "FLAT", "HEAL"]:
        g = df[(df.state == s) & (df.m_state == b)]["ew_f60"].dropna()
        row += f"{100*(g>0).mean():>9.0f}% n={len(g):<4}" if len(g) else f"{'—':>10}     "
    print(row)

# 2x2: level x momentum within benign index states (NEUTRAL/BULL/EX-BULL)
ben = df[df.state >= 3].copy()
print("\n=== Within DT5G NEUTRAL/BULL/EX-BULL: level x momentum, EW fwd60 median (win%) [n] ===")
print(f"{'':<10}" + "".join(f"{m:>22}" for m in ["BLEED", "FLAT", "HEAL"]))
for lv in ["WEAK", "MID", "STRONG"]:
    row = f"{lv:<10}"
    for m in ["BLEED", "FLAT", "HEAL"]:
        g = ben[(ben.b_state == lv) & (ben.m_state == m)]["ew_f60"].dropna()
        row += (f"{fmt(g.median())} ({100*(g>0).mean():3.0f}%) [{len(g):>4}]" if len(g) >= 15
                else f"{'·':>21} ")
    print(row)

# speed discriminator inside WEAK level: how fast did we get here? (10d momentum)
wk = df[(df.state >= 3) & (df.b_state == "WEAK")].copy()
fast = wk[wk.b_mom10 < -0.06]   # crashing fast = washout
slow = wk[wk.b_mom10 >= -0.06]  # slow bleed / stabilizing
print("\n=== Inside (index>=NEUTRAL & breadth WEAK): fast washout vs slow bleed, EW fwd60 ===")
for name, g0 in [("fast washout (b_mom10<-6pp)", fast), ("slow bleed/flat", slow)]:
    g = g0["ew_f60"].dropna()
    if len(g):
        print(f"  {name:<30} median {fmt(g.median())}%  win {100*(g>0).mean():.0f}%  n={len(g)}")

# timeline check: what did momentum say during the 2025-08+ grind?
w = df[df.time >= "2025-07-01"][["time", "state", "breadth_s", "b_state", "b_mom40", "m_state"]]
w = w.set_index("time").resample("MS").first()
print("\n=== Monthly snapshot since 2025-07 (first session of month) ===")
print(f"{'month':<10}{'DT5G':<9}{'breadth':>8}{'level':>8}{'mom40':>8}{'mom':>7}")
for t, r in w.iterrows():
    if pd.isna(r.state): continue
    print(f"{t.strftime('%Y-%m'):<10}{STATE_NAMES[int(r.state)]:<9}{r.breadth_s:>7.1%}{str(r.b_state):>8}"
          f"{r.b_mom40:>+7.1%}{str(r.m_state):>7}")

# same monthly trace for the 2022 disaster for comparison
w2 = df[(df.time >= "2022-06-01") & (df.time <= "2022-12-31")][["time", "state", "breadth_s", "b_state", "b_mom40", "m_state"]]
w2 = w2.set_index("time").resample("MS").first()
print("\n=== Monthly snapshot 2022-06..12 (the grind->crash) ===")
for t, r in w2.iterrows():
    if pd.isna(r.state): continue
    print(f"{t.strftime('%Y-%m'):<10}{STATE_NAMES[int(r.state)]:<9}{r.breadth_s:>7.1%}{str(r.b_state):>8}"
          f"{r.b_mom40:>+7.1%}{str(r.m_state):>7}")
