# -*- coding: utf-8 -*-
"""
test_state_free_bav11.py
========================
Test state-free BA v11 via progressive stripping of state dependencies.

Variants (BAL leg, 25B book, 2014-2026):
  V_PROD       canonical sig + TQ34b state + full state-aware runner
  V_SFSIG      state_free sig + TQ34b state + SAME runner filters
  V_NO_SVT     V_SFSIG without SV_TIGHT filter (no days_since_release gate)
  V_NO_OH      V_NO_SVT without overheat AVOID
  V_NO_D1S     V_NO_OH with D1 RE_BACKLOG state cond REMOVED
  V_NO_ETFS    V_NO_D1S without cash_etf_states (no idle ETF parking)
  V_BLIND      V_NO_ETFS with state_by_date=None (fully state-blind runner)

Question: how much performance is lost as we strip state? Does V_BLIND
still beat B&H? If yes, BA v11 can be fully state-independent.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B = "2014-01-01"
END_B   = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASE  = {3: 0.7}
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B = "vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*100)
print("  STATE-FREE BA v11 PROGRESSION TEST")
print("="*100)

# ─── Common setup ────────────────────────────────────────────────────────
print("\n[1] Loading canonical + state_free signals...")
with open("ba_v11_unified_12y_sig.pkl","rb") as f: sig_canon = pickle.load(f)
with open("ba_v11_state_free_sig.pkl","rb") as f: sig_sf    = pickle.load(f)
sig_canon["time"] = pd.to_datetime(sig_canon["time"])
sig_sf["time"]    = pd.to_datetime(sig_sf["time"])
sig_canon = sig_canon[(sig_canon["time"]>=START_B) & (sig_canon["time"]<=END_B)].copy()
sig_sf    = sig_sf[(sig_sf["time"]>=START_B) & (sig_sf["time"]<=END_B)].copy()
print(f"  canonical: {len(sig_canon):,} rows | state_free: {len(sig_sf):,} rows")

with open("sim_v11_for_analyzer.py","r",encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE|re.DOTALL).group(1)

prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_canon.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_canon.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B))
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

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ─── State CSV → state_ff ─────────────────────────────────────────────────
state_df_tq = pd.read_csv(STATE_CSV_TQ34B)
state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B) & (state_df_tq["time"]<=END_B)][["time","state"]]
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"]))
state_ff_tq = {}; last=None
for d in vni_dates_B:
    s = sbd_tq.get(d)
    if s is not None: last = s
    state_ff_tq[d] = last

# ─── D1 reclassification (computed once; provides RE_BACKLOG_BUY in both sig sets) ────
print("\n[2] D1 RE_BACKLOG_BUY query...")
d1 = bq(f"""
WITH adv_dated AS (
  SELECT f.ticker, f.time AS f_time,
    SAFE_DIVIDE(f.AdvCust_P0, NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.ticker_financial AS f
),
fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
)
SELECT t.ticker, t.time, fa.fa_tier,
  SAFE_DIVIDE(t.NP_P0, t.NP_P4)-1 AS np_yoy,
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy, s5.state AS state5
FROM tav2_bq.ticker AS t
LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time = t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])
# Two versions: with vs without state condition
d1_mask_full = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
                & d1["state5"].isin([3,4,5])
                & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_mask_nostate = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
                   & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))


def apply_d1(sig, mask_df):
    d1_q = d1.loc[mask_df,["ticker","time"]].assign(_d1_ok=True)
    sig = sig.merge(d1_q, on=["ticker","time"], how="left")
    omask = sig["_d1_ok"].fillna(False) & (sig["ta"]>=120)
    sig.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
    sig = sig.drop(columns=["_d1_ok"])
    return sig


def sv_tight_keep(row):
    s = row.get("state5"); days = row.get("days_since_release")
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True


def apply_sv_tight(sig):
    mb_buy = sig["play_type"].isin(BUY_TIERS_V11)
    keep_mask = (~mb_buy) | sig.apply(sv_tight_keep, axis=1)
    return sig[keep_mask].copy()


def apply_overheat(sig, state_df):
    v_st = vni_full.merge(state_df, on="time", how="left"); v_st["state"] = v_st["state"].ffill()
    v_st["overheat"] = ((v_st["Close"]/v_st["MA200"]>1.30) & ((v_st["state"]==5) | (v_st["D_RSI"]>0.75)))
    oh = set(v_st[v_st["overheat"]]["time"])
    sig = sig.copy()
    sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return sig


def run_sim(sig, state_ff_param, cash_etf_param, label):
    nav, _ = simulate(sig, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=state_ff_param,
        cash_etf_states=cash_etf_param, vn30_underlying=vn30_underlying,
        etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0,
        etf_rebalance_friction=0.0015,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ, name=label)
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]


def metrics(nav_s):
    init = nav_s.iloc[0]; final = nav_s.iloc[-1]
    years = (nav_s.index[-1] - nav_s.index[0]).days/365.25
    cagr = (final/init)**(1/years)-1
    daily = nav_s.pct_change().dropna()
    sh = daily.mean()/daily.std()*np.sqrt(252) if daily.std()>0 else 0
    rm = nav_s.expanding().max()
    dd = ((nav_s-rm)/rm).min()
    return {"final":final/1e9, "cagr":cagr*100, "sharpe":sh, "maxdd":dd*100,
            "calmar": cagr/(-dd) if dd<0 else float('inf')}


# ─── Run all 7 variants ──────────────────────────────────────────────────
print("\n[3] Running 7 variants...")

# Need to add state5_dyn to state_free sig for SV_TIGHT (else returns True for all)
# Use TQ34b state for SV_TIGHT in all variants except V_NO_SVT and below
state_series = pd.DataFrame({"time": list(state_ff_tq.keys()), "state5_dyn": list(state_ff_tq.values())})

