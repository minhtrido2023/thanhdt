#!/usr/bin/env python3
"""
tune_lagged_v2.py — second-pass smart combinations
Stack winning single-tweaks from round 1 (post8, npr25, revreq, top100, secboost).
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

# Import shared backtest from tune script
sys.path.insert(0, ".")
exec(open("tune_lagged_pos.py").read().split("# ─── Run experiments ─")[0])

# Now `backtest` function is available. Define COMBO_v2 configs.
configs_v2 = [
    # Pairs
    {"name": "v2_p8_npr25",        "post_ret_min":8, "npr_min":0.25},
    {"name": "v2_p8_revreq",       "post_ret_min":8, "rev_req":True},
    {"name": "v2_npr25_revreq",    "npr_min":0.25, "rev_req":True},
    {"name": "v2_top100_npr25",    "top_n_uni":100, "npr_min":0.25},
    {"name": "v2_top100_revreq",   "top_n_uni":100, "rev_req":True},
    {"name": "v2_p8_secboost",     "post_ret_min":8, "sector_boost":{"SECURITIES":0.13,"REIT_RES":0.13}},
    {"name": "v2_p8_npr20",        "post_ret_min":8, "npr_min":0.20},  # slightly looser
    {"name": "v2_top100_npr20",    "top_n_uni":100, "npr_min":0.20},
    # Triples
    {"name": "v2_p8_npr25_revreq",     "post_ret_min":8, "npr_min":0.25, "rev_req":True},
    {"name": "v2_top100_npr25_revreq", "top_n_uni":100, "npr_min":0.25, "rev_req":True},
    # Position sizing tweaks on top winner
    {"name": "v2_p8_12pct",        "post_ret_min":8, "pos_pct":0.12},
    {"name": "v2_p8_15pct",        "post_ret_min":8, "pos_pct":0.15},
    # Maxpos tweaks
    {"name": "v2_p8_max6",         "post_ret_min":8, "max_pos":6},
    {"name": "v2_p8_max10",        "post_ret_min":8, "max_pos":10},
    {"name": "v2_top100_max6_15pct","top_n_uni":100, "max_pos":6, "pos_pct":0.15},
]

results_v2 = []
print(f"\nCOMBO v2: {len(configs_v2)} configs ...\n")
for i, cfg in enumerate(configs_v2):
    print(f"[{i+1:>2}/{len(configs_v2)}] {cfg['name']:<24} ...", end="", flush=True)
    try:
        r = backtest(cfg)
        results_v2.append(r)
        print(f" N={r['n_trades']:3d}  WR={r['WR']:.1f}%  avg={r['avg_ret']:+.2f}%  "
              f"CAGR={r['full_CAGR']:+.2f}%  Sh={r['full_Sharpe']:.2f}  "
              f"DD={r['full_DD']:.1f}%  Cal={r['full_Calmar']:.2f}  Q126={r['q126_CAGR']:+.1f}%  Y22={r['y22_CAGR']:+.1f}%", flush=True)
    except Exception as e:
        print(f" ERROR: {e}"); continue

df = pd.DataFrame(results_v2)
df.to_csv("data/lagged_pos_tune_v2.csv", index=False)

# Add round-1 winners for comparison
round1 = pd.DataFrame([
    {"name":"R1_BASE",        "n_trades":455,"WR":63.96,"avg_ret":8.48,"full_CAGR":16.62,"full_Sharpe":1.43,"full_DD":-16.66,"full_Calmar":1.00,"oos_CAGR":12.37,"oos_Sharpe":1.17,"y22_CAGR":9.02,"q126_CAGR":-6.15,"final_nav":383.39},
    {"name":"R1_post8",       "n_trades":337,"WR":68.25,"avg_ret":12.34,"full_CAGR":17.85,"full_Sharpe":1.86,"full_DD":-12.69,"full_Calmar":1.41,"oos_CAGR":14.24,"oos_Sharpe":1.37,"y22_CAGR":14.78,"q126_CAGR":10.50,"final_nav":431.97},
    {"name":"R1_npr25",       "n_trades":454,"WR":65.20,"avg_ret":8.83,"full_CAGR":17.67,"full_Sharpe":1.59,"full_DD":-10.53,"full_Calmar":1.68,"oos_CAGR":12.46,"oos_Sharpe":1.18,"y22_CAGR":12.60,"q126_CAGR":-7.87,"final_nav":427.50},
    {"name":"R1_revreq",      "n_trades":412,"WR":65.29,"avg_ret":9.26,"full_CAGR":17.98,"full_Sharpe":1.64,"full_DD":-13.58,"full_Calmar":1.32,"oos_CAGR":12.03,"oos_Sharpe":1.12,"y22_CAGR":12.06,"q126_CAGR":-11.12,"final_nav":420.18},
    {"name":"R1_top100",      "n_trades":243,"WR":70.37,"avg_ret":14.23,"full_CAGR":16.00,"full_Sharpe":1.87,"full_DD":-11.42,"full_Calmar":1.40,"oos_CAGR":11.93,"oos_Sharpe":1.20,"y22_CAGR":14.52,"q126_CAGR":21.29,"final_nav":348.06},
])
combined = pd.concat([round1, df], ignore_index=True)
combined.to_csv("data/lagged_pos_tune_combined.csv", index=False)

print("\n" + "="*130)
print("  TOP 10 BY CAGR (R1 winners + v2)")
print("="*130)
print(combined.nlargest(10, "full_CAGR").to_string(index=False, float_format="%.2f"))

print("\n" + "="*130)
print("  TOP 10 BY SHARPE")
print("="*130)
print(combined.nlargest(10, "full_Sharpe").to_string(index=False, float_format="%.2f"))

print("\n" + "="*130)
print("  TOP 10 BY CALMAR")
print("="*130)
print(combined.nlargest(10, "full_Calmar").to_string(index=False, float_format="%.2f"))
