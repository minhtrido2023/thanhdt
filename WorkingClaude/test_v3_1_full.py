#!/usr/bin/env python3
"""
test_v3_1_full.py — Full validation:
  Phase A: pre-2014 stress test (2007-2013) — Tinh Tế vs v3 vs v3.1
  Phase B: post-2014 V11 backtest (2014-2026) — Tinh Tế vs v3 vs v3.1

Verifies v3.1 fixes 2008 GFC failure without regressing 2014-2026 wins.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, re, bisect, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq, VNI_QUERY

# ──────────────────────────────────────────────────────────────────
# PHASE A: PRE-2014 STRESS TEST (1B init, 2007-2013)
# ──────────────────────────────────────────────────────────────────
START_A = "2007-01-01"; END_A = "2013-12-31"
INIT_NAV_A = 1e9
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
P3_VNI_MA200_THRESHOLD = 1.30; P3_VNI_RSI_THRESHOLD = 0.75

PHASE_A_VARIANTS = [
    ("LIVE Tinh Tế",       "tav2_bq.vnindex_5state"),
    ("v3 staging",         "tav2_bq.vnindex_5state_staging"),
    ("v3.1-clean overlay", "tav2_bq.vnindex_5state_tam_quan_v31_clean"),
]

def make_signal_sql_pre2014(state_table):
    return f"""
WITH fa_union AS (
  SELECT f.ticker, f.time, f.tier FROM tav2_bq.fa_ratings AS f
  UNION ALL SELECT f.ticker, f.time, f.tier FROM tav2_bq.fa_ratings_pre2014 AS f),
fa_dated AS (SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM fa_union AS f),
fin_dated AS (SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
    FROM tav2_bq.ticker_financial AS f),
vni_rsi AS (SELECT t.time, t.D_RSI AS vni_rsi,
    MAX(t.D_RSI) OVER (ORDER BY t.time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS vni_rsi_max3m
    FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.time BETWEEN DATE '{{start}}' AND DATE '{{end}}'),
classified AS (
  SELECT t.ticker, t.time, t.Close,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN vr.vni_rsi_max3m > 0.65 THEN 10 ELSE 0 END
    + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
    + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
    + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
    + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
    + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="D" THEN 10 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier="A" THEN -10 ELSE 0 END) AS ta,
    s5.state AS state5, fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy, fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * t.Close AS liq, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec
  FROM tav2_bq.ticker AS t
  LEFT JOIN {state_table} AS s5 ON s5.time = t.time
  LEFT JOIN fa_dated AS fa ON fa.ticker = t.ticker AND t.time >= fa.f_time AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin ON fin.ticker = t.ticker AND t.time >= fin.fin_time AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  LEFT JOIN vni_rsi AS vr ON vr.time = t.time
  WHERE t.time BETWEEN DATE '{{start}}' AND DATE '{{end}}' AND t.ticker != 'VNINDEX' AND t.MA200 IS NOT NULL)
SELECT ticker, time, Close,
  CASE WHEN state5 IN (1, 2) THEN 'AVOID_bear' WHEN fa_tier = 'E' THEN 'AVOID_faE'
    WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 170 AND state5 IN (4,5) THEN 'S_PRO'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D') THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
    WHEN ta >= 140 AND state5 IN (4,5) THEN 'MOMENTUM_S'
    WHEN ta >= 125 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT' ELSE 'PASS' END AS play_type,
  ta, liq, sec FROM classified WHERE liq >= 1e8
"""

print("="*100); print(f"PHASE A: pre-2014 stress test 2007-2013, 1B init"); print("="*100)

# Shared data
releases = bq(f"""SELECT tf.ticker, tf.Release_Date FROM tav2_bq.ticker_financial AS tf
WHERE tf.Release_Date BETWEEN DATE '2005-01-01' AND DATE '{END_A}'""")
releases["Release_Date"] = pd.to_datetime(releases["Release_Date"])
release_by_ticker = releases.groupby("ticker")["Release_Date"].apply(sorted).to_dict()

vni_full_A = bq(f"""SELECT t.time, t.Close, t.D_RSI, t.MA200 FROM tav2_bq.ticker AS t
              WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '2005-01-01' AND DATE '{END_A}'""")
vni_full_A["time"] = pd.to_datetime(vni_full_A["time"])
vni_full_A = vni_full_A.sort_values("time").reset_index(drop=True)
if vni_full_A["MA200"].isna().all():
    vni_full_A["MA200"] = vni_full_A["Close"].rolling(200, min_periods=200).mean()
vni_full_A["ratio"] = vni_full_A["Close"] / vni_full_A["MA200"]
vni_ratio_today_A = dict(zip(vni_full_A["time"], vni_full_A["ratio"]))
vni_rsi_today_A = dict(zip(vni_full_A["time"], vni_full_A["D_RSI"]))

vni_dates_A = sorted(bq(VNI_QUERY.format(start=START_A, end=END_A))["time"].apply(pd.to_datetime).unique())
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
            """).set_index("ticker")["s"].to_dict()

