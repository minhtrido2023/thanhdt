#!/usr/bin/env python3
"""
research_lh_v3_c14_hybrid.py
============================
C14 Hybrid: C13 sector-conditional for CYCLICAL bucket + v8c for STANDARD/DEFAULT.

Rationale: per-bucket IC analysis shows:
  - CYCLICAL: C13 +0.132 IC >> v8c +0.043 → use C13
  - STANDARD: v8c +0.066 > C13 +0.052 → use v8c
  - DEFAULT: ~tied → use v8c (more samples, more stable)

Hypothesis: Hybrid preserves multi-year winners (FPT/VNM) while filtering commodity peaks (DGC/HPG).
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np
from simulate_lh_nav import run_lh, compute_metrics, _CACHE

INIT_NAV = 50e9

df = pd.read_csv("lh_v3_factor_panel_cycle.csv", parse_dates=["time"])

COMMODITY_CYCLICAL = {"STEEL","OIL_GAS","RUBBER","AQUACULTURE","SHIPPING","CHEMICAL","COAL","SUGAR","CEMENT","PAPER_PULP","AVIATION"}
df["bucket"] = df["cmd_group"].apply(lambda g: "CYCLICAL" if g in COMMODITY_CYCLICAL else "STANDARD")

# Use existing C13_sector_cond from panel + v8c_score
# If C13 not in panel, rebuild from raw factors
if "C13_sector_cond" not in df.columns:
    print("Rebuilding C13_sector_cond from raw factors ...")
    df["F_rev_NP_yoy"] = -df["F_NP_TTM_growth"]

    def composite_for_bucket(df, bucket, weights):
        sub = df[df["bucket"] == bucket].copy()
        if len(sub) == 0: return pd.Series(np.nan, index=df.index)
        parts, used_w = [], 0
        for f, w in weights.items():
            if f not in df.columns: continue
            rank = df.groupby("quarter")[f].rank(pct=True, na_option="keep")
            if w >= 0:
                parts.append(rank * w)
            else:
                parts.append((1 - rank) * abs(w))
            used_w += abs(w)
        if not parts: return pd.Series(np.nan, index=df.index)
        score = sum(parts) / used_w
        out = pd.Series(np.nan, index=df.index)
        out.loc[sub.index] = score.loc[sub.index]
        return out

    CYC_W = {"F_rev_12_1":0.20,"F_rev_NP_yoy":0.10,"F_smoothed_EY":0.15,"F_BY":0.10,
             "F_Cash_MktCap":0.10,"F_NetDebt_EBITDA_inv":0.10,"F_ROE_min5Y":0.10,
             "F_NP_stability":0.10,"F_NP_peak_ratio":-0.05,"F_far_52w":0.05,"F_FCF_yield":0.05}
    cyc = composite_for_bucket(df, "CYCLICAL", CYC_W)
    df["C13_sector_cond"] = cyc.fillna(df["v8c_score"])  # fill non-cyclical with v8c

# C14: use C13 for CYCLICAL, v8c for others
df["C14_hybrid"] = np.where(df["bucket"]=="CYCLICAL", df["C13_sector_cond"], df["v8c_score"])

# But scales differ — need to rank within quarter
df["C14_hybrid_rank"] = df.groupby("quarter")["C14_hybrid"].rank(pct=True, na_option="keep")

# Actually the simpler approach: rank each within quarter, then take corresponding ranked value
df["v8c_rank"] = df.groupby("quarter")["v8c_score"].rank(pct=True, na_option="keep")
df["C13_rank"] = df.groupby("quarter")["C13_sector_cond"].rank(pct=True, na_option="keep")
df["C14_hybrid_v2"] = np.where(df["bucket"]=="CYCLICAL", df["C13_rank"], df["v8c_rank"])

# C15: 80/20 weighted blend (mostly v8c, cycle-aware tilt)
df["C15_v8c_cycle_tilt"] = 0.80 * df["v8c_rank"] + 0.20 * df["C13_rank"]

# C16: 50/50 blend
df["C16_balanced"] = 0.50 * df["v8c_rank"] + 0.50 * df["C13_rank"]

def spearman_ic(x, y):
    s = pd.DataFrame({"x":x, "y":y}).dropna()
    if len(s) < 100: return np.nan, 0
    return s["x"].rank().corr(s["y"].rank(), method="pearson"), len(s)

print("\n" + "="*120)
print("  IC + TOP DECILE COMPARISON")
print("="*120)
print(f"\n  {'Composite':<25}{'IC_3M':>8}{'IC_6M':>8}{'IC_1Y':>8}{'IC_2Y':>8}{'top10_1Y':>12}{'spread':>10}{'WR':>8}")
for name in ["v8c_score","C13_sector_cond","C14_hybrid_v2","C15_v8c_cycle_tilt","C16_balanced"]:
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
    label = name if name != "v8c_score" else "v8c (baseline)"
    print(f"  {label:<25}{ic_3m:>+8.4f}{ic_6m:>+8.4f}{ic_1y:>+8.4f}{ic_2y:>+8.4f}{top_med:>+11.2f}%{spread:>+9.2f}pp{wr:>7.1f}%")

# ─── PORTFOLIO BACKTEST ──────────────────────────────────────────────────
TIER_BANDS = [("A",0.90,1.00),("B",0.70,0.90),("C",0.40,0.70),("D",0.15,0.40),("E",0.00,0.15)]
def tier_of(pct):
    for n, lo, hi in TIER_BANDS:
        if lo <= pct <= hi: return n
    return "E"

# Build ratings file for each candidate
fa_orig = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
meta = fa_orig[["ticker","quarter","time","Release_Date","sub","ICB_Code","MktCap","Volume_3M_P50","Close"]]

results = {"v8c_baseline": None}
print("\n--- v8c baseline ---", flush=True)
_CACHE.clear()
results["v8c_baseline"] = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                                   refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)

for name in ["C14_hybrid_v2","C15_v8c_cycle_tilt","C16_balanced"]:
    df_o = df.dropna(subset=[name]).copy()
    df_o["pct"] = df_o.groupby("quarter")[name].rank(pct=True)
    df_o["tier"] = df_o["pct"].apply(tier_of)
    df_o["score"] = df_o[name]
    out = meta.merge(df_o[["ticker","quarter","score","pct","tier"]], on=["ticker","quarter"], how="inner")
    out = out.dropna(subset=["score","tier"]).sort_values(["quarter","ticker"]).reset_index(drop=True)
    fname = f"fa_ratings_lh_{name}.csv"
    out.to_csv(fname, index=False)

    print(f"\n--- {name} ---", flush=True)
    os.rename("fa_ratings_lh.csv", "fa_ratings_lh.csv.bak")
    os.rename(fname, "fa_ratings_lh.csv")
    try:
        _CACHE.clear()
        results[name] = run_lh(hold_quarters=4, n_positions=10, tier_set=("A","B"), incl_sub="all",
                                refresh_mode="staggered", crisis_gate=True, init_nav=INIT_NAV)
    finally:
        os.rename("fa_ratings_lh.csv", fname)
        os.rename("fa_ratings_lh.csv.bak", "fa_ratings_lh.csv")

# Metrics
periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

print("\n" + "="*120)
print("  PORTFOLIO METRICS — ALL VARIANTS")
print("="*120)
for pname, ps, pe in periods:
    print(f"\n─── {pname} ───")
    print(f"  {'Variant':<25}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'avg_pos':>10}")
    for label, res in results.items():
        nav = res["nav"]["nav"]
        s = nav[(nav.index >= ps) & (nav.index <= pe)]
        if len(s) < 30: continue
        m = compute_metrics(INIT_NAV * s/s.iloc[0], ps, pe)
        avg_p = res["nav"]["n_pos"].mean()
        print(f"  {label:<25}{m['CAGR']:>+10.2%}{m['Sharpe']:>+10.2f}{m['MaxDD']:>+10.2%}{m['Calmar']:>+10.2f}{avg_p:>+10.2f}")

# 5-ticker lifecycle
print("\n" + "="*120)
print("  5-TICKER LIFECYCLE — KEY VARIANTS")
print("="*120)
CASES = ["VCS","DGC","VNM","FPT","HPG","BSR","VHC","HAH","GVR"]
prices = pd.read_csv("prices_lh.csv", parse_dates=["time"])
for tk in CASES:
    p = prices[prices["ticker"]==tk].sort_values("time")
    if len(p) == 0: continue
    peak_dt = p.loc[p["Close"].idxmax(), "time"]
    peak_px = p["Close"].max()
    print(f"\n--- {tk} (peak {peak_px:.0f} on {peak_dt.date()}) ---")
    for label, res in results.items():
        tr = res["trades"]
        tk_tr = tr[tr["ticker"]==tk] if len(tr) > 0 else pd.DataFrame()
        if len(tk_tr) == 0:
            print(f"  {label:<25}  NOT PICKED")
            continue
        buys = tk_tr[tk_tr["side"]=="BUY"]
        sells = tk_tr[tk_tr["side"].isin(["SELL","TRAIL_STOP"])]
        if len(buys) == 0: continue
        fb = buys.iloc[0]
        if len(sells) > 0:
            ls = sells.iloc[-1]
            ret = (ls["px"]/fb["px"] - 1)*100
            print(f"  {label:<25}  buy @ {fb['px']:.0f} ({fb['dt'].strftime('%Y-%m-%d')}) → exit @ {ls['px']:.0f} ({ls['dt'].strftime('%Y-%m-%d')})  {ret:+.1f}%")
        else:
            cur = p["Close"].iloc[-1]
            ret = (cur/fb["px"]-1)*100
            print(f"  {label:<25}  buy @ {fb['px']:.0f} ({fb['dt'].strftime('%Y-%m-%d')}) → HOLD, now {cur:.0f}  {ret:+.1f}%")

print("\nDONE")
