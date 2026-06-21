# -*- coding: utf-8 -*-
"""Phase A: Build & validate multi-factor regime score.

4 factors (no look-ahead, expanding distribution where applicable):
  F1 Vol        — VNI 20d realized vol; bearish if > P75 expanding (252d min warmup)
  F2 Breadth    — pct of ticker_prune universe with Close > MA50; bearish if 5d-MA < 50% AND declining
  F3 Trend      — VNI/MA200; bearish if ratio < 1.0 AND MA200 slope 20d < 0
  F4 Momentum   — VNI D_RSI; bearish if < 35 (oversold) OR > 78 (overbought)

Score = sum (0-4). Map → hold_days: {0:90, 1:70, 2:50, 3:30, 4:15}

Validation:
  - Distribution of score days 2014-2026
  - Forward VNI return T+20/T+45/T+60 per score: mean, hit rate, Spearman ρ
  - Compare with TQ v3.4b 5-state mapping (option 1 baseline)
  - Threshold sweep on F1/F4 to check robustness

Outputs:
  - regime_score_research.csv         : daily score time series
  - regime_score_research_summary.md  : tables + verdict
"""
import os, io, sys
import numpy as np
import pandas as pd
def spearmanr(a, b):
    """Minimal Spearman implementation (no scipy)."""
    a = pd.Series(a).reset_index(drop=True)
    b = pd.Series(b).reset_index(drop=True)
    ra = a.rank(); rb = b.rank()
    n = len(a)
    if n < 3: return (np.nan, np.nan)
    rho = ra.corr(rb)
    # Approximate p-value via normal approximation
    if pd.isna(rho) or abs(rho) >= 1: return (rho, 0.0)
    t = rho * np.sqrt((n-2)/(1-rho*rho))
    # two-sided p from normal approx (rough but fine for our use)
    from math import erfc, sqrt
    p = erfc(abs(t)/sqrt(2))
    return (rho, p)
import subprocess

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

START = "2014-01-01"
END   = "2026-05-19"


BQ_EXE = r"bq"
BQ_ENV = os.environ.copy()
BQ_ENV["CLOUDSDK_PYTHON"] = r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\platform\bundledpython\python.exe"
import tempfile
def bq(sql):
    # Write SQL to a temp file and pass via stdin to avoid Windows cmd line mangling
    r = subprocess.run(
        [BQ_EXE,"query","--use_legacy_sql=false","--project_id=lithe-record-440915-m9","--format=csv","--max_rows=10000000"],
        input=sql, capture_output=True, text=True, timeout=600, shell=False, env=BQ_ENV
    )
    if r.returncode != 0:
        raise RuntimeError(f"BQ error (rc={r.returncode}): STDERR={r.stderr[:500]} STDOUT={r.stdout[:500]}")
    return pd.read_csv(io.StringIO(r.stdout))


print("="*100)
print("  PHASE A — Multi-factor regime score research")
print(f"  Period: {START} → {END}")
print("="*100)

# ============================================================================
# 1. Pull VNI history (Close, MA200, D_RSI)
# ============================================================================
print("\n[1] Pulling VNI history...")
vni = bq(f"""
SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START}' AND DATE '{END}'
ORDER BY t.time
""")
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
print(f"  {len(vni)} VNI rows")

# ============================================================================
# 2. Compute breadth from ticker_prune universe
# ============================================================================
print("\n[2] Computing breadth (% prune > MA50)...")
breadth = bq(f"""
SELECT t.time,
  SUM(CASE WHEN t.MA50 IS NOT NULL AND t.Close > t.MA50 THEN 1.0 ELSE 0 END) /
  NULLIF(SUM(CASE WHEN t.MA50 IS NOT NULL THEN 1.0 ELSE 0 END), 0) AS breadth,
  COUNT(*) AS n_universe
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START}' AND DATE '{END}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.time
ORDER BY t.time
""")
breadth["time"] = pd.to_datetime(breadth["time"])
print(f"  {len(breadth)} breadth rows; mean universe size = {breadth['n_universe'].mean():.0f}")

# ============================================================================
# 3. Pull TQ v3.4b state for comparison
# ============================================================================
print("\n[3] Pulling TQ v3.4b state...")
state = bq(f"""
SELECT s.time, s.state
FROM tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s
WHERE s.time BETWEEN DATE '{START}' AND DATE '{END}'
ORDER BY s.time
""")
state["time"] = pd.to_datetime(state["time"])
print(f"  {len(state)} state rows")

# ============================================================================
# 4. Merge + compute factors (no look-ahead)
# ============================================================================
print("\n[4] Computing factors...")
df = vni.merge(breadth[["time","breadth"]], on="time", how="left").merge(state, on="time", how="left")

