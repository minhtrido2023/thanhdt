#!/usr/bin/env python3
"""
backtest_asymmetric_ts.py
=========================
Strategy: Time-Stop 20d  +  Asymmetric Trailing Stop

Asymmetric Trailing Stop logic:
  - Phase 1 (WAITING): position opened, trailing NOT yet active.
  - Activation: Close >= avg_cost * (1 + ACTIVATE_PCT) for the first time.
  - Phase 2 (ACTIVE): track running peak from day 1 (not just from activation).
    Exit when Close <= running_peak * (1 - TRAIL_PCT).
  - Fill price: Open[D+1] for all triggered exits.

Time-Stop 20d (unchanged from prev backtest):
  - On trading day 20: if price NEVER exceeded avg_cost -> sell at Open[D+1].

Grid sweep:
  ACTIVATE_PCT : [0.15, 0.20, 0.25, 0.30]   (lãi tối thiểu để bật trailing)
  TRAIL_PCT    : [0.10, 0.12, 0.15, 0.20]   (% rớt từ đỉnh để bán)
  => 4x4 = 16 combos, each tested with/without TS20 => 32 + 4 baselines

Baselines compared:
  (A) Original          — no overlay
  (B) TS20 only         — proven best from previous runs
  (C) Each combo (TS20 + Asymmetric)
"""

import json
import subprocess
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
TX_FILE        = "transactions_email_special_2026-04-07_15.14.47.jsonl"
PROJECT        = "lithe-record-440915-m9"
OUT_IMG        = "backtest_asymmetric_ts.png"
BQ_CHUNK       = 150
BQ_BIN         = r"bq"
FILTER_FROM    = pd.Timestamp("2020-01-01")   # same window as last run

TIME_STOP_DAYS = 20
ACTIVATE_GRID  = [0.15, 0.20, 0.25, 0.30]
TRAIL_GRID     = [0.10, 0.12, 0.15, 0.20]

# ── STYLE ─────────────────────────────────────────────────────────────────────
DARK_BG  = "#0f1117"; PANEL_BG = "#1a1d27"; GRID_CLR = "#2a2d3a"
TEXT_CLR = "#e0e0e0"; BLUE = "#4fa3e0";     GREEN = "#4ecb71"
RED      = "#e05c5c"; YELLOW = "#f0c060";   PURPLE = "#b57bee"
ORANGE   = "#f0904a"; TEAL = "#4ecbbb"

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

def fmt_b(v): return f"{v/1e9:,.2f}B"
def fmt_p(v): sign = "+" if v >= 0 else ""; return f"{sign}{v:.2f}%"

def make_exit_pnl(cum_sh, cum_inv, total_fees, close, open_next):
    fill  = open_next if (not pd.isna(open_next) and open_next > 0) else close
    denom = cum_inv + total_fees
    proc  = fill * cum_sh
    return proc - denom, (proc / denom - 1) * 100

# ── LOAD & FILTER ─────────────────────────────────────────────────────────────
print("Loading transactions ...")
tx = load_jsonl(TX_FILE)
tx.sort_values("ymd", inplace=True)

print("Building closed positions ...")
pos_records = []
for hid, grp in tx.groupby("holding_id"):
    buys  = grp[grp["action"] == "buy"].sort_values("ymd")
    sells = grp[grp["action"] == "sell"].sort_values("ymd")
    if sells.empty: continue
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
print(f"  {len(pos_df)} closed positions (>= {FILTER_FROM.date()}) | {pos_df['ticker'].nunique()} tickers")

