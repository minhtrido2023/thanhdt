#!/usr/bin/env python3
"""
test_option1_bal_lagged.py — Replace VN30 book by LAGGED HL_3y
================================================================
Architecture:
  - 25B BA v11 BAL universe (no Fin/RE sector cap, full ticker_prune)
  - 25B LAGGED HL_3y (earnings drift)
  - V6 ETF parking on BA leg (70% idle → VN30 in NEUTRAL state 3)

Compare to current production:
  - 25B BA v11 BAL + 25B BA v11 VN30 + V6 ETF on both

Goal: confirm LAGGED replacing VN30 book improves Sharpe while keeping CAGR.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq

# Extract SIGNAL_V11_UNIFIED
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED  = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2014-01-01"; END_DATE = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2  # 25B per book
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01; ETF_STATES = {3: 0.7}
OOS_START = pd.Timestamp("2024-01-01")

print("="*100)
print("  OPTION 1 — BA v11 BAL + LAGGED HL_3y (replace VN30) vs current production")
print("="*100)

# ─── 1. Load BA v11 signals (cache) ──────────────────────────────────────
sig_cache = "data/ba_v11_unified_12y_sig.pkl"
with open(sig_cache, "rb") as f: sig = pickle.load(f)
sig["time"] = pd.to_datetime(sig["time"])
print(f"[1] BA v11 signals loaded: {len(sig):,} rows")

# ─── 2. P3 overheat filter ───────────────────────────────────────────────
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}'
ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
state5 = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY s.time""")
state5["time"] = pd.to_datetime(state5["time"])
vni_full = vni_full.merge(state5, on="time", how="left")
vni_full["state"] = vni_full["state"].ffill()
vni_full["overheat"] = ((vni_full["Close"]/vni_full["MA200"] > 1.30)
                        & ((vni_full["state"] == 5) | (vni_full["D_RSI"] > 0.75)))
overheat_dates = set(vni_full[vni_full["overheat"]]["time"])
mask = sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11)
sig.loc[mask, "play_type"] = "AVOID_overheated"
print(f"[2] P3 blocked: {mask.sum():,} signals")

# ─── 3. Common data ──────────────────────────────────────────────────────
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}