# Forward fill state (small gaps)
df["state"] = df["state"].ffill()

# F1: 20d realized vol on log returns
df["log_ret"] = np.log(df["Close"] / df["Close"].shift(1))
df["vol_20d"] = df["log_ret"].rolling(20, min_periods=15).std() * np.sqrt(252)  # annualised

# Vol rank expanding (no look-ahead): rank-percentile vs expanding window, 252d min warmup
def expanding_rank_pct(s, min_periods=252):
    out = np.full(len(s), np.nan)
    arr = s.values
    for i in range(min_periods-1, len(s)):
        window = arr[:i+1]
        valid = window[~np.isnan(window)]
        if len(valid) < min_periods: continue
        cur = arr[i]
        if np.isnan(cur): continue
        out[i] = (valid < cur).mean()  # percentile 0-1
    return pd.Series(out, index=s.index)

df["vol_rank"] = expanding_rank_pct(df["vol_20d"], min_periods=252)

# F2: breadth 5d MA + declining
df["breadth_ma5"] = df["breadth"].rolling(5, min_periods=3).mean()
df["breadth_ma5_d10"] = df["breadth_ma5"] - df["breadth_ma5"].shift(10)  # slope over 10d

# F3: VNI/MA200 ratio + MA200 slope 20d
df["vni_ma200"] = df["Close"] / df["MA200"]
df["ma200_slope_20d"] = df["MA200"] / df["MA200"].shift(20) - 1

# F4: D_RSI (already 0-1 daily)

# ============================================================================
# 5. Apply primary thresholds → 4-factor binary
# ============================================================================
print("\n[5] Building primary regime score (baseline thresholds)...")
df["F1_vol_bear"]     = (df["vol_rank"] > 0.75).astype(int)
df["F2_breadth_bear"] = ((df["breadth_ma5"] < 0.50) & (df["breadth_ma5_d10"] < 0)).astype(int)
df["F3_trend_bear"]   = ((df["vni_ma200"] < 1.0) & (df["ma200_slope_20d"] < 0)).astype(int)
df["F4_rsi_extreme"]  = (((df["D_RSI"] * 100) < 35) | ((df["D_RSI"] * 100) > 78)).astype(int)
# Zero out where any factor undefined (warmup)
mask_def = df[["vol_rank","breadth_ma5","ma200_slope_20d","D_RSI"]].notna().all(axis=1)
for c in ["F1_vol_bear","F2_breadth_bear","F3_trend_bear","F4_rsi_extreme"]:
    df.loc[~mask_def, c] = np.nan
df["regime_score"] = df[["F1_vol_bear","F2_breadth_bear","F3_trend_bear","F4_rsi_extreme"]].sum(axis=1, min_count=4)
print(f"  Days with defined score: {df['regime_score'].notna().sum()} / {len(df)}")

# Map score → hold_days
HOLD_MAP = {0:90, 1:70, 2:50, 3:30, 4:15}
df["hold_days_score"] = df["regime_score"].map(HOLD_MAP)

# ============================================================================
# 6. Forward VNI returns for validation
# ============================================================================
print("\n[6] Computing forward VNI returns (T+20, T+45, T+60)...")
for h in [20, 45, 60]:
    df[f"fwd_ret_{h}d"] = df["Close"].shift(-h) / df["Close"] - 1

# ============================================================================
# 7. Distribution + predictive power per score
# ============================================================================
print("\n[7] Score distribution & predictive power...")
score_dist = df["regime_score"].value_counts().sort_index()
print("\n  Score distribution (days):")
for s, n in score_dist.items():
    print(f"    score={int(s)}  n={n:>5}  pct={n/score_dist.sum()*100:5.1f}%")

predictive = []
for s in sorted(df["regime_score"].dropna().unique()):
    sub = df[df["regime_score"] == s]
    row = {"score": int(s), "n_days": len(sub),
           "hold_map_d": HOLD_MAP[int(s)]}
    for h in [20, 45, 60]:
        r = sub[f"fwd_ret_{h}d"].dropna()
        row[f"T+{h}_mean%"] = r.mean()*100 if len(r) else np.nan
        row[f"T+{h}_med%"]  = r.median()*100 if len(r) else np.nan
        row[f"T+{h}_hit%"]  = (r > 0).mean()*100 if len(r) else np.nan
    predictive.append(row)
predictive_df = pd.DataFrame(predictive)
print("\n  Forward return per score:")
print(predictive_df.to_string(index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x,float) and not pd.isna(x) else "n/a"))

