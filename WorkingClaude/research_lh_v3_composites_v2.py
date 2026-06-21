#!/usr/bin/env python3
"""
research_lh_v3_composites_v2.py
================================
Iterate composite designs based on phase 1 IC findings:
  - Momentum is NEGATIVE (-0.17 IC) → use REVERSE momentum (oversold buy)
  - smoothed_EY top value factor (+0.16)
  - Cash_MktCap surprising winner (+0.16)
  - Quality moderate (ROE_min5Y +0.09)
  - Growth bad (-0.04 to -0.07)

New composites:
  C6_smart_value: heavy smoothed_EY + Cash_MktCap + reverse_12m_mom
  C7_value_quality_cash: balanced value + quality + cash defense
  C8_ultra_value: max value tilt + reverse mom
  C9_v8c_plus: v8c_final + Cash_MktCap + reverse mom overlay
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

df = pd.read_csv("lh_v3_factor_panel.csv", parse_dates=["time"])
print(f"Loaded panel: {len(df):,} rows")

# Add reverse momentum (mean reversion signal)
df["F_rev_12_1"] = -df["F_ret_12_1"]      # invert: high = oversold (good)
df["F_rev_12m"]  = -df["F_ret_12m"]
df["F_rev_3m"]   = -df["F_ret_3m"]
df["F_far_52w"]  = 1 - df["F_dist_52w_high"]  # how far below 52w high (cheap)

COMPOSITES_V2 = {
    # C6: smart value (smoothed_EY + Cash + reverse mom)
    "C6_smart_value": {
        "F_smoothed_EY": 0.20, "F_EVEB_inv": 0.10, "F_BY": 0.10, "F_FCF_yield": 0.05,  # value 45%
        "F_Cash_MktCap": 0.15,  # cash defense 15%
        "F_rev_12_1": 0.10, "F_far_52w": 0.05,  # reverse momentum 15%
        "F_ROE_min5Y": 0.10, "F_NP_stability": 0.05,  # quality 15%
        "F_NetDebt_EBITDA_inv": 0.05, "F_DY_sust": 0.05,  # health/shareholder 10%
    },
    # C7: balanced value + quality + cash
    "C7_balanced_VQC": {
        "F_smoothed_EY": 0.15, "F_BY": 0.10, "F_EY": 0.05, "F_EVEB_inv": 0.05,  # value 35%
        "F_Cash_MktCap": 0.15, "F_NetDebt_EBITDA_inv": 0.10,  # health 25%
        "F_ROE_min5Y": 0.10, "F_ROIC5Y": 0.05, "F_NP_stability": 0.05, "F_CFOA_NP_4Q": 0.05,  # quality 25%
        "F_rev_12_1": 0.10, "F_Div_Min3Y": 0.05,  # other 15%
    },
    # C8: ultra value (max value tilt)
    "C8_ultra_value": {
        "F_smoothed_EY": 0.20, "F_BY": 0.15, "F_EY": 0.10, "F_EVEB_inv": 0.10, "F_CFY": 0.05,  # value 60%
        "F_Cash_MktCap": 0.10, "F_NetDebt_EBITDA_inv": 0.05,  # health 15%
        "F_ROE_min5Y": 0.10,  # quality 10%
        "F_rev_12_1": 0.10, "F_far_52w": 0.05,  # reverse mom 15%
    },
    # C9: v8c-style with explicit reverse momentum overlay
    "C9_value_mom_blend": {
        "F_smoothed_EY": 0.15, "F_FCF_yield": 0.10, "F_BY": 0.10,  # value 35%
        "F_Cash_MktCap": 0.15,  # cash 15%
        "F_rev_12_1": 0.10, "F_rev_3m": 0.05,  # reverse mom 15%
        "F_ROE_min5Y": 0.10, "F_NP_stability": 0.05, "F_CFOA_NP_4Q": 0.05,  # quality 20%
        "F_Backlog_yld": 0.05, "F_NetDebt_EBITDA_inv": 0.10,  # VN specific + health 15%
    },
    # C10: contrarian (heavy reverse momentum)
    "C10_contrarian": {
        "F_rev_12_1": 0.20, "F_rev_12m": 0.10, "F_far_52w": 0.10,  # reverse mom 40%
        "F_smoothed_EY": 0.15, "F_BY": 0.10,  # value 25%
        "F_Cash_MktCap": 0.10,  # cash 10%
        "F_ROE_min5Y": 0.10, "F_NP_stability": 0.05,  # quality 15%
        "F_NetDebt_EBITDA_inv": 0.10,  # health 10%
    },
}

# Compute composites
def rank_pct(df, factor): return df.groupby("quarter")[factor].rank(pct=True, na_option="keep")

for name, w_dict in COMPOSITES_V2.items():
    total_w = sum(w_dict.values())
    assert abs(total_w - 1.0) < 0.001, f"{name} weights {total_w}"
    parts = []
    for f, w in w_dict.items():
        if f not in df.columns:
            print(f"WARN: {f} missing for {name}"); continue
        parts.append(rank_pct(df, f) * w)
    df[name] = sum(parts) / sum(w_dict.values())

# Also recompute baseline v8c
fa = pd.read_csv("fa_ratings_lh.csv", usecols=["ticker","quarter","score"]).rename(columns={"score":"v8c_score"})
df = df.merge(fa, on=["ticker","quarter"], how="left")

# IC analysis
def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 100: return np.nan, 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

print("\n" + "="*120)
print(f"  COMPOSITE IC + TOP DECILE FORWARD RETURN")
print("="*120)
print(f"\n  {'Composite':<25}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}{'top10_1Y':>12}{'spread':>10}{'WR':>8}{'big_loss%':>11}")

candidates = list(COMPOSITES_V2.keys()) + ["v8c_score"]
for name in candidates:
    if name not in df.columns: continue
    ic_3m, _ = spearman_ic(df[name], df["O3M_ret"])
    ic_6m, _ = spearman_ic(df[name], df["O6M_ret"])
    ic_1y, _ = spearman_ic(df[name], df["O1Y_ret"])
    ic_2y, _ = spearman_ic(df[name], df["O2Y_ret"])
    df_v = df.dropna(subset=[name, "O1Y_ret"])
    df_v["decile"] = df_v.groupby("quarter")[name].rank(pct=True)
    top10 = df_v[df_v["decile"] >= 0.90]
    top_med = top10["O1Y_ret"].median()
    full_med = df_v["O1Y_ret"].median()
    spread = top_med - full_med
    wr = (top10["O1Y_ret"] > 0).mean() * 100
    big_loss = (top10["O1Y_ret"] < -20).mean() * 100
    label = name if name != "v8c_score" else "v8c (baseline)"
    print(f"  {label:<25}{ic_3m:>+8.4f}{ic_6m:>+8.4f}{ic_1y:>+8.4f}{ic_2y:>+8.4f}{top_med:>+11.2f}%{spread:>+9.2f}pp{wr:>7.1f}%{big_loss:>10.1f}%")

# Multi-horizon decile breakdown for best composite
print("\n" + "="*120)
print("  DECILE BREAKDOWN — top vs bottom (best composites)")
print("="*120)

for name in ["C8_ultra_value", "C10_contrarian", "C6_smart_value", "v8c_score"]:
    if name not in df.columns: continue
    print(f"\n  --- {name} ---")
    df_v = df.dropna(subset=[name, "O1Y_ret"]).copy()
    df_v["decile_label"] = pd.qcut(df_v.groupby("quarter")[name].rank(pct=True), 10, labels=range(1,11))
    for d in [10, 9, 5, 2, 1]:
        sub = df_v[df_v["decile_label"]==d]
        if len(sub) < 30: continue
        print(f"    D{d:>2}: N={len(sub):4d}  O1Y_med={sub['O1Y_ret'].median():>+6.2f}%  mean={sub['O1Y_ret'].mean():>+6.2f}%  WR={((sub['O1Y_ret']>0).mean()*100):>4.1f}%  big_loss%={((sub['O1Y_ret']<-20).mean()*100):>4.1f}%")

# 5-ticker performance under each composite
print("\n" + "="*120)
print("  5-CASE TICKER scores under best composites (at peak quarter)")
print("="*120)

CASES = {"VCS":"2021Q3", "DGC":"2024Q1", "VNM":"2017Q3", "FPT":"2024Q4", "MWG":"2025Q4"}
for name in ["C8_ultra_value", "C10_contrarian", "C6_smart_value", "v8c_score"]:
    if name not in df.columns: continue
    print(f"\n  {name}:")
    for tk, q in CASES.items():
        sub = df[(df["ticker"]==tk) & (df["quarter"]==q)]
        if len(sub) == 0:
            print(f"    {tk} {q}: no data")
            continue
        score = sub[name].iloc[0]
        pct = sub.groupby("quarter")[name].rank(pct=True).iloc[0] if False else None
        # Compute pct within quarter
        all_q = df[df["quarter"]==q][name].dropna()
        if len(all_q) > 0:
            pct = (all_q < score).sum() / len(all_q)
        else:
            pct = np.nan
        o1y = sub["O1Y_ret"].iloc[0] if "O1Y_ret" in sub.columns else np.nan
        print(f"    {tk} @ {q}: score={score:.3f}  pct={pct:.2f}  O1Y_after={o1y:+.1f}%")

df.to_csv("lh_v3_factor_panel_v2.csv", index=False)
print("\nSaved: lh_v3_factor_panel_v2.csv")
