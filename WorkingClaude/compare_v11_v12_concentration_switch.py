#!/usr/bin/env python3
"""compare_v11_v12_concentration_switch.py — V11/V12 dynamic switcher driven by market concentration.

Hypothesis (user 2026-05-22): "winner-takes-all" markets favor V11 (BAL+VN30),
broad-rally markets favor V12 (BAL+LAGGED). Test 3 concentration metrics with
binary above/below expanding-median rule and realistic switching costs.

Strategy: BAL leg (25B) is shared. Second 25B leg toggles between VN30 and LAGGED
based on previous-day concentration signal. Round-trip switching cost = 0.5% on
the second leg (sell + buy with slippage + tax).

Metrics tested:
  M1 = VNI − Equal-Weight VNI return divergence (6M rolling)
  M2 = Breadth %>MA50 (INVERTED — low breadth = concentrated)
  M3 = Top10 cap-weight 6M return − all-ticker median 6M return

Rule: signal_t = 1 (V11/VN30) if metric_t > expanding_median (252+ days), else 0 (V12/LAGGED).
Apply T+1 execution: act on signal at t-1.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq

# ─────── Load leg NAVs from previous run ──────────────────────────────────────
print("="*100); print("  V11/V12 CONCENTRATION SWITCHER — 3 metrics, binary swap, v3.4b state"); print("="*100)
print("\n[1] Loading cached leg NAVs from compare_v11_v12_v121_v34b run...")
combo = pd.read_csv("data/compare_v11_v12_v121_v34b.csv", index_col=0, parse_dates=True)
# nav_v11 = BAL + VN30 ; nav_v12 = BAL + LAGGED
# To recover legs, we need raw NAVs. Re-run quick component recovery from sim.
# Trick: each leg starts at BOOK_NAV=25B; their sum/2 = portfolio. We don't
# have individual leg series saved. Re-run the script's legs by re-importing.
#
# Actually simpler: synthesize from observation. We have nav_v11 and nav_v12
# normalized to 1.0 at start. Both share BAL leg. Define:
#   bal_share[t] = 0.5 * (nav_v11[t] + nav_v12[t]) - 0.5 * (nav_v11[t] - nav_v12[t]) doesn't decompose.
#
# Best path: re-run the 3 legs (BAL, VN30, LAGGED) and save them individually.
# Implementing inline to keep one source of truth.

import re
from simulate_holistic_nav import simulate

with open("data/ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")

START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10; ETF_STATES = {3: 0.7}   # cost model per user 2026-05-23
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
STATE_CSV = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

state_df = pd.read_csv(STATE_CSV); state_df["time"] = pd.to_datetime(state_df["time"])
state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]
sbd = dict(zip(state_df["time"], state_df["state"]))
sbd_ff = {}; last = None
for d in vni_dates_B:
    s = sbd.get(d)
    if s is not None: last = s
    sbd_ff[d] = last
v = vni_full.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
overheat_dates = set(v[v["overheat"]]["time"])
sig_v = sig_B.copy()
sig_v.loc[sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

print("[2] Running 3 legs (BAL / VN30 / LAGGED)...")
nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name="BAL")
nav_bal["time"] = pd.to_datetime(nav_bal["time"]); nav_bal_s = nav_bal.set_index("time")["nav"]
print(f"  BAL: {nav_bal_s.iloc[-1]/1e9:.2f}B")

sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
LIQ30 = {**LIQ, "liquidity_lookup":liq30}
nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
    allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
    min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
    ticker_sector_map=sec_map,
    deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
    cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ30, name="VN30")
nav_vn30["time"] = pd.to_datetime(nav_vn30["time"]); nav_vn30_s = nav_vn30.set_index("time")["nav"]
print(f"  VN30: {nav_vn30_s.iloc[-1]/1e9:.2f}B")

# LAGGED book
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns"); px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f); ov["time"] = pd.to_datetime(ov["time"])
px_open = ov.pivot_table(index="time", columns="ticker", values="Open", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
liq_l = ov.pivot_table(index="time", columns="ticker", values="Volume_3M_P50", aggfunc="first").sort_index().reindex(master_idx).ffill(limit=5)
with open("data/earnings_surprise_data.pkl","rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv("data/earnings_events_classified.csv", parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
                     on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    good_history = []
    for row_idx in g.index.tolist():
        row = ev.loc[row_idx]; cur_date = row["Release_Date"]; n_good = len(good_history)
        ev.at[row_idx, "prior_n_good"] = n_good
        if n_good >= 1:
            dates_arr = pd.to_datetime([d for d,_ in good_history])
            posts_arr = np.array([p for _,p in good_history])
            age_yrs = (cur_date - dates_arr).days.values / 365.25
            w = np.exp(-LN2 * age_yrs / HL)
            ev.at[row_idx, "pa_HL3"] = (posts_arr * w).sum() / w.sum() if w.sum() > 0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            good_history.append((cur_date, row["post_ret"]))
e_hl3 = ev[(ev["NP_R"] >= 15) & (ev["prior_n_good"] >= 4) & (ev["pa_HL3"] >= 5)].copy()
def offset_date(ref_dt, offset):
    ref = np.datetime64(ref_dt); pos = np.searchsorted(all_dates, ref, side="right") - 1
    if pos < 0: return None
    tgt = pos + offset
    if tgt >= len(all_dates) or tgt < 0: return None
    return pd.Timestamp(all_dates[tgt])
ENTRY_OFFSET, HOLD_DAYS, MAX_POS, LIQ_MIN = 5, 25, 12, 2e9
schedule = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]; rdt = row["Release_Date"]
    if tk not in px_open.columns: continue
    entry_dt = offset_date(rdt, ENTRY_OFFSET); exit_dt = offset_date(rdt, ENTRY_OFFSET + HOLD_DAYS)
    if entry_dt is None or exit_dt is None: continue
    schedule.append({"ticker":tk,"entry_dt":entry_dt,"exit_dt":exit_dt,"surprise":row["surprise_B_MA"]})
sched_lag = pd.DataFrame(schedule).sort_values("entry_dt").reset_index(drop=True)
entries_by_day = sched_lag.groupby("entry_dt"); exits_by_day = sched_lag.groupby("exit_dt")

def run_lagged(init_nav, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    sim_days = [d for d in master_idx if sw <= d <= ew]
    cash = init_nav; positions = {}; nav_history = []
    SLIP_IN, SLIP_OUT, TAX = 0.001, 0.0015, 0.001
    LIQ_CAP, MAX_FILL = 0.20, 5
    # cost model: deposit=0%, no daily cash accrual. LAGGED is no-margin.
    for dt in sim_days:
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
                gross = pos["shares"]*fpx*(1-SLIP_OUT); cash += gross*(1-TAX); del positions[tk]
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
                pos_pct = 0.08
                target = pos_pct * nav_now; cap = LIQ_CAP * adv * MAX_FILL * fpx
                alloc = min(target, cap)
                if alloc < 1e6 or alloc > cash: continue
                eff_px = fpx*(1+SLIP_IN); shares = alloc/eff_px; cost = shares*eff_px
                cash -= cost
                positions[tk] = {"entry_dt":dt,"exit_dt":en_row["exit_dt"],"shares":shares,"entry_px":fpx}
        mtm = sum(p["shares"]*px_close.at[dt, tk] for tk,p in positions.items() if tk in px_close.columns and pd.notna(px_close.at[dt, tk]))
        nav_history.append({"time":dt,"nav":cash+mtm})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

print("  LAGGED (v12 fixed-8%): running...")
nav_lag = run_lagged(BOOK_NAV); print(f"  LAGGED: {nav_lag.iloc[-1]/1e9:.2f}B")

# ─────── 3. Compute concentration metrics ────────────────────────────────────
print("\n[3] Computing concentration metrics...")

# M1: VNI − Equal-Weight return divergence (6M rolling). Use ticker_prune universe EW.
ew_q = """WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
)
SELECT time, AVG(ret_6m) AS ew_ret_6m FROM base GROUP BY time ORDER BY time"""
ew_df = bq(ew_q.format(END_B)); ew_df["time"] = pd.to_datetime(ew_df["time"])
vni_with = vni_full[["time","Close"]].copy()
vni_with["vni_ret_6m"] = vni_with["Close"].pct_change(126)
m1 = vni_with.merge(ew_df, on="time", how="inner")
m1["M1"] = m1["vni_ret_6m"] - m1["ew_ret_6m"]
m1 = m1.set_index("time")["M1"]
print(f"  M1 (VNI vs EW 6M): {m1.dropna().min():.3f} to {m1.dropna().max():.3f}")

# M2: Breadth %>MA50 (INVERTED — high = low breadth = concentrated)
br_q = """SELECT t.time,
  COUNTIF(t.Close > t.MA50)/NULLIF(COUNT(*),0) AS breadth_ma50
FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Close IS NOT NULL AND t.MA50 IS NOT NULL
GROUP BY t.time ORDER BY t.time"""
br_df = bq(br_q.format(END_B)); br_df["time"] = pd.to_datetime(br_df["time"])
br_df["M2"] = -br_df["breadth_ma50"]  # negate so high = concentrated
m2 = br_df.set_index("time")["M2"]
print(f"  M2 (-Breadth %>MA50): {m2.dropna().min():.3f} to {m2.dropna().max():.3f}")

# M3: Top10 cap return − all-prune median 6M return
top10 = bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 10""")["ticker"].tolist()
top10_str = "','".join(top10)
m3_q = f"""WITH base AS (
  SELECT t.time, t.ticker,
    SAFE_DIVIDE(t.Close, LAG(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret_6m,
    CASE WHEN t.ticker IN ('{top10_str}') THEN 1 ELSE 0 END AS is_top10
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '2013-01-01' AND DATE '{END_B}'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
)
SELECT time, AVG(IF(is_top10=1, ret_6m, NULL)) AS top10_ret, AVG(ret_6m) AS all_ret
FROM base GROUP BY time ORDER BY time"""
m3_df = bq(m3_q); m3_df["time"] = pd.to_datetime(m3_df["time"])
m3_df["M3"] = m3_df["top10_ret"] - m3_df["all_ret"]
m3 = m3_df.set_index("time")["M3"]
print(f"  M3 (Top10 − all 6M): {m3.dropna().min():.3f} to {m3.dropna().max():.3f}")

