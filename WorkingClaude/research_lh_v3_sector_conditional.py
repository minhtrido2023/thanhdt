#!/usr/bin/env python3
"""
research_lh_v3_sector_conditional.py
====================================
Build LH v3 Sector-Conditional (v3-SC) composite based on insight:
  - Commodity-cyclical groups (STEEL, OIL_GAS, RUBBER, AQUA, SHIPPING, CHEMICAL, COAL, SUGAR, CEMENT)
    → INVERSE cycle logic (buy at trough, sell at peak)
  - Non-commodity (BANK, REIT, INSURANCE, TEXTILE, RETAIL, etc.)
    → NORMAL cycle logic (buy improving fundamentals)
  - DEFAULT (OTHER) → moderate, value-tilted

Test IC + portfolio backtest at 12y canonical sim.
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, _CACHE

INIT_NAV = 50e9

# ─── LOAD PANEL ──────────────────────────────────────────────────────────
df = pd.read_csv("lh_v3_factor_panel_cycle.csv", parse_dates=["time"])
print(f"Panel: {len(df):,} rows")

# ─── SECTOR CLASSIFICATION (3 buckets) ───────────────────────────────────
COMMODITY_CYCLICAL = {"STEEL","OIL_GAS","RUBBER","AQUACULTURE","SHIPPING","CHEMICAL","COAL","SUGAR","CEMENT","PAPER_PULP","AVIATION"}
NON_COMMODITY_NORMAL = {"BANK","REIT_RES","REIT_KCN","INSURANCE","TEXTILE","RETAIL","SECURITIES","DAIRY","BEVERAGE","REAL_ESTATE_DIVERSIFIED"}

def bucket_of(grp):
    if grp in COMMODITY_CYCLICAL: return "CYCLICAL"
    if grp in NON_COMMODITY_NORMAL: return "STANDARD"
    return "DEFAULT"

df["bucket"] = df["cmd_group"].apply(bucket_of)
print(f"Bucket distribution: {df['bucket'].value_counts().to_dict()}")

# ─── COMPOSITE V13 — SECTOR CONDITIONAL ──────────────────────────────────
# Add reverse-NP-growth signal for cyclical (buy at trough)
df["F_rev_NP_yoy"] = -df["F_NP_TTM_growth"]

# Universal pct rank within (quarter, bucket) to keep apples-to-apples
def rank_q(df, col, bucket=None):
    if bucket:
        mask = df["bucket"] == bucket
        out = pd.Series(np.nan, index=df.index)
        for q, g in df[mask].groupby("quarter"):
            out.loc[g.index] = g[col].rank(pct=True, na_option="keep")
        return out
    else:
        return df.groupby("quarter")[col].rank(pct=True, na_option="keep")

# CYCLICAL formula — INVERSE cycle, deep value
CYC_W = {
    "F_rev_12_1":            0.20,  # reverse 12-1M momentum (buy oversold)
    "F_rev_NP_yoy":          0.10,  # reverse NP yoy (buy at NP trough)
    "F_smoothed_EY":         0.15,  # value
    "F_BY":                  0.10,
    "F_Cash_MktCap":         0.10,  # cash buffer survives downcycle
    "F_NetDebt_EBITDA_inv":  0.10,  # low leverage survives
    "F_ROE_min5Y":           0.10,  # quality floor
    "F_NP_stability":        0.10,  # less volatile through cycles
    "F_NP_peak_ratio":      -0.05,  # negative = anti-peak (NP_P0/max should be LOW = past peak)
}
# Note: F_NP_peak_ratio negative weight = invert it
# Sum: 0.20+0.10+0.15+0.10+0.10+0.10+0.10+0.10-0.05 = 0.90 (5% reserved)
# Reserve: add F_far_52w bonus for trough buying
CYC_W["F_far_52w"] = 0.05  # high = far below 52w high = at trough
CYC_W["F_FCF_yield"] = 0.05
# Re-sum: should be 1.0
total = sum(abs(v) for v in CYC_W.values())
# Normalize to absolute sum = 1.0
CYC_W = {k: v/total for k, v in CYC_W.items()}

# STANDARD formula (BANK, REIT, etc.) — normal momentum + quality
STD_W = {
    "F_smoothed_EY":         0.12,
    "F_BY":                  0.08,
    "F_FCF_yield":           0.08,
    "F_Cash_MktCap":         0.10,
    "F_ROE_min5Y":           0.12,
    "F_NP_stability":        0.08,
    "F_CFOA_NP_4Q":          0.08,
    "F_NP_TTM_growth":       0.10,  # NORMAL direction (improving fundamentals)
    "F_NetDebt_EBITDA_inv":  0.08,
    "F_Backlog_yld":         0.08,  # REIT/construction specific
    "F_DY_sust":             0.05,
    "F_above_MA200":         0.03,
}
total = sum(STD_W.values())
STD_W = {k: v/total for k, v in STD_W.items()}

# DEFAULT formula (universal value-balanced)
DEF_W = {
    "F_smoothed_EY":         0.15,
    "F_BY":                  0.10,
    "F_Cash_MktCap":         0.12,
    "F_ROE_min5Y":           0.10,
    "F_NP_stability":        0.08,
    "F_FCF_yield":           0.08,
    "F_NetDebt_EBITDA_inv":  0.08,
    "F_rev_12_1":            0.10,  # mild reverse mom (global tendency)
    "F_CFOA_NP_4Q":          0.08,
    "F_DY_sust":             0.05,
    "F_NP_TTM_growth":       0.06,
}
total = sum(DEF_W.values())
DEF_W = {k: v/total for k, v in DEF_W.items()}

# Build composite per bucket
def composite_for_bucket(df, bucket, weights):
    sub = df[df["bucket"] == bucket].copy()
    if len(sub) == 0: return pd.Series(np.nan, index=df.index)
    # Rank within (quarter, bucket) for each factor, then weighted sum
    parts = []
    used_w_sum = 0
    for f, w in weights.items():
        if f not in df.columns:
            print(f"  WARN: {f} missing in panel for {bucket}")
            continue
        # Rank globally within quarter (more apples-to-apples) but compute only for bucket
        rank = df.groupby("quarter")[f].rank(pct=True, na_option="keep")
        if w >= 0:
            parts.append(rank * w)
        else:
            parts.append((1 - rank) * abs(w))  # invert for negative weight
        used_w_sum += abs(w)
    if not parts: return pd.Series(np.nan, index=df.index)
    score = sum(parts) / used_w_sum
    out = pd.Series(np.nan, index=df.index)
    out.loc[sub.index] = score.loc[sub.index]
    return out

print("\nBuilding sector-conditional composite v13 ...")
cyc_score = composite_for_bucket(df, "CYCLICAL", CYC_W)
std_score = composite_for_bucket(df, "STANDARD", STD_W)
def_score = composite_for_bucket(df, "DEFAULT", DEF_W)

df["C13_sector_cond"] = cyc_score.fillna(std_score).fillna(def_score)

# ─── IC ANALYSIS ─────────────────────────────────────────────────────────
def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 100: return np.nan, 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

print("\n" + "="*120)
print("  C13 SECTOR-CONDITIONAL COMPOSITE — IC analysis")
print("="*120)

print(f"\n  {'Composite':<25}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}{'top10_1Y':>12}{'spread':>10}{'WR':>8}{'big_loss%':>11}")
for name in ["v8c_score","C13_sector_cond"]:
    if name not in df.columns: continue
    ic_3m, _ = spearman_ic(df[name], df["O3M_ret"])
    ic_6m, _ = spearman_ic(df[name], df["O6M_ret"])
    ic_1y, _ = spearman_ic(df[name], df["O1Y_ret"])
    ic_2y, _ = spearman_ic(df[name], df["O2Y_ret"])
    df_v = df.dropna(subset=[name,"O1Y_ret"]).copy()
    df_v["dec"] = df_v.groupby("quarter")[name].rank(pct=True)
    top10 = df_v[df_v["dec"] >= 0.90]
    top_med = top10["O1Y_ret"].median()
    spread = top_med - df_v["O1Y_ret"].median()
    wr = (top10["O1Y_ret"] > 0).mean() * 100
    big_loss = (top10["O1Y_ret"] < -20).mean() * 100
    label = name if name != "v8c_score" else "v8c (baseline)"
    print(f"  {label:<25}{ic_3m:>+8.4f}{ic_6m:>+8.4f}{ic_1y:>+8.4f}{ic_2y:>+8.4f}{top_med:>+11.2f}%{spread:>+9.2f}pp{wr:>7.1f}%{big_loss:>10.1f}%")

# IC per bucket
print("\n  IC by bucket:")
for bucket in ["CYCLICAL", "STANDARD", "DEFAULT"]:
    sub = df[df["bucket"]==bucket]
    if len(sub) < 100: continue
    ic_1y, n = spearman_ic(sub["C13_sector_cond"], sub["O1Y_ret"])
    ic_v8c, _ = spearman_ic(sub["v8c_score"], sub["O1Y_ret"])
    print(f"    {bucket:<12} N={n:>6}  C13 IC_1Y={ic_1y:+.4f}  v8c IC_1Y={ic_v8c:+.4f}")

# Top decile by bucket
print("\n  Top decile O1Y by bucket:")
for bucket in ["CYCLICAL", "STANDARD", "DEFAULT"]:
    sub = df[df["bucket"]==bucket].copy()
    if len(sub) < 100: continue
    sub["dec_v8c"] = sub.groupby("quarter")["v8c_score"].rank(pct=True)
    sub["dec_c13"] = sub.groupby("quarter")["C13_sector_cond"].rank(pct=True)
    v8c_top = sub[sub["dec_v8c"] >= 0.90]["O1Y_ret"].dropna()
    c13_top = sub[sub["dec_c13"] >= 0.90]["O1Y_ret"].dropna()
    print(f"    {bucket:<12}  v8c_top_med={v8c_top.median():>+6.2f}%  c13_top_med={c13_top.median():>+6.2f}%  delta={c13_top.median()-v8c_top.median():>+6.2f}pp")

# ─── PORTFOLIO BACKTEST ──────────────────────────────────────────────────
TIER_BANDS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]
def tier_of(pct):
    for n, lo, hi in TIER_BANDS:
        if lo <= pct <= hi: return n
    return "E"

# Build fa_ratings_lh_C13.csv
df_o = df.dropna(subset=["C13_sector_cond"]).copy()
df_o["pct"] = df_o.groupby("quarter")["C13_sector_cond"].rank(pct=True)
df_o["tier"] = df_o["pct"].apply(tier_of)
df_o["score"] = df_o["C13_sector_cond"]

fa_orig = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
meta = fa_orig[["ticker","quarter","time","Release_Date","sub","ICB_Code","MktCap","Volume_3M_P50","Close"]]
out = meta.merge(df_o[["ticker","quarter","score","pct","tier"]], on=["ticker","quarter"], how="inner")
out = out.dropna(subset=["score","tier"]).sort_values(["quarter","ticker"]).reset_index(drop=True)
out.to_csv("fa_ratings_lh_C13_sector_cond.csv", index=False)
print(f"\nBuilt fa_ratings_lh_C13: {len(out):,} rows, tier dist: {out['tier'].value_counts().to_dict()}")

# Backup and run
print("\n" + "="*120)
print("  PORTFOLIO BACKTEST — C13 vs v8c baseline")
print("="*120)

print("\n--- v8c baseline ---", flush=True)
_CACHE.clear()
res_v8c = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                  refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)

print("\n--- C13 sector-conditional ---", flush=True)
os.rename("fa_ratings_lh.csv", "fa_ratings_lh.csv.bak")
os.rename("fa_ratings_lh_C13_sector_cond.csv", "fa_ratings_lh.csv")
try:
    _CACHE.clear()
    res_c13 = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                      refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)
finally:
    os.rename("fa_ratings_lh.csv", "fa_ratings_lh_C13_sector_cond.csv")
    os.rename("fa_ratings_lh.csv.bak", "fa_ratings_lh.csv")

# Metrics
periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

for pname, ps, pe in periods:
    print(f"\n─── {pname} ───")
    print(f"  {'Variant':<25}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}")
    for label, res in [("v8c_baseline", res_v8c), ("C13_sector_cond", res_c13)]:
        nav = res["nav"]["nav"]
        s = nav[(nav.index >= ps) & (nav.index <= pe)]
        if len(s) < 30: continue
        m = compute_metrics(INIT_NAV * s/s.iloc[0], ps, pe)
        print(f"  {label:<25}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}")

# Picks comparison: 5-ticker
print("\n" + "="*120)
print("  5-TICKER LIFECYCLE (v8c vs C13)")
print("="*120)
CASES = ["VCS","DGC","VNM","FPT","MWG","HPG","BSR","VHC"]
prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])
for tk in CASES:
    p = prices[prices["ticker"]==tk].sort_values("time")
    if len(p) == 0: continue
    peak_dt = p.loc[p["Close"].idxmax(), "time"]
    peak_px = p["Close"].max()
    print(f"\n--- {tk} (peak {peak_px:.0f} on {peak_dt.date()}) ---")
    for label, res in [("v8c", res_v8c), ("C13", res_c13)]:
        tr = res["trades"]
        tk_tr = tr[tr["ticker"]==tk] if len(tr) > 0 else pd.DataFrame()
        if len(tk_tr) == 0:
            print(f"  {label}: NOT PICKED")
            continue
        buys = tk_tr[tk_tr["side"]=="BUY"]
        sells = tk_tr[tk_tr["side"].isin(["SELL","TRAIL_STOP"])]
        if len(buys) == 0:
            print(f"  {label}: no buy")
            continue
        fb = buys.iloc[0]
        if len(sells) > 0:
            ls = sells.iloc[-1]
            off_b = (peak_dt - fb["dt"]).days
            off_s = (ls["dt"] - peak_dt).days
            ret = (ls["px"]/fb["px"] - 1)*100
            print(f"  {label}: buy {fb['dt'].strftime('%Y-%m-%d')} @ {fb['px']:.0f} (peak{off_b:+d}d) → exit @ {ls['px']:.0f} (peak{off_s:+d}d)  {ret:+.1f}%")
        else:
            cur_px = p["Close"].iloc[-1]
            ret = (cur_px/fb["px"]-1)*100
            print(f"  {label}: buy {fb['dt'].strftime('%Y-%m-%d')} @ {fb['px']:.0f} → HOLD, now {cur_px:.0f}  {ret:+.1f}%")

print("\nDONE")
