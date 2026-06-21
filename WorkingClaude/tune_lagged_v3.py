#!/usr/bin/env python3
"""
tune_lagged_v3.py — micro-tune around winner v2_p8_max10
WINNER baseline: post_ret_min=8, max_pos=10, pos_pct=0.10, npr_min=0.15, hold=25, entry=5

Round 3 micro-sweep:
  - post_ret_min: 7, 8, 9
  - max_pos: 9, 10, 11, 12
  - pos_pct: 9%, 10%, 11%, 12%
  - hold_days near 25
  - stack secboost / revreq / npr20
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

# Reuse setup + backtest function from tune_lagged_pos.py
sys.path.insert(0, ".")
exec(open("tune_lagged_pos.py").read().split("# ─── Run experiments ─")[0])

# Round 3 configs — all share post8 + max10 + pos10% baseline
WIN = {"post_ret_min":8, "max_pos":10, "pos_pct":0.10}

configs_v3 = [
    {"name":"v3_BASELINE",      **WIN},  # confirm reproducibility
    # post_ret_min micro
    {"name":"v3_post7_max10",   **{**WIN, "post_ret_min":7}},
    {"name":"v3_post9_max10",   **{**WIN, "post_ret_min":9}},
    {"name":"v3_post6_max10",   **{**WIN, "post_ret_min":6}},
    # max_pos micro
    {"name":"v3_max9",          **{**WIN, "max_pos":9}},
    {"name":"v3_max11",         **{**WIN, "max_pos":11}},
    {"name":"v3_max12",         **{**WIN, "max_pos":12}},
    {"name":"v3_max14",         **{**WIN, "max_pos":14}},
    # pos_pct micro
    {"name":"v3_pos9pct",       **{**WIN, "pos_pct":0.09}},
    {"name":"v3_pos11pct",      **{**WIN, "pos_pct":0.11}},
    {"name":"v3_pos8pct_max12", **{**WIN, "pos_pct":0.08, "max_pos":12}},  # more diverse
    # hold micro
    {"name":"v3_hold23",        **{**WIN, "hold_days":23}},
    {"name":"v3_hold27",        **{**WIN, "hold_days":27}},
    {"name":"v3_hold20",        **{**WIN, "hold_days":20}},
    {"name":"v3_hold30",        **{**WIN, "hold_days":30}},
    # signal strength
    {"name":"v3_max10_npr20",   **{**WIN, "npr_min":0.20}},
    {"name":"v3_max10_npr25",   **{**WIN, "npr_min":0.25}},
    # stacked best
    {"name":"v3_max10_secboost", **{**WIN, "sector_boost":{"SECURITIES":0.13,"REIT_RES":0.13}}},
    {"name":"v3_max10_revreq",   **{**WIN, "rev_req":True}},
    {"name":"v3_max12_secboost", **{**WIN, "max_pos":12, "sector_boost":{"SECURITIES":0.12,"REIT_RES":0.12}}},
    # 2nd-pass dual stack
    {"name":"v3_max10_npr20_revreq", **{**WIN, "npr_min":0.20, "rev_req":True}},
    {"name":"v3_max12_npr20",        **{**WIN, "max_pos":12, "npr_min":0.20}},
]

results_v3 = []
print(f"\nRound 3: {len(configs_v3)} configs ...\n")
for i, cfg in enumerate(configs_v3):
    print(f"[{i+1:>2}/{len(configs_v3)}] {cfg['name']:<28} ...", end="", flush=True)
    try:
        r = backtest(cfg)
        results_v3.append(r)
        print(f" N={r['n_trades']:3d}  WR={r['WR']:.1f}%  CAGR={r['full_CAGR']:+.2f}%  "
              f"Sh={r['full_Sharpe']:.2f}  DD={r['full_DD']:.1f}%  Cal={r['full_Calmar']:.2f}  "
              f"Q126={r['q126_CAGR']:+.1f}%  Y22={r['y22_CAGR']:+.1f}%  NAV={r['final_nav']:.0f}B", flush=True)
    except Exception as e:
        print(f" ERROR: {e}"); continue

df = pd.DataFrame(results_v3)
df.to_csv("data/lagged_pos_tune_v3.csv", index=False)

print("\n" + "="*135)
print("  TOP 10 BY CAGR (R3)")
print("="*135)
print(df.nlargest(10, "full_CAGR").to_string(index=False, float_format="%.2f"))
print("\n" + "="*135)
print("  TOP 10 BY SHARPE (R3)")
print("="*135)
print(df.nlargest(10, "full_Sharpe").to_string(index=False, float_format="%.2f"))
print("\n" + "="*135)
print("  TOP 10 BY CALMAR (R3)")
print("="*135)
print(df.nlargest(10, "full_Calmar").to_string(index=False, float_format="%.2f"))