# ─────── 4. Build signals: expanding-median binary rule (T+1 execution) ──────
def make_signal(metric, min_history=252):
    """Return Series with 1=V11(VN30) / 0=V12(LAGGED), shifted +1 for T+1 exec."""
    s = metric.dropna().sort_index()
    expanding_med = s.expanding(min_periods=min_history).median()
    raw_signal = (s > expanding_med).astype(int)
    # warmup before min_history: default to 1 (V11) to match V11 baseline mode
    raw_signal = raw_signal.reindex(metric.index).ffill().fillna(1).astype(int)
    return raw_signal.shift(1).fillna(1).astype(int)

sig_m1 = make_signal(m1); sig_m2 = make_signal(m2); sig_m3 = make_signal(m3)

# ─────── 5. Build switched NAV ───────────────────────────────────────────────
# Strategy: BAL leg always on; second 25B leg = VN30 if signal==1 else LAGGED.
# Each leg has its own daily return. Track 2nd leg capital pool; switch cost
# = 0.5% on its value when signal flips (round-trip slippage + tax + spread).

def switched_nav(bal_ret, vn30_ret, lag_ret, signal, switch_cost=0.005):
    common = bal_ret.index.intersection(vn30_ret.index).intersection(lag_ret.index).intersection(signal.index)
    bal_ret = bal_ret.loc[common]; vn30_ret = vn30_ret.loc[common]; lag_ret = lag_ret.loc[common]
    signal = signal.loc[common]
    # Track NAV components
    nav_bal_path = (1+bal_ret).cumprod() * BOOK_NAV
    second = np.full(len(common), BOOK_NAV, dtype=float)
    prev_sig = signal.iloc[0]
    second[0] = BOOK_NAV  # day 0
    flips = 0
    for i in range(1, len(common)):
        cur_sig = signal.iloc[i]
        if cur_sig != prev_sig:
            second[i] = second[i-1] * (1 - switch_cost)
            flips += 1
        else:
            second[i] = second[i-1]
        # apply today's return based on cur_sig
        r = vn30_ret.iloc[i] if cur_sig==1 else lag_ret.iloc[i]
        second[i] = second[i] * (1 + r)
        prev_sig = cur_sig
    total = nav_bal_path.values + second
    return pd.Series(total / TOTAL_NAV, index=common), flips

# Daily returns from leg NAVs (already at 25B init)
common_idx = nav_bal_s.index.intersection(nav_vn30_s.index).intersection(nav_lag.index)
bal_ret  = nav_bal_s.loc[common_idx].pct_change().fillna(0)
vn30_ret = nav_vn30_s.loc[common_idx].pct_change().fillna(0)
lag_ret  = nav_lag.loc[common_idx].pct_change().fillna(0)

# Static baselines (apples-to-apples within common_idx)
nav_v11_static = (nav_bal_s.loc[common_idx] + nav_vn30_s.loc[common_idx]) / TOTAL_NAV
nav_v12_static = (nav_bal_s.loc[common_idx] + nav_lag.loc[common_idx])    / TOTAL_NAV
vni_aligned = vni_B.set_index("time")["Close"].reindex(common_idx).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

