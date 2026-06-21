#!/usr/bin/env python3
"""
backtest_lagged_pos.py
======================
Strategy A: Mua T+5 sau ngày release nếu (a) ticker có freq_LAGGED_POS ≥ 12%,
            (b) earnings NP_R ≥ 15%. Hold 25 trading days rồi bán.

Sim: 2010-01 → 2026-05, 50B init, T+1 open, slip 0.1/0.15%, tax 0.1%
"""
import warnings; warnings.filterwarnings("ignore")
import os, subprocess, tempfile, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import pandas as pd, numpy as np

PROJECT = "lithe-record-440915-m9"
BQ = r"bq"
INIT_NAV = 50e9

# ─── Params ──────────────────────────────────────────────────────────────
POST_RET_MIN  = 5.0     # avg_post_good >= 5% (alpha in T+5→T+30 window historically)
N_GOOD_MIN    = 4       # minimum 4 historical good-earnings events
NPR_MIN       = 0.15    # earnings ≥ +15%
ENTRY_OFFSET  = 5
HOLD_DAYS     = 25
MAX_POSITIONS = 8
POS_PCT       = 0.10
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE  = 0.01
LIQ_CAP_PCT   = 0.20
MAX_FILL_DAYS = 5
LIQ_MIN_VND   = 2e9

# ─── 1. Load profiles + events ───────────────────────────────────────────
print("[1] Loading profiles + events ...", flush=True)
prof = pd.read_csv("ticker_reaction_profile.csv", index_col=0)
# Filter on actual alpha-after-release performance, not just frequency
mask = (prof["avg_post_good"] >= POST_RET_MIN) & (prof["n_good"] >= N_GOOD_MIN)
universe = prof[mask].index.tolist()
print(f"  Eligible universe: {len(universe)} tickers (avg_post_good ≥ {POST_RET_MIN}%, n_good ≥ {N_GOOD_MIN})")
print(f"  Top 10 by avg_post_good:")
for tk, r in prof[mask].nlargest(10, "avg_post_good").iterrows():
    print(f"    {tk:<7} N_good={int(r['n_good']):3d}  avg_post_good={r['avg_post_good']:>+6.1f}%  avg_rel_good={r['avg_rel_good']:>+6.1f}%  avg_pre_good={r['avg_pre_good']:>+6.1f}%")

events = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
events = events[events["ticker"].isin(universe)]
events = events[events["NP_R"] >= NPR_MIN * 100]
print(f"  Good-earnings events in universe (NP_R ≥ {NPR_MIN*100:.0f}%): {len(events)}")

# ─── 2. Load price pivot ─────────────────────────────────────────────────
print("\n[2] Loading price cache ...", flush=True)
with open("earnings_px.pkl","rb") as f: px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
px_close = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)
print(f"  Pivot: {len(master_idx)} days × {len(px_close.columns)} tickers")

# We need Open + liquidity proxy. Pull separately
print("\n[3] Pulling Open + Volume_3M_P50 for universe ...")

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

ov_cache = "lagged_pos_ov.pkl"
if os.path.exists(ov_cache):
    with open(ov_cache,"rb") as f: ov = pickle.load(f)
    print(f"  Loaded cache: {len(ov):,} rows")
else:
    tk_list = "','".join(universe)
    ov = bq_query(f"""
    SELECT t.ticker, t.time, t.Open, t.Volume_3M_P50
    FROM tav2_bq.ticker AS t
    WHERE t.ticker IN ('{tk_list}') AND t.time >= '2009-01-01' AND t.Close > 0
    """)
    ov["time"] = pd.to_datetime(ov["time"])
    with open(ov_cache,"wb") as f: pickle.dump(ov, f)
    print(f"  Pulled + cached: {len(ov):,} rows")

px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index()
px_open = px_open.reindex(master_idx).ffill(limit=5)
liq     = liq.reindex(master_idx).ffill(limit=5)

# ─── 4. Build buy schedule ───────────────────────────────────────────────
print("\n[4] Building buy schedule ...")
def offset_date(ref_dt, offset_days):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    target = pos + offset_days
    if target >= len(all_dates) or target < 0: return None
    return pd.Timestamp(all_dates[target])

