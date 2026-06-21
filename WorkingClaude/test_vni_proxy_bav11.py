# -*- coding: utf-8 -*-
"""
test_vni_proxy_bav11.py
=======================
Alternative approach to state-independence:
Replace 5-state machine flags with TRANSPARENT VNI-based market regime
proxies — still simple price/MA rules, but NOT the 5-state system.

VNI-PROXY rules (all derived from VNINDEX Close/MA50/MA200/D_RSI only):
  bear_zone   = (VNI < MA200 * 0.95) OR (VNI < MA50 AND MA50 < MA200)
  neutral     = NOT bear_zone AND VNI < MA200 * 1.10
  bull        = VNI > MA200 * 1.10 AND VNI > MA50
  overheat    = VNI/MA200 > 1.30 AND D_RSI > 0.75

Filter mapping (mimics the 5-state filters using VNI-proxy):
  AVOID_bear_proxy: bear_zone → block buys
  SV_TIGHT_proxy:  universal days_since_release <= 60 (state-free)
  Overheat_proxy:  overheat = TRUE → AVOID_overheated
  D1_state_proxy:  D1 RE_BACKLOG requires NOT bear_zone (less restrictive than state5∈{3,4,5})
  Cash_ETF_proxy:  fixed 70% ETF when neutral else 0%

This is FULLY independent of the 5-state machine — only uses VNI MA values.
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
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATE_CSV_TQ34B = "vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*100)
print("  VNI-PROXY BA v11 (state-machine-independent, VNI-MA based)")
print("="*100)

# Load signals
print("\n[1] Load signals + prices + VNI...")
with open("ba_v11_unified_12y_sig.pkl","rb") as f: sig_canon = pickle.load(f)
with open("ba_v11_state_free_sig.pkl","rb") as f: sig_sf    = pickle.load(f)
sig_canon["time"] = pd.to_datetime(sig_canon["time"])
sig_sf["time"]    = pd.to_datetime(sig_sf["time"])
sig_canon = sig_canon[(sig_canon["time"]>=START_B) & (sig_canon["time"]<=END_B)].copy()
sig_sf    = sig_sf[(sig_sf["time"]>=START_B) & (sig_sf["time"]<=END_B)].copy()

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

vni_full = bq(f"""SELECT t.time, t.Close, t.MA20, t.MA50, t.MA200, t.D_RSI
FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

# ─── VNI-PROXY zones ─────────────────────────────────────────────────────
print("\n[2] Building VNI-proxy regime zones...")
v = vni_full.copy()
v["bear_zone"]   = (v["Close"] < v["MA200"] * 0.95) | ((v["Close"] < v["MA50"]) & (v["MA50"] < v["MA200"]))
v["bull"]        = (v["Close"] > v["MA200"] * 1.10) & (v["Close"] > v["MA50"])
v["neutral"]     = (~v["bear_zone"]) & (~v["bull"])
v["overheat"]    = (v["Close"]/v["MA200"] > 1.30) & (v["D_RSI"] > 0.75)

print(f"  bear_zone days: {v['bear_zone'].sum()} ({v['bear_zone'].mean()*100:.1f}%)")
print(f"  neutral days:   {v['neutral'].sum()} ({v['neutral'].mean()*100:.1f}%)")
print(f"  bull days:      {v['bull'].sum()} ({v['bull'].mean()*100:.1f}%)")
print(f"  overheat days:  {v['overheat'].sum()} ({v['overheat'].mean()*100:.1f}%)")

bear_dates     = set(v[v["bear_zone"]]["time"])
overheat_dates = set(v[v["overheat"]]["time"])
neutral_dates  = set(v[v["neutral"]]["time"])

# Build proxy state mapping for SV_TIGHT-like behavior
# Map proxy: bear_zone -> 'state5'=1 (CRISIS), neutral -> 3, bull -> 4
proxy_state_map = {}
for _, r in v.iterrows():
    if r["bear_zone"]: proxy_state_map[r["time"]] = 1
    elif r["neutral"]: proxy_state_map[r["time"]] = 3
    else:              proxy_state_map[r["time"]] = 4

# Sector + liquidity
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# TQ34b state_ff (for V_PROD comparison)
state_df_tq = pd.read_csv(STATE_CSV_TQ34B)
state_df_tq["time"] = pd.to_datetime(state_df_tq["time"])
state_df_tq = state_df_tq[(state_df_tq["time"]>=START_B) & (state_df_tq["time"]<=END_B)][["time","state"]]
sbd_tq = dict(zip(state_df_tq["time"], state_df_tq["state"]))
state_ff_tq = {}; last=None
for d in vni_dates_B:
    s = sbd_tq.get(d)
    if s is not None: last = s
    state_ff_tq[d] = last

