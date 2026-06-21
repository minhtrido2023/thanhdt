#!/usr/bin/env python3
"""
backtest_fundamental_rating.py
==============================
Yearly-rebalance backtest of the 5-axis fundamental rating system.

Strategy: each April 1 (after annual reports release), buy equal-weighted
basket from each tier (A, A+B, C, D+E) using the latest Q4 (annual) report.
Hold for 1 year, rebalance.

Compares against VNINDEX buy-and-hold over same window.

Output:
- backtest_fundamental_rating.csv  (NAV per strategy by date)
- backtest_fundamental_rating.png  (NAV curves + per-year bars + DD)
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
RATING_CSV = "fundamental_rating.csv"
PRICE_CSV  = "fundamental_rating_prices.csv"
OUT_NAV    = "backtest_fundamental_rating.csv"
OUT_PNG    = "backtest_fundamental_rating.png"

START      = "2015-04-01"   # First rebalance after 2014Q4 reports
END        = "2025-04-01"   # Last rebalance using 2024Q4 reports
TC         = 0.001          # 0.1% per side (CLAUDE.md convention)
MAX_REPORT_AGE = 400        # days; only use Q4 reports released within last ~13M

# ─── Style ───────────────────────────────────────────────────────────────────
DARK_BG="#0f1117"; PANEL_BG="#1a1d27"; GRID_CLR="#2a2d3a"; TEXT_CLR="#e0e0e0"
BLUE="#4fa3e0"; GREEN="#4ecb71"; RED="#e05c5c"; YELLOW="#f0c060"
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

# ─── Load Q4 ratings ─────────────────────────────────────────────────────────
print(f"Loading {RATING_CSV} ...")
df = pd.read_csv(RATING_CSV)
df["time"] = pd.to_datetime(df["time"])
df = df[df["quarter"].str.endswith("Q4")].copy()
print(f"  {len(df):,} Q4 rating rows, {df['ticker'].nunique()} tickers, "
      f"{df['quarter'].nunique()} years")

# Rebalance schedule
rebal_dates = pd.date_range(START, END, freq=pd.DateOffset(years=1))
print(f"  {len(rebal_dates)} rebalance dates: {rebal_dates[0].date()} -> {rebal_dates[-1].date()}")

# ─── Universe schedule ──────────────────────────────────────────────────────
def get_universe(d, tier_set):
    cutoff = d - pd.Timedelta(days=MAX_REPORT_AGE)
    valid = df[(df["time"] <= d) & (df["time"] >= cutoff) & (df["tier"].isin(tier_set))]
    if valid.empty:
        return []
    latest = valid.sort_values("time").groupby("ticker").tail(1)
    return latest["ticker"].tolist()

# Collect all tickers ever used (any tier) -> for price pull
print("Building universe schedule ...")
all_tickers = set()
schedule = {}  # date -> {tier_set_key: [tickers]}
for d in rebal_dates:
    schedule[d] = {
        "A":   get_universe(d, ["A"]),
        "AB":  get_universe(d, ["A", "B"]),
        "C":   get_universe(d, ["C"]),
        "DE":  get_universe(d, ["D", "E"]),
    }
    for tickers in schedule[d].values():
        all_tickers.update(tickers)
all_tickers = sorted(all_tickers)
print(f"  {len(all_tickers)} unique tickers across all rebalances")
for d in rebal_dates:
    print(f"  {d.date()}: A={len(schedule[d]['A'])} "
          f"AB={len(schedule[d]['AB'])} C={len(schedule[d]['C'])} DE={len(schedule[d]['DE'])}")

# ─── Pull daily Close prices ─────────────────────────────────────────────────
if os.path.exists(PRICE_CSV):
    print(f"Loading cached prices {PRICE_CSV} ...")
    prices = pd.read_csv(PRICE_CSV, parse_dates=["time"])
else:
    print(f"Pulling daily Close for {len(all_tickers)} tickers ...")
    tickers_sql = ",".join(f'"{t}"' for t in all_tickers)
    sql = f"""
    SELECT t.ticker, t.time, t.Close
    FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
    WHERE t.ticker IN UNNEST([{tickers_sql}])
      AND t.time BETWEEN "{START}" AND "{(pd.Timestamp(END) + pd.Timedelta(days=10)).date()}"
    """
    prices = bq_query(sql, "prices")
    prices["time"] = pd.to_datetime(prices["time"])
    prices.to_csv(PRICE_CSV, index=False)
    print(f"  {len(prices):,} price rows cached to {PRICE_CSV}")

price_pivot = prices.pivot_table(index="time", columns="ticker", values="Close", aggfunc="last").sort_index()
print(f"  Price pivot: {price_pivot.shape[0]} days × {price_pivot.shape[1]} tickers")

# ─── VNINDEX benchmark ──────────────────────────────────────────────────────
print("Loading VNINDEX from VNINDEX.csv ...")
vni = pd.read_csv("VNINDEX.csv", parse_dates=["time"], usecols=["time", "ticker", "Close"])
vni = vni[vni["ticker"] == "VNINDEX"][["time", "Close"]].set_index("time").sort_index()
vni = vni.loc[START:pd.Timestamp(END) + pd.Timedelta(days=10)]
print(f"  {len(vni)} VNINDEX days")

# ─── NAV simulation ──────────────────────────────────────────────────────────
def simulate(strategy_key, name):
    records = []
    nav = 1.0
    for i in range(len(rebal_dates) - 1):
        d_curr, d_next = rebal_dates[i], rebal_dates[i+1]
        universe = schedule[d_curr][strategy_key]
        tc_cost = TC if i == 0 else 2 * TC  # first entry vs rebalance
        nav *= (1 - tc_cost)

        if not universe:
            records.append((d_curr, nav))
            continue

        period = price_pivot.loc[d_curr:d_next]
        if period.empty:
            records.append((d_curr, nav)); continue
        # Snap to nearest available trading day for d_curr
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

    out = pd.DataFrame(records, columns=["time", "nav"]).drop_duplicates("time", keep="last")
    out = out.sort_values("time").set_index("time")
    print(f"  {name:<8} final NAV = {out['nav'].iloc[-1]:.3f}x")
    return out

print("\nSimulating ...")
nav_A   = simulate("A",   "A-tier")
nav_AB  = simulate("AB",  "A+B")
nav_C   = simulate("C",   "C-tier")
nav_DE  = simulate("DE",  "D+E")

# VNINDEX B&H aligned to same start
common_start = max(nav_A.index[0], vni.index[0])
common_end   = min(nav_A.index[-1], vni.index[-1])
vni_aligned = vni.loc[common_start:common_end].copy()
vni_aligned["nav"] = vni_aligned["Close"] / vni_aligned["Close"].iloc[0]

# ─── Metrics ────────────────────────────────────────────────────────────────
def metrics(nav_series, name):
    s = nav_series["nav"].dropna()
    if len(s) < 2:
        return None
    days = (s.index[-1] - s.index[0]).days
    years = days / 365.25
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1 / years) - 1
    daily_ret = s.pct_change().dropna()
    spy = len(daily_ret) / years   # actual sessions/year
    sharpe = daily_ret.mean() / daily_ret.std() * np.sqrt(spy) if daily_ret.std() > 0 else 0
    rolling_max = s.expanding().max()
    dd = s / rolling_max - 1
    maxdd = dd.min()
    calmar = cagr / abs(maxdd) if maxdd < 0 else np.nan
    print(f"  {name:<14} CAGR={cagr*100:6.2f}%  Sharpe={sharpe:5.2f}  "
          f"MaxDD={maxdd*100:6.1f}%  Calmar={calmar:5.2f}  Final={s.iloc[-1]:.2f}x")
    return dict(name=name, cagr=cagr, sharpe=sharpe, maxdd=maxdd, calmar=calmar, final=s.iloc[-1])

print("\n=== Performance Metrics ===")
m_A   = metrics(nav_A,   "A-tier")
m_AB  = metrics(nav_AB,  "A+B")
m_C   = metrics(nav_C,   "C-tier")
m_DE  = metrics(nav_DE,  "D+E")
m_VNI = metrics(vni_aligned[["nav"]], "VNINDEX B&H")

# ─── Per-year returns ───────────────────────────────────────────────────────
print("\n=== Annual Returns (rebalance-to-rebalance) ===")
print(f"  {'Year':<10}{'A':>8}{'A+B':>8}{'C':>8}{'D+E':>8}{'VNI':>8}")
for i in range(len(rebal_dates) - 1):
    d_curr, d_next = rebal_dates[i], rebal_dates[i+1]
    def ret(s):
        try:
            v0 = s.loc[s.index >= d_curr].iloc[0]
            v1 = s.loc[s.index <= d_next].iloc[-1]
            return (v1 / v0 - 1) * 100
        except: return float("nan")
    label = f"{d_curr.year}-{d_next.year-2000:02d}"
    rA  = ret(nav_A["nav"]);  rAB = ret(nav_AB["nav"])
    rC  = ret(nav_C["nav"]);  rDE = ret(nav_DE["nav"])
    rV  = ret(vni_aligned["nav"])
    print(f"  {label:<10}{rA:>7.1f}%{rAB:>7.1f}%{rC:>7.1f}%{rDE:>7.1f}%{rV:>7.1f}%")

# ─── Save NAVs ──────────────────────────────────────────────────────────────
combo = pd.concat([
    nav_A["nav"].rename("A"),
    nav_AB["nav"].rename("AB"),
    nav_C["nav"].rename("C"),
    nav_DE["nav"].rename("DE"),
    vni_aligned["nav"].rename("VNINDEX"),
], axis=1).sort_index()
combo.to_csv(OUT_NAV)
print(f"\nSaved NAV series -> {OUT_NAV}")

# ─── Plot ────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(3, 1, figsize=(15, 13),
                         gridspec_kw={"height_ratios": [3, 1.3, 1.3]})

# (a) NAV curves (log scale)
ax = axes[0]
ax.plot(nav_A.index, nav_A["nav"], label=f"A-tier (final={m_A['final']:.2f}x, CAGR={m_A['cagr']*100:.1f}%)",
        color=GREEN, linewidth=2.0)
ax.plot(nav_AB.index, nav_AB["nav"], label=f"A+B (final={m_AB['final']:.2f}x, CAGR={m_AB['cagr']*100:.1f}%)",
        color=BLUE, linewidth=1.8)
ax.plot(nav_C.index, nav_C["nav"], label=f"C-tier (final={m_C['final']:.2f}x, CAGR={m_C['cagr']*100:.1f}%)",
        color=YELLOW, linewidth=1.5, alpha=0.85)
ax.plot(nav_DE.index, nav_DE["nav"], label=f"D+E (final={m_DE['final']:.2f}x, CAGR={m_DE['cagr']*100:.1f}%)",
        color=RED, linewidth=1.5, alpha=0.85)
ax.plot(vni_aligned.index, vni_aligned["nav"],
        label=f"VNINDEX B&H (final={m_VNI['final']:.2f}x, CAGR={m_VNI['cagr']*100:.1f}%)",
        color="white", linewidth=1.5, linestyle="--", alpha=0.8)
ax.set_yscale("log")
ax.set_ylabel("NAV (log scale)")
ax.set_title("Fundamental Rating Backtest — Annual Rebalance (Q4-only ratings, equal-weight)",
             fontsize=14, color=TEXT_CLR, pad=10)
ax.legend(loc="upper left", framealpha=0.85, fontsize=10)
ax.grid(True, which="both", alpha=0.3)

# (b) Drawdown
ax = axes[1]
for label, n, col in [("A", nav_A, GREEN), ("A+B", nav_AB, BLUE),
                      ("D+E", nav_DE, RED), ("VNI", vni_aligned[["nav"]], "white")]:
    s = n["nav"]
    dd = s / s.expanding().max() - 1
    ax.fill_between(dd.index, dd.values * 100, 0,
                    color=col, alpha=0.35 if label != "VNI" else 0.15,
                    label=f"{label} (MaxDD={dd.min()*100:.1f}%)")
ax.set_ylabel("Drawdown (%)")
ax.set_title("Drawdown comparison")
ax.legend(loc="lower left", framealpha=0.85, fontsize=9)
ax.grid(True, alpha=0.3)

# (c) Annual returns bar chart
ax = axes[2]
years_x, rA_y, rAB_y, rC_y, rDE_y, rV_y = [], [], [], [], [], []
for i in range(len(rebal_dates) - 1):
    d_curr, d_next = rebal_dates[i], rebal_dates[i+1]
    def ret(s):
        try:
            v0 = s.loc[s.index >= d_curr].iloc[0]
            v1 = s.loc[s.index <= d_next].iloc[-1]
            return (v1 / v0 - 1) * 100
        except: return float("nan")
    years_x.append(f"{d_curr.year}")
    rA_y.append(ret(nav_A["nav"]));   rAB_y.append(ret(nav_AB["nav"]))
    rC_y.append(ret(nav_C["nav"]));   rDE_y.append(ret(nav_DE["nav"]))
    rV_y.append(ret(vni_aligned["nav"]))

x = np.arange(len(years_x)); width = 0.18
ax.bar(x - 2*width, rA_y,  width, label="A",     color=GREEN)
ax.bar(x - width,   rAB_y, width, label="A+B",   color=BLUE)
ax.bar(x,           rC_y,  width, label="C",     color=YELLOW)
ax.bar(x + width,   rDE_y, width, label="D+E",   color=RED)
ax.bar(x + 2*width, rV_y,  width, label="VNI",   color="white", alpha=0.7)
ax.axhline(0, color=GRID_CLR, linewidth=0.8)
ax.set_xticks(x); ax.set_xticklabels(years_x)
ax.set_ylabel("Return (%)")
ax.set_title("Annual returns by tier (rebalance-to-rebalance)")
ax.legend(loc="best", framealpha=0.85, fontsize=9, ncol=5)
ax.grid(True, alpha=0.3, axis="y")

plt.tight_layout()
plt.savefig(OUT_PNG, dpi=120, facecolor=DARK_BG)
print(f"Saved chart -> {OUT_PNG}")
