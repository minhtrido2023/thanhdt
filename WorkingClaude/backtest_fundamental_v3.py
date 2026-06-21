#!/usr/bin/env python3
"""
backtest_fundamental_v3.py
==========================
(i)  Top-N sweep    : N in {15, 20, 30, 40, 50} for yearly + combo configs
(ii) IS/OOS split   : 2015-2020 (IS) vs 2020-2025 (OOS) for chosen strategies

Reuses helpers from v2 (price cache, state history, rating CSVs).

Output:
- backtest_fundamental_v3_topN.csv   (Top-N sweep metrics table)
- backtest_fundamental_v3_isoos.csv  (IS/OOS split metrics table)
- backtest_fundamental_v3.png        (NAV curves: Top-N sweep + IS/OOS bars)
"""
import warnings; warnings.filterwarnings("ignore")
import os
from io import StringIO
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PRICE_CSV = "data/fundamental_rating_prices.csv"
START     = "2015-04-01"
END       = "2025-04-01"
SPLIT     = "2020-04-01"          # boundary between IS and OOS
TC        = 0.001
DEPOSIT   = 0.06
BORROW    = 0.10
STATE_ALLOC = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}
TOP_N_LIST = [15, 20, 30, 40, 50]

# ─── Style ───────────────────────────────────────────────────────────────────
DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
GREEN="#4ecb71"; BLUE="#4fa3e0"; RED="#e05c5c"; YELLOW="#f0c060"
ORANGE="#f0904a"; PURPLE="#b57bee"; TEAL="#4ecbbb"; CYAN="#4ecbee"
plt.rcParams.update({
    "figure.facecolor":DARK_BG,"axes.facecolor":PANEL_BG,"axes.edgecolor":GRID_CLR,
    "axes.labelcolor":TEXT_CLR,"xtick.color":TEXT_CLR,"ytick.color":TEXT_CLR,
    "text.color":TEXT_CLR,"grid.color":GRID_CLR,"grid.linestyle":"--","grid.alpha":0.4,
    "font.family":"DejaVu Sans",
})

# ─── Load data ───────────────────────────────────────────────────────────────
print("Loading ...")
rating_q4  = pd.read_csv("data/fundamental_rating.csv");      rating_q4["time"]  = pd.to_datetime(rating_q4["time"])
rating_all = pd.read_csv("data/fundamental_rating_all.csv");  rating_all["time"] = pd.to_datetime(rating_all["time"])

state_df = pd.read_csv("data/vnindex_state_history.csv", parse_dates=["time"])
state_df["alloc"] = state_df["state"].map(STATE_ALLOC)
state_df = state_df.set_index("time")[["state","alloc"]].sort_index()

prices = pd.read_csv(PRICE_CSV, parse_dates=["time"])
price_pivot = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
print(f"  Q4-only ratings: {len(rating_q4):,}, all: {len(rating_all):,}")
print(f"  State days: {len(state_df):,}, prices: {price_pivot.shape}")

vni = pd.read_csv("data/VNINDEX.csv", parse_dates=["time"], usecols=["time","ticker","Close"])
vni = vni[vni["ticker"]=="VNINDEX"][["time","Close"]].set_index("time").sort_index()
vni = vni.loc[START:pd.Timestamp(END) + pd.Timedelta(days=10)]

# ─── Schedules ──────────────────────────────────────────────────────────────
rebal_yearly = pd.date_range(START, END, freq=pd.DateOffset(years=1))
rebal_qtr    = pd.date_range(START, END, freq=pd.DateOffset(months=3))

def select_topN(rating_df, d, N, max_age):
    cutoff = d - pd.Timedelta(days=max_age)
    valid = rating_df[(rating_df["time"] <= d) & (rating_df["time"] >= cutoff)]
    if valid.empty:
        return []
    latest = valid.sort_values("time").groupby("ticker").tail(1)
    return latest.sort_values("total_score", ascending=False).head(N)["ticker"].tolist()

def build_schedule(rating_df, rebal_dates, N, max_age):
    return {d: select_topN(rating_df, d, N, max_age) for d in rebal_dates}

