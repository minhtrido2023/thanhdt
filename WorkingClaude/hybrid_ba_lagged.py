#!/usr/bin/env python3
"""
hybrid_ba_lagged.py — Hybrid BA v11 + LAGGED standalone (honest)
=================================================================
1. Re-run LAGGED CAND_B (post8, max_pos=12, pos_pct=0.08) with HONEST rolling profile
   → save NAV time series
2. Load BA v11 BASELINE NAV from previous run
3. Combine NAVs at multiple weight ratios:
   100/0, 90/10, 80/20, 70/30, 60/40, 50/50, 30/70, 0/100
4. Report CAGR/Sharpe/DD/Calmar per ratio across periods
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
INIT_NAV = 50e9

# ─── 1. Run LAGGED honest CAND_B → save NAV ──────────────────────────────
print("[1] Loading LAGGED data ...")
with open("data/earnings_px.pkl","rb") as f: px = pickle.load(f)
px["time"] = pd.to_datetime(px["time"])
px_close = px.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index()
liq     = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index()
px_open = px_open.reindex(master_idx).ffill(limit=5)
liq     = liq.reindex(master_idx).ffill(limit=5)

ev_classified = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev_classified = ev_classified.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev_classified["prior_n_good"] = 0
ev_classified["prior_avg_post_good"] = np.nan
for tk, g in ev_classified.groupby("ticker"):
    idxs = g.index.tolist()
    pre_n_good = 0; pre_sum_post = 0.0
    for row_idx in idxs:
        row = ev_classified.loc[row_idx]
        ev_classified.at[row_idx, "prior_n_good"] = pre_n_good
        if pre_n_good > 0:
            ev_classified.at[row_idx, "prior_avg_post_good"] = pre_sum_post / pre_n_good
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15:
            pre_n_good += 1
            pre_sum_post += row["post_ret"]

# CAND_B params
POST_RET_MIN = 8; N_GOOD_MIN = 4; NPR_MIN = 0.15
ENTRY_OFFSET = 5; HOLD_DAYS = 25; MAX_POS = 12; POS_PCT = 0.08
SLIP_IN, SLIP_OUT, TAX_SALE = 0.001, 0.0015, 0.001
DEPOSIT_RATE = 0.01; LIQ_CAP_PCT = 0.20; MAX_FILL_DAYS = 5; LIQ_MIN = 2e9

def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt)
    pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])

print("[2] Running LAGGED honest CAND_B sim ...")
ev = ev_classified.copy()
ev = ev[ev["NP_R"] >= NPR_MIN * 100]
ev = ev[ev["prior_n_good"] >= N_GOOD_MIN]
ev = ev[ev["prior_avg_post_good"] >= POST_RET_MIN]

schedule = []
for _, row in ev.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET)
    exit_dt  = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
sched = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched.groupby("entry_dt")
exits_by_day = sched.groupby("exit_dt")
print(f"  Schedule: {len(sched):,} entries")

sw, ew = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-01-16")  # align with BA period
sim_days = [d for d in master_idx if sw <= d <= ew]
cash = INIT_NAV; positions = {}; nav_history = []
daily_rate = (1+DEPOSIT_RATE)**(1/365.25) - 1

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
            gross = pos["shares"]*fpx*(1-SLIP_OUT); net = gross*(1-TAX_SALE); cash += net
            del positions[tk]
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_now = cash + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions: continue
            if len(positions) >= MAX_POS: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx <= 0: continue
            adv = liq.at[dt, tk] if tk in liq.columns else 0
            if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
            target = POS_PCT * nav_now
            cap = LIQ_CAP_PCT * adv * MAX_FILL_DAYS * fpx
            alloc = min(target, cap)
            if alloc < 1e6 or alloc > cash: continue
            eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
            cash -= cost
            positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_history.append({"date":dt,"nav":cash+mtm})

lagged_nav_df = pd.DataFrame(nav_history).set_index("date")
lagged_nav = lagged_nav_df["nav"] / INIT_NAV  # normalize to 1.0
lagged_nav.to_csv("data/lagged_honest_candb_nav.csv")
print(f"  LAGGED CAND_B final: {lagged_nav.iloc[-1]:.3f}x ({(lagged_nav.iloc[-1]-1)*100:+.1f}%)")

# ─── 3. Load BA v11 BASELINE NAV ─────────────────────────────────────────
print("\n[3] Loading BA v11 BASELINE NAV ...")
ba_df = pd.read_csv("data/ba_v11_lagged_factor_nav.csv", index_col=0, parse_dates=True)
ba_nav = ba_df["BASELINE"]
print(f"  BA v11 BASELINE final: {ba_nav.iloc[-1]:.3f}x ({(ba_nav.iloc[-1]-1)*100:+.1f}%)")

# Align
common = ba_nav.index.intersection(lagged_nav.index)
ba_aligned = ba_nav.loc[common]
lag_aligned = lagged_nav.loc[common]
print(f"  Common dates: {len(common)} (from {common.min()} to {common.max()})")

# Renormalize both to start at 1.0 on first common date
ba_norm  = ba_aligned / ba_aligned.iloc[0]
lag_norm = lag_aligned / lag_aligned.iloc[0]

# VNI for comparison
vni = pd.read_csv("data/VNINDEX.csv", parse_dates=["time"])
vni = vni.set_index("time").sort_index()
vni_aligned = vni["Close"].reindex(common).ffill()
vni_norm = vni_aligned / vni_aligned.iloc[0]

# ─── 4. Combine at multiple weights ──────────────────────────────────────
weights = [(1.0, 0.0), (0.9, 0.1), (0.8, 0.2), (0.7, 0.3),
           (0.6, 0.4), (0.5, 0.5), (0.3, 0.7), (0.0, 1.0)]

hybrids = {}
for wb, wl in weights:
    label = f"BA{int(wb*100)}_LAG{int(wl*100)}"
    hybrids[label] = wb * ba_norm + wl * lag_norm

# ─── 5. Metrics ──────────────────────────────────────────────────────────
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
    cal = cagr/abs(mdd) if mdd<0 else 0
    return {"CAGR":cagr*100, "Sharpe":sh, "MaxDD":mdd*100, "Calmar":cal, "wealth":s.iloc[-1]/s.iloc[0]}

periods = [
    ("FULL 2014-26", common.min(), common.max()),
    ("OOS 2024-26", pd.Timestamp("2024-01-01"), common.max()),
    ("Pre-OOS 14-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23", pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022", pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 2026", pd.Timestamp("2025-12-30"), common.max()),
]

print("\n" + "="*125)
print("  Hybrid BA v11 + LAGGED standalone — multiple weight ratios")
print("="*125)
print(f"  {'Period':<18}{'Mix':<14}{'CAGR%':>8}{'Sharpe':>8}{'MaxDD%':>9}{'Calmar':>8}{'Wealth':>8}{'Δ vs 100/0':>12}")
print("  " + "-"*100)
for label, st, en in periods:
    base100 = metrics(hybrids["BA100_LAG0"], st, en)
    vm = metrics(vni_norm, st, en)
    for name, nav in hybrids.items():
        m = metrics(nav, st, en)
        if not m: continue
        delta = m["CAGR"] - base100["CAGR"]
        print(f"  {label:<18}{name:<14}{m['CAGR']:>+7.2f}{m['Sharpe']:>+8.2f}{m['MaxDD']:>+8.2f}{m['Calmar']:>+8.2f}{m['wealth']:>+8.2f}{delta:>+11.2f}")
    if vm:
        print(f"  {label:<18}{'VNI':<14}{vm['CAGR']:>+7.2f}{vm['Sharpe']:>+8.2f}{vm['MaxDD']:>+8.2f}{vm['Calmar']:>+8.2f}{vm['wealth']:>+8.2f}")
    print()

# Save
combo_df = pd.DataFrame(hybrids)
combo_df.to_csv("data/hybrid_ba_lagged_nav.csv")
print("Saved: hybrid_ba_lagged_nav.csv")
