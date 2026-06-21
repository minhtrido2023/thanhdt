# -*- coding: utf-8 -*-
"""
cross_test_state_filter.py
==========================
Cross-test BA v11: state series × filter config.

States:    TQ34b, DT_10_25_25 (best DT)
Filters:   V_PROD (current), C3_cons (modest), C2_no_svt (aggressive)
Matrix:    2 × 3 = 6 combos

Question: does best filter tune cross-multiply with best state tune?
  - If TQ34b + C2 still wins, state-machine optimization is irrelevant
  - If DT + C2 wins more, they stack additively
  - If DT + C2 underperforms TQ34b + C2, they conflict (state-machine tuned-for-PROD-filters)
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

STATE_CSVS = {
    "TQ34b":       "vnindex_5state_tam_quan_v3_4b_full_history.csv",
    "DT_10_25_25": "vnindex_5state_dt_10_25_25.csv",
}

FILTER_CFG = {
    "V_PROD":   dict(svt={1:30,2:60,3:60},   bear=(1,2), oh=dict(ma200_thr=1.30, rsi_thr=0.75, oh_states=(5,)),    etf={3:0.7}),
    "C3_cons":  dict(svt={1:30,2:60,3:90},   bear=(1,2), oh=dict(ma200_thr=1.30, rsi_thr=0.75, oh_states=(5,)),    etf={2:0.5, 3:0.7}),
    "C2_no_svt":dict(svt=None,               bear=(1,2), oh=dict(ma200_thr=1.25, rsi_thr=0.70, oh_states=(4,5)),  etf={2:0.5, 3:0.7}),
}

print("="*100)
print("  CROSS-TEST: state × filter config (2 × 3 = 6 combos)")
print("="*100)

# ─── Common data load ────────────────────────────────────────────────────
print("\n[1] Loading...")
with open("ba_v11_unified_12y_sig.pkl","rb") as f: sig_canon = pickle.load(f)
sig_canon["time"] = pd.to_datetime(sig_canon["time"])
sig_canon = sig_canon[(sig_canon["time"]>=START_B) & (sig_canon["time"]<=END_B)].copy()

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

vni_full = bq(f"""SELECT t.time, t.Close, t.MA50, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()
LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# ─── D1 once (BQ canonical state, applies to both state series) ─────────
print("[2] D1 RE_BACKLOG query...")
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
d1_mask = (d1["adv_yoy"].notna() & (d1["adv_yoy"]>0.5) & d1["fa_tier"].isin(["C","D"])
           & d1["state5"].isin([3,4,5])
           & ((d1["np_yoy"].fillna(-99)>0) | (d1["rev_yoy"].fillna(-99)>0)))
d1_q = d1.loc[d1_mask,["ticker","time"]].assign(_d1_ok=True)
sig_canon = sig_canon.merge(d1_q, on=["ticker","time"], how="left")
omask = sig_canon["_d1_ok"].fillna(False) & (sig_canon["ta"]>=120)
sig_canon.loc[omask,"play_type"] = "RE_BACKLOG_BUY"
sig_canon = sig_canon.drop(columns=["_d1_ok"])

# ─── State loaders ───────────────────────────────────────────────────────
def load_state(csv_path):
    sdf = pd.read_csv(csv_path)
    sdf["time"] = pd.to_datetime(sdf["time"])
    sdf = sdf[(sdf["time"]>=START_B) & (sdf["time"]<=END_B)][["time","state"]]
    sbd = dict(zip(sdf["time"], sdf["state"]))
    sff = {}; last = None
    for d in vni_dates_B:
        s = sbd.get(d)
        if s is not None: last = s
        sff[d] = last
    return sdf, sff

state_data = {name: load_state(csv) for name, csv in STATE_CSVS.items()}

