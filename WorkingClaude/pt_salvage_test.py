#!/usr/bin/env python3
"""
pt_salvage_test.py — what's still worth salvaging from V5 / V6-v3?
===============================================================================
Two candidates, tested faithfully on the V2.2 frame (no-capit level for clean
sleeve comparison; capit applies to the winner afterwards):

  TEST A (from V5/KELLY): LAG book parks ETF in BULL too — {3:0.7, 4:0.7}
    vs base {3:0.7}. LAG holds idle cash ~60% of days; in BULL that idle earns 0.

  TEST B (from V6-v3): VALUE sleeve as a THIRD book (AMH capstone fix —
    the current book is a momentum monoculture; VALUE corr −0.30 diversifier).
    Spec per pt_v6v3: vscore = PB pct-rank + PE pct-rank per day; cheapest
    quintile; buy in states 3/4/5; hold 60d; stop −15%; w 12.5%/name max 8;
    liq>=2B at signal; park {3:0.7}.
    Architectures compared at 50B total:
      2-book : BAL 25 | LAG 25                      (= V2.2 base, ref 23.20%)
      3-book : BAL 16.7 | LAG 16.7 | VAL 16.7
      VAL standalone 25B (sleeve quality check)
Run: python pt_salvage_test.py
"""
import sys, os, pickle
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
import simulate_holistic_nav as shn
from simulate_holistic_nav import simulate

W = r"/home/trido/thanhdt/WorkingClaude"
TIER_BAL = ["MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY"]
TIER_WEIGHTS = {t: 0.10 for t in TIER_BAL}
BUY_TIERS = {"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","MOMENTUM_QUALITY",
             "MOMENTUM_A","MOMENTUM_S_N","DEEP_VALUE_RECOVERY","RE_BACKLOG_BUY","COMPOUNDER_BUY","S_PRO"}

print("[1] Loading...")
panel = pd.read_csv(os.path.join(W,"data","v4f_panel_2014.csv"), parse_dates=["time"])
vni_dates = sorted(panel["time"].unique())
prices = {tk: dict(zip(g["time"], g["Close"])) for tk, g in panel.groupby("ticker")}
opens  = {tk: dict(zip(g["time"], g["Open"]))  for tk, g in panel.groupby("ticker")}
liqlk  = {(r.ticker, r.time): r.liq_adv for r in panel.itertuples()}
dtg = pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"), parse_dates=["time"])
state_by_date = {t: int(s) for t, s in zip(dtg["time"], dtg["state"])}
last=None
for d in vni_dates:
    if d in state_by_date: last=state_by_date[d]
    elif last is not None: state_by_date[d]=last
vnx = pd.read_csv(os.path.join(W,"VNINDEX.csv"), usecols=["time","Close","MA200","D_RSI"], parse_dates=["time"])
vnx = vnx[vnx["time"] >= panel["time"].min()]
etf = pd.read_csv(os.path.join(W,"data","e1vfvn30_daily.csv"), parse_dates=["time"])
vn30_und = pd.Series(etf["Close"].values, index=etf["time"])

sig_b = pickle.load(open(os.path.join(W,"ba_v11_unified_12y_sig.pkl"),"rb"))
sig_b["time"] = pd.to_datetime(sig_b["time"])
sig_b = sig_b[sig_b["time"] >= panel["time"].min()].copy()
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
v["st"]=v["st"].ffill()
oh = set(v[(v["Close"]/v["MA200"]>1.30)&((v["st"]==5)|(v["D_RSI"]>0.75))]["time"])
sig_b.loc[sig_b["time"].isin(oh) & sig_b["play_type"].isin(BUY_TIERS), "play_type"]="AVOID_overheated"
sec_map = sig_b.dropna(subset=["sec"]).drop_duplicates("ticker").set_index("ticker")["sec"].to_dict()
sig_mom = sig_b[["time","ticker","play_type","ta","Close"]].copy()