# Spearman rank corr: high score should predict LOWER forward returns (negative ρ)
spearman_rows = []
for h in [20, 45, 60]:
    sub = df[["regime_score", f"fwd_ret_{h}d"]].dropna()
    rho, p = spearmanr(sub["regime_score"].values, sub[f"fwd_ret_{h}d"].values)
    spearman_rows.append({"horizon": f"T+{h}d", "n": len(sub), "rho": rho, "p_value": p})
spearman_df = pd.DataFrame(spearman_rows)
print("\n  Spearman ρ (score vs forward return; expect NEGATIVE):")
print(spearman_df.to_string(index=False, float_format=lambda x: f"{x:.4f}" if isinstance(x,float) else x))

# ============================================================================
# 8. Compare with TQ v3.4b 5-state mapping (option 1 baseline)
# ============================================================================
print("\n[8] Compare with TQ v3.4b state mapping (option 1)...")
STATE_HOLD = {1:15, 2:20, 3:40, 4:75, 5:45}
df["hold_days_state"] = df["state"].map(STATE_HOLD)

state_pred = []
for s in sorted(df["state"].dropna().unique()):
    sub = df[df["state"] == s]
    row = {"state": int(s), "n_days": len(sub), "hold_map_d": STATE_HOLD.get(int(s))}
    for h in [20, 45, 60]:
        r = sub[f"fwd_ret_{h}d"].dropna()
        row[f"T+{h}_mean%"] = r.mean()*100 if len(r) else np.nan
        row[f"T+{h}_med%"]  = r.median()*100 if len(r) else np.nan
        row[f"T+{h}_hit%"]  = (r > 0).mean()*100 if len(r) else np.nan
    state_pred.append(row)
state_pred_df = pd.DataFrame(state_pred)
print("\n  Forward return per TQ v3.4b state (baseline option 1):")
print(state_pred_df.to_string(index=False, float_format=lambda x: f"{x:.2f}" if isinstance(x,float) and not pd.isna(x) else "n/a"))

# Spearman: high state = bull → POSITIVE forward return; so ρ should be POSITIVE
spearman_state = []
for h in [20, 45, 60]:
    sub = df[["state", f"fwd_ret_{h}d"]].dropna()
    rho, p = spearmanr(sub["state"], sub[f"fwd_ret_{h}d"])
    spearman_state.append({"horizon": f"T+{h}d", "n": len(sub), "rho": rho, "p_value": p})
spearman_state_df = pd.DataFrame(spearman_state)
print("\n  TQ v3.4b state Spearman ρ (expect POSITIVE since high state = bull):")
print(spearman_state_df.to_string(index=False, float_format=lambda x: f"{x:.4f}" if isinstance(x,float) else x))

# Cross-tab score x state (overlap matrix)
ct = pd.crosstab(df["regime_score"], df["state"], margins=True, margins_name="ALL")
print("\n  Overlap matrix (score × state):")
print(ct.to_string())

# ============================================================================
# 9. Threshold sweep on F1 (vol percentile) and F4 (RSI cutoffs)
# ============================================================================
print("\n[9] Threshold sweep...")
sweep_rows = []
for vol_p in [0.70, 0.75, 0.80, 0.85]:
    for rsi_lo, rsi_hi in [(30,80),(35,78),(40,75)]:
        f1 = (df["vol_rank"] > vol_p).astype(int)
        f4 = (((df["D_RSI"]*100) < rsi_lo) | ((df["D_RSI"]*100) > rsi_hi)).astype(int)
        f2 = df["F2_breadth_bear"]; f3 = df["F3_trend_bear"]
        for c in [f1, f4]: c.loc[~mask_def] = np.nan
        sc = (f1 + f2 + f3 + f4)
        for h in [45]:
            sub = pd.concat([sc.rename("sc"), df[f"fwd_ret_{h}d"]], axis=1).dropna()
            rho,_ = spearmanr(sub["sc"], sub[f"fwd_ret_{h}d"])
            sweep_rows.append({"vol_p": vol_p, "rsi_lo": rsi_lo, "rsi_hi": rsi_hi,
                "horizon": h, "rho_T+45": rho,
                "n_score4": int((sc==4).sum()), "n_score0": int((sc==0).sum())})
sweep_df = pd.DataFrame(sweep_rows)
print("\n  Threshold sweep (target: most negative ρ_T+45):")
print(sweep_df.sort_values("rho_T+45").to_string(index=False, float_format=lambda x: f"{x:.4f}" if isinstance(x,float) else x))

# ============================================================================
# 10. Save outputs + verdict
# ============================================================================
print("\n[10] Saving outputs...")
out_cols = ["time","Close","MA200","D_RSI","breadth","vol_20d","vol_rank",
            "breadth_ma5","breadth_ma5_d10","vni_ma200","ma200_slope_20d",
            "F1_vol_bear","F2_breadth_bear","F3_trend_bear","F4_rsi_extreme",
            "regime_score","hold_days_score","state","hold_days_state",
            "fwd_ret_20d","fwd_ret_45d","fwd_ret_60d"]
