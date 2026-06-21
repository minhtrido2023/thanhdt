#!/usr/bin/env python3
"""
test_v3_3_walkforward.py — Walk-forward robustness test for v3.3 conc threshold.

Runs V11 12y backtest across the full conc threshold sweep
[no-filter, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70] and reports:

  (A) Robustness — performance plateau across thresholds.
      If many thresholds cluster at similar CAGR/Sharpe → robust.
      If only one specific value wins → overfit risk.

  (B) IS/OOS split — split 12y into IS (2014-2021) and OOS (2022-2026).
      Rank thresholds in IS; check if IS-best is also OOS-strong.
      If IS-best ≠ OOS-best → overfit.
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
IS_END   = pd.Timestamp("2021-12-31")
OOS_START_NEW = pd.Timestamp("2022-01-01")
TIER_BAL_B = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_B = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

# 8 variants: baseline v3.1, no-filter v3.3, and 6 conc thresholds
VARIANTS = [
    ("v3.1 baseline",   "vnindex_5state_tam_quan_v3_1_full_history.csv"),
    ("v3.3 (no filter)","vnindex_5state_tam_quan_v3_3_full_history.csv"),
    ("v3.3 t≤0.40",     "vnindex_5state_tam_quan_v3_3_t40_full_history.csv"),
    ("v3.3 t≤0.45",     "vnindex_5state_tam_quan_v3_3_t45_full_history.csv"),
    ("v3.3 t≤0.50",     "vnindex_5state_tam_quan_v3_3_t50_full_history.csv"),
    ("v3.3 t≤0.55",     "vnindex_5state_tam_quan_v3_3_t55_full_history.csv"),
    ("v3.3 t≤0.60",     "vnindex_5state_tam_quan_v3_3_t60_full_history.csv"),
    ("v3.3 t≤0.65",     "vnindex_5state_tam_quan_v3_3_t65_full_history.csv"),
    ("v3.3 t≤0.70",     "vnindex_5state_tam_quan_v3_3_t70_full_history.csv"),
]

print("="*100); print("Walk-forward robustness sweep: v3.3 conc threshold"); print("="*100)

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
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()

def run_variant(name, csv):
    print(f"  {name} ...", flush=True)
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

# Print three panels: FULL, IS (2014-2021), OOS (2022-2026)
print("\n\n" + "="*100)
print("  ROBUSTNESS PANEL — FULL period 2014-05-15")
print("="*100)
print(f"  {'Variant':<22} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
m_full = {}
for name, _ in VARIANTS:
    m = metrics(navs[name], pd.Timestamp("2014-01-01"), pd.Timestamp(END_B))
    if not m: continue
    m_full[name] = m
    print(f"  {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")

print("\n" + "="*100)
print("  IS PANEL — 2014-01-01 → 2021-12-31  (tune threshold using only this)")
print("="*100)
print(f"  {'Variant':<22} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
m_is = {}
for name, _ in VARIANTS:
    m = metrics(navs[name], pd.Timestamp("2014-01-01"), IS_END)
    if not m: continue
    m_is[name] = m
    print(f"  {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")

print("\n" + "="*100)
print("  OOS PANEL — 2022-01-01 → 2026-05-15  (verify IS-best threshold)")
print("="*100)
print(f"  {'Variant':<22} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
m_oos = {}
for name, _ in VARIANTS:
    m = metrics(navs[name], OOS_START_NEW, pd.Timestamp(END_B))
    if not m: continue
    m_oos[name] = m
    print(f"  {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")

# Rank: who's best in IS, OOS, FULL by Calmar?
def rank_by(d, key):
    items = sorted(d.items(), key=lambda kv: kv[1][key], reverse=True)
    return [k for k,v in items]

print("\n\n" + "="*100)
print("  RANKINGS (Calmar; higher = better)")
print("="*100)
print(f"  {'Rank':<6}{'FULL':<26}{'IS 2014-21':<26}{'OOS 2022-26':<26}")
r_full = rank_by(m_full, 'calmar')
r_is   = rank_by(m_is, 'calmar')
r_oos  = rank_by(m_oos, 'calmar')
for i in range(len(r_full)):
    print(f"  {i+1:<6}{r_full[i]:<26}{r_is[i]:<26}{r_oos[i]:<26}")

# CAGR rank too
print(f"\n  Same by CAGR:")
print(f"  {'Rank':<6}{'FULL':<26}{'IS 2014-21':<26}{'OOS 2022-26':<26}")
r_full_c = rank_by(m_full, 'cagr')
r_is_c   = rank_by(m_is, 'cagr')
r_oos_c  = rank_by(m_oos, 'cagr')
for i in range(len(r_full_c)):
    print(f"  {i+1:<6}{r_full_c[i]:<26}{r_is_c[i]:<26}{r_oos_c[i]:<26}")

# Spread analysis — is performance flat across thresholds (= robust) or peaked?
print(f"\n  SPREAD ANALYSIS (excluding v3.1 baseline)")
v3_only = {k:v for k,v in m_full.items() if k != "v3.1 baseline"}
cagrs = [v['cagr'] for v in v3_only.values()]
calmars = [v['calmar'] for v in v3_only.values()]
print(f"    FULL CAGR: min {min(cagrs):.2f}  max {max(cagrs):.2f}  spread {max(cagrs)-min(cagrs):.2f}pp")
print(f"    FULL Calmar: min {min(calmars):.2f}  max {max(calmars):.2f}  spread {max(calmars)-min(calmars):.2f}")
v3_oos = {k:v for k,v in m_oos.items() if k != "v3.1 baseline"}
oos_cagrs = [v['cagr'] for v in v3_oos.values()]
print(f"    OOS CAGR:  min {min(oos_cagrs):.2f}  max {max(oos_cagrs):.2f}  spread {max(oos_cagrs)-min(oos_cagrs):.2f}pp")

print("\n" + "="*100); print("DONE."); print("="*100)
