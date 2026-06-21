#!/usr/bin/env python3
"""
backtest_combined.py
====================
Combined strategy: Time-Stop (20 trading days) + Cut-Loss sweep.

Execution model (realistic):
  - TRIGGER detected using Close[D]  (end-of-day signal)
  - EXECUTION at Open[D+1]           (next morning fill)
  - Fallback to Close[D] if D+1 missing (last trading day of data)

For each closed position, on each trading day:
  1. CUT-LOSS first: if Close[D] <= avg_cost*(1-cl_pct) -> sell at Open[D+1].
  2. TIME-STOP on day 20: if price NEVER rose above avg_cost -> sell at Open[D+1].
  3. Otherwise -> keep original exit.

Grid:
  - Time-stop fixed at 20 days (proven best from previous backtest)
  - Cut-loss sweep: [None, 5%, 7%, 8%, 10%, 12%, 15%, 20%]
  - Also test: cut-loss only (no time-stop) for clean comparison

Output: console table + 5-panel chart
"""

import json
import subprocess
from io import StringIO
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap

# ── CONFIG ────────────────────────────────────────────────────────────────────
TX_FILE   = "transactions_email_special_2026-04-07_15.14.47.jsonl"
PROJECT   = "lithe-record-440915-m9"
OUT_IMG   = "backtest_combined_2020.png"
BQ_CHUNK  = 150
BQ_BIN    = r"bq"

TIME_STOP_DAYS = 20
CL_GRID = [None, 0.05, 0.07, 0.08, 0.10, 0.12, 0.15, 0.20]

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
    df = pd.DataFrame(rows); df["ymd"] = pd.to_datetime(df["ymd"])
    return df

def bq_query(sql):
    cmd = [BQ_BIN, "query", "--use_legacy_sql=false",
           f"--project_id={PROJECT}", "--format=csv", "--max_rows=5000000", sql]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:600])
    return pd.read_csv(StringIO(r.stdout))

def fmt_b(v):  return f"{v/1e9:,.2f}B"
def fmt_p(v):  sign = "+" if v >= 0 else ""; return f"{sign}{v:.2f}%"

# ── LOAD ──────────────────────────────────────────────────────────────────────
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
# ── Filter: only positions opened from 2020 onwards ──────────────────────────
FILTER_FROM = pd.Timestamp("2020-01-01")
pos_df = pos_df[pos_df["first_buy"] >= FILTER_FROM].reset_index(drop=True)
print(f"  {len(pos_df)} closed positions (>= {FILTER_FROM.date()}) | {pos_df['ticker'].nunique()} tickers")

# ── FETCH PRICES ──────────────────────────────────────────────────────────────
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

# price_map: ticker -> DataFrame(index=date, columns=[Close, Open_next])
# Open_next = Open of the following trading day (next-day fill price)
price_map = {}
for ticker, grp in prices_df.groupby("ticker"):
    grp = grp.sort_values("time").set_index("time")[["Close", "Open"]].copy()
    grp["Open_next"] = grp["Open"].shift(-1)   # next trading day's open
    price_map[ticker] = grp