def with_state5_from_tq(sig):
    sig = sig.copy()
    if "state5" in sig.columns: sig = sig.drop(columns=["state5"])
    sig = sig.merge(state_series, on="time", how="left")
    sig = sig.rename(columns={"state5_dyn":"state5"})
    return sig

results = {}

# V_PROD: canonical + TQ34b + full state-aware runner (overheat + SV_TIGHT + D1state + ETF)
print("  V_PROD...")
sig_v = apply_d1(sig_canon, d1_mask_full)
sig_v = apply_sv_tight(sig_v)
sig_v = apply_overheat(sig_v, state_df_tq)
results["V_PROD"]    = run_sim(sig_v, state_ff_tq, ETF_BASE, "V_PROD")

# V_SFSIG: state_free signals + TQ34b state + full runner filters (with state-derived state5 for SV_TIGHT)
print("  V_SFSIG...")
sig_v = with_state5_from_tq(sig_sf)
sig_v = apply_d1(sig_v, d1_mask_full)
sig_v = apply_sv_tight(sig_v)
sig_v = apply_overheat(sig_v, state_df_tq)
results["V_SFSIG"]   = run_sim(sig_v, state_ff_tq, ETF_BASE, "V_SFSIG")

# V_NO_SVT: drop SV_TIGHT
print("  V_NO_SVT...")
sig_v = with_state5_from_tq(sig_sf)
sig_v = apply_d1(sig_v, d1_mask_full)
sig_v = apply_overheat(sig_v, state_df_tq)
results["V_NO_SVT"]  = run_sim(sig_v, state_ff_tq, ETF_BASE, "V_NO_SVT")

# V_NO_OH: also drop overheat
print("  V_NO_OH...")
sig_v = with_state5_from_tq(sig_sf)
sig_v = apply_d1(sig_v, d1_mask_full)
results["V_NO_OH"]   = run_sim(sig_v, state_ff_tq, ETF_BASE, "V_NO_OH")

# V_NO_D1S: also drop D1 state condition
print("  V_NO_D1S...")
sig_v = with_state5_from_tq(sig_sf)
sig_v = apply_d1(sig_v, d1_mask_nostate)
results["V_NO_D1S"]  = run_sim(sig_v, state_ff_tq, ETF_BASE, "V_NO_D1S")

# V_NO_ETFS: also drop cash_etf_states (no idle ETF parking)
print("  V_NO_ETFS...")
sig_v = with_state5_from_tq(sig_sf)
sig_v = apply_d1(sig_v, d1_mask_nostate)
results["V_NO_ETFS"] = run_sim(sig_v, state_ff_tq, None, "V_NO_ETFS")

# V_BLIND: state_by_date=None — fully state-blind runner
print("  V_BLIND...")
sig_v = with_state5_from_tq(sig_sf)
sig_v = apply_d1(sig_v, d1_mask_nostate)
results["V_BLIND"]   = run_sim(sig_v, None, None, "V_BLIND")

# B&H reference
bh = pd.DataFrame({"time": list(vn30_underlying.keys()), "Close": list(vn30_underlying.values())})
bh = bh.sort_values("time").reset_index(drop=True)
bh["nav"] = BOOK_NAV * bh["Close"] / bh["Close"].iloc[0]
results["B&H"] = bh.set_index("time")["nav"]

# ─── Summary ─────────────────────────────────────────────────────────────
print("\n"+"="*100)
print("  RESULTS — Progressive state-stripping (BAL leg, 25B book, Full 2014-2026)")
print("="*100)
print(f"\n  {'Variant':<11} {'Final':>9} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'ΔvsPROD':>9}")
m_prod = metrics(results["V_PROD"])
print(f"  {'V_PROD':<11} {m_prod['final']:>8.2f}B {m_prod['cagr']:>+6.2f}% {m_prod['sharpe']:>7.2f} {m_prod['maxdd']:>+6.1f}% {m_prod['calmar']:>7.2f} {'baseline':>9}")
for name in ["V_SFSIG","V_NO_SVT","V_NO_OH","V_NO_D1S","V_NO_ETFS","V_BLIND","B&H"]:
    m = metrics(results[name])
    d = (m['cagr'] - m_prod['cagr'])
    print(f"  {name:<11} {m['final']:>8.2f}B {m['cagr']:>+6.2f}% {m['sharpe']:>7.2f} {m['maxdd']:>+6.1f}% {m['calmar']:>7.2f} {d:>+6.2f}pp")

# By IS/OOS
print("\n  IS 2014-2019 vs OOS 2020-2026:")
for label, sd, ed in [("IS 14-19","2014-01-01","2019-12-31"), ("OOS 20-26","2020-01-01","2026-05-15")]:
    print(f"\n  [{label}]")
    m_prod_p = metrics(results["V_PROD"].loc[sd:ed])
    print(f"  {'V_PROD':<11} CAGR={m_prod_p['cagr']:>+.2f}% baseline")
    for name in ["V_SFSIG","V_NO_SVT","V_NO_OH","V_NO_D1S","V_NO_ETFS","V_BLIND","B&H"]:
        sub = results[name].loc[sd:ed]
        m = metrics(sub)
        d = m['cagr'] - m_prod_p['cagr']
        print(f"  {name:<11} CAGR={m['cagr']:>+.2f}% Δ={d:>+.2f}pp  Sh={m['sharpe']:.2f}  DD={m['maxdd']:+.1f}%")

# Save NAV curves
combined = pd.DataFrame({n: nav for n, nav in results.items()})
combined.to_csv(os.path.join(WORKDIR, "data/state_free_progression_nav.csv"))
print(f"\n  Saved -> data/state_free_progression_nav.csv")
