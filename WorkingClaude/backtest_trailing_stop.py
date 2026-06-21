#!/usr/bin/env python3
"""
backtest_trailing_stop.py
=========================
Trailing-stop backtest:
  - Bluechip (top-30 by avg daily value 2023-2025): trailing stop = 10%
  - SME (everyone else): trailing stop = 15%

For every closed position:
  - Track running peak price since first buy (DCA-aware cost basis).
  - Exit when Close drops >= trailing_pct from the running peak.
  - If never triggered -> keep original exit.
Compare aggregate metrics vs original (no overlay).
"""

import json
import subprocess
import sys
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
TX_FILE    = "transactions_email_special_2026-04-07_15.14.47.jsonl"
LOGS_FILE  = "portfolio_email_special_2026-04-07_15.14.52.jsonl"
VOL_RANK   = "ticker_volume_rank.csv"   # pre-fetched earlier
PROJECT    = "lithe-record-440915-m9"
OUT_IMG    = "backtest_trailing_stop.png"
BQ_CHUNK   = 150

BLUECHIP_N          = 30    # top-N by avg daily value -> bluechip
TS_BLUECHIP         = 0.10  # trailing stop for bluechip
TS_SME              = 0.15  # trailing stop for SME

# Also sweep a range for sensitivity analysis
TS_BLUECHIP_GRID    = [0.07, 0.10, 0.12, 0.15]
TS_SME_GRID         = [0.10, 0.15, 0.20, 0.25]

BQ_BIN = r"bq"

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG  = "#0f1117"
PANEL_BG = "#1a1d27"
GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"
BLUE     = "#4fa3e0"
GREEN    = "#4ecb71"
RED      = "#e05c5c"
YELLOW   = "#f0c060"
PURPLE   = "#b57bee"

plt.rcParams.update({
    "figure.facecolor": DARK_BG, "axes.facecolor": PANEL_BG,
    "axes.edgecolor":   GRID_CLR, "axes.labelcolor": TEXT_CLR,
    "xtick.color":      TEXT_CLR, "ytick.color":    TEXT_CLR,
    "text.color":       TEXT_CLR, "grid.color":     GRID_CLR,
    "grid.linestyle":   "--",     "grid.alpha":     0.5,
    "font.family":      "DejaVu Sans",
})


# ── HELPERS ───────────────────────────────────────────────────────────────────
def load_jsonl(path):
    rows = [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()]
    df = pd.DataFrame(rows)
    df["ymd"] = pd.to_datetime(df["ymd"])
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


# ── LOAD & CLASSIFY ───────────────────────────────────────────────────────────
print("Loading transactions ...")
tx = load_jsonl(TX_FILE)
tx.sort_values("ymd", inplace=True)

print("Classifying tickers ...")
vol_rank = pd.read_csv(VOL_RANK)
bluechip_set = set(vol_rank.head(BLUECHIP_N)["ticker"].tolist())
print(f"  Bluechip ({len(bluechip_set)}): {sorted(bluechip_set)}")

def classify(ticker):
    return "bluechip" if ticker in bluechip_set else "sme"


# ── BUILD CLOSED POSITIONS ────────────────────────────────────────────────────
print("Building positions ...")
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
        "type":         classify(grp["ticker"].iloc[0]),
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
bc_pos = pos_df[pos_df["type"] == "bluechip"]
sme_pos = pos_df[pos_df["type"] == "sme"]
print(f"  Total closed: {len(pos_df)}  |  Bluechip: {len(bc_pos)}  |  SME: {len(sme_pos)}")


