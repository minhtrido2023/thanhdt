#!/usr/bin/env python3
"""
Portfolio visualization - reads JSONL input files and renders charts.
"""

import sys
import json
import io
from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as mticker
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patches as mpatches

# ── Reuse helpers from analyze_portfolio ────────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from analyze_portfolio import (
    compute_positions, transaction_summary,
    portfolio_overview, yearly_breakdown, top_positions, most_traded,
)

# ── Config ───────────────────────────────────────────────────────────────────
LOGS_FILE   = "portfolio_email_2026-04-07_00.31.17.jsonl"
TX_FILE     = "transactions_email_2026-04-07_00.28.31.jsonl"
OUT_IMAGE   = "portfolio_report.png"

DARK_BG     = "#0f1117"
PANEL_BG    = "#1a1d27"
GRID_CLR    = "#2a2d3a"
TEXT_CLR    = "#e0e0e0"
ACCENT_BLUE = "#4fa3e0"
ACCENT_GRN  = "#4ecb71"
ACCENT_RED  = "#e05c5c"
ACCENT_YLW  = "#f0c060"

def vnd_b(v): return f"{v/1e9:,.1f}B"
def pct_s(v): sign = "+" if v >= 0 else ""; return f"{sign}{v:.1f}%"

# ── Load ──────────────────────────────────────────────────────────────────────
def load_jsonl(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df["ymd"] = pd.to_datetime(df["ymd"])
    return df

logs = load_jsonl(LOGS_FILE)
tx   = load_jsonl(TX_FILE)
logs.sort_values("ymd", inplace=True)
tx.sort_values("ymd", inplace=True)

positions = compute_positions(tx)
overview  = portfolio_overview(logs)
summary   = transaction_summary(tx, positions)
yearly    = yearly_breakdown(logs, tx)
top, bottom = top_positions(positions, n=10)

# Drawdown series
logs2 = logs.copy()
logs2["rolling_peak"] = logs2["nav"].cummax()
logs2["drawdown_pct"] = (logs2["nav"] - logs2["rolling_peak"]) / logs2["rolling_peak"] * 100

# ── Figure layout ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": DARK_BG,
    "axes.facecolor":   PANEL_BG,
    "axes.edgecolor":   GRID_CLR,
    "axes.labelcolor":  TEXT_CLR,
    "xtick.color":      TEXT_CLR,
    "ytick.color":      TEXT_CLR,
    "text.color":       TEXT_CLR,
    "grid.color":       GRID_CLR,
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
    "axes.titlecolor":  TEXT_CLR,
    "axes.titlepad":    8,
})

fig = plt.figure(figsize=(22, 28), facecolor=DARK_BG)
fig.suptitle("Portfolio Simulation Report", fontsize=22, fontweight="bold",
             color=TEXT_CLR, y=0.995)

gs = gridspec.GridSpec(
    5, 3,
    figure=fig,
    hspace=0.52,
    wspace=0.32,
    left=0.06, right=0.97,
    top=0.97, bottom=0.03,
)

# ── Helper ────────────────────────────────────────────────────────────────────
def styled_ax(ax, title):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_CLR)
    ax.grid(True, axis="y")
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    return ax


# ══════════════════════════════════════════════════════════════════════════════
# 1. NAV over time  (full width row 0)
# ══════════════════════════════════════════════════════════════════════════════
ax_nav = fig.add_subplot(gs[0, :])
styled_ax(ax_nav, "Portfolio NAV over Time")

dates = logs2["ymd"]
nav   = logs2["nav"] / 1e9   # billions

ax_nav.fill_between(dates, nav, alpha=0.15, color=ACCENT_BLUE)
ax_nav.plot(dates, nav, color=ACCENT_BLUE, linewidth=1.5, label="NAV (B VND)")

# Annotate start / end / peak
ax_nav.axhline(overview["initial_nav"]/1e9, color=GRID_CLR, linewidth=0.8, linestyle=":")
peak_idx = logs2["nav"].idxmax()
ax_nav.annotate(f"Peak\n{vnd_b(overview['peak_nav'])}",
                xy=(logs2.loc[peak_idx,"ymd"], overview["peak_nav"]/1e9),
                xytext=(0, 18), textcoords="offset points",
                arrowprops=dict(arrowstyle="->", color=ACCENT_YLW),
                color=ACCENT_YLW, fontsize=8, ha="center")