# ── CORE SIMULATION ───────────────────────────────────────────────────────────
def simulate(ticker, first_buy, last_sell, buys_df,
             total_inv, total_fees, orig_pnl, orig_pnl_pct,
             cl_pct, use_timestop):
    """
    Realistic execution model:
      - Trigger condition evaluated on Close[D]
      - Exit price = Open[D+1]  (next morning fill)
      - Fallback to Close[D] if Open[D+1] is NaN (last day of data)

    cl_pct      : float or None  — cut-loss % below avg cost
    use_timestop: bool           — apply 20-day time-stop rule
    exit_type   : 'cut_loss' | 'time_stop' | 'original' | 'no_data'
    """
    if ticker not in price_map:
        return orig_pnl, orig_pnl_pct, "no_data", None

    df_px = price_map[ticker]
    try:
        window = df_px.loc[first_buy:last_sell]
    except Exception:
        return orig_pnl, orig_pnl_pct, "original", None
    if window.empty:
        return orig_pnl, orig_pnl_pct, "original", None

    buy_list    = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr     = 0
    n_buys      = len(buy_list)
    cum_inv     = 0.0
    cum_sh      = 0.0
    ever_above  = False
    trading_day = 0

    def make_exit(date, close, open_next):
        # Use next-day open as fill; fallback to close if unavailable
        fill = open_next if (open_next and not pd.isna(open_next) and open_next > 0) else close
        denom = cum_inv + total_fees
        proc  = fill * cum_sh
        return proc - denom, (proc / denom - 1) * 100, (date - first_buy).days

    for date, row in window.iterrows():
        close     = row["Close"]
        open_next = row["Open_next"]   # next trading day's open

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

        avg_cost = cum_inv / cum_sh

        if date == first_buy:
            trading_day = 0
            continue

        trading_day += 1

        if close > avg_cost:
            ever_above = True

        # 1. Cut-loss — trigger on Close[D], fill at Open[D+1]
        if cl_pct and close <= avg_cost * (1 - cl_pct):
            pnl, pct_v, hdays = make_exit(date, close, open_next)
            return pnl, pct_v, "cut_loss", hdays

        # 2. Time-stop on exactly day 20 — fill at Open[D+1]
        if use_timestop and trading_day == TIME_STOP_DAYS:
            if not ever_above and close <= avg_cost:
                pnl, pct_v, hdays = make_exit(date, close, open_next)
                return pnl, pct_v, "time_stop", hdays

    return orig_pnl, orig_pnl_pct, "original", (last_sell - first_buy).days

# ── BASELINE ─────────────────────────────────────────────────────────────────
orig_total_pnl = pos_df["orig_pnl"].sum()
orig_win_rate  = (pos_df["orig_pnl_pct"] > 0).mean() * 100
orig_avg_pct   = pos_df["orig_pnl_pct"].mean()
orig_avg_win   = pos_df[pos_df["orig_pnl_pct"] > 0]["orig_pnl_pct"].mean()
orig_avg_loss  = pos_df[pos_df["orig_pnl_pct"] <= 0]["orig_pnl_pct"].mean()
orig_max_loss  = pos_df["orig_pnl_pct"].min()

pos_list = [
    (row["ticker"], row["first_buy"], row["last_sell"], row["buys_df"],
     row["total_inv"], row["total_fees"], row["orig_pnl"], row["orig_pnl_pct"])
    for _, row in pos_df.iterrows()
]

# ── GRID SEARCH ───────────────────────────────────────────────────────────────
scenarios = []
# A) Time-stop only (no cut-loss)  — already proven
scenarios.append(("TS20 only",       None,  True))
# B) Cut-loss only (no time-stop)   — baseline comparison
for cl in CL_GRID[1:]:
    scenarios.append((f"CL {cl*100:.0f}% only", cl, False))
# C) Time-stop 20d + Cut-loss combined
for cl in CL_GRID[1:]:
    scenarios.append((f"TS20 + CL {cl*100:.0f}%", cl, True))

print(f"\nRunning {len(scenarios)} scenarios ...")

results = []
for label, cl_pct, use_ts in scenarios:
    pnls, pcts, exits = [], [], []
    for args in pos_list:
        pnl, pct_v, etype, _ = simulate(*args, cl_pct, use_ts)
        pnls.append(pnl); pcts.append(pct_v); exits.append(etype)

    pnls_a  = np.array(pnls,  dtype=float)
    pcts_a  = np.array(pcts,  dtype=float)
    exits_a = np.array(exits)
    wins    = pcts_a > 0

    results.append({
        "label":        label,
        "cl_pct":       cl_pct,
        "use_ts":       use_ts,
        "total_pnl":    pnls_a.sum(),
        "win_rate":     wins.mean() * 100,
        "avg_pct":      pcts_a.mean(),
        "avg_win":      pcts_a[wins].mean()  if wins.any()   else 0.0,
        "avg_loss":     pcts_a[~wins].mean() if (~wins).any() else 0.0,
        "max_loss":     pcts_a.min(),
        "pnl_diff":     pnls_a.sum() - orig_total_pnl,
        "pnl_diff_pct": (pnls_a.sum() - orig_total_pnl) / abs(orig_total_pnl) * 100,
        "n_cl":         (exits_a == "cut_loss").sum(),
        "n_ts":         (exits_a == "time_stop").sum(),
        "n_orig":       (exits_a == "original").sum(),
        "pcts_arr":     pcts_a,
        "exits_arr":    exits_a,
    })

