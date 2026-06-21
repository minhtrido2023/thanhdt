#!/usr/bin/env python3
"""
backtest_timestop.py
====================
Time-stop strategy:
  - After TIME_STOP_DAYS trading days from first buy,
    if Close is STILL below average cost basis -> exit immediately.
  - If price ever went above cost basis before day N -> keep original exit
    (position is "alive", let it run).
  - Sweep grid of [30, 45, 60, 90] days for sensitivity analysis.
  - Highlight user-requested: 45 days.
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

# ── CONFIG ────────────────────────────────────────────────────────────────────
TX_FILE   = "transactions_email_special_2026-04-07_15.14.47.jsonl"
PROJECT   = "lithe-record-440915-m9"
OUT_IMG   = "backtest_timestop.png"
BQ_CHUNK  = 150

REQUESTED_DAYS = 45
DAY_GRID       = [20, 30, 45, 60, 90]   # trading days, not calendar days

BQ_BIN = r"bq"

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG  = "#0f1117"; PANEL_BG = "#1a1d27"; GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"; BLUE = "#4fa3e0";     GREEN = "#4ecb71"
RED      = "#e05c5c"; YELLOW = "#f0c060";   PURPLE = "#b57bee"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor":   GRID_CLR, "axes.labelcolor": TEXT_CLR,
    "xtick.color": TEXT_CLR,     "ytick.color":  TEXT_CLR,
    "text.color":  TEXT_CLR,     "grid.color":   GRID_CLR,
    "grid.linestyle": "--",      "grid.alpha":   0.5,
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

def fmt_b(v): return f"{v/1e9:,.2f}B"
def fmt_p(v): sign = "+" if v >= 0 else ""; return f"{sign}{v:.2f}%"

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
print(f"  {len(pos_df)} closed positions  |  {pos_df['ticker'].nunique()} tickers")

# ── FETCH PRICES ──────────────────────────────────────────────────────────────
tickers  = pos_df["ticker"].unique().tolist()
date_min = pos_df["first_buy"].min().strftime("%Y-%m-%d")
date_max = pos_df["last_sell"].max().strftime("%Y-%m-%d")
n_chunks = -(-len(tickers) // BQ_CHUNK)
print(f"Fetching prices: {len(tickers)} tickers | {date_min} -> {date_max} | {n_chunks} chunks ...")

frames = []
for i in range(0, len(tickers), BQ_CHUNK):
    chunk = tickers[i : i + BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = (f'SELECT t.ticker, t.time, t.Close '
             f'FROM tav2_bq.ticker AS t '
             f'WHERE t.ticker IN ({tstr}) '
             f'  AND t.time BETWEEN "{date_min}" AND "{date_max}" '
             f'ORDER BY t.ticker, t.time')
    df = bq_query(sql)
    df["time"] = pd.to_datetime(df["time"])
    frames.append(df)
    print(f"  chunk {i//BQ_CHUNK+1}/{n_chunks}: {len(df):,} rows")

prices_df = pd.concat(frames, ignore_index=True)
print(f"  Total rows: {len(prices_df):,}")

price_map = {
    ticker: grp.set_index("time")["Close"].sort_index()
    for ticker, grp in prices_df.groupby("ticker")
}

# ── SIMULATE: TIME-STOP ───────────────────────────────────────────────────────
def simulate_timestop(ticker, first_buy, last_sell, buys_df,
                      total_inv, total_fees, orig_pnl, orig_pnl_pct,
                      stop_days):
    """
    Rules:
      - Count trading days since first_buy.
      - Track running avg cost basis as DCA buys accumulate.
      - If price EVER closes ABOVE avg cost -> position is "alive", skip time-stop.
      - On trading day = stop_days: if Close still <= avg cost -> exit at that Close.
      - Otherwise -> original exit.

    Returns (pnl, pnl_pct, exit_type, holding_days, exit_close, avg_cost_at_exit)
    exit_type: 'time_stop' | 'original' | 'no_data'
    """
    if ticker not in price_map:
        return orig_pnl, orig_pnl_pct, "no_data", None, None, None

    series = price_map[ticker]
    try:
        window = series.loc[first_buy : last_sell]
    except Exception:
        return orig_pnl, orig_pnl_pct, "original", None, None, None
    if window.empty:
        return orig_pnl, orig_pnl_pct, "original", None, None, None

    buy_list  = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr   = 0
    n_buys    = len(buy_list)
    cum_inv   = 0.0
    cum_sh    = 0.0
    ever_above = False      # ever traded above avg cost
    trading_day = 0         # count from first_buy (exclusive)

    for date, close in window.items():
        if pd.isna(close) or close <= 0:
            continue

        # Absorb buys on or before this date
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

        # Check if price ever rose above cost basis
        if close > avg_cost:
            ever_above = True

        # On the exact stop_day: if still below cost -> exit
        if trading_day == stop_days:
            if not ever_above and close <= avg_cost:
                denom = cum_inv + total_fees
                proc  = close * cum_sh
                return (
                    proc - denom,
                    (proc / denom - 1) * 100,
                    "time_stop",
                    (date - first_buy).days,
                    close,
                    avg_cost,
                )
            else:
                # Price was above cost at some point -> let it run
                break

    return orig_pnl, orig_pnl_pct, "original", (last_sell - first_buy).days, None, None


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
print(f"\nGrid search over {DAY_GRID} day thresholds ...")
grid_rows = []

for stop_days in DAY_GRID:
    pnls, pcts, exits = [], [], []
    loss_saved_list   = []   # how much was saved on time-stopped positions

    for args in pos_list:
        pnl, pct_v, etype, hdays, exit_close, avg_cost = simulate_timestop(*args, stop_days)
        pnls.append(pnl); pcts.append(pct_v); exits.append(etype)
        if etype == "time_stop":
            loss_saved_list.append(args[7] - pct_v)   # orig_pnl_pct - sim_pnl_pct

    pnls_a  = np.array(pnls,  dtype=float)
    pcts_a  = np.array(pcts,  dtype=float)
    exits_a = np.array(exits)
    wins    = pcts_a > 0

    n_ts      = (exits_a == "time_stop").sum()
    n_orig    = (exits_a == "original").sum()
    n_no_data = (exits_a == "no_data").sum()

    # P&L of only the time-stopped positions: original vs simulated
    ts_mask = exits_a == "time_stop"
    orig_pnl_ts = np.array([args[6] for args in pos_list])[ts_mask]
    sim_pnl_ts  = pnls_a[ts_mask]
    pnl_rescued = (sim_pnl_ts - orig_pnl_ts).sum()   # how much was rescued (negative = saved loss)

    grid_rows.append({
        "days":         stop_days,
        "total_pnl":    pnls_a.sum(),
        "win_rate":     wins.mean() * 100,
        "avg_pct":      pcts_a.mean(),
        "avg_win":      pcts_a[wins].mean()   if wins.any()   else 0.0,
        "avg_loss":     pcts_a[~wins].mean()  if (~wins).any() else 0.0,
        "max_loss":     pcts_a.min(),
        "pnl_diff_pct": (pnls_a.sum() - orig_total_pnl) / abs(orig_total_pnl) * 100,
        "n_ts":         n_ts,
        "n_orig":       n_orig,
        "pnl_rescued":  pnl_rescued,
        "pcts_arr":     pcts_a,
        "exits_arr":    exits_a,
    })

gdf  = pd.DataFrame(grid_rows)
req  = gdf[gdf["days"] == REQUESTED_DAYS].iloc[0]
best = gdf.loc[gdf["total_pnl"].idxmax()]

# ── CONSOLE ───────────────────────────────────────────────────────────────────
SEP = "=" * 66
print(f"\n{SEP}")
print("ORIGINAL (no time-stop)")
print(f"  Total P&L : {fmt_b(orig_total_pnl)}")
print(f"  Win rate  : {orig_win_rate:.1f}%")
print(f"  Avg ret   : {fmt_p(orig_avg_pct)}  |  Avg gain: {fmt_p(orig_avg_win)}  |  Avg loss: {fmt_p(orig_avg_loss)}")
print(f"  Max loss  : {fmt_p(orig_max_loss)}")

print(f"\n{SEP}")
print(f"REQUESTED: Time-stop = {REQUESTED_DAYS} trading days")
print(f"  Total P&L    : {fmt_b(req['total_pnl'])}  ({req['pnl_diff_pct']:+.1f}% vs orig)")
print(f"  Win rate     : {req['win_rate']:.1f}%")
print(f"  Avg ret      : {fmt_p(req['avg_pct'])}  |  Avg gain: {fmt_p(req['avg_win'])}  |  Avg loss: {fmt_p(req['avg_loss'])}")
print(f"  Max loss     : {fmt_p(req['max_loss'])}")
print(f"  Time-stop exits : {int(req['n_ts'])}  |  Kept original: {int(req['n_orig'])}")
print(f"  P&L change on TS positions: {fmt_b(req['pnl_rescued'])}  "
      f"({'rescued loss' if req['pnl_rescued'] > 0 else 'extra cost'})")

print(f"\n{SEP}")
print(f"BEST COMBO: Time-stop = {int(best['days'])} trading days")
print(f"  Total P&L    : {fmt_b(best['total_pnl'])}  ({best['pnl_diff_pct']:+.1f}% vs orig)")
print(f"  Win rate     : {best['win_rate']:.1f}%")
print(f"  Avg ret      : {fmt_p(best['avg_pct'])}  |  Avg gain: {fmt_p(best['avg_win'])}  |  Avg loss: {fmt_p(best['avg_loss'])}")
print(f"  Time-stop exits : {int(best['n_ts'])}  |  Kept original: {int(best['n_orig'])}")

print(f"\n{SEP}")
print("Full grid:")
print(f"{'Days':>6} | {'P&L(B)':>10} {'vs orig':>9} {'WR':>7} {'AvgPct':>8} "
      f"{'AvgGain':>8} {'AvgLoss':>9} {'MaxLoss':>9} {'TS exits':>9} {'Rescued(B)':>11}")
print("-" * 95)
for _, r in gdf.sort_values("total_pnl", ascending=False).iterrows():
    marker = " <-- requested" if r["days"] == REQUESTED_DAYS else (
             " <-- BEST"     if r["days"] == best["days"]    else "")
    print(f"{int(r['days']):>6} | {r['total_pnl']/1e9:>10,.2f} {r['pnl_diff_pct']:>+8.1f}% "
          f"{r['win_rate']:>6.1f}% {r['avg_pct']:>7.2f}% "
          f"{r['avg_win']:>7.2f}% {r['avg_loss']:>8.2f}% {r['max_loss']:>8.2f}% "
          f"{int(r['n_ts']):>8}  {r['pnl_rescued']/1e9:>+9.2f}B{marker}")

# ── DETAIL: what positions got time-stopped at 45d ────────────────────────────
print(f"\n--- Positions exited by time-stop (day={REQUESTED_DAYS}) ---")
req_exits = req["exits_arr"]
detail_rows = []
for idx, (args, etype) in enumerate(zip(pos_list, req_exits)):
    if etype == "time_stop":
        pnl_sim  = req["pcts_arr"][idx]
        pnl_orig = args[7]
        detail_rows.append({
            "ticker":    args[0],
            "first_buy": args[1].strftime("%Y-%m-%d"),
            "orig_pct":  pnl_orig,
            "sim_pct":   pnl_sim,
            "saved_pct": pnl_orig - pnl_sim,   # negative = we exit worse, positive = we save
        })
detail_df = pd.DataFrame(detail_rows)
if not detail_df.empty:
    worse  = detail_df[detail_df["saved_pct"] < 0]
    better = detail_df[detail_df["saved_pct"] >= 0]
    print(f"  Total TS exits: {len(detail_df)}")
    print(f"  -> Better outcome (avoided deeper loss): {len(better)}")
    print(f"  -> Worse outcome (original recovered):   {len(worse)}")
    print(f"\n  Top 10 best saves (time-stop helped most):")
    for _, r in better.nlargest(10, "saved_pct").iterrows():
        print(f"    {r['ticker']:6s}  orig {r['orig_pct']:+6.1f}%  -> sim {r['sim_pct']:+6.1f}%  saved {r['saved_pct']:+5.1f}%")
    print(f"\n  Top 10 worst cuts (original would have recovered):")
    for _, r in worse.nsmallest(10, "saved_pct").iterrows():
        print(f"    {r['ticker']:6s}  orig {r['orig_pct']:+6.1f}%  -> sim {r['sim_pct']:+6.1f}%  cost  {r['saved_pct']:+5.1f}%")


# ── VISUALISATION ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 26), facecolor=DARK_BG)
fig.suptitle(f"Backtest: Time-Stop (exit if below cost after N trading days)",
             fontsize=20, fontweight="bold", color=TEXT_CLR, y=0.998)
gs = gridspec.GridSpec(3, 3, figure=fig,
                       hspace=0.48, wspace=0.35,
                       left=0.06, right=0.97, top=0.965, bottom=0.03)

def styled(ax, title):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_CLR, pad=8)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    ax.grid(True, axis="y"); return ax

COLORS = [BLUE, GREEN, YELLOW, PURPLE, RED]

# ── Row 0: P&L bar + Win rate + Avg loss per day threshold ───────────────────
ax0 = fig.add_subplot(gs[0, :])
styled(ax0, "Total P&L & Win Rate by Time-Stop Threshold  (vs Original)")

day_lbls = [f"{int(r['days'])}d" for _, r in gdf.iterrows()]
pnl_vals = [r["total_pnl"]/1e9 for _, r in gdf.iterrows()]
wr_vals  = [r["win_rate"]     for _, r in gdf.iterrows()]

x = np.arange(len(DAY_GRID) + 1)  # +1 for original
bar_lbls  = ["Original"] + day_lbls
bar_pnls  = [orig_total_pnl/1e9] + pnl_vals
bar_wrs   = [orig_win_rate] + wr_vals
bar_clrs  = [BLUE] + [GREEN if v >= orig_total_pnl/1e9 else YELLOW if v >= orig_total_pnl*0.9/1e9 else RED
                       for v in pnl_vals]

bars = ax0.bar(x, bar_pnls, color=bar_clrs, width=0.55, zorder=3, alpha=0.85)
ax0.axhline(orig_total_pnl/1e9, color=GRID_CLR, linewidth=1, linestyle="--", alpha=0.6)

ax_wr = ax0.twinx()
ax_wr.plot(x, bar_wrs, color=PURPLE, linewidth=2, marker="o", markersize=8,
           label="Win Rate %", zorder=4)
ax_wr.set_ylabel("Win Rate %", color=PURPLE)
ax_wr.tick_params(colors=PURPLE)
ax_wr.set_ylim(40, 70)

for bar, pnl, wr, lbl in zip(bars, bar_pnls, bar_wrs, bar_lbls):
    diff = "" if lbl == "Original" else f"\n({(pnl - orig_total_pnl/1e9):+.0f}B)"
    ax0.text(bar.get_x()+bar.get_width()/2, bar.get_height() + 5,
             f"WR {wr:.0f}%{diff}", ha="center", fontsize=9, color=TEXT_CLR)

ax0.set_xticks(x); ax0.set_xticklabels(bar_lbls, fontsize=10)
ax0.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
ax0.set_ylabel("Total P&L (B VND)")

# Highlight requested
req_x = DAY_GRID.index(REQUESTED_DAYS) + 1
ax0.get_children()[req_x].set_edgecolor(YELLOW)
ax0.get_children()[req_x].set_linewidth(3)
ax0.text(req_x, bar_pnls[req_x] + orig_total_pnl*0.02/1e9,
         "REQ", ha="center", fontsize=9, color=YELLOW, fontweight="bold")


# ── Row 1 col 0-1: Distribution overlay ──────────────────────────────────────
ax1 = fig.add_subplot(gs[1, :2])
styled(ax1, f"P&L Distribution: Original vs Time-Stop {REQUESTED_DAYS}d  vs  Best ({int(best['days'])}d)")
ax1.grid(True, axis="y")

orig_arr = pos_df["orig_pnl_pct"].values
req_arr  = req["pcts_arr"]
best_arr = best["pcts_arr"]
all_arr  = np.concatenate([orig_arr, req_arr, best_arr])
q01, q99 = np.percentile(all_arr[np.isfinite(all_arr)], [1, 99])
bins = np.linspace(q01, q99, 60)

ax1.hist(orig_arr, bins=bins, alpha=0.45, color=BLUE,
         label=f"Original  (mean {orig_avg_pct:.1f}%  WR {orig_win_rate:.0f}%)")
ax1.hist(req_arr,  bins=bins, alpha=0.55, color=GREEN,
         label=f"Time-stop {REQUESTED_DAYS}d  (mean {req['avg_pct']:.1f}%  WR {req['win_rate']:.0f}%)")
if best["days"] != REQUESTED_DAYS:
    ax1.hist(best_arr, bins=bins, alpha=0.35, color=YELLOW,
             label=f"Best {int(best['days'])}d  (mean {best['avg_pct']:.1f}%  WR {best['win_rate']:.0f}%)")

for v, c, ls in [(orig_avg_pct, BLUE, ":"), (req["avg_pct"], GREEN, ":")]:
    ax1.axvline(v, color=c, linewidth=1.4, linestyle=ls)
ax1.axvline(0, color=YELLOW, linewidth=1, linestyle="--", alpha=0.6)
ax1.legend(fontsize=9, framealpha=0.25)
ax1.set_xlabel("Return %"); ax1.set_ylabel("# Positions")
ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))


# ── Row 1 col 2: Exit pie ─────────────────────────────────────────────────────
ax2 = fig.add_subplot(gs[1, 2])
ax2.set_facecolor(PANEL_BG)
ax2.set_title(f"Exit Types  (Time-stop = {REQUESTED_DAYS}d)\n"
              f"TS: {int(req['n_ts'])}  |  Original: {int(req['n_orig'])}",
              fontsize=10, fontweight="bold", color=TEXT_CLR)
ea = req["exits_arr"]
pie_data = [("Time-Stop", (ea=="time_stop").sum(), RED),
            ("Original Exit", (ea=="original").sum(), BLUE),
            ("No Data", (ea=="no_data").sum(), GRID_CLR)]
pie_data = [(l, s, c) for l, s, c in pie_data if s > 0]
lbls, szs, clrs = zip(*pie_data)
wedges, texts, autos = ax2.pie(
    szs, labels=lbls, colors=clrs, autopct="%1.0f%%", startangle=90,
    textprops={"color": TEXT_CLR, "fontsize": 9},
    wedgeprops={"edgecolor": DARK_BG, "linewidth": 2},
    pctdistance=0.72,
)
for at in autos: at.set_color("black"); at.set_fontweight("bold")


# ── Row 2 left: Time-stop outcome breakdown (better vs worse) ─────────────────
ax3 = fig.add_subplot(gs[2, :2])
styled(ax3, f"Time-Stop {REQUESTED_DAYS}d: Per-Position Impact  (green = avoided loss, red = cut too early)")
ax3.grid(True, axis="y")

if not detail_df.empty:
    detail_sorted = detail_df.sort_values("saved_pct", ascending=False).reset_index(drop=True)
    clrs_bar = [GREEN if v >= 0 else RED for v in detail_sorted["saved_pct"]]
    ax3.bar(range(len(detail_sorted)), detail_sorted["saved_pct"], color=clrs_bar, width=1.0, zorder=3)
    ax3.axhline(0, color=GRID_CLR, linewidth=0.8)
    n_better = (detail_sorted["saved_pct"] >= 0).sum()
    n_worse  = (detail_sorted["saved_pct"] < 0).sum()
    ax3.text(0.02, 0.94, f"Avoided deeper loss: {n_better} positions",
             transform=ax3.transAxes, color=GREEN, fontsize=10, fontweight="bold")
    ax3.text(0.02, 0.87, f"Cut too early (orig recovered): {n_worse} positions",
             transform=ax3.transAxes, color=RED,   fontsize=10, fontweight="bold")
    ax3.set_xlabel("Position index (sorted by impact)")
    ax3.set_ylabel("% saved  (positive = helped)")
    ax3.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:+.0f}%"))


# ── Row 2 right: Avg loss comparison ─────────────────────────────────────────
ax4 = fig.add_subplot(gs[2, 2])
styled(ax4, "Key Metrics vs Time-Stop Threshold")
ax4.grid(True, axis="both")

metrics = {
    "Avg Loss %":  [orig_avg_loss]  + [r["avg_loss"]  for _, r in gdf.iterrows()],
    "Avg Return %":[orig_avg_pct]   + [r["avg_pct"]   for _, r in gdf.iterrows()],
    "Max Loss %":  [orig_max_loss]  + [r["max_loss"]  for _, r in gdf.iterrows()],
}
x_pts = [0] + list(range(1, len(DAY_GRID)+1))
x_lbls = ["Orig"] + [f"{d}d" for d in DAY_GRID]

for (name, vals), clr, mk in zip(metrics.items(), [RED, GREEN, PURPLE], ["o","s","^"]):
    ax4.plot(x_pts, vals, color=clr, linewidth=2, marker=mk, markersize=7, label=name)

ax4.set_xticks(x_pts); ax4.set_xticklabels(x_lbls, fontsize=9)
ax4.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:.0f}%"))
ax4.axhline(0, color=GRID_CLR, linewidth=0.6)
ax4.axvline(DAY_GRID.index(REQUESTED_DAYS)+1, color=YELLOW,
            linewidth=1.5, linestyle="--", alpha=0.7, label=f"{REQUESTED_DAYS}d (req)")
ax4.legend(fontsize=8, framealpha=0.25)

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved -> {Path(OUT_IMG).resolve()}")