def run_phaseA(name, state_table):
    print("\n" + "="*100); print(f"  PHASE A — {name}"); print("="*100)
    SIGNAL = make_signal_sql_pre2014(state_table)
    sig = bq(SIGNAL.format(start="2006-01-01", end=END_A))
    sig["time"] = pd.to_datetime(sig["time"])
    ds = np.empty(len(sig))
    ticker_arr = sig["ticker"].values; time_arr = sig["time"].values
    for i in range(len(sig)):
        arr = release_by_ticker.get(ticker_arr[i])
        if not arr: ds[i] = np.nan; continue
        idx = bisect.bisect_right(arr, pd.Timestamp(time_arr[i]))
        if idx == 0: ds[i] = np.nan; continue
        ds[i] = (pd.Timestamp(time_arr[i]) - arr[idx-1]).days
    sig["days_since_release"] = ds

    state_df = bq(f"""SELECT s.time, s.state FROM {state_table} AS s
                  WHERE s.time BETWEEN DATE '2006-01-01' AND DATE '{END_A}' ORDER BY s.time""")
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_by_date = dict(zip(state_df["time"], state_df["state"]))

    s = sig.copy()
    s["state"] = s["time"].map(state_by_date)
    s["vni_ratio"] = s["time"].map(vni_ratio_today_A); s["vni_rsi"] = s["time"].map(vni_rsi_today_A)
    keep = s["state"].isin([4, 5])
    has_rel = s["days_since_release"].notna()
    keep |= (s["state"] == 1) & has_rel & (s["days_since_release"] <= 30)
    keep |= (s["state"].isin([2, 3])) & has_rel & (s["days_since_release"] <= 60)
    s = s[keep].copy()
    overheat = (s["vni_ratio"] > P3_VNI_MA200_THRESHOLD).fillna(False)
    regime = ((s["state"] == 5) | (s["vni_rsi"] > P3_VNI_RSI_THRESHOLD)).fillna(False)
    block = overheat & regime & s["play_type"].isin(BUY_TIERS)
    s.loc[block, "play_type"] = "AVOID_overheated"
    prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig.groupby("ticker")}
    liq_map = {(r["ticker"], r["time"]): r["liq"] for _, r in sig.iterrows()}
    nav, trades = simulate(s, prices, vni_dates_A,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=INIT_NAV_A,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        state_by_date={pd.Timestamp(k): int(v) for k,v in state_by_date.items()},
        liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liq_map,
        exit_slippage_tiered=True)
    nav["time"] = pd.to_datetime(nav["time"])
    trades["entry_date"] = pd.to_datetime(trades["entry_date"])
    trades = trades[trades["entry_date"] >= pd.Timestamp(START_A)].copy()
    return nav, trades

resA = {}
for name, st in PHASE_A_VARIANTS:
    resA[name] = run_phaseA(name, st)

def metricsA(nav_df, trades_df):
    nav_w = nav_df[(nav_df["time"]>=pd.Timestamp(START_A)) & (nav_df["time"]<=pd.Timestamp(END_A))]
    if len(nav_w)<2: return None
    final = nav_w["nav"].iloc[-1]
    yrs = (nav_w["time"].iloc[-1] - nav_w["time"].iloc[0]).days / 365.25
    cagr = (final/INIT_NAV_A)**(1/yrs)-1
    rets = nav_w["nav"].pct_change().dropna()
    sharpe = rets.mean()/rets.std()*np.sqrt(252) if rets.std()>0 else 0
    dd = ((nav_w["nav"]-nav_w["nav"].cummax())/nav_w["nav"].cummax()).min()
    return {"final":final,"cagr":cagr*100,"sharpe":sharpe,"dd":dd*100,
            "calmar":(cagr*100)/abs(dd*100) if dd!=0 else 0,"ntr":len(trades_df)}

print("\n\n" + "="*100); print(f"  PHASE A RESULTS  (2007-2013, init 1B)"); print("="*100)
print(f"\n  {'Variant':<22}{'Final':>9}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>10}{'Calmar':>9}{'Trades':>9}")
print("  " + "-"*78)
for name, _ in PHASE_A_VARIANTS:
    nav, tr = resA[name]
    m = metricsA(nav, tr)
    if not m: continue
    print(f"  {name:<22}{m['final']/1e9:>8.3f}B{m['cagr']:>+8.2f}%{m['sharpe']:>+9.2f}{m['dd']:>+9.2f}%{m['calmar']:>+8.2f}{m['ntr']:>9d}")

