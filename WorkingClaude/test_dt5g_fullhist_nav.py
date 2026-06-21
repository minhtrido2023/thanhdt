# -*- coding: utf-8 -*-
"""
test_dt5g_fullhist_nav.py
=========================
(a) Quantify the pure-index NAV value of the DT5G macro overlay over FULL HISTORY
    (2000→now) — esp. how much the 2008 GFC / 2011 inflation de-risks are worth in pp.
(b) Ablation: DT5G with the EASING/RE-RISK arm DISABLED (caps only), since the
    full-history audit showed the easing floor re-entered too early in 2012 (T+60 −2.27%).

Pure-index harness (same STATE_ALLOC / up-trend boost / cost model as
validate_macro_overlay.py) on LOCAL full-history sources. NOTE: integrated
stock-selection cannot run pre-2014 (BQ `ticker` is 2014+), so this isolates the
state→allocation channel — exactly where the overlay acts. Causal (US T-1, refi +5d).

Periods: FULL 2000-now | 2003+ (drop nascent <5-listed-co market, per user) |
         PRE14 2003-2013 | MODERN 2014-now.  Output: data/dt5g_fullhist_nav.md
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from macro_state_live import _dt_4gate, _commit, P, NEUTRAL, CRISIS, BEAR
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
TC, TAX, BORROW, INIT, RF = 0.001, 0.001, 0.10, 1_000_000_000, 0.001
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}

# ── full-history data (local) ──
sf = pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv"); sf["time"] = pd.to_datetime(sf["time"])
sf = sf.sort_values("time").reset_index(drop=True); sf["state_dt"] = _dt_4gate(sf["state"].values.astype(int))
vx = pd.read_csv("data/VNINDEX.csv"); vx["time"] = pd.to_datetime(vx["time"]); vx = vx.sort_values("time").reset_index(drop=True)
vx["MA200"] = vx["Close"].rolling(200, min_periods=50).mean()
# Wilder RSI14 (for the up-trend NEUTRAL boost; applied identically to all arms)
d = vx["Close"].diff(); up = d.clip(lower=0); dn = (-d).clip(lower=0)
rs = up.ewm(alpha=1/14, adjust=False).mean() / dn.ewm(alpha=1/14, adjust=False).mean().replace(0, np.nan)
vx["D_RSI"] = (100 - 100/(1+rs)) / 100.0
df = vx[["time","Close","MA200","D_RSI"]].merge(sf[["time","state_dt"]], on="time", how="inner").sort_values("time").reset_index(drop=True)
df["state_dt"] = df["state_dt"].astype(int)
us = pd.read_csv("data/us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = df[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time":"us_time"}), left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
df = df.merge(um[["time","vix","spx_dd_1y","vix_ma252"]], on="time", how="left")
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time","refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(df["time"].min(), df["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill(); df = df.merge(dr, on="time", how="left"); df["refi"] = df["refi"].ffill().bfill()
df["refi_chg6m"] = (df["refi"] - df["refi"].shift(P["refi_chg_win"])).shift(P["refi_lag"])
peak = df["refi"].rolling(P["refi_chg_win"], min_periods=20).max()
df["refi_cut"] = ((peak-df["refi"])>=P["refi_cut_drop"]).shift(P["refi_lag"]).fillna(False)
df["bull"] = ((df["Close"]/df["Close"].shift(P["refi_chg_win"])-1>P["bull_r6m"]) & (df["Close"]>df["MA200"])).shift(1).fillna(False)

n = len(df); vix=df["vix"].values; sdd=df["spx_dd_1y"].values; vma=df["vix_ma252"].values
rc6=df["refi_chg6m"].values; cut=df["refi_cut"].values.astype(bool); bull=df["bull"].values.astype(bool); close=df["Close"].values
cap = np.full(n, 9); easing = np.zeros(n, bool)
for t in range(n):
    v,dd,vm,rr = vix[t],sdd[t],vma[t],rc6[t]
    if bull[t]: uc=ub=umild=False
    else:
        uc=(not np.isnan(dd) and dd<P["spx_crisis"]) or (not np.isnan(v) and v>P["vix_crisis"])
        ub=(not np.isnan(dd) and dd<P["spx_bear"]) and (not np.isnan(v) and v>P["vix_bear"])
        umild=(not np.isnan(dd) and dd<P["spx_mild"]) and (not np.isnan(v) and v>P["vix_mild"])
    de=(not np.isnan(rr) and rr>=P["dom_extreme"]); ds=(not np.isnan(rr) and rr>=P["dom_strong"]); dm=(not np.isnan(rr) and rr>=P["dom_mild"])
    if uc or de: cap[t]=CRISIS
    elif ub or ds: cap[t]=BEAR
    elif umild or dm: cap[t]=NEUTRAL
    calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(dd) and dd>-0.05)
    if cap[t]==9 and cut[t] and calm: easing[t]=True
persist=np.zeros(n,int)
for t in range(n): persist[t]=persist[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
lb=P["ez_price_lb"]; pup=np.zeros(n,bool); pup[lb:]=close[lb:]>close[:-lb]
ez = easing & (persist>=P["ez_confirm"]) & pup
cap = _commit(cap, P["cap_commit"]); st = df["state_dt"].values

# ── three state series ──
S_DT4    = st.copy()
S_DT5G   = np.where(cap!=9, np.minimum(st,cap), st)
S_DT5G   = np.where((cap==9)&ez&(S_DT5G<NEUTRAL), NEUTRAL, S_DT5G).astype(int)   # caps + easing
S_NOEASE = np.where(cap!=9, np.minimum(st,cap), st).astype(int)                   # caps only (easing OFF)

# ── pure-index NAV sim ──
ma200=df["MA200"].values; rsi=df["D_RSI"].values
def build_w(state):
    w=np.array([STATE_ALLOC[int(s)] for s in state],float)
    up_raw=(close>ma200)&(~np.isnan(ma200))&(np.nan_to_num(rsi,nan=0.0)<=0.72)
    cf=False; ru=rd=0; upf=np.zeros(n,bool)
    for t in range(n):
        if up_raw[t]: ru+=1; rd=0
        else: rd+=1; ru=0
        if not cf and ru>=10: cf=True
        elif cf and rd>=10: cf=False
        upf[t]=cf
    w[(state==NEUTRAL)&upf]=0.90
    return w
r=np.zeros(n); r[1:]=close[1:]/close[:-1]-1
yr=df["time"].dt.year.values; dep=np.array([VGB_1Y.get(int(y),0.001) for y in yr])
yrs_all=(df["time"].iloc[-1]-df["time"].iloc[0]).days/365.25; spy=n/yrs_all
def sim(state):
    tgt=build_w(state); tl=np.concatenate([[0.0],tgt[:-1]])
    nav=np.empty(n); nav[0]=INIT; dret=np.zeros(n)
    for t in range(n):
        w=tl[t]; wp=tl[t-1] if t>0 else 0.0
        cf=max(0,1-w); lf=max(0,w-1); buy=max(0,w-wp); sell=max(0,wp-w)
        dret[t]=w*r[t]+cf*dep[t]/spy-lf*BORROW/spy-(buy+sell)*TC-sell*TAX
        if t>0: nav[t]=nav[t-1]*(1+dret[t])
    return pd.DataFrame({"time":df["time"],"nav":nav,"ret":dret})
def met(o,a,b):
    o=o[(o["time"]>=a)&(o["time"]<=b)].reset_index(drop=True)
    if len(o)<30: return None
    nv=INIT*o["nav"].values/o["nav"].values[0]; tm=pd.DatetimeIndex(o["time"]); y=(tm[-1]-tm[0]).days/365.25
    cagr=(nv[-1]/nv[0])**(1/y)-1; ex=o["ret"].values-RF/spy
    sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    dd=((nv-np.maximum.accumulate(nv))/np.maximum.accumulate(nv)).min()
    return dict(cagr=cagr*100, sh=sh, dd=dd*100)

o4=sim(S_DT4); o5=sim(S_DT5G); on=sim(S_NOEASE)
b_h = df[["time","Close"]].copy()
periods=[("FULL 2000-now","2000-01-01","2026-12-31"),
         ("2003+ (drop nascent)","2003-01-01","2026-12-31"),
         ("PRE14 2003-2013","2003-01-01","2013-12-31"),
         ("MODERN 2014-now","2014-01-01","2026-12-31")]
L=["# DT5G Full-History pure-index NAV — (a) value + (b) easing-off ablation\n",
   "*Pure-index allocation on VNINDEX, 1B, real costs. Three state series share an identical "
   "book; only the state differs. DT4=base, DT5G=caps+easing, NOEASE=caps only (easing arm OFF). "
   "Integrated stock-selection unavailable pre-2014 → this isolates the state→allocation channel.*\n",
   "| Period | DT4 CAGR | DT5G CAGR | NOEASE CAGR | Δ DT5G | Δ NOEASE | DT5G Sh | DT5G DD |",
   "|---|---|---|---|---|---|---|---|"]
for nm,a,b in periods:
    m4=met(o4,a,b); m5=met(o5,a,b); mn=met(on,a,b)
    if not m4: continue
    L.append(f"| {nm} | {m4['cagr']:+.2f}% | {m5['cagr']:+.2f}% | {mn['cagr']:+.2f}% | "
             f"{m5['cagr']-m4['cagr']:+.2f}pp | {mn['cagr']-m4['cagr']:+.2f}pp | {m5['sh']:.2f} | {m5['dd']:.1f}% |")
    print(f"{nm:<24} DT4 {m4['cagr']:+6.2f}  DT5G {m5['cagr']:+6.2f} (Δ{m5['cagr']-m4['cagr']:+.2f})  "
          f"NOEASE {mn['cagr']:+6.2f} (Δ{mn['cagr']-m4['cagr']:+.2f})  | DD DT5G {m5['dd']:.1f} NOEASE {mn['dd']:.1f} DT4 {m4['dd']:.1f}")

# crisis-window zoom: how much are 2008 + 2011 worth?
L.append("\n## Crisis-window value (DT5G − DT4, pure-index)")
L.append("| Window | DT4 | DT5G | Δ | note |")
L.append("|---|---|---|---|---|")
for nm,a,b,note in [("2008 GFC","2008-06-01","2009-03-31","79d CRISIS cap"),
                    ("2011 inflation","2011-01-01","2011-12-31","181d CRISIS cap, SBV 14-15%"),
                    ("2012 easing era","2012-01-01","2013-06-30","easing arm fires 12x")]:
    m4=met(o4,a,b); m5=met(o5,a,b); mn=met(on,a,b)
    if not m4: continue
    L.append(f"| {nm} | {m4['cagr']:+.1f}% | {m5['cagr']:+.1f}% | {m5['cagr']-m4['cagr']:+.1f}pp | {note} |")
    print(f"  [{nm}] DT4 {m4['cagr']:+.1f} DT5G {m5['cagr']:+.1f} (Δ{m5['cagr']-m4['cagr']:+.1f}) NOEASE {mn['cagr']:+.1f}")

with open("data/dt5g_fullhist_nav.md","w",encoding="utf-8") as f: f.write("\n".join(L))
print("\nReport: data/dt5g_fullhist_nav.md")