vni = bq(VNI_QUERY_UNIFIED.format(start=START_DATE, end=END_DATE))
vni["time"] = pd.to_datetime(vni["time"])
vni_dates = sorted(vni["time"].unique())
vn30_underlying = dict(zip(vni["time"], vni["Close"]))

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""").set_index("ticker")["s"].to_dict()

state_by_date = dict(zip(state5["time"], state5["state"]))
state_by_date_ff = {}
last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_state = s
    state_by_date_ff[d] = last_state

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# ─── 4. BAL book at 25B with V6 ETF ──────────────────────────────────────
print("\n[4] Running BAL book at 25B with V6 ETF parking ...")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_FULL, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
print(f"  Closed trades: {len(trades_bal)}")
nav_bal_s = nav_bal.set_index("time")["nav"]
print(f"  BAL final at 25B init: {nav_bal_s.iloc[-1]/1e9:.2f}B")

# ─── 5. LAGGED HL_3y at 25B ──────────────────────────────────────────────
print("\n[5] Running LAGGED HL_3y at 25B ...")
INIT_NAV_LAG = BOOK_NAV  # 25B

with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)

with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l   = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)

ev = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)

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
    entry_dt = offset_date(rdt, ENTRY); exit_dt = offset_date(rdt, ENTRY + HOLD)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt")
exits_by_day = sched_lag.groupby("exit_dt")

sw_lag, ew_lag = pd.Timestamp("2014-01-02"), pd.Timestamp("2026-05-15")
sim_days_lag = [d for d in master_idx if sw_lag <= d <= ew_lag]
cash = INIT_NAV_LAG; positions = {}; nav_history_l = []
SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
LIQ_CAP=0.20; MAX_FILL=5; LIQ_MIN=2e9
daily_rate = (1+DEPOSIT)**(1/365.25) - 1
for dt in sim_days_lag:
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
            del positions[tk]
    if dt in entries_by_day.groups:
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_now = cash + mtm
        for _, en_row in entries_by_day.get_group(dt).iterrows():
            tk = en_row["ticker"]
            if tk in positions or len(positions) >= MAX_POS: continue
            fpx = px_open.at[dt, tk] if tk in px_open.columns else np.nan
            if pd.isna(fpx) or fpx <= 0: continue
            adv = liq_l.at[dt, tk] if tk in liq_l.columns else 0
            if pd.isna(adv) or adv*fpx < LIQ_MIN: continue
            target = POS_PCT * nav_now
            cap = LIQ_CAP * adv * MAX_FILL * fpx
            alloc = min(target, cap)
            if alloc < 1e6 or alloc > cash: continue
            eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
            cash -= cost
            positions[tk] = {"entry_dt":dt, "exit_dt":en_row["exit_dt"], "shares":shares, "entry_px":fpx}
    mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
    nav_history_l.append({"time":dt, "nav":cash+mtm})

nav_lag_df = pd.DataFrame(nav_history_l).set_index("time")
nav_lag_s = nav_lag_df["nav"]
print(f"  LAGGED final at 25B init: {nav_lag_s.iloc[-1]/1e9:.2f}B")

# ─── 6. Combine + Metrics ────────────────────────────────────────────────
print("\n[6] Combining BAL@25B + LAGGED@25B → 50B total ...")
common = nav_bal_s.index.intersection(nav_lag_s.index)
nav_combined = nav_bal_s.loc[common] + nav_lag_s.loc[common]
nav_norm = nav_combined / TOTAL_NAV

# Load existing BAL+VN30 production NAV
ba_v11_prod = pd.read_csv("data/ba_v11_production_12y_nav.csv", index_col=0, parse_dates=True).iloc[:,0]
ba_v11_prod = ba_v11_prod.loc[ba_v11_prod.index.intersection(common)]

vni_aligned = vni.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

# Metrics function
def window_metrics(nav, start, end):
    sub = nav[(nav.index >= start) & (nav.index <= end)]
    if len(sub) < 30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1] / sub.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sharpe = rets.mean() / rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    dd = ((sub - sub.cummax()) / sub.cummax()).min()
    cal = cagr / abs(dd) if dd < 0 else 0
    return {"cagr": cagr*100, "sharpe": sharpe, "mdd": dd*100, "calmar": cal, "wealth": sub.iloc[-1]/sub.iloc[0]}

periods = [
    ("FULL 2014-26",  common.min(), common.max()),
    ("OOS 2024-26",   OOS_START, common.max()),
    ("Pre-OOS 14-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",         pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 2026",       pd.Timestamp("2025-12-30"), common.max()),
]

print("\n" + "="*120)
print("  OPTION 1 (BAL+LAGGED+ETF) vs CURRENT PRODUCTION (BAL+VN30+ETF)")
print("="*120)
print(f"  {'Period':<22}{'Variant':<20}{'CAGR%':>9}{'Sharpe':>9}{'MaxDD%':>10}{'Calmar':>9}{'Wealth':>9}")
print("  " + "-"*96)
for label, st, en in periods:
    opt1 = window_metrics(nav_norm, st, en)
    prod = window_metrics(ba_v11_prod, st, en)
    vm = window_metrics(vni_n, st, en)
    if opt1 is None or prod is None: continue
    print(f"  {label:<22}{'CURRENT (BA+VN30)':<20}{prod['cagr']:>+8.2f}{prod['sharpe']:>+9.2f}{prod['mdd']:>+9.2f}{prod['calmar']:>+9.2f}{prod['wealth']:>+9.2f}")
    print(f"  {label:<22}{'OPT1 (BAL+LAGGED)':<20}{opt1['cagr']:>+8.2f}{opt1['sharpe']:>+9.2f}{opt1['mdd']:>+9.2f}{opt1['calmar']:>+9.2f}{opt1['wealth']:>+9.2f}")
    d_cagr = opt1['cagr'] - prod['cagr']
    d_sh = opt1['sharpe'] - prod['sharpe']
    d_dd = opt1['mdd'] - prod['mdd']
    print(f"  {label:<22}{'Δ (Opt1 - Prod)':<20}{d_cagr:>+8.2f}{d_sh:>+9.2f}{d_dd:>+9.2f}")
    if vm:
        print(f"  {label:<22}{'VNI':<20}{vm['cagr']:>+8.2f}{vm['sharpe']:>+9.2f}{vm['mdd']:>+9.2f}{vm['calmar']:>+9.2f}{vm['wealth']:>+9.2f}")
    print()

# Save
out_df = pd.DataFrame({"CURRENT_BA+VN30": ba_v11_prod, "OPT1_BAL+LAGGED": nav_norm.loc[ba_v11_prod.index]})
out_df.to_csv("data/option1_bal_lagged_vs_prod.csv")
print("Saved: option1_bal_lagged_vs_prod.csv")
