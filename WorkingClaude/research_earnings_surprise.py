#!/usr/bin/env python3
"""
research_earnings_surprise.py — PEAD research

Hypothesis: market extrapolates next quarter from 4 prior quarters. Actual results
that BEAT this expectation drive positive drift (post-release T+5→T+30).

Test 5 expectation models built from NP_P1..NP_P4:
  A_linear   : trend(P3→P1) extrapolated to P0
  B_MA       : mean(P1..P4)
  C_YoY      : P4 × (1 + avg yoy growth from {P1/P5..P4/P8})  [needs P1..P8]
  D_LastQ    : P1 (latest quarter, naive anchor)
  E_Seasonal : P4 × (P1/P5) [seasonal-adjusted YoY]

For each event: surprise_method = (NP_P0 - expected) / max(|expected|, floor)
                surprise_z      = z-score of surprise within ticker history

Analyses:
  1. IC (rank correlation) — surprise vs post_ret
  2. Quintile breakdown — Q1 (worst surprise) vs Q5 (best) post_ret spread
  3. Time-decay — does surprise predict drift at T+10, T+30, T+60?
  4. Combined with current NP_R filter

Data: tav2_bq.ticker_financial (NP_P0..NP_P7 available)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
PROJECT = "lithe-record-440915-m9"
BQ = r"bq"

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

print("="*100)
print("  EARNINGS SURPRISE / PEAD RESEARCH")
print("="*100)

# ─── 1. Pull NP_P0..NP_P7 for all events ─────────────────────────────────
nq_cache = "data/earnings_surprise_data.pkl"
if os.path.exists(nq_cache):
    with open(nq_cache, "rb") as f: fin = pickle.load(f)
    print(f"[1] Loaded cache: {len(fin):,} events")
else:
    print("[1] Pulling NP_P0..NP_P7 from BQ ...")
    fin = bq_query("""
    SELECT f.ticker, f.quarter, f.time, f.Release_Date,
           f.NP_P0, f.NP_P1, f.NP_P2, f.NP_P3, f.NP_P4,
           f.NP_P5, f.NP_P6, f.NP_P7,
           f.NP_R, f.Revenue_YoY_P0
    FROM tav2_bq.ticker_financial AS f
    WHERE f.Release_Date IS NOT NULL
      AND f.Release_Date >= '2009-01-01'
      AND f.NP_P0 IS NOT NULL
    """)
    fin["Release_Date"] = pd.to_datetime(fin["Release_Date"])
    fin["time"] = pd.to_datetime(fin["time"])
    with open(nq_cache, "wb") as f: pickle.dump(fin, f)
    print(f"  Pulled + cached: {len(fin):,} events / {fin['ticker'].nunique()} tickers")

# ─── 2. Compute 5 expectation models + surprise scores ───────────────────
print("\n[2] Computing expectation models ...")
FLOOR = 1e9  # 1B VND floor to avoid divide-by-zero for small-NP tickers

def safe_div(num, denom, floor=FLOOR):
    """Bounded division for surprise computation"""
    return num / np.maximum(np.abs(denom), floor)

# A_linear: trend P3→P1 extrapolated to P0
# slope = (P1 - P3) / 2 (per quarter); predicted P0 = P1 + slope
fin["exp_A_linear"] = fin["NP_P1"] + (fin["NP_P1"] - fin["NP_P3"]) / 2

# B_MA: mean(P1..P4)
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)

# C_YoY: P4 × (1 + avg yoy growth from {P1/P5..P4/P8})  — needs P1..P8
yoy_p1 = fin["NP_P1"] / fin["NP_P5"].replace(0, np.nan) - 1
yoy_p2 = fin["NP_P2"] / fin["NP_P6"].replace(0, np.nan) - 1
yoy_p3 = fin["NP_P3"] / fin["NP_P7"].replace(0, np.nan) - 1
# Only 3 yoy ratios available (P0/P4 is what we're predicting, P4/P8 needs P8 we don't have)
yoy_avg = pd.concat([yoy_p1, yoy_p2, yoy_p3], axis=1).mean(axis=1)
fin["exp_C_YoY"] = fin["NP_P4"] * (1 + yoy_avg)

# D_LastQ: just P1 (latest quarter)
fin["exp_D_LastQ"] = fin["NP_P1"]

# E_Seasonal: P4 × (P1/P5)  — seasonal YoY adjusted from one cycle ago
fin["exp_E_Seasonal"] = fin["NP_P4"] * (fin["NP_P1"] / fin["NP_P5"].replace(0, np.nan))

# Compute surprises
for method in ["A_linear","B_MA","C_YoY","D_LastQ","E_Seasonal"]:
    col_exp = f"exp_{method}"
    fin[f"surprise_{method}"] = safe_div(fin["NP_P0"] - fin[col_exp], fin[col_exp])

# Summary diag
print(f"  Events with valid expectations:")
for m in ["A_linear","B_MA","C_YoY","D_LastQ","E_Seasonal"]:
    n = fin[f"surprise_{m}"].notna().sum()
    print(f"    {m:<12}: {n:>6,} valid")

# Clip extreme surprises to prevent outliers
for m in ["A_linear","B_MA","C_YoY","D_LastQ","E_Seasonal"]:
    fin[f"surprise_{m}"] = fin[f"surprise_{m}"].clip(-5, 5)

# ─── 3. Merge with post_ret data ─────────────────────────────────────────
print("\n[3] Merging with post-release returns ...")
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
print(f"  Classified events: {len(ev_class):,}")

merged = fin.merge(
    ev_class[["ticker","quarter","Release_Date","pre_ret","rel_ret","post_ret","NP_R"]],
    on=["ticker","quarter","Release_Date"], how="inner", suffixes=("","_class"))
print(f"  Merged: {len(merged):,} events with both surprise + post_ret")

# Filter to events with valid post_ret
merged = merged[merged["post_ret"].notna()]
print(f"  With post_ret available: {len(merged):,}")

# ─── 4. IC analysis (Pearson + Spearman) ─────────────────────────────────
print("\n" + "="*100)
print("  IC ANALYSIS — Correlation between surprise vs post-release returns")
print("="*100)

results = []
for m in ["A_linear","B_MA","C_YoY","D_LastQ","E_Seasonal"]:
    col = f"surprise_{m}"
    sub = merged[[col, "pre_ret","rel_ret","post_ret"]].dropna()
    if len(sub) < 100: continue
    res = {"method": m, "N": len(sub)}
    for ret_col in ["pre_ret","rel_ret","post_ret"]:
        pearson = sub[col].corr(sub[ret_col])
        # Manual Spearman via rank to avoid scipy dependency
        spearman = sub[col].rank().corr(sub[ret_col].rank())
        res[f"{ret_col}_pearson"] = pearson
        res[f"{ret_col}_spearman"] = spearman
    results.append(res)

# Compare with raw NP_R as benchmark
sub_npr = merged[["NP_R","post_ret","rel_ret","pre_ret"]].dropna()
res_npr = {"method": "BENCHMARK_NP_R", "N": len(sub_npr)}
for ret_col in ["pre_ret","rel_ret","post_ret"]:
    res_npr[f"{ret_col}_pearson"] = sub_npr["NP_R"].corr(sub_npr[ret_col])
    res_npr[f"{ret_col}_spearman"] = sub_npr["NP_R"].rank().corr(sub_npr[ret_col].rank())
results.append(res_npr)

ic_df = pd.DataFrame(results)
print(f"\n  {'Method':<18}{'N':>7}{'pre_S':>10}{'rel_S':>10}{'post_S':>10}{'pre_P':>10}{'rel_P':>10}{'post_P':>10}")
print("  " + "-"*85)
for _, r in ic_df.iterrows():
    print(f"  {r['method']:<18}{r['N']:>7d}"
          f"{r['pre_ret_spearman']:>+9.3f}{r['rel_ret_spearman']:>+9.3f}{r['post_ret_spearman']:>+9.3f}"
          f"{r['pre_ret_pearson']:>+9.3f}{r['rel_ret_pearson']:>+9.3f}{r['post_ret_pearson']:>+9.3f}")

print("\n  Spearman = rank correlation (robust to outliers)")
print("  Higher post_S = stronger drift prediction")

# ─── 5. Quintile analysis ────────────────────────────────────────────────
print("\n" + "="*100)
print("  QUINTILE ANALYSIS — Sort events by surprise, measure post_ret per bucket")
print("="*100)

best_method = None
best_spread = 0

for m in ["A_linear","B_MA","C_YoY","D_LastQ","E_Seasonal","NP_R_benchmark"]:
    col = "NP_R" if m == "NP_R_benchmark" else f"surprise_{m}"
    sub = merged[[col, "pre_ret","rel_ret","post_ret"]].dropna()
    if len(sub) < 500: continue
    sub = sub.copy()
    sub["Q"] = pd.qcut(sub[col], 5, labels=["Q1_worst","Q2","Q3","Q4","Q5_best"])

    q_stats = sub.groupby("Q").agg(
        N=("post_ret","size"),
        pre_avg=("pre_ret","mean"),
        rel_avg=("rel_ret","mean"),
        post_avg=("post_ret","mean"),
        post_med=("post_ret","median"),
        post_wr=("post_ret", lambda x: (x>0).mean()*100),
    )
    print(f"\n  --- {m} ---")
    print(q_stats.to_string(float_format="%.2f"))
    spread = q_stats.loc["Q5_best","post_avg"] - q_stats.loc["Q1_worst","post_avg"]
    print(f"  Q5-Q1 spread (post_ret): {spread:+.2f}pp")
    if abs(spread) > abs(best_spread):
        best_spread = spread
        best_method = m

print(f"\n  🏆 Best Q5-Q1 spread: {best_method} ({best_spread:+.2f}pp)")

# ─── 6. Combined filter: surprise + NP_R ─────────────────────────────────
print("\n" + "="*100)
print("  COMBINED FILTER — surprise top quintile + NP_R ≥ 15%")
print("="*100)

best_col = "NP_R" if best_method == "NP_R_benchmark" else f"surprise_{best_method}"
sub = merged[[best_col,"NP_R","post_ret"]].dropna().copy()
# Find top quintile threshold
q80_thr = sub[best_col].quantile(0.80)
print(f"  Top-20% surprise threshold ({best_method}): {q80_thr:.3f}")

# Test 4 filter combinations
filters = {
    "All events":                                   sub[best_col].notna(),
    "Only NP_R ≥ 15%":                              sub["NP_R"] >= 15,
    f"Only surprise top-20% ({best_method})":       sub[best_col] >= q80_thr,
    f"Both NP_R≥15 AND surprise top-20%":           (sub["NP_R"] >= 15) & (sub[best_col] >= q80_thr),
}
print(f"\n  {'Filter':<45}{'N':>8}{'avg post_ret':>15}{'WR':>10}")
print("  " + "-"*78)
for name, mask in filters.items():
    fs = sub[mask]
    if len(fs) < 10: continue
    avg = fs["post_ret"].mean()
    wr = (fs["post_ret"] > 0).mean() * 100
    print(f"  {name:<45}{len(fs):>8,d}{avg:>+14.2f}%{wr:>+9.1f}%")

# ─── 7. Time-decay analysis (use post_ret as proxy — already T+5→T+30) ───
# We don't have post_ret_60d easily. Skip for now or note as future work.
print("\n  Note: post_ret is fixed T+5→T+30 window. Future work: extend to T+5→T+60.")

# ─── 8. Save merged data for later ───────────────────────────────────────
out_cols = ["ticker","quarter","Release_Date","NP_R","Revenue_YoY_P0",
            "NP_P0","NP_P1","NP_P4",
            "exp_A_linear","exp_B_MA","exp_C_YoY","exp_D_LastQ","exp_E_Seasonal",
            "surprise_A_linear","surprise_B_MA","surprise_C_YoY","surprise_D_LastQ","surprise_E_Seasonal",
            "pre_ret","rel_ret","post_ret"]
merged[out_cols].to_csv("data/earnings_surprise_research.csv", index=False)
ic_df.to_csv("data/earnings_surprise_IC.csv", index=False)
print("\nSaved: earnings_surprise_research.csv, earnings_surprise_IC.csv")