# ── FETCH PRICES ──────────────────────────────────────────────────────────────
tickers  = pos_df["ticker"].unique().tolist()
date_min = pos_df["first_buy"].min().strftime("%Y-%m-%d")
date_max = pos_df["last_sell"].max().strftime("%Y-%m-%d")
n_chunks = -(-len(tickers) // BQ_CHUNK)
print(f"Fetching prices: {len(tickers)} tickers | {date_min} -> {date_max} | {n_chunks} chunks ...")

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

price_map = {}
for ticker, grp in prices_df.groupby("ticker"):
    grp = grp.sort_values("time").set_index("time")[["Close","Open"]].copy()
    grp["Open_next"] = grp["Open"].shift(-1)
    price_map[ticker] = grp

# ── CORE SIMULATION ───────────────────────────────────────────────────────────
def simulate(ticker, first_buy, last_sell, buys_df,
             total_inv, total_fees, orig_pnl, orig_pnl_pct,
             activate_pct, trail_pct, use_timestop):
    """
    exit_type: 'asymmetric_ts' | 'time_stop' | 'original' | 'no_data'
    """
    if ticker not in price_map:
        return orig_pnl, orig_pnl_pct, "no_data", None

    df_px = price_map[ticker]
    try:    window = df_px.loc[first_buy:last_sell]
    except: return orig_pnl, orig_pnl_pct, "original", None
    if window.empty: return orig_pnl, orig_pnl_pct, "original", None

    buy_list    = list(buys_df.sort_values("ymd").itertuples())
    buy_ptr     = 0; n_buys = len(buy_list)
    cum_inv     = 0.0; cum_sh = 0.0
    ever_above  = False      # for time-stop rule
    trading_day = 0
    activated   = False      # asymmetric TS not yet active
    running_peak = None      # track from day 1, use only after activation

    for date, row in window.iterrows():
        close     = row["Close"]
        open_next = row["Open_next"]
        if pd.isna(close) or close <= 0: continue

        # Absorb buys
        while buy_ptr < n_buys and buy_list[buy_ptr].ymd <= date:
            b = buy_list[buy_ptr]
            if b.adj_price > 0:
                cum_sh  += b.buy_amount / b.adj_price
                cum_inv += b.buy_amount
            buy_ptr += 1
        if cum_sh <= 0: continue

        avg_cost = cum_inv / cum_sh

        # Track running peak from day 1
        if running_peak is None or close > running_peak:
            running_peak = close

        if date == first_buy:
            trading_day = 0
            continue
        trading_day += 1

        # ever_above: for time-stop check
        if close > avg_cost:
            ever_above = True

        # ── Check activation of asymmetric trailing stop ──────────────────
        if not activated and close >= avg_cost * (1 + activate_pct):
            activated = True

        # ── Asymmetric trailing stop (only after activation) ──────────────
        if activated and close <= running_peak * (1 - trail_pct):
            pnl, pct_v = make_exit_pnl(cum_sh, cum_inv, total_fees, close, open_next)
            return pnl, pct_v, "asymmetric_ts", (date - first_buy).days

        # ── Time-stop on day 20 ───────────────────────────────────────────
        if use_timestop and trading_day == TIME_STOP_DAYS:
            if not ever_above and close <= avg_cost:
                pnl, pct_v = make_exit_pnl(cum_sh, cum_inv, total_fees, close, open_next)
                return pnl, pct_v, "time_stop", (date - first_buy).days

    return orig_pnl, orig_pnl_pct, "original", (last_sell - first_buy).days


# ── BASELINES ─────────────────────────────────────────────────────────────────
orig_total_pnl = pos_df["orig_pnl"].sum()
orig_win_rate  = (pos_df["orig_pnl_pct"] > 0).mean() * 100
orig_avg_pct   = pos_df["orig_pnl_pct"].mean()
orig_avg_win   = pos_df[pos_df["orig_pnl_pct"] > 0]["orig_pnl_pct"].mean()
orig_avg_loss  = pos_df[pos_df["orig_pnl_pct"] <= 0]["orig_pnl_pct"].mean()

pos_list = [
    (row["ticker"], row["first_buy"], row["last_sell"], row["buys_df"],
     row["total_inv"], row["total_fees"], row["orig_pnl"], row["orig_pnl_pct"])
    for _, row in pos_df.iterrows()
]

# TS20 only baseline
def run_ts20_only():
    pnls, pcts, exits = [], [], []
    for args in pos_list:
        pnl, pct_v, etype, _ = simulate(*args, activate_pct=9999, trail_pct=0,
                                         use_timestop=True)
        pnls.append(pnl); pcts.append(pct_v); exits.append(etype)
    return np.array(pnls), np.array(pcts), np.array(exits)

print("\nRunning TS20-only baseline ...")
ts20_pnls, ts20_pcts, ts20_exits = run_ts20_only()
ts20_total = ts20_pnls.sum()
ts20_wr    = (ts20_pcts > 0).mean() * 100
ts20_avg   = ts20_pcts.mean()

# ── GRID SEARCH ───────────────────────────────────────────────────────────────
n_combos = len(ACTIVATE_GRID) * len(TRAIL_GRID)
print(f"Grid search: {len(ACTIVATE_GRID)} activate x {len(TRAIL_GRID)} trail = {n_combos} combos ...")

grid_rows = []
for act_pct, tr_pct in product(ACTIVATE_GRID, TRAIL_GRID):
    pnls, pcts, exits = [], [], []
    for args in pos_list:
        pnl, pct_v, etype, _ = simulate(*args, activate_pct=act_pct,
                                         trail_pct=tr_pct, use_timestop=True)
        pnls.append(pnl); pcts.append(pct_v); exits.append(etype)

    pnls_a  = np.array(pnls, dtype=float)
    pcts_a  = np.array(pcts, dtype=float)
    exits_a = np.array(exits)
    wins    = pcts_a > 0

    grid_rows.append({
        "act_pct":      act_pct,
        "tr_pct":       tr_pct,
        "label":        f"Act{int(act_pct*100)}%+Tr{int(tr_pct*100)}%",
        "total_pnl":    pnls_a.sum(),
        "win_rate":     wins.mean() * 100,
        "avg_pct":      pcts_a.mean(),
        "avg_win":      pcts_a[wins].mean()  if wins.any()   else 0.0,
        "avg_loss":     pcts_a[~wins].mean() if (~wins).any() else 0.0,
        "max_loss":     pcts_a.min(),
        "pnl_vs_orig":  (pnls_a.sum() - orig_total_pnl) / abs(orig_total_pnl) * 100,
        "pnl_vs_ts20":  (pnls_a.sum() - ts20_total) / abs(ts20_total) * 100,
        "n_ats":        (exits_a == "asymmetric_ts").sum(),
        "n_ts":         (exits_a == "time_stop").sum(),
        "n_orig":       (exits_a == "original").sum(),
        "pcts_arr":     pcts_a,
        "exits_arr":    exits_a,
    })
    print(f"  {grid_rows[-1]['label']}: {fmt_b(pnls_a.sum())} "
          f"({grid_rows[-1]['pnl_vs_orig']:+.2f}% vs orig)"
          f"  ATS={int((exits_a=='asymmetric_ts').sum())}"
          f"  TS={int((exits_a=='time_stop').sum())}")

gdf  = pd.DataFrame(grid_rows)
best = gdf.loc[gdf["total_pnl"].idxmax()]

# ── CONSOLE SUMMARY ───────────────────────────────────────────────────────────
SEP = "=" * 72
print(f"\n{SEP}")
print("ORIGINAL (no overlay)")
print(f"  P&L: {fmt_b(orig_total_pnl)}  WR: {orig_win_rate:.1f}%  "
      f"Avg: {fmt_p(orig_avg_pct)}  Gain: {fmt_p(orig_avg_win)}  Loss: {fmt_p(orig_avg_loss)}")

print(f"\n{SEP}")
print("TIME-STOP 20d ONLY  (previous best)")
print(f"  P&L: {fmt_b(ts20_total)}  ({(ts20_total-orig_total_pnl)/1e9:+.2f}B vs orig)  "
      f"WR: {ts20_wr:.1f}%  Avg: {fmt_p(ts20_avg)}")

print(f"\n{SEP}")
print(f"BEST: TS20 + Asymmetric TS  [Activate>={best['act_pct']*100:.0f}%  Trail={best['tr_pct']*100:.0f}%]")
print(f"  P&L: {fmt_b(best['total_pnl'])}  "
      f"({(best['total_pnl']-orig_total_pnl)/1e9:+.2f}B vs orig  /  "
      f"{(best['total_pnl']-ts20_total)/1e9:+.2f}B vs TS20)")
print(f"  WR: {best['win_rate']:.1f}%  Avg: {fmt_p(best['avg_pct'])}"
      f"  Gain: {fmt_p(best['avg_win'])}  Loss: {fmt_p(best['avg_loss'])}")
print(f"  Exits -> ATS={int(best['n_ats'])}  TS20={int(best['n_ts'])}  Original={int(best['n_orig'])}")

print(f"\n{SEP}")
print("Full grid (sorted by P&L):\n")
print(f"{'Combo':<22} | {'P&L(B)':>10} {'vsOrig':>8} {'vsTS20':>8} "
      f"{'WR':>6} {'AvgPct':>8} {'AvgWin':>8} {'AvgLoss':>9} {'MaxLoss':>9} "
      f"{'nATS':>6} {'nTS':>5} {'nOrig':>6}")
print("-" * 108)
for _, r in gdf.sort_values("total_pnl", ascending=False).iterrows():
    mark = " ***" if r["label"] == best["label"] else ""
    print(f"{r['label']:<22} | {r['total_pnl']/1e9:>10,.2f} "
          f"{r['pnl_vs_orig']:>+7.2f}% {r['pnl_vs_ts20']:>+7.2f}% "
          f"{r['win_rate']:>6.1f}% {r['avg_pct']:>7.2f}% "
          f"{r['avg_win']:>7.2f}% {r['avg_loss']:>8.2f}% {r['max_loss']:>8.2f}% "
          f"{int(r['n_ats']):>6} {int(r['n_ts']):>5} {int(r['n_orig']):>6}{mark}")

# Winners protected analysis: positions where ATS fired
print(f"\n{SEP}")
print(f"ANALYSIS: What did ATS exit on best combo? "
      f"(Activate>={best['act_pct']*100:.0f}%  Trail={best['tr_pct']*100:.0f}%)")
ats_mask = best["exits_arr"] == "asymmetric_ts"
ats_pcts = best["pcts_arr"][ats_mask]
orig_pcts_arr = pos_df["orig_pnl_pct"].values
orig_pcts_ats  = orig_pcts_arr[ats_mask]

if ats_mask.any():
    better = (best["pcts_arr"][ats_mask] > orig_pcts_arr[ats_mask]).sum()
    worse  = ats_mask.sum() - better
    print(f"  ATS exits: {ats_mask.sum()}")
    print(f"  -> Better than original: {better} positions  "
          f"(ATS locked in more profit / avoided deeper loss)")
    print(f"  -> Worse than original:  {worse} positions  "
          f"(original would have done better)")
    print(f"  Avg ATS exit return: {fmt_p(ats_pcts.mean())}  "
          f"(vs orig avg for same positions: {fmt_p(orig_pcts_ats.mean())})")
    print(f"  Min ATS exit: {fmt_p(ats_pcts.min())}  "
          f"Max ATS exit: {fmt_p(ats_pcts.max())}")


# ── VISUALISATION ─────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(22, 30), facecolor=DARK_BG)
fig.suptitle(
    "Backtest: TS20  +  Asymmetric Trailing Stop  [Trigger=Close, Fill=Open(D+1)]",
    fontsize=20, fontweight="bold", color=TEXT_CLR, y=0.998
)
gs = gridspec.GridSpec(4, 3, figure=fig,
                       hspace=0.46, wspace=0.35,
                       left=0.06, right=0.97, top=0.965, bottom=0.03)

ACT_LBL  = [f"Act {int(a*100)}%" for a in ACTIVATE_GRID]
TR_LBL   = [f"Trail {int(t*100)}%" for t in TRAIL_GRID]

def make_matrix(col):
    mat = np.zeros((len(ACTIVATE_GRID), len(TRAIL_GRID)))
    for r in grid_rows:
        i = ACTIVATE_GRID.index(r["act_pct"])
        j = TRAIL_GRID.index(r["tr_pct"])
        mat[i, j] = r[col]
    return mat

best_i = ACTIVATE_GRID.index(best["act_pct"])
best_j = TRAIL_GRID.index(best["tr_pct"])

def draw_hm(ax, mat, title, fmt="{:.2f}", colors=None, cbar_lbl="",
            mark_best=True):
    ax.set_title(title, fontsize=11, fontweight="bold", color=TEXT_CLR, pad=8)
    ax.spines[["top","right","left","bottom"]].set_visible(False)
    cmap = LinearSegmentedColormap.from_list("c", colors or [RED, PANEL_BG, GREEN], N=256)
    im = ax.imshow(mat, aspect="auto", cmap=cmap, interpolation="nearest")
    ax.set_xticks(range(len(TRAIL_GRID)));    ax.set_xticklabels(TR_LBL, fontsize=9)
    ax.set_yticks(range(len(ACTIVATE_GRID))); ax.set_yticklabels(ACT_LBL, fontsize=9)
    ax.set_xlabel("Trailing %", fontsize=9)
    ax.set_ylabel("Activation %", fontsize=9)
    vmin, vmax = mat.min(), mat.max()
    mid = (vmin + vmax) / 2
    for i in range(mat.shape[0]):
        for j in range(mat.shape[1]):
            v = mat[i, j]
            tc = "black" if abs(v - mid) > (vmax - vmin) * 0.3 else TEXT_CLR
            ax.text(j, i, fmt.format(v), ha="center", va="center",
                    fontsize=9.5, color=tc, fontweight="bold")
    if mark_best:
        ax.add_patch(plt.Rectangle((best_j-.5, best_i-.5), 1, 1,
                     fill=False, edgecolor=YELLOW, linewidth=2.5, zorder=5))
        ax.text(best_j, best_i - 0.42, "BEST", ha="center",
                fontsize=7.5, color=YELLOW, fontweight="bold")
    cb = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cb.ax.tick_params(colors=TEXT_CLR)
    cb.set_label(cbar_lbl, color=TEXT_CLR, fontsize=8)

# ── Row 0: 3 heatmaps ─────────────────────────────────────────────────────────
ax0 = fig.add_subplot(gs[0, 0])
draw_hm(ax0, make_matrix("pnl_vs_orig"),
        f"P&L vs Original (%)\n[orig: {fmt_b(orig_total_pnl)}]",
        fmt="{:+.2f}", colors=[RED, PANEL_BG, GREEN], cbar_lbl="% vs orig")

ax1 = fig.add_subplot(gs[0, 1])
draw_hm(ax1, make_matrix("pnl_vs_ts20"),
        f"P&L vs TS20-only (%)\n[TS20: {fmt_b(ts20_total)}]",
        fmt="{:+.2f}", colors=[RED, PANEL_BG, GREEN], cbar_lbl="% vs TS20")

ax2 = fig.add_subplot(gs[0, 2])
draw_hm(ax2, make_matrix("n_ats"),
        "# Asymmetric TS Exits\n(out of 755 positions)",
        fmt="{:.0f}", colors=[PANEL_BG, BLUE, PURPLE], cbar_lbl="# exits")

# ── Row 1: Win rate + Avg gain heatmaps + Exit breakdown ─────────────────────
ax3 = fig.add_subplot(gs[1, 0])
draw_hm(ax3, make_matrix("win_rate"),
        f"Win Rate (%)\n[orig: {orig_win_rate:.1f}%  TS20: {ts20_wr:.1f}%]",
        fmt="{:.1f}", colors=[RED, PANEL_BG, GREEN], cbar_lbl="%")

ax4 = fig.add_subplot(gs[1, 1])
draw_hm(ax4, make_matrix("avg_win"),
        f"Avg Gain on Winners (%)\n[orig: {orig_avg_win:.1f}%]",
        fmt="{:.1f}", colors=[PANEL_BG, GREEN, TEAL], cbar_lbl="%")

ax5 = fig.add_subplot(gs[1, 2])
draw_hm(ax5, make_matrix("avg_loss"),
        f"Avg Loss on Losers (%)\n[orig: {orig_avg_loss:.1f}%]",
        fmt="{:.1f}", colors=[GREEN, PANEL_BG, RED], cbar_lbl="%")

# ── Row 2: P&L distribution comparison ───────────────────────────────────────
ax6 = fig.add_subplot(gs[2, :2])
ax6.set_title(
    f"P&L Distribution: Original  vs  TS20-only  vs  Best combo "
    f"(Act>={best['act_pct']*100:.0f}% / Trail={best['tr_pct']*100:.0f}%)",
    fontsize=10, fontweight="bold", color=TEXT_CLR, pad=8)
ax6.spines[["top","right","left","bottom"]].set_visible(False)
ax6.grid(True, axis="y")

orig_arr = pos_df["orig_pnl_pct"].values
best_arr = best["pcts_arr"]
all_arr  = np.concatenate([orig_arr, ts20_pcts, best_arr])
q01, q99 = np.percentile(all_arr[np.isfinite(all_arr)], [1, 99])
bins = np.linspace(q01, q99, 65)

ax6.hist(orig_arr,  bins=bins, alpha=0.40, color=BLUE,
         label=f"Original  mean={orig_avg_pct:.1f}%  WR={orig_win_rate:.0f}%")
ax6.hist(ts20_pcts, bins=bins, alpha=0.40, color=GREEN,
         label=f"TS20 only  mean={ts20_avg:.1f}%  WR={ts20_wr:.0f}%")
ax6.hist(best_arr,  bins=bins, alpha=0.45, color=YELLOW,
         label=f"Best combo  mean={best['avg_pct']:.1f}%  WR={best['win_rate']:.0f}%")

for v, c in [(orig_avg_pct, BLUE), (ts20_avg, GREEN), (best["avg_pct"], YELLOW)]:
    ax6.axvline(v, color=c, linewidth=1.3, linestyle=":")
ax6.axvline(0, color=GRID_CLR, linewidth=1, linestyle="--")
ax6.legend(fontsize=9, framealpha=0.25)
ax6.set_xlabel("Return %"); ax6.set_ylabel("# Positions")
ax6.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x:.0f}%"))

