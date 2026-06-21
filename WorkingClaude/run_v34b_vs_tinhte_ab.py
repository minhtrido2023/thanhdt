#!/usr/bin/env python3
"""A/B backtest: V11/V12 with TQ34b state vs Tinh Tế state, 2014-01-01 -> 2026-05-26."""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B, END_B = "2014-01-01", "2026-05-26"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT, BORROW = 0.0, 0.10
ETF_BASE = {3: 0.7}
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY","MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12

print("="*80); print(f"  A/B: V11+TQ34b vs V11+Tinh_Te vs V12+Tinh_Te ({START_B}->{END_B})"); print("="*80)

print("\n[1] Loading signals/prices/VNI/Open...")
with open("data/ba_v11_unified_12y_sig.pkl","rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
sig_B = sig_B[(sig_B["time"]>=START_B) & (sig_B["time"]<=END_B)].copy()
with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VQ = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_B.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_B.iterrows()}
vni_B = bq(VQ.format(start=START_B, end=END_B))
vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))

opens_df = bq(f"""SELECT t.ticker, t.time, t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk,g in opens_df.groupby("ticker")}

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

print("\n[2] Loading 2 state series...")
# TQ34b from CSV (clean)
state_tq = pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
state_tq["time"] = pd.to_datetime(state_tq["time"])
state_tq = state_tq[(state_tq["time"]>=START_B) & (state_tq["time"]<=END_B)][["time","state"]]
# Tinh Tế from BQ archive
state_tt = bq(f"""SELECT s.time, s.state FROM tav2_bq.vnindex_5state_archive_tinh_te_20260525_220329 AS s
WHERE s.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY s.time""")
state_tt["time"] = pd.to_datetime(state_tt["time"])

def ff_states(state_df):
    sbd = dict(zip(state_df["time"], state_df["state"]))
    out = {}; last=None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        out[d] = last
    return out

ff_tq = ff_states(state_tq); ff_tt = ff_states(state_tt)

# State distribution comparison
print(f"\n  TQ34b distribution: {dict(state_tq['state'].value_counts().sort_index())}")
print(f"  Tinh_Te distribution: {dict(state_tt['state'].value_counts().sort_index())}")

print("\n[3] D1 RE_BACKLOG reclassification...")
d1 = bq(f"""WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_B = sig_B.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_B["_d1_ok"].fillna(False) & (sig_B["ta"]>=120)
sig_B.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_B = sig_B.drop(columns=["_d1_ok"])

print("\n[4] SV_TIGHT per-state...")
def sv_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True
mb_buy = sig_B["play_type"].isin(BUY_TIERS)
keep_mask = (~mb_buy) | sig_B.apply(sv_keep, axis=1)
sig_B = sig_B[keep_mask].copy()

print("\n[5] Overheat AVOID per state-set...")
def overheat_set(state_df):
    v = vni_full.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
    v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
    return set(v[v["overheat"]]["time"])

oh_tq = overheat_set(state_tq); oh_tt = overheat_set(state_tt)
def apply_oh(sig, oh):
    s2 = sig.copy()
    s2.loc[s2["time"].isin(oh) & s2["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"
    return s2
sig_tq = apply_oh(sig_B, oh_tq); sig_tt = apply_oh(sig_B, oh_tt)

print("\n[6] Universe + sector...")
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,"liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

def run_bal(sig_use, ff, label):
    nav, _ = simulate(sig_use, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT, tier_weights=TIER_WEIGHTS,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=ff,
        cash_etf_states=ETF_BASE, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015, open_prices=open_prices, t1_open_exec=True,
        **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    print(f"  {label}: {s.iloc[-1]/1e9:.3f}B"); return s

def run_vn30(sig_use, ff, label):
    sig30 = sig_use[sig_use["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map, tier_weights=TIER_WEIGHTS,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=ff,
        cash_etf_states=ETF_BASE, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015, open_prices=open_prices, t1_open_exec=True,
        **LIQ30, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); s = nav.set_index("time")["nav"]
    print(f"  {label}: {s.iloc[-1]/1e9:.3f}B"); return s

print("\n[7] 4 legs...")
bal_tq = run_bal(sig_tq, ff_tq, "BAL_TQ34b")
bal_tt = run_bal(sig_tt, ff_tt, "BAL_TinhTe")
vn30_tq = run_vn30(sig_tq, ff_tq, "VN30_TQ34b")
vn30_tt = run_vn30(sig_tt, ff_tt, "VN30_TinhTe")

print("\n[8] Metrics...")
common = bal_tq.index.intersection(bal_tt.index).intersection(vn30_tq.index).intersection(vn30_tt.index)
nav_V11_tq = (bal_tq.loc[common] + vn30_tq.loc[common]) / TOTAL_NAV
nav_V11_tt = (bal_tt.loc[common] + vn30_tt.loc[common]) / TOTAL_NAV
vni_aligned = vni_B.set_index("time")["Close"].reindex(common).ffill()
vni_n = vni_aligned / vni_aligned.iloc[0]

def metrics(nav, start, end):
    s = nav[(nav.index>=start)&(nav.index<=end)].dropna()
    if len(s)<30: return None
    r = s.pct_change().dropna(); y = (s.index[-1]-s.index[0]).days/365.25
    spy = len(r)/y if y>0 else 252
    cagr = (s.iloc[-1]/s.iloc[0])**(1/y)-1 if y>0 else 0
    sh = r.mean()/r.std()*np.sqrt(spy) if r.std()>0 else 0
    dd = ((s-s.cummax())/s.cummax()).min()
    cal = cagr/abs(dd) if dd<0 else 0
    return cagr*100, sh, dd*100, cal, s.iloc[-1]/s.iloc[0]

print("\n"+"="*100); print(f"  V11 STACK A/B: TQ34b (v3.4b) vs Tinh_Te (LIVE pre-2026-05-21)  ({START_B}->{common.max().date()})"); print("="*100)
print(f"{'System':<22}{'CAGR':>9}{'Sharpe':>9}{'MaxDD':>9}{'Calmar':>8}{'Wealth':>9}")
for name, nav in [("V11+TQ34b", nav_V11_tq),("V11+Tinh_Te", nav_V11_tt),("VNI B&H", vni_n)]:
    m = metrics(nav, common.min(), common.max())
    if m: print(f"  {name:<20}{m[0]:>+8.2f}%{m[1]:>+9.2f}{m[2]:>+8.2f}%{m[3]:>+8.2f}{m[4]:>+9.2f}")

# Save NAVs
out = pd.DataFrame({"V11_TQ34b": nav_V11_tq, "V11_Tinh_Te": nav_V11_tt, "VNI": vni_n})
out.index.name = "time"
out.to_csv("data/ab_v34b_vs_tinhte.csv")
print(f"\nSaved: data/ab_v34b_vs_tinhte.csv  shape={out.shape}")

# Period slices
print()
periods = [("FULL","2014-01-01","2026-05-26"),
           ("IS_14_19","2014-01-01","2019-12-31"),
           ("OOS_20_23","2020-01-01","2023-12-31"),
           ("OOS_24_26","2024-01-01","2026-05-26"),
           ("YTD_2026","2026-01-01","2026-05-26")]
print(f"{'Period':<12}{'V11+TQ34b':>15}{'V11+Tinh_Te':>15}{'Delta':>10}{'VNI':>10}")
for p,sd,ed in periods:
    mt = metrics(nav_V11_tq, sd, ed); mn = metrics(nav_V11_tt, sd, ed); mv = metrics(vni_n, sd, ed)
    if mt and mn:
        print(f"{p:<12}{mt[0]:>+13.2f}% {mn[0]:>+13.2f}% {mt[0]-mn[0]:>+8.2f}pp{mv[0]:>+9.2f}%")
print("DONE.")