ax_nav.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:,.0f}B"))
ax_nav.set_ylabel("NAV (B VND)")

# Shade yearly bands
for _, yr in yearly.iterrows():
    yr_logs = logs2[logs2["ymd"].dt.year == yr["year"]]
    if yr_logs.empty: continue
    clr = ACCENT_GRN if yr["return_pct"] >= 0 else ACCENT_RED
    ax_nav.axvspan(yr_logs["ymd"].iloc[0], yr_logs["ymd"].iloc[-1],
                   alpha=0.04, color=clr)
    mid = yr_logs["ymd"].iloc[len(yr_logs)//2]
    ax_nav.text(mid, nav.min()*0.99,
                f"{int(yr['year'])}\n{pct_s(yr['return_pct'])}",
                ha="center", fontsize=7, color=clr, alpha=0.85)

ax_nav.legend(loc="upper left", fontsize=9, framealpha=0.2)

# Key stats strip
kv = [
    ("Period", f"{overview['start_date']} → {overview['end_date']}"),
    ("Total Return", pct_s(overview["total_return"])),
    ("CAGR", pct_s(overview["cagr"])),
    ("Max Drawdown", pct_s(overview["max_drawdown"])),
    ("Win Rate", f"{summary['win_rate']:.1f}%"),
    ("Positions", f"{summary['num_positions']}"),
]
for i,(k,v) in enumerate(kv):
    ax_nav.text(0.01 + i*0.165, 1.06, f"{k}: ", transform=ax_nav.transAxes,
                fontsize=8.5, color="#888", ha="left")
    clr = ACCENT_GRN if ("+" in str(v) and "%" in str(v)) else (
          ACCENT_RED if ("-" in str(v) and "%" in str(v)) else TEXT_CLR)
    ax_nav.text(0.01 + i*0.165 + 0.065, 1.06, v, transform=ax_nav.transAxes,
                fontsize=8.5, color=clr, ha="left", fontweight="bold")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Drawdown  (full width row 1)
# ══════════════════════════════════════════════════════════════════════════════
ax_dd = fig.add_subplot(gs[1, :])
styled_ax(ax_dd, "Drawdown from Peak (%)")

dd = logs2["drawdown_pct"]
ax_dd.fill_between(dates, dd, 0, alpha=0.4, color=ACCENT_RED)
ax_dd.plot(dates, dd, color=ACCENT_RED, linewidth=0.8)
ax_dd.axhline(0, color=GRID_CLR, linewidth=0.6)

# Mark max drawdown
md_idx = dd.idxmin()
ax_dd.annotate(f"Max DD\n{dd[md_idx]:.1f}%",
               xy=(logs2.loc[md_idx,"ymd"], dd[md_idx]),
               xytext=(0,-22), textcoords="offset points",
               arrowprops=dict(arrowstyle="->", color=ACCENT_YLW),
               color=ACCENT_YLW, fontsize=8, ha="center")
ax_dd.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.0f}%"))
ax_dd.set_ylabel("Drawdown (%)")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Yearly returns bar  (row 2, col 0)
# ══════════════════════════════════════════════════════════════════════════════
ax_yr = fig.add_subplot(gs[2, 0])
styled_ax(ax_yr, "Year-by-Year Returns")

years_list = yearly["year"].astype(int).tolist()
rets  = yearly["return_pct"].tolist()
clrs  = [ACCENT_GRN if r >= 0 else ACCENT_RED for r in rets]

bars = ax_yr.bar(years_list, rets, color=clrs, width=0.6, zorder=3)
ax_yr.axhline(0, color=GRID_CLR, linewidth=0.8)
ax_yr.set_xticks(years_list)
ax_yr.set_xticklabels([str(y) for y in years_list], rotation=45, ha="right", fontsize=8)
ax_yr.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.0f}%"))
for bar, r in zip(bars, rets):
    ax_yr.text(bar.get_x()+bar.get_width()/2, bar.get_height() + (0.5 if r>=0 else -2.5),
               f"{r:.1f}%", ha="center", va="bottom" if r>=0 else "top",
               fontsize=7, color=TEXT_CLR)