rdf = pd.DataFrame(results)

# Separate groups
ts_only  = rdf[rdf["label"] == "TS20 only"].iloc[0]
cl_only  = rdf[rdf["use_ts"] == False]
combined = rdf[rdf["use_ts"] == True]
best_cl_only  = cl_only.loc[cl_only["total_pnl"].idxmax()]
best_combined = combined.loc[combined["total_pnl"].idxmax()]
best_overall  = rdf.loc[rdf["total_pnl"].idxmax()]

# ── CONSOLE ───────────────────────────────────────────────────────────────────
SEP = "=" * 72

def prow(r):
    print(f"  P&L      : {fmt_b(r['total_pnl'])}  ({r['pnl_diff_pct']:+.2f}% vs orig  /  {fmt_b(r['pnl_diff'])} diff)")
    print(f"  Win rate : {r['win_rate']:.1f}%   Avg ret: {fmt_p(r['avg_pct'])}"
          f"   Avg gain: {fmt_p(r['avg_win'])}   Avg loss: {fmt_p(r['avg_loss'])}")
    print(f"  Max loss : {fmt_p(r['max_loss'])}")
    n_cl = int(r['n_cl']); n_ts = int(r['n_ts']); n_o = int(r['n_orig'])
    print(f"  Exits    : CutLoss={n_cl}  TimeStop={n_ts}  Original={n_o}  Total={n_cl+n_ts+n_o}")

print(f"\n{SEP}")
print("ORIGINAL (no overlay)")
print(f"  P&L      : {fmt_b(orig_total_pnl)}")
print(f"  Win rate : {orig_win_rate:.1f}%   Avg ret: {fmt_p(orig_avg_pct)}"
      f"   Avg gain: {fmt_p(orig_avg_win)}   Avg loss: {fmt_p(orig_avg_loss)}")
print(f"  Max loss : {fmt_p(orig_max_loss)}")

print(f"\n{SEP}")
print("TIME-STOP 20d ONLY")
prow(ts_only)

print(f"\n{SEP}")
print(f"BEST CUT-LOSS ONLY -> CL = {best_cl_only['cl_pct']*100:.0f}%")
prow(best_cl_only)

print(f"\n{SEP}")
print(f"BEST COMBINED (TS20 + CL) -> {best_combined['label']}")
prow(best_combined)

print(f"\n{SEP}")
print(f"BEST OVERALL -> {best_overall['label']}")
prow(best_overall)

print(f"\n{SEP}")
print("\nFull results (sorted by Total P&L):\n")
print(f"{'Label':<22} | {'P&L(B)':>10} {'vs orig':>9} {'WR':>7} "
      f"{'AvgPct':>8} {'AvgGain':>8} {'AvgLoss':>9} {'MaxLoss':>9} "
      f"{'nCL':>5} {'nTS':>5} {'nOrig':>6}")
print("-" * 105)
for _, r in rdf.sort_values("total_pnl", ascending=False).iterrows():
    marker = " ***" if r["label"] == best_overall["label"] else ""
    print(f"{r['label']:<22} | {r['total_pnl']/1e9:>10,.2f} {r['pnl_diff_pct']:>+8.2f}% "
          f"{r['win_rate']:>6.1f}% {r['avg_pct']:>7.2f}% "
          f"{r['avg_win']:>7.2f}% {r['avg_loss']:>8.2f}% {r['max_loss']:>8.2f}% "
          f"{int(r['n_cl']):>5} {int(r['n_ts']):>5} {int(r['n_orig']):>6}{marker}")


