#!/usr/bin/env python3
"""
backtest_tp_sl.py
=================
Grid-search take-profit / cut-loss levels on historical closed positions.

For every closed position:
  - Track daily price vs. running average cost basis (handles DCA buys).
  - Exit when price first hits TP or SL; otherwise keep original exit.
  - Sweep a grid of TP × SL levels and compare aggregate metrics.
"""

import json
import subprocess
import sys
from io import StringIO
from itertools import product
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
LOGS_FILE = "portfolio_email_special_2026-04-07_15.14.52.jsonl"
PROJECT   = "lithe-record-440915-m9"
OUT_IMG   = "backtest_tp_sl.png"

TP_GRID = [0.08, 0.10, 0.15, 0.20, 0.25, 0.30]   # take-profit levels
SL_GRID = [0.03, 0.05, 0.07, 0.08, 0.10, 0.12]   # stop-loss levels
BQ_CHUNK = 150                                      # tickers per BQ query

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG  = "#0f1117"
PANEL_BG = "#1a1d27"
GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"
BLUE     = "#4fa3e0"
GREEN    = "#4ecb71"
RED      = "#e05c5c"
YELLOW   = "#f0c060"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor":   GRID_CLR, "axes.labelcolor": TEXT_CLR,
    "xtick.color":      TEXT_CLR, "ytick.color":    TEXT_CLR,
    "text.color":       TEXT_CLR, "grid.color":     GRID_CLR,
    "grid.linestyle":   "--",     "grid.alpha":     0.5,
    "font.family":      "DejaVu Sans",
})


# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_jsonl(path: str) -> pd.DataFrame:
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df["ymd"] = pd.to_datetime(df["ymd"])
    return df


BQ_BIN = r"bq"

def bq_query(sql: str) -> pd.DataFrame:
    cmd = [
        BQ_BIN, "query", "--use_legacy_sql=false",
        f"--project_id={PROJECT}", "--format=csv", "--max_rows=5000000", sql,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=300, shell=True)
    if r.returncode != 0:
        raise RuntimeError(r.stderr[:600])
    return pd.read_csv(StringIO(r.stdout))


# ── LOAD TRANSACTIONS ─────────────────────────────────────────────────────────
print("Loading transactions …")
tx = load_jsonl(TX_FILE)
tx.sort_values("ymd", inplace=True)

# ── BUILD CLOSED POSITIONS ────────────────────────────────────────────────────
print("Building positions …")
pos_records = []
for hid, grp in tx.groupby("holding_id"):
    buys  = grp[grp["action"] == "buy"].sort_values("ymd")
    sells = grp[grp["action"] == "sell"].sort_values("ymd")
    if sells.empty:
        continue                          # skip open positions

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
n_pos  = len(pos_df)
n_tick = pos_df["ticker"].nunique()
print(f"  {n_pos} closed positions  |  {n_tick} unique tickers")