# ── FETCH PRICES ──────────────────────────────────────────────────────────────
tickers   = pos_df["ticker"].unique().tolist()
date_min  = pos_df["first_buy"].min().strftime("%Y-%m-%d")
date_max  = pos_df["last_sell"].max().strftime("%Y-%m-%d")
n_chunks  = -(-len(tickers) // BQ_CHUNK)
print(f"Fetching prices: {len(tickers)} tickers | {date_min} -> {date_max} | {n_chunks} chunks ...")

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
    print(f"  chunk {i//BQ_CHUNK+1}/{n_chunks}: {len(df):,} rows")

prices_df = pd.concat(frames, ignore_index=True)
print(f"  Total rows: {len(prices_df):,}")

price_map = {
    ticker: grp.set_index("time")["Close"].sort_index()
    for ticker, grp in prices_df.groupby("ticker")
}


# ── SIMULATE ONE POSITION WITH TRAILING STOP ──────────────────────────────────
def simulate_trailing(ticker, first_buy, last_sell, buys_df,
                      total_inv, total_fees, orig_pnl, orig_pnl_pct,
                      trailing_pct):
    """
    Trailing stop logic:
      - running_peak tracks the highest Close seen since position opened.
      - Exit when Close < running_peak * (1 - trailing_pct).
    Returns (pnl, pnl_pct, exit_type, holding_days).
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

    buy_list    = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr     = 0
    n_buys      = len(buy_list)
    cum_inv     = 0.0
    cum_sh      = 0.0
    running_peak = None

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

        if cum_sh <= 0 or date == first_buy:
            continue

        # Update running peak
        if running_peak is None or close > running_peak:
            running_peak = close

        # Trailing stop trigger
        if close <= running_peak * (1 - trailing_pct):
            denom = cum_inv + total_fees
            proc  = close * cum_sh
            return (
                proc - denom,
                (proc / denom - 1) * 100,
                "trailing_stop",
                (date - first_buy).days,
            )

    return orig_pnl, orig_pnl_pct, "original", (last_sell - first_buy).days


# ── BASELINE ─────────────────────────────────────────────────────────────────
orig_total_pnl  = pos_df["orig_pnl"].sum()
orig_win_rate   = (pos_df["orig_pnl_pct"] > 0).mean() * 100
orig_avg_pct    = pos_df["orig_pnl_pct"].mean()
orig_avg_win    = pos_df[pos_df["orig_pnl_pct"] > 0]["orig_pnl_pct"].mean()
orig_avg_loss   = pos_df[pos_df["orig_pnl_pct"] <= 0]["orig_pnl_pct"].mean()
orig_max_loss   = pos_df["orig_pnl_pct"].min()

# Baseline by type
def baseline_stats(sub):
    w = (sub["orig_pnl_pct"] > 0)
    return dict(
        total_pnl  = sub["orig_pnl"].sum(),
        win_rate   = w.mean() * 100,
        avg_pct    = sub["orig_pnl_pct"].mean(),
        avg_win    = sub.loc[w,  "orig_pnl_pct"].mean(),
        avg_loss   = sub.loc[~w, "orig_pnl_pct"].mean(),
        n          = len(sub),
    )

orig_bc  = baseline_stats(bc_pos)
orig_sme = baseline_stats(sme_pos)

pos_list = [
    (row["ticker"], row["first_buy"], row["last_sell"], row["buys_df"],
     row["total_inv"], row["total_fees"], row["orig_pnl"], row["orig_pnl_pct"],
     row["type"])
    for _, row in pos_df.iterrows()
]


# ── GRID SEARCH ──────────────────────────────────────────────────────────────
print(f"\nGrid search: {len(TS_BLUECHIP_GRID)} BC x {len(TS_SME_GRID)} SME = "
      f"{len(TS_BLUECHIP_GRID)*len(TS_SME_GRID)} combos ...")

grid_rows = []
for ts_bc, ts_sme in [(b, s) for b in TS_BLUECHIP_GRID for s in TS_SME_GRID]:
    pnls, pcts, exits, types = [], [], [], []
    for ticker, first_buy, last_sell, buys_df, total_inv, total_fees, orig_pnl, orig_pnl_pct, typ in pos_list:
        ts = ts_bc if typ == "bluechip" else ts_sme
        pnl, pct_v, etype, _ = simulate_trailing(
            ticker, first_buy, last_sell, buys_df,
            total_inv, total_fees, orig_pnl, orig_pnl_pct, ts
        )
        pnls.append(pnl); pcts.append(pct_v)
        exits.append(etype); types.append(typ)

    pnls_a  = np.array(pnls,  dtype=float)
    pcts_a  = np.array(pcts,  dtype=float)
    exits_a = np.array(exits)
    types_a = np.array(types)
    wins    = pcts_a > 0

    # Per-type breakdown
    bc_mask  = types_a == "bluechip"
    sme_mask = types_a == "sme"

    grid_rows.append({
        "ts_bc":       ts_bc,
        "ts_sme":      ts_sme,
        "total_pnl":   pnls_a.sum(),
        "win_rate":    wins.mean() * 100,
        "avg_pct":     pcts_a.mean(),
        "avg_win":     pcts_a[wins].mean() if wins.any() else 0.0,
        "avg_loss":    pcts_a[~wins].mean() if (~wins).any() else 0.0,
        "max_loss":    pcts_a.min(),
        "pnl_diff_pct": (pnls_a.sum() - orig_total_pnl) / abs(orig_total_pnl) * 100,
        "n_ts":        (exits_a == "trailing_stop").sum(),
        "n_orig":      (exits_a == "original").sum(),
        "pcts_arr":    pcts_a,
        "exits_arr":   exits_a,
        # bluechip sub
        "bc_pnl":      pnls_a[bc_mask].sum(),
        "bc_wr":       (pcts_a[bc_mask] > 0).mean() * 100 if bc_mask.any() else 0,
        "bc_avg":      pcts_a[bc_mask].mean() if bc_mask.any() else 0,
        "bc_ts":       (exits_a[bc_mask] == "trailing_stop").sum(),
        # sme sub
        "sme_pnl":     pnls_a[sme_mask].sum(),
        "sme_wr":      (pcts_a[sme_mask] > 0).mean() * 100 if sme_mask.any() else 0,
        "sme_avg":     pcts_a[sme_mask].mean() if sme_mask.any() else 0,
        "sme_ts":      (exits_a[sme_mask] == "trailing_stop").sum(),
    })

gdf  = pd.DataFrame(grid_rows)
best = gdf.loc[gdf["total_pnl"].idxmax()]

# The user's requested combo
req_row = gdf[(gdf["ts_bc"] == TS_BLUECHIP) & (gdf["ts_sme"] == TS_SME)].iloc[0]


# ── CONSOLE OUTPUT ─────────────────────────────────────────────────────────────
SEP = "=" * 66

def print_stats(label, row_or_dict, is_dict=False):
    if is_dict:
        d = row_or_dict
        print(f"  Total P&L : {fmt_b(d['total_pnl'])}  |  n={d['n']}")
        print(f"  Win rate  : {d['win_rate']:.1f}%")
        print(f"  Avg ret   : {fmt_p(d['avg_pct'])}  |  Avg gain: {fmt_p(d['avg_win'])}  |  Avg loss: {fmt_p(d['avg_loss'])}")
    else:
        r = row_or_dict
        print(f"  Total P&L : {fmt_b(r['total_pnl'])}  ({r['pnl_diff_pct']:+.1f}% vs orig)")
        print(f"  Win rate  : {r['win_rate']:.1f}%")
        print(f"  Avg ret   : {fmt_p(r['avg_pct'])}  |  Avg gain: {fmt_p(r['avg_win'])}  |  Avg loss: {fmt_p(r['avg_loss'])}")
        print(f"  Trailing stop exits: {int(r['n_ts'])}  |  No trigger: {int(r['n_orig'])}")

print(f"\n{SEP}")
print("ORIGINAL (no trailing stop overlay)")
print(f"  Total P&L : {fmt_b(orig_total_pnl)}")
print(f"  Win rate  : {orig_win_rate:.1f}%")
print(f"  Avg ret   : {fmt_p(orig_avg_pct)}  |  Avg gain: {fmt_p(orig_avg_win)}  |  Avg loss: {fmt_p(orig_avg_loss)}")
print(f"  Max loss  : {fmt_p(orig_max_loss)}")
print(f"\n  -- Bluechip ({int(orig_bc['n'])} pos): WR {orig_bc['win_rate']:.1f}%  avg {fmt_p(orig_bc['avg_pct'])}")
print(f"  -- SME     ({int(orig_sme['n'])} pos): WR {orig_sme['win_rate']:.1f}%  avg {fmt_p(orig_sme['avg_pct'])}")

print(f"\n{SEP}")
print(f"REQUESTED: Bluechip TS={TS_BLUECHIP*100:.0f}%  /  SME TS={TS_SME*100:.0f}%")
print_stats("requested", req_row)
print(f"  -- Bluechip: P&L {fmt_b(req_row['bc_pnl'])}  WR {req_row['bc_wr']:.1f}%  avg {fmt_p(req_row['bc_avg'])}  TS exits {int(req_row['bc_ts'])}")
print(f"  -- SME     : P&L {fmt_b(req_row['sme_pnl'])}  WR {req_row['sme_wr']:.1f}%  avg {fmt_p(req_row['sme_avg'])}  TS exits {int(req_row['sme_ts'])}")

print(f"\n{SEP}")
print(f"BEST COMBO: Bluechip TS={best['ts_bc']*100:.0f}%  /  SME TS={best['ts_sme']*100:.0f}%")
print_stats("best", best)

print(f"\n{SEP}")
print("Full grid (sorted by Total P&L):")
print(f"{'BC%':>5} {'SME%':>5} | {'P&L(B)':>10} {'vs orig':>9} {'WR':>7} {'AvgPct':>8} {'AvgWin':>8} {'AvgLoss':>9} {'TS exits':>9}")
print("-" * 75)
for _, r in gdf.sort_values("total_pnl", ascending=False).iterrows():
    marker = " <-- requested" if (r["ts_bc"] == TS_BLUECHIP and r["ts_sme"] == TS_SME) else (
             " <-- BEST"     if (r["ts_bc"] == best["ts_bc"] and r["ts_sme"] == best["ts_sme"]) else "")
    print(f"{r['ts_bc']*100:4.0f}% {r['ts_sme']*100:4.0f}% | "
          f"{r['total_pnl']/1e9:>10,.2f} {r['pnl_diff_pct']:>+8.1f}% "
          f"{r['win_rate']:>6.1f}% {r['avg_pct']:>7.2f}% "
          f"{r['avg_win']:>7.2f}% {r['avg_loss']:>8.2f}% "
          f"{int(r['n_ts']):>8}{marker}")


# ── VISUALISATION ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 28), facecolor=DARK_BG)
fig.suptitle("Backtest: Trailing Stop (Bluechip vs SME)",
             fontsize=22, fontweight="bold", color=TEXT_CLR, y=0.998)
gs = gridspec.GridSpec(4, 3, figure=fig,
                       hspace=0.48, wspace=0.35,
                       left=0.06, right=0.97, top=0.965, bottom=0.03)

# ── Row 0: Heatmaps ───────────────────────────────────────────────────────────
BC_LBL  = [f"{int(t*100)}%" for t in TS_BLUECHIP_GRID]
SME_LBL = [f"{int(s*100)}%" for s in TS_SME_GRID]

def make_matrix(col):
    mat = np.zeros((len(TS_BLUECHIP_GRID), len(TS_SME_GRID)))
    for r in grid_rows:
        i = TS_BLUECHIP_GRID.index(r["ts_bc"])
        j = TS_SME_GRID.index(r["ts_sme"])
        mat[i, j] = r[col]
    return mat

bi_req = TS_BLUECHIP_GRID.index(TS_BLUECHIP)
bj_req = TS_SME_GRID.index(TS_SME)
bi_best = TS_BLUECHIP_GRID.index(best["ts_bc"])
bj_best = TS_SME_GRID.index(best["ts_sme"])

def draw_hm(ax, mat, title, fmt="{:.1f}", colors=None, cbar_label="",
            mark_req=True, mark_best=True):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_CLR, pad=8)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    cmap = LinearSegmentedColormap.from_list("c", colors or [RED, PANEL_BG, GREEN], N=256)
    im = ax.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")
    ax.set_xticks(range(len(TS_SME_GRID)));      ax.set_xticklabels(SME_LBL, fontsize=9)
    ax.set_yticks(range(len(TS_BLUECHIP_GRID))); ax.set_yticklabels(BC_LBL, fontsize=9)
    ax.set_xlabel("SME Trailing Stop %", fontsize=9)
    ax.set_ylabel("Bluechip Trailing Stop %", fontsize=9)
    vmin, vmax = mat.min(), mat.max()
    mid = (vmin + vmax) / 2
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            tc = "black" if abs(v - mid) > (vmax - vmin) * 0.3 else TEXT_CLR
            ax.text(j, i, fmt.format(v), ha="center", va="center",
                    fontsize=9, color=tc, fontweight="bold")
    if mark_req:
        ax.add_patch(plt.Rectangle((bj_req-0.5, bi_req-0.5), 1, 1,
                     fill=False, edgecolor=BLUE, linewidth=2.5, zorder=5))
        ax.text(bj_req, bi_req+0.38, "REQ", ha="center", fontsize=7,
                color=BLUE, fontweight="bold", zorder=6)
    if mark_best and not (bi_best == bi_req and bj_best == bj_req):
        ax.add_patch(plt.Rectangle((bj_best-0.5, bi_best-0.5), 1, 1,
                     fill=False, edgecolor=YELLOW, linewidth=2.5, zorder=5))
        ax.text(bj_best, bi_best-0.42, "BEST", ha="center", fontsize=7,
                color=YELLOW, fontweight="bold", zorder=6)
    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.tick_params(colors=TEXT_CLR)
    cb.set_label(cbar_label, color=TEXT_CLR, fontsize=8)

ax0 = fig.add_subplot(gs[0, 0])
draw_hm(ax0, make_matrix("pnl_diff_pct"),
        f"Delta P&L vs Original (%)\n[orig: {fmt_b(orig_total_pnl)}]",
        fmt="{:+.1f}", colors=[RED, PANEL_BG, GREEN], cbar_label="% vs orig")

ax1 = fig.add_subplot(gs[0, 1])
draw_hm(ax1, make_matrix("win_rate"),
        f"Win Rate (%)\n[orig: {orig_win_rate:.1f}%]",
        fmt="{:.1f}", colors=[RED, PANEL_BG, GREEN], cbar_label="%")

ax2 = fig.add_subplot(gs[0, 2])
draw_hm(ax2, make_matrix("avg_loss"),
        f"Avg Loss % (higher = worse)\n[orig: {orig_avg_loss:.1f}%]",
        fmt="{:.1f}", colors=[GREEN, PANEL_BG, RED], cbar_label="%")

# ── Row 1: Distribution (original vs requested vs best) ───────────────────────
ax3 = fig.add_subplot(gs[1, :2])
ax3.set_title(
    f"P&L Distribution: Original  vs  BC={TS_BLUECHIP*100:.0f}%/SME={TS_SME*100:.0f}%"
    + (f"  vs  Best BC={best['ts_bc']*100:.0f}%/SME={best['ts_sme']*100:.0f}%"
       if not (best["ts_bc"] == TS_BLUECHIP and best["ts_sme"] == TS_SME) else ""),
    fontsize=10, fontweight="bold", color=TEXT_CLR,
)
ax3.spines[["top","right","left","bottom"]].set_visible(False)
ax3.grid(True, axis="y")

orig_arr = pos_df["orig_pnl_pct"].values
req_arr  = req_row["pcts_arr"]
best_arr = best["pcts_arr"]
all_arr  = np.concatenate([orig_arr, req_arr, best_arr])
q01, q99 = np.percentile(all_arr[np.isfinite(all_arr)], [1, 99])
bins = np.linspace(q01, q99, 60)

ax3.hist(orig_arr, bins=bins, alpha=0.45, color=BLUE,
         label=f"Original  (mean {orig_avg_pct:.1f}%  WR {orig_win_rate:.0f}%)")
ax3.hist(req_arr,  bins=bins, alpha=0.45, color=GREEN,
         label=f"BC {TS_BLUECHIP*100:.0f}% / SME {TS_SME*100:.0f}%"
               f"  (mean {req_row['avg_pct']:.1f}%  WR {req_row['win_rate']:.0f}%)")
if not (best["ts_bc"] == TS_BLUECHIP and best["ts_sme"] == TS_SME):
    ax3.hist(best_arr, bins=bins, alpha=0.35, color=YELLOW,
             label=f"Best BC {best['ts_bc']*100:.0f}% / SME {best['ts_sme']*100:.0f}%"
                   f"  (mean {best['avg_pct']:.1f}%  WR {best['win_rate']:.0f}%)")

for v, c in [(orig_avg_pct, BLUE), (req_row["avg_pct"], GREEN)]:
    ax3.axvline(v, color=c, linewidth=1.2, linestyle=":")
ax3.axvline(0, color=YELLOW, linewidth=1, linestyle="--", alpha=0.6)
ax3.legend(fontsize=9, framealpha=0.25)
ax3.set_xlabel("Return %"); ax3.set_ylabel("# Positions")
ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

# ── Row 1 col 2: Exit type pie ─────────────────────────────────────────────────
ax4 = fig.add_subplot(gs[1, 2])
ax4.set_facecolor(PANEL_BG)
ax4.set_title(
    f"Exit Types  BC={TS_BLUECHIP*100:.0f}% / SME={TS_SME*100:.0f}%\n"
    f"TS exits: {int(req_row['n_ts'])}  |  No trigger: {int(req_row['n_orig'])}",
    fontsize=10, fontweight="bold", color=TEXT_CLR,
)
ea = req_row["exits_arr"]
pie_data = [
    ("Trailing Stop", (ea == "trailing_stop").sum(), RED),
    ("Original Exit", (ea == "original").sum(),      BLUE),
    ("No Data",       (ea == "no_data").sum(),        GRID_CLR),
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

# ── Row 2: Bluechip vs SME breakdown bar ──────────────────────────────────────
ax5 = fig.add_subplot(gs[2, :])
ax5.set_title("P&L Breakdown: Original vs Requested vs Best  (by Bluechip / SME)",
              fontsize=11, fontweight="bold", color=TEXT_CLR)
ax5.spines[["top","right","left","bottom"]].set_visible(False)
ax5.grid(True, axis="y")

scenarios = [
    ("Original",                BLUE,   orig_bc["total_pnl"],  orig_sme["total_pnl"],
     orig_bc["win_rate"],  orig_sme["win_rate"]),
    (f"BC {TS_BLUECHIP*100:.0f}%\nSME {TS_SME*100:.0f}%", GREEN,
     req_row["bc_pnl"],  req_row["sme_pnl"],
     req_row["bc_wr"],   req_row["sme_wr"]),
    (f"Best\nBC {best['ts_bc']*100:.0f}% SME {best['ts_sme']*100:.0f}%", YELLOW,
     best["bc_pnl"],  best["sme_pnl"],
     best["bc_wr"],   best["sme_wr"]),
]

x = np.arange(len(scenarios))
w = 0.35
for idx, (lbl, clr, bc_pnl, sme_pnl, bc_wr, sme_wr) in enumerate(scenarios):
    b1 = ax5.bar(x[idx]-w/2, bc_pnl/1e9,  width=w, color=clr,    alpha=0.85, zorder=3, label="Bluechip" if idx==0 else "")
    b2 = ax5.bar(x[idx]+w/2, sme_pnl/1e9, width=w, color=PURPLE, alpha=0.65, zorder=3, label="SME"      if idx==0 else "")
    for bar, wr, val in [(b1, bc_wr, bc_pnl), (b2, sme_wr, sme_pnl)]:
        ax5.text(bar[0].get_x()+bar[0].get_width()/2,
                 bar[0].get_height() + abs(orig_bc["total_pnl"]/1e9)*0.015,
                 f"WR {wr:.0f}%\n{val/1e9:+.0f}B",
                 ha="center", fontsize=8, color=TEXT_CLR)

ax5.set_xticks(x); ax5.set_xticklabels([s[0] for s in scenarios], fontsize=10)
ax5.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
ax5.set_ylabel("P&L (B VND)")
ax5.legend(fontsize=9, framealpha=0.25)
ax5.axhline(0, color=GRID_CLR, linewidth=0.8)

# ── Row 3: Waterfall by year ──────────────────────────────────────────────────
ax6 = fig.add_subplot(gs[3, :])
ax6.set_title("Yearly P&L: Original vs Requested Trailing Stop",
              fontsize=11, fontweight="bold", color=TEXT_CLR)
ax6.spines[["top","right","left","bottom"]].set_visible(False)
ax6.grid(True, axis="y")

# Assign year to each position by first_buy
pos_df2 = pos_df.copy()
pos_df2["year"] = pos_df2["first_buy"].dt.year

req_pcts = req_row["pcts_arr"]
pos_df2["req_pnl"] = req_pcts * pos_df2["total_inv"] / 100  # approx

yearly_orig = pos_df2.groupby("year")["orig_pnl"].sum()
yearly_req  = pos_df2.groupby("year")["req_pnl"].sum()
years = sorted(yearly_orig.index.tolist())
x_yr  = np.arange(len(years))
w_yr  = 0.38

b_orig = ax6.bar(x_yr - w_yr/2, [yearly_orig.get(y, 0)/1e9 for y in years],
                 width=w_yr, color=BLUE, alpha=0.8, label="Original")
b_req  = ax6.bar(x_yr + w_yr/2, [yearly_req.get(y, 0)/1e9  for y in years],
                 width=w_yr, color=GREEN, alpha=0.8,
                 label=f"BC {TS_BLUECHIP*100:.0f}% / SME {TS_SME*100:.0f}%")
ax6.axhline(0, color=GRID_CLR, linewidth=0.8)
ax6.set_xticks(x_yr); ax6.set_xticklabels([str(y) for y in years], fontsize=9)
ax6.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
ax6.set_ylabel("P&L (B VND)")
ax6.legend(fontsize=9, framealpha=0.25)

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved -> {Path(OUT_IMG).resolve()}")
