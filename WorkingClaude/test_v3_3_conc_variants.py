#!/usr/bin/env python3
"""
test_v3_3_conc_variants.py — V11 12y backtest comparing v3.1 baseline
against v3.3 and 2 concentration variants:

  v3.1         baseline
  v3.3         RSI gate (no conc filter), 31 fires
  v3.3b        RSI gate + conc ≤ 0.55,     26 fires
  v3.3c        RSI gate + conc ≤ 0.45,     24 fires

Focus on Q1 2026 and OOS 24-26 to see if conc filter improves recent
weakness without sacrificing the +0.87pp FULL-period win.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, re, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV_B  = 50_000_000_000; BOOK_NAV_B = TOTAL_NAV_B / 2
DEPOSIT = 0.01; ETF_STATES = {3: 0.7}
OOS_START = pd.Timestamp("2024-01-01")
TIER_BAL_B = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_B = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

VARIANTS = [
    ("v3.1 baseline",     "vnindex_5state_tam_quan_v3_1_full_history.csv"),
    ("v3.3 RSI gate",     "vnindex_5state_tam_quan_v3_3_full_history.csv"),
    ("v3.3b conc≤0.55",   "vnindex_5state_tam_quan_v3_3b_full_history.csv"),
    ("v3.3c conc≤0.45",   "vnindex_5state_tam_quan_v3_3c_full_history.csv"),
]

print("="*100); print("V11 12y backtest: v3.1 vs v3.3 vs v3.3b vs v3.3c"); print("="*100)

# Shared data
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

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL
            """).set_index("ticker")["s"].to_dict()

def run_variant(name, csv):
    print(f"\n=== {name} ===")
    state_df = pd.read_csv(os.path.join(WORKDIR, csv))
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
    LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
           "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}
    nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
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
    nav_vn30, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL_B, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV_B,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=sbd_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ30, name="VN30")
    nav_vn30["time"] = pd.to_datetime(nav_vn30["time"])
    common = nav_bal.set_index("time")["nav"].index.intersection(nav_vn30.set_index("time")["nav"].index)
    nav_total = nav_bal.set_index("time")["nav"].loc[common] + nav_vn30.set_index("time")["nav"].loc[common]
    return nav_total / TOTAL_NAV_B

navs = {}
for name, csv in VARIANTS:
    navs[name] = run_variant(name, csv)

def metrics(nav, start, end):
    sub = nav[(nav.index>=start) & (nav.index<=end)]
    if len(sub)<30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1]-sub.index[0]).days/365.25
    spy = len(rets)/yrs if yrs>0 else 252
    cagr = (sub.iloc[-1]/sub.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sharpe = rets.mean()/rets.std()*np.sqrt(spy) if rets.std()>0 else 0
    dd = ((sub-sub.cummax())/sub.cummax()).min()
    return {"cagr":cagr*100,"sharpe":sharpe,"mdd":dd*100,
            "calmar":cagr/abs(dd) if dd<0 else 0,"wealth":sub.iloc[-1]/sub.iloc[0]}

periods = [
    ("FULL 14-26",  pd.Timestamp("2014-01-01"), pd.Timestamp(END_B)),
    ("OOS 24-26",   OOS_START, pd.Timestamp(END_B)),
    ("Pre-OOS 14-19", pd.Timestamp("2014-01-01"), pd.Timestamp("2019-12-31")),
    ("Mid 18-23",   pd.Timestamp("2018-01-01"), pd.Timestamp("2023-12-31")),
    ("Y2022",       pd.Timestamp("2022-01-01"), pd.Timestamp("2022-12-31")),
    ("Q1 26",       pd.Timestamp("2025-12-30"), pd.Timestamp(END_B)),
]

print("\n\n" + "="*100); print("  RESULTS — V11 stack, 50B init"); print("="*100)
for label, st, en in periods:
    print(f"\n  ── {label} ──")
    print(f"    {'Variant':<22} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
    base_m = None
    for name, _ in VARIANTS:
        m = metrics(navs[name], st, en)
        if not m: continue
        if name == "v3.1 baseline":
            base_m = m
            print(f"    {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")
        else:
            d_cagr = m['cagr']-base_m['cagr']; d_sh = m['sharpe']-base_m['sharpe']
            d_dd = m['mdd']-base_m['mdd']; d_cal = m['calmar']-base_m['calmar']
            d_w = m['wealth']-base_m['wealth']
            print(f"    {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}  Δ({d_cagr:+.2f}/{d_sh:+.2f}/{d_dd:+.2f}/{d_cal:+.2f}/{d_w:+.2f})")

# Year-by-year
print(f"\n  ── Year-by-year (annual %) ──")
print(f"    {'Year':<6}", end="")
for name, _ in VARIANTS:
    print(f" {name[:14]:>15}", end="")
print()
for yr in range(2014, 2027):
    yres = {}
    for name, _ in VARIANTS:
        nv = navs[name]
        s = nv[(nv.index>=f"{yr}-01-01") & (nv.index<=f"{yr}-12-31")]
        if len(s)<2: yres[name]=None; continue
        yres[name] = (s.iloc[-1]/s.iloc[0]-1)*100
    if all(v is None for v in yres.values()): continue
    print(f"    {yr:<6}", end="")
    for name, _ in VARIANTS:
        v = yres.get(name)
        print(f" {v:>+14.1f}%" if v is not None else f" {'—':>15}", end="")
    print()

print("\n" + "="*100); print("DONE."); print("="*100)
