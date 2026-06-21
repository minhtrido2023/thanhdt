# -*- coding: utf-8 -*-
"""
test_v5_macro_integrated.py
===========================
Step (b): does the consolidated MACRO layer (SBV money + US panic, fused, with
bull-aware bypass + confirmed easing) convert to REAL ALPHA inside the Kelly
stock book (V5) under leverage — or is it only a pure-index effect?

Method: identical validated harness to test_v5_dt4gate_integrated.py, but adds
the macro-adjusted state series `vnindex_5state_dt4_macro.csv` (produced by
sim_dt4g_macro_overlay.py: DT4 state + macro cap/floor). Compares, for both
KELLY (V5) and BASE (V1) ETF configs:
    DT_4gate            (no macro)
    DT_4gate + MACRO    (cap/floor injected into the state V5 consumes)

Macro state differs from DT4 on ~106/3089 modern days (95 de-risk, 11 re-risk),
so this isolates whether those interventions help under leverage. 2014-2026.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, pickle, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import simulate, bq

START_B, END_B = "2014-01-01", "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT, BORROW = 0.0, 0.10
ETF_BASE, ETF_KELLY = {3: 0.7}, {3: 1.0}
SECTOR_CAP_EXEMPT = {"RE_BACKLOG_BUY"}
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS_V11 = {t: 0.10 for t in TIER_BAL}
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                 "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO","RE_BACKLOG_BUY"}
MAX_POS = 12
STATES = {"DT_4gate": "vnindex_5state_dt_4gate.csv", "DT4_MACRO": "vnindex_5state_dt4_macro.csv"}
# cost-stress knobs (env): SLIP per-trade slippage, FRICT ETF rebalance friction
SLIP = float(os.environ.get("SLIP", "0.001"))
FRICT = float(os.environ.get("FRICT", "0.0015"))

print("=" * 96)
print(f"  V5/V1 INTEGRATED — DT_4gate vs DT_4gate+MACRO  (slippage={SLIP:.4f}, ETF_friction={FRICT:.4f})")
print("=" * 96)
print("\n[1] Load signals + prices...")
with open("ba_v11_unified_12y_sig.pkl", "rb") as f: sig_canon = pickle.load(f)
sig_canon["time"] = pd.to_datetime(sig_canon["time"])
sig_canon = sig_canon[(sig_canon["time"] >= START_B) & (sig_canon["time"] <= END_B)].copy()
with open("sim_v11_for_analyzer.py", "r", encoding="utf-8") as f: _c = f.read()
VNI_QUERY_UNIFIED = re.search(r'^VNI_QUERY_UNIFIED\s*=\s*"""(.+?)"""', _c, re.MULTILINE | re.DOTALL).group(1)
prices_B = {tk: dict(zip(g["time"], g["Close"])) for tk, g in sig_canon.groupby("ticker")}
liq_map_B = {(r["ticker"], r["time"]): r["liq"] for _, r in sig_canon.iterrows()}
vni_B = bq(VNI_QUERY_UNIFIED.format(start=START_B, end=END_B)); vni_B["time"] = pd.to_datetime(vni_B["time"])
vni_dates_B = sorted(vni_B["time"].unique())
vn30_underlying = dict(zip(vni_B["time"], vni_B["Close"]))
opens_df = bq(f"""SELECT t.ticker,t.time,t.Open AS open_price FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2) AND t.Open IS NOT NULL""")
opens_df["time"] = pd.to_datetime(opens_df["time"])
open_prices = {tk: dict(zip(g["time"], g["open_price"])) for tk, g in opens_df.groupby("ticker")}
vni_full = bq(f"""SELECT t.time,t.Close,t.MA200,t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])
top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50*t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("SELECT DISTINCT t.ticker,CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct": 0.20, "max_fill_days": 5, "liquidity_lookup": liq_map_B, "exit_slippage_tiered": True}

