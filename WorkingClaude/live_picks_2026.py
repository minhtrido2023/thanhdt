#!/usr/bin/env python3
"""
live_picks_2026.py
==================
Top 10 cổ phiếu hệ thống chọn cho 2026 (v4 Hybrid: 7-axis fundamental + tech multiplier).
+ YTD performance + tech multiplier per stock + weighted portfolio return.

Pipeline:
1. Top 40 by fundamental total_score (latest report each, max_age 400d)
2. Filter by current liquidity Volume_3M_P50 * Close >= 1B VND
3. Compute per-stock tech multiplier from MA50/MA200/MACD/CMB
4. Take top 10 by score, show multiplier
5. Weighted YTD return (multiplier as weight)
"""
import os, subprocess, tempfile
from io import StringIO
import pandas as pd, numpy as np

PROJECT  = "lithe-record-440915-m9"
BQ_BIN   = r"bq"
TODAY    = pd.Timestamp("2026-05-09")
YTD_START = pd.Timestamp("2026-01-01")
MAX_AGE  = 180   # 2 quarters — stale ratings excluded from live picks
TOP_N    = 10
NP_R_THRESHOLD = 0.20
STATE_ALLOC = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}
STATE_NAME = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}

def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

# ─── Per-stock technical multiplier (same as v4) ────────────────────────────
def tech_multiplier(close, ma50, ma200, macd_diff, cmb_bottom_5d, np_r):
    if pd.isna(close) or pd.isna(ma200): return 1.0
    md = macd_diff if pd.notna(macd_diff) else 0.0
    above_200 = close > ma200
    above_50  = (close > ma50) if pd.notna(ma50) else above_200
    has_growth = (np_r is not None) and (not pd.isna(np_r)) and (np_r >= NP_R_THRESHOLD)
    if above_200:
        if above_50 and md > 0:
            return 1.5 if has_growth else 1.0
        return 0.7
    signals = int(above_50) + int(md > 0)
    if signals == 0:   base = 0.1
    elif signals == 1: base = 0.4
    else:              base = 0.8
    if cmb_bottom_5d:
        base = min(0.9, base + 0.1)
    return base

# ─── Load latest ratings ────────────────────────────────────────────────────
df = pd.read_csv("data/fundamental_rating_all.csv", parse_dates=["time"])
cutoff = TODAY - pd.Timedelta(days=MAX_AGE)
valid = df[(df["time"] <= TODAY) & (df["time"] >= cutoff)]
latest = valid.sort_values("time").groupby("ticker").tail(1)

candidates = latest.sort_values("total_score", ascending=False).head(40).reset_index(drop=True)
print(f"Live picks as of {TODAY.date()}:")
print(f"  Universe: {len(latest):,} tickers with rating < {MAX_AGE}d old")
print(f"  Top 40 candidates by fundamental score, will filter by liquidity then take top {TOP_N}")

# ─── Current liquidity check ────────────────────────────────────────────────
cand_tickers = candidates["ticker"].tolist()
liq_sql = f"""
WITH latest_dates AS (
  SELECT ticker, MAX(time) AS time
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker IN UNNEST([{",".join(f'"{t}"' for t in cand_tickers)}])
  GROUP BY ticker
)
SELECT t.ticker, t.time AS px_date, t.Close, t.MA50, t.MA200, t.D_MACDdiff,
       t.Volume_3M_P50 * t.Close AS tv_now
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
JOIN latest_dates USING(ticker, time)
"""
print("\nPulling current liquidity + tech indicators ...")
liq = bq_query(liq_sql, "liq")
liq["tv_now_B"] = liq["tv_now"] / 1e9

# ─── Pull D_CMB_Peak_T1 last 5 days for each candidate ───────────────────────
cmb_sql = f"""
SELECT ticker, time, D_CMB_Peak_T1
FROM `lithe-record-440915-m9.tav2_bq.ticker`
WHERE ticker IN UNNEST([{",".join(f'"{t}"' for t in cand_tickers)}])
  AND time >= DATE_SUB("{TODAY.date()}", INTERVAL 14 DAY)
  AND D_CMB_Peak_T1 IS NOT NULL
"""
print("Pulling CMB peak signal (last 14 days) ...")
cmb = bq_query(cmb_sql, "cmb")
cmb_bottom_5d = {}
if not cmb.empty and "time" in cmb.columns:
    cmb["time"] = pd.to_datetime(cmb["time"])
    for tk, g in cmb.groupby("ticker"):
        recent5 = g.sort_values("time").tail(5)
        cmb_bottom_5d[tk] = bool((recent5["D_CMB_Peak_T1"] == -1).any())