# ─── Filter functions ────────────────────────────────────────────────────
def apply_sv_tight(sig, days_by_state, sff):
    """Use the CURRENT state series for SV_TIGHT (state-aware filter)."""
    if days_by_state is None: return sig.copy()
    sig = sig.copy()
    if "state5" in sig.columns: sig = sig.drop(columns=["state5"])
    sss = pd.DataFrame({"time": list(sff.keys()), "state5": list(sff.values())})
    sig = sig.merge(sss, on="time", how="left")
    def keep(row):
        s = row.get("state5"); days = row.get("days_since_release")
        if pd.isna(s): return True
        s = int(s)
        if s in (4,5): return True
        thr = days_by_state.get(s)
        if thr is None: return True
        return pd.notna(days) and days <= thr
    mb_buy = sig["play_type"].isin(BUY_TIERS_V11)
    keep_mask = (~mb_buy) | sig.apply(keep, axis=1)
    return sig[keep_mask].copy()

def apply_avoid_bear(sig, bear_states, sff):
    """Use current state series for AVOID_bear."""
    sig = sig.copy()
    ss = pd.DataFrame({"time": list(sff.keys()), "_st": list(sff.values())})
    sig = sig.merge(ss, on="time", how="left")
    block = sig["_st"].isin(bear_states) & sig["play_type"].isin(BUY_TIERS_V11)
    sig.loc[block, "play_type"] = "AVOID_bear"
    return sig.drop(columns=["_st"])

