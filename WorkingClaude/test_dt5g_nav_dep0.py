# -*- coding: utf-8 -*-
"""
test_dt5g_nav_dep0.py
=====================
DT5G full-history pure-index NAV sim, with the user's exact reconciliation params:
  INIT = 1,000,000,000 VND (1 tỷ)
  BORROW = 10%/yr (lãi vay margin)
  DEPOSIT = 0%/yr (tiền gửi không kỳ hạn — idle cash earns nothing)
Same DT5G state machine + book/cost model as test_dt5g_fullhist_nav.py.
Reports DT5G vs Buy&Hold over FULL 2000-now (+ sub-periods) for dev reconciliation.
"""
import sys, io, os
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from macro_state_live import _dt_4gate, _commit, P, NEUTRAL, CRISIS, BEAR
from sbv_macro_overlay import SBV_REFI_EVENTS

STATE_ALLOC = {1: 0.0, 2: 0.2, 3: 0.7, 4: 1.0, 5: 1.3}
TC, TAX, BORROW, INIT, RF = 0.001, 0.001, 0.10, 1_000_000_000, 0.0
DEPOSIT = 0.0   # tiền gửi không kỳ hạn = 0%/yr (user spec)

# ── full-history data (local) ──
STATE_CSV = os.environ.get("STATE_CSV", "data/vnindex_5state_tam_quan_v3_4b_full_history.csv")
print(f"[state] {STATE_CSV}")
sf = pd.read_csv(STATE_CSV); sf["time"] = pd.to_datetime(sf["time"])
sf = sf.sort_values("time").reset_index(drop=True); sf["state_dt"] = _dt_4gate(sf["state"].values.astype(int))
vx = pd.read_csv("data/VNINDEX.csv"); vx["time"] = pd.to_datetime(vx["time"]); vx = vx.sort_values("time").reset_index(drop=True)
vx["MA200"] = vx["Close"].rolling(200, min_periods=50).mean()
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

S_DT5G = np.where(cap!=9, np.minimum(st,cap), st)
S_DT5G = np.where((cap==9)&ez&(S_DT5G<NEUTRAL), NEUTRAL, S_DT5G).astype(int)

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
yrs_all=(df["time"].iloc[-1]-df["time"].iloc[0]).days/365.25; spy=n/yrs_all
def sim(state):
    tgt=build_w(state); tl=np.concatenate([[0.0],tgt[:-1]])
    nav=np.empty(n); nav[0]=INIT; dret=np.zeros(n)
    for t in range(n):
        w=tl[t]; wp=tl[t-1] if t>0 else 0.0
        cf=max(0,1-w); lf=max(0,w-1); buy=max(0,w-wp); sell=max(0,wp-w)
        dret[t]=w*r[t]+cf*DEPOSIT/spy-lf*BORROW/spy-(buy+sell)*TC-sell*TAX
        if t>0: nav[t]=nav[t-1]*(1+dret[t])
    return pd.DataFrame({"time":df["time"],"nav":nav,"ret":dret})
def met(o,a,b):
    o=o[(o["time"]>=a)&(o["time"]<=b)].reset_index(drop=True)
    if len(o)<30: return None
    nv=INIT*o["nav"].values/o["nav"].values[0]; tm=pd.DatetimeIndex(o["time"]); y=(tm[-1]-tm[0]).days/365.25
    cagr=(nv[-1]/nv[0])**(1/y)-1; ex=o["ret"].values-RF/spy
    sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    dd=((nv-np.maximum.accumulate(nv))/np.maximum.accumulate(nv)).min()
    calmar=cagr/abs(dd) if dd<0 else float('nan')
    return dict(cagr=cagr*100, sh=sh, dd=dd*100, calmar=calmar, end=nv[-1], yrs=y)

o5=sim(S_DT5G)
# Buy & Hold (always 100% index, no costs after entry)
bh=df[["time"]].copy(); bhnav=np.empty(n); bhnav[0]=INIT
for t in range(1,n): bhnav[t]=bhnav[t-1]*(1+r[t])
bh["nav"]=bhnav; bh["ret"]=np.concatenate([[0.0],r[1:]])

# transition count (DT5G)
trans=int((np.diff(S_DT5G)!=0).sum())

periods=[("FULL 2000-now","2000-01-01","2026-12-31"),
         ("2003+ (drop nascent)","2003-01-01","2026-12-31"),
         ("Since 2011","2011-01-01","2026-12-31"),
         ("MODERN 2014-now","2014-01-01","2026-12-31")]
print(f"DT5G pure-index NAV | INIT={INIT:,} | BORROW={BORROW:.0%} | DEPOSIT={DEPOSIT:.0%} | TC={TC:.1%} TAX={TAX:.1%}")
print(f"Data: {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()} | {n} sessions | DT5G transitions={trans}\n")
hdr=f"{'Period':<24} {'DT5G CAGR':>10} {'B&H CAGR':>9} {'Δ':>7} | {'Sh':>5} {'MaxDD':>7} {'Calmar':>6} {'EndNAV':>10}"
print(hdr); print("-"*len(hdr))
L=["# DT5G Full-History NAV — dev reconciliation (deposit=0%)\n",
   f"*Pure-index allocation on VNINDEX. INIT={INIT:,} VND, BORROW={BORROW:.0%}/yr, "
   f"DEPOSIT={DEPOSIT:.0%}/yr (idle cash), TC={TC:.1%}/side, TAX={TAX:.1%} on sells. "
   f"T+1 execution. Data {df['time'].iloc[0].date()}→{df['time'].iloc[-1].date()}, {n} sessions, "
   f"DT5G transitions={trans}.*\n",
   "| Period | DT5G CAGR | B&H CAGR | Δ | DT5G Sh | DT5G MaxDD | DT5G Calmar | DT5G EndNAV |",
   "|---|---|---|---|---|---|---|---|"]
for nm,a,b in periods:
    m5=met(o5,a,b); mb=met(bh,a,b)
    if not m5: continue
    print(f"{nm:<24} {m5['cagr']:>9.2f}% {mb['cagr']:>8.2f}% {m5['cagr']-mb['cagr']:>+6.2f} | "
          f"{m5['sh']:>5.2f} {m5['dd']:>6.1f}% {m5['calmar']:>6.2f} {m5['end']/1e9:>8.2f}B")
    L.append(f"| {nm} | {m5['cagr']:+.2f}% | {mb['cagr']:+.2f}% | {m5['cagr']-mb['cagr']:+.2f}pp | "
             f"{m5['sh']:.2f} | {m5['dd']:.1f}% | {m5['calmar']:.2f} | {m5['end']/1e9:.2f}B |")
_otag = os.environ.get("OUT_TAG", "")
with open(f"data/dt5g_nav_dep0{_otag}.md","w",encoding="utf-8") as f: f.write("\n".join(L))
# also dump daily NAV for dev to diff
o5.assign(state_dt5g=S_DT5G).to_csv(f"data/dt5g_nav_dep0{_otag}_daily.csv", index=False)
print(f"\nReport: data/dt5g_nav_dep0{_otag}.md | Daily NAV: data/dt5g_nav_dep0{_otag}_daily.csv")
