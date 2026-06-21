#!/usr/bin/env python3
"""
backtest_fundamental_v2.py
==========================
Multi-strategy comparison of the 5-axis fundamental rating system.

Strategies:
1. Original A     — Q4-only ratings, yearly rebalance, tier A
2. Top-30 yearly  — Q4-only ratings, yearly rebalance, top 30 by total_score
3. Quarterly A    — All-quarters ratings, quarterly rebalance, tier A
4. Overlay A      — Q4-only ratings, yearly rebalance, tier A * 5-state allocation
5. Combo          — All-quarters ratings, quarterly rebalance, top 30, with overlay

5-state allocation: CRISIS=0%, BEAR=20%, NEUTRAL=70%, BULL=100%, EX-BULL=130%
Cash deposit=6%/yr, margin borrow=10%/yr, TC=0.1% per side.

Output:
- backtest_fundamental_v2.csv  (NAV series per strategy)
- backtest_fundamental_v2.png  (NAV + drawdown comparison)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

PROJECT   = "lithe-record-440915-m9"
BQ_BIN    = r"bq"
PRICE_CSV = "fundamental_rating_prices.csv"
START     = "2015-04-01"
END       = "2025-04-01"
TC        = 0.001    # 0.1% per side
DEPOSIT   = 0.06     # cash yield
BORROW    = 0.10     # margin cost
STATE_ALLOC = {1: 0.0, 2: 0.20, 3: 0.70, 4: 1.0, 5: 1.30}

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

# ─── BQ helper ───────────────────────────────────────────────────────────────
def bq_query(sql, label=""):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = (f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
               f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=900, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0:
        raise RuntimeError(f"[BQ ERROR] {label}: {(r.stdout or r.stderr)[:600]}")
    txt = r.stdout.strip()
    return pd.read_csv(StringIO(txt)) if txt else pd.DataFrame()

# ─── Load ratings ────────────────────────────────────────────────────────────
print("Loading ratings ...")
rating_q4  = pd.read_csv("fundamental_rating.csv");      rating_q4["time"]  = pd.to_datetime(rating_q4["time"])
rating_all = pd.read_csv("fundamental_rating_all.csv");  rating_all["time"] = pd.to_datetime(rating_all["time"])
print(f"  Q4-only:    {len(rating_q4):,} rows")
print(f"  All-quarter:{len(rating_all):,} rows")

# ─── Load 5-state history ───────────────────────────────────────────────────
print("Loading 5-state history ...")
state_df = pd.read_csv("vnindex_state_history.csv", parse_dates=["time"])
state_df["alloc"] = state_df["state"].map(STATE_ALLOC)
state_df = state_df.set_index("time")[["state","state_name","alloc"]].sort_index()
print(f"  {len(state_df):,} state days, {state_df.index.min().date()} to {state_df.index.max().date()}")

# ─── Strategies definition ──────────────────────────────────────────────────
rebal_yearly = pd.date_range(START, END, freq=pd.DateOffset(years=1))
rebal_qtr    = pd.date_range(START, END, freq=pd.DateOffset(months=3))

STRATEGIES = {
    "1. Original A":          dict(rebal=rebal_yearly, ratings=rating_q4,  selector="tier_A",  max_age=400, overlay=False),
    "2. Top-30 yearly":       dict(rebal=rebal_yearly, ratings=rating_q4,  selector="topN_30", max_age=400, overlay=False),
    "3. Quarterly A":         dict(rebal=rebal_qtr,    ratings=rating_all, selector="tier_A",  max_age=150, overlay=False),
    "4. Overlay A yearly":    dict(rebal=rebal_yearly, ratings=rating_q4,  selector="tier_A",  max_age=400, overlay=True),
    "5. Combo (Top-30+Q+OL)": dict(rebal=rebal_qtr,    ratings=rating_all, selector="topN_30", max_age=150, overlay=True),
}

# ─── Universe selector ──────────────────────────────────────────────────────
def select_universe(rating_df, d, selector, max_age):
    cutoff = d - pd.Timedelta(days=max_age)
    valid = rating_df[(rating_df["time"] <= d) & (rating_df["time"] >= cutoff)]
    if valid.empty:
        return []
    latest = valid.sort_values("time").groupby("ticker").tail(1)
    if selector == "tier_A":
        return latest[latest["tier"] == "A"]["ticker"].tolist()
    if selector == "topN_30":
        return latest.sort_values("total_score", ascending=False).head(30)["ticker"].tolist()
    return []

# Build all schedules
print("\nBuilding universe schedules ...")
all_tickers = set()
schedules = {}
for name, s in STRATEGIES.items():
    sched = {}
    for d in s["rebal"]:
        u = select_universe(s["ratings"], d, s["selector"], s["max_age"])
        sched[d] = u
        all_tickers.update(u)
    schedules[name] = sched
    sizes = [len(sched[d]) for d in s["rebal"]]
    print(f"  {name:<26} rebals={len(s['rebal']):>2}  univ size: min={min(sizes)}, max={max(sizes)}, avg={np.mean(sizes):.0f}")

print(f"  {len(all_tickers)} unique tickers across all strategies")

# ─── Load/pull prices ───────────────────────────────────────────────────────
prices = None
need_pull = True
if os.path.exists(PRICE_CSV):
    prices = pd.read_csv(PRICE_CSV, parse_dates=["time"])
    cached_tickers = set(prices["ticker"].unique())
    missing = all_tickers - cached_tickers
    if not missing:
        print(f"\n  Using cached prices ({len(cached_tickers)} tickers)")
        need_pull = False
    else:
        print(f"\n  Cache has {len(cached_tickers)} tickers, need {len(missing)} more")
        # Pull missing only
        tickers_sql = ",".join(f'"{t}"' for t in sorted(missing))
        sql = f"""
        SELECT t.ticker, t.time, t.Close
        FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
        WHERE t.ticker IN UNNEST([{tickers_sql}])
          AND t.time BETWEEN "{START}" AND "{(pd.Timestamp(END) + pd.Timedelta(days=10)).date()}"
        """
        extra = bq_query(sql, "delta")
        extra["time"] = pd.to_datetime(extra["time"])
        prices = pd.concat([prices, extra], ignore_index=True)
        prices.to_csv(PRICE_CSV, index=False)
        print(f"  Cache updated with {len(extra):,} new rows")
        need_pull = False

if need_pull:
    print("Pulling all prices ...")
    tickers_sql = ",".join(f'"{t}"' for t in sorted(all_tickers))
    sql = f"""
    SELECT t.ticker, t.time, t.Close
    FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
    WHERE t.ticker IN UNNEST([{tickers_sql}])
      AND t.time BETWEEN "{START}" AND "{(pd.Timestamp(END) + pd.Timedelta(days=10)).date()}"
    """
    prices = bq_query(sql, "prices")
    prices["time"] = pd.to_datetime(prices["time"])
    prices.to_csv(PRICE_CSV, index=False)

price_pivot = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
print(f"  Price pivot: {price_pivot.shape[0]} days x {price_pivot.shape[1]} tickers")

# ─── VNINDEX ────────────────────────────────────────────────────────────────
vni = pd.read_csv("VNINDEX.csv", parse_dates=["time"], usecols=["time","ticker","Close"])
vni = vni[vni["ticker"]=="VNINDEX"][["time","Close"]].set_index("time").sort_index()
vni = vni.loc[START:pd.Timestamp(END) + pd.Timedelta(days=10)]
vni_nav = pd.DataFrame({"nav": vni["Close"] / vni["Close"].iloc[0]})

# ─── Basic NAV simulation (fully invested) ──────────────────────────────────
def simulate_basic(rebal_dates, schedule):
    records = []
    nav = 1.0
    for i in range(len(rebal_dates) - 1):
        d_curr, d_next = rebal_dates[i], rebal_dates[i+1]
        universe = schedule[d_curr]
        tc_cost = TC if i == 0 else 2 * TC
        nav *= (1 - tc_cost)

        if not universe:
            records.append((d_curr, nav)); continue
        period = price_pivot.loc[d_curr:d_next]
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

# ─── Apply 5-state market overlay ───────────────────────────────────────────
def apply_overlay(nav_basic):
    s = nav_basic["nav"].copy()
    r_stock = s.pct_change().fillna(0).values
    w = state_df["alloc"].reindex(s.index).ffill().fillna(0.7).values

    r_cash_d   = DEPOSIT / 365
    r_borrow_d = BORROW / 365

    new_nav = np.zeros(len(s)); new_nav[0] = 1.0
    prev_w = w[0]
    for i in range(1, len(s)):
        wt = w[i]
        rt = r_stock[i]
        cash_part   = max(0.0, 1 - wt) * r_cash_d
        margin_part = max(0.0, wt - 1) * r_borrow_d
        dw = abs(wt - prev_w)
        tc_cost = dw * TC if dw > 0.03 else 0.0
        new_nav[i] = new_nav[i-1] * (1 + wt*rt + cash_part - margin_part - tc_cost)
        prev_w = wt
    return pd.DataFrame({"nav": new_nav}, index=s.index)

# ─── Run all strategies ─────────────────────────────────────────────────────
print("\nSimulating ...")
results = {}
for name, s in STRATEGIES.items():
    nav_basic = simulate_basic(s["rebal"], schedules[name])
    if s["overlay"]:
        results[name] = apply_overlay(nav_basic)
        kind = "(stock x state-alloc overlay)"
    else:
        results[name] = nav_basic
        kind = "(fully invested)"
    print(f"  {name:<26} final={results[name]['nav'].iloc[-1]:.3f}x   {kind}")

# ─── Metrics ────────────────────────────────────────────────────────────────
def metrics(nav_series):
    s = nav_series["nav"].dropna()
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

print("\n=== Performance Comparison ===")
header = f"  {'Strategy':<26}{'CAGR':>8}{'Sharpe':>8}{'MaxDD':>8}{'Calmar':>8}{'Final':>8}"
print(header)
print("  " + "-" * (len(header)-2))
all_metrics = {}
for name, nav in results.items():
    m = metrics(nav); all_metrics[name] = m
    print(f"  {name:<26}{m['cagr']*100:>7.2f}%{m['sharpe']:>8.2f}{m['maxdd']*100:>7.1f}%{m['calmar']:>8.2f}{m['final']:>8.2f}x")
mvni = metrics(vni_nav); all_metrics["VNINDEX B&H"] = mvni
print(f"  {'VNINDEX B&H':<26}{mvni['cagr']*100:>7.2f}%{mvni['sharpe']:>8.2f}{mvni['maxdd']*100:>7.1f}%{mvni['calmar']:>8.2f}{mvni['final']:>8.2f}x")

# ─── Save NAV series ────────────────────────────────────────────────────────
combo = pd.concat(
    [r["nav"].rename(name) for name, r in results.items()] + [vni_nav["nav"].rename("VNINDEX")],
    axis=1
).sort_index()
combo.to_csv("backtest_fundamental_v2.csv")
print(f"\nSaved NAV -> backtest_fundamental_v2.csv")

# ─── Plot ────────────────────────────────────────────────────────────────────
COLORS = [GREEN, BLUE, YELLOW, ORANGE, PURPLE]
fig, axes = plt.subplots(2, 1, figsize=(15, 11), gridspec_kw={"height_ratios":[3, 1.4]})

# (a) NAV log
ax = axes[0]
for (name, nav), col in zip(results.items(), COLORS):
    m = all_metrics[name]
    ax.plot(nav.index, nav["nav"],
            label=f"{name}  (final={m['final']:.2f}x, CAGR={m['cagr']*100:.1f}%, MaxDD={m['maxdd']*100:.0f}%)",
            color=col, linewidth=1.8)
ax.plot(vni_nav.index, vni_nav["nav"],
        label=f"VNINDEX B&H  (final={mvni['final']:.2f}x, CAGR={mvni['cagr']*100:.1f}%, MaxDD={mvni['maxdd']*100:.0f}%)",
        color="white", linewidth=1.5, linestyle="--", alpha=0.8)
ax.set_yscale("log")
ax.legend(loc="upper left", fontsize=9, framealpha=0.85)
ax.grid(True, which="both", alpha=0.3)
ax.set_ylabel("NAV (log scale)")
ax.set_title("Fundamental Rating v2 — 5-Strategy Comparison (2015-2025)", fontsize=14, pad=10)

# (b) Drawdown
ax = axes[1]
for (name, nav), col in zip(results.items(), COLORS):
    s = nav["nav"]; dd = s / s.expanding().max() - 1
    ax.fill_between(dd.index, dd.values * 100, 0, color=col, alpha=0.25)
    ax.plot(dd.index, dd.values * 100, color=col, linewidth=1.0,
            label=f"{name} (MaxDD={dd.min()*100:.1f}%)")
s = vni_nav["nav"]; dd = s / s.expanding().max() - 1
ax.plot(dd.index, dd.values * 100, color="white", linewidth=1.0, linestyle="--", alpha=0.6,
        label=f"VNINDEX MaxDD={dd.min()*100:.1f}%")
ax.set_ylabel("Drawdown (%)")
ax.set_title("Drawdown comparison")
ax.legend(loc="lower left", fontsize=8.5, ncol=2, framealpha=0.85)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("backtest_fundamental_v2.png", dpi=120, facecolor=DARK_BG)
print("Saved chart -> backtest_fundamental_v2.png")