# ── FETCH DAILY PRICES FROM BIGQUERY ─────────────────────────────────────────
tickers  = pos_df["ticker"].unique().tolist()
date_min = pos_df["first_buy"].min().strftime("%Y-%m-%d")
date_max = pos_df["last_sell"].max().strftime("%Y-%m-%d")
total_chunks = -(-len(tickers) // BQ_CHUNK)
print(f"Fetching prices: {len(tickers)} tickers  |  {date_min} -> {date_max}  |  {total_chunks} chunks …")

frames = []
for i in range(0, len(tickers), BQ_CHUNK):
    chunk = tickers[i : i + BQ_CHUNK]
    tstr  = ", ".join(f'"{t}"' for t in chunk)
    sql   = (
        f'SELECT t.ticker, t.time, t.Close '
        f'FROM tav2_bq.ticker AS t '
        f'WHERE t.ticker IN ({tstr}) '
        f'  AND t.time BETWEEN "{date_min}" AND "{date_max}" '
        f'ORDER BY t.ticker, t.time'
    )
    df = bq_query(sql)
    df["time"] = pd.to_datetime(df["time"])
    frames.append(df)
    print(f"  chunk {i//BQ_CHUNK + 1}/{total_chunks}: {len(df):,} rows")

prices_df = pd.concat(frames, ignore_index=True)
print(f"  Total price rows: {len(prices_df):,}")

# price_map: ticker -> pd.Series(DatetimeIndex -> Close)
price_map: dict[str, pd.Series] = {
    ticker: grp.set_index("time")["Close"].sort_index()
    for ticker, grp in prices_df.groupby("ticker")
}


# ── SIMULATE ONE POSITION ─────────────────────────────────────────────────────
def simulate_one(
    ticker: str,
    first_buy: pd.Timestamp,
    last_sell: pd.Timestamp,
    buys_df: pd.DataFrame,
    total_inv: float,
    total_fees: float,
    orig_pnl: float,
    orig_pnl_pct: float,
    tp_pct: float,
    sl_pct: float,
) -> tuple[float, float, str, int | None]:
    """
    Returns (sim_pnl, sim_pnl_pct, exit_type, holding_days).

    exit_type is one of: 'take_profit', 'cut_loss', 'original', 'no_data'.

    Cost basis tracks running avg of buys processed so far (handles DCA).
    P&L denominator for early exits uses only cum_inv (not full total_inv).
    """
    if ticker not in price_map:
        return orig_pnl, orig_pnl_pct, "no_data", None

    series = price_map[ticker]
    try:
        window = series.loc[first_buy : last_sell]
    except Exception:
        return orig_pnl, orig_pnl_pct, "original", None
    if window.empty:
        return orig_pnl, orig_pnl_pct, "original", None

    buy_list = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr  = 0
    n_buys   = len(buy_list)
    cum_inv  = 0.0
    cum_sh   = 0.0

    for date, close in window.items():
        if pd.isna(close) or close <= 0:
            continue

        # Absorb any buys that have occurred on or before this date
        while buy_ptr < n_buys and buy_list[buy_ptr].ymd <= date:
            b = buy_list[buy_ptr]
            if b.adj_price > 0:
                cum_sh  += b.buy_amount / b.adj_price
                cum_inv += b.buy_amount
            buy_ptr += 1

        # Nothing to sell yet, or don't trigger on the exact buy date
        if cum_sh <= 0 or date == first_buy:
            continue

        avg_cost = cum_inv / cum_sh
        # Use cum_inv for early-exit denom (only invested amount so far)
        denom = cum_inv + total_fees

        # ── Take Profit ───────────────────────────────────────────────────────
        if close >= avg_cost * (1 + tp_pct):
            proc = close * cum_sh
            return (
                proc - denom,
                (proc / denom - 1) * 100,
                "take_profit",
                (date - first_buy).days,
            )

        # ── Cut Loss ──────────────────────────────────────────────────────────
        if close <= avg_cost * (1 - sl_pct):
            proc = close * cum_sh
            return (
                proc - denom,
                (proc / denom - 1) * 100,
                "cut_loss",
                (date - first_buy).days,
            )

    # Neither triggered -> keep original exit
    return orig_pnl, orig_pnl_pct, "original", (last_sell - first_buy).days


# ── BASELINE ─────────────────────────────────────────────────────────────────
orig_total_pnl = pos_df["orig_pnl"].sum()
orig_win_rate  = (pos_df["orig_pnl_pct"] > 0).mean() * 100
orig_avg_pct   = pos_df["orig_pnl_pct"].mean()
orig_avg_win   = pos_df[pos_df["orig_pnl_pct"] > 0]["orig_pnl_pct"].mean()
orig_avg_loss  = pos_df[pos_df["orig_pnl_pct"] <= 0]["orig_pnl_pct"].mean()
orig_max_loss  = pos_df["orig_pnl_pct"].min()

# Pre-extract rows into a plain list for speed (avoid DataFrame row overhead)
pos_list = [
    (
        row["ticker"], row["first_buy"], row["last_sell"], row["buys_df"],
        row["total_inv"], row["total_fees"], row["orig_pnl"], row["orig_pnl_pct"],
    )
    for _, row in pos_df.iterrows()
]

# ── GRID SEARCH ───────────────────────────────────────────────────────────────
n_combos = len(TP_GRID) * len(SL_GRID)
print(f"\nGrid search: {len(TP_GRID)} TP × {len(SL_GRID)} SL = {n_combos} combos …")

grid_rows = []
for tp, sl in product(TP_GRID, SL_GRID):
    pnls, pcts, exits = [], [], []
    for args in pos_list:
        pnl, pct_v, etype, _ = simulate_one(*args, tp, sl)
        pnls.append(pnl)
        pcts.append(pct_v)
        exits.append(etype)

    pnls_a  = np.array(pnls,  dtype=float)
    pcts_a  = np.array(pcts,  dtype=float)
    exits_a = np.array(exits)
    wins    = pcts_a > 0
    losses  = pcts_a <= 0

    grid_rows.append({
        "tp":          tp,
        "sl":          sl,
        "total_pnl":   pnls_a.sum(),
        "win_rate":    wins.mean() * 100,
        "avg_pct":     pcts_a.mean(),
        "avg_win":     pcts_a[wins].mean()   if wins.any()   else 0.0,
        "avg_loss":    pcts_a[losses].mean() if losses.any() else 0.0,
        "max_loss":    pcts_a.min(),
        "n_tp":        (exits_a == "take_profit").sum(),
        "n_sl":        (exits_a == "cut_loss").sum(),
        "n_orig":      (exits_a == "original").sum(),
        "pnl_diff_pct": (pnls_a.sum() - orig_total_pnl) / abs(orig_total_pnl) * 100,
        "pcts_arr":    pcts_a,   # kept for distribution chart
        "exits_arr":   exits_a,
    })

gdf  = pd.DataFrame(grid_rows)
best = gdf.loc[gdf["total_pnl"].idxmax()]

# ── CONSOLE SUMMARY ───────────────────────────────────────────────────────────
SEP = "=" * 58
print(f"\n{SEP}")
print("ORIGINAL  (no TP/SL overlay)")
print(f"  Total P&L  : {orig_total_pnl/1e9:,.2f} B VND")
print(f"  Win rate   : {orig_win_rate:.1f}%")
print(f"  Avg return : {orig_avg_pct:.2f}%")
print(f"  Avg gain   : {orig_avg_win:.2f}%")
print(f"  Avg loss   : {orig_avg_loss:.2f}%")
print(f"  Max loss   : {orig_max_loss:.2f}%")
print(SEP)
print(f"BEST COMBO  TP = {best['tp']*100:.0f}%   SL = {best['sl']*100:.0f}%")
print(f"  Total P&L  : {best['total_pnl']/1e9:,.2f} B VND  ({best['pnl_diff_pct']:+.1f}% vs orig)")
print(f"  Win rate   : {best['win_rate']:.1f}%")
print(f"  Avg return : {best['avg_pct']:.2f}%")
print(f"  Avg gain   : {best['avg_win']:.2f}%")
print(f"  Avg loss   : {best['avg_loss']:.2f}%")
print(f"  Max loss   : {best['max_loss']:.2f}%")
print(f"  TP exits   : {int(best['n_tp'])}  |  SL exits: {int(best['n_sl'])}  |  No trigger: {int(best['n_orig'])}")
print(SEP)

# Print full grid table
print("\nFull grid (sorted by Total P&L):")
print(f"{'TP':>5} {'SL':>5} | {'TotalPnL(B)':>12} {'vs orig':>9} {'WinRate':>8} "
      f"{'AvgPct':>8} {'AvgWin':>8} {'AvgLoss':>9} {'MaxLoss':>9}")
print("-" * 80)
for _, r in gdf.sort_values("total_pnl", ascending=False).iterrows():
    print(f"{r['tp']*100:4.0f}% {r['sl']*100:4.0f}% | "
          f"{r['total_pnl']/1e9:>12,.2f} {r['pnl_diff_pct']:>+8.1f}% "
          f"{r['win_rate']:>7.1f}% {r['avg_pct']:>7.2f}% "
          f"{r['avg_win']:>7.2f}% {r['avg_loss']:>8.2f}% {r['max_loss']:>8.2f}%")


# ── VISUALISATION ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 26), facecolor=DARK_BG)
fig.suptitle("Backtest: Take-Profit / Cut-Loss Grid Search",
             fontsize=22, fontweight="bold", color=TEXT_CLR, y=0.995)
gs = gridspec.GridSpec(
    3, 3, figure=fig,
    hspace=0.48, wspace=0.38,
    left=0.07, right=0.97, top=0.96, bottom=0.03,
)

TP_LBL = [f"{int(t*100)}%" for t in TP_GRID]
SL_LBL = [f"{int(s*100)}%" for s in SL_GRID]


def make_matrix(col: str) -> np.ndarray:
    mat = np.zeros((len(TP_GRID), len(SL_GRID)))
    for r in grid_rows:
        i = TP_GRID.index(r["tp"])
        j = SL_GRID.index(r["sl"])
        mat[i, j] = r[col]
    return mat


def draw_heatmap(ax, mat, title, fmt="{:.1f}", colors=None, cbar_label=""):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_CLR)
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    cmap = LinearSegmentedColormap.from_list(
        "c", colors or [RED, PANEL_BG, GREEN], N=256
    )
    im = ax.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")
    ax.set_xticks(range(len(SL_GRID))); ax.set_xticklabels(SL_LBL, fontsize=9)
    ax.set_yticks(range(len(TP_GRID))); ax.set_yticklabels(TP_LBL, fontsize=9)
    ax.set_xlabel("Stop-Loss %",   fontsize=9)
    ax.set_ylabel("Take-Profit %", fontsize=9)
    vmin, vmax = mat.min(), mat.max()
    mid = (vmin + vmax) / 2
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            tc = "black" if abs(v - mid) > (vmax - vmin) * 0.25 else TEXT_CLR
            ax.text(j, i, fmt.format(v), ha="center", va="center",
                    fontsize=8.5, color=tc, fontweight="bold")
    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.tick_params(colors=TEXT_CLR)
    if cbar_label:
        cb.set_label(cbar_label, color=TEXT_CLR, fontsize=8)