def apply_overheat(sig, sdf, ma200_thr=1.30, rsi_thr=0.75, oh_states=(5,)):
    v = vni_full.merge(sdf, on="time", how="left"); v["state"] = v["state"].ffill()
    cond_price = v["Close"]/v["MA200"] > ma200_thr
    cond_state = v["state"].isin(oh_states)
    cond_rsi   = v["D_RSI"] > rsi_thr
    v["overheat"] = cond_price & (cond_state | cond_rsi)
    oh = set(v[v["overheat"]]["time"])
    sig = sig.copy()
    sig.loc[sig["time"].isin(oh) & sig["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"
    return sig

def run_sim(sig, cash_etf, sff, label):
    nav, _ = simulate(sig, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=MAX_POS, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        sector_cap_exempt_tiers=SECTOR_CAP_EXEMPT, tier_weights=TIER_WEIGHTS_V11,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sff,
        cash_etf_states=cash_etf, vn30_underlying=vn30_underlying,
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

def run_combo(state_name, filter_name):
    sdf, sff = state_data[state_name]
    cfg = FILTER_CFG[filter_name]
    sig = apply_avoid_bear(sig_canon, cfg["bear"], sff)
    sig = apply_sv_tight(sig, cfg["svt"], sff)
    sig = apply_overheat(sig, sdf, **cfg["oh"])
    return run_sim(sig, cfg["etf"], sff, f"{state_name}+{filter_name}")

# ─── Run 6 combos ────────────────────────────────────────────────────────
print("\n[3] Run 2×3 matrix...")
results = {}
for sn in STATE_CSVS:
    for fn in FILTER_CFG:
        lbl = f"{sn}+{fn}"
        print(f"  {lbl}...")
        results[lbl] = run_combo(sn, fn)

# B&H
bh_df = pd.DataFrame({"time": list(vn30_underlying.keys()), "Close": list(vn30_underlying.values())})
bh_df = bh_df.sort_values("time").reset_index(drop=True)
bh_df["nav"] = BOOK_NAV * bh_df["Close"] / bh_df["Close"].iloc[0]
results["B&H"] = bh_df.set_index("time")["nav"]

# ─── Summary ─────────────────────────────────────────────────────────────
print("\n" + "="*100)
print("  RESULTS — state × filter combinations")
print("="*100)

# Pivot table
def get_metrics_3p(nav):
    return {
        "full": metrics(nav),
        "is":   metrics(nav.loc["2014-01-01":"2019-12-31"]),
        "oos":  metrics(nav.loc["2020-01-01":"2026-05-15"]),
    }

m_base = get_metrics_3p(results["TQ34b+V_PROD"])

print(f"\n  {'Combo':<24} {'Full':>8} {'IS':>8} {'OOS':>8} {'ΔFull':>8} {'ΔIS':>8} {'ΔOOS':>8} {'DD_F':>7} {'Sh_F':>5}")
for name in ["TQ34b+V_PROD","TQ34b+C3_cons","TQ34b+C2_no_svt",
             "DT_10_25_25+V_PROD","DT_10_25_25+C3_cons","DT_10_25_25+C2_no_svt"]:
    nav = results[name]
    m = get_metrics_3p(nav)
    d_full = m["full"]["cagr"] - m_base["full"]["cagr"]
    d_is   = m["is"]["cagr"]   - m_base["is"]["cagr"]
    d_oos  = m["oos"]["cagr"]  - m_base["oos"]["cagr"]
    star = " ⭐" if (d_oos > 0 and d_full > 0 and m["full"]["maxdd"] >= -23) else ""
    print(f"  {name:<24} {m['full']['cagr']:>+6.2f}% {m['is']['cagr']:>+6.2f}% {m['oos']['cagr']:>+6.2f}% "
          f"{d_full:>+6.2f}pp {d_is:>+6.2f}pp {d_oos:>+6.2f}pp {m['full']['maxdd']:>+6.1f}% {m['full']['sharpe']:>5.2f}{star}")

# B&H reference
m_bh = metrics(results["B&H"])
print(f"  {'B&H':<24} {m_bh['cagr']:>+6.2f}% {'-':>7} {'-':>7} {'-':>7} {'-':>7} {'-':>7} {m_bh['maxdd']:>+6.1f}% {m_bh['sharpe']:>5.2f}")

# Sub-period breakdown
print("\n" + "="*100)
print("  SUB-PERIOD CAGR (4-year windows)")
print("="*100)
periods = [("14-17","2014-01-01","2017-12-31"), ("18-19","2018-01-01","2019-12-31"),
           ("20-22","2020-01-01","2022-12-31"), ("23-26","2023-01-01","2026-05-15")]
print(f"\n  {'Combo':<24}", end="")
for p,_,_ in periods: print(f"{p:>8}", end="")
print()
for name in ["TQ34b+V_PROD","TQ34b+C3_cons","TQ34b+C2_no_svt",
             "DT_10_25_25+V_PROD","DT_10_25_25+C3_cons","DT_10_25_25+C2_no_svt"]:
    print(f"  {name:<24}", end="")
    for _, sd, ed in periods:
        sub = results[name].loc[sd:ed]
        m = metrics(sub)
        print(f"{m['cagr']:>+6.2f}%", end="  ")
    print()

# Save NAVs
combined = pd.DataFrame({n: nav for n, nav in results.items()})
combined.to_csv(os.path.join(WORKDIR, "data/cross_test_state_filter_nav.csv"))
print(f"\n  Saved -> data/cross_test_state_filter_nav.csv")

# ─── Global winner search ────────────────────────────────────────────────
print("\n" + "="*100)
print("  GLOBAL OPTIMUM")
print("="*100)
scores = []
for name in ["TQ34b+V_PROD","TQ34b+C3_cons","TQ34b+C2_no_svt",
             "DT_10_25_25+V_PROD","DT_10_25_25+C3_cons","DT_10_25_25+C2_no_svt"]:
    m = get_metrics_3p(results[name])
    scores.append({"name":name, "full":m["full"]["cagr"], "is":m["is"]["cagr"], "oos":m["oos"]["cagr"],
                   "dd": m["full"]["maxdd"], "sh": m["full"]["sharpe"],
                   "min_period": min(m["is"]["cagr"], m["oos"]["cagr"])})

df_scores = pd.DataFrame(scores)
print("\n  By Full CAGR (top-3):")
for _, r in df_scores.nlargest(3, "full").iterrows():
    print(f"    {r['name']:<22}  Full={r['full']:+.2f}%  IS={r['is']:+.2f}%  OOS={r['oos']:+.2f}%  DD={r['dd']:+.1f}%  Sh={r['sh']:.2f}")
print("\n  By OOS CAGR (top-3):")
for _, r in df_scores.nlargest(3, "oos").iterrows():
    print(f"    {r['name']:<22}  Full={r['full']:+.2f}%  IS={r['is']:+.2f}%  OOS={r['oos']:+.2f}%  DD={r['dd']:+.1f}%  Sh={r['sh']:.2f}")
print("\n  By MIN(IS, OOS) — most robust (top-3):")
for _, r in df_scores.nlargest(3, "min_period").iterrows():
    print(f"    {r['name']:<22}  Full={r['full']:+.2f}%  IS={r['is']:+.2f}%  OOS={r['oos']:+.2f}%  DD={r['dd']:+.1f}%  Sh={r['sh']:.2f}")