# ─── Simulation ─────────────────────────────────────────────────────────────
def simulate_basic(rebal_dates, schedule, price_subset=None):
    pp = price_subset if price_subset is not None else price_pivot
    records = []; nav = 1.0
    for i in range(len(rebal_dates) - 1):
        d_curr, d_next = rebal_dates[i], rebal_dates[i+1]
        universe = schedule[d_curr]
        tc_cost = TC if i == 0 else 2 * TC
        nav *= (1 - tc_cost)
        if not universe:
            records.append((d_curr, nav)); continue
        period = pp.loc[d_curr:d_next]
        if period.empty:
            records.append((d_curr, nav)); continue
        first_row = period.iloc[0]
        valid = [t for t in universe if t in first_row.index and pd.notna(first_row[t])]
        if not valid:
            records.append((d_curr, nav)); continue
        sub = period[valid].ffill()
        norm = sub.div(sub.iloc[0])
        port = norm.mean(axis=1)
        for d, p in port.items():
            records.append((d, nav * p))
        nav = nav * port.iloc[-1]
    out = pd.DataFrame(records, columns=["time","nav"]).drop_duplicates("time", keep="last")
    return out.sort_values("time").set_index("time")

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

def run_strategy(N, mode):
    """mode in {'yearly', 'combo'}"""
    if mode == "yearly":
        sched = build_schedule(rating_q4, rebal_yearly, N, max_age=400)
        nav = simulate_basic(rebal_yearly, sched)
        return nav
    if mode == "combo":
        sched = build_schedule(rating_all, rebal_qtr, N, max_age=150)
        nav = simulate_basic(rebal_qtr, sched)
        return apply_overlay(nav)

def metrics(nav_series, start_d=None, end_d=None):
    s = nav_series["nav"].dropna()
    if start_d:
        s = s.loc[start_d:]
        s = s / s.iloc[0]
    if end_d:
        s = s.loc[:end_d]
    if len(s) < 2:
        return None
    days = (s.index[-1] - s.index[0]).days
    years = days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/years) - 1
    daily_ret = s.pct_change().dropna()
    spy = len(daily_ret) / years
    sharpe = daily_ret.mean() / daily_ret.std() * np.sqrt(spy) if daily_ret.std() > 0 else 0
    rolling_max = s.expanding().max()
    dd = s / rolling_max - 1
    maxdd = dd.min()
    calmar = cagr / abs(maxdd) if maxdd < 0 else np.nan
    return dict(cagr=cagr, sharpe=sharpe, maxdd=maxdd, calmar=calmar, final=s.iloc[-1])

# ─── (i) Top-N sweep ────────────────────────────────────────────────────────
print("\n=== (i) Top-N Sweep ===")
sweep = []
sweep_navs = {}  # for plotting
for N in TOP_N_LIST:
    for mode in ["yearly", "combo"]:
        nav = run_strategy(N, mode)
        m = metrics(nav)
        sweep.append(dict(N=N, mode=mode, **m))
        sweep_navs[(N, mode)] = nav

sweep_df = pd.DataFrame(sweep)
print(f"\n  {'Mode':<8}{'N':>4}  {'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}{'Final':>8}")
print("  " + "-"*52)
for mode in ["yearly", "combo"]:
    for _, r in sweep_df[sweep_df["mode"]==mode].iterrows():
        print(f"  {mode:<8}{int(r['N']):>4}  {r['cagr']*100:>7.2f}%{r['sharpe']:>8.2f}"
              f"{r['maxdd']*100:>7.1f}%{r['calmar']:>8.2f}{r['final']:>8.2f}x")
    print()
sweep_df.to_csv("data/backtest_fundamental_v3_topN.csv", index=False)

# ─── (ii) IS/OOS split for selected strategies ──────────────────────────────
print("=== (ii) IS/OOS Split — robustness check ===")
print(f"  IS:  {START} to {SPLIT}  ({(pd.Timestamp(SPLIT)-pd.Timestamp(START)).days/365.25:.1f}y)")
print(f"  OOS: {SPLIT} to {END}    ({(pd.Timestamp(END)-pd.Timestamp(SPLIT)).days/365.25:.1f}y)")