# ── Row 0: three heatmaps ─────────────────────────────────────────────────────
bi = TP_GRID.index(best["tp"])
bj = SL_GRID.index(best["sl"])

ax0 = fig.add_subplot(gs[0, 0])
draw_heatmap(ax0, make_matrix("pnl_diff_pct"),
             f"ΔP&L vs Original (%)\n[orig: {orig_total_pnl/1e9:,.1f}B VND]",
             fmt="{:+.1f}", colors=[RED, PANEL_BG, GREEN], cbar_label="%")
ax0.add_patch(plt.Rectangle((bj-0.5, bi-0.5), 1, 1,
              fill=False, edgecolor=YELLOW, linewidth=2.5, zorder=5))
ax0.text(bj, bi - 0.35, "* BEST", ha="center", fontsize=7,
         color=YELLOW, fontweight="bold", zorder=6)

ax1 = fig.add_subplot(gs[0, 1])
draw_heatmap(ax1, make_matrix("win_rate"),
             f"Win Rate (%)\n[orig: {orig_win_rate:.1f}%]",
             fmt="{:.1f}", colors=[RED, PANEL_BG, GREEN], cbar_label="%")
ax1.add_patch(plt.Rectangle((bj-0.5, bi-0.5), 1, 1,
              fill=False, edgecolor=YELLOW, linewidth=2.5, zorder=5))