# ── Row 2: ATS exit outcomes (better vs worse than original) ──────────────────
ax7 = fig.add_subplot(gs[2, 2])
ax7.set_facecolor(PANEL_BG)
ax7.set_title(
    f"ATS Exit Outcomes\n(Act>={best['act_pct']*100:.0f}% / Trail={best['tr_pct']*100:.0f}%)",
    fontsize=10, fontweight="bold", color=TEXT_CLR, pad=8)

if ats_mask.any():
    ats_sim  = best["pcts_arr"][ats_mask]
    ats_orig = orig_pcts_arr[ats_mask]
    better_m = ats_sim >= ats_orig
    worse_m  = ~better_m

    n_better = better_m.sum()
    n_worse  = worse_m.sum()
    pie_data = [
        (f"ATS better\n({n_better})", n_better, GREEN),
        (f"Orig better\n({n_worse})", n_worse,  RED),
    ]
    lbls, szs, clrs = zip(*pie_data)
    wedges, texts, autos = ax7.pie(
        szs, labels=lbls, colors=clrs, autopct="%1.0f%%", startangle=90,
        textprops={"color": TEXT_CLR, "fontsize": 10},
        wedgeprops={"edgecolor": DARK_BG, "linewidth": 2},
        pctdistance=0.72,
    )
    for at in autos: at.set_color("black"); at.set_fontweight("bold")
    ax7.set_title(
        f"ATS Exit Outcomes  ({ats_mask.sum()} exits)\n"
        f"ATS avg: {fmt_p(ats_sim.mean())}  vs  Orig avg: {fmt_p(ats_orig.mean())}",
        fontsize=10, fontweight="bold", color=TEXT_CLR, pad=8)

