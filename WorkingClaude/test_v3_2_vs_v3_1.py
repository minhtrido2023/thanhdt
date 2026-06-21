#!/usr/bin/env python3
"""
test_v3_2_vs_v3_1.py — V11 12y backtest comparing v3.2 (waypoint rule)
against v3.1 baseline.

v3.2 rule: when state goes CRISIS→NEUTRAL directly and r_dual<0.60 at the
trigger day, snap to BEAR waypoint until r_dual ≥ 0.60 or state changes
naturally. Diagnostic showed this fires 9 times across 26y, all in weak
post-crisis recovery scenarios with negative T+20 forward edge.

Stack: V11 BAL (50/50 BAL leg + VN30 leg) + V6 ETF + standard P3 overheat
guard, 2014-01-01 → 2026-05-15, 50B init.

Compares:
  • v3.1 (local CSV vnindex_5state_tam_quan_v3_1_full_history.csv)
  • v3.2 (local CSV vnindex_5state_tam_quan_v3_2_full_history.csv)
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
    ("v3.1 baseline", "vnindex_5state_tam_quan_v3_1_full_history.csv"),
    ("v3.2 waypoint", "vnindex_5state_tam_quan_v3_2_full_history.csv"),
]

print("="*100); print("V11 12y backtest: v3.1 vs v3.2 waypoint rule"); print("="*100)

# ── Shared data ────────────────────────────────────────────────────────
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

# ── Run each variant ───────────────────────────────────────────────────
def run_variant(name, csv):
    print("\n" + "="*100); print(f"  {name}"); print("="*100)
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

    # BAL leg
    nav_bal, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL_B, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV_B,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=sbd_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name="BAL")
    nav_bal["time"] = pd.to_datetime(nav_bal["time"])

    # VN30 leg
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

# ── Metrics ───────────────────────────────────────────────────────────
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
    print(f"    {'Variant':<18} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
    ms = {}
    for name, _ in VARIANTS:
        m = metrics(navs[name], st, en)
        if not m: continue
        ms[name] = m
        print(f"    {name:<18} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")
    if "v3.1 baseline" in ms and "v3.2 waypoint" in ms:
        a = ms["v3.1 baseline"]; b = ms["v3.2 waypoint"]
        print(f"    {'Δ (v3.2 - v3.1)':<18} {b['cagr']-a['cagr']:>+7.2f} {b['sharpe']-a['sharpe']:>+8.2f} "
              f"{b['mdd']-a['mdd']:>+8.2f} {b['calmar']-a['calmar']:>+7.2f} {b['wealth']-a['wealth']:>+8.2f}")

# Year-by-year
print(f"\n  ── Year-by-year (annual %) ──")
print(f"    {'Year':<6} {'v3.1':>8} {'v3.2':>8} {'Δ pp':>9}")
for yr in range(2014, 2027):
    yres = {}
    for name, _ in VARIANTS:
        nv = navs[name]
        s = nv[(nv.index>=f"{yr}-01-01") & (nv.index<=f"{yr}-12-31")]
        if len(s)<2: yres[name]=None; continue
        yres[name] = (s.iloc[-1]/s.iloc[0]-1)*100
    if all(v is None for v in yres.values()): continue
    a = yres.get("v3.1 baseline"); b = yres.get("v3.2 waypoint")
    if a is None or b is None: continue
    print(f"    {yr:<6} {a:>+7.1f}% {b:>+7.1f}% {b-a:>+7.1f}pp")

# Save NAV CSVs for archival
out_dir = WORKDIR
for name, _ in VARIANTS:
    fn = f"v11_nav_{name.replace(' ','_').replace('.','_')}.csv"
    navs[name].to_csv(os.path.join(out_dir, fn), header=["nav_norm"])
print(f"\n  NAV CSVs saved (v11_nav_*.csv)")

print("\n" + "="*100); print("DONE."); print("="*100)