print("[2] D1 RE_BACKLOG...")
d1 = bq(f"""WITH adv_dated AS (SELECT f.ticker,f.time AS f_time,SAFE_DIVIDE(f.AdvCust_P0,NULLIF(f.AdvCust_P4,0))-1 AS adv_yoy,
  LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.ticker_financial AS f),
fa_dated AS (SELECT f.ticker,f.time AS f_time,f.tier AS fa_tier,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time FROM tav2_bq.fa_ratings AS f),
fin_dated AS (SELECT f.ticker,f.time AS fin_time,f.Revenue_YoY_P0,LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time FROM tav2_bq.ticker_financial AS f)
SELECT t.ticker,t.time,fa.fa_tier,SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1 AS np_yoy,fin.Revenue_YoY_P0 AS rev_yoy,adv.adv_yoy,s5.state AS state5
FROM tav2_bq.ticker AS t LEFT JOIN tav2_bq.vnindex_5state_tam_quan_v34b_clean AS s5 ON s5.time=t.time
LEFT JOIN fa_dated AS fa ON fa.ticker=t.ticker AND t.time>=fa.f_time AND (fa.next_f_time IS NULL OR t.time<fa.next_f_time)
LEFT JOIN fin_dated AS fin ON fin.ticker=t.ticker AND t.time>=fin.fin_time AND (fin.next_fin_time IS NULL OR t.time<fin.next_fin_time)
LEFT JOIN adv_dated AS adv ON adv.ticker=t.ticker AND t.time>=adv.f_time AND (adv.next_f_time IS NULL OR t.time<adv.next_f_time)
WHERE t.ICB_Code=8633 AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)""")
d1["time"] = pd.to_datetime(d1["time"])
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"] > 0.5) & d1["fa_tier"].isin(["C", "D"]) & d1["state5"].isin([3, 4, 5]) & ((d1["np_yoy"].fillna(-99) > 0) | (d1["rev_yoy"].fillna(-99) > 0)))
sig_canon = sig_canon.merge(d1.loc[d1_mask, ["ticker", "time"]].assign(_d1_ok=True), on=["ticker", "time"], how="left")
omask = sig_canon["_d1_ok"].fillna(False) & (sig_canon["ta"] >= 120)
sig_canon.loc[omask, "play_type"] = "RE_BACKLOG_BUY"; sig_canon = sig_canon.drop(columns=["_d1_ok"])

def load_state(csv):
    sdf = pd.read_csv(csv); sdf["time"] = pd.to_datetime(sdf["time"])
    sdf = sdf[(sdf["time"] >= START_B) & (sdf["time"] <= END_B)][["time", "state"]]
    sbd = dict(zip(sdf["time"], sdf["state"])); sff = {}; last = None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        sff[d] = last
    return sdf, sff
state_data = {name: load_state(csv) for name, csv in STATES.items()}

def apply_sv_tight(sig, sff):
    dbs = {1: 30, 2: 60, 3: 60}; sig = sig.copy()
    if "state5" in sig.columns: sig = sig.drop(columns=["state5"])
    sig = sig.merge(pd.DataFrame({"time": list(sff.keys()), "state5": list(sff.values())}), on="time", how="left")
    def keep(row):
        s = row.get("state5"); days = row.get("days_since_release")
        if pd.isna(s): return True
        s = int(s)
        if s in (4, 5): return True
        thr = dbs.get(s)
        return True if thr is None else (pd.notna(days) and days <= thr)
    mb = sig["play_type"].isin(BUY_TIERS_V11)
    return sig[(~mb) | sig.apply(keep, axis=1)].copy()

def apply_overheat(sig, sdf):
    v = vni_full.merge(sdf, on="time", how="left"); v["state"] = v["state"].ffill()
    oh = set(v[(v["Close"] / v["MA200"] > 1.30) & ((v["state"] == 5) | (v["D_RSI"] > 0.75))]["time"])
    sig = sig.copy()
    sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return sig

def run_leg(sig, sff, cash_etf, universe, label):
    s = sig if universe is None else sig[sig["ticker"].isin(universe)].copy()
    pr = prices_B if universe is None else {tk: prices_B[tk] for tk in universe if tk in prices_B}
    lq = liq_map_B if universe is None else {k: v for k, v in liq_map_B.items() if k[0] in universe}
    extra = dict(sector_limit_per_sector={8: 4}, sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT) if universe is None else {}
    nav, _ = simulate(s, pr, vni_dates_B, allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45,
        stop_loss=-0.20, min_hold=2, slippage=SLIP, init_nav=BOOK_NAV, ticker_sector_map=sec_map,
        tier_weights=TIER_WEIGHTS_V11, deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=cash_etf, vn30_underlying=vn30_underlying, etf_mgmt_fee_annual=0.0,
        etf_tracking_drag_annual=0.0, etf_rebalance_friction=FRICT, open_prices=open_prices,
        t1_open_exec=True, **{**LIQ, "liquidity_lookup": lq}, **extra, name=label)
    nav["time"] = pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]

def run_v5(state_name, cash_etf):
    sdf, sff = state_data[state_name]
    sig_v = apply_overheat(apply_sv_tight(sig_canon, sff), sdf)
    nb = run_leg(sig_v, sff, cash_etf, None, f"{state_name}_BAL")
    nv = run_leg(sig_v, sff, cash_etf, top30, f"{state_name}_VN30")
    return nb + nv

