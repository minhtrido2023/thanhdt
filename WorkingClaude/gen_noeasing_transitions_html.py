# -*- coding: utf-8 -*-
"""Generate transitions HTML for the EASING-OFF variant (keep defensive CAP, drop monetary
recovery FLOOR) vs canonical, full-history 2000-now. Highlights the windows that CHANGE
if easing is disabled, with forward VNINDEX return per change-episode, to support a deploy
decision. Research-only. Output: dt4g_macro_transitions_noeasing.html"""
import sys, io, os, json
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"; os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS

NEUTRAL,CRISIS,BEAR,EXBULL=3,1,2,5
ALLOC={1:0,2:20,3:70,4:100,5:130}
NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
COLOR={1:"#ef4444",2:"#f97316",3:"#eab308",4:"#22c55e",5:"#14b8a6"}
T_MILD,T_STR,T_EXT=0.5,1.5,3.0; CUT_PEAK=0.5; LAG=5; CAP_COMMIT=7
BREADTH_FILE=r"/home/trido/thanhdt/WorkingClaude/data/preprocess_others_market_indicators_all_tickers.csv"
DT=dict(default=10,enter_crisis=25,exit_crisis=10,enter_exbull=25,exit_exbull=10)

def asym(s,default,enter_crisis,exit_crisis,enter_exbull,exit_exbull):
    s=np.asarray(s,int); o=s.copy(); cm=s[0]; ps,pr=s[0],1
    for t in range(1,len(s)):
        x=s[t]
        if x==ps: pr+=1
        else: ps,pr=x,1
        if ps==cm: o[t]=cm; continue
        need=enter_crisis if ps==CRISIS else enter_exbull if ps==EXBULL else exit_crisis if cm==CRISIS else exit_exbull if cm==EXBULL else default
        if pr>=need: cm=ps
        o[t]=cm
    return o
def commit(a,K):
    o=a.copy(); c=a[0]; ps,pr=a[0],1
    for t in range(1,len(a)):
        if a[t]==ps: pr+=1
        else: ps,pr=a[t],1
        if pr>=K: c=ps
        o[t]=c
    return o