# ══════════════════════════════════════════════════════════════════════════════
# 4. Win/Loss pie  (row 2, col 1)
# ══════════════════════════════════════════════════════════════════════════════
ax_pie = fig.add_subplot(gs[2, 1])
ax_pie.set_facecolor(PANEL_BG)
ax_pie.set_title("Closed Positions: Win vs Loss", fontsize=11, fontweight="bold", color=TEXT_CLR)

closed = positions[positions["status"] == "closed"]
wins   = (closed["pnl"] > 0).sum()
losses = len(closed) - wins
wedges, texts, autotexts = ax_pie.pie(
    [wins, losses],
    labels=[f"Win ({wins})", f"Loss ({losses})"],
    colors=[ACCENT_GRN, ACCENT_RED],
    autopct="%1.1f%%", startangle=90,
    textprops={"color": TEXT_CLR, "fontsize": 10},
    wedgeprops={"edgecolor": DARK_BG, "linewidth": 2},
    pctdistance=0.75,
)
for at in autotexts: at.set_color(DARK_BG); at.set_fontweight("bold")


# ══════════════════════════════════════════════════════════════════════════════
# 5. P&L distribution histogram  (row 2, col 2)
# ══════════════════════════════════════════════════════════════════════════════
ax_hist = fig.add_subplot(gs[2, 2])
styled_ax(ax_hist, "Return Distribution (Closed Positions)")

pnl_pcts = closed["pnl_pct"].dropna()
bins_edges = np.linspace(pnl_pcts.quantile(0.01), pnl_pcts.quantile(0.99), 40)
n, bins_e, patches = ax_hist.hist(pnl_pcts, bins=bins_edges, edgecolor=PANEL_BG, linewidth=0.4)
for patch, left in zip(patches, bins_e[:-1]):
    patch.set_facecolor(ACCENT_GRN if left >= 0 else ACCENT_RED)
ax_hist.axvline(0, color=ACCENT_YLW, linewidth=1, linestyle="--")
ax_hist.axvline(pnl_pcts.mean(), color=ACCENT_BLUE, linewidth=1, linestyle="--",
                label=f"Mean {pnl_pcts.mean():.1f}%")
ax_hist.legend(fontsize=8, framealpha=0.2)
ax_hist.set_xlabel("Return %")
ax_hist.set_ylabel("Count")
ax_hist.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x:.0f}%"))


# ══════════════════════════════════════════════════════════════════════════════
# 6. Top 10 Winners  (row 3, col 0-1)
# ══════════════════════════════════════════════════════════════════════════════
ax_top = fig.add_subplot(gs[3, :2])
styled_ax(ax_top, "Top 10 Most Profitable Positions (Realised P&L)")

top_plot = top.copy().reset_index(drop=True)
tickers_t = [f"{row['ticker']}" for _,row in top_plot.iterrows()]
pnls_t    = top_plot["pnl"] / 1e6  # millions

bars_t = ax_top.barh(range(len(tickers_t)), pnls_t, color=ACCENT_GRN, height=0.6, zorder=3)
ax_top.set_yticks(range(len(tickers_t)))
ax_top.set_yticklabels(tickers_t, fontsize=9)
ax_top.invert_yaxis()
ax_top.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e3:,.0f}B"))
ax_top.set_xlabel("P&L (B VND)")
for i,(bar,(_,row)) in enumerate(zip(bars_t, top_plot.iterrows())):
    pct_val = row["pnl_pct"] if row["pnl_pct"] is not None else 0
    ax_top.text(bar.get_width()+abs(pnls_t.max())*0.01, bar.get_y()+bar.get_height()/2,
                f"{pct_s(pct_val)}", va="center", fontsize=8, color=ACCENT_GRN)


# ══════════════════════════════════════════════════════════════════════════════
# 7. Top 10 Losers  (row 3, col 2)
# ══════════════════════════════════════════════════════════════════════════════
ax_bot = fig.add_subplot(gs[3, 2])
styled_ax(ax_bot, "Top 10 Biggest Losses")