ax2 = fig.add_subplot(gs[0, 2])
draw_heatmap(ax2, make_matrix("avg_loss"),
             f"Avg Loss % (higher=worse)\n[orig: {orig_avg_loss:.1f}%]",
             fmt="{:.1f}", colors=[GREEN, PANEL_BG, RED], cbar_label="%")
ax2.add_patch(plt.Rectangle((bj-0.5, bi-0.5), 1, 1,
              fill=False, edgecolor=YELLOW, linewidth=2.5, zorder=5))

# ── Row 1: distribution + exit-type pie ──────────────────────────────────────
ax3 = fig.add_subplot(gs[1, :2])
ax3.set_title(
    f"P&L Distribution: Original  vs  Best combo  (TP={best['tp']*100:.0f}% / SL={best['sl']*100:.0f}%)",
    fontsize=11, fontweight="bold", color=TEXT_CLR,
)
ax3.spines[["top", "right", "left", "bottom"]].set_visible(False)
ax3.grid(True, axis="y")

orig_pcts_arr = pos_df["orig_pnl_pct"].values
best_pcts_arr = best["pcts_arr"]
combined = np.concatenate([orig_pcts_arr, best_pcts_arr])
q01, q99 = np.percentile(combined, [1, 99])
bins = np.linspace(q01, q99, 55)

ax3.hist(orig_pcts_arr, bins=bins, alpha=0.55, color=BLUE,
         label=f"Original  (mean {orig_avg_pct:.1f}%  |  WR {orig_win_rate:.0f}%)")
