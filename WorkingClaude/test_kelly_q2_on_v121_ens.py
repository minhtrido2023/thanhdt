# -*- coding: utf-8 -*-
"""Test Q2_ONLY effect on V11 + V12.1 architectures (TRUE production ETF schedule).

Critical config correction (2026-05-23 evening):
  Production sim_v11_transparent uses `cash_etf_states={3: 0.7}` (NEUTRAL only).
  All states 1/2/4/5 have NO ETF (default 0). My earlier Q2 test used a fuller
  schedule {1:0, 2:0.2, 3:0.7, 4:1.0, 5:1.3} which over-allocated to ETF in
  BULL/EX-BULL. Real production Q2_ONLY = change {3:0.7} -> {3:1.0} only.

Architectures tested:
  V11   = BAL @ 25B + VN30 @ 25B   (both with ETF)
  V12.1 = BAL @ 25B + LAGGED V12.1 @ 25B (LAGGED has no ETF; only BAL affected)

For each architecture, run two scenarios:
  BASELINE: ETF_STATES = {3: 0.7}  (current production)
  Q2_ONLY : ETF_STATES = {3: 1.0}  (proposed Q2 change)

V121_ENS in production switches VN30 <-> LAGGED based on M1+M3r signal. We don't
ensemble here — instead we measure Q2 effect bounds:
  - Max effect: V11 (BAL+VN30, ETF on both legs)
  - Min effect: V12.1 (BAL+LAGGED, ETF on BAL only)
  - Ensemble lies between, weighted by signal occupancy
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, io, re, pickle
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
OUTDIR = os.path.join(WORKDIR, "kelly_q2_v121_out")
os.makedirs(OUTDIR, exist_ok=True)
from simulate_holistic_nav import simulate, bq

# --- Config ------------------------------------------------------------------
START_B = "2014-01-01"; END_B = "2026-05-15"
TOTAL_NAV = 50_000_000_000; BOOK_NAV = TOTAL_NAV / 2
DEPOSIT = 0.0; BORROW = 0.10
ETF_BASELINE = {3: 0.7}   # current production
ETF_Q2_ONLY  = {3: 1.0}   # proposed
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"]
BUY_TIERS_V11 = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
                  "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","S_PRO"}
STATE_CSV = "data/vnindex_5state_tam_quan_v3_4b_full_history.csv"

print("="*100)
print("  KELLY Q2_ONLY EFFECT — V11 vs V12.1 architectures (TRUE prod ETF schedule)")
print(f"  Period: {START_B} -> {END_B} | NAV: 50B (25B/25B)")
print(f"  BASELINE ETF: {ETF_BASELINE} | Q2_ONLY ETF: {ETF_Q2_ONLY}")
print("="*100)

# --- Load data ---------------------------------------------------------------
print("\n[1] Loading signals, prices, state...")
with open("data/ba_v11_unified_12y_sig.pkl", "rb") as f: sig_B = pickle.load(f)
sig_B["time"] = pd.to_datetime(sig_B["time"])
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

vni_full = bq(f"""SELECT t.time, t.Close, t.MA200, t.D_RSI FROM tav2_bq.ticker AS t
WHERE t.ticker='VNINDEX' AND t.time BETWEEN DATE '{START_B}' AND DATE '{END_B}' ORDER BY t.time""")
vni_full["time"] = pd.to_datetime(vni_full["time"])

state_df = pd.read_csv(STATE_CSV)
state_df["time"] = pd.to_datetime(state_df["time"])
state_df = state_df[(state_df["time"]>=START_B) & (state_df["time"]<=END_B)][["time","state"]]
sbd = dict(zip(state_df["time"], state_df["state"]))
sbd_ff = {}; last = None
for d in vni_dates_B:
    s = sbd.get(d)
    if s is not None: last = s
    sbd_ff[d] = last

v = vni_full.merge(state_df, on="time", how="left"); v["state"] = v["state"].ffill()
v["overheat"] = ((v["Close"]/v["MA200"]>1.30) & ((v["state"]==5) | (v["D_RSI"]>0.75)))
overheat_dates = set(v[v["overheat"]]["time"])
sig_v = sig_B.copy()
sig_v.loc[sig_v["time"].isin(overheat_dates) & sig_v["play_type"].isin(BUY_TIERS_V11), "play_type"] = "AVOID_overheated"

top30 = set(bq("""SELECT t.ticker FROM tav2_bq.ticker AS t
WHERE t.time BETWEEN DATE '2020-01-01' AND DATE '2025-01-01'
AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
GROUP BY t.ticker ORDER BY AVG(t.Volume_3M_P50 * t.Close) DESC LIMIT 30""")["ticker"])
sec_map = bq("""SELECT DISTINCT t.ticker, CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS s
                FROM tav2_bq.ticker AS t WHERE t.ICB_Code IS NOT NULL""").set_index("ticker")["s"].to_dict()

LIQ = {"liquidity_volume_pct":0.20,"max_fill_days":5,
       "liquidity_lookup":liq_map_B,"exit_slippage_tiered":True}

# --- Run BAL leg twice (baseline ETF vs Q2 ETF) -----------------------------
def run_bal(etf_states, label):
    print(f"\n[BAL] etf_states={etf_states}  ({label})")
    nav, _ = simulate(sig_v, prices_B, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        **LIQ, name=f"BAL_{label}")
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]

nav_bal_base = run_bal(ETF_BASELINE, "base")
print(f"  BAL base final: {nav_bal_base.iloc[-1]/1e9:.2f}B")
nav_bal_q2   = run_bal(ETF_Q2_ONLY,  "q2")
print(f"  BAL q2 final:   {nav_bal_q2.iloc[-1]/1e9:.2f}B")

# --- Run VN30 leg twice -----------------------------------------------------
def run_vn30(etf_states, label):
    print(f"\n[VN30] etf_states={etf_states}  ({label})")
    sig30 = sig_v[sig_v["ticker"].isin(top30)].copy()
    prices30 = {tk: prices_B[tk] for tk in top30 if tk in prices_B}
    liq30 = {k:v for k,v in liq_map_B.items() if k[0] in top30}
    LIQ30 = {**LIQ, "liquidity_lookup":liq30}
    nav, _ = simulate(sig30, prices30, vni_dates_B,
        allowed_tiers=TIER_BAL, max_positions=10, hold_days=45, stop_loss=-0.20,
        min_hold=2, slippage=0.001, init_nav=BOOK_NAV,
        ticker_sector_map=sec_map,
        deposit_annual=DEPOSIT, borrow_annual=BORROW, state_by_date=sbd_ff,
        cash_etf_states=etf_states, vn30_underlying=vn30_underlying,
        **LIQ30, name=f"VN30_{label}")
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]

nav_vn30_base = run_vn30(ETF_BASELINE, "base")
print(f"  VN30 base final: {nav_vn30_base.iloc[-1]/1e9:.2f}B")
nav_vn30_q2   = run_vn30(ETF_Q2_ONLY,  "q2")
print(f"  VN30 q2 final:   {nav_vn30_q2.iloc[-1]/1e9:.2f}B")

# --- Run LAGGED V12.1 leg ONCE (no ETF dependency) --------------------------
print("\n[LAGGED V12.1] (state-independent, no ETF, run once)")
with open("data/earnings_px.pkl","rb") as f: px_data = pickle.load(f)
px_data["time"] = pd.to_datetime(px_data["time"])
px_close = px_data.pivot_table(index="time", columns="ticker", values="Close", aggfunc="first").sort_index().ffill(limit=5)
master_idx = pd.DatetimeIndex(px_close.index).as_unit("ns")
px_close.index = master_idx
all_dates = np.array(master_idx)
with open("data/lagged_pos_ov.pkl","rb") as f: ov = pickle.load(f)
ov["time"] = pd.to_datetime(ov["time"])

def run_lagged_book(init_nav, use_s2_sizing, sw=pd.Timestamp(START_B), ew=pd.Timestamp(END_B)):
    cash = init_nav; positions = {}; nav_history = []
    HOLD_DAYS = 25
    ov_in = ov[(ov["time"]>=sw) & (ov["time"]<=ew)].copy()
    for _, sig in ov_in.iterrows():
        entry_d = pd.Timestamp(sig["time"]) + pd.Timedelta(days=7)
        # snap to next trading day
        ent_idx = np.searchsorted(all_dates, entry_d.asm8, side="left")
        if ent_idx >= len(all_dates): continue
        entry_d = pd.Timestamp(all_dates[ent_idx])
        exit_idx = ent_idx + HOLD_DAYS
        if exit_idx >= len(all_dates): continue
        exit_d = pd.Timestamp(all_dates[exit_idx])
        if exit_d > ew: continue
        ticker = sig["ticker"]
        if ticker not in px_close.columns: continue
        if pd.isna(px_close.loc[entry_d, ticker]) or pd.isna(px_close.loc[exit_d, ticker]): continue
        pos_pct = 0.08
        if use_s2_sizing and sig.get("surprise_B_MA", 0) > 0.5:
            pos_pct = 0.10
        sig["entry_d"] = entry_d
        sig["exit_d"] = exit_d
        sig["pos_pct"] = pos_pct
    schedule = []
    for _, sig in ov_in.iterrows():
        if "entry_d" not in sig or pd.isna(sig.get("entry_d")): continue
        schedule.append(sig)
    for d in vni_dates_B:
        if d < sw or d > ew: continue
        # close exits
        for pid in list(positions):
            if positions[pid]["exit_d"] == d:
                px_ex = px_close.loc[d, positions[pid]["ticker"]]
                if not pd.isna(px_ex):
                    cash += positions[pid]["shares"] * px_ex * (1 - 0.001)
                del positions[pid]
        # entries today
        for sig in schedule:
            if sig.get("entry_d") != d: continue
            tk = sig["ticker"]
            nav_now = cash + sum(positions[p]["shares"] * px_close.loc[d, positions[p]["ticker"]]
                                  if not pd.isna(px_close.loc[d, positions[p]["ticker"]]) else 0
                                  for p in positions)
            sz = nav_now * sig["pos_pct"]
            if sz > cash * 0.95: sz = cash * 0.95
            if sz < 1_000_000: continue
            px_en = px_close.loc[d, tk]
            if pd.isna(px_en): continue
            shares = sz / (px_en * 1.001)
            cost = shares * px_en * 1.001
            cash -= cost
            pid = f"{tk}_{d.strftime('%Y%m%d')}"
            positions[pid] = {"ticker": tk, "shares": shares, "exit_d": sig["exit_d"]}
        # mark NAV
        pos_mv = sum(positions[p]["shares"] * px_close.loc[d, positions[p]["ticker"]]
                     if not pd.isna(px_close.loc[d, positions[p]["ticker"]]) else 0
                     for p in positions)
        nav_history.append({"time": d, "nav": cash + pos_mv})
    return pd.DataFrame(nav_history).set_index("time")["nav"]

nav_lag_v121 = run_lagged_book(BOOK_NAV, use_s2_sizing=True)
print(f"  LAGGED V12.1 final: {nav_lag_v121.iloc[-1]/1e9:.2f}B")

# --- Build architectures ----------------------------------------------------
common = nav_bal_base.index.intersection(nav_vn30_base.index).intersection(nav_lag_v121.index)
nav_v11_base  = (nav_bal_base.loc[common] + nav_vn30_base.loc[common])
nav_v11_q2    = (nav_bal_q2.loc[common]   + nav_vn30_q2.loc[common])
nav_v121_base = (nav_bal_base.loc[common] + nav_lag_v121.loc[common])
nav_v121_q2   = (nav_bal_q2.loc[common]   + nav_lag_v121.loc[common])  # LAGGED unchanged

# --- Metrics ----------------------------------------------------------------
PERIODS = [
    ("FULL 2014-2026", "2014-01-01", "2026-05-15"),
    ("Pre-OOS 2014-19","2014-01-01", "2019-12-31"),
    ("OOS 2024-2026",  "2024-01-01", "2026-05-15"),
    ("Y2022 CRISIS",   "2022-01-01", "2022-12-31"),
    ("Y2024",          "2024-01-01", "2024-12-31"),
    ("Y2025",          "2025-01-01", "2025-12-31"),
]

def metrics(nav):
    rets = nav.pct_change().dropna()
    yrs = (nav.index[-1] - nav.index[0]).days / 365.25
    spy = len(rets)/yrs if yrs > 0 else 252
    cagr = (nav.iloc[-1]/nav.iloc[0])**(1/yrs) - 1 if yrs > 0 else 0
    sh = rets.mean()/rets.std() * np.sqrt(spy) if rets.std() > 0 else 0
    peak = nav.cummax(); dd_s = (nav - peak)/peak
    dd = dd_s.min()
    cal = cagr/abs(dd) if dd < 0 else 0
    return {"CAGR":cagr*100, "Sharpe":sh, "MaxDD":dd*100, "Calmar":cal,
            "Wealth": nav.iloc[-1]/nav.iloc[0]}

print("\n" + "="*120)
print("  Q2_ONLY EFFECT — V11 vs V12.1 architectures")
print("="*120)
arms = [("V11 base", nav_v11_base), ("V11 Q2", nav_v11_q2),
        ("V12.1 base", nav_v121_base), ("V12.1 Q2", nav_v121_q2)]

results = {}
for label, ps, pe in PERIODS:
    ps_ts, pe_ts = pd.Timestamp(ps), pd.Timestamp(pe)
    print(f"\n  --- {label} ---")
    print(f"  {'Arm':<14} {'CAGR':>8} {'Sharpe':>7} {'MaxDD':>8} {'Calmar':>7} {'Wealth':>7}")
    res = {}
    for arm, nav in arms:
        sub = nav[(nav.index >= ps_ts) & (nav.index <= pe_ts)]
        if len(sub) < 30: continue
        m = metrics(sub)
        res[arm] = m
        print(f"  {arm:<14} {m['CAGR']:>+7.2f}% {m['Sharpe']:>+7.2f} {m['MaxDD']:>+7.2f}% "
              f"{m['Calmar']:>+7.2f} {m['Wealth']:>+6.2f}x")
    # Compute Q2 deltas for each arch
    if "V11 base" in res and "V11 Q2" in res:
        dC = res["V11 Q2"]["CAGR"] - res["V11 base"]["CAGR"]
        dS = res["V11 Q2"]["Sharpe"] - res["V11 base"]["Sharpe"]
        dD = res["V11 Q2"]["MaxDD"] - res["V11 base"]["MaxDD"]
        print(f"  V11 Q2-base  : dCAGR={dC:+.2f}pp dSharpe={dS:+.2f} dMaxDD={dD:+.2f}pp")
    if "V12.1 base" in res and "V12.1 Q2" in res:
        dC = res["V12.1 Q2"]["CAGR"] - res["V12.1 base"]["CAGR"]
        dS = res["V12.1 Q2"]["Sharpe"] - res["V12.1 base"]["Sharpe"]
        dD = res["V12.1 Q2"]["MaxDD"] - res["V12.1 base"]["MaxDD"]
        print(f"  V12.1 Q2-base: dCAGR={dC:+.2f}pp dSharpe={dS:+.2f} dMaxDD={dD:+.2f}pp")
    results[label] = res

# --- Write markdown ---------------------------------------------------------
md = []
md.append("# Kelly Q2_ONLY effect on V11 vs V12.1 architectures (TRUE prod ETF)\n")
md.append(f"**Date**: 2026-05-23")
md.append(f"**Period**: {START_B} -> {END_B} | NAV 50B (25B/25B split)")
md.append(f"**State source**: TQ v3.4b (`{STATE_CSV}`)")
md.append(f"**BASELINE ETF**: `{ETF_BASELINE}` (current production)")
md.append(f"**Q2_ONLY ETF**: `{ETF_Q2_ONLY}` (proposed)\n")
md.append("## Note on V121_ENS\n")
md.append("V121_ENS in production switches VN30 <-> LAGGED based on M1+M3r AND-HOLD signal.")
md.append("This script doesn't ensemble; instead it bounds Q2 effect:")
md.append("- **Max Q2 impact**: V11 architecture (BAL+VN30 — both have ETF overlay)")
md.append("- **Min Q2 impact**: V12.1 architecture (BAL+LAGGED — only BAL has ETF)")
md.append("Ensemble Q2 effect lies between, weighted by signal occupancy.\n")
md.append("## Results per window\n")
md.append("| Period | Arm | CAGR | Sharpe | MaxDD | Calmar | Wealth |")
md.append("|---|---|---:|---:|---:|---:|---:|")
for label, res in results.items():
    for arm in ["V11 base","V11 Q2","V12.1 base","V12.1 Q2"]:
        if arm not in res: continue
        m = res[arm]
        md.append(f"| {label} | {arm} | {m['CAGR']:+.2f}% | {m['Sharpe']:+.2f} | "
                  f"{m['MaxDD']:+.2f}% | {m['Calmar']:+.2f} | {m['Wealth']:.2f}x |")
md.append("\n## Q2 deltas per architecture per window\n")
md.append("| Period | Arch | dCAGR | dSharpe | dMaxDD |")
md.append("|---|---|---:|---:|---:|")
for label, res in results.items():
    if "V11 base" in res and "V11 Q2" in res:
        dC = res["V11 Q2"]["CAGR"] - res["V11 base"]["CAGR"]
        dS = res["V11 Q2"]["Sharpe"] - res["V11 base"]["Sharpe"]
        dD = res["V11 Q2"]["MaxDD"] - res["V11 base"]["MaxDD"]
        md.append(f"| {label} | V11 | {dC:+.2f}pp | {dS:+.2f} | {dD:+.2f}pp |")
    if "V12.1 base" in res and "V12.1 Q2" in res:
        dC = res["V12.1 Q2"]["CAGR"] - res["V12.1 base"]["CAGR"]
        dS = res["V12.1 Q2"]["Sharpe"] - res["V12.1 base"]["Sharpe"]
        dD = res["V12.1 Q2"]["MaxDD"] - res["V12.1 base"]["MaxDD"]
        md.append(f"| {label} | V12.1 | {dC:+.2f}pp | {dS:+.2f} | {dD:+.2f}pp |")

with open(os.path.join(WORKDIR, "kelly_q2_v121_ens_results.md"), "w", encoding="utf-8") as f:
    f.write("\n".join(md))
print(f"\nWrote: kelly_q2_v121_ens_results.md")
print("DONE.")