# ── VISUALISATION ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 30), facecolor=DARK_BG)
fig.suptitle("Backtest: Time-Stop 20d + Cut-Loss  [Fill = Open[D+1]]  —  2020 to present",
             fontsize=20, fontweight="bold", color=TEXT_CLR, y=0.998)
gs = gridspec.GridSpec(4, 2, figure=fig,
                       hspace=0.44, wspace=0.32,
                       left=0.06, right=0.97, top=0.965, bottom=0.03)

def styled(ax, title, grid_axis="y"):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_CLR, pad=8)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    ax.grid(True, axis=grid_axis)
    return ax

# ── Panel 0 (full width): P&L bar for all scenarios ──────────────────────────
ax0 = fig.add_subplot(gs[0, :])
styled(ax0, "Total P&L: All Scenarios  (dashed line = original baseline)")

# Group: original | TS only | CL only (8) | Combined (8)
labels_plot = ["Original", "TS20\nonly"] + \
              [f"CL\n{int(r['cl_pct']*100)}%" for _, r in cl_only.sort_values("cl_pct").iterrows()] + \
              [f"TS20+\nCL{int(r['cl_pct']*100)}%" for _, r in combined.dropna(subset=["cl_pct"]).sort_values("cl_pct").iterrows()]

combined_plot = combined.dropna(subset=["cl_pct"]).sort_values("cl_pct")

pnls_plot = [orig_total_pnl/1e9, ts_only["total_pnl"]/1e9] + \
            [r["total_pnl"]/1e9 for _, r in cl_only.sort_values("cl_pct").iterrows()] + \
            [r["total_pnl"]/1e9 for _, r in combined_plot.iterrows()]

wr_plot = [orig_win_rate, ts_only["win_rate"]] + \
          [r["win_rate"] for _, r in cl_only.sort_values("cl_pct").iterrows()] + \
          [r["win_rate"] for _, r in combined_plot.iterrows()]

n_bars = len(labels_plot)
x = np.arange(n_bars)

def bar_color(i, pnl):
    if i == 0: return BLUE
    if i == 1: return GREEN if pnl >= orig_total_pnl/1e9 else YELLOW
    if i <= 8:  return ORANGE  # CL only
    return PURPLE              # Combined

clrs_bar = [bar_color(i, p) for i, p in enumerate(pnls_plot)]
bars = ax0.bar(x, pnls_plot, color=clrs_bar, width=0.65, zorder=3, alpha=0.88)
ax0.axhline(orig_total_pnl/1e9, color=YELLOW, linewidth=1.2, linestyle="--", alpha=0.6)

# Separator lines between groups
for sep_x in [1.5, 9.5]:
    ax0.axvline(sep_x, color=GRID_CLR, linewidth=1, linestyle=":", alpha=0.8)

ax0.text(0.5,  0.96, "TS Only", transform=ax0.transAxes, ha="center",
         color=GREEN,  fontsize=9, style="italic")
ax0.text(0.35, 0.96, "CL Only", transform=ax0.transAxes, ha="center",
         color=ORANGE, fontsize=9, style="italic")
ax0.text(0.73, 0.96, "TS20 + CL Combined", transform=ax0.transAxes, ha="center",
         color=PURPLE, fontsize=9, style="italic")

# Win rate twin axis
ax0r = ax0.twinx()
ax0r.plot(x, wr_plot, color=RED, linewidth=1.8, marker="o", markersize=6,
          zorder=5, label="Win Rate %")
ax0r.set_ylabel("Win Rate %", color=RED, fontsize=10)
ax0r.tick_params(colors=RED)
ax0r.set_ylim(35, 70)

