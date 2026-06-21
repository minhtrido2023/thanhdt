#!/usr/bin/env python3
"""
test_v3_4_btc_walkforward.py — V11 12y backtest sweep across BTC thresholds.

14 BTC variants + v3.1 baseline = 15 backtests.
Reports IS (2014-2021) / OOS (2022-2026) / FULL panels +
ranking + plateau analysis.

If FULL CAGR has plateau across reasonable thresholds AND IS-best is also
OOS-strong → not overfit. Otherwise → tune-the-corner.
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
IS_END = pd.Timestamp("2021-12-31")
OOS_NEW = pd.Timestamp("2022-01-01")
TIER_BAL_B = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_B = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}

# All 14 BTC variants + baseline
VARIANTS = [("v3.1 baseline", "vnindex_5state_tam_quan_v3_1_full_history.csv")]
for h, ts in [(120, [5,10,15,20,25,30]), (60, [5,8,12,15]), (180, [15,20,25,30])]:
    h_label = {60:"3M", 120:"6M", 180:"9M"}[h]
    for t in ts:
        name = f"{h_label} T>{t}%"
        csv  = f"vnindex_5state_tam_quan_v3_4_btc{h_label}_T{t:02d}_full_history.csv"
        VARIANTS.append((name, csv))

print("="*100); print(f"V11 12y backtest: {len(VARIANTS)} BTC sweep variants"); print("="*100)
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

def run(name, csv):
    print(f"  {name:<14} ...", flush=True)
    state_df = pd.read_csv(os.path.join(WORKDIR, csv))
    state_df["time"] = pd.to_datetime(state_df["time"])
    state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]
    sbd = dict(zip(state_df["time"], state_df["state"]))
    sbd_ff = {}; last = None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        sbd_ff[d] = last
    v = vni_full_B.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    od = set(v[v["overheat"]]["time"])
    sig_v = sig_B.copy()
    sig_v.loc[sig_v["time"].isin(od) & sig_v["play_type"].isin(BUY_TIERS_B), "play_type"] = "AVOID_overheated"
    LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
           "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}
    nb, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL_B, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV_B,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=sbd_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ, name="BAL")
    nb["time"] = pd.to_datetime(nb["time"])
    sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nv, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL_B, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV_B,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, state_by_date=sbd_ff,
        cash_etf_states=ETF_STATES, vn30_underlying=vn30_underlying, **LIQ30, name="VN30")
    nv["time"] = pd.to_datetime(nv["time"])
    common = nb.set_index("time")["nav"].index.intersection(nv.set_index("time")["nav"].index)
    tot = nb.set_index("time")["nav"].loc[common] + nv.set_index("time")["nav"].loc[common]
    return tot/TOTAL_NAV_B

navs = {}
for name, csv in VARIANTS:
    navs[name] = run(name, csv)

def metrics(nav, start, end):
    sub = nav[(nav.index>=start) & (nav.index<=end)]
    if len(sub)<30: return None
    rets = sub.pct_change().dropna()
    yrs = (sub.index[-1]-sub.index[0]).days/365.25
    cagr = (sub.iloc[-1]/sub.iloc[0])**(1/yrs)-1 if yrs>0 else 0
    sharpe = rets.mean()/rets.std()*np.sqrt(len(rets)/yrs) if rets.std()>0 else 0
    dd = ((sub-sub.cummax())/sub.cummax()).min()
    return {"cagr":cagr*100,"sharpe":sharpe,"mdd":dd*100,
            "calmar":cagr/abs(dd) if dd<0 else 0,"wealth":sub.iloc[-1]/sub.iloc[0]}

# === Print 3 panels: FULL, IS (2014-2021), OOS (2022-2026) ===
def panel(label, st, en):
    print(f"\n{'='*100}\n  PANEL: {label}\n{'='*100}")
    print(f"  {'Variant':<22} {'CAGR%':>8} {'Sharpe':>8} {'MaxDD%':>9} {'Calmar':>8} {'Wealth':>8}")
    base_m = metrics(navs["v3.1 baseline"], st, en)
    rows = []
    for name, _ in VARIANTS:
        m = metrics(navs[name], st, en)
        if not m: continue
        rows.append((name, m))
        if name == "v3.1 baseline":
            print(f"  {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}")
        else:
            print(f"  {name:<22} {m['cagr']:>+7.2f} {m['sharpe']:>+8.2f} {m['mdd']:>+8.2f} {m['calmar']:>+7.2f} {m['wealth']:>+8.2f}  Δ({m['cagr']-base_m['cagr']:+.2f}/{m['calmar']-base_m['calmar']:+.2f})")
    return rows

rows_full = panel("FULL 14-26", pd.Timestamp("2014-01-01"), pd.Timestamp(END_B))
rows_is   = panel("IS  14-21",  pd.Timestamp("2014-01-01"), IS_END)
rows_oos  = panel("OOS 22-26",  OOS_NEW,                    pd.Timestamp(END_B))

# Rankings by Calmar + CAGR
print(f"\n{'='*100}\n  RANKINGS (top 5 by Calmar; higher = better)\n{'='*100}")
def rank_by(rows, key):
    rs = [r for r in rows if r[0] != "v3.1 baseline"]
    return sorted(rs, key=lambda r: r[1][key], reverse=True)

for label, rows in [("FULL", rows_full), ("IS", rows_is), ("OOS", rows_oos)]:
    print(f"\n  {label} — by Calmar:")
    for r in rank_by(rows, "calmar")[:5]:
        print(f"    {r[0]:<22}  CAGR={r[1]['cagr']:+.2f}  Calmar={r[1]['calmar']:.2f}  Sharpe={r[1]['sharpe']:.2f}")
    print(f"  {label} — by CAGR:")
    for r in rank_by(rows, "cagr")[:5]:
        print(f"    {r[0]:<22}  CAGR={r[1]['cagr']:+.2f}  Calmar={r[1]['calmar']:.2f}  Sharpe={r[1]['sharpe']:.2f}")

# Spread analysis — exclude baseline
print(f"\n{'='*100}\n  SPREAD ANALYSIS (excluding baseline)\n{'='*100}")
for label, rows in [("FULL", rows_full), ("IS", rows_is), ("OOS", rows_oos)]:
    cagrs = [r[1]['cagr'] for r in rows if r[0] != "v3.1 baseline"]
    calmars = [r[1]['calmar'] for r in rows if r[0] != "v3.1 baseline"]
    print(f"  {label}: CAGR spread {max(cagrs)-min(cagrs):.2f}pp ({min(cagrs):.2f} → {max(cagrs):.2f})  "
          f"Calmar spread {max(calmars)-min(calmars):.2f}")

# Subset by horizon: plateau within 6M
print(f"\n{'='*100}\n  6M HORIZON THRESHOLD SWEEP — FULL CAGR plateau check\n{'='*100}")
print(f"  {'Threshold':<8} {'FULL CAGR':>10} {'IS CAGR':>10} {'OOS CAGR':>10}")
for t in [5,10,15,20,25,30]:
    nm = f"6M T>{t}%"
    if nm not in [r[0] for r in rows_full]: continue
    fc = next(r[1]['cagr'] for r in rows_full if r[0]==nm)
    ic = next(r[1]['cagr'] for r in rows_is if r[0]==nm)
    oc = next(r[1]['cagr'] for r in rows_oos if r[0]==nm)
    print(f"  T>{t:>2}%  {fc:>+9.2f}  {ic:>+9.2f}  {oc:>+9.2f}")

print(f"\n  3M HORIZON THRESHOLD SWEEP:")
print(f"  {'Threshold':<8} {'FULL CAGR':>10} {'IS CAGR':>10} {'OOS CAGR':>10}")
for t in [5,8,12,15]:
    nm = f"3M T>{t}%"
    fc = next(r[1]['cagr'] for r in rows_full if r[0]==nm)
    ic = next(r[1]['cagr'] for r in rows_is if r[0]==nm)
    oc = next(r[1]['cagr'] for r in rows_oos if r[0]==nm)
    print(f"  T>{t:>2}%  {fc:>+9.2f}  {ic:>+9.2f}  {oc:>+9.2f}")

print(f"\n  9M HORIZON THRESHOLD SWEEP:")
print(f"  {'Threshold':<8} {'FULL CAGR':>10} {'IS CAGR':>10} {'OOS CAGR':>10}")
for t in [15,20,25,30]:
    nm = f"9M T>{t}%"
    fc = next(r[1]['cagr'] for r in rows_full if r[0]==nm)
    ic = next(r[1]['cagr'] for r in rows_is if r[0]==nm)
    oc = next(r[1]['cagr'] for r in rows_oos if r[0]==nm)
    print(f"  T>{t:>2}%  {fc:>+9.2f}  {ic:>+9.2f}  {oc:>+9.2f}")

print("\n" + "="*100); print("DONE.")
