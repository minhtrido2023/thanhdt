#!/usr/bin/env python3
"""
pt_v4_full_faithful.py — the MOST FAITHFUL reproduction of V4 (V121_ENS) possible:
two REAL 25B ledgers, every leg transaction-level, the ensemble switch executed as
REAL liquidate-and-rebuy (not the virtual 0.5% haircut).
===============================================================================
WHY: both run_5systems_prodspec AND the live pt_v4_dt5g build the SWITCHED leg as
return-switching between two independently-running sims (the inactive book keeps
compounding; flips inherit its NAV path minus a flat 0.5%). That has never been a
real wallet. Here:

  BOOK A (25B) — BAL: real BA-v11 signal (pkl) + SV_TIGHT + overheat-AVOID,
    TIER_BAL tw 10%, max 12, hold 45d, stop -20%, DT5G parking {3:0.7} E1VFVN30.
  BOOK B (25B) — SWITCHED, ONE LEDGER: sig_AH==1 -> BA-v11 restricted to top-30;
    sig_AH==0 -> LAGGED earnings-surprise schedule (T+5 entry, 25td hold, 10%/8%
    S2 sizing, no stop). On every flip the outgoing mode's positions are SOLD FOR
    REAL at T+1 Open (slippage + tax + tiered exit slip) and the incoming mode
    rebuys from actual cash. No NAV inheritance, no flat haircut.
  V4_faithful = A + B (25/25 split is a real partition - two accounts).
  Optional --capit: committed capitulation sleeve per playbook in EACH book,
    sized by that book's own free cash (two accounts each running the playbook).

All fills: T+1 Open, 20%-ADV/day cap, 5 fill days, TC 0.3% round-trip, borrow 10%.
sig_AH = the saved point-in-time M1+M3r AND-HOLD series (rscap CSV) - NAV-independent.
Run: python pt_v4_full_faithful.py [--capit]
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
BOOK = 25_000_000_000
WITH_CAPIT = "--capit" in sys.argv
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}
EVENTS = [("2014-05-08",1,False),("2015-08-24",3,False),("2016-01-18",3,True),
          ("2018-05-28",1,False),("2020-03-12",2,False),
          ("2022-04-20",1,False),("2022-06-20",2,True),("2022-09-29",2,True),
          ("2023-10-31",1,False),("2024-04-19",4,False),("2025-04-03",4,False),
          ("2026-03-09",3,False)]
def size_of(state, grind):
    return (1.0 if state == 1 else 0.5) * (0.5 if grind else 1.0)

# ── shared data (same as pt_v4_capit_faithful --full) ───────────────────────
print("[1] Loading shared data...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
sig_b = pickle.load(open(os.path.join(W,"data/ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"] = pd.to_datetime(sig_b["time"])
sig_b = sig_b[sig_b["time"] >= panel["time"].min()].copy()

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

# ── ensemble signal (point-in-time, saved) ──────────────────────────────────
rc = pd.read_csv(os.path.join(W,"data","5sys_prodspec_201401_202605_dt5g_rscap.csv"), parse_dates=["time"])
sigAH = pd.Series(rc["sig_AH"].values, index=rc["time"]).reindex(pd.Index(vni_dates)).ffill().fillna(1).astype(int)

# ── LAGGED schedule (exact prodspec construction) ───────────────────────────
print("[2] Building LAGGED earnings schedule...")
with open(os.path.join(W,"data/earnings_surprise_data.pkl"),"rb") as f: fin = pickle.load(f)
fin["Release_Date"] = pd.to_datetime(fin["Release_Date"]); FLOOR = 1e9
fin["exp_B_MA"] = fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"] = ((fin["NP_P0"] - fin["exp_B_MA"]) / np.maximum(np.abs(fin["exp_B_MA"]), FLOOR)).clip(-5, 5)
ev_class = pd.read_csv(os.path.join(W,"data/earnings_events_classified.csv"), parse_dates=["Release_Date"])
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
    sigday = offset_date(entry, -1)           # engine buys T+1 Open => signal the day before
    if sigday is None or sigday not in prices[tk]: continue
    pt = "LAG_HI" if row["surprise_B_MA"] > 0.5 else "LAG_LO"
    lag_rows.append({"time": sigday, "ticker": tk, "play_type": pt, "ta": 400.0,
                     "Close": prices[tk][sigday]})
sig_lag = pd.DataFrame(lag_rows)
print(f"    LAG schedule: {len(sig_lag)} entries (HI {(sig_lag['play_type']=='LAG_HI').sum()}, LO {(sig_lag['play_type']=='LAG_LO').sum()})")

# ── BOOK B switched signal stream + real flip liquidation ───────────────────
print("[3] Building switched stream (mode-gated) + flip force-close dates...")
top30 = set(pd.read_csv(os.path.join(W,"data","v4f_top30.csv"))["ticker"])
V30_TIERS = TIER_BAL
LAG_TIERS = ["LAG_HI","LAG_LO"]
shn.TIER_PRIORITY.update({"LAG_HI": 88, "LAG_LO": 82})
# mode effective at the FILL day (signal day d fills at next_day(d))
def fill_mode(d):
    nd = next_day(d)
    return int(sigAH.loc[nd]) if nd is not None and nd in sigAH.index else int(sigAH.loc[d])
sig_v30 = sig_mom[sig_mom["ticker"].isin(top30)].copy()
keep_v30 = sig_v30["time"].map(lambda d: fill_mode(d) == 1)
keep_lag = sig_lag["time"].map(lambda d: fill_mode(d) == 0)
sig_sw = pd.concat([sig_v30[keep_v30], sig_lag[keep_lag]], ignore_index=True)
# flips: first day t with new sig value -> close outgoing tiers (queued at t-1, sells at t Open)
flips = [t for p, t in zip(sigAH.values[:-1], sigAH.values[1:]) if False]  # placeholder
fc_dates = {}
sv = sigAH.values; sidx = sigAH.index
n_flip = 0
for i in range(1, len(sv)):
    if sv[i] != sv[i-1]:
        n_flip += 1
        out_tiers = set(V30_TIERS) if sv[i] == 0 else set(LAG_TIERS)
        for back in (1, 0, -1, -2, -3):       # t-1 (sell at t open) + sticky days for min_hold stragglers
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

def add_capit(sig, navlog_base, tag):
    """committed sleeve per playbook, sized by THIS book's own free cash (two real accounts)."""
    elig = pd.read_csv(os.path.join(W,"data","capit_event_elig_full.csv"), parse_dates=["event"])
    basecash = navlog_base.set_index("time")["cash_pct"]/100.0
    rows, tw, tiers = [], {}, []
    for i,(ds,st,gr) in enumerate(EVENTS):
        d = pd.Timestamp(ds)
        e = elig[elig["event"]==d].copy()
        e = e[[t in prices and d in prices[t] for t in e["ticker"]]]
        g = e[e["pbz"]<-1]; c = e[e["pbz"]<0]
        pick = g if len(g)>=3 else (c if len(c)>=3 else e)
        pick = pick.nsmallest(15,"pbz") if len(pick)>15 else pick
        names = list(pick["ticker"])
        if len(names)<3: continue
        pos = basecash.index.searchsorted(d); cfree = float(basecash.iloc[max(0,pos-2):pos+1].mean())
        wt = size_of(st,gr)*max(cfree,0.0)
        if wt <= 0.005: continue
        pt = f"CAPIT{tag}_E{i}"; shn.TIER_PRIORITY[pt] = 95
        tw[pt] = wt/len(names); tiers.append(pt)
        for t in names:
            rows.append({"time":d,"ticker":t,"play_type":pt,"ta":500.0,"Close":prices[t][d]})
    extra = dict(hold_days_by_tier={t:60 for t in tiers}, stop_exempt_tiers=set(tiers),
                 slot_exempt_tiers=set(tiers), tier_position_limit={t:15 for t in tiers})
    return pd.concat([sig, pd.DataFrame(rows)], ignore_index=True), tw, tiers, extra