# Annotate diff vs orig on each bar
for i, (bar, pnl) in enumerate(zip(bars, pnls_plot)):
    diff = pnl - orig_total_pnl/1e9
    if i > 0:
        clr = GREEN if diff >= 0 else RED
        ax0.text(bar.get_x()+bar.get_width()/2,
                 max(bar.get_height(), 0) + orig_total_pnl*0.008/1e9,
                 f"{diff:+.0f}B", ha="center", fontsize=7.5, color=clr)

# Mark best
best_idx = pnls_plot.index(max(pnls_plot))
ax0.get_children()[best_idx].set_edgecolor(YELLOW)
ax0.get_children()[best_idx].set_linewidth(3)
ax0.text(x[best_idx], pnls_plot[best_idx] + orig_total_pnl*0.025/1e9,
         "BEST", ha="center", fontsize=9, color=YELLOW, fontweight="bold")

ax0.set_xticks(x); ax0.set_xticklabels(labels_plot, fontsize=8.5)
ax0.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
ax0.set_ylabel("Total P&L (B VND)")

# ── Panel 1 left: CL-only sweep line chart ────────────────────────────────────
ax1 = fig.add_subplot(gs[1, 0])
styled(ax1, "Cut-Loss Only: Key Metrics vs CL Level", grid_axis="both")

cl_sorted = cl_only.sort_values("cl_pct")
cl_x  = [r["cl_pct"]*100 for _, r in cl_sorted.iterrows()]
metric_pairs = [
    ("Total P&L (B)",  [r["total_pnl"]/1e9  for _, r in cl_sorted.iterrows()], ORANGE, "s"),
]
ax1b = ax1.twinx()
metric_pairs2 = [
    ("Avg Loss %",    [r["avg_loss"]   for _, r in cl_sorted.iterrows()], RED,    "o"),
    ("Avg Gain %",    [r["avg_win"]    for _, r in cl_sorted.iterrows()], GREEN,  "^"),
]
for name, vals, clr, mk in metric_pairs:
    ax1.plot(cl_x, vals, color=clr, linewidth=2.5, marker=mk, markersize=8, label=name)
for name, vals, clr, mk in metric_pairs2:
    ax1b.plot(cl_x, vals, color=clr, linewidth=2, marker=mk, markersize=7,
              linestyle="--", label=name)

ax1.axhline(orig_total_pnl/1e9, color=YELLOW, linewidth=1, linestyle=":", alpha=0.7,
            label="Orig P&L")
ax1.set_xlabel("Cut-Loss Level (%)"); ax1.set_ylabel("P&L (B VND)", color=ORANGE)
ax1b.set_ylabel("Avg Return %", color=TEXT_CLR)
ax1.tick_params(axis="y", colors=ORANGE)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
lines1, lbl1 = ax1.get_legend_handles_labels()
lines2, lbl2 = ax1b.get_legend_handles_labels()
ax1.legend(lines1+lines2, lbl1+lbl2, fontsize=8, framealpha=0.2, loc="lower left")

# ── Panel 1 right: Combined sweep line chart ──────────────────────────────────
ax2 = fig.add_subplot(gs[1, 1])
styled(ax2, "TS20 + Cut-Loss Combined: Key Metrics vs CL Level", grid_axis="both")

comb_sorted = combined.sort_values("cl_pct")
cx = [r["cl_pct"]*100 for _, r in comb_sorted.iterrows()]
ax2b = ax2.twinx()
ax2.plot(cx, [r["total_pnl"]/1e9 for _, r in comb_sorted.iterrows()],
         color=PURPLE, linewidth=2.5, marker="s", markersize=8, label="Total P&L (B)")
ax2.axhline(orig_total_pnl/1e9, color=YELLOW, linewidth=1, linestyle=":", alpha=0.7,
            label="Orig P&L")
ax2b.plot(cx, [r["avg_loss"] for _, r in comb_sorted.iterrows()],
          color=RED,   linewidth=2, marker="o", markersize=7, linestyle="--", label="Avg Loss %")
ax2b.plot(cx, [r["avg_win"]  for _, r in comb_sorted.iterrows()],
          color=GREEN, linewidth=2, marker="^", markersize=7, linestyle="--", label="Avg Gain %")