# ── Row 3: Bar chart — all strategies side by side ────────────────────────────
ax8 = fig.add_subplot(gs[3, :])
ax8.set_title("Total P&L: Strategy Comparison  (2020-present, Fill=Open[D+1])",
              fontsize=11, fontweight="bold", color=TEXT_CLR, pad=8)
ax8.spines[["top","right","left","bottom"]].set_visible(False)
ax8.grid(True, axis="y")

# Collect top 8 combos
top8 = gdf.nlargest(8, "total_pnl")

bar_items = [
    ("Original\n(baseline)", orig_total_pnl, BLUE,   orig_win_rate),
    ("TS20\nonly",           ts20_total,      GREEN,  ts20_wr),
]
for _, r in top8.iterrows():
    lbl = f"Act{int(r['act_pct']*100)}%\nTr{int(r['tr_pct']*100)}%"
    clr = YELLOW if r["label"] == best["label"] else PURPLE
    bar_items.append((lbl, r["total_pnl"], clr, r["win_rate"]))

x         = np.arange(len(bar_items))
bar_vals  = [b[1]/1e9 for b in bar_items]
bar_clrs  = [b[2]     for b in bar_items]
bar_wr    = [b[3]     for b in bar_items]
bar_lbls  = [b[0]     for b in bar_items]

