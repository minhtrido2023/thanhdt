#!/usr/bin/env python3
"""
backtest_fast_riser_ts.py
=========================
Hypothesis: stocks that rise too fast in a short time are more likely
to have sharp pullbacks — apply a 15% trailing stop ONLY to those.

Definition of "fast riser":
  gain of >= GAIN_THRESHOLD% achieved within <= SPEED_DAYS trading days.

Exit logic (only for fast risers):
  - Track peak Close since first buy
  - Once fast-riser condition is met, activate trailing stop
  - If Close falls below peak * (1 - TRAIL_PCT) -> sell at Open[D+1]
  - For non-fast-risers: keep original exit

Execution model (realistic):
  - Signal on Close[D]  -> fill at Open[D+1]
  - Fallback to Close[D] if D+1 missing

Grid:
  GAIN_THRESHOLD : [20%, 30%, 40%, 50%, 60%]
  SPEED_DAYS     : [15, 20, 30, 45, 60]
  TRAIL_PCT      : fixed 15% (user hypothesis)

Output:
  1. Console: position-level analysis of fast risers
  2. Heatmap chart: PnL delta vs grid
  3. Detail chart: deal-level gains for fast-riser positions
"""

import json
import os
import subprocess
import tempfile
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker

# ── CONFIG ────────────────────────────────────────────────────────────────────
TX_FILE  = "transactions_email_special_2026-04-07_15.14.47.jsonl"
PROJECT  = "lithe-record-440915-m9"
BQ_CHUNK = 150
BQ_BIN   = r"bq"
OUT_IMG  = "backtest_fast_riser_ts.png"
FILTER_FROM = pd.Timestamp("2020-01-01")

TRAIL_PCT = 0.15  # fixed trailing stop: 15% from peak