# Year by year
print(f"\n  Year-by-year (relative to LIVE Tinh Tế):")
nav_l = resA["LIVE Tinh Tế"][0]
print(f"  {'Year':<6}{'Tinh Tế%':>10}{'v3%':>10}{'v3.1%':>10}{'v3.1 vs LIVE':>15}")
for yr in range(2007, 2014):
    yoys = {}
    for vn in [n for n,_ in PHASE_A_VARIANTS]:
        nv = resA[vn][0]
        s = nv[(nv["time"]>=f"{yr}-01-01") & (nv["time"]<=f"{yr}-12-31")]
        if len(s)<2: yoys[vn]=None; continue
        yoys[vn] = (s["nav"].iloc[-1]/s["nav"].iloc[0]-1)*100
    if any(v is None for v in yoys.values()): continue
    delta = yoys["v3.1-clean overlay"] - yoys["LIVE Tinh Tế"]
    print(f"  {yr:<6}{yoys['LIVE Tinh Tế']:>+9.1f}%{yoys['v3 staging']:>+9.1f}%{yoys['v3.1-clean overlay']:>+9.1f}%{delta:>+13.1f}pp")

# ──────────────────────────────────────────────────────────────────
# PHASE B: POST-2014 V11 (50B init, 2014-2026)
# ──────────────────────────────────────────────────────────────────
START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV_B  = 50_000_000_000; BOOK_NAV_B = TOTAL_NAV_B / 2
DEPOSIT = 0.01; ETF_STATES = {3: 0.7}; OOS_START = pd.Timestamp("2024-01-01")
TIER_BAL_B = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_B = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

PHASE_B_VARIANTS = [
    ("LIVE Tinh Tế",       "BQ"),
    ("v3 staging",         "vnindex_5state_dual_v3_staging.csv"),
    ("v3.1-clean overlay", "BQ:tav2_bq.vnindex_5state_tam_quan_v31_clean"),
]

print("\n\n" + "="*100); print(f"PHASE B: post-2014 V11 backtest 2014-2026, 50B init"); print("="*100)

with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _content = f.read()
def _extract(varname):
    m = re.search(rf'^{varname}\s*=\s*"""(.+?)"""', _content, re.MULTILINE | re.DOTALL)
    return m.group(1) if m else None
VNI_QUERY_UNIFIED = _extract("VNI_QUERY_UNIFIED")
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))
vni_full_B = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full_B["time"] = pd.to_datetime(vni_full_B["time"])
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])

def run_phaseB(name, source):
    print("\n" + "="*100); print(f"  PHASE B — {name}"); print("="*100)
    if source == "BQ":
        state_df = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
        state_df["time"] = pd.to_datetime(state_df["time"])
    elif source.startswith("BQ:"):
        tbl = source.split(":")[1]
        state_df = bq(f"""SELECT s.time, s.state FROM {tbl} AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
        state_df["time"] = pd.to_datetime(state_df["time"])
    else:
        state_df = pd.read_csv(os.path.join(WORKDIR, source))
        state_df["time"] = pd.to_datetime(state_df["time"])
        state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]
    state_by_date = dict(zip(state_df["time"], state_df["state"]))
    sbd_ff = {}; last = None
    for d in vni_dates_B:
        s = state_by_date.get(d)
        if s is not None: last = s
        sbd_ff[d] = last
    v = vni_full_B.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    od = set(v[v["overheat"]]["time"])
    sig_v = sig_B.copy()
    sig_v.loc[sig_v["time"].isin(od) & sig_v["play_type"].isin(BUY_TIERS_B), "play_type"] = "AVOID_overheated"
    LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}
    nav_bal, tr_bal = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL_B, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV_B,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=sbd_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name="BAL")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])
    sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav_vn30, tr_vn30 = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL_B, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV_B,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=sbd_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ30, name="VN30")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
    common = nav_bal.set_index("time")["nav"].index.intersection(nav_vn30.set_index("time")["nav"].index)
    nav_total = nav_bal.set_index("time")["nav"].loc[common] + nav_vn30.set_index("time")["nav"].loc[common]
    nav_norm = nav_total/TOTAL_NAV_B
    return nav_norm

navsB = {}
for name, src in PHASE_B_VARIANTS:
    navsB[name] = run_phaseB(name, src)

def metricsB(nav, start, end):
    sub = nav[(nav.index>=start) & (nav.index<=end)]
    if len(sub)<30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1]-sub.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (sub.iloc[-1]/sub.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sharpe = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((sub-sub.cummax())/sub.cummax()).min()
    return {"cagr":cagr*100,"sharpe":sharpe,"mdd":dd*100,"calmar":cagr/abs(dd) if dd<0 else 0,"wealth":sub.iloc[-1]/sub.iloc[0]}

periodsB = [
    ("FULL 14-26",  pd.Timestamp("2014-01-01"), pd.Timestamp(END_B)),
    ("OOS 24-26",   OOS_START, pd.Timestamp(END_B)),
    ("Pre-OOS 14-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 18-23",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",       pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 26",       pd.Timestamp("2025-12-30"), pd.Timestamp(END_B)),
]
print("\n\n" + "="*100); print(f"  PHASE B RESULTS  (V11 stack, 50B init, 2014-2026)"); print("="*100)
for label, st, en in periodsB:
    print(f"\n  ── {label} ──")
    print(f"    {'Variant':<22} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
    for name, _ in PHASE_B_VARIANTS:
        m = metricsB(navsB[name], st, en)
        if not m: continue
        print(f"    {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")
print("\n" + "="*100); print("DONE.")