schedule = []
for _, row in events.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    entry_dt = offset_date(rdt, ENTRY_OFFSET)
    exit_dt  = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt,
                     "release_dt":rdt, "NP_R":row["NP_R"]})
sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
print(f"  Entries scheduled: {len(sched)}")

# Group by entry date for fast lookup
entries_by_day = sched.groupby("entry_dt")
exits_by_day = sched.groupby("exit_dt")

# ─── 5. Simulator ────────────────────────────────────────────────────────
print("\n[5] Running backtest ...")
start_dt = pd.Timestamp("2010-01-01")
end_dt   = pd.Timestamp("2026-05-13")
sim_days = [d for d in master_idx if start_dt <= d <= end_dt]

cash = INIT_NAV
positions = {}   # tk → {entry_dt, exit_dt, shares, entry_px, release_dt}
nav_history, trades = [], []
daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

for i, dt in enumerate(sim_days):
    if i % 500 == 0:
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        print(f"  Day {i}/{len(sim_days)} ({dt.date()}): NAV={(cash+mtm)/1e9:.2f}B pos={len(positions)} cash={cash/1e9:.1f}B", flush=True)
    cash *= (1 + daily_rate)

    # ── EXITS ──
    if dt in exits_by_day.groups:
        for _, ex_row in exits_by_day.get_group(dt).iterrows():
            tk = ex_row["ticker"]
            if tk not in positions: continue
            pos = positions[tk]
            if pos["exit_dt"] != dt: continue
            if tk not in px_open.columns: continue
            fpx = px_open.at[dt, tk]
            if pd.isna(fpx) or fpx <= 0:
                # fall back to Close if Open missing
                fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
            gross = pos["shares"] * fpx * (1 - SLIP_OUT)
            net = gross * (1 - TAX_SALE)
            cash += net
            ret_pct = (fpx / pos["entry_px"] - 1) * 100
            trades.append({"dt":dt,"ticker":tk,"side":"SELL","shares":pos["shares"],
                           "px":fpx,"net":net,"entry_dt":pos["entry_dt"],"entry_px":pos["entry_px"],
                           "ret_pct":ret_pct,"hold_days":(dt-pos["entry_dt"]).days,
                           "release_dt":pos["release_dt"]})
            del positions[tk]

    # ── ENTRIES ──
    if dt in entries_by_day.groups:
        # Compute current NAV for sizing
        mtm = sum(p["shares"] * px_close.at[dt, tk] for tk,p in positions.items()
                  if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_now = cash + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions: continue
            if len(positions) >= MAX_POSITIONS: continue
            if tk not in px_open.columns: continue
            fpx = px_open.at[dt, tk]
            if pd.isna(fpx) or fpx <= 0: continue

            # Liquidity check
            adv = liq.at[dt, tk] if tk in liq.columns else 0
            if pd.isna(adv) or adv * fpx < LIQ_MIN_VND: continue
            cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
            target = POS_PCT * nav_now
            alloc = min(target, cap)
            if alloc < 1e6 or alloc > cash: continue

            eff_px = fpx * (1 + SLIP_IN)
            shares = alloc / eff_px
            cost = shares * eff_px
            cash -= cost

            positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"],
                              "shares":shares, "entry_px":fpx,
                              "release_dt":en_row["release_dt"]}
            trades.append({"dt":dt,"ticker":tk,"side":"BUY","shares":shares,
                           "px":fpx,"net":-cost,"entry_dt":dt,"entry_px":fpx,
                           "ret_pct":0,"hold_days":0,
                           "release_dt":en_row["release_dt"]})

    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items()
              if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav = cash + mtm
    nav_history.append({"date":dt,"nav":nav,"cash":cash,"equity":mtm,"n_pos":len(positions)})

nav_df = pd.DataFrame(nav_history).set_index("date")
trades_df = pd.DataFrame(trades)
print(f"\n  Sim complete: {len(trades_df)} events, final NAV={nav_df['nav'].iloc[-1]/1e9:.2f}B")

