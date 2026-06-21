# -*- coding: utf-8 -*-
"""custom30b_stage1.py — Stage-1 (kill-early) for the BULL sleeve (custom30B).
Builds a top-30 gated basket under several selectors, then measures each basket's realized
performance RESTRICTED TO BULL/EX-BULL days (state 4/5, the only regime it would deploy in),
full + IS/OOS (signature test). The blend uplift into production scales with whichever basket
wins in bull, so this head-to-head is the decisive cheap test before touching the harness.

Selectors (all: gate_rating<=3, top_n=30, q2m5 rebal, namecap<=10%):
  custom30V (1/PE+1/PCF)  -- the parking basket we already deploy in NEUTRAL (control)
  custom30B petop (1/PE)  -- bull IC champion (+0.161), absolute liq floor 10B/day
  custom30B pemom .5      -- rank(1/PE)+0.5*rank(mom200), liq floor 10B/day
  custom30B pemom 1.0     -- heavier momentum tilt
Also reports capwt variants of the two best to see if "deploy all the money" cap-weight differs.
"""
import sys, os
import numpy as np, pandas as pd
os.chdir(r"/home/trido/thanhdt/WorkingClaude")
from simulate_holistic_nav import bq
import custom_basket

END = os.environ.get("AUDIT_END", "2026-06-19")
START = "2014-01-01"

# DT5G production state (2014+)
st = bq(f"SELECT time, state FROM tav2_bq.vnindex_5state_dt5g_live WHERE time>='{START}' AND time<='{END}'")
st["time"] = pd.to_datetime(st["time"]); state = st.set_index("time")["state"]
state = state[~state.index.duplicated(keep="last")].sort_index()
bull_days = state[state.isin([4, 5])].index   # BULL + EXBULL

def basket_series(env, weight="namecap"):
    for k, v in env.items(): os.environ[k] = str(v)
    lvl, adv, mem, raw = custom_basket.build_pit(bq, START, END, top_n=30, gate_rating=3,
                                                 rebal="q2m5", weight_scheme=weight)
    for k in env: os.environ.pop(k, None)
    s = pd.Series(lvl); s.index = pd.to_datetime(s.index); s = s.sort_index()
    return s

def met(r):
    r = r.dropna()
    if len(r) < 20: return None
    nav = (1 + r).cumprod(); yrs = (r.index[-1] - r.index[0]).days / 365.25
    cg = nav.iloc[-1] ** (1 / yrs) - 1 if yrs > 0 else 0
    dd = (nav / nav.cummax() - 1).min()
    return dict(cagr=cg * 100, sh=r.mean() / r.std() * np.sqrt(252) if r.std() > 0 else 0,
                dd=dd * 100, cal=cg / abs(dd) if dd < 0 else 0, n=len(r))

def bull_only(s):
    """daily returns of the basket, kept ONLY on bull/exbull days (the deploy regime)."""
    r = s.pct_change()
    return r[r.index.isin(bull_days)]

def win(r, lo, hi): return r[(r.index >= lo) & (r.index <= hi)]

def report(lbl, s):
    rb = bull_only(s)
    f = met(rb); i = met(win(rb, "2014-01-01", "2019-12-31")); o = met(win(rb, "2020-01-01", "2026-12-31"))
    fa = met(s.pct_change())  # all-day reference
    if not f:
        print(f"  {lbl:28s} n/a"); return
    sig = "PASS" if (i and o and i["cagr"] > 0 and o["cagr"] > 0) else "fail"
    print(f"  {lbl:28s} BULL-days FULL {f['cagr']:6.1f}%/Sh{f['sh']:.2f}/DD{f['dd']:6.1f}/Cal{f['cal']:.2f} "
          f"(n{f['n']:4d}) | IS {i['cagr'] if i else float('nan'):6.1f}% OOS {o['cagr'] if o else float('nan'):6.1f}% [{sig}]"
          f" | all-day {fa['cagr']:5.1f}%")

print(f"window {START} -> {END}  | bull/exbull days = {len(bull_days)}\n")
print("=== custom30B selector head-to-head (basket return on BULL/EXBULL days only) ===")
report("custom30V 1/PE+1/PCF (ctrl)", basket_series({"BASKET_SELECT": "yieldcombo"}))
report("custom30B 1/PE (petop)",      basket_series({"BASKET_SELECT": "petop",  "BASKET_LIQ_FLOOR_B": 10}))
report("custom30B 1/PE+0.5mom",       basket_series({"BASKET_SELECT": "pemom",  "BASKET_LIQ_FLOOR_B": 10, "BASKET_MOM_W": 0.5}))
report("custom30B 1/PE+1.0mom",       basket_series({"BASKET_SELECT": "pemom",  "BASKET_LIQ_FLOOR_B": 10, "BASKET_MOM_W": 1.0}))
print("\n=== cap-weight variants (deploy-all-money, mega lean) ===")
report("custom30B 1/PE capwt",        basket_series({"BASKET_SELECT": "petop",  "BASKET_LIQ_FLOOR_B": 10}, weight="capwt"))
report("custom30B 1/PE+0.5mom capwt", basket_series({"BASKET_SELECT": "pemom",  "BASKET_LIQ_FLOOR_B": 10, "BASKET_MOM_W": 0.5}, weight="capwt"))
print("\nREAD: higher BULL-days CAGR/Sharpe = better bull deployment vehicle. PASS = IS>0 AND OOS>0 (not regime-luck).")
print("Compare custom30B vs custom30V(ctrl): does a 1/PE-led / momentum-tilted basket beat the value-yield parking IN BULL?")