ax2b.plot(cx, [r["win_rate"] for _, r in comb_sorted.iterrows()],
          color=BLUE,  linewidth=2, marker="D", markersize=6, linestyle=":",  label="Win Rate %")

ax2.set_xlabel("Cut-Loss Level (%)"); ax2.set_ylabel("P&L (B VND)", color=PURPLE)
ax2b.set_ylabel("% metrics", color=TEXT_CLR)
ax2.tick_params(axis="y", colors=PURPLE)
ax2.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
lines1, lbl1 = ax2.get_legend_handles_labels()
lines2, lbl2 = ax2b.get_legend_handles_labels()
ax2.legend(lines1+lines2, lbl1+lbl2, fontsize=8, framealpha=0.2, loc="lower left")

# ── Panel 2 left: P&L Distribution — orig vs best combined ───────────────────
ax3 = fig.add_subplot(gs[2, 0])
styled(ax3, f"P&L Distribution: Original vs Best Combined ({best_combined['label']})")
ax3.grid(True, axis="y")

orig_arr = pos_df["orig_pnl_pct"].values
best_arr = best_combined["pcts_arr"]
all_arr  = np.concatenate([orig_arr, best_arr])
q01, q99 = np.percentile(all_arr[np.isfinite(all_arr)], [1, 99])
bins = np.linspace(q01, q99, 60)

ax3.hist(orig_arr, bins=bins, alpha=0.45, color=BLUE,
         label=f"Original  mean={orig_avg_pct:.1f}%  WR={orig_win_rate:.0f}%")
ax3.hist(best_arr, bins=bins, alpha=0.55, color=PURPLE,
         label=f"{best_combined['label']}  mean={best_combined['avg_pct']:.1f}%  WR={best_combined['win_rate']:.0f}%")

for v, c in [(orig_avg_pct, BLUE), (best_combined["avg_pct"], PURPLE)]:
    ax3.axvline(v, color=c, linewidth=1.4, linestyle=":")
ax3.axvline(0, color=YELLOW, linewidth=1, linestyle="--", alpha=0.6)
ax3.legend(fontsize=9, framealpha=0.25)
ax3.set_xlabel("Return %"); ax3.set_ylabel("# Positions")
ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

# ── Panel 2 right: Exit type breakdown stacked bar ────────────────────────────
ax4 = fig.add_subplot(gs[2, 1])
styled(ax4, "Exit Type Breakdown by Scenario")
ax4.grid(True, axis="x")

# Show all combined + ts_only scenarios
plot_rows = [ts_only] + [r for _, r in combined.sort_values("cl_pct").iterrows()]
plot_lbls = [r["label"] for r in plot_rows]
n_cl_arr  = [int(r["n_cl"])   for r in plot_rows]
n_ts_arr  = [int(r["n_ts"])   for r in plot_rows]
n_or_arr  = [int(r["n_orig"]) for r in plot_rows]

y = np.arange(len(plot_lbls))
h = 0.55
b1 = ax4.barh(y, n_or_arr, height=h, color=BLUE,   label="Original Exit", alpha=0.85)
b2 = ax4.barh(y, n_ts_arr, height=h, left=n_or_arr, color=GREEN, label="Time-Stop", alpha=0.85)
b3 = ax4.barh(y, n_cl_arr, height=h,
              left=[a+b for a,b in zip(n_or_arr, n_ts_arr)],
              color=RED, label="Cut-Loss", alpha=0.85)

ax4.set_yticks(y); ax4.set_yticklabels(plot_lbls, fontsize=9)
ax4.set_xlabel("# Positions"); ax4.legend(fontsize=9, framealpha=0.25)
ax4.invert_yaxis()

# ── Panel 3 (full width): Avg loss reduction heatmap ─────────────────────────
ax5 = fig.add_subplot(gs[3, :])
ax5.set_title("Summary Table: Delta vs Original  (P&L change in Billions VND)",
              fontsize=11, fontweight="bold", color=TEXT_CLR, pad=8)