# Re-run a few representative strategies on full period, then split metrics
# Strategy 4 (Overlay A yearly) — reuse from v2 logic: tier_A yearly + overlay
def select_tierA(rating_df, d, max_age):
    cutoff = d - pd.Timedelta(days=max_age)
    valid = rating_df[(rating_df["time"] <= d) & (rating_df["time"] >= cutoff)]
    if valid.empty: return []
    latest = valid.sort_values("time").groupby("ticker").tail(1)
    return latest[latest["tier"]=="A"]["ticker"].tolist()

sched_tierA_yr = {d: select_tierA(rating_q4, d, 400) for d in rebal_yearly}
nav_overlay_A  = apply_overlay(simulate_basic(rebal_yearly, sched_tierA_yr))

# Pick best Combo from sweep
combo_best = sweep_df[sweep_df["mode"]=="combo"].sort_values("calmar", ascending=False).iloc[0]
N_best = int(combo_best["N"])
print(f"  Best Combo by Calmar: Top-{N_best} (Calmar={combo_best['calmar']:.2f})")
nav_combo_best = sweep_navs[(N_best, "combo")]

# Best yearly Top-N
yearly_best = sweep_df[sweep_df["mode"]=="yearly"].sort_values("calmar", ascending=False).iloc[0]
N_yearly_best = int(yearly_best["N"])
nav_yearly_best = sweep_navs[(N_yearly_best, "yearly")]

# VNINDEX B&H
vni_nav = pd.DataFrame({"nav": vni["Close"] / vni["Close"].iloc[0]})

isoos_strategies = {
    f"Yearly Top-{N_yearly_best} (no overlay)": nav_yearly_best,
    "Overlay A yearly (Strat 4)":               nav_overlay_A,
    f"Combo Top-{N_best}+Q+OL (Strat 5)":       nav_combo_best,
    "VNINDEX B&H":                              vni_nav,
}

isoos_rows = []
print(f"\n  {'Strategy':<32}{'Window':<5}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}")
print("  " + "-"*73)
for name, nav in isoos_strategies.items():
    for window, sd, ed in [("IS", START, SPLIT), ("OOS", SPLIT, END), ("Full", START, END)]:
        m = metrics(nav, sd, ed)
        if m is None: continue
        isoos_rows.append(dict(strategy=name, window=window, **m))
        print(f"  {name:<32}{window:<5}{m['cagr']*100:>7.2f}%{m['sharpe']:>8.2f}"
              f"{m['maxdd']*100:>7.1f}%{m['calmar']:>8.2f}")
    print()

isoos_df = pd.DataFrame(isoos_rows)
isoos_df.to_csv("data/backtest_fundamental_v3_isoos.csv", index=False)

# ─── Plot ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(16, 12))
gs = fig.add_gridspec(3, 2, height_ratios=[2, 1.4, 1.4], hspace=0.35, wspace=0.25)

# (a) Top-N CAGR vs Calmar curves
ax = fig.add_subplot(gs[0, 0])
y_cagr = [sweep_df[(sweep_df["mode"]=="yearly") & (sweep_df["N"]==N)]["cagr"].iloc[0]*100 for N in TOP_N_LIST]
c_cagr = [sweep_df[(sweep_df["mode"]=="combo") & (sweep_df["N"]==N)]["cagr"].iloc[0]*100 for N in TOP_N_LIST]
y_cal  = [sweep_df[(sweep_df["mode"]=="yearly") & (sweep_df["N"]==N)]["calmar"].iloc[0] for N in TOP_N_LIST]
c_cal  = [sweep_df[(sweep_df["mode"]=="combo") & (sweep_df["N"]==N)]["calmar"].iloc[0] for N in TOP_N_LIST]
ax.plot(TOP_N_LIST, y_cagr, "o-", color=BLUE, label="Yearly CAGR", linewidth=2)
ax.plot(TOP_N_LIST, c_cagr, "s-", color=GREEN, label="Combo CAGR", linewidth=2)
ax.set_xlabel("Top-N"); ax.set_ylabel("CAGR (%)")
ax.set_title("(i) Top-N sweep: CAGR")
ax.legend(); ax.grid(True, alpha=0.3)

ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(TOP_N_LIST, y_cal, "o-", color=BLUE, label="Yearly Calmar", linewidth=2)
ax2.plot(TOP_N_LIST, c_cal, "s-", color=GREEN, label="Combo Calmar", linewidth=2)
ax2.set_xlabel("Top-N"); ax2.set_ylabel("Calmar (CAGR/|MaxDD|)")
ax2.set_title("(i) Top-N sweep: Calmar (risk-adjusted)")
ax2.legend(); ax2.grid(True, alpha=0.3)

