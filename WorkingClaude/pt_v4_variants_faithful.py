#!/usr/bin/env python3
"""
pt_v4_variants_faithful.py — faithful V1 / V2(V12) / V2.1(V12.1) vs faithful V4.
===============================================================================
Same two-real-25B-ledger framework as pt_v4_full_faithful.py, but the SECOND book
is a STATIC (never-switching) variant — exactly the V1/V2 system shapes:
  V1   = BAL 25B + VN30 25B            (BA-v11 on top-30, always on, parking {3:0.7})
  V2   = BAL 25B + LAG-v12 25B         (earnings schedule, flat 8% sizing, no parking)
  V2.1 = BAL 25B + LAG-v12.1 25B       (S2 sizing 10%/8% by surprise, no parking)
  V4   = BAL 25B + SWITCHED 25B        (already run: pt_v4_full_faithful_nav_B.csv)
Spec fidelity: VN30 book = prodspec run_vn30 (no sector cap, hold 45/stop -20, ETF
parking); LAG books = prodspec run_lagged (25td time-exit only, no stop, no sector
cap, no parking, liq>=2B handled by 20%ADV cap + engine).
No flips -> no flip liquidation cost, no post-flip cash drag. The question: does
the ensemble switch EARN its real-world cost?
Run: python pt_v4_variants_faithful.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
BOOK = 25_000_000_000
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}

print("[1] Loading shared data...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
sig_b = pickle.load(open(os.path.join(W,"ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"] = pd.to_datetime(sig_b["time"])
sig_b = sig_b[sig_b["time"] >= panel["time"].min()].copy()
dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
vni_dates = sorted(panel["time"].unique())
last_st = None
for d in vni_dates:
    if d in state_by_date: last_st = state_by_date[d]
    elif last_st is not None: state_by_date[d] = last_st
vnx = pd.read_csv(os.path.join(W,"VNINDEX.csv"), usecols=["time","Close","MA200","D_RSI"], parse_dates=["time"])
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

print("[2] LAGGED schedule...")
with open(os.path.join(W,"earnings_surprise_data.pkl"),"rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv(os.path.join(W,"earnings_events_classified.csv"), parse_dates=["Release_Date"])
ev = ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],
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
e_hl3 = ev[(ev["NP_R"]>=15) & (ev["prior_n_good"]>=4) & (ev["pa_HL3"]>=5)].copy()
arr = np.array(vni_dates, dtype="datetime64[ns]")
def offset_date(ref, off):
    pos = np.searchsorted(arr, np.datetime64(ref), side="right") - 1
    tgt = pos + off
    return pd.Timestamp(arr[tgt]) if 0 <= tgt < len(arr) else None
lag_rows = []
for _, row in e_hl3.iterrows():
    tk = row["ticker"]
    entry = offset_date(row["Release_Date"], 5)
    if entry is None or tk not in prices: continue
    sigday = offset_date(entry, -1)
    if sigday is None or sigday not in prices[tk]: continue
    pt = "LAG_HI" if row["surprise_B_MA"] > 0.5 else "LAG_LO"
    lag_rows.append({"time": sigday, "ticker": tk, "play_type": pt, "ta": 400.0,
                     "Close": prices[tk][sigday]})
sig_lag = pd.DataFrame(lag_rows)
shn.TIER_PRIORITY.update({"LAG_HI": 88, "LAG_LO": 82})

top30 = set(pd.read_csv(os.path.join(W,"data","v4f_top30.csv"))["ticker"])
sig_v30 = sig_mom[sig_mom["ticker"].isin(top30)].copy()

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
BASE_KW = dict(max_positions=12, min_hold=2, slippage=0.001, init_nav=BOOK,
               ticker_sector_map=sec_map, deposit_annual=0.0, borrow_annual=0.10,
               state_by_date=state_by_date, open_prices=opens, t1_open_exec=True, **LIQ)

def run(sig, tiers, label, tw, **kw):
    nav, _ = simulate(sig, prices, vni_dates, allowed_tiers=tiers, tier_weights=tw,
                      name=label, **BASE_KW, **kw)
    nav["time"] = pd.to_datetime(nav["time"])
    return nav.set_index("time")["nav"]

def metrics(s):
    r = s.pct_change().dropna(); yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    dd = (s/s.cummax()-1).min(); sh = r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, (cagr/abs(dd) if dd<0 else 0)

print("[3] Second-book variants (25B each)...")
nav_v30 = run(sig_v30, TIER_BAL, "VN30_always", TIER_WEIGHTS,
              hold_days=45, stop_loss=-0.20,
              cash_etf_states={3:0.7}, vn30_underlying=vn30_und,
              etf_mgmt_fee_annual=0.0, etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015)
print(f"    VN30 always-on : {nav_v30.iloc[-1]/1e9:.1f}B")
nav_l12 = run(sig_lag, ["LAG_HI","LAG_LO"], "LAG_v12", {"LAG_HI":0.08,"LAG_LO":0.08},
              hold_days=25, stop_loss=-0.99, stop_exempt_tiers={"LAG_HI","LAG_LO"},
              hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},
              tier_position_limit={"LAG_HI":12,"LAG_LO":12})
print(f"    LAG v12 (8%)   : {nav_l12.iloc[-1]/1e9:.1f}B")
nav_l121 = run(sig_lag, ["LAG_HI","LAG_LO"], "LAG_v121", {"LAG_HI":0.10,"LAG_LO":0.08},
               hold_days=25, stop_loss=-0.99, stop_exempt_tiers={"LAG_HI","LAG_LO"},
               hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},
               tier_position_limit={"LAG_HI":12,"LAG_LO":12})
print(f"    LAG v12.1 (S2) : {nav_l121.iloc[-1]/1e9:.1f}B")

navA = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_A.csv"), parse_dates=["time"]).set_index("time")["nav"]
navB_sw = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_B.csv"), parse_dates=["time"]).set_index("time")["nav"]

print("\n" + "="*94)
print("FAITHFUL SYSTEM COMPARISON (two real 25B ledgers each, 2014 -> now, real fills)")
print("="*94)
rows = [("V1  = BAL + VN30 (static)",        navA + nav_v30.reindex(navA.index).ffill()),
        ("V2  = BAL + LAG v12 (static)",     navA + nav_l12.reindex(navA.index).ffill()),
        ("V2.1= BAL + LAG v12.1 (static)",   navA + nav_l121.reindex(navA.index).ffill()),
        ("V4  = BAL + SWITCHED (ensemble)",  navA + navB_sw.reindex(navA.index).ffill())]
print(f"  {'system':<34}{'CAGR':>8}{'MaxDD':>9}{'Sharpe':>8}{'Calmar':>8}{'NAV':>9}")
for lbl, s in rows:
    c,d,sh,cal = metrics(s.dropna())
    print(f"  {lbl:<34}{c:>7.2f}%{d:>8.1f}%{sh:>8.2f}{cal:>8.2f}{s.dropna().iloc[-1]/1e9:>8.1f}B")
print("\n  standalone second books (25B):")
for lbl, s in [("BAL (book A)",navA),("VN30 always",nav_v30),("LAG v12",nav_l12),("LAG v12.1",nav_l121),("SWITCHED",navB_sw)]:
    c,d,sh,cal = metrics(s.dropna())
    print(f"    {lbl:<16}: CAGR {c:6.2f}%  MaxDD {d:6.1f}%  Sharpe {sh:.2f}")
# recombined references, same CSV
rc = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap.csv"), parse_dates=["time"]).set_index("time")
def m2(s):
    s = s/s.iloc[0]; r = s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return (s.iloc[-1]**(1/yrs)-1)*100, (s/s.cummax()-1).min()*100, r.mean()/r.std()*np.sqrt(252)
print("\n  recombined references:")
for col,lbl in [("V1_V11_TQ34b","V1"),("V2_V12_TQ34b","V2"),("V4_V121_ENS_TQ34b","V4"),("VNI","VNINDEX")]:
    cg,dd_,sh_ = m2(rc[col]); print(f"    {lbl:<8}: CAGR {cg:6.2f}%  MaxDD {dd_:6.1f}%  Sharpe {sh_:.2f}")
for name, s in [("v30_always",nav_v30),("lag_v12",nav_l12),("lag_v121",nav_l121)]:
    s.to_frame("nav").to_csv(os.path.join(W,f"data/pt_v4_variants_{name}.csv"))
print("  Saved: data/pt_v4_variants_*.csv")
