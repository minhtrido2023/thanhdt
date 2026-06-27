#!/usr/bin/env python3
"""
lag_harness_dnpr.py — V2.4 50B harness A/B: baseline LAG vs LAG + d_NPR>=0 filter.
=================================================================================
Faithful clone of pt_v4_full_faithful.py (two real 25B ledgers, Book A BAL +
Book B SWITCHED with the LAGGED earnings-drift schedule). The ONLY change vs the
production harness: the LAG entry schedule is built TWICE —
  Version A (baseline): exact prodspec LAG gate (NP_R>=15 & prior_n_good>=4 & pa_HL3>=5)
  Version B          : same gate PLUS d_NPR >= 0 (drop events with d_NPR<0 or NaN)
d_NPR (earnings acceleration, PIT at Release_Date):
  d_NPR = (NP_P0/NP_P4 - 1) - (NP_P1/NP_P5 - 1)   [denom==0 -> NaN]
Book A (BAL) is IDENTICAL across versions; only Book B's LAG entries change, so
the difference in the 50B total NAV is attributable to the filter.

NOTE: data/earnings_surprise_data.pkl is unreadable under pandas 2.3.3 (2D-datetime
block bug). surprise_B_MA (HI/LO split) AND d_NPR are reconstructed directly from
data/bq_cache/ticker_financial.parquet (NP_P0..P5), merged on (ticker,quarter,Release_Date)
— byte-identical reconstruction of fin's surprise_B_MA, auditable.

Reports total/IS/OOS CAGR, MaxDD, Calmar for both versions. NO production code touched.
Run: python data/lag_harness_dnpr.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

W = r"/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, W)
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate
BOOK = 25_000_000_000
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}

# ── shared data ──────────────────────────────────────────────────────────────
print("[1] Loading shared data...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
sig_b = pickle.load(open(os.path.join(W,"data/ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"] = pd.to_datetime(sig_b["time"])
# clamp to the panel's tradeable calendar (sig pkl can be newer than the panel)
sig_b = sig_b[(sig_b["time"] >= panel["time"].min()) & (sig_b["time"] <= panel["time"].max())].copy()

dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
vni_dates = sorted(panel["time"].unique())
last_st = None
for d in vni_dates:
    if d in state_by_date: last_st = state_by_date[d]
    elif last_st is not None: state_by_date[d] = last_st

vnx = pd.read_csv(os.path.join(W,"data/VNINDEX.csv"), usecols=["time","Close","MA200","D_RSI"], parse_dates=["time"])
vnx = vnx[vnx["time"] >= panel["time"].min()]
etf = pd.read_csv(os.path.join(W,"data","e1vfvn30_daily.csv"), parse_dates=["time"])
vn30_und = pd.Series(etf["Close"].values, index=etf["time"])

def sv_tight_keep(row):
    s, days = row["state5"], row["days_since_release"]
    if pd.isna(s): return True
    s = int(s)
    if s in (4,5): return True
    if s == 1: return pd.notna(days) and days <= 30
    if s in (2,3): return pd.notna(days) and days <= 60
    return True
mb = sig_b["play_type"].isin(BUY_TIERS)
sig_b = sig_b[(~mb) | sig_b.apply(sv_tight_keep, axis=1)].copy()
v = vnx.merge(pd.DataFrame({"time": list(state_by_date.keys()), "st": list(state_by_date.values())}), on="time", how="left")
v["st"] = v["st"].ffill()
oh_dates = set(v[(v["Close"]/v["MA200"] > 1.30) & ((v["st"]==5) | (v["D_RSI"] > 0.75))]["time"])
sig_b.loc[sig_b["time"].isin(oh_dates) & sig_b["play_type"].isin(BUY_TIERS), "play_type"] = "AVOID_overheated"

sec_map = sig_b.dropna(subset=["sec"]).drop_duplicates("ticker").set_index("ticker")["sec"].to_dict()
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opens  = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
liqlk  = {(r.ticker, r.time): r.liq_adv for r in panel.itertuples()}
sig_mom = sig_b[["time","ticker","play_type","ta","Close"]].copy()

date_pos = {d: i for i, d in enumerate(vni_dates)}
def next_day(d):
    i = date_pos.get(d)
    return vni_dates[i+1] if i is not None and i+1 < len(vni_dates) else None

rc = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap.csv"), parse_dates=["time"])
sigAH = pd.Series(rc["sig_AH"].values, index=rc["time"]).reindex(pd.Index(vni_dates)).ffill().fillna(1).astype(int)

# ── LAGGED schedule (exact prodspec construction) ───────────────────────────
# fin reconstructed from parquet (pkl unreadable). surprise_B_MA + d_NPR.
print("[2] Building LAGGED earnings schedule (fin from ticker_financial.parquet)...")
fc = pd.read_parquet(os.path.join(W,"data/bq_cache/ticker_financial.parquet"))
fc["Release_Date"] = pd.to_datetime(fc["Release_Date"])
fin = fc[["ticker","quarter","Release_Date","NP_P0","NP_P1","NP_P2","NP_P3","NP_P4","NP_P5"]].copy()
FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
def safe_yoy(num, den):
    den = den.where(den != 0, np.nan)
    return num/den - 1.0
fin["d_NPR"] = safe_yoy(fin["NP_P0"], fin["NP_P4"]) - safe_yoy(fin["NP_P1"], fin["NP_P5"])

ev_class = pd.read_csv(os.path.join(W,"data/earnings_events_classified.csv"), parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA","d_NPR"]],
                    on=["ticker","quarter","Release_Date"], how="left")
ev = ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True)
ev["surprise_B_MA"] = ev["surprise_B_MA"].fillna(0)
LN2 = np.log(2); HL = 3.0
ev["prior_n_good"] = 0; ev["pa_HL3"] = np.nan
for tk, g in ev.groupby("ticker"):
    hist = []
    for ri in g.index.tolist():
        row = ev.loc[ri]; cur = row["Release_Date"]
        ev.at[ri,"prior_n_good"] = len(hist)
        if hist:
            da = pd.to_datetime([d for d,_ in hist]); pa = np.array([p for _,p in hist])
            wts = np.exp(-LN2 * ((cur-da).days.values/365.25) / HL)
            ev.at[ri,"pa_HL3"] = (pa*wts).sum()/wts.sum() if wts.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"] >= 15 and pd.notna(row["post_ret"]):
            hist.append((cur, row["post_ret"]))
e_hl3_full = ev[(ev["NP_R"]>=15) & (ev["prior_n_good"]>=4) & (ev["pa_HL3"]>=5)].copy()
arr = np.array(vni_dates, dtype="datetime64[ns]")
def offset_date(ref, off):
    pos = np.searchsorted(arr, np.datetime64(ref), side="right") - 1
    tgt = pos + off
    return pd.Timestamp(arr[tgt]) if 0 <= tgt < len(arr) else None

def build_lag(e_hl3):
    lag_rows = []
    for _, row in e_hl3.iterrows():
        tk = row["ticker"]
        entry = offset_date(row["Release_Date"], 5)
        if entry is None or tk not in prices: continue
        sigday = offset_date(entry, -1)
        if sigday is None or sigday not in prices[tk]: continue
        pt = "LAG_HI" if row["surprise_B_MA"] > 0.5 else "LAG_LO"
        lag_rows.append({"time": sigday, "ticker": tk, "play_type": pt, "ta": 400.0,
                         "Close": prices[tk][sigday], "year": row["Release_Date"].year})
    return pd.DataFrame(lag_rows)

# Version A = baseline; Version B = + d_NPR>=0 (drop d_NPR<0 or NaN)
e_hl3_A = e_hl3_full
e_hl3_B = e_hl3_full[e_hl3_full["d_NPR"] >= 0]
sig_lag_A = build_lag(e_hl3_A)
sig_lag_B = build_lag(e_hl3_B)
print(f"    LAG schedule A (baseline): {len(sig_lag_A)} entries "
      f"(HI {(sig_lag_A['play_type']=='LAG_HI').sum()}, LO {(sig_lag_A['play_type']=='LAG_LO').sum()})")
print(f"    LAG schedule B (dNPR>=0) : {len(sig_lag_B)} entries "
      f"(HI {(sig_lag_B['play_type']=='LAG_HI').sum()}, LO {(sig_lag_B['play_type']=='LAG_LO').sum()})")
print(f"    dropped by filter: {len(sig_lag_A)-len(sig_lag_B)} "
      f"({100*(len(sig_lag_A)-len(sig_lag_B))/max(1,len(sig_lag_A)):.1f}%)")

# ── switched stream + flip force-close dates (shared across versions) ─────────
print("[3] Building switched stream + flip force-close dates...")
top30 = set(pd.read_csv(os.path.join(W,"data","v4f_top30.csv"))["ticker"])
V30_TIERS = TIER_BAL
LAG_TIERS = ["LAG_HI","LAG_LO"]
shn.TIER_PRIORITY.update({"LAG_HI": 88, "LAG_LO": 82})
def fill_mode(d):
    nd = next_day(d)
    return int(sigAH.loc[nd]) if nd is not None and nd in sigAH.index else int(sigAH.loc[d])
sig_v30 = sig_mom[sig_mom["ticker"].isin(top30)].copy()
keep_v30 = sig_v30["time"].map(lambda d: fill_mode(d) == 1)

def build_switched(sig_lag):
    keep_lag = sig_lag["time"].map(lambda d: fill_mode(d) == 0)
    cols = ["time","ticker","play_type","ta","Close"]
    return pd.concat([sig_v30[keep_v30][cols], sig_lag[keep_lag][cols]], ignore_index=True)

fc_dates = {}
sv = sigAH.values; sidx = sigAH.index
n_flip = 0
for i in range(1, len(sv)):
    if sv[i] != sv[i-1]:
        n_flip += 1
        out_tiers = set(V30_TIERS) if sv[i] == 0 else set(LAG_TIERS)
        for back in (1, 0, -1, -2, -3):
            j = i - back
            if 0 <= j < len(sidx):
                fc_dates.setdefault(sidx[j], set()).update(out_tiers)
print(f"    {n_flip} real flips -> force-liquidation dates set")

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
COMMON = dict(max_positions=12, hold_days=45, stop_loss=-0.20, min_hold=2,
              slippage=0.001, init_nav=BOOK,
              sector_limit_per_sector={8:4}, ticker_sector_map=sec_map,
              sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},
              deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
              cash_etf_states={3:0.7}, vn30_underlying=vn30_und,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015,
              open_prices=opens, t1_open_exec=True, **LIQ)

def run(sig, tiers, label, tw, extra=None):
    nav, _ = simulate(sig, prices, vni_dates, allowed_tiers=tiers,
                      tier_weights=tw, name=label, **COMMON, **(extra or {}))
    nav["time"] = pd.to_datetime(nav["time"])
    return nav

extraB = dict(hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},
              stop_exempt_tiers={"LAG_HI","LAG_LO"},
              force_close_tiers_dates=fc_dates,
              tier_position_limit={"LAG_HI":12,"LAG_LO":12})

# ── run books ───────────────────────────────────────────────────────────────
print("[4] BOOK A — BAL 25B (shared, identical both versions)...")
navA = run(sig_mom, TIER_BAL, "BAL", TIER_WEIGHTS)
sA = navA.set_index("time")["nav"]

print("[5] BOOK B — SWITCHED 25B, Version A (baseline LAG)...")
navB_A = run(build_switched(sig_lag_A), V30_TIERS+LAG_TIERS, "SW_A",
             {**TIER_WEIGHTS, "LAG_HI":0.10, "LAG_LO":0.08}, extraB)
print("[6] BOOK B — SWITCHED 25B, Version B (LAG + dNPR>=0)...")
navB_B = run(build_switched(sig_lag_B), V30_TIERS+LAG_TIERS, "SW_B",
             {**TIER_WEIGHTS, "LAG_HI":0.10, "LAG_LO":0.08}, extraB)

sB_A = navB_A.set_index("time")["nav"]
sB_B = navB_B.set_index("time")["nav"]
total_A = sA + sB_A.reindex(sA.index).ffill()
total_B = sA + sB_B.reindex(sA.index).ffill()

# ── metrics windowed ─────────────────────────────────────────────────────────
def metrics(s, lo=None, hi=None):
    s = s.copy()
    if lo is not None: s = s[s.index >= pd.Timestamp(lo)]
    if hi is not None: s = s[s.index <= pd.Timestamp(hi)]
    s = s / s.iloc[0]
    r = s.pct_change().dropna(); yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    dd = (s/s.cummax()-1).min(); sh = r.mean()/r.std()*np.sqrt(252)
    cal = cagr/abs(dd) if dd < 0 else 0
    return cagr*100, dd*100, sh, cal

WINDOWS = [("FULL", None, None), ("IS 2014-19","2014-01-01","2019-12-31"), ("OOS 2020+","2020-01-01",None)]
def n_events(sig_lag, lo, hi):
    y = sig_lag["year"]
    if lo and hi: return int(((y>=lo)&(y<=hi)).sum())
    if lo: return int((y>=lo).sum())
    return len(sig_lag)

print("\n" + "="*100)
print(f"V2.4 50B HARNESS A/B — LAG d_NPR>=0 filter   ({sA.index[0].date()} -> {sA.index[-1].date()})")
print("="*100)
hdr = f"{'Window':<12} {'N_evt A':>8} {'N_evt B':>8} | {'CAGR_A':>8} {'CAGR_B':>8} {'dCAGR':>7} | {'DD_A':>7} {'DD_B':>7} | {'Cal_A':>6} {'Cal_B':>6} {'dCal':>6}"
print(hdr); print("-"*len(hdr))
results = {}
for name, lo, hi in WINDOWS:
    cA,dA,shA,calA = metrics(total_A, lo, hi)
    cB,dB,shB,calB = metrics(total_B, lo, hi)
    loy = int(lo[:4]) if lo else None; hiy = int(hi[:4]) if hi else None
    nA = n_events(sig_lag_A, loy, hiy); nB = n_events(sig_lag_B, loy, hiy)
    print(f"{name:<12} {nA:>8} {nB:>8} | {cA:>8.2f} {cB:>8.2f} {cB-cA:>+7.2f} | {dA:>7.1f} {dB:>7.1f} | {calA:>6.2f} {calB:>6.2f} {calB-calA:>+6.2f}")
    results[name] = dict(nA=nA,nB=nB,cagrA=round(cA,2),cagrB=round(cB,2),dcagr=round(cB-cA,2),
                         ddA=round(dA,1),ddB=round(dB,1),shA=round(shA,2),shB=round(shB,2),
                         calA=round(calA,2),calB=round(calB,2),dcal=round(calB-calA,2))

# ── WIRE rule check ──────────────────────────────────────────────────────────
oos = results["OOS 2020+"]
nA_oos, nB_oos = oos["nA"], oos["nB"]
drop_pct = 100*(nA_oos-nB_oos)/max(1,nA_oos)
wire = (oos["cagrB"] > oos["cagrA"]) and (oos["calB"] > oos["calA"]) and (drop_pct <= 40)
print("\n" + "-"*100)
print(f"WIRE rule (OOS CAGR↑ AND Calmar↑ AND N_evt drop<=40%):")
print(f"  OOS CAGR: {oos['cagrA']:.2f} -> {oos['cagrB']:.2f} ({oos['dcagr']:+.2f}pp) {'PASS' if oos['cagrB']>oos['cagrA'] else 'FAIL'}")
print(f"  OOS Calmar: {oos['calA']:.2f} -> {oos['calB']:.2f} ({oos['dcal']:+.2f}) {'PASS' if oos['calB']>oos['calA'] else 'FAIL'}")
print(f"  OOS N_evt drop: {nA_oos} -> {nB_oos} ({drop_pct:.1f}%) {'PASS' if drop_pct<=40 else 'FAIL'}")
print(f"  ==> VERDICT: {'WIRE' if wire else 'DO NOT WIRE'}")

# save
for k, df in [("A_BAL",navA),("B_SW_A",navB_A),("B_SW_B",navB_B)]:
    df.to_csv(os.path.join(W, f"data/lag_harness_dnpr_nav_{k}.csv"), index=False)
import json
with open(os.path.join(W,"data/lag_harness_dnpr_results.json"),"w") as f:
    json.dump({"results":results,"wire":bool(wire),"drop_pct_oos":round(drop_pct,1)}, f, indent=2)
print("  Saved: data/lag_harness_dnpr_nav_*.csv, lag_harness_dnpr_results.json")