# ─── 6. VNI benchmark ────────────────────────────────────────────────────
vni = bq_query("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.time >= '2009-12-01' AND t.Close > 100 ORDER BY t.time""")
vni["time"] = pd.to_datetime(vni["time"])
vni_px = vni.set_index("time")["Close"]
vni_aligned = vni_px.reindex(nav_df.index).ffill()

def metrics(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)]
    if len(s) < 30: return None
    yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
    rets = s.pct_change().dropna()
    spy = len(rets)/yrs
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = (s - s.cummax())/s.cummax()
    mdd = dd.min()
    calmar = cagr/abs(mdd) if mdd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"MaxDD":mdd*100,"Calmar":calmar}

periods = [
    ("FULL_2010-2026", pd.Timestamp("2010-01-01"), pd.Timestamp("2026-05-13")),
    ("FULL_12y_match", pd.Timestamp("2014-04-01"), pd.Timestamp("2026-05-13")),
    ("OOS_2024+",      pd.Timestamp("2024-01-01"), pd.Timestamp("2026-05-13")),
    ("Y2022",          pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1_2026",        pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
]
print("\n" + "="*100)
print(f"  {'Period':<18}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}{'Calmar':>10}{'VNI':>10}{'alpha':>10}")
for nm, ps, pe in periods:
    m = metrics(nav_df["nav"], ps, pe); vm = metrics(vni_aligned, ps, pe)
    if m is None or vm is None: continue
    a = m["CAGR"] - vm["CAGR"]
    print(f"  {nm:<18}{m['CAGR']:>+9.2f}%{m['Sharpe']:>+10.2f}{m['MaxDD']:>+9.2f}%{m['Calmar']:>+10.2f}{vm['CAGR']:>+9.2f}%{a:>+9.2f}pp")

# ─── 7. Trade analysis ───────────────────────────────────────────────────
sells = trades_df[trades_df["side"]=="SELL"]
print(f"\n  --- Trade summary ---")
print(f"  Total trades: {len(trades_df)} (buys={len(trades_df)-len(sells)}, sells={len(sells)})")
if len(sells) > 0:
    print(f"  Win rate: {(sells['ret_pct']>0).mean()*100:.1f}%")
    print(f"  Avg return: {sells['ret_pct'].mean():+.2f}%")
    print(f"  Median: {sells['ret_pct'].median():+.2f}% | std {sells['ret_pct'].std():.2f}%")
    print(f"  Best: {sells['ret_pct'].max():+.1f}% ({sells.loc[sells['ret_pct'].idxmax(),'ticker']})")
    print(f"  Worst: {sells['ret_pct'].min():+.1f}% ({sells.loc[sells['ret_pct'].idxmin(),'ticker']})")
    print(f"  Avg hold: {sells['hold_days'].mean():.0f}d")

    print(f"\n  Top 15 tickers by cum return:")
    per_tk = sells.groupby("ticker").agg(n=("ticker","size"), avg=("ret_pct","mean"),
                                          total=("ret_pct","sum"))
    per_tk = per_tk.sort_values("total", ascending=False)
    for tk, r in per_tk.head(15).iterrows():
        print(f"    {tk:<7} N={int(r['n']):2d}  avg={r['avg']:+6.1f}%  cum={r['total']:+7.1f}%")

    print(f"\n  Yearly performance:")
    sells["year"] = pd.to_datetime(sells["dt"]).dt.year
    yr = sells.groupby("year").agg(n=("ret_pct","size"), wr=("ret_pct", lambda x: (x>0).mean()*100),
                                    avg=("ret_pct","mean"), total=("ret_pct","sum"))
    for y, r in yr.iterrows():
        print(f"    {y}: N={int(r['n']):3d}  WR={r['wr']:>5.1f}%  avg={r['avg']:+6.2f}%  cum={r['total']:+7.1f}%")

nav_df.to_csv("lagged_pos_nav.csv")
trades_df.to_csv("lagged_pos_trades.csv", index=False)
print("\nSaved: lagged_pos_nav.csv, lagged_pos_trades.csv")