def run(sig, tiers, label, tw, extra=None):
    evl = []
    nav, _ = simulate(sig, prices, vni_dates, allowed_tiers=tiers,
                      tier_weights=tw, event_log=evl, name=label, **COMMON, **(extra or {}))
    nav["time"] = pd.to_datetime(nav["time"])
    return nav, pd.DataFrame(evl)

def metrics(s):
    r = s.pct_change().dropna(); yrs = (s.index[-1]-s.index[0]).days/365.25
    cagr = (s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    dd = (s/s.cummax()-1).min(); sh = r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, (cagr/abs(dd) if dd<0 else 0)

# ── run books ───────────────────────────────────────────────────────────────
print("[4] BOOK A — BAL 25B...")
navA, evA = run(sig_mom, TIER_BAL, "V4F_BAL", TIER_WEIGHTS)
print("[5] BOOK B — SWITCHED 25B (one ledger, real flips)...")
extraB = dict(hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},
              stop_exempt_tiers={"LAG_HI","LAG_LO"},
              force_close_tiers_dates=fc_dates,
              tier_position_limit={"LAG_HI":12,"LAG_LO":12})
navB, evB = run(sig_sw, V30_TIERS+LAG_TIERS, "V4F_SW",
                {**TIER_WEIGHTS, "LAG_HI":0.10, "LAG_LO":0.08}, extraB)