with open(os.path.join(W,"earnings_surprise_data.pkl"),"rb") as f: fin = pickle.load(f)
fin["Release_Date"]=pd.to_datetime(fin["Release_Date"]); FLOOR=1e9
fin["exp_B_MA"]=fin[["NP_P1","NP_P2","NP_P3","NP_P4"]].mean(axis=1)
fin["surprise_B_MA"]=((fin["NP_P0"]-fin["exp_B_MA"])/np.maximum(np.abs(fin["exp_B_MA"]),FLOOR)).clip(-5,5)
ev_class=pd.read_csv(os.path.join(W,"earnings_events_classified.csv"),parse_dates=["Release_Date"])
ev=ev_class.merge(fin[["ticker","quarter","Release_Date","surprise_B_MA"]],on=["ticker","quarter","Release_Date"],how="left")
ev=ev.sort_values(["ticker","Release_Date"]).reset_index(drop=True); ev["surprise_B_MA"]=ev["surprise_B_MA"].fillna(0)
LN2=np.log(2); HL=3.0; ev["prior_n_good"]=0; ev["pa_HL3"]=np.nan
for tk,g in ev.groupby("ticker"):
    hist=[]
    for ri in g.index.tolist():
        row=ev.loc[ri]; cur=row["Release_Date"]; ev.at[ri,"prior_n_good"]=len(hist)
        if hist:
            da=pd.to_datetime([d for d,_ in hist]); pa=np.array([p for _,p in hist])
            wts=np.exp(-LN2*((cur-da).days.values/365.25)/HL)
            ev.at[ri,"pa_HL3"]=(pa*wts).sum()/wts.sum() if wts.sum()>0 else np.nan
        if pd.notna(row["NP_R"]) and row["NP_R"]>=15 and pd.notna(row["post_ret"]): hist.append((cur,row["post_ret"]))
e_hl3=ev[(ev["NP_R"]>=15)&(ev["prior_n_good"]>=4)&(ev["pa_HL3"]>=5)].copy()
arr=np.array(vni_dates,dtype="datetime64[ns]")
def offd(ref,off):
    pos=np.searchsorted(arr,np.datetime64(ref),side="right")-1; t=pos+off
    return pd.Timestamp(arr[t]) if 0<=t<len(arr) else None
rows=[]
for _,row in e_hl3.iterrows():
    tk=row["ticker"]; entry=offd(row["Release_Date"],5)
    if entry is None or tk not in prices: continue
    sd=offd(entry,-1)
    if sd is None or sd not in prices[tk]: continue
    rows.append({"time":sd,"ticker":tk,"play_type":"LAG_HI" if row["surprise_B_MA"]>0.5 else "LAG_LO",
                 "ta":400.0,"Close":prices[tk][sd]})
sig_lag=pd.DataFrame(rows)
shn.TIER_PRIORITY.update({"LAG_HI":88,"LAG_LO":82,"VALUE":70})
LAG_TW={"LAG_HI":0.10,"LAG_LO":0.08}

print("[2] VALUE signal (V6-v3 spec: cheapest PB+PE quintile, states 3/4/5, liq>=2B)...")
vp = pd.read_csv(os.path.join(W,"data","v4f_valpanel.csv"), parse_dates=["time"])
liq_s = panel.set_index(["time","ticker"])["liq_adv"]
vp = vp.set_index(["time","ticker"]).join(liq_s, how="left").reset_index()
vp = vp[vp["liq_adv"]>=2e9]
vp["st"] = vp["time"].map(lambda d: state_by_date.get(d,3))
vp = vp[vp["st"].isin([3,4,5])]
parts=[]
for t,g in vp.groupby("time"):
    g=g.copy()
    g["vscore"]=g["PB"].rank(pct=True)+g["PE"].rank(pct=True)
    ch=g[g["vscore"]<=g["vscore"].quantile(0.20)].copy()
    ch["ta"]=100+100*(1-ch["vscore"]/2)
    parts.append(ch[["time","ticker","ta"]])
val=pd.concat(parts,ignore_index=True); val["play_type"]="VALUE"
val["Close"]=[prices.get(tk,{}).get(d,np.nan) for tk,d in zip(val["ticker"],val["time"])]
val=val.dropna(subset=["Close"])
sig_val=val[["time","ticker","play_type","ta","Close"]]
print(f"    VALUE signal rows: {len(sig_val):,}")

LIQ = dict(liquidity_volume_pct=0.20, max_fill_days=5, liquidity_lookup=liqlk, exit_slippage_tiered=True)
def BKW(init): return dict(max_positions=12, min_hold=2, slippage=0.001, init_nav=init,
               deposit_annual=0.0, borrow_annual=0.10, state_by_date=state_by_date,
               open_prices=opens, t1_open_exec=True, **LIQ)
ETF_KW = dict(vn30_underlying=vn30_und, etf_mgmt_fee_annual=0.0,
              etf_tracking_drag_annual=0.0, etf_rebalance_friction=0.0015)

def run_bal(init,label):
    nav,_=simulate(sig_mom,prices,vni_dates,allowed_tiers=TIER_BAL,tier_weights=TIER_WEIGHTS,
        hold_days=45,stop_loss=-0.20,sector_limit_per_sector={8:4},ticker_sector_map=sec_map,
        sector_cap_exempt_tiers={"RE_BACKLOG_BUY"},cash_etf_states={3:0.7},**ETF_KW,
        name=label,**BKW(init))
    nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]