# (b) Top-N NAV curves (combo only — clearer)
ax = fig.add_subplot(gs[1, :])
shades = [GREEN, TEAL, BLUE, PURPLE, ORANGE]
for N, col in zip(TOP_N_LIST, shades):
    nav = sweep_navs[(N, "combo")]
    m = metrics(nav)
    ax.plot(nav.index, nav["nav"], label=f"Combo Top-{N} ({m['final']:.2f}x, Calmar={m['calmar']:.2f})",
            color=col, linewidth=1.5)
ax.plot(vni_nav.index, vni_nav["nav"], color="white", linewidth=1.0, linestyle="--", alpha=0.6,
        label="VNINDEX B&H")
ax.set_yscale("log"); ax.legend(loc="upper left", fontsize=9)
ax.grid(True, which="both", alpha=0.3); ax.set_ylabel("NAV (log)")
ax.axvline(pd.Timestamp(SPLIT), color=YELLOW, linestyle=":", linewidth=1.0, alpha=0.7)
ax.text(pd.Timestamp(SPLIT), ax.get_ylim()[1]*0.7, "  IS / OOS", color=YELLOW, fontsize=10)
ax.set_title("Combo Top-N NAV curves (with IS/OOS split line)")

# (c) IS/OOS bar chart
ax = fig.add_subplot(gs[2, :])
strats = list(isoos_strategies.keys())
x = np.arange(len(strats)); width = 0.27
is_cagr = [isoos_df[(isoos_df["strategy"]==s) & (isoos_df["window"]=="IS")]["cagr"].iloc[0]*100 for s in strats]
oos_cagr = [isoos_df[(isoos_df["strategy"]==s) & (isoos_df["window"]=="OOS")]["cagr"].iloc[0]*100 for s in strats]
full_cagr = [isoos_df[(isoos_df["strategy"]==s) & (isoos_df["window"]=="Full")]["cagr"].iloc[0]*100 for s in strats]
ax.bar(x - width, is_cagr,  width, label="IS (2015-2020)",  color=BLUE)
ax.bar(x,         oos_cagr, width, label="OOS (2020-2025)", color=GREEN)
ax.bar(x + width, full_cagr,width, label="Full (2015-2025)",color=YELLOW, alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(strats, rotation=10, ha="right", fontsize=9)
ax.set_ylabel("CAGR (%)"); ax.set_title("(ii) IS/OOS robustness — CAGR by window")
ax.axhline(0, color=GRID_CLR, linewidth=0.8); ax.legend(loc="upper right", fontsize=9)
ax.grid(True, alpha=0.3, axis="y")
for i, s in enumerate(strats):
    ax.text(x[i] - width, is_cagr[i] + 0.4, f"{is_cagr[i]:.1f}", ha="center", fontsize=8, color=TEXT_CLR)
    ax.text(x[i],         oos_cagr[i] + 0.4, f"{oos_cagr[i]:.1f}", ha="center", fontsize=8, color=TEXT_CLR)
    ax.text(x[i] + width, full_cagr[i]+ 0.4, f"{full_cagr[i]:.1f}",ha="center", fontsize=8, color=TEXT_CLR)

plt.suptitle("Fundamental Rating v3 — Top-N Sweep & IS/OOS Robustness", fontsize=15, color=TEXT_CLR, y=0.995)
plt.savefig("backtest_fundamental_v3.png", dpi=120, facecolor=DARK_BG, bbox_inches="tight")
print("\nSaved chart -> backtest_fundamental_v3.png")
print("Saved metrics -> backtest_fundamental_v3_topN.csv, backtest_fundamental_v3_isoos.csv")