sA = navA.set_index("time")["nav"]; sB = navB.set_index("time")["nav"]
total = (sA + sB.reindex(sA.index).ffill())
cT,dT,shT,calT = metrics(total)
cA,dA,shA,calA = metrics(sA); cB,dB,shB,calB = metrics(sB)

out = {"A": navA, "B": navB}
if WITH_CAPIT:
    print("[6] CAPIT arms (sleeve per book, own free cash)...")
    sigA2, twA2, tiersA2, exA2 = add_capit(sig_mom, navA, "A")
    navA2, _ = run(sigA2, TIER_BAL+tiersA2, "V4F_BAL_CAP", {**TIER_WEIGHTS, **twA2}, exA2)
    sigB2, twB2, tiersB2, exB2 = add_capit(sig_sw, navB, "B")
    exB2_all = {**extraB,
                "hold_days_by_tier": {**extraB["hold_days_by_tier"], **exB2["hold_days_by_tier"]},
                "stop_exempt_tiers": extraB["stop_exempt_tiers"] | exB2["stop_exempt_tiers"],
                "slot_exempt_tiers": exB2["slot_exempt_tiers"],
                "tier_position_limit": {**extraB["tier_position_limit"], **exB2["tier_position_limit"]}}
    navB2, _ = run(sigB2, V30_TIERS+LAG_TIERS+tiersB2, "V4F_SW_CAP",
                   {**TIER_WEIGHTS,"LAG_HI":0.10,"LAG_LO":0.08, **twB2}, exB2_all)
    sA2 = navA2.set_index("time")["nav"]; sB2 = navB2.set_index("time")["nav"]
    total2 = sA2 + sB2.reindex(sA2.index).ffill()
    c2,d2,sh2,cal2 = metrics(total2)
    out["A_cap"] = navA2; out["B_cap"] = navB2

# ── report ──────────────────────────────────────────────────────────────────
print("\n" + "="*92)
print(f"V4 FULL-FAITHFUL (two real 25B ledgers, real flip liquidation; {sA.index[0].date()} -> {sA.index[-1].date()})")
print("="*92)
print(f"  Book A BAL 25B            : CAGR {cA:6.2f}%  MaxDD {dA:6.1f}%  Sharpe {shA:.2f}  NAV {sA.iloc[-1]/1e9:6.1f}B")
print(f"  Book B SWITCHED 25B       : CAGR {cB:6.2f}%  MaxDD {dB:6.1f}%  Sharpe {shB:.2f}  NAV {sB.iloc[-1]/1e9:6.1f}B")
print(f"  V4 FAITHFUL = A+B (50B)   : CAGR {cT:6.2f}%  MaxDD {dT:6.1f}%  Sharpe {shT:.2f}  Calmar {calT:.2f}  NAV {total.iloc[-1]/1e9:6.1f}B")
if WITH_CAPIT:
    print(f"  V4 FAITHFUL + CAPIT       : CAGR {c2:6.2f}%  MaxDD {d2:6.1f}%  Sharpe {sh2:.2f}  Calmar {cal2:.2f}  NAV {total2.iloc[-1]/1e9:6.1f}B   ({c2-cT:+.2f}pp)")
# references
rcs = rc.set_index("time")
def m2(s):
    s = s/s.iloc[0]; r = s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    return (s.iloc[-1]**(1/yrs)-1)*100, (s/s.cummax()-1).min()*100, r.mean()/r.std()*np.sqrt(252)
for col,lbl in [("V4_V121_ENS_TQ34b","V4 recombined"),("VNI","VNINDEX B&H")]:
    cg,dd_,sh_ = m2(rcs[col]); print(f"  REF {lbl:<22}: CAGR {cg:6.2f}%  MaxDD {dd_:6.1f}%  Sharpe {sh_:.2f}")
# flip cost accounting
if len(evB):
    fl = evB[evB["reason"]=="MODE_FLIP"]
    print(f"\n  Real flip liquidations: {len(fl)} sells over {n_flip} flips")
for k, df in out.items():
    df.to_csv(os.path.join(W, f"data/pt_v4_full_faithful_nav_{k}.csv"), index=False)
if len(evB): evB.to_csv(os.path.join(W,"data/pt_v4_full_faithful_tx_B.csv"), index=False)
print("  Saved: data/pt_v4_full_faithful_nav_*.csv, tx_B.csv")
