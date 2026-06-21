#!/usr/bin/env python3
"""
backtest_tech_sell.py
=====================
Test whether pure technical sell signals can outperform the current
strategy's exit timing on closed positions (2020-present).

For each closed position we:
  1. Replay each day from first_buy to last_sell
  2. Check if each technical signal fires (after MIN_HOLD_DAYS)
  3. If signal fires BEFORE the original exit -> exit at Open[D+1]
  4. If no signal fires -> keep original exit

Execution: signal on Close[D] -> fill at Open[D+1] (realistic)

Technical signals tested:
  S1  RSI overbought:         D_RSI > 0.70
  S2  RSI peak reversal:      D_RSI > 0.60 AND D_RSI < D_RSI_T1 (RSI falling)
  S3  MACD cross negative:    D_MACDdiff crosses below 0 (was positive)
  S4  MA10 death cross:       MA10 < MA20 AND MA10_T1 >= MA20_T1
  S5  CMB weekly top:         D_CMB_Peak_T1 > 0.5
  S6  High-volume red candle: Volume > 2x P50 AND Close < Open
  S7  Close cross below VAP1M:Close < VAP1M AND Close_T1 >= VAP1M
  S8  RSI+MACD composite:     D_RSI > 0.62 AND D_MACDdiff < 0
  S9  RSI+MACD+CMB:           D_RSI > 0.60 AND D_MACDdiff < 0 AND D_CMB_Peak_T1 > 0.3

MIN_HOLD_DAYS = 10 trading days before any signal can fire
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

# ── CONFIG ────────────────────────────────────────────────────────────────────
TX_FILE      = "transactions_email_special_2026-04-07_15.14.47.jsonl"
PROJECT      = "lithe-record-440915-m9"
BQ_CHUNK     = 120
BQ_BIN       = r"bq"
OUT_IMG      = "backtest_tech_sell.png"
FILTER_FROM  = pd.Timestamp("2020-01-01")
MIN_HOLD     = 10   # minimum trading days before any sell signal can fire

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG = "#0f1117"; PANEL_BG = "#1a1d27"; GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"; BLUE = "#4fa3e0"; GREEN = "#4ecb71"
RED = "#e05c5c"; YELLOW = "#f0c060"; ORANGE = "#f0904a"; PURPLE = "#b57bee"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor": GRID_CLR,  "axes.labelcolor": TEXT_CLR,
    "xtick.color": TEXT_CLR,     "ytick.color": TEXT_CLR,
    "text.color": TEXT_CLR,      "grid.color": GRID_CLR,
    "grid.linestyle": "--",      "grid.alpha": 0.5,
    "font.family": "DejaVu Sans",
})

# ── SIGNAL DEFINITIONS ────────────────────────────────────────────────────────
# Each signal is a function(row, prev_row) -> bool
# row = current day Series, prev_row = previous day Series (can be None on day 1)
SIGNALS = {
    "S1_RSI_OB":      lambda r, p: r.D_RSI > 0.70,
    "S2_RSI_Peak":    lambda r, p: r.D_RSI > 0.60 and p is not None and r.D_RSI < p.D_RSI,
    "S3_MACD_Cross":  lambda r, p: r.D_MACDdiff < 0 and p is not None and p.D_MACDdiff >= 0,
    "S4_MA_DeathX":   lambda r, p: (r.MA10 < r.MA20 and p is not None
                                     and p.MA10 >= p.MA20),
    "S5_CMB_Top":     lambda r, p: r.D_CMB_Peak_T1 > 0.50,
    "S6_VolRed":      lambda r, p: (r.Volume > 2.0 * r.Volume_3M_P50
                                     and r.Close < r.Open),
    "S7_VAP_Break":   lambda r, p: (r.Close < r.VAP1M and p is not None
                                     and p.Close >= p.VAP1M),
    "S8_RSI_MACD":    lambda r, p: r.D_RSI > 0.62 and r.D_MACDdiff < 0,
    "S9_RSI_MACD_CMB":lambda r, p: (r.D_RSI > 0.60 and r.D_MACDdiff < 0
                                     and r.D_CMB_Peak_T1 > 0.30),
}

SIGNAL_LABELS = {
    "S1_RSI_OB":       "S1: RSI > 0.70",
    "S2_RSI_Peak":     "S2: RSI Falling (>0.60)",
    "S3_MACD_Cross":   "S3: MACD Cross Neg",
    "S4_MA_DeathX":    "S4: MA10 x MA20 Death",
    "S5_CMB_Top":      "S5: CMB Weekly Top",
    "S6_VolRed":       "S6: Vol Spike + Red",
    "S7_VAP_Break":    "S7: Close < VAP1M",
    "S8_RSI_MACD":     "S8: RSI+MACD Combo",
    "S9_RSI_MACD_CMB": "S9: RSI+MACD+CMB",
}

# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_jsonl(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows); df["ymd"] = pd.to_datetime(df["ymd"])
    return df

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sql', delete=False, encoding='utf-8') as f:
        f.write(sql); tmppath = f.name
    try:
        cmd = f'type "{tmppath}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=5000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    finally:
        try: os.unlink(tmppath)
        except OSError: pass
    if r.returncode != 0:
        raise RuntimeError(r.stdout[:400] + r.stderr[:400])
    return pd.read_csv(StringIO(r.stdout))

def fmt_b(v):   return f"{v/1e9:+,.2f}B"
def fmt_pct(v): return f"{v:+.2f}%"

# ── LOAD TRANSACTIONS ─────────────────────────────────────────────────────────
print("Loading transactions ...")
tx = load_jsonl(TX_FILE)
tx.sort_values("ymd", inplace=True)

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
orig_total = pos_df["orig_pnl"].sum()
print(f"  Original total PnL: {fmt_b(orig_total)}")

# ── FETCH INDICATORS FROM BQ ──────────────────────────────────────────────────
COLS = ("t.ticker, t.time, t.Open, t.Close, t.Close_T1, "
        "t.D_RSI, t.D_RSI_T1, t.D_MACDdiff, t.D_CMF, "
        "t.MA10, t.MA20, t.MA10_T1, t.MA20_T1, "
        "t.Volume, t.Volume_3M_P50, t.VAP1M, t.D_CMB_Peak_T1")

tickers  = pos_df["ticker"].unique().tolist()
date_min = pos_df["first_buy"].min().strftime("%Y-%m-%d")
date_max = pos_df["last_sell"].max().strftime("%Y-%m-%d")
n_chunks = -(-len(tickers) // BQ_CHUNK)
print(f"\nFetching indicators: {len(tickers)} tickers, {n_chunks} chunks ...")

frames = []
for i in range(0, len(tickers), BQ_CHUNK):
    chunk = tickers[i:i+BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = (f'SELECT {COLS} FROM tav2_bq.ticker AS t '
             f'WHERE t.ticker IN ({tstr}) '
             f'AND t.time BETWEEN "{date_min}" AND "{date_max}" '
             f'ORDER BY t.ticker, t.time')
    df = bq_query(sql)
    df["time"] = pd.to_datetime(df["time"])
    frames.append(df)
    print(f"  chunk {i//BQ_CHUNK+1}/{n_chunks}: {len(df):,} rows")

ind_df = pd.concat(frames, ignore_index=True)
print(f"  Total rows: {len(ind_df):,}")

# Build indicator map: ticker -> DataFrame(index=date)
ind_map = {}
for ticker, grp in ind_df.groupby("ticker"):
    g = grp.sort_values("time").set_index("time").copy()
    g["Open_next"] = g["Open"].shift(-1)
    ind_map[ticker] = g

# ── CORE SIMULATION ───────────────────────────────────────────────────────────
def simulate_signal(pos, signal_fn):
    """
    Apply one technical sell signal to a position.
    Returns (pnl, pct, exit_type, days_early)
    """
    ticker    = pos["ticker"]
    first_buy = pos["first_buy"]
    last_sell = pos["last_sell"]
    buys_df   = pos["buys_df"]
    orig_pnl  = pos["orig_pnl"]
    orig_pct  = pos["orig_pnl_pct"]
    total_fees= pos["total_fees"]

    if ticker not in ind_map:
        return orig_pnl, orig_pct, "no_data", 0

    df_px = ind_map[ticker]
    try:
        window = df_px.loc[first_buy:last_sell]
    except Exception:
        return orig_pnl, orig_pct, "original", 0
    if window.empty:
        return orig_pnl, orig_pct, "original", 0

    buy_list = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr  = 0
    n_buys   = len(buy_list)
    cum_inv  = 0.0
    cum_sh   = 0.0
    trading_day = 0
    prev_row    = None

    def make_exit(date, close, open_next):
        fill  = open_next if (open_next and not pd.isna(open_next) and open_next > 0) else close
        denom = cum_inv + total_fees
        proc  = fill * cum_sh
        return proc - denom, (proc / denom - 1) * 100

    rows = list(window.iterrows())
    for idx, (date, row) in enumerate(rows):
        close     = row["Close"]
        open_next = row.get("Open_next", float("nan"))

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
            prev_row = row
            continue

        trading_day += 1

        if trading_day >= MIN_HOLD:
            # Evaluate signal — catch any indicator NaN gracefully
            try:
                fired = signal_fn(row, prev_row)
            except Exception:
                fired = False

            if fired:
                pnl, pct = make_exit(date, close, open_next)
                orig_td  = len(rows) - 1  # approximate original hold in trading days
                days_early = (last_sell - date).days
                return pnl, pct, "signal", days_early

        prev_row = row

    return orig_pnl, orig_pct, "original", 0

# ── RUN ALL SIGNALS ────────────────────────────────────────────────────────────
print("\n=== Technical Signal Backtest Results ===")
print(f"{'Signal':<22} {'Total PnL':>12} {'Delta':>12} {'Delta%':>8} {'Fired':>6} "
      f"{'Win%':>6} {'Avg Early':>10} {'Avg Ret':>9}")
print("-" * 100)

signal_results = {}
for sig_id, sig_fn in SIGNALS.items():
    pnls, types, days_early_list = [], [], []
    early_wins = 0
    n_fired = 0

    for _, pos in pos_df.iterrows():
        pnl, pct, etype, days_early = simulate_signal(pos, sig_fn)
        pnls.append(pnl)
        types.append(etype)
        if etype == "signal":
            n_fired += 1
            days_early_list.append(days_early)
            if pnl >= pos["orig_pnl"]:
                early_wins += 1

    total_pnl = sum(pnls)
    delta = total_pnl - orig_total
    win_pct = (early_wins / n_fired * 100) if n_fired > 0 else 0
    avg_early = np.mean(days_early_list) if days_early_list else 0
    avg_ret = np.mean([p / pos["total_inv"] * 100 for p, (_, pos) in
                       zip(pnls, pos_df.iterrows())]) if pnls else 0

    signal_results[sig_id] = {
        "total_pnl": total_pnl,
        "delta": delta,
        "delta_pct": delta / abs(orig_total) * 100,
        "n_fired": n_fired,
        "win_pct": win_pct,
        "avg_early_days": avg_early,
        "pnls": pnls,
        "types": types,
        "days_early": days_early_list,
    }
    label = SIGNAL_LABELS[sig_id]
    print(f"  {label:<20} {fmt_b(total_pnl):>12} {fmt_b(delta):>12} "
          f"{fmt_pct(delta/abs(orig_total)*100):>8} {n_fired:>6} "
          f"{win_pct:>5.1f}% {avg_early:>9.1f}d {avg_ret:>8.2f}%")

# ── FIND BEST SIGNAL ──────────────────────────────────────────────────────────
best_sig = max(signal_results, key=lambda s: signal_results[s]["delta"])
print(f"\nBest signal: {SIGNAL_LABELS[best_sig]}")
print(f"  Delta: {fmt_b(signal_results[best_sig]['delta'])} "
      f"({fmt_pct(signal_results[best_sig]['delta_pct'])})")

# ── POSITION-LEVEL DETAIL for best signal ─────────────────────────────────────
print(f"\n=== Detail: {SIGNAL_LABELS[best_sig]} ===")
best_fn = SIGNALS[best_sig]
detail_rows = []
for _, pos in pos_df.iterrows():
    pnl, pct, etype, days_early = simulate_signal(pos, best_fn)
    detail_rows.append({
        "ticker":    pos["ticker"],
        "first_buy": pos["first_buy"].date(),
        "orig_pnl":  pos["orig_pnl"],
        "sim_pnl":   pnl,
        "delta":     pnl - pos["orig_pnl"],
        "orig_pct":  pos["orig_pnl_pct"],
        "sim_pct":   pct,
        "exit_type": etype,
        "days_early": days_early,
    })

det_df = pd.DataFrame(detail_rows)
fired_df = det_df[det_df["exit_type"] == "signal"]
print(f"  Fired: {len(fired_df)} | Win: {(fired_df['delta']>=0).sum()} | "
      f"Loss: {(fired_df['delta']<0).sum()}")
print(f"  Avg orig return (fired): {fired_df['orig_pct'].mean():.1f}%")
print(f"  Avg sim  return (fired): {fired_df['sim_pct'].mean():.1f}%")
print(f"  Total delta (fired): {fmt_b(fired_df['delta'].sum())}")
print(f"  Avg days early: {fired_df['days_early'].mean():.0f} days")
print()
# Top gainers & losers from signal
print("  Top 10 positions where signal helped most:")
for _, r in fired_df.sort_values("delta", ascending=False).head(10).iterrows():
    print(f"    {r['ticker']:6s} {str(r['first_buy']):10s} "
          f"orig={r['orig_pct']:+6.1f}% -> sim={r['sim_pct']:+6.1f}% "
          f"delta={fmt_b(r['delta'])} ({r['days_early']:+.0f}d early)")
print()
print("  Top 10 positions where signal hurt most:")
for _, r in fired_df.sort_values("delta").head(10).iterrows():
    print(f"    {r['ticker']:6s} {str(r['first_buy']):10s} "
          f"orig={r['orig_pct']:+6.1f}% -> sim={r['sim_pct']:+6.1f}% "
          f"delta={fmt_b(r['delta'])} ({r['days_early']:+.0f}d early)")

# ── COMPOSITE: combine best 2 signals (fire on EITHER) ────────────────────────
print("\n=== Testing combinations (signal fires if ANY of 2 triggers) ===")
top3 = sorted(signal_results, key=lambda s: signal_results[s]["delta"], reverse=True)[:3]
combo_results = {}
for i, sa in enumerate(top3):
    for sb in top3[i+1:]:
        fn_a = SIGNALS[sa]; fn_b = SIGNALS[sb]
        def combo_fn(r, p, fa=fn_a, fb=fn_b):
            try: a = fa(r, p)
            except: a = False
            try: b = fb(r, p)
            except: b = False
            return a or b
        pnls = [simulate_signal(pos, combo_fn)[0] for _, pos in pos_df.iterrows()]
        total_pnl = sum(pnls)
        delta = total_pnl - orig_total
        combo_name = f"{SIGNAL_LABELS[sa].split(':')[0]} OR {SIGNAL_LABELS[sb].split(':')[0]}"
        combo_results[combo_name] = {"total_pnl": total_pnl, "delta": delta}
        print(f"  {combo_name:<25} {fmt_b(total_pnl):>12} delta={fmt_b(delta)} "
              f"({fmt_pct(delta/abs(orig_total)*100)})")

# ── CHART ─────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(20, 14), facecolor=DARK_BG)
gs  = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.38)

# Panel 1: Bar chart — delta PnL for each signal
ax1 = fig.add_subplot(gs[0, :2])
sig_names = list(SIGNALS.keys())
deltas = [signal_results[s]["delta"] / 1e9 for s in sig_names]
bar_colors = [GREEN if d > 0 else RED for d in deltas]
bars = ax1.bar(range(len(sig_names)), deltas, color=bar_colors, alpha=0.85, width=0.65)
ax1.axhline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
ax1.set_xticks(range(len(sig_names)))
ax1.set_xticklabels([SIGNAL_LABELS[s].split(":")[0] for s in sig_names], fontsize=8)
ax1.set_ylabel("PnL Delta vs Original (B VND)")
ax1.set_title("Technical Sell Signals: PnL Delta vs Current Strategy", color=TEXT_CLR, fontweight="bold")
for bar, val in zip(bars, deltas):
    ax1.text(bar.get_x() + bar.get_width()/2,
             bar.get_height() + (0.3 if val >= 0 else -1.5),
             f"{val:+.1f}B", ha="center", fontsize=8, color=TEXT_CLR)

# Panel 2: Win rate and fires count
ax2 = fig.add_subplot(gs[0, 2])
win_pcts  = [signal_results[s]["win_pct"] for s in sig_names]
n_fired   = [signal_results[s]["n_fired"] for s in sig_names]
colors2   = [GREEN if w > 50 else RED for w in win_pcts]
bars2 = ax2.bar(range(len(sig_names)), win_pcts, color=colors2, alpha=0.8)
ax2.axhline(50, color=YELLOW, linewidth=1.0, linestyle="--", label="50% line")
ax2.set_xticks(range(len(sig_names)))
ax2.set_xticklabels([s.split("_")[0] for s in sig_names], fontsize=8)
ax2.set_ylabel("Win Rate (%) when fired")
ax2.set_title("Win Rate When Signal Fires", color=TEXT_CLR, fontweight="bold")
ax2.set_ylim(0, 100)
for bar, wn, nf in zip(bars2, win_pcts, n_fired):
    ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f"{wn:.0f}%\n(n={nf})", ha="center", fontsize=7, color=TEXT_CLR)

# Panel 3: Return distribution for best signal — original vs signal exit
ax3 = fig.add_subplot(gs[1, 0])
best_pnls = signal_results[best_sig]["pnls"]
best_types = signal_results[best_sig]["types"]
sig_rets  = [(pnl / pos["total_inv"] * 100)
             for pnl, etype, (_, pos) in zip(best_pnls, best_types, pos_df.iterrows())
             if etype == "signal"]
orig_rets = [pos["orig_pnl_pct"]
             for etype, (_, pos) in zip(best_types, pos_df.iterrows())
             if etype == "signal"]
if sig_rets:
    all_vals = sig_rets + orig_rets
    bins = np.linspace(min(all_vals) - 5, max(all_vals) + 5, 30)
    ax3.hist(orig_rets, bins=bins, alpha=0.6, color=BLUE,   label="Original exit")
    ax3.hist(sig_rets,  bins=bins, alpha=0.6, color=ORANGE, label=f"{SIGNAL_LABELS[best_sig].split(':')[0]} exit")
    ax3.axvline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax3.set_xlabel("Return (%)")
    ax3.set_title(f"Returns: Best Signal vs Original\n(only fired positions)", color=TEXT_CLR)
    ax3.legend(fontsize=8)

# Panel 4: Scatter — original return vs delta
ax4 = fig.add_subplot(gs[1, 1])
if not fired_df.empty:
    colors4 = [GREEN if d >= 0 else RED for d in fired_df["delta"]]
    ax4.scatter(fired_df["orig_pct"], fired_df["delta"] / 1e9,
                c=colors4, alpha=0.7, s=50)
    ax4.axhline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax4.axvline(0, color=TEXT_CLR, linewidth=0.8, linestyle="--")
    ax4.set_xlabel("Original Return (%)")
    ax4.set_ylabel("PnL Delta (B VND)")
    ax4.set_title(f"Signal Helped (green) vs Hurt (red)\n{SIGNAL_LABELS[best_sig]}",
                  color=TEXT_CLR)
    n_pos = (fired_df["delta"] >= 0).sum()
    n_neg = (fired_df["delta"] < 0).sum()
    ax4.text(0.02, 0.98, f"Helped: {n_pos} | Hurt: {n_neg}",
             transform=ax4.transAxes, va="top", fontsize=9, color=TEXT_CLR)

# Panel 5: Days early distribution
ax5 = fig.add_subplot(gs[1, 2])
all_days_early = []
labels_de = []
for sig_id in sig_names:
    de = signal_results[sig_id]["days_early"]
    if de:
        all_days_early.append(de)
        labels_de.append(SIGNAL_LABELS[sig_id].split(":")[0])

if all_days_early:
    bp = ax5.boxplot(all_days_early, labels=labels_de, patch_artist=True,
                     medianprops=dict(color=YELLOW, linewidth=2))
    for patch in bp["boxes"]:
        patch.set_facecolor(BLUE)
        patch.set_alpha(0.6)
    ax5.set_ylabel("Days Before Original Exit")
    ax5.set_title("How Early Does Each Signal Fire?", color=TEXT_CLR)
    ax5.tick_params(axis="x", labelsize=7, rotation=45)

# Panel 6: Cumulative PnL chart across positions sorted by date
ax6 = fig.add_subplot(gs[2, :])
# Sort positions by first_buy
sorted_idx = pos_df.sort_values("first_buy").index
orig_cumsum = pos_df.loc[sorted_idx, "orig_pnl"].cumsum() / 1e9

ax6.plot(range(len(sorted_idx)), orig_cumsum.values, color=BLUE,
         linewidth=2.0, label="Original strategy", zorder=5)

# Plot top 3 signals
colors_top = [GREEN, ORANGE, PURPLE]
for color, sig_id in zip(colors_top, top3):
    sim_pnls = signal_results[sig_id]["pnls"]
    sorted_pnls = [sim_pnls[i] for i in sorted_idx]
    cumsum = np.cumsum(sorted_pnls) / 1e9
    ax6.plot(range(len(sorted_idx)), cumsum, color=color, linewidth=1.5, alpha=0.85,
             label=SIGNAL_LABELS[sig_id])

ax6.set_xlabel("Position # (sorted by entry date)")
ax6.set_ylabel("Cumulative PnL (B VND)")
ax6.set_title("Cumulative PnL: Original vs Best Technical Signals", color=TEXT_CLR, fontweight="bold")
ax6.legend(fontsize=8, loc="upper left")
ax6.grid(True, alpha=0.3)

fig.suptitle(f"Technical Sell Signal Backtest  |  {len(pos_df)} positions (2020-present)  |  Original: {fmt_b(orig_total)}",
             color=TEXT_CLR, fontsize=13, fontweight="bold", y=0.99)

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved: {OUT_IMG}")
