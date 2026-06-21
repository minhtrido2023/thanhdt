#!/usr/bin/env python3
"""
backtest_fundamental_v4.py
==========================
Hybrid B+C: Fundamental as universe filter, Technical as position-sizing weight,
5-state market overlay for total allocation.

Strategy (v4, 2-signal reversal + CMB bonus):
- Universe: Top-N by 7-axis fundamental score (quarterly rebalance, Top-50 default)
- Per-stock technical multiplier (0.1 .. 1.5x):
    Above MA200:
      * uptrend (above MA50, MACD+) + growth >= 70%ile  -> 1.5x  (priority)
      * uptrend                                          -> 1.0x
      * consolidation / pullback within uptrend          -> 0.7x
    Below MA200 — base on 2 reversal signals (above_MA50, MACD>0):
      * 0 signals (distribution) -> 0.1x   (avoid, gãy trend)
      * 1 signal                 -> 0.4x   (light, building)
      * 2 signals                -> 0.8x   (CONFIRMED reversal — buy more)
      Bonus: +0.1 if CMB bottom signal in last 5 days (capped at 0.9)
- Portfolio weight = multiplier / sum(multipliers) within universe
- 5-state market overlay applied on top (CRISIS=0%, BEAR=20%, NEUTRAL=70%, BULL=100%, EX-BULL=130%)

Compare to:
- Combo Top-N (v3, equal-weight, with overlay)
- VNINDEX B&H

Output:
- backtest_fundamental_v4.csv  (NAV)
- backtest_fundamental_v4.png  (chart)
- backtest_fundamental_v4_isoos.csv (IS/OOS metrics)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT   = "lithe-record-440915-m9"
BQ_BIN    = r"bq"
PRICE_CSV = "data/fundamental_rating_prices.csv"
TECH_CSV  = "data/fundamental_rating_tech.csv"   # cache for tech indicators
START     = "2015-04-01"
END       = "2025-04-01"
SPLIT     = "2020-04-01"
TC        = 0.001
DEPOSIT   = 0.06
BORROW    = 0.10
STATE_ALLOC = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}
TOP_N_LIST = [15, 20, 30, 40, 50, 75]   # sweep
TOP_N_DEFAULT = 50       # the focus run for distribution + plot
NP_R_THRESHOLD = 0.20    # NP YoY growth flag for "priority" 1.5x bucket
MAX_AGE   = 150          # days for rating freshness

# ─── Style ───────────────────────────────────────────────────────────────────
DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
GREEN="#4ecb71"; BLUE="#4fa3e0"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"
plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.4,
    "font.family":"DejaVu Sans",
})

def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=20000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

# ─── Load ratings + state + prices ──────────────────────────────────────────
print("Loading ...")
rating = pd.read_csv("data/fundamental_rating_all.csv"); rating["time"] = pd.to_datetime(rating["time"])
state_df = pd.read_csv("data/vnindex_state_history.csv", parse_dates=["time"])
state_df["alloc"] = state_df["state"].map(STATE_ALLOC)
state_df = state_df.set_index("time")[["state","alloc"]].sort_index()
prices = pd.read_csv(PRICE_CSV, parse_dates=["time"])
price_pivot = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
print(f"  rating={len(rating):,} rows, state={len(state_df):,} days, prices={price_pivot.shape}")

# ─── Universe schedule (Top-N by score with max_age) ───────────────────────
rebal_qtr = pd.date_range(START, END, freq=pd.DateOffset(months=3))

def select_topN(d, N):
    cutoff = d - pd.Timedelta(days=MAX_AGE)
    valid = rating[(rating["time"] <= d) & (rating["time"] >= cutoff)]
    if valid.empty: return pd.DataFrame()
    latest = valid.sort_values("time").groupby("ticker").tail(1)
    return latest.sort_values("total_score", ascending=False).head(N)

print(f"\nBuilding universe schedules for N in {TOP_N_LIST} ({len(rebal_qtr)} rebals each) ...")
schedules_by_N = {N: {d: select_topN(d, N) for d in rebal_qtr} for N in TOP_N_LIST}
schedules = schedules_by_N[TOP_N_DEFAULT]   # alias for default

# Union of tickers across all N (driven by largest N)
N_max = max(TOP_N_LIST)
all_tickers = sorted(set(t for d in rebal_qtr for t in schedules_by_N[N_max][d]["ticker"].tolist()))
print(f"  {len(all_tickers)} unique tickers across all N values")

# ─── Pull tech indicators (cached) ──────────────────────────────────────────
need_pull = True
if os.path.exists(TECH_CSV):
    tech_cached = pd.read_csv(TECH_CSV, parse_dates=["time"])
    cached_tk = set(tech_cached["ticker"].unique())
    missing = set(all_tickers) - cached_tk
    if not missing:
        print(f"  Using cached tech indicators ({len(cached_tk)} tickers)")
        tech_df = tech_cached
        need_pull = False
    else:
        print(f"  Cache has {len(cached_tk)} tickers, need {len(missing)} more")

if need_pull:
    print(f"Pulling tech indicators for {len(all_tickers)} tickers ...")
    tickers_sql = ",".join(f'"{t}"' for t in all_tickers)
    sql = f"""
    SELECT t.ticker, t.time, t.Close, t.MA50, t.MA200,
           t.D_MACDdiff, t.D_CMB_Peak_T1
    FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
    WHERE t.ticker IN UNNEST([{tickers_sql}])
      AND t.time BETWEEN "{START}" AND "{(pd.Timestamp(END) + pd.Timedelta(days=10)).date()}"
    """
    tech_df = bq_query(sql, "tech")
    tech_df["time"] = pd.to_datetime(tech_df["time"])
    tech_df.to_csv(TECH_CSV, index=False)
    print(f"  Cached {len(tech_df):,} rows -> {TECH_CSV}")

# Pivot tech indicators by ticker for fast lookup
tech_lookup = {}
for col in ["Close","MA50","MA200","D_MACDdiff","D_CMB_Peak_T1"]:
    tech_lookup[col] = tech_df.pivot_table(index="time", columns="ticker", values=col, aggfunc="last").sort_index()

# ─── Per-stock technical multiplier ─────────────────────────────────────────
def tech_multiplier(close, ma50, ma200, macd_diff, cmb_bottom_5d, np_r):
    """Returns multiplier in [0.1 .. 1.5].
    Growth flag uses NP_R (NP YoY = NP_P0/NP_P4 - 1) >= 0.20 directly."""
    if pd.isna(close) or pd.isna(ma200):
        return 1.0  # neutral if no data

    md = macd_diff if pd.notna(macd_diff) else 0.0
    above_200 = close > ma200
    above_50  = (close > ma50) if pd.notna(ma50) else above_200
    has_growth = (np_r is not None) and (not pd.isna(np_r)) and (np_r >= NP_R_THRESHOLD)

    if above_200:
        if above_50 and md > 0:
            return 1.5 if has_growth else 1.0   # healthy uptrend
        return 0.7   # consolidation / pullback within uptrend

    # Below MA200 — base on 2 reversal signals (above_MA50, MACD>0)
    signals = int(above_50) + int(md > 0)
    if signals == 0:   base = 0.1   # distribution
    elif signals == 1: base = 0.4   # 1 signal, building
    else:              base = 0.8   # 2 signals — CONFIRMED reversal, buy more
    # Bonus: CMB bottom in last 5 days
    if cmb_bottom_5d:
        base = min(0.9, base + 0.1)
    return base

# Helper: get latest tech indicator values on/before rebal date,
# plus a 5-day window check for CMB bottom signal.
def latest_tech_at(d, ticker):
    out = {}
    for col, pv in tech_lookup.items():
        if ticker not in pv.columns:
            out[col] = float("nan")
            continue
        s = pv[ticker].loc[:d].dropna()
        out[col] = s.iloc[-1] if len(s) else float("nan")
    # CMB bottom signal in last 5 trading days
    cmb_pv = tech_lookup.get("D_CMB_Peak_T1")
    if cmb_pv is not None and ticker in cmb_pv.columns:
        recent = cmb_pv[ticker].loc[:d].dropna().tail(5)
        out["CMB_bottom_5d"] = bool((recent == -1).any())
    else:
        out["CMB_bottom_5d"] = False
    return out

# ─── NAV simulation: weighted basket ────────────────────────────────────────
def simulate_weighted(rebal_dates, schedules, use_tech_mult=True):
    records = []; nav = 1.0
    weight_log = []   # for analysis: weights per rebal

    for i in range(len(rebal_dates) - 1):
        d_curr, d_next = rebal_dates[i], rebal_dates[i+1]
        sched = schedules[d_curr]
        if sched.empty:
            records.append((d_curr, nav)); continue

        # Compute per-stock multiplier
        if use_tech_mult:
            mults = {}
            for _, r in sched.iterrows():
                tk = r["ticker"]
                tech = latest_tech_at(d_curr, tk)
                m = tech_multiplier(tech["Close"], tech["MA50"], tech["MA200"],
                                     tech["D_MACDdiff"], tech.get("CMB_bottom_5d", False),
                                     r.get("NP_R"))
                mults[tk] = m
        else:
            mults = {r["ticker"]: 1.0 for _, r in sched.iterrows()}

        weight_log.append((d_curr, mults.copy()))

        # TC at rebal
        tc_cost = TC if i == 0 else 2 * TC
        nav *= (1 - tc_cost)

        # Get period prices
        period = price_pivot.loc[d_curr:d_next]
        if period.empty:
            records.append((d_curr, nav)); continue
        first_row = period.iloc[0]
        valid_tk = [t for t in mults if t in first_row.index and pd.notna(first_row[t])]
        if not valid_tk:
            records.append((d_curr, nav)); continue

        # Normalize multipliers across valid tickers (sum to 1.0)
        wseries = pd.Series({t: mults[t] for t in valid_tk})
        total_mult = wseries.sum()
        if total_mult <= 0:
            records.append((d_curr, nav)); continue
        weights = wseries / total_mult

        # Daily portfolio path = weighted sum of normalized prices
        sub = period[valid_tk].ffill()
        norm = sub.div(sub.iloc[0])    # each ticker normalized to 1.0 at start
        port = (norm * weights).sum(axis=1)

        for d, p in port.items():
            records.append((d, nav * p))
        nav = nav * port.iloc[-1]

    out = pd.DataFrame(records, columns=["time","nav"]).drop_duplicates("time", keep="last").sort_values("time").set_index("time")
    return out, weight_log

def apply_overlay(nav_basic):
    s = nav_basic["nav"].copy()
    r_stock = s.pct_change().fillna(0).values
    w = state_df["alloc"].reindex(s.index).ffill().fillna(0.7).values
    r_cash_d   = DEPOSIT / 365
    r_borrow_d = BORROW / 365
    new_nav = np.zeros(len(s)); new_nav[0] = 1.0
    prev_w = w[0]
    for i in range(1, len(s)):
        wt, rt = w[i], r_stock[i]
        cash_part   = max(0.0, 1 - wt) * r_cash_d
        margin_part = max(0.0, wt - 1) * r_borrow_d
        dw = abs(wt - prev_w)
        tc_cost = dw * TC if dw > 0.03 else 0.0
        new_nav[i] = new_nav[i-1] * (1 + wt*rt + cash_part - margin_part - tc_cost)
        prev_w = wt
    return pd.DataFrame({"nav": new_nav}, index=s.index)

# ─── Run strategies ─────────────────────────────────────────────────────────
print("\nSimulating Top-N sweep ...")
sweep_results = {}    # N -> {baseline_basic, baseline_overlay, v4_basic, v4_overlay}
weight_log_default = None
for N in TOP_N_LIST:
    sched_N = schedules_by_N[N]
    nb_basic, _ = simulate_weighted(rebal_qtr, sched_N, use_tech_mult=False)
    nv_basic, wlog = simulate_weighted(rebal_qtr, sched_N, use_tech_mult=True)
    sweep_results[N] = {
        "baseline_basic":   nb_basic,
        "baseline_overlay": apply_overlay(nb_basic),
        "v4_basic":         nv_basic,
        "v4_overlay":       apply_overlay(nv_basic),
    }
    if N == TOP_N_DEFAULT:
        weight_log = wlog
    print(f"  Top-{N:>2}: baseline={sweep_results[N]['baseline_overlay']['nav'].iloc[-1]:.2f}x, "
          f"v4={sweep_results[N]['v4_overlay']['nav'].iloc[-1]:.2f}x")

# Aliases for default N
nav_baseline_basic   = sweep_results[TOP_N_DEFAULT]["baseline_basic"]
nav_v4_basic         = sweep_results[TOP_N_DEFAULT]["v4_basic"]
nav_baseline_overlay = sweep_results[TOP_N_DEFAULT]["baseline_overlay"]
nav_v4_overlay       = sweep_results[TOP_N_DEFAULT]["v4_overlay"]

# VNINDEX B&H
vni = pd.read_csv("data/VNINDEX.csv", parse_dates=["time"], usecols=["time","ticker","Close"])
vni = vni[vni["ticker"]=="VNINDEX"][["time","Close"]].set_index("time").sort_index().loc[START:pd.Timestamp(END)+pd.Timedelta(days=10)]
vni_nav = pd.DataFrame({"nav": vni["Close"] / vni["Close"].iloc[0]})

# ─── Metrics + IS/OOS ───────────────────────────────────────────────────────
def metrics(nav_series, start_d=None, end_d=None):
    s = nav_series["nav"].dropna()
    if start_d:
        s = s.loc[start_d:]; s = s / s.iloc[0]
    if end_d: s = s.loc[:end_d]
    if len(s) < 2: return None
    days = (s.index[-1] - s.index[0]).days
    years = days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/years) - 1
    daily_ret = s.pct_change().dropna()
    spy = len(daily_ret) / years
    sharpe = daily_ret.mean() / daily_ret.std() * np.sqrt(spy) if daily_ret.std() > 0 else 0
    rolling_max = s.expanding().max(); dd = s / rolling_max - 1
    maxdd = dd.min(); calmar = cagr / abs(maxdd) if maxdd < 0 else np.nan
    return dict(cagr=cagr, sharpe=sharpe, maxdd=maxdd, calmar=calmar, final=s.iloc[-1])

strategies = {
    f"Baseline Top-{TOP_N_DEFAULT} (no tech, no overlay)":  nav_baseline_basic,
    f"v4 Tech-weighted Top-{TOP_N_DEFAULT} (no overlay)":   nav_v4_basic,
    f"Baseline Top-{TOP_N_DEFAULT} + Overlay":              nav_baseline_overlay,
    f"v4 Tech-weighted Top-{TOP_N_DEFAULT} + Overlay":      nav_v4_overlay,
    "VNINDEX B&H":                                          vni_nav,
}

print(f"\n=== Performance Comparison (Full + IS + OOS) ===")
print(f"  {'Strategy':<48}{'Window':<5}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}")
print("  " + "-"*88)
isoos_rows = []
for name, nav in strategies.items():
    for window, sd, ed in [("Full", START, END), ("IS", START, SPLIT), ("OOS", SPLIT, END)]:
        m = metrics(nav, sd, ed)
        if m is None: continue
        isoos_rows.append(dict(strategy=name, window=window, **m))
        print(f"  {name:<48}{window:<5}{m['cagr']*100:>7.2f}%{m['sharpe']:>8.2f}"
              f"{m['maxdd']*100:>7.1f}%{m['calmar']:>8.2f}")
    print()

pd.DataFrame(isoos_rows).to_csv("data/backtest_fundamental_v4_isoos.csv", index=False)

# ─── Top-N sweep summary ────────────────────────────────────────────────────
print("\n=== Top-N Sweep (v4 Tech-weighted + Overlay vs Baseline + Overlay) ===")
print(f"  {'N':>3}  {'Baseline+OL CAGR':>18}  {'v4+OL CAGR':>12}  {'v4+OL MaxDD':>13}  {'v4+OL Calmar':>14}  {'IS CAGR':>9}  {'OOS CAGR':>10}")
print("  " + "-"*100)
sweep_rows = []
for N in TOP_N_LIST:
    bl = sweep_results[N]["baseline_overlay"]
    v4 = sweep_results[N]["v4_overlay"]
    m_bl = metrics(bl)
    m_v4 = metrics(v4)
    m_v4_is  = metrics(v4, START, SPLIT)
    m_v4_oos = metrics(v4, SPLIT, END)
    sweep_rows.append(dict(N=N, baseline_cagr=m_bl["cagr"], v4_cagr=m_v4["cagr"],
                           v4_maxdd=m_v4["maxdd"], v4_calmar=m_v4["calmar"],
                           v4_is_cagr=m_v4_is["cagr"], v4_oos_cagr=m_v4_oos["cagr"]))
    print(f"  {N:>3}  {m_bl['cagr']*100:>17.2f}%  {m_v4['cagr']*100:>11.2f}%  "
          f"{m_v4['maxdd']*100:>12.1f}%  {m_v4['calmar']:>14.2f}  "
          f"{m_v4_is['cagr']*100:>8.2f}%  {m_v4_oos['cagr']*100:>9.2f}%")
pd.DataFrame(sweep_rows).to_csv("data/backtest_fundamental_v4_sweep.csv", index=False)

# ─── Save NAVs ──────────────────────────────────────────────────────────────
combo = pd.concat([s["nav"].rename(name) for name, s in strategies.items()], axis=1).sort_index()
combo.to_csv("data/backtest_fundamental_v4.csv")

# ─── Plot ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 1, figsize=(15, 11), gridspec_kw={"height_ratios":[3, 1.3]})
COLORS = [BLUE, GREEN, ORANGE, PURPLE, "white"]
ax = axes[0]
for (name, nav), col in zip(strategies.items(), COLORS):
    s = nav["nav"]; m = metrics(nav)
    ls = "--" if "VNINDEX" in name else "-"
    ax.plot(s.index, s.values,
            label=f"{name}  ({m['final']:.2f}x, CAGR={m['cagr']*100:.1f}%, MaxDD={m['maxdd']*100:.0f}%)",
            color=col, linewidth=1.8, linestyle=ls)
ax.axvline(pd.Timestamp(SPLIT), color=YELLOW, linestyle=":", alpha=0.7)
ax.set_yscale("log"); ax.legend(loc="upper left", fontsize=9, framealpha=0.85)
ax.grid(True, which="both", alpha=0.3); ax.set_ylabel("NAV (log)")
ax.set_title(f"v4 Hybrid — Fundamental Top-{TOP_N_DEFAULT} + Technical position-sizing + 5-state overlay",
             fontsize=14, pad=10)

ax = axes[1]
for (name, nav), col in zip(strategies.items(), COLORS):
    s = nav["nav"]; dd = s / s.expanding().max() - 1
    ls = "--" if "VNINDEX" in name else "-"
    ax.fill_between(dd.index, dd.values * 100, 0, color=col, alpha=0.20)
    ax.plot(dd.index, dd.values * 100, color=col, linewidth=1.0, linestyle=ls,
            label=f"{name} (MaxDD={dd.min()*100:.1f}%)")
ax.set_ylabel("Drawdown (%)"); ax.set_title("Drawdown comparison")
ax.legend(loc="lower left", fontsize=8.5, ncol=2, framealpha=0.85)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("backtest_fundamental_v4.png", dpi=120, facecolor=DARK_BG)

# ─── Multiplier distribution audit ──────────────────────────────────────────
print("\n=== Tech multiplier distribution across rebals ===")
all_mults = []
for d, mults in weight_log:
    all_mults.extend(mults.values())
m_arr = np.array(all_mults)
print(f"  Total multipliers logged: {len(m_arr):,}")
print(f"  Mean: {m_arr.mean():.2f}, Median: {np.median(m_arr):.2f}")
buckets = [(0.1, "0.1 (distribution)"), (0.2, "0.2 (distribution + CMB bot)"),
           (0.4, "0.4 (1 signal, building)"), (0.5, "0.5 (1 signal + CMB bot)"),
           (0.8, "0.8 (2 signals — CONFIRMED reversal)"),
           (0.9, "0.9 (2 signals + CMB bot, strong)"),
           (0.7, "0.7 (consolidation above MA200)"),
           (1.0, "1.0 (uptrend)"), (1.5, "1.5 (priority: uptrend+growth)")]
for v, label in buckets:
    n = (np.abs(m_arr - v) < 0.01).sum()
    print(f"    {label:<22}: {n:>5,} ({100*n/len(m_arr):.1f}%)")
print(f"\nSaved -> backtest_fundamental_v4.csv, .png, _isoos.csv")