GAIN_GRID  = [0.20, 0.30, 0.40, 0.50, 0.60]   # min gain to qualify as "fast riser"
SPEED_GRID = [15, 20, 30, 45, 60]              # max trading days to reach that gain

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG  = "#0f1117"; PANEL_BG = "#1a1d27"; GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"; BLUE = "#4fa3e0";     GREEN = "#4ecb71"
RED      = "#e05c5c"; YELLOW = "#f0c060";   PURPLE = "#b57bee"
ORANGE   = "#f0904a"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor": GRID_CLR,  "axes.labelcolor": TEXT_CLR,
    "xtick.color": TEXT_CLR,     "ytick.color": TEXT_CLR,
    "text.color": TEXT_CLR,      "grid.color": GRID_CLR,
    "grid.linestyle": "--",      "grid.alpha": 0.5,
    "font.family": "DejaVu Sans",
})

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_jsonl(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df["ymd"] = pd.to_datetime(df["ymd"])
    return df

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(sql)
        tmppath = f.name
    try:
        cmd_str = f'type "{tmppath}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=5000000'
        r = subprocess.run(cmd_str, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try:
            os.unlink(tmppath)
        except OSError:
            pass
    if r.returncode != 0:
        raise RuntimeError(r.stdout[:400] + r.stderr[:400])
    return pd.read_csv(StringIO(r.stdout))

def fmt_b(v):    return f"{v/1e9:+,.2f}B"
def fmt_pct(v):  return f"{v:+.2f}%"

# ── LOAD TRANSACTIONS ─────────────────────────────────────────────────────────
print("Loading transactions ...")
tx = load_jsonl(TX_FILE)
tx.sort_values("ymd", inplace=True)

print("Building closed positions ...")
pos_records = []
for hid, grp in tx.groupby("holding_id"):
    buys  = grp[grp["action"] == "buy"].sort_values("ymd")
    sells = grp[grp["action"] == "sell"].sort_values("ymd")
    if sells.empty:
        continue
    total_inv  = buys["buy_amount"].sum()
    total_proc = sells["sell_amount"].sum()
    total_fees = grp["fee"].sum()
    denom      = total_inv + total_fees
    pos_records.append({
        "holding_id":   hid,
        "ticker":       grp["ticker"].iloc[0],
        "first_buy":    buys["ymd"].min(),
        "last_sell":    sells["ymd"].max(),
        "total_inv":    total_inv,
        "total_proc":   total_proc,
        "total_fees":   total_fees,
        "orig_pnl":     total_proc - denom,
        "orig_pnl_pct": (total_proc / denom - 1) * 100 if denom > 0 else 0.0,
        "buys_df":      buys,
    })

pos_df = pd.DataFrame(pos_records)
pos_df = pos_df[pos_df["first_buy"] >= FILTER_FROM].reset_index(drop=True)
print(f"  {len(pos_df)} closed positions | {pos_df['ticker'].nunique()} tickers")
orig_total_pnl = pos_df["orig_pnl"].sum()

# ── FETCH PRICES FROM BQ ──────────────────────────────────────────────────────
tickers  = pos_df["ticker"].unique().tolist()
date_min = pos_df["first_buy"].min().strftime("%Y-%m-%d")
date_max = pos_df["last_sell"].max().strftime("%Y-%m-%d")
n_chunks = -(-len(tickers) // BQ_CHUNK)
print(f"Fetching prices: {len(tickers)} tickers | {n_chunks} chunks ...")

frames = []
for i in range(0, len(tickers), BQ_CHUNK):
    chunk = tickers[i:i+BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = (f'SELECT t.ticker, t.time, t.Open, t.Close FROM tav2_bq.ticker AS t '
             f'WHERE t.ticker IN ({tstr}) '
             f'AND t.time BETWEEN "{date_min}" AND "{date_max}" '
             f'ORDER BY t.ticker, t.time')
    df = bq_query(sql)
    df["time"] = pd.to_datetime(df["time"])
    frames.append(df)
    print(f"  chunk {i//BQ_CHUNK+1}/{n_chunks}: {len(df):,} rows")

prices_df = pd.concat(frames, ignore_index=True)
print(f"  Total rows: {len(prices_df):,}")

# Build price_map: ticker -> DataFrame(index=date, cols=[Close, Open_next])
price_map = {}
for ticker, grp in prices_df.groupby("ticker"):
    g = grp.sort_values("time").set_index("time")[["Close", "Open"]].copy()
    g["Open_next"] = g["Open"].shift(-1)
    price_map[ticker] = g

# ── CORE: measure each position's "fastest rise" ──────────────────────────────
def measure_position(pos):
    """
    For each position, compute:
      - For each trading day D, the gain since first_buy
      - The fastest day at which gain >= each GAIN_GRID threshold
    Returns a dict keyed by gain_threshold -> trading_days_to_reach (None if never)
    """
    ticker     = pos["ticker"]
    first_buy  = pos["first_buy"]
    last_sell  = pos["last_sell"]
    buys_df    = pos["buys_df"]

    result = {g: None for g in GAIN_GRID}

    if ticker not in price_map:
        return result

    df_px = price_map[ticker]
    try:
        window = df_px.loc[first_buy:last_sell]
    except Exception:
        return result
    if window.empty:
        return result

    buy_list = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr  = 0
    n_buys   = len(buy_list)
    cum_inv  = 0.0
    cum_sh   = 0.0
    trading_day = 0

    for date, row in window.iterrows():
        close = row["Close"]
        if pd.isna(close) or close <= 0:
            continue

        # accumulate buys
        while buy_ptr < n_buys and buy_list[buy_ptr].ymd <= date:
            b = buy_list[buy_ptr]
            if b.adj_price > 0:
                cum_sh  += b.buy_amount / b.adj_price
                cum_inv += b.buy_amount
            buy_ptr += 1

        if cum_sh <= 0:
            continue

        if date == first_buy:
            trading_day = 0
            continue

        trading_day += 1
        avg_cost = cum_inv / cum_sh
        gain_pct = (close / avg_cost) - 1

        for g in GAIN_GRID:
            if result[g] is None and gain_pct >= g:
                result[g] = trading_day

    return result

print("\nMeasuring speed of rise for each position ...")
speed_records = []
for _, pos in pos_df.iterrows():
    r = measure_position(pos)
    r["holding_id"] = pos["holding_id"]
    speed_records.append(r)

speed_df = pd.DataFrame(speed_records).set_index("holding_id")

# Merge speed info into pos_df
pos_df = pos_df.set_index("holding_id")
for g in GAIN_GRID:
    pos_df[f"days_to_{int(g*100)}pct"] = speed_df[g]
pos_df = pos_df.reset_index()

# ── ANALYSIS: how many positions qualify under each threshold? ─────────────────
print("\n=== Fast-Riser Qualification Matrix ===")
print(f"{'':>10}", end="")
for s in SPEED_GRID:
    print(f"  {s:>5}d", end="")
print()
for g in GAIN_GRID:
    col = f"days_to_{int(g*100)}pct"
    print(f"  +{int(g*100):>2}% gain", end="")
    for s in SPEED_GRID:
        n = (pos_df[col] <= s).sum()
        print(f"  {n:>5}", end="")
    print()

# ── SIMULATE: trailing stop for fast risers ────────────────────────────────────
def simulate_fast_riser(pos, gain_thresh, speed_days):
    """
    Apply 15% trailing stop ONLY if position qualifies as fast-riser.
    Fast-riser = gained >= gain_thresh within speed_days trading days.
    """
    ticker    = pos["ticker"]
    first_buy = pos["first_buy"]
    last_sell = pos["last_sell"]
    buys_df   = pos["buys_df"]
    orig_pnl  = pos["orig_pnl"]
    orig_pct  = pos["orig_pnl_pct"]
    total_fees= pos["total_fees"]

    if ticker not in price_map:
        return orig_pnl, orig_pct, "no_data"

    df_px = price_map[ticker]
    try:
        window = df_px.loc[first_buy:last_sell]
    except Exception:
        return orig_pnl, orig_pct, "original"
    if window.empty:
        return orig_pnl, orig_pct, "original"

    buy_list    = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr     = 0
    n_buys      = len(buy_list)
    cum_inv     = 0.0
    cum_sh      = 0.0
    trading_day = 0
    peak_close  = 0.0
    ts_active   = False  # trailing stop activated

    def make_exit(date, close, open_next):
        fill  = open_next if (open_next and not pd.isna(open_next) and open_next > 0) else close
        denom = cum_inv + total_fees
        proc  = fill * cum_sh
        return proc - denom, (proc / denom - 1) * 100

    for date, row in window.iterrows():
        close     = row["Close"]
        open_next = row["Open_next"]

        if pd.isna(close) or close <= 0:
            continue

        while buy_ptr < n_buys and buy_list[buy_ptr].ymd <= date:
            b = buy_list[buy_ptr]
            if b.adj_price > 0:
                cum_sh  += b.buy_amount / b.adj_price
                cum_inv += b.buy_amount
            buy_ptr += 1

        if cum_sh <= 0:
            continue

        if date == first_buy:
            trading_day = 0
            avg_cost = cum_inv / cum_sh
            peak_close = close
            continue

        trading_day += 1
        avg_cost = cum_inv / cum_sh
        gain_pct = (close / avg_cost) - 1

        # Update peak
        if close > peak_close:
            peak_close = close

        # Check if qualifies as fast-riser and activate trailing stop
        if not ts_active and gain_pct >= gain_thresh and trading_day <= speed_days:
            ts_active = True

        # Apply trailing stop if active
        if ts_active:
            stop_price = peak_close * (1 - TRAIL_PCT)
            if close <= stop_price:
                pnl, pct = make_exit(date, close, open_next)
                return pnl, pct, "trailing_stop"

    return orig_pnl, orig_pct, "original"

# ── GRID SEARCH ───────────────────────────────────────────────────────────────
print("\n=== Grid Search: 15% Trailing Stop for Fast Risers ===")
print(f"Original strategy PnL: {fmt_b(orig_total_pnl)}")
print()

grid_results = []
for gain_thresh in GAIN_GRID:
    for speed_days in SPEED_GRID:
        sim_pnls = []
        n_ts_triggered = 0
        ts_pnls  = []
        ts_orig_pnls = []

        for _, pos in pos_df.iterrows():
            pnl, pct, exit_type = simulate_fast_riser(pos, gain_thresh, speed_days)
            sim_pnls.append(pnl)
            if exit_type == "trailing_stop":
                n_ts_triggered += 1
                ts_pnls.append(pnl)
                ts_orig_pnls.append(pos["orig_pnl"])

        total_pnl = sum(sim_pnls)
        delta = total_pnl - orig_total_pnl
        ts_delta = sum(ts_pnls) - sum(ts_orig_pnls) if ts_pnls else 0

        grid_results.append({
            "gain_thresh":    gain_thresh,
            "speed_days":     speed_days,
            "total_pnl":      total_pnl,
            "delta":          delta,
            "delta_pct":      delta / abs(orig_total_pnl) * 100,
            "n_triggered":    n_ts_triggered,
            "ts_delta":       ts_delta,
        })

        print(f"  +{int(gain_thresh*100)}% in {speed_days:2}d -> "
              f"total={fmt_b(total_pnl)} delta={fmt_b(delta)} "
              f"({fmt_pct(delta/abs(orig_total_pnl)*100)}) "
              f"| {n_ts_triggered} stops triggered, TS delta={fmt_b(ts_delta)}")

grid_df = pd.DataFrame(grid_results)
best = grid_df.loc[grid_df["delta"].idxmax()]
print(f"\nBest combo: +{int(best['gain_thresh']*100)}% in {int(best['speed_days'])}d "
      f"-> delta={fmt_b(best['delta'])} ({fmt_pct(best['delta_pct'])})")

# ── POSITION-LEVEL ANALYSIS of fast risers ────────────────────────────────────
# Use the best combo for detailed position analysis
print(f"\n=== Position analysis: +{int(best['gain_thresh']*100)}% in {int(best['speed_days'])}d ===")
best_gain  = best["gain_thresh"]
best_speed = int(best["speed_days"])

detail_rows = []
for _, pos in pos_df.iterrows():
    pnl, pct, exit_type = simulate_fast_riser(pos, best_gain, best_speed)
    detail_rows.append({
        "ticker":    pos["ticker"],
        "first_buy": pos["first_buy"].date(),
        "orig_pnl":  pos["orig_pnl"],
        "sim_pnl":   pnl,
        "delta":     pnl - pos["orig_pnl"],
        "exit_type": exit_type,
        "orig_pct":  pos["orig_pnl_pct"],
        "sim_pct":   pct,
    })

det_df = pd.DataFrame(detail_rows)
ts_hits = det_df[det_df["exit_type"] == "trailing_stop"]
ts_miss = det_df[det_df["exit_type"] != "trailing_stop"]

print(f"  Trailing stop triggered: {len(ts_hits)} positions")
print(f"  PnL delta on triggered:  {fmt_b(ts_hits['delta'].sum())}")
print(f"  Avg orig return:         {ts_hits['orig_pct'].mean():.1f}%")
print(f"  Avg sim return:          {ts_hits['sim_pct'].mean():.1f}%")
print(f"\n  Top 10 biggest delta positions:")
for _, r in ts_hits.sort_values("delta").head(10).iterrows():
    print(f"    {r['ticker']:6s} {str(r['first_buy']):10s} "
          f"orig={fmt_pct(r['orig_pct'])} -> sim={fmt_pct(r['sim_pct'])} "
          f"delta={fmt_b(r['delta'])}")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 12), facecolor=DARK_BG)
gs  = gridspec.GridSpec(2, 3, figure=fig, hspace=0.4, wspace=0.4)

# Panel 1: Heatmap of PnL delta
ax1 = fig.add_subplot(gs[0, :2])
pivot = grid_df.pivot(index="gain_thresh", columns="speed_days", values="delta") / 1e9
g_labels = [f"+{int(g*100)}%" for g in GAIN_GRID]
s_labels  = [f"{s}d" for s in SPEED_GRID]
im = ax1.imshow(pivot.values, cmap="RdYlGn", aspect="auto",
                vmin=-abs(pivot.values).max(), vmax=abs(pivot.values).max())
ax1.set_xticks(range(len(SPEED_GRID)));  ax1.set_xticklabels(s_labels)
ax1.set_yticks(range(len(GAIN_GRID)));   ax1.set_yticklabels(g_labels)
ax1.set_xlabel("Speed window (trading days)", color=TEXT_CLR)
ax1.set_ylabel("Gain threshold", color=TEXT_CLR)
ax1.set_title("PnL Delta vs Original (B VND)\n15% Trailing Stop for Fast Risers",
              color=TEXT_CLR, fontweight="bold")
for i in range(len(GAIN_GRID)):
    for j in range(len(SPEED_GRID)):
        val = pivot.values[i, j]
        color = "black" if abs(val) < abs(pivot.values).max() * 0.5 else "white"
        ax1.text(j, i, f"{val:+.2f}B", ha="center", va="center",
                 fontsize=9, color=color, fontweight="bold")
plt.colorbar(im, ax=ax1, shrink=0.8)

# Panel 2: Number of triggers heatmap
ax2 = fig.add_subplot(gs[0, 2])
pivot_n = grid_df.pivot(index="gain_thresh", columns="speed_days", values="n_triggered")
im2 = ax2.imshow(pivot_n.values, cmap="Blues", aspect="auto")
ax2.set_xticks(range(len(SPEED_GRID)));  ax2.set_xticklabels(s_labels, fontsize=8)
ax2.set_yticks(range(len(GAIN_GRID)));   ax2.set_yticklabels(g_labels, fontsize=8)
ax2.set_title("# Positions with\nTrailing Stop Triggered", color=TEXT_CLR, fontweight="bold")
for i in range(len(GAIN_GRID)):
    for j in range(len(SPEED_GRID)):
        ax2.text(j, i, str(int(pivot_n.values[i, j])),
                 ha="center", va="center", fontsize=9, color="white", fontweight="bold")

# Panel 3: Distribution of returns for fast-riser positions (best combo)
ax3 = fig.add_subplot(gs[1, 0])
if not ts_hits.empty:
    bins = np.linspace(
        min(ts_hits["orig_pct"].min(), ts_hits["sim_pct"].min()) - 5,
        max(ts_hits["orig_pct"].max(), ts_hits["sim_pct"].max()) + 5,
        25
    )
    ax3.hist(ts_hits["orig_pct"], bins=bins, alpha=0.6, color=BLUE, label="Original")
    ax3.hist(ts_hits["sim_pct"],  bins=bins, alpha=0.6, color=ORANGE, label="With TS")
    ax3.axvline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax3.set_xlabel("Return (%)")
    ax3.set_ylabel("Count")
    ax3.set_title(f"Return Distribution\nFast-Riser Positions (best combo)", color=TEXT_CLR)
    ax3.legend(fontsize=8)

# Panel 4: Scatter: original return vs delta, colored by outcome
ax4 = fig.add_subplot(gs[1, 1])
if not ts_hits.empty:
    colors = [GREEN if d >= 0 else RED for d in ts_hits["delta"]]
    ax4.scatter(ts_hits["orig_pct"], ts_hits["delta"] / 1e9, c=colors, alpha=0.7, s=50)
    ax4.axhline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax4.axvline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax4.set_xlabel("Original Return (%)")
    ax4.set_ylabel("PnL Delta (B VND)")
    ax4.set_title("TS cut early = green win\nTS cut runner = red loss",
                  color=TEXT_CLR, fontsize=9)
    n_win = (ts_hits["delta"] >= 0).sum()
    n_lose = (ts_hits["delta"] < 0).sum()
    ax4.text(0.02, 0.98, f"Saved: {n_win} | Cut runners: {n_lose}",
             transform=ax4.transAxes, va="top", fontsize=8, color=TEXT_CLR)

# Panel 5: Bar chart comparing PnL
ax5 = fig.add_subplot(gs[1, 2])
labels  = ["Original"] + [f"+{int(g*100)}%/{s}d"
                           for g in [best_gain] for s in SPEED_GRID]
best_rows = grid_df[grid_df["gain_thresh"] == best_gain].sort_values("speed_days")
vals = [orig_total_pnl / 1e9] + list(best_rows["total_pnl"] / 1e9)
bar_labels = ["Original"] + [f"{s}d" for s in SPEED_GRID]
bar_colors = [BLUE] + [GREEN if v > orig_total_pnl/1e9 else RED for v in vals[1:]]
bars = ax5.bar(range(len(bar_labels)), vals, color=bar_colors, alpha=0.85)
ax5.set_xticks(range(len(bar_labels)))
ax5.set_xticklabels(bar_labels, fontsize=8)
ax5.set_ylabel("Total PnL (B VND)")
ax5.set_title(f"Total PnL: +{int(best_gain*100)}% threshold\nvs. speed window",
              color=TEXT_CLR, fontweight="bold")
for bar, val in zip(bars, vals):
    ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"{val:.1f}B", ha="center", va="bottom", fontsize=7, color=TEXT_CLR)

fig.suptitle("Fast-Riser Trailing Stop (15%) — Only applied when stock rose sharply",
             color=TEXT_CLR, fontsize=14, fontweight="bold", y=0.98)

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: {OUT_IMG}")