print(f"  {sum(cmb_bottom_5d.values())} tickers with CMB bottom signal in last 5 days")

# Merge tech indicators into candidates
candidates = candidates.merge(
    liq[["ticker","tv_now_B","Close","MA50","MA200","D_MACDdiff","px_date"]],
    on="ticker", how="left")

# Liquidity filter
illiq = candidates[candidates["tv_now_B"] < 1.0]
if len(illiq) > 0:
    print(f"  Dropped {len(illiq)} illiquid: "
          + ", ".join(f"{r['ticker']}({r['tv_now_B']:.2f}B)" for _, r in illiq.iterrows()))
candidates = candidates[candidates["tv_now_B"] >= 1.0].reset_index(drop=True)

# Compute tech multiplier for each
candidates["tech_mult"] = candidates.apply(
    lambda r: tech_multiplier(
        r["Close"], r["MA50"], r["MA200"], r["D_MACDdiff"],
        cmb_bottom_5d.get(r["ticker"], False),
        r.get("NP_R")
    ), axis=1
)

top = candidates.head(TOP_N).reset_index(drop=True)
print(f"  {len(top)} tickers passed liquidity filter, taking top {TOP_N}")

# ─── Pull YTD prices ────────────────────────────────────────────────────────
tickers_list = top["ticker"].tolist()
tickers_sql = ",".join(f'"{t}"' for t in tickers_list + ["VNINDEX"])
sql = f"""
SELECT t.ticker, t.time, t.Close
FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
WHERE t.ticker IN UNNEST([{tickers_sql}])
  AND t.time >= "2025-12-25"
ORDER BY t.ticker, t.time
"""
print("\nPulling YTD prices ...")
prices = bq_query(sql, "ytd")
prices["time"] = pd.to_datetime(prices["time"])

def ytd_return(t):
    g = prices[prices["ticker"]==t].sort_values("time")
    if g.empty: return None, None, None, None
    pre = g[g["time"] < YTD_START]
    post = g[g["time"] >= YTD_START]
    if pre.empty or post.empty: return None, None, None, None
    p0 = pre["Close"].iloc[-1]
    p1 = post["Close"].iloc[-1]
    last_d = post["time"].iloc[-1]
    return p0, p1, (p1/p0 - 1) * 100, last_d

vni_p0, vni_p1, vni_ret, vni_d = ytd_return("VNINDEX")
print(f"\nVNINDEX YTD: {vni_p0:.2f} -> {vni_p1:.2f} = {vni_ret:+.2f}% (as of {vni_d.date()})")

# ─── Current 5-state ────────────────────────────────────────────────────────
state_df = pd.read_csv("data/vnindex_state_history.csv", parse_dates=["time"]).sort_values("time")
state_today = state_df[state_df["time"] <= TODAY].iloc[-1]
sc = int(state_today["state"]); sn = state_today["state_name"]
alloc = STATE_ALLOC[sc]
print(f"Current 5-state ({state_today['time'].date()}): {sn} -> total allocation {alloc*100:.0f}%")

