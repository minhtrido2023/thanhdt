# -*- coding: utf-8 -*-
"""Axis 3 deep-dive — entry-day vs post-entry liquidity, and a liquidity-aware sizing proposal.
Job Taylor_20260720_164006.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

OUT = "/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_capitexit"
pan = pd.read_csv(f"{OUT}/panel.csv", parse_dates=["time"])

ent = pan[pan["k"] == 0].groupby(["event", "ticker"])["adv_b"].first().rename("adv_entry")
a20 = pan[pan["k"].between(1, 20)].groupby(["event", "ticker"])["adv_b"].median().rename("adv20")
a60 = pan[pan["k"].between(1, 60)].groupby(["event", "ticker"])["adv_b"].median().rename("adv60")
L = pd.concat([ent, a20, a60], axis=1).reset_index()
L["ratio20"] = L["adv20"] / L["adv_entry"]

print("="*78); print("A. LIQUIDITY AT ENTRY vs AFTER ENTRY (gate only checks entry day)"); print("="*78)
print(f"positions n={len(L)}")
print(f"  adv_entry (gate >=2 tỷ): p10={L['adv_entry'].quantile(.1):.2f} p50={L['adv_entry'].median():.2f}")
print(f"  adv20 post-entry:        p10={L['adv20'].quantile(.1):.2f} p50={L['adv20'].median():.2f}")
print(f"  ratio adv20/adv_entry:   p10={L['ratio20'].quantile(.1):.2f} p50={L['ratio20'].median():.2f}")
dry = L[L["adv20"] < 2]
print(f"\n  positions that FALL BELOW the 2 tỷ gate after entry: {len(dry)}/{len(L)} "
      f"({len(dry)/len(L):.0%})")
print(dry.sort_values("adv20")[["event", "ticker", "adv_entry", "adv20"]].head(10).to_string(index=False))
print("\n  -> the >=2 tỷ liquidity gate is a POINT-IN-TIME entry check only. Washout days are")
print("     volume spikes by construction, so entry-day ADV systematically OVERSTATES the")
print("     liquidity available during the 60-session hold and at exit.")

# ---- B. capacity under equal-weight vs liquidity-aware weighting ---------------------
print("\n" + "="*78); print("B. SLEEVE CAPACITY — equal-weight vs liquidity-aware cap"); print("="*78)
X, DAYS = 0.10, 2.0          # 10% of ADV per day, exit spread over 2 sessions

def cap_equal(g):
    """Equal weight: sleeve limited by the thinnest name."""
    n = len(g)
    return g["adv20"].min() * X * DAYS * n

def cap_liqaware(g, max_mult=3.0):
    """Weight_i proportional to ADV_i but capped at max_mult x equal weight.
    Sleeve capacity = min over names of (name budget_i / weight_i)."""
    n = len(g)
    w = g["adv20"] / g["adv20"].sum()
    w = np.minimum(w, max_mult / n)
    w = w / w.sum()
    budget = g["adv20"].values * X * DAYS
    return float(np.min(budget / w.values))

rows = []
for ev, g in L.groupby("event"):
    rows.append(dict(event=ev, n=len(g), thin=g["adv20"].min(),
                     eq=cap_equal(g), liq=cap_liqaware(g)))
C = pd.DataFrame(rows)
C["gain"] = C["liq"] / C["eq"]
print(f"  {'event':12s} {'n':>3s} {'thin':>7s} {'cap_equal':>10s} {'cap_liqaw':>10s} {'x':>6s}")
for _, r in C.iterrows():
    print(f"  {r['event']:12s} {r['n']:3.0f} {r['thin']:7.2f} {r['eq']:10.1f} {r['liq']:10.1f} {r['gain']:6.1f}x")
print(f"\n  median capacity: equal={C['eq'].median():.1f} tỷ -> liq-aware={C['liq'].median():.1f} tỷ "
      f"({C['gain'].median():.1f}x)")
print(f"  worst event:     equal={C['eq'].min():.1f} tỷ -> liq-aware={C['liq'].min():.1f} tỷ")

# ---- C. what does the CURRENT live sizing actually demand? ---------------------------
print("\n" + "="*78); print("C. SENSITIVITY — required sleeve vs available capacity"); print("="*78)
print("  sleeve = NAV_book_LAG x capit_size ; capit_size in {0.375 grind, 0.75 NEUTRAL full}")
for nav in [0.5, 1.0, 2.0, 5.0, 10.0]:
    for size in [0.375, 0.75]:
        need = nav * size
        ok_eq = int((C["eq"] >= need).sum()); ok_lq = int((C["liq"] >= need).sum())
        print(f"  NAV_LAG={nav:5.1f} tỷ x {size:.3f} = {need:5.2f} tỷ sleeve -> "
              f"events with enough capacity: equal {ok_eq:2d}/14 | liq-aware {ok_lq:2d}/14")