bot_plot = bottom.copy().reset_index(drop=True)
tickers_b = [row["ticker"] for _,row in bot_plot.iterrows()]
pnls_b    = bot_plot["pnl"] / 1e6

bars_b = ax_bot.barh(range(len(tickers_b)), pnls_b, color=ACCENT_RED, height=0.6, zorder=3)
ax_bot.set_yticks(range(len(tickers_b)))
ax_bot.set_yticklabels(tickers_b, fontsize=9)
ax_bot.invert_yaxis()
ax_bot.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x,_: f"{x/1e3:,.0f}B"))
ax_bot.set_xlabel("P&L (B VND)")
for bar,(_,row) in zip(bars_b, bot_plot.iterrows()):
    pct_val = row["pnl_pct"] if row["pnl_pct"] is not None else 0
    ax_bot.text(bar.get_width() - abs(pnls_b.min())*0.01, bar.get_y()+bar.get_height()/2,
                f"{pct_s(pct_val)}", va="center", ha="right", fontsize=8, color=ACCENT_RED)


# ══════════════════════════════════════════════════════════════════════════════
# 8. Monthly trading activity heatmap  (row 4, col 0-1)
# ══════════════════════════════════════════════════════════════════════════════
ax_hm = fig.add_subplot(gs[4, :2])
ax_hm.set_title("Monthly Trading Activity (# Trades)", fontsize=11, fontweight="bold", color=TEXT_CLR)
ax_hm.set_facecolor(PANEL_BG)
ax_hm.spines[["top","right","left","bottom"]].set_visible(False)

tx2 = tx.copy()
tx2["year"]  = tx2["ymd"].dt.year
tx2["month"] = tx2["ymd"].dt.month
heat = tx2.groupby(["year","month"]).size().unstack(fill_value=0)

all_years  = sorted(heat.index.tolist())
all_months = list(range(1,13))
mat = np.zeros((len(all_years), 12))
for i,yr in enumerate(all_years):
    for j,mo in enumerate(all_months):
        mat[i,j] = heat.loc[yr, mo] if mo in heat.columns else 0

cmap = LinearSegmentedColormap.from_list("trades", ["#1a1d27","#4fa3e0","#f0c060"], N=256)
im = ax_hm.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")

mon_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ax_hm.set_xticks(range(12)); ax_hm.set_xticklabels(mon_labels, color=TEXT_CLR, fontsize=8)
ax_hm.set_yticks(range(len(all_years))); ax_hm.set_yticklabels(all_years, color=TEXT_CLR, fontsize=8)
ax_hm.tick_params(length=0)

for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        v = int(mat[i,j])
        if v > 0:
            ax_hm.text(j, i, str(v), ha="center", va="center",
                       fontsize=6.5, color="white" if v > mat.max()*0.5 else TEXT_CLR)

plt.colorbar(im, ax=ax_hm, fraction=0.02, pad=0.02, label="# Trades")


# ══════════════════════════════════════════════════════════════════════════════
# 9. Holdings over time  (row 4, col 2)
# ══════════════════════════════════════════════════════════════════════════════
ax_hold = fig.add_subplot(gs[4, 2])
styled_ax(ax_hold, "# Holdings over Time")

ax_hold.fill_between(logs2["ymd"], logs2["num_holdings"], alpha=0.3, color=ACCENT_YLW)
ax_hold.plot(logs2["ymd"], logs2["num_holdings"], color=ACCENT_YLW, linewidth=1)
ax_hold.axhline(logs2["num_holdings"].mean(), color=ACCENT_BLUE, linestyle="--", linewidth=0.8,
                label=f"Avg {logs2['num_holdings'].mean():.1f}")
ax_hold.legend(fontsize=8, framealpha=0.2)
ax_hold.set_ylabel("# Positions")
ax_hold.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))


# ── Save ──────────────────────────────────────────────────────────────────────
plt.savefig(OUT_IMAGE, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"Chart saved to: {Path(OUT_IMAGE).resolve()}")