ax5.spines[["top","right","left","bottom"]].set_visible(False)
ax5.axis("off")

# Build rich summary table
all_cl_pcts = sorted([cl for cl in CL_GRID if cl is not None])
col_headers = ["Scenario", "Total P&L", "vs Orig (B)", "vs Orig (%)",
               "Win Rate", "Avg Return", "Avg Gain", "Avg Loss", "Max Loss",
               "CL exits", "TS exits", "Orig exits"]

rows_table = []
# Original
rows_table.append(["Original (baseline)",
                   fmt_b(orig_total_pnl), "-", "-",
                   f"{orig_win_rate:.1f}%", fmt_p(orig_avg_pct),
                   fmt_p(orig_avg_win), fmt_p(orig_avg_loss), fmt_p(orig_max_loss),
                   "-", "-", "1155"])
# TS only
r = ts_only
rows_table.append([r["label"],
                   fmt_b(r["total_pnl"]),
                   f"{r['pnl_diff']/1e9:+.2f}B",
                   f"{r['pnl_diff_pct']:+.2f}%",
                   f"{r['win_rate']:.1f}%", fmt_p(r["avg_pct"]),
                   fmt_p(r["avg_win"]), fmt_p(r["avg_loss"]), fmt_p(r["max_loss"]),
                   str(int(r["n_cl"])), str(int(r["n_ts"])), str(int(r["n_orig"]))])

# CL only
for _, r in cl_only.sort_values("cl_pct").iterrows():
    rows_table.append([r["label"],
                       fmt_b(r["total_pnl"]),
                       f"{r['pnl_diff']/1e9:+.2f}B",
                       f"{r['pnl_diff_pct']:+.2f}%",
                       f"{r['win_rate']:.1f}%", fmt_p(r["avg_pct"]),
                       fmt_p(r["avg_win"]), fmt_p(r["avg_loss"]), fmt_p(r["max_loss"]),
                       str(int(r["n_cl"])), str(int(r["n_ts"])), str(int(r["n_orig"]))])

# Combined
for _, r in combined.sort_values("cl_pct").iterrows():
    rows_table.append([r["label"],
                       fmt_b(r["total_pnl"]),
                       f"{r['pnl_diff']/1e9:+.2f}B",
                       f"{r['pnl_diff_pct']:+.2f}%",
                       f"{r['win_rate']:.1f}%", fmt_p(r["avg_pct"]),
                       fmt_p(r["avg_win"]), fmt_p(r["avg_loss"]), fmt_p(r["max_loss"]),
                       str(int(r["n_cl"])), str(int(r["n_ts"])), str(int(r["n_orig"]))])

# Color rows
row_colors = []
for row in rows_table:
    vs = row[3]
    if vs == "-":
        row_colors.append([BLUE] + ["#1e2130"] * (len(col_headers)-1))
    elif vs.startswith("+"):
        row_colors.append([GREEN] + ["#152117"] * (len(col_headers)-1))
    else:
        val = float(vs.replace("%",""))
        if val > -1:
            row_colors.append(["#1c2218"] + ["#181d28"] * (len(col_headers)-1))
        else:
            row_colors.append(["#291414"] + ["#1a1519"] * (len(col_headers)-1))

tbl = ax5.table(
    cellText=rows_table,
    colLabels=col_headers,
    cellLoc="center", loc="center",
    cellColours=row_colors,
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(8.5)
tbl.scale(1, 1.55)

# Header style
for j in range(len(col_headers)):
    tbl[(0, j)].set_facecolor("#0a2a4a")
    tbl[(0, j)].set_text_props(color=TEXT_CLR, fontweight="bold")

# Text color all cells
for (row, col), cell in tbl.get_celld().items():
    if row > 0:
        cell.set_text_props(color=TEXT_CLR)
        cell.set_edgecolor(GRID_CLR)

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved -> {Path(OUT_IMG).resolve()}")