bars = ax8.bar(x, bar_vals, color=bar_clrs, width=0.62, zorder=3, alpha=0.88)
ax8.axhline(orig_total_pnl/1e9, color=BLUE,  linewidth=1,   linestyle=":", alpha=0.5)
ax8.axhline(ts20_total/1e9,     color=GREEN, linewidth=1.2, linestyle="--", alpha=0.6,
            label="TS20-only level")

ax8r = ax8.twinx()
ax8r.plot(x, bar_wr, color=RED, linewidth=1.8, marker="o",
          markersize=7, zorder=5, label="Win Rate %")
ax8r.set_ylabel("Win Rate %", color=RED, fontsize=10)
ax8r.tick_params(colors=RED); ax8r.set_ylim(40, 72)

for bar, val, wr in zip(bars, bar_vals, bar_wr):
    diff  = val - orig_total_pnl/1e9
    clr_t = GREEN if diff >= 0 else RED
    ax8.text(bar.get_x()+bar.get_width()/2,
             bar.get_height() + orig_total_pnl*0.006/1e9,
             f"{diff:+.1f}B\nWR {wr:.0f}%",
             ha="center", fontsize=8, color=clr_t)

ax8.set_xticks(x); ax8.set_xticklabels(bar_lbls, fontsize=9)
ax8.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}B"))
ax8.set_ylabel("Total P&L (B VND)")
ax8.legend(loc="lower right", fontsize=9, framealpha=0.25)

plt.savefig(OUT_IMG, dpi=150, bbox_inches="tight", facecolor=DARK_BG)
print(f"\nChart saved -> {Path(OUT_IMG).resolve()}")
