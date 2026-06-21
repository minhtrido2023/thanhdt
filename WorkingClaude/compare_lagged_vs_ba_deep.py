#!/usr/bin/env python3
"""
compare_lagged_vs_ba_deep.py — Deep dive comparison BA v11 vs LAGGED HL_3y

Periods analyzed:
  Q1 2026 (recovery rally): 2025-12-30 → 2026-03-30
  Y2022 (bear):             2022-01-01 → 2022-12-31
  OOS 2024-26 (mixed):      2024-01-01 → 2026-05-13

For each period:
  - NAV path comparison
  - Trades count + WR
  - Correlation of daily returns
  - Diversification ratio (sqrt(N_uncorrelated))
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import pandas as pd, numpy as np

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)

# Load NAVs
ba_nav = pd.read_csv("ba_v11_production_12y_nav.csv", index_col=0, parse_dates=True)
ba_nav.columns = ["BA_v11"]
print(f"BA v11 NAV: {len(ba_nav)} days, {ba_nav.index.min().date()} → {ba_nav.index.max().date()}")
print(f"  Final: {ba_nav['BA_v11'].iloc[-1]:.3f}x  ({(ba_nav['BA_v11'].iloc[-1]-1)*100:+.1f}%)")

# Need LAGGED HL_3y NAV. Let's re-run a quick LAGGED to get NAV time series matching the BA period.
# Actually use the existing lagged_paper_nav as proxy if available — no, that's from 2026-04
# Use the just-completed validation script result. We need to recompute.

# Quick re-build of LAGGED HL_3y NAV for comparison window
import pickle
print("\n[Setup] Building LAGGED HL_3y NAV for comparison ...")
with open("earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

ev = pd.read_csv("earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)

# HL_3y profile + post_min=5 (production)
LN2 = np.log(2); HL = 3.0
ev["pa_HL3"] = np.nan; ev["prior_n_good"] = 0
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]
        cur_date = row["Release_Date"]
        n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))

# Schedule
POST_MIN, N_MIN, NPR_MIN, ENTRY, HOLD, MAX_POS, POS_PCT = 5.0, 4, 0.15, 5, 25, 12, 0.08
e = ev[(ev["NP_R"] >= NPR_MIN*100) & (ev["prior_n_good"] >= N_MIN) & (ev["pa_HL3"] >= POST_MIN)].copy()

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

schedule = []
for _, row in e.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY)
    exit_dt  = offset_date(rdt, ENTRY + HOLD)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt, "release_dt":rdt, "NP_R":row["NP_R"]})
sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched.groupby("entry_dt")
exits_by_day = sched.groupby("exit_dt")

INIT_NAV = 50e9
sw, ew = ba_nav.index.min(), ba_nav.index.max()
sim_days = [d for d in master_idx if sw <= d <= ew]
cash = INIT_NAV; positions = {}; nav_history = []; trades = []
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
DEPOSIT = 0.01; LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
daily_rate = (1+DEPOSIT)**(1/365.25) - 1
for dt in sim_days:
    cash *= (1 + daily_rate)
    if dt in exits_by_day.groups:
        for _, ex_row in exits_by_day.get_group(dt).iterrows():
            tk = ex_row["ticker"]
            if tk not in positions: continue
            pos = positions[tk]
            if pos["exit_dt"] != dt: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx <= 0:
                fpx = px_close.at[dt, tk] if tk in px_close.columns else np.nan
                if pd.isna(fpx) or fpx <= 0: continue
            gross = pos["shares"]*fpx*(1-SLIP_OUT); net = gross*(1-TAX); cash += net
            trades.append({"dt":dt,"ticker":tk,"side":"SELL","ret_pct":(fpx/pos["entry_px"]-1)*100,
                           "entry_dt":pos["entry_dt"]})
            del positions[tk]
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_now = cash + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions or len(positions) >= MAX_POS: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx <= 0: continue
            adv = liq.at[dt, tk] if tk in liq.columns else 0
            if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
            target = POS_PCT * nav_now
            cap = LIQ_CAP * adv * MAX_FILL * fpx
            alloc = min(target, cap)
            if alloc < 1e6 or alloc > cash: continue
            eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
            cash -= cost
            positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
            trades.append({"dt":dt,"ticker":tk,"side":"BUY","ret_pct":0,"entry_dt":dt})
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_history.append({"date":dt,"nav":cash+mtm})

lagged_nav_df = pd.DataFrame(nav_history).set_index("date")
lagged_nav = lagged_nav_df["nav"] / INIT_NAV  # normalize
lagged_trades = pd.DataFrame(trades)
print(f"  LAGGED HL_3y NAV: {lagged_nav.iloc[-1]:.3f}x ({(lagged_nav.iloc[-1]-1)*100:+.1f}%)  | trades: {len(trades)}")

# Align
common = ba_nav.index.intersection(lagged_nav.index)
ba_aligned = ba_nav["BA_v11"].loc[common]
lag_aligned = lagged_nav.loc[common]
# Renormalize to first common date
ba_n = ba_aligned / ba_aligned.iloc[0]
lag_n = lag_aligned / lag_aligned.iloc[0]
print(f"  Common dates: {len(common)}")

# ─── Period analysis ───────────────────────────────────────────────────
def metrics_period(nav, start, end):
    s = nav[(nav.index>=start) & (nav.index<=end)]
    if len(s) < 5: return None
    pct = (s.iloc[-1]/s.iloc[0] - 1) * 100
    yrs = max((s.index[-1]-s.index[0]).days/365.25, 0.01)
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs) - 1
    rets = s.pct_change().dropna()
    sh = rets.mean()/rets.std()*np.sqrt(252) if rets.std()>0 else 0
    dd = (s - s.cummax())/s.cummax()
    return {"pct":pct, "CAGR":cagr*100, "Sharpe":sh, "DD":dd.min()*100}

periods = [
    ("Q1 2026 (rally)",     pd.Timestamp("2025-12-30"), pd.Timestamp("2026-03-30")),
    ("Q2 2026 partial",     pd.Timestamp("2026-04-01"), common.max()),
    ("Y2022 (bear)",        pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Y2021 (bull)",        pd.Timestamp("2021-01-01"), pd.Timestamp("2021-12-31")),
    ("Y2020 (COVID)",       pd.Timestamp("2020-01-01"), pd.Timestamp("2020-12-31")),
    ("Y2018 (mid bear)",    pd.Timestamp("2018-01-01"), pd.Timestamp("2018-12-31")),
    ("OOS 2024-26",         pd.Timestamp("2024-01-01"), common.max()),
    ("FULL aligned",        common.min(), common.max()),
]

print("\n" + "="*100)
print(f"  PERIOD-BY-PERIOD COMPARISON")
print("="*100)
print(f"  {'Period':<20}{'System':<14}{'Return':>10}{'CAGR':>10}{'Sharpe':>10}{'MaxDD':>10}")
print("  " + "-"*74)
for label, st, en in periods:
    ba_m = metrics_period(ba_n, st, en)
    lag_m = metrics_period(lag_n, st, en)
    if ba_m is None or lag_m is None:
        print(f"  {label:<20} (insufficient data)"); continue
    print(f"  {label:<20}{'BA v11':<14}{ba_m['pct']:>+9.2f}%{ba_m['CAGR']:>+9.2f}%{ba_m['Sharpe']:>+10.2f}{ba_m['DD']:>+9.2f}%")
    print(f"  {label:<20}{'LAGGED HL_3y':<14}{lag_m['pct']:>+9.2f}%{lag_m['CAGR']:>+9.2f}%{lag_m['Sharpe']:>+10.2f}{lag_m['DD']:>+9.2f}%")
    delta = lag_m['CAGR'] - ba_m['CAGR']
    print(f"  {label:<20}{'Δ LAGGED-BA':<14}{lag_m['pct']-ba_m['pct']:>+9.2f}%{delta:>+9.2f}%")
    print()

# ─── Correlation analysis ────────────────────────────────────────────────
ba_rets = ba_n.pct_change().dropna()
lag_rets = lag_n.pct_change().dropna()
common_rets = ba_rets.index.intersection(lag_rets.index)
ba_r = ba_rets.loc[common_rets]; lag_r = lag_rets.loc[common_rets]
corr = ba_r.corr(lag_r)
print("="*100)
print(f"  CORRELATION ANALYSIS (daily returns)")
print("="*100)
print(f"  Full period: correlation = {corr:+.3f}")
# By year
for yr in range(2020, 2026):
    ba_yr = ba_r[(ba_r.index.year==yr)]
    lag_yr = lag_r[(lag_r.index.year==yr)]
    if len(ba_yr) < 30 or len(lag_yr) < 30: continue
    c_yr = ba_yr.corr(lag_yr)
    print(f"  Y{yr}: {c_yr:+.3f}")

print(f"\n  Diversification value:")
print(f"  Low correlation (~0.3-0.5) → strategies somewhat independent → diversification benefit")
print(f"  High correlation (>0.7)    → similar bets, less diversification")

# Save
combo = pd.DataFrame({"BA_v11": ba_n, "LAGGED_HL3y": lag_n})
combo.to_csv("compare_lagged_vs_ba_navs.csv")
print("\nSaved: compare_lagged_vs_ba_navs.csv")