# ─── Build output ───────────────────────────────────────────────────────────
print(f"\n{'='*150}")
print(f"  Rank Tkr   Q       ICB   Score  Q   St  Cs  Sh  Gr  H   V    Mult  NP%   above200/MA50/MACD  TV(B) | Px2025  Latest  YTD%   vsVNI")
print(f"  {'-'*150}")
ytd_rets = []; mults = []; rows = []
for i, r in top.iterrows():
    tk = r["ticker"]
    p0, p1, ret, last_d = ytd_return(tk)
    rel = ret - vni_ret if ret is not None else None
    ytd_rets.append(ret); mults.append(r["tech_mult"])
    icb = str(int(r["ICB_Code"])) if pd.notna(r.get("ICB_Code")) else "?"
    np_r_pct = (r.get("NP_R", float("nan")) * 100)
    above200 = "Y" if (pd.notna(r["Close"]) and pd.notna(r["MA200"]) and r["Close"] > r["MA200"]) else "N"
    above50  = "Y" if (pd.notna(r["Close"]) and pd.notna(r["MA50"]) and r["Close"] > r["MA50"]) else "N"
    macd     = "+" if (pd.notna(r["D_MACDdiff"]) and r["D_MACDdiff"] > 0) else "-"
    rows.append({
        "rank": i+1, "ticker": tk, "quarter": r["quarter"], "ICB": icb,
        "score": r["total_score"], "tier": r["tier"], "tech_mult": r["tech_mult"],
        "Q": r["score_quality"], "St": r["score_stability"], "Cs": r["score_cash"],
        "Sh": r["score_shareholder"],
        "Gr": r["score_growth"], "H": r["score_health"], "V": r["score_valuation"],
        "NP_R_pct": np_r_pct, "above_MA200": above200, "above_MA50": above50, "MACD": macd,
        "tv_now_B": r["tv_now_B"],
        "px_2025_close": p0, "px_latest": p1,
        "ytd_pct": ret, "vs_vnindex_pp": rel,
    })
    if ret is not None:
        print(f"  {i+1:>4} {tk:<5} {r['quarter']:<7} {icb:<5} "
              f"{r['total_score']:>5.3f} "
              f"{r['score_quality']:.2f} {r['score_stability']:.2f} "
              f"{r['score_cash']:.2f} {r['score_shareholder']:.2f} "
              f"{r['score_growth']:.2f} {r['score_health']:.2f} "
              f"{r['score_valuation']:.2f} {r['tech_mult']:>4.2f}  "
              f"{np_r_pct:>+5.0f}%   {above200}/{above50}/{macd}        "
              f"{r['tv_now_B']:>5.1f} | "
              f"{p0:>7.0f} {p1:>6.0f} {ret:>+5.1f}% {rel:>+5.1f}pp")
    else:
        print(f"  {i+1:>4} {tk:<5} {r['quarter']:<7} {icb:<5} {r['total_score']:>5.3f} (no YTD price data)")

# ─── Aggregate (equal-weight + tech-weighted) ───────────────────────────────
clean = [(t, x) for t, x in zip(mults, ytd_rets) if x is not None]
if clean:
    rets = np.array([x for _, x in clean])
    mwts = np.array([t for t, _ in clean])
    eq_avg = rets.mean()
    # Tech-weighted: sum(mult * ret) / sum(mult)
    tech_avg = (mwts * rets).sum() / mwts.sum() if mwts.sum() > 0 else 0
    # Effective allocation (sum of multipliers / N)
    eff_alloc_pct = mwts.mean() * 100   # average multiplier (vs. baseline 1.0 = 100%)

    print(f"  {'-'*148}")
    print(f"  Equal-weight Top-{TOP_N} YTD: {eq_avg:+.2f}%   |   VNI {vni_ret:+.2f}%   = {eq_avg-vni_ret:+.2f}pp alpha")
    print(f"  Tech-weighted YTD:         {tech_avg:+.2f}%   ({len(clean)} stocks, "
          f"avg multiplier {mwts.mean():.2f})")
    # Apply 5-state overlay: total invested = state_alloc * (avg_mult / 1.0 base)
    overlay_invested = alloc * mwts.mean()
    overlay_invested = min(overlay_invested, 1.3)
    cash_yield = max(0, 1 - overlay_invested) * 0.06 * 130/365   # cash for ~130 days YTD
    overlay_ret = tech_avg * overlay_invested + cash_yield * 100
    print(f"  With 5-state overlay ({sn}, base {alloc*100:.0f}%): "
          f"effective stocks {overlay_invested*100:.0f}%, rest in cash@6%/yr  "
          f"-> net YTD ~ {overlay_ret:+.2f}%")

pd.DataFrame(rows).to_csv("data/live_picks_2026.csv", index=False)
print(f"\nSaved -> live_picks_2026.csv")