px=bq("""SELECT p.time,p.Close,p.MA200,p.D_RSI FROM tav2_bq.ticker AS p WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"]=pd.to_datetime(px["time"]); px=px.dropna(subset=["Close"]).sort_values("time").reset_index(drop=True)
base=pd.read_csv("data/vnindex_5state_tam_quan_v3_4b_full_history.csv"); base["time"]=pd.to_datetime(base["time"])
px=px.merge(base[["time","state"]].rename(columns={"state":"bs"}),on="time",how="inner").dropna(subset=["bs"]).reset_index(drop=True)
px["bs"]=px["bs"].astype(int)
us=pd.read_csv("data/us_market_history.csv",parse_dates=["time"]).sort_values("time")
k=px[["time"]].copy(); k["jt"]=k["time"]-pd.Timedelta(days=1)
um=pd.merge_asof(k.sort_values("jt"),us.rename(columns={"time":"us_time"}),left_on="jt",right_on="us_time",direction="backward").sort_values("time").reset_index(drop=True)
px=px.merge(um[["time","vix","spx_dd_1y","vix_ma252"]],on="time",how="left")
ev=pd.DataFrame(SBV_REFI_EVENTS,columns=["time","refi"]); ev["time"]=pd.to_datetime(ev["time"])
dr=pd.DataFrame({"time":pd.date_range(px["time"].min(),px["time"].max(),freq="D")}).merge(ev,on="time",how="left"); dr["refi"]=dr["refi"].ffill().bfill()
px=px.merge(dr,on="time",how="left"); px["refi"]=px["refi"].ffill().bfill()
px["refi_chg6m"]=(px["refi"]-px["refi"].shift(126)).shift(LAG)
px["refi_cut"]=((px["refi"].rolling(126,min_periods=20).max()-px["refi"])>=CUT_PEAK).shift(LAG).fillna(False)
px["bull"]=((px["Close"]/px["Close"].shift(126)-1>0.15)&(px["Close"]>px["MA200"])).shift(1).fillna(False)
px["dec"]=False
try:
    bd=pd.read_csv(BREADTH_FILE); bd["time"]=pd.to_datetime(bd["time"]); bd=bd[["time","Breadth_MA200","Breadth_Total_MA200"]].sort_values("time")
    px=pd.merge_asof(px.sort_values("time"),bd,on="time",direction="backward").sort_values("time").reset_index(drop=True)
    px["dec"]=((px["Breadth_Total_MA200"].fillna(0)>=100)&(px["Breadth_MA200"]>=0.50)).shift(1).fillna(False)
except Exception as e: print(f"[breadth inactive {e}]")

n=len(px); vix=px["vix"].values; sdd=px["spx_dd_1y"].values; vma=px["vix_ma252"].values
rc6=px["refi_chg6m"].values; cut=px["refi_cut"].values.astype(bool); bull=px["bull"].values.astype(bool); dec=px["dec"].values.astype(bool); close=px["Close"].values
cap=np.full(n,9); easing=np.zeros(n,bool)
for t in range(n):
    v,d2,vm,rr=vix[t],sdd[t],vma[t],rc6[t]
    if bull[t] or dec[t]: uc=ub=um_=False
    else:
        uc=(not np.isnan(d2) and d2<-0.25) or (not np.isnan(v) and v>35); ub=(not np.isnan(d2) and d2<-0.15) and (not np.isnan(v) and v>25); um_=(not np.isnan(d2) and d2<-0.10) and (not np.isnan(v) and v>20)
    de=(not np.isnan(rr) and rr>=T_EXT); ds=(not np.isnan(rr) and rr>=T_STR); dm=(not np.isnan(rr) and rr>=T_MILD)
    if uc or de: cap[t]=CRISIS
    elif ub or ds: cap[t]=BEAR
    elif um_ or dm: cap[t]=NEUTRAL
    calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(d2) and d2>-0.05)
    if cap[t]==9 and cut[t] and calm: easing[t]=True
per=np.zeros(n,int)
for t in range(n): per[t]=per[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
pu=np.zeros(n,bool); pu[10:]=close[10:]>close[:-10]; ezc=easing&(per>=10)&pu
cap=commit(cap,CAP_COMMIT)
dt=asym(px["bs"].values,**DT)
capn=np.where(cap==9,9,cap)
m_off=np.where(capn!=9,np.minimum(dt,capn),dt)                       # CAP only
m_can=np.where((capn==9)&ezc&(m_off<NEUTRAL),NEUTRAL,m_off)          # + easing FLOOR
m_can=np.where(capn!=9,np.minimum(dt,capn),np.where(ezc&(dt<NEUTRAL),NEUTRAL,dt))

def trans(st):
    out=[]
    for t in range(1,n):
        if st[t]!=st[t-1]:
            drv = ("MACRO cap (stress)" if st[t]<dt[t] else ("DT4 regime"))
            out.append((px["time"].iloc[t],int(st[t-1]),int(st[t]),drv))
    return out
to_off=trans(m_off); to_can=trans(m_can)
# change windows: where m_can != m_off (easing floor lifting canon above off)
diff=m_can!=m_off
chg=[]; i=0
while i<n:
    if diff[i]:
        j=i
        while j<n and diff[j]: j+=1
        a,b=i,j-1
        # forward 60d VNINDEX from window start
        f60=close[min(a+60,n-1)]/close[a]-1
        chg.append((px["time"].iloc[a],px["time"].iloc[b],j-i,m_can[a],m_off[a],f60))
        i=j
    else: i+=1
print(f"transitions: OFF={len(to_off)}  CANON={len(to_can)}  | change-windows (easing lifted canon): {len(chg)}  total days {int(diff.sum())}")

def badge(s): return f"<span class='b' style='background:{COLOR[s]}'>{NAMES[s]}</span>"
rows=""
pxmap=dict(zip(px["time"],close))
for tm,fr,to,drv in to_off:
    cl="macro" if drv.startswith("MACRO") else "dt"
    rows+=f"<tr><td>{tm.date()}</td><td>{badge(fr)} → {badge(to)}</td><td>{ALLOC[to]}%</td><td>{pxmap[tm]:.2f}</td><td class='{cl}'>{drv}</td></tr>"
chg_rows=""
for a,b,d,sc,so,f60 in chg:
    col="green" if f60>0 else "red"
    chg_rows+=(f"<tr><td>{a.date()} → {b.date()}</td><td>{d}</td><td>{badge(sc)} (canon) vs {badge(so)} (off)</td>"
               f"<td class='{col}'>{f60*100:+.1f}%</td></tr>")
html=f"""<!doctype html><html><head><meta charset=utf-8><title>DT5G transitions — EASING OFF</title>
<style>body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:13px;line-height:1.6;padding:18px;max-width:1100px;margin:auto}}
h1{{font-size:20px;color:#fff}}h2{{font-size:14px;color:#94a3b8;text-transform:uppercase;letter-spacing:.05em;margin-top:24px}}
.b{{display:inline-block;padding:2px 9px;border-radius:6px;color:#fff;font-size:11px;font-weight:700}}
table{{width:100%;border-collapse:collapse;margin-top:8px}}th{{background:#1e293b;padding:7px 10px;text-align:left;color:#64748b;border-bottom:1px solid #334155;position:sticky;top:0}}
td{{padding:6px 10px;border-bottom:1px solid #1e293b}}tr:hover{{background:#1e293b}}
.macro{{color:#f59e0b}}.dt{{color:#64748b}}.green{{color:#22c55e}}.red{{color:#ef4444}}
.alert{{background:#1e3a5f;border:1px solid #3b82f6;border-radius:8px;padding:12px 16px;margin:14px 0;font-size:12.5px;color:#bfdbfe}}</style></head><body>
<h1>DT5G transitions — EASING FLOOR DISABLED (asymmetry variant)</h1>
<p style='color:#94a3b8'>DT_10_25_25 base + defensive CAP, monetary recovery FLOOR removed. Re-risk happens only via the price-based DT base. Full history {px['time'].iloc[0].date()} → {px['time'].iloc[-1].date()}. Research-only.</p>
<div class=alert><b>Deploy-decision summary:</b> OFF has <b>{len(to_off)}</b> transitions vs CANON <b>{len(to_can)}</b>.
Disabling easing changes <b>{len(chg)} window(s)</b> ({int(diff.sum())} days) — these are the spots where the canonical easing-floor lifted the state above what price/DT alone justified.
Each window's fwd-60d VNINDEX return (from window start) shows whether the floor was catching a falling knife (red = market kept falling → floor would have hurt → OFF is better) or a real bottom (green = floor helped).</div>
<h2>Change windows (easing-floor episodes removed by OFF)</h2>
<table><tr><th>Window</th><th>Days</th><th>Canon vs OFF state</th><th>VNINDEX fwd-60d from start</th></tr>{chg_rows}</table>
<h2>Full OFF transition timeline ({len(to_off)})</h2>
<table><tr><th>Date</th><th>Transition</th><th>Weight</th><th>VNINDEX</th><th>Reason</th></tr>{rows}</table>
</body></html>"""
out=os.path.join(WORKDIR,"dt4g_macro_transitions_noeasing.html")
open(out,"w",encoding="utf-8").write(html)
print(f"wrote {out}")
print("\nChange windows (canon easing-floor episodes):")
for a,b,d,sc,so,f60 in chg:
    print(f"  {a.date()} -> {b.date()} ({d}d) canon={NAMES[sc]} off={NAMES[so]}  fwd60 {f60*100:+.1f}%")