# D1 base
print("\n[3] D1 RE_BACKLOG (with VNI-proxy state cond)...")
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
  fin.Revenue_YoY_P0 AS rev_yoy, adv.adv_yoy
FROM tav2_bq.ticker AS t
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}'
  AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
""")
d1["time"] = pd.to_datetime(d1["time"])

# D1 mask: vni-proxy NOT bear_zone (more transparent than state5∈{3,4,5})
d1_mask_vniproxy = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
                    & ~d1["time"].isin(bear_dates)
                    & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_mask_full = d1_mask_vniproxy  # same — using VNI proxy

def apply_d1(sig, mask):
    d1_q = d1.loc[mask,["ticker","time"]].assign(_d1_ok=True)
    sig = sig.merge(d1_q, on=["ticker","time"], how="left")
    omask = sig["_d1_ok"].fillna(False) & (sig["ta"]>=120)
    sig.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
    return sig.drop(columns=["_d1_ok"])

# ─── VNI-proxy filter functions ──────────────────────────────────────────
def apply_avoid_bear_vniproxy(sig):
    """Replace state5∈{1,2} → AVOID_bear with VNI bear_zone."""
    sig = sig.copy()
    sig.loc[sig["time"].isin(bear_dates) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_bear_VNI"
    return sig

def apply_overheat_vniproxy(sig):
    """Replace state5==5 + overheat with VNI-only overheat (no state needed)."""
    sig = sig.copy()
    sig.loc[sig["time"].isin(overheat_dates) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return sig

def apply_universal_svtight(sig, max_days=60):
    """Universal days_since_release filter (no state)."""
    sig = sig.copy()
    mb_buy = sig["play_type"].isin(BUY_TIERS_V11)
    bad = mb_buy & (sig["days_since_release"].isna() | (sig["days_since_release"] > max_days))
    sig.loc[bad, "play_type"] = "PASS_stale_Q"
    return sig

# Helper to attach proxy_state5 to sig
def attach_proxy_state5(sig):
    sig = sig.copy()
    if "state5" in sig.columns: sig = sig.drop(columns=["state5"])
    psr = pd.DataFrame({"time": list(proxy_state_map.keys()), "state5": list(proxy_state_map.values())})
    return sig.merge(psr, on="time", how="left")

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

# ─── Variants ────────────────────────────────────────────────────────────
print("\n[4] Running 5 variants...")

# V_PROD: canonical signals + TQ34b state + full state-aware runner (BASELINE for comparison)
print("  V_PROD...")
sig_v = apply_d1(sig_canon, d1.assign(state5_d1=d1["time"].map(lambda t: proxy_state_map.get(t, 3))).pipe(
    lambda x: (x["adv_yoy"].notna() & (x["adv_yoy"]>0.5) & x["fa_tier"].isin(["C","D"])
               & x["state5_d1"].isin([3,4,5])
               & ((x["np_yoy"].fillna(-99)>0) | (x["rev_yoy"].fillna(-99)>0)))
))
# Apply canonical SV_TIGHT using TQ34b state
def sv_tight_canonical(row, sf):
    s = sf.get(row["time"]); days = row.get("days_since_release")
    if s is None: return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days<=30
    if s in (2,3): return pd.notna(days) and days<=60
    return True

mb_buy = sig_v["play_type"].isin(BUY_TIERS_V11)
keep = (~mb_buy) | sig_v.apply(lambda r: sv_tight_canonical(r, state_ff_tq), axis=1)
sig_v_prod = sig_v[keep].copy()

# Overheat for V_PROD: needs state5==5 OR D_RSI>0.75 + Close/MA200>1.30
v_oh = vni_full.merge(state_df_tq, on="time", how="left"); v_oh["state"] = v_oh["state"].ffill()
v_oh["overheat"] = ((v_oh["Close"]/v_oh["MA200"]>1.30) & ((v_oh["state"]==5) | (v_oh["D_RSI"]>0.75)))
oh_canon = set(v_oh[v_oh["overheat"]]["time"])
sig_v_prod.loc[sig_v_prod["time"].isin(oh_canon) & sig_v_prod["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

nav_prod = run_sim(sig_v_prod, state_ff_tq, {3: 0.7}, "V_PROD")

# V_VNI: VNI-proxy ALL THE WAY — state_free signals + VNI-proxy filters + VNI-proxy ETF
print("  V_VNI...")
sig_v = apply_d1(sig_sf, d1_mask_vniproxy)
sig_v = apply_avoid_bear_vniproxy(sig_v)
sig_v = apply_universal_svtight(sig_v, max_days=60)
sig_v = apply_overheat_vniproxy(sig_v)
sig_v = attach_proxy_state5(sig_v)
# Use proxy_state_map as state_by_date for ETF parking (only neutral → ETF)
nav_vni = run_sim(sig_v, proxy_state_map, {3: 0.7}, "V_VNI")

# V_VNI_NO_ETF: VNI-proxy filters but no ETF parking
print("  V_VNI_NO_ETF...")
nav_vni_noetf = run_sim(sig_v, None, None, "V_VNI_NO_ETF")

# V_VNI_DEPOSIT: VNI-proxy filters, no ETF, deposit=6%/yr (idle cash earns deposit interest)
print("  V_VNI_DEPOSIT...")
nav_vni_dep = None
try:
    nav_dep_raw, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT,
        tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=0.06, borrow_annual=BORROW,
        state_by_date=None, cash_etf_states=None,
        vn30_underlying=vn30_underlying,
        open_prices=open_prices, t1_open_exec=True,
        **LIQ, name="V_VNI_DEP")
    nav_dep_raw["time"] = pd.to_datetime(nav_dep_raw["time"])
    nav_vni_dep = nav_dep_raw.set_index("time")["nav"]
except Exception as e:
    print(f"    ERROR: {e}")

# V_VNI_LIGHT: VNI-proxy WITHOUT bear_zone block (only overheat + SV_TIGHT)
print("  V_VNI_LIGHT (no bear_zone)...")
sig_l = apply_d1(sig_sf, d1_mask_vniproxy)
sig_l = apply_universal_svtight(sig_l, max_days=60)
sig_l = apply_overheat_vniproxy(sig_l)
sig_l = attach_proxy_state5(sig_l)
nav_vni_light = run_sim(sig_l, proxy_state_map, {3: 0.7}, "V_VNI_LIGHT")

results = {"V_PROD": nav_prod, "V_VNI": nav_vni, "V_VNI_NO_ETF": nav_vni_noetf,
           "V_VNI_DEP": nav_vni_dep, "V_VNI_LIGHT": nav_vni_light}

# B&H
bh_df = pd.DataFrame({"time": list(vn30_underlying.keys()), "Close": list(vn30_underlying.values())})
bh_df = bh_df.sort_values("time").reset_index(drop=True)
bh_df["nav"] = BOOK_NAV * bh_df["Close"] / bh_df["Close"].iloc[0]
results["B&H"] = bh_df.set_index("time")["nav"]

# ─── Summary ─────────────────────────────────────────────────────────────
print("\n"+"="*100)
print("  RESULTS — VNI-PROXY BA v11 (state-machine-independent)")
print("="*100)
print(f"\n  {'Variant':<14} {'Final':>9} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>7} {'Calmar':>7} {'ΔvsPROD':>9}")
m_prod = metrics(results["V_PROD"])
print(f"  {'V_PROD':<14} {m_prod['final']:>8.2f}B {m_prod['cagr']:>+6.2f}% {m_prod['sharpe']:>7.2f} {m_prod['maxdd']:>+6.1f}% {m_prod['calmar']:>7.2f} {'baseline':>9}")
for name in ["V_VNI","V_VNI_NO_ETF","V_VNI_DEP","V_VNI_LIGHT","B&H"]:
    if results.get(name) is None: continue
    m = metrics(results[name])
    d = m['cagr'] - m_prod['cagr']
    print(f"  {name:<14} {m['final']:>8.2f}B {m['cagr']:>+6.2f}% {m['sharpe']:>7.2f} {m['maxdd']:>+6.1f}% {m['calmar']:>7.2f} {d:>+6.2f}pp")

# IS/OOS
print("\n  IS 2014-2019 vs OOS 2020-2026:")
for label, sd, ed in [("IS 14-19","2014-01-01","2019-12-31"), ("OOS 20-26","2020-01-01","2026-05-15")]:
    print(f"\n  [{label}]")
    m_prod_p = metrics(results["V_PROD"].loc[sd:ed])
    print(f"  {'V_PROD':<14} CAGR={m_prod_p['cagr']:>+.2f}%")
    for name in ["V_VNI","V_VNI_NO_ETF","V_VNI_DEP","V_VNI_LIGHT","B&H"]:
        if results.get(name) is None: continue
        sub = results[name].loc[sd:ed]
        m = metrics(sub)
        d = m['cagr'] - m_prod_p['cagr']
        print(f"  {name:<14} CAGR={m['cagr']:>+.2f}% Sh={m['sharpe']:.2f} DD={m['maxdd']:+.1f}% Δ={d:+.2f}pp")

# Save
combined = pd.DataFrame({n: nav for n, nav in results.items() if nav is not None})
combined.to_csv(os.path.join(WORKDIR, "data/vni_proxy_progression.csv"))
print("\n  Saved -> data/vni_proxy_progression.csv")