# Switched variants
print("\n[4] Building switched NAVs...")
nav_m1, flips_m1 = switched_nav(bal_ret, vn30_ret, lag_ret, sig_m1.reindex(common_idx).ffill().fillna(1).astype(int))
nav_m2, flips_m2 = switched_nav(bal_ret, vn30_ret, lag_ret, sig_m2.reindex(common_idx).ffill().fillna(1).astype(int))
nav_m3, flips_m3 = switched_nav(bal_ret, vn30_ret, lag_ret, sig_m3.reindex(common_idx).ffill().fillna(1).astype(int))
print(f"  M1 flips: {flips_m1}  |  M2 flips: {flips_m2}  |  M3 flips: {flips_m3}")

# ─────── 6. Metrics ──────────────────────────────────────────────────────────
def metrics(nav, start, end):
    s = nav[(nav.index >= start) & (nav.index <= end)]
    if len(s) < 30: return None
    rets = s.pct_change().dropna()
    yrs = (s.index[-1] - s.index[0]).days / 365.25
    spy = len(rets) / yrs if yrs > 0 else 252
    cagr = (s.iloc[-1] / s.iloc[0]) ** (1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((s - s.cummax())/s.cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    return {"CAGR":cagr*100,"Sharpe":sh,"DD":dd*100,"Calmar":cal,"wealth":s.iloc[-1]/s.iloc[0],"ret":(s.iloc[-1]/s.iloc[0]-1)*100}

periods = [
    ("FULL 2014-26",     common_idx.min(), common_idx.max()),
    ("OOS 2024-26 ⭐",    pd.Timestamp("2024-01-01"), common_idx.max()),
    ("Pre-OOS 14-19",    pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 2018-23",      pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2024",            pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")),
    ("Y2025",            pd.Timestamp("2025-01-01"), pd.Timestamp("2025-12-31")),
    ("Q1 2026 + May",    pd.Timestamp("2025-12-30"), common_idx.max()),
]

print("\n" + "="*110)
print("  RESULTS — concentration-switched portfolios vs static baselines (v3.4b state)")
print("="*110)
variants = [
    ("V11 static (BAL+VN30)",   nav_v11_static),
    ("V12 static (BAL+LAGGED)", nav_v12_static),
    ("SWITCH M1 (VNI-EW 6M)",   nav_m1),
    ("SWITCH M2 (-Breadth)",    nav_m2),
    ("SWITCH M3 (Top10-All)",   nav_m3),
    ("VNI B&H",                 vni_n),
]
for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"  {'System':<28}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
    print(f"  {'-'*28}{'-'*9}{'-'*9}{'-'*9}{'-'*8}{'-'*9}")
    for name, nav in variants:
        m = metrics(nav, st, en)
        if not m: continue
        print(f"  {name:<28}{m['CAGR']:>+8.2f}%{m['Sharpe']:>+9.2f}{m['DD']:>+8.2f}%{m['Calmar']:>+8.2f}{m['wealth']:>+9.2f}")

# Signal regime breakdown — % of days V11-side
print("\n" + "="*110)
print("  SIGNAL REGIME — % of OOS days favoring V11 (VN30 leg)")
print("="*110)
oos_idx = common_idx[(common_idx>=pd.Timestamp("2024-01-01")) & (common_idx<=common_idx.max())]
for name, sigser in [("M1", sig_m1), ("M2", sig_m2), ("M3", sig_m3)]:
    s = sigser.reindex(oos_idx).ffill().fillna(1).astype(int)
    pct_v11 = (s==1).mean()*100
    print(f"  {name}: {pct_v11:.1f}% V11-favored | {100-pct_v11:.1f}% V12-favored")

# Save
out_df = pd.DataFrame({"v11_static":nav_v11_static, "v12_static":nav_v12_static,
                        "switch_m1":nav_m1, "switch_m2":nav_m2, "switch_m3":nav_m3, "vni":vni_n,
                        "sig_m1":sig_m1.reindex(common_idx), "sig_m2":sig_m2.reindex(common_idx), "sig_m3":sig_m3.reindex(common_idx)})
out_df.to_csv("data/compare_v11_v12_concentration_switch.csv")
print(f"\n  Saved: compare_v11_v12_concentration_switch.csv")
print("\n" + "="*110); print("DONE.")