ax3.hist(best_pcts_arr, bins=bins, alpha=0.55, color=GREEN,
         label=f"TP {best['tp']*100:.0f}% / SL {best['sl']*100:.0f}%"
               f"  (mean {best['avg_pct']:.1f}%  |  WR {best['win_rate']:.0f}%)")
ax3.axvline(0, color=YELLOW, linewidth=1.2, linestyle="--", alpha=0.7)
ax3.axvline(orig_avg_pct,      color=BLUE,  linewidth=1.2, linestyle=":")
ax3.axvline(best["avg_pct"],   color=GREEN, linewidth=1.2, linestyle=":")
ax3.legend(fontsize=10, framealpha=0.25)
ax3.set_xlabel("Return %"); ax3.set_ylabel("# Positions")
ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

ax4 = fig.add_subplot(gs[1, 2])
ax4.set_facecolor(PANEL_BG)
ax4.set_title(
    f"Exit Types  (TP={best['tp']*100:.0f}% / SL={best['sl']*100:.0f}%)",
    fontsize=11, fontweight="bold", color=TEXT_CLR,
)
ea = best["exits_arr"]
pie_data = [
    ("Take Profit",   (ea == "take_profit").sum(), GREEN),
    ("Cut Loss",      (ea == "cut_loss").sum(),     RED),
    ("Original Exit", (ea == "original").sum(),     BLUE),
    ("No Data",       (ea == "no_data").sum(),      GRID_CLR),
]
pie_data = [(l, s, c) for l, s, c in pie_data if s > 0]
lbls, szs, clrs = zip(*pie_data)
wedges, texts, autos = ax4.pie(
    szs, labels=lbls, colors=clrs, autopct="%1.0f%%", startangle=90,
    textprops={"color": TEXT_CLR, "fontsize": 9},
    wedgeprops={"edgecolor": DARK_BG, "linewidth": 2},
    pctdistance=0.72,
)
for at in autos:
    at.set_color("black"); at.set_fontweight("bold")

# ── Row 2: Top combos + original bar chart ────────────────────────────────────
ax5 = fig.add_subplot(gs[2, :])
ax5.set_title("Total Realised P&L — Original vs Top-8 TP/SL Combos",
              fontsize=11, fontweight="bold", color=TEXT_CLR)
ax5.spines[["top", "right", "left", "bottom"]].set_visible(False)
ax5.grid(True, axis="y")

top8 = gdf.nlargest(8, "total_pnl")
bar_items = [("Original\n(no TP/SL)", orig_total_pnl, BLUE, orig_win_rate)]
for _, r in top8.iterrows():
    lbl = f"TP {r['tp']*100:.0f}%\nSL {r['sl']*100:.0f}%"
    clr = GREEN if r["total_pnl"] >= orig_total_pnl else RED
    bar_items.append((lbl, r["total_pnl"], clr, r["win_rate"]))

bar_lbls = [b[0] for b in bar_items]
bar_vals = [b[1] / 1e9 for b in bar_items]
bar_clrs = [b[2] for b in bar_items]
bar_wr   = [b[3] for b in bar_items]

bars = ax5.bar(range(len(bar_items)), bar_vals, color=bar_clrs, width=0.6, zorder=3, alpha=0.85)
ax5.set_xticks(range(len(bar_items)))
ax5.set_xticklabels(bar_lbls, fontsize=9)
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.1f}B"))
ax5.set_ylabel("Total P&L (B VND)")
ax5.axhline(orig_total_pnl / 1e9, color=YELLOW, linewidth=1, linestyle="--", alpha=0.5)

for bar, wr, val in zip(bars, bar_wr, bar_vals):
    sign = "+" if val >= orig_total_pnl / 1e9 else ""
    diff = val - orig_total_pnl / 1e9
    label = f"WR {wr:.0f}%\n{sign}{diff:+.1f}B" if bar_lbls[bars.patches.index(bar)] != "Original\n(no TP/SL)" else f"WR {wr:.0f}%"
    ax5.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + abs(max(bar_vals)) * 0.008,
        f"WR {wr:.0f}%",
        ha="center", fontsize=8.5, color=TEXT_CLR,
    )

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved -> {Path(OUT_IMG).resolve()}")