df[out_cols].to_csv(os.path.join(WORKDIR,"data","regime_score_research.csv"), index=False)

# Verdict summary
multi_rho_45 = spearman_df.set_index("horizon").loc["T+45d","rho"]
state_rho_45 = spearman_state_df.set_index("horizon").loc["T+45d","rho"]

verdict_lines = []
verdict_lines.append("# Phase A — Regime Score Research Summary\n")
verdict_lines.append(f"**Period**: {df['time'].min().date()} → {df['time'].max().date()} ({df['regime_score'].notna().sum()} days with defined score)\n")
verdict_lines.append("## Score distribution\n")
verdict_lines.append("| Score | Days | Pct | hold_d |")
verdict_lines.append("|---|---|---|---|")
for s, n in score_dist.items():
    verdict_lines.append(f"| {int(s)} | {n} | {n/score_dist.sum()*100:.1f}% | {HOLD_MAP[int(s)]} |")
verdict_lines.append("\n## Forward return per score (Multi-factor)\n")
verdict_lines.append("| Score | n | T+20 mean% | T+45 mean% | T+60 mean% | T+45 hit% |")
verdict_lines.append("|---|---|---|---|---|---|")
for _,r in predictive_df.iterrows():
    verdict_lines.append(f"| {r['score']} | {r['n_days']} | {r['T+20_mean%']:.2f} | {r['T+45_mean%']:.2f} | {r['T+60_mean%']:.2f} | {r['T+45_hit%']:.1f} |")

verdict_lines.append("\n## Forward return per TQ v3.4b state (Option 1 baseline)\n")
verdict_lines.append("| State | n | T+20 mean% | T+45 mean% | T+60 mean% | T+45 hit% |")
verdict_lines.append("|---|---|---|---|---|---|")
for _,r in state_pred_df.iterrows():
    verdict_lines.append(f"| {r['state']} | {r['n_days']} | {r['T+20_mean%']:.2f} | {r['T+45_mean%']:.2f} | {r['T+60_mean%']:.2f} | {r['T+45_hit%']:.1f} |")

verdict_lines.append("\n## Spearman ρ comparison (T+45d)\n")
verdict_lines.append(f"- **Multi-factor score**: ρ = {multi_rho_45:+.4f}  (expect NEGATIVE; magnitude → stronger predictor)")
verdict_lines.append(f"- **TQ v3.4b state**:    ρ = {state_rho_45:+.4f}  (expect POSITIVE; |ρ| → stronger)")
verdict_lines.append(f"- **|Multi-ρ| vs |State-ρ|**: {abs(multi_rho_45):.4f} vs {abs(state_rho_45):.4f}  → {'Multi WINS' if abs(multi_rho_45)>abs(state_rho_45) else 'State WINS'}")

verdict_lines.append("\n## Threshold sweep top 5 (lowest ρ_T+45 = best predictor)\n")
verdict_lines.append("| vol_p | rsi_lo | rsi_hi | ρ_T+45 | n_score4 | n_score0 |")
verdict_lines.append("|---|---|---|---|---|---|")
for _,r in sweep_df.nsmallest(5, "rho_T+45").iterrows():
    verdict_lines.append(f"| {r['vol_p']} | {r['rsi_lo']} | {r['rsi_hi']} | {r['rho_T+45']:+.4f} | {r['n_score4']} | {r['n_score0']} |")

# Gate
gate_pass = (multi_rho_45 < -0.10) and (abs(multi_rho_45) >= abs(state_rho_45) * 0.8)
verdict_lines.append(f"\n## GATE\n")
verdict_lines.append(f"- Required: ρ_T+45 < -0.10 AND |multi-ρ| ≥ 0.8 × |state-ρ|")
verdict_lines.append(f"- Got: ρ_T+45 = {multi_rho_45:+.4f}, |multi|/|state| = {abs(multi_rho_45)/max(abs(state_rho_45),1e-9):.2f}")
verdict_lines.append(f"- **{'PASS — proceed to Phase B' if gate_pass else 'FAIL — redesign or use simpler state mapping'}**")

with open(os.path.join(WORKDIR,"data","regime_score_research_summary.md"),"w",encoding="utf-8") as f:
    f.write("\n".join(verdict_lines))

print("\n  data/regime_score_research.csv")
print("  data/regime_score_research_summary.md")
print("\n" + "="*100)
print(f"  VERDICT: Multi-ρ={multi_rho_45:+.4f}  State-ρ={state_rho_45:+.4f}  Gate {'PASS' if gate_pass else 'FAIL'}")
print("="*100)