def run_lagb(init,label,park_map):
    nav,_=simulate(sig_lag,prices,vni_dates,allowed_tiers=["LAG_HI","LAG_LO"],tier_weights=LAG_TW,
        hold_days=25,stop_loss=-0.99,stop_exempt_tiers={"LAG_HI","LAG_LO"},
        hold_days_by_tier={"LAG_HI":25,"LAG_LO":25},tier_position_limit={"LAG_HI":12,"LAG_LO":12},
        cash_etf_states=park_map,**ETF_KW,name=label,**BKW(init))
    nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]
def run_val(init,label):
    nav,_=simulate(sig_val,prices,vni_dates,allowed_tiers=["VALUE"],tier_weights={"VALUE":0.125},
        hold_days=60,stop_loss=-0.15,tier_position_limit={"VALUE":8},
        cash_etf_states={3:0.7},**ETF_KW,name=label,**BKW(init))
    nav["time"]=pd.to_datetime(nav["time"]); return nav.set_index("time")["nav"]
def metrics(s):
    s=s.dropna(); r=s.pct_change().dropna(); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1; dd=(s/s.cummax()-1).min(); sh=r.mean()/r.std()*np.sqrt(252)
    return cagr*100, dd*100, sh, (cagr/abs(dd) if dd<0 else 0)

print("[3] TEST A — Kelly parking on LAG (BULL too)...")
lag_park   = pd.read_csv(os.path.join(W,"data","pt_orch_lag_park.csv"),parse_dates=["time"]).set_index("time")["nav"]
lag_kelly  = run_lagb(25_000_000_000,"LAG_pk_kelly",{3:0.7,4:0.7})
navA = pd.read_csv(os.path.join(W,"data","pt_v4_full_faithful_nav_A.csv"),parse_dates=["time"]).set_index("time")["nav"]
for lbl,b in [("LAG park {3:0.7} (ref)",lag_park),("LAG park {3:0.7,4:0.7} KELLY",lag_kelly)]:
    c,d,sh,cal=metrics(b); print(f"    {lbl:<32} standalone: {c:6.2f}% / {d:6.1f}% / Sh {sh:.2f}")
    s=(navA+b.reindex(navA.index).ffill()).dropna(); c,d,sh,cal=metrics(s)
    print(f"    {'-> 2-book BAL|LAG':<32}          : {c:6.2f}% / {d:6.1f}% / Sh {sh:.2f} / Cal {cal:.2f}")

print("[4] TEST B — VALUE third book (V6-v3 salvage)...")
val25 = run_val(25_000_000_000,"VAL25")
c,d,sh,cal=metrics(val25); print(f"    VALUE standalone 25B            : {c:6.2f}% / {d:6.1f}% / Sh {sh:.2f}")
B3 = 50_000_000_000/3
bal3 = run_bal(B3,"BAL3"); lag3 = run_lagb(B3,"LAG3",{3:0.7}); val3 = run_val(B3,"VAL3")
s3=(bal3+lag3.reindex(bal3.index).ffill()+val3.reindex(bal3.index).ffill()).dropna()
c3,d3,sh3,cal3=metrics(s3)
s2=(navA+lag_park.reindex(navA.index).ffill()).dropna(); c2,d2,sh2,cal2=metrics(s2)
print("\n"+"="*92)
print("SALVAGE RESULTS (faithful, 50B total, no-capit level)")
print("="*92)
print(f"  {'architecture':<44}{'CAGR':>8}{'MaxDD':>9}{'Sharpe':>8}{'Calmar':>8}")
print(f"  {'2-book BAL25|LAG25+park (V2.2 base ref)':<44}{c2:>7.2f}%{d2:>8.1f}%{sh2:>8.2f}{cal2:>8.2f}")
print(f"  {'3-book BAL16.7|LAG16.7|VAL16.7':<44}{c3:>7.2f}%{d3:>8.1f}%{sh3:>8.2f}{cal3:>8.2f}")
# correlation of VALUE sleeve vs others (diversification check)
rb=bal3.pct_change(); rl=lag3.pct_change(); rv=val3.pct_change()
print(f"\n  daily-ret corr: VAL-BAL {rv.corr(rb):.2f} | VAL-LAG {rv.corr(rl):.2f} | BAL-LAG {rb.corr(rl):.2f}")
for nm,s in [("val25",val25),("lag_kelly",lag_kelly),("bal3",bal3),("lag3",lag3),("val3",val3)]:
    s.to_frame("nav").to_csv(os.path.join(W,f"data/pt_salvage_{nm}.csv"))
print("  Saved: data/pt_salvage_*.csv")