print("\n[3] Run combos...")
results = {}
for sn, cfg, lbl in [("DT_4gate", ETF_KELLY, "V5_DT4_KELLY"), ("DT4_MACRO", ETF_KELLY, "V5_DT4MACRO_KELLY"),
                     ("DT_4gate", ETF_BASE, "V1_DT4_BASE"), ("DT4_MACRO", ETF_BASE, "V1_DT4MACRO_BASE")]:
    print(f"  [{lbl}] {sn} + {'KELLY' if cfg==ETF_KELLY else 'BASE'}...")
    results[lbl] = run_v5(sn, cfg)
bh = pd.DataFrame({"time": list(vn30_underlying.keys()), "Close": list(vn30_underlying.values())}).sort_values("time")
bh["nav"] = TOTAL_NAV * bh["Close"] / bh["Close"].iloc[0]; results["B&H"] = bh.set_index("time")["nav"]

def metrics(s):
    init, final = s.iloc[0], s.iloc[-1]; yrs = (s.index[-1] - s.index[0]).days / 365.25
    cagr = (final / init) ** (1 / yrs) - 1; d = s.pct_change().dropna()
    sh = d.mean() / d.std() * np.sqrt(252) if d.std() > 0 else 0
    dd = ((s - s.expanding().max()) / s.expanding().max()).min()
    return dict(final=final / 1e9, cagr=cagr * 100, sharpe=sh, maxdd=dd * 100, calmar=cagr / (-dd) if dd < 0 else 0)

print("\n" + "=" * 96)
print(f"  {'Combo':<20}{'Final':>10}{'CAGR':>8}{'IS14-19':>9}{'OOS20-26':>10}{'DD':>8}{'Sharpe':>8}{'Calmar':>8}")
for n in ["V5_DT4_KELLY", "V5_DT4MACRO_KELLY", "V1_DT4_BASE", "V1_DT4MACRO_BASE", "B&H"]:
    s = results[n]; m = metrics(s)
    mis = metrics(s.loc["2014-01-01":"2019-12-31"]) if n != "B&H" else None
    moos = metrics(s.loc["2020-01-01":"2026-05-15"]) if n != "B&H" else None
    isv = f"{mis['cagr']:>+7.2f}%" if mis else f"{'-':>8}"
    oosv = f"{moos['cagr']:>+8.2f}%" if moos else f"{'-':>9}"
    print(f"  {n:<20}{m['final']:>9.2f}B{m['cagr']:>+7.2f}%{isv}{oosv}{m['maxdd']:>+7.1f}%{m['sharpe']:>8.2f}{m['calmar']:>8.2f}")

def dpp(a, b, lo=None, hi=None):
    na, nb = results[a], results[b]
    if lo: na, nb = na.loc[lo:hi], nb.loc[lo:hi]
    return metrics(na)["cagr"] - metrics(nb)["cagr"]
print("\n  MACRO vs no-macro:")
print(f"  KELLY (V5):  Full {dpp('V5_DT4MACRO_KELLY','V5_DT4_KELLY'):+.2f}pp  IS {dpp('V5_DT4MACRO_KELLY','V5_DT4_KELLY','2014','2019'):+.2f}pp  OOS {dpp('V5_DT4MACRO_KELLY','V5_DT4_KELLY','2020','2026-05-15'):+.2f}pp")
print(f"  BASE  (V1):  Full {dpp('V1_DT4MACRO_BASE','V1_DT4_BASE'):+.2f}pp  IS {dpp('V1_DT4MACRO_BASE','V1_DT4_BASE','2014','2019'):+.2f}pp  OOS {dpp('V1_DT4MACRO_BASE','V1_DT4_BASE','2020','2026-05-15'):+.2f}pp")
periods = [("14-17", "2014-01-01", "2017-12-31"), ("18-19", "2018-01-01", "2019-12-31"),
           ("20-22", "2020-01-01", "2022-12-31"), ("23-26", "2023-01-01", "2026-05-15")]
print("\n  Sub-period CAGR (KELLY):")
print(f"  {'Combo':<20}" + "".join(f"{p:>9}" for p, _, _ in periods))
for n in ["V5_DT4_KELLY", "V5_DT4MACRO_KELLY"]:
    print(f"  {n:<20}" + "".join(f"{metrics(results[n].loc[sd:ed])['cagr']:>+8.2f}%" for _, sd, ed in periods))
pd.DataFrame(results).to_csv(os.path.join(WORKDIR, "data/v5_macro_integrated_nav.csv"))
print("\n  Saved -> data/v5_macro_integrated_nav.csv")
print("DONE.")
