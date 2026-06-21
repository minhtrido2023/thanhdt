#!/usr/bin/env python3
"""
sim_v12_amduong_window.py - BA v12 Am Duong simulation, windowed 2025-06-09 to 2026-05-15

Architecture (per memory spec ba_v12_am_duong_spec.md):
  - 25B BA v11 BAL universe + V6 ETF parking (70% idle in NEUTRAL state)
  - 25B LAGGED HL_3y (earnings post-release drift)
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR)
sys.path.insert(0, WORKDIR)

from simulate_holistic_nav import simulate, bq

with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
SIGNAL_V11_UNIFIED = _extract("SIGNAL_V11_UNIFIED")
VNI_QUERY_UNIFIED  = _extract("VNI_QUERY_UNIFIED")

START_DATE = "2025-06-09"
END_DATE   = "2026-05-15"
TOTAL_NAV  = 50_000_000_000
BOOK_NAV   = TOTAL_NAV / 2

TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
DEPOSIT = 0.01
ETF_STATES = {3: 0.7}

print("="*100)
print(f"  BA v12 'AM DUONG' SIMULATION   window: {START_DATE} -> {END_DATE}")
print(f"  Total NAV = 50B (25B BAL + 25B LAGGED)")
print("="*100)

# 1. Load BA v11 signals + filter to window
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig = pickle.load(f)
sig["time"] = pd.to_datetime(sig["time"])
sw = pd.Timestamp(START_DATE); ew = pd.Timestamp(END_DATE)
sig = sig[(sig["time"] >= sw) & (sig["time"] <= ew)].copy()
print(f"[1] BA v11 signals (windowed): {len(sig):,} rows")

# 2. P3 overheat filter
vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX'
AND t.time BETWEEN DATE '{START_DATE}' AND DATE '{END_DATE}' ORDER BY t.time""")
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
print(f"[2] P3 overheat blocked: {mask.sum():,} signals")

# 3. Common data
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
state_by_date_ff = {}; last_state = None
for d in vni_dates:
    s = state_by_date.get(d)
    if s is not None: last_state = s
    state_by_date_ff[d] = last_state

LIQ_FULL = {"liquidity_volume_pct": 0.20, "max_fill_days": 5,
            "liquidity_lookup": liq_map, "exit_slippage_tiered": True}

# 4. BAL book @ 25B
print(f"\n[4] BAL book @ 25B (BA v11 + V6 ETF parking) ...")
nav_bal, trades_bal = simulate(sig, prices, vni_dates,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8: 4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, state_by_date=state_by_date_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying,
    **LIQ_FULL, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"])
nav_bal_s = nav_bal.set_index("time")["nav"]
print(f"  Closed trades: {len(trades_bal)}   final: {nav_bal_s.iloc[-1]/1e9:.2f}B")

# 5. LAGGED HL_3y @ 25B
print(f"\n[5] LAGGED HL_3y @ 25B ...")
INIT_NAV_LAG = BOOK_NAV
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

# Build prior_avg_post_good_HL3y per release event (uses full history before each release)
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
    # Only keep events whose entry falls within sim window
    if entry_dt < sw or entry_dt > ew: continue
    schedule.append({"ticker":tk, "entry_dt":entry_dt, "exit_dt":exit_dt})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
print(f"  LAGGED entry events in window: {len(sched_lag)}")

entries_by_day = sched_lag.groupby("entry_dt")
exits_by_day = sched_lag.groupby("exit_dt")

sim_days_lag = [d for d in master_idx if sw <= d <= ew]
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
print(f"  LAGGED final @ 25B init: {nav_lag_s.iloc[-1]/1e9:.2f}B  (closed events tracked: {len(sched_lag)})")

# 6. Combine + metrics
print(f"\n[6] Combining BAL@25B + LAGGED@25B = 50B total ...")
common = nav_bal_s.index.intersection(nav_lag_s.index)
nav_combined = nav_bal_s.loc[common] + nav_lag_s.loc[common]
nav_norm = nav_combined / TOTAL_NAV

vni_aligned = vni.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

def metrics(nav):
    sub = nav.dropna()
    if len(sub) < 5: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1] - sub.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (sub.iloc[-1]/sub.iloc[0])**(1/yrs)-1 if yrs > 0 else 0
    sharpe = rets.mean()/rets.std()*np.sqrt(spy) if rets.std() > 0 else 0
    sortino_den = rets[rets<0].std()
    sortino = rets.mean()/sortino_den*np.sqrt(spy) if sortino_den > 0 else 0
    dd_series = (sub - sub.cummax()) / sub.cummax()
    dd = dd_series.min()
    cal = cagr/abs(dd) if dd < 0 else 0
    total_ret = sub.iloc[-1]/sub.iloc[0] - 1
    return dict(cagr=cagr*100, total=total_ret*100, sharpe=sharpe, sortino=sortino,
                mdd=dd*100, calmar=cal, wealth=sub.iloc[-1]/sub.iloc[0])

m_v12 = metrics(nav_norm)
m_vni = metrics(vni_n)
m_bal = metrics(nav_bal_s)
m_lag = metrics(nav_lag_s)

print("\n" + "="*100)
print(f"  RESULTS  |  BA v12 'AM DUONG'  |  {START_DATE} -> {END_DATE}  ({(common[-1]-common[0]).days} cal days)")
print("="*100)
header = f"  {'Variant':<30}{'Total%':>9}{'CAGR%':>9}{'Sharpe':>9}{'Sortino':>9}{'MaxDD%':>10}{'Calmar':>9}{'Wealth':>9}"
print(header); print("  " + "-"*94)
def row(label, m):
    if m is None: print(f"  {label:<30}  n/a"); return
    print(f"  {label:<30}{m['total']:>+8.2f}{m['cagr']:>+8.2f}{m['sharpe']:>+9.2f}{m['sortino']:>+9.2f}{m['mdd']:>+9.2f}{m['calmar']:>+9.2f}{m['wealth']:>+9.2f}")
row("v12 TOTAL (50B init)", m_v12)
row("  BAL leg (25B init)", m_bal)
row("  LAGGED leg (25B init)", m_lag)
row("VNINDEX buy & hold", m_vni)

# Final NAV in VND
print()
print(f"  Final NAV: {nav_combined.iloc[-1]/1e9:.2f}B VND   (initial 50.00B)   wealth = {m_v12['wealth']:.3f}x")
print(f"  BAL leg:    {nav_bal_s.iloc[-1]/1e9:.2f}B VND   (initial 25.00B)")
print(f"  LAGGED leg: {nav_lag_s.iloc[-1]/1e9:.2f}B VND   (initial 25.00B)")
print(f"  vs VNI b&h: {m_vni['total']:+.2f}% total return, alpha = {(m_v12['total']-m_vni['total']):+.2f}pp")
print(f"  BAL closed trades: {len(trades_bal)}   LAGGED entries: {len(sched_lag)}")

# Save
out_df = pd.DataFrame({"BAL_25B": nav_bal_s.loc[common], "LAGGED_25B": nav_lag_s.loc[common],
                      "v12_TOTAL_50B": nav_combined, "VNI_norm": vni_n*TOTAL_NAV})
out_df.to_csv("data/v12_amduong_window_2025_06_09_nav.csv")
print(f"\n  Saved daily NAV -> v12_amduong_window_2025_06_09_nav.csv")
