#!/usr/bin/env python3
"""
backtest_quality_tactical.py
=============================
12y backtest of Quality + Tactical Entry framework.

Rules:
  Universe: ≥70% A+B history (≥12Q), latest tier A/B, liq ≥5B/day
  Entry: Valuation undervalued (PE_z<-0.5 OR PB_z<-0.5 OR DD>25%) AND TA reversal
         (RSI rebound from <35 OR Close>MA50 with vol>=1.5x)
  Exit:  FA → C/D OR Close < MA200 5+ days OR Trail stop -25% from peak
  Reentry blacklist: 60 days

Sim: 50B init, T+1 open execution, slip 0.1/0.15%, tax 0.1%, liq cap 20% ADV × 5d
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"
INIT_NAV = 50e9

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp = f.name
    try:
        cmd = f'type "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=10000000'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=1800, shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode != 0: raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

# ─── 1. Build quality universe from FA history ───────────────────────────
print("[1] Building quality universe from FA history ...", flush=True)
fa = pd.read_csv("fa_ratings_lh.csv", parse_dates=["time","Release_Date"])
fa = fa.sort_values(["ticker","quarter"]).reset_index(drop=True)

# Per-quarter universe: rolling check ≥70% A+B over last 12Q
# Pre-compute per (ticker, quarter): expanding pct_AB up to that quarter
quality_at_q = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("quarter").reset_index(drop=True)
    for i, row in g.iterrows():
        if i < 12: continue  # need ≥12Q history
        history = g.iloc[:i+1]
        pct_ab = (history["tier"].isin(["A","B"])).sum() / len(history) * 100
        quality_at_q[(tk, row["quarter"])] = {
            "pct_AB": pct_ab,
            "latest_tier": row["tier"],
            "score": row["score"],
            "sub": row["sub"],
            "effective_release": row.get("Release_Date") if pd.notna(row.get("Release_Date")) else row["time"] + pd.Timedelta(days=60),
            "n_q": len(history),
        }
print(f"  Quality lookup built: {len(quality_at_q):,} (ticker, quarter) entries")

# ─── 2. Pull TA + price + volume panel ───────────────────────────────────
print("\n[2] Pulling TA panel from BQ (2014-2026) ...", flush=True)
panel_path = "qt_panel_2014_2026.pkl"
if os.path.exists(panel_path):
    import pickle
    with open(panel_path, "rb") as f:
        panel = pickle.load(f)
    print(f"  Loaded from cache: {len(panel):,} rows")
else:
    panel = bq_query("""
    SELECT t.ticker, t.time, t.Close, t.MA50, t.MA200,
      t.D_RSI, t.D_RSI_T1W, t.D_MACDdiff,
      t.Volume, t.Volume_3M_P50,
      t.PE, t.PE_MA5Y, t.PE_SD5Y, t.PB, t.PB_MA5Y, t.PB_SD5Y,
      t.Open, t.High, t.Low
    FROM tav2_bq.ticker AS t
    WHERE t.time >= '2014-01-01' AND t.Close > 0
      AND t.Volume_3M_P50 * t.Close >= 1e9
    """)
    panel["time"] = pd.to_datetime(panel["time"])
    import pickle
    with open(panel_path, "wb") as f:
        pickle.dump(panel, f)
    print(f"  Saved cache: {len(panel):,} rows")

# Compute additional indicators
print("  Computing rolling 52w high + derived features ...", flush=True)
panel = panel.sort_values(["ticker","time"]).reset_index(drop=True)
panel["hi_52w"] = panel.groupby("ticker")["Close"].transform(
    lambda x: x.rolling(252, min_periods=60).max())
panel["dd_52w_pct"] = (panel["Close"] / panel["hi_52w"] - 1) * 100
panel["pe_z"] = ((panel["PE"] - panel["PE_MA5Y"]) / panel["PE_SD5Y"].replace(0, np.nan)).clip(-10, 10)
panel["pb_z"] = ((panel["PB"] - panel["PB_MA5Y"]) / panel["PB_SD5Y"].replace(0, np.nan)).clip(-10, 10)
panel["vs_MA50_pct"] = (panel["Close"] / panel["MA50"] - 1) * 100
panel["vs_MA200_pct"] = (panel["Close"] / panel["MA200"] - 1) * 100
panel["vol_ratio"] = panel["Volume"] / panel["Volume_3M_P50"]
panel["rsi"] = panel["D_RSI"] * 100
panel["rsi_1w_ago"] = panel["D_RSI_T1W"] * 100
panel["below_ma200_streak"] = panel.groupby("ticker")["Close"].transform(
    lambda x: (x < panel.loc[x.index, "MA200"]).astype(int).groupby(
        (x >= panel.loc[x.index, "MA200"]).astype(int).cumsum()).cumsum())

# Build ticker → date → quarter mapping (assign quarter based on time)
def time_to_quarter(t):
    return f"{t.year}Q{(t.month-1)//3 + 1}"
panel["quarter"] = panel["time"].apply(time_to_quarter)

# Build quarter release lookup: at any date, what's the latest FA quarter available
# Simplest: assume Q1 reports released by mid-May, Q2 by mid-Aug, Q3 by mid-Nov, Q4 by mid-Feb
def latest_fa_quarter_at(dt):
    y = dt.year; m = dt.month; d = dt.day
    if (m, d) >= (5, 15):   return f"{y}Q1"
    elif (m, d) >= (2, 15): return f"{y-1}Q4"
    elif m >= 11 or (m==11 and d >= 15): return f"{y}Q3"
    elif m >= 8 or (m==8 and d >= 15): return f"{y}Q2"
    else: return f"{y-1}Q4"

# More accurate: use last quarter whose effective_release < current date
# Cache release dates per ticker
print("  Building per-ticker FA release schedule ...", flush=True)
fa_release_map = {}
for tk, g in fa.groupby("ticker"):
    g = g.sort_values("time")
    fa_release_map[tk] = g[["time","Release_Date","quarter","tier","score","sub"]].copy()
    fa_release_map[tk]["eff_release"] = fa_release_map[tk]["Release_Date"].fillna(
        fa_release_map[tk]["time"] + pd.Timedelta(days=60))

# Build daily ticker FA lookup
def get_fa_at(ticker, date):
    """Return (tier, score, sub, quarter_used, pct_AB_history) at given date."""
    if ticker not in fa_release_map: return None
    g = fa_release_map[ticker]
    available = g[g["eff_release"] <= date]
    if len(available) == 0: return None
    last = available.iloc[-1]
    q = last["quarter"]
    qinfo = quality_at_q.get((ticker, q))
    if qinfo is None: return None
    return qinfo

print(f"\n[3] Setting up simulator state ...", flush=True)

# Trading days
trading_days = sorted(panel["time"].unique())
# Pivot for fast lookups
px_close = panel.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill()
px_open = panel.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().ffill()
ma50 = panel.pivot_table(index="time", columns="ticker", values="MA50", aggfunc="first").sort_index().ffill()
ma200 = panel.pivot_table(index="time", columns="ticker", values="MA200", aggfunc="first").sort_index().ffill()
rsi = panel.pivot_table(index="time", columns="ticker", values="rsi", aggfunc="first").sort_index().ffill()
rsi_1w_ago = panel.pivot_table(index="time", columns="ticker", values="rsi_1w_ago", aggfunc="first").sort_index().ffill()
pe_z = panel.pivot_table(index="time", columns="ticker", values="pe_z", aggfunc="first").sort_index().ffill()
pb_z = panel.pivot_table(index="time", columns="ticker", values="pb_z", aggfunc="first").sort_index().ffill()
dd_52w = panel.pivot_table(index="time", columns="ticker", values="dd_52w_pct", aggfunc="first").sort_index().ffill()
vs_ma50 = panel.pivot_table(index="time", columns="ticker", values="vs_MA50_pct", aggfunc="first").sort_index().ffill()
vs_ma200 = panel.pivot_table(index="time", columns="ticker", values="vs_MA200_pct", aggfunc="first").sort_index().ffill()
vol_ratio = panel.pivot_table(index="time", columns="ticker", values="vol_ratio", aggfunc="first").sort_index().ffill()
liq = panel.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().ffill()

# ─── 4. Simulator ────────────────────────────────────────────────────────
print("\n[4] Running 12y backtest ...", flush=True)

MAX_POSITIONS = 10
LIQ_CAP_PCT = 0.20
MAX_FILL_DAYS = 5
SLIP_IN = 0.001
SLIP_OUT = 0.0015
TAX_SALE = 0.001
DEPOSIT_RATE = 0.01
TRAIL_PCT = 0.25
TRAIL_ACTIVATION = 0.20
BELOW_MA200_DAYS = 5
BLACKLIST_DAYS = 60

start_dt = pd.Timestamp("2014-04-01")
end_dt = pd.Timestamp("2026-05-13")
sim_days = [d for d in trading_days if start_dt <= d <= end_dt]

# State
cash = INIT_NAV
positions = {}  # ticker -> {entry_dt, entry_px, shares, peak_px, below_ma200_count}
blacklist = {}  # ticker -> blacklist_until_date
nav_history = []
trades = []
daily_cash_rate = (1 + DEPOSIT_RATE) ** (1/365.25) - 1

# Pending orders (signal at T-close → execute T+1 open)
pending_buys = []
pending_sells = []

vni = bq_query("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '2014-01-01' AND t.Close > 100 ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"])
vni_px = vni.set_index("time")["Close"]

print(f"  Sim window: {start_dt.date()} → {end_dt.date()} ({len(sim_days)} trading days)", flush=True)
print(f"  Universe at start ~50-80 quality tickers, growing over time")

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={cash + sum(px_close.at[dt, tk] * pos['shares'] for tk, pos in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))/1e9:.2f}B, positions={len(positions)}", flush=True)
    cash *= (1 + daily_cash_rate)

    # T+1: Execute pending sells first (so cash freed for buys)
    new_pending_sells = []
    for s in pending_sells:
        tk = s["ticker"]
        if tk not in positions: continue
        if tk not in px_open.columns: continue
        fill_px = px_open.at[dt, tk]
        if pd.isna(fill_px) or fill_px <= 0:
            new_pending_sells.append(s); continue
        pos = positions[tk]
        gross = pos["shares"] * fill_px * (1 - SLIP_OUT)
        net = gross * (1 - TAX_SALE)
        cash += net
        trades.append({"dt":dt, "ticker":tk, "side":s["reason"], "shares":pos["shares"],
                       "px":fill_px, "net":net, "entry_dt":pos["entry_dt"], "entry_px":pos["entry_px"],
                       "ret_pct": (fill_px/pos["entry_px"]-1)*100, "hold_days":(dt-pos["entry_dt"]).days})
        blacklist[tk] = dt + pd.Timedelta(days=BLACKLIST_DAYS)
        del positions[tk]
    pending_sells = new_pending_sells

    # T+1: Execute pending buys
    new_pending_buys = []
    for b in pending_buys:
        tk = b["ticker"]
        if tk in positions: continue
        if len(positions) >= MAX_POSITIONS: continue
        if tk in blacklist and blacklist[tk] > dt: continue
        if tk not in px_open.columns: continue
        fill_px = px_open.at[dt, tk]
        if pd.isna(fill_px) or fill_px <= 0:
            new_pending_buys.append(b); continue

        # Liq cap
        adv = liq.at[dt, tk] if tk in liq.columns else 0
        if pd.isna(adv) or adv <= 0: adv = 1e6
        max_pos_vnd = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fill_px

        # Current NAV
        mtm = sum(pos["shares"] * px_close.at[dt, t_] for t_, pos in positions.items()
                  if t_ in px_close.columns and pd.notna(px_close.at[dt, t_]))
        nav_now = cash + mtm
        target = (nav_now / MAX_POSITIONS) * 0.98
        alloc = min(target, max_pos_vnd)
        if alloc < 1e6: continue

        eff_px = fill_px * (1 + SLIP_IN)
        shares = alloc / eff_px
        cost = shares * eff_px
        if cost > cash: continue
        cash -= cost
        positions[tk] = {"entry_dt":dt, "entry_px":fill_px, "shares":shares,
                          "peak_px":fill_px, "below_ma200_count":0}
        trades.append({"dt":dt, "ticker":tk, "side":"BUY", "shares":shares,
                        "px":fill_px, "net":-cost, "entry_dt":dt, "entry_px":fill_px,
                        "ret_pct":0, "hold_days":0})
    pending_buys = []

    # Check exits on current holdings (signal at T-close → execute T+1 open)
    for tk, pos in list(positions.items()):
        if tk not in px_close.columns: continue
        p_today = px_close.at[dt, tk]
        if pd.isna(p_today): continue
        # Update peak
        if p_today > pos["peak_px"]: pos["peak_px"] = p_today

        exit_reason = None
        # Trail stop (after +20% gain achieved)
        if pos["peak_px"] / pos["entry_px"] - 1 >= TRAIL_ACTIVATION:
            if p_today < pos["peak_px"] * (1 - TRAIL_PCT):
                exit_reason = "TRAIL_STOP"

        # Trend break (Close < MA200 for 5+ days)
        if exit_reason is None and tk in ma200.columns:
            m200 = ma200.at[dt, tk]
            if pd.notna(m200):
                if p_today < m200:
                    pos["below_ma200_count"] += 1
                    if pos["below_ma200_count"] >= BELOW_MA200_DAYS:
                        exit_reason = "TREND_BREAK"
                else:
                    pos["below_ma200_count"] = 0

        # FA tier drop (check at any time, not just quarter end)
        if exit_reason is None:
            fa_info = get_fa_at(tk, dt)
            if fa_info is not None and fa_info["latest_tier"] in ("C","D","E"):
                exit_reason = "FA_DROP"

        if exit_reason:
            pending_sells.append({"ticker":tk, "reason":exit_reason})

    # Scan for BUY signals on quality universe (only if have room and not too many pending buys)
    if len(positions) < MAX_POSITIONS and len(pending_buys) < (MAX_POSITIONS - len(positions)):
        # Build today's quality universe efficiently
        for tk in px_close.columns:
            if tk in positions: continue
            if tk in blacklist and blacklist[tk] > dt: continue
            if any(b["ticker"] == tk for b in pending_buys): continue

            fa_info = get_fa_at(tk, dt)
            if fa_info is None: continue
            if fa_info["pct_AB"] < 70: continue
            if fa_info["latest_tier"] not in ("A","B"): continue

            # Liquidity ≥ 5B/day
            adv_vnd = liq.at[dt, tk] if tk in liq.columns else 0
            p = px_close.at[dt, tk]
            if pd.isna(p) or pd.isna(adv_vnd) or adv_vnd * p < 5e9: continue

            # Valuation undervalued (any)
            pez = pe_z.at[dt, tk] if tk in pe_z.columns else np.nan
            pbz = pb_z.at[dt, tk] if tk in pb_z.columns else np.nan
            ddv = dd_52w.at[dt, tk] if tk in dd_52w.columns else np.nan
            v_under = (pez < -0.5) or (pbz < -0.5) or (ddv < -25)
            if not v_under: continue

            # TA reversal
            rsi_now = rsi.at[dt, tk] if tk in rsi.columns else np.nan
            rsi_1w = rsi_1w_ago.at[dt, tk] if tk in rsi_1w_ago.columns else np.nan
            vs50 = vs_ma50.at[dt, tk] if tk in vs_ma50.columns else np.nan
            vs200 = vs_ma200.at[dt, tk] if tk in vs_ma200.columns else np.nan
            volr = vol_ratio.at[dt, tk] if tk in vol_ratio.columns else np.nan

            rsi_rebound = (pd.notna(rsi_1w) and pd.notna(rsi_now) and rsi_1w < 35 and rsi_now > 40)
            ma50_breakout = (pd.notna(vs50) and vs50 > 0 and pd.notna(volr) and volr > 1.5)
            ta_setup = rsi_rebound or ma50_breakout

            # Above MA200 requirement (avoid catching falling knife)
            if not pd.notna(vs200) or vs200 < 0: continue

            if ta_setup and v_under:
                pending_buys.append({"ticker":tk, "signal_dt":dt})
                if len(pending_buys) >= (MAX_POSITIONS - len(positions)):
                    break

    # NAV mark-to-market
    mtm = sum(pos["shares"] * px_close.at[dt, tk] for tk, pos in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt, "nav":nav, "cash":cash, "equity":mtm, "n_pos":len(positions)})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
print(f"\n  Sim complete: {len(trades_df)} trades, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B", flush=True)

# ─── 5. Metrics ──────────────────────────────────────────────────────────
def compute_metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    years = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (s.iloc[-1]/s.iloc[0]) ** (1/years) - 1
    rets = s.pct_change().dropna()
    spy = len(rets)/years
    sharpe = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else 0
    dd = (s - s.cummax()) / s.cummax()
    mdd = dd.min()
    calmar = cagr / abs(mdd) if mdd < 0 else 0
    return {"CAGR":cagr*100, "Sharpe":sharpe, "MaxDD":mdd*100, "Calmar":calmar}

vni_aligned = vni_px.reindex(nav_df.index).ffill()

print("\n" + "="*100)
print("  QUALITY + TACTICAL ENTRY — 12y BACKTEST RESULTS (50B canonical)")
print("="*100)

periods = [
    ("FULL_12y",  pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("PRE_2024",  pd.Timestamp("2014-04-01"), pd.Timestamp("2023-12-31")),
    ("OOS_2024+", pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",     pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",   pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]

print(f"\n  {'Period':<14}{'QT CAGR':>10}{'QT Sharpe':>11}{'QT DD':>9}{'QT Calmar':>11}{'VNI CAGR':>10}{'alpha':>10}")
for pname, ps, pe in periods:
    m = compute_metrics(nav_df["nav"], ps, pe)
    vm = compute_metrics(vni_aligned, ps, pe)
    if m is None or vm is None: continue
    alpha = m["CAGR"] - vm["CAGR"]
    print(f"  {pname:<14}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+11.2f}{m['MaxDD']:>+8.2f}%{m['Calmar']:>+11.2f}{vm['CAGR']:>+9.2f}%{alpha:>+9.2f}pp")

# Exit reason breakdown
if len(trades_df) > 0:
    print(f"\n  --- Exit reason breakdown ---")
    exits = trades_df[trades_df["side"] != "BUY"]
    if len(exits) > 0:
        for reason, group in exits.groupby("side"):
            avg_ret = group["ret_pct"].mean()
            med_hold = group["hold_days"].median()
            wr = (group["ret_pct"] > 0).mean() * 100
            print(f"    {reason:<12}: N={len(group):3d}, avg_ret={avg_ret:+6.1f}%, median_hold={med_hold:.0f}d, WR={wr:.1f}%")

    print(f"\n  --- Trade summary ---")
    print(f"  Total trades: {len(trades_df)}")
    print(f"  Buys: {(trades_df['side']=='BUY').sum()}")
    print(f"  Avg hold days: {exits['hold_days'].mean():.0f}d")
    print(f"  Avg return per trade: {exits['ret_pct'].mean():+.2f}%")
    print(f"  Win rate: {(exits['ret_pct']>0).mean()*100:.1f}%")
    print(f"  Best trade: {exits['ret_pct'].max():+.1f}% ({exits.loc[exits['ret_pct'].idxmax(), 'ticker']})")
    print(f"  Worst trade: {exits['ret_pct'].min():+.1f}% ({exits.loc[exits['ret_pct'].idxmin(), 'ticker']})")

    # Top tickers by total pnl
    if "shares" in trades_df.columns:
        buys = trades_df[trades_df["side"]=="BUY"][["ticker","px","shares"]]
        sells = trades_df[trades_df["side"]!="BUY"]
        # Per-ticker stats
        per_tk = exits.groupby("ticker").agg(
            n=("ticker","size"),
            avg_ret=("ret_pct","mean"),
            total_ret=("ret_pct","sum"),
            avg_hold=("hold_days","mean"),
        ).sort_values("total_ret", ascending=False)
        print(f"\n  Top 15 tickers by cumulative return:")
        print(f"  {'Ticker':<7}{'N':>4}{'Avg ret':>10}{'Cum ret':>10}{'Avg hold':>10}")
        for tk, r in per_tk.head(15).iterrows():
            print(f"  {tk:<7}{int(r['n']):>4}{r['avg_ret']:>+9.1f}%{r['total_ret']:>+9.1f}%{r['avg_hold']:>9.0f}d")

# Save
nav_df.to_csv("qt_backtest_nav.csv")
trades_df.to_csv("qt_backtest_trades.csv", index=False)
print("\nSaved: qt_backtest_nav.csv, qt_backtest_trades.csv")
