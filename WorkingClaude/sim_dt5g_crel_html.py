# -*- coding: utf-8 -*-
"""
sim_dt5g_crel_html.py
=====================
Builds the transitions + system HTML dashboards (same dark/Chart.js template as
sim_dt4g_macro_html.py) for the NEW system = DT5G + CRISIS-RELEASE overlay,
full history 2000 -> now, 1B VND.

Pipeline = EXACT canonical DT5G (copied from export_dt5g_transitions.py: BQ VNINDEX
+ vnindex_5state_dt_4gate + macro fusion + breadth gate + cap-commit K=7 + confirmed
easing + weight-ceiling NAV), THEN apply the unconfirmed-CRISIS release overlay
(crisis_release.apply_crisis_release, NEUTRAL / K=15 / margin=3% / hold=3) to both the
PUBLISHED STATE and the ALLOCATION (0% -> NEUTRAL on confirmed-recovery days).

Outputs:
  dt5g_cr_transitions.html  — state timeline (price colored by state) + table
  dt5g_cr_system.html       — overview (state, metrics, NAV, DD, annual, dist)
  data/dt5g_cr_daily.csv     — verifiable daily (price·state·weight·NAV)
"""
import sys, io, os, json
import numpy as np, pandas as pd
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
os.chdir(WORKDIR); sys.path.insert(0, WORKDIR)
from simulate_holistic_nav import bq
from sbv_macro_overlay import SBV_REFI_EVENTS
from crisis_release import apply_crisis_release

STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
STATE_ALLOC_S = {1: "0%", 2: "20%", 3: "70%", 4: "100%", 5: "130%"}
STATE_ALLOC = {1: 0.00, 2: 0.20, 3: 0.70, 4: 1.00, 5: 1.30}
STATE_COLOR = {1: "#ef4444", 2: "#f97316", 3: "#eab308", 4: "#22c55e", 5: "#3b82f6"}
TC, TAX, BORROW, INIT = 0.001, 0.001, 0.10, 1_000_000_000
NEUTRAL, CRISIS, BEAR = 3, 1, 2
US_REFI_LAG = 5; T_DOM_MILD, T_DOM_STRONG, T_DOM_EXTREME = 0.5, 1.5, 3.0
REFI_CUT_FROM_PEAK = 0.5; CAP_COMMIT = 7
# crisis-release overlay params (validated 2026-06-02, DT engine optimum)
CR_K, CR_MARGIN, CR_HOLD = 15, 0.03, 3
VGB_1Y = {2000:.075,2001:.07,2002:.075,2003:.08,2004:.085,2005:.085,2006:.08,2007:.085,
          2008:.14,2009:.09,2010:.11,2011:.12,2012:.095,2013:.07,2014:.055,2015:.05,
          2016:.05,2017:.045,2018:.04,2019:.036,2020:.025,2021:.012,2022:.035,2023:.025,
          2024:.02,2025:.025,2026:.027}
BREADTH_TH, BREADTH_MIN_UNIVERSE = 0.50, 100

# ── data (identical to canonical DT5G) ──────────────────────────────────────
print("[1] Loading REAL BQ VNINDEX + DT4 4-gate state + US/SBV macro...")
px = bq("""SELECT p.time, p.Close, p.MA200, p.D_RSI, s.state FROM tav2_bq.ticker AS p
JOIN tav2_bq.vnindex_5state_dt_4gate AS s ON s.time=p.time
WHERE p.ticker='VNINDEX' ORDER BY p.time""")
px["time"] = pd.to_datetime(px["time"]); px["state"] = px["state"].astype(int)
px = px.dropna(subset=["Close", "state"]).sort_values("time").reset_index(drop=True)
us = pd.read_csv("us_market_history.csv", parse_dates=["time"]).sort_values("time")
key = px[["time"]].copy(); key["jt"] = key["time"] - pd.Timedelta(days=1)
um = pd.merge_asof(key.sort_values("jt"), us.rename(columns={"time": "us_time"}),
                   left_on="jt", right_on="us_time", direction="backward").sort_values("time").reset_index(drop=True)
px = px.merge(um[["time", "vix", "spx_dd_1y", "vix_ma252"]], on="time", how="left")
ev = pd.DataFrame(SBV_REFI_EVENTS, columns=["time", "refi"]); ev["time"] = pd.to_datetime(ev["time"])
dr = pd.DataFrame({"time": pd.date_range(px["time"].min(), px["time"].max(), freq="D")}).merge(ev, on="time", how="left")
dr["refi"] = dr["refi"].ffill().bfill()
px = px.merge(dr, on="time", how="left"); px["refi"] = px["refi"].ffill().bfill()
px["refi_chg6m"] = (px["refi"] - px["refi"].shift(126)).shift(US_REFI_LAG)
px["refi_peak6m"] = px["refi"].rolling(126, min_periods=20).max()
px["refi_cut"] = ((px["refi_peak6m"] - px["refi"]) >= REFI_CUT_FROM_PEAK).shift(US_REFI_LAG).fillna(False)
px["vni_r6m"] = px["Close"] / px["Close"].shift(126) - 1
px["bull"] = ((px["vni_r6m"] > 0.15) & (px["Close"] > px["MA200"])).shift(1).fillna(False)
px["us_decoupled"] = False
try:
    bd = bq(f"""SELECT t.time, AVG(IF(t.Close>t.MA200,1.0,0.0)) AS Breadth_MA200,
       COUNT(*) AS Breadth_Total_MA200
FROM tav2_bq.ticker AS t
WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
  AND t.MA200 IS NOT NULL AND t.time BETWEEN DATE '2014-01-01' AND DATE '{px["time"].max().date()}'
GROUP BY t.time ORDER BY t.time""")
    bd["time"] = pd.to_datetime(bd["time"]); px = px.merge(bd, on="time", how="left")
    px["us_decoupled"] = ((px["Breadth_Total_MA200"].fillna(0) >= BREADTH_MIN_UNIVERSE)
                          & (px["Breadth_MA200"] >= BREADTH_TH)).shift(1).fillna(False)
except Exception as e:
    print(f"[breadth guard inactive: {e}]")
n = len(px)

# ── macro fusion (canonical + gate) ─────────────────────────────────────────
vix=px["vix"].values; sdd=px["spx_dd_1y"].values; vixma=px["vix_ma252"].values
rc6=px["refi_chg6m"].values; cut=px["refi_cut"].values.astype(bool)
bull=px["bull"].values.astype(bool); decoup=px["us_decoupled"].values.astype(bool)
cap=np.full(n,9); easing=np.zeros(n,bool); src=np.array([""]*n,dtype=object)
for t in range(n):
    v,dd,vm,rr=vix[t],sdd[t],vixma[t],rc6[t]
    if bull[t] or decoup[t]: uc=ub=umn=False
    else:
        uc=(not np.isnan(dd) and dd<-0.25) or (not np.isnan(v) and v>35)
        ub=(not np.isnan(dd) and dd<-0.15) and (not np.isnan(v) and v>25)
        umn=(not np.isnan(dd) and dd<-0.10) and (not np.isnan(v) and v>20)
    de=(not np.isnan(rr) and rr>=T_DOM_EXTREME); ds=(not np.isnan(rr) and rr>=T_DOM_STRONG); dm=(not np.isnan(rr) and rr>=T_DOM_MILD)
    if uc or de: cap[t]=CRISIS; src[t]="US-crisis" if uc else "SBV-tighten-extreme"
    elif ub or ds: cap[t]=BEAR; src[t]="US-bear" if ub else "SBV-tighten-strong"
    elif umn or dm: cap[t]=NEUTRAL; src[t]="US-mild" if umn else "SBV-tighten-mild"
    calm=(not np.isnan(v) and not np.isnan(vm) and v<vm) and (not np.isnan(dd) and dd>-0.05)
    if cap[t]==9 and cut[t] and calm: easing[t]=True; src[t]="SBV-cut+US-calm"
close=px["Close"].values; persist=np.zeros(n,int)
for t in range(n): persist[t]=persist[t-1]+1 if (t>0 and easing[t]) else (1 if easing[t] else 0)
price_up=np.zeros(n,bool); price_up[10:]=close[10:]>close[:-10]
easing_conf=easing & (persist>=10) & price_up
def _commit(arr,K):
    out=arr.copy(); c=arr[0]; ps,pr=arr[0],1
    for t in range(1,len(arr)):
        if arr[t]==ps: pr+=1
        else: ps,pr=arr[t],1
        if pr>=K: c=ps
        out[t]=c
    return out
cap=_commit(cap,CAP_COMMIT)

# ── DT5G published state sm + weight + NAV (canonical) ──────────────────────
st=px["state"].values.astype(int)
sm=np.where(cap!=9,np.minimum(st,cap),st)
sm=np.where((cap==9)&easing_conf&(sm<NEUTRAL),NEUTRAL,sm).astype(int)
ma200=px["MA200"].values; rsi=px["D_RSI"].values
up_raw=(close>ma200)&(~np.isnan(ma200))&(np.nan_to_num(rsi,nan=0.0)<=0.72)
up=np.zeros(n,bool); cf=False; ru=rd=0
for t in range(n):
    if up_raw[t]: ru+=1; rd=0
    else: rd+=1; ru=0
    if not cf and ru>=10: cf=True
    elif cf and rd>=10: cf=False
    up[t]=cf
ceil=np.where(cap==9,1.30,np.array([STATE_ALLOC.get(c,1.30) for c in cap]))

def build_weight(state_disp):
    """weight from displayed state with trend overlay (NEUTRAL->0.90 in confirmed uptrend),
       then macro ceiling + easing floor. Uses the DISPLAYED state so crisis-release lifts
       0% -> NEUTRAL on released days."""
    w=np.array([STATE_ALLOC[s] for s in state_disp],float)
    w[(state_disp==NEUTRAL)&up]=0.90
    w=np.minimum(w,ceil); w=np.where(easing_conf&(w<0.70),0.70,w)
    return w

def nav_path(w):
    r=np.zeros(n); r[1:]=close[1:]/close[:-1]-1
    spy=n/((px["time"].iloc[-1]-px["time"].iloc[0]).days/365.25)
    wl=np.concatenate([[0.0],w[:-1]]); ya=px["time"].dt.year.values
    dep=np.array([VGB_1Y.get(int(y),0.001) for y in ya])
    nav=np.empty(n); nav[0]=INIT
    for t in range(n):
        ww=wl[t]; wp=wl[t-1] if t>0 else 0.0
        cfr=max(0,1-ww); lfr=max(0,ww-1); buy=max(0,ww-wp); sell=max(0,wp-ww)
        dret=ww*r[t]+cfr*dep[t]/spy-lfr*BORROW/spy-(buy+sell)*TC-sell*TAX
        if t>0: nav[t]=nav[t-1]*(1+dret)
    return nav

# baseline DT5G (no overlay)
w_dt5g=build_weight(sm); nav_dt5g=nav_path(w_dt5g)

# ── CRISIS-RELEASE overlay on published state + allocation ──────────────────
tidx=pd.DatetimeIndex(px["time"])
sm_cr=apply_crisis_release(pd.Series(sm,index=tidx), pd.Series(close,index=tidx),
                           K=CR_K, margin=CR_MARGIN, hold=CR_HOLD, downgrade_to=NEUTRAL).values.astype(int)
released = (sm_cr!=sm)                       # days the overlay lifted CRISIS->NEUTRAL
w_cr=build_weight(sm_cr)
# faithful to validated rule: released CRISIS days go to NEUTRAL *base* (0.70), NOT the
# 0.90 uptrend boost — a freshly-released de-risk re-enters cautiously (capped by macro ceil).
w_cr[released]=np.minimum(0.70, ceil[released])
w_cr=np.where(easing_conf&(w_cr<0.70),0.70,w_cr)
nav_cr=nav_path(w_cr)
print(f"  DT5G CRISIS days {int((sm==CRISIS).sum())} -> {int((sm_cr==CRISIS).sum())}  "
      f"(released {int(released.sum())} days)")

# ── assemble dataframe for HTML (model = DT5G-CR) ───────────────────────────
df=pd.DataFrame({"time":px["time"],"Close":close,"dtstate":st,"mstate":sm_cr,
                 "smbase":sm,"released":released.astype(int),
                 "cap":cap,"easing_conf":easing_conf.astype(int),
                 "w_macro":w_cr,"nav_macro":nav_cr,"nav_base":nav_dt5g,"src":src})
df["bh"]=INIT*df["Close"]/df["Close"].iloc[0]
print(f"  {n:,} sessions {df['time'].iloc[0].date()} -> {df['time'].iloc[-1].date()}")

df[["time","Close","dtstate","smbase","mstate","released","w_macro","cap","easing_conf",
    "nav_macro","nav_base","bh"]].assign(
    time=df["time"].dt.strftime("%Y-%m-%d")).to_csv("data/dt5g_cr_daily.csv",index=False)

# ── metrics ─────────────────────────────────────────────────────────────────
def metrics(navs, time):
    navs=np.asarray(navs,float); time=pd.DatetimeIndex(time)
    yrs=(time[-1]-time[0]).days/365.25
    r=np.zeros(len(navs)); r[1:]=navs[1:]/navs[:-1]-1
    spy=len(navs)/yrs; cagr=(navs[-1]/navs[0])**(1/yrs)-1
    ex=r-0.001/spy; sh=ex.mean()/ex.std()*np.sqrt(spy) if ex.std()>0 else 0
    dn=ex[ex<0]; so=ex.mean()/dn.std()*np.sqrt(spy) if len(dn) and dn.std()>0 else 0
    rmax=np.maximum.accumulate(navs); dds=(navs-rmax)/rmax; mdd=dds.min()
    under=dds<-1e-9; longest=cur=0
    for u in under: cur=cur+1 if u else 0; longest=max(longest,cur)
    return dict(cagr=cagr*100,sharpe=sh,sortino=so,mdd=mdd*100,
                calmar=cagr/(-mdd) if mdd<0 else 0,final=navs[-1]/1e9,ddur=longest)

def seg(col,a):
    s=df[(df["time"]>=a)&(df["time"]<=df["time"].iloc[-1])].reset_index(drop=True)
    nv=INIT*s[col].values/s[col].values[0]; return metrics(nv,s["time"])

mfull=metrics(df["nav_macro"].values,df["time"]); mbh=metrics(df["bh"].values,df["time"])
m11s=seg("nav_macro",pd.Timestamp("2011-01-01")); m11b=seg("bh",pd.Timestamp("2011-01-01"))
m14s=seg("nav_macro",pd.Timestamp("2014-01-01")); m14b=seg("bh",pd.Timestamp("2014-01-01"))

df["year"]=df["time"].dt.year
annual=[(int(yr),g["nav_macro"].iloc[-1]/g["nav_macro"].iloc[0]-1,g["bh"].iloc[-1]/g["bh"].iloc[0]-1)
        for yr,g in df.groupby("year") if len(g)>=5]
navm=df["nav_macro"].values; rmax=np.maximum.accumulate(navm); dd=(navm-rmax)/rmax
episodes=[]; i=0
while i<n:
    if dd[i]<-1e-9:
        j=i
        while j<n and dd[j]<-1e-9: j+=1
        s=dd[i:j]; ti=i+int(s.argmin())
        episodes.append((df["time"].iloc[i],df["time"].iloc[ti],df["time"].iloc[min(j,n-1)],float(s.min())))
        i=j
    else: i+=1
episodes=sorted([e for e in episodes if e[3]<-0.08],key=lambda x:x[3])[:8]

# ── transitions on DT5G-CR state ────────────────────────────────────────────
stt=df["mstate"].values; trans=[]
for t in range(1,n):
    if stt[t]!=stt[t-1]:
        if df["released"].iloc[t]:        drv="Crisis-release (hồi phục +3%)"
        elif sm[t]<st[t]:                 drv=f"MACRO cap → {src[t] if src[t] else 'stress'}"
        elif sm[t]>st[t]:                 drv="MACRO easing (recovery)"
        else:                             drv="DT4 regime"
        trans.append(dict(date=df["time"].iloc[t].strftime("%Y-%m-%d"),frm=int(stt[t-1]),to=int(stt[t]),
                          close=float(df["Close"].iloc[t]),drv=drv))
ntr=len(trans)
sd=pd.Series(stt).value_counts(normalize=True).sort_index()
n_macro_tr=sum(1 for t in trans if t["drv"].startswith("MACRO"))
n_cr_tr=sum(1 for t in trans if t["drv"].startswith("Crisis-release"))
cur_state=int(stt[-1]); cur_date=df["time"].iloc[-1].strftime("%Y-%m-%d")
cur_close=float(df["Close"].iloc[-1]); cur_cap=int(df["cap"].iloc[-1])
print(f"[2] metrics done. Full CAGR {mfull['cagr']:.2f}%, transitions {ntr} "
      f"({n_macro_tr} macro, {n_cr_tr} crisis-release)")

# ── JS helpers + downsample ─────────────────────────────────────────────────
def jarr(a,dec=2): return "["+",".join(("null" if (isinstance(x,float) and np.isnan(x)) else f"{x:.{dec}f}") for x in a)+"]"
def jstr(a): return json.dumps(list(a))
step=max(1,n//1200); idx=list(range(0,n,step))
if idx[-1]!=n-1: idx.append(n-1)
dates_js=jstr([df["time"].iloc[i].strftime("%Y-%m-%d") for i in idx])
navm_js=jarr([df["nav_macro"].iloc[i]/1e9 for i in idx],4)
navd_js=jarr([df["nav_base"].iloc[i]/1e9 for i in idx],4)
bh_js=jarr([df["bh"].iloc[i]/1e9 for i in idx],4)
dd_js=jarr([dd[i]*100 for i in idx],2)
ddbh=(df["bh"].values-np.maximum.accumulate(df["bh"].values))/np.maximum.accumulate(df["bh"].values)
ddbh_js=jarr([ddbh[i]*100 for i in idx],2)
price_js=jarr([df["Close"].iloc[i] for i in idx],2)
ann_years=jstr([a[0] for a in annual]); ann_sys=jarr([a[1]*100 for a in annual],1); ann_bh=jarr([a[2]*100 for a in annual],1)
dist_js=jstr([round(sd.get(s,0)*100,1) for s in [1,2,3,4,5]])
seg_color_js=jstr([STATE_COLOR[int(df["mstate"].iloc[i])] for i in idx])

CSS="""*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:13px;line-height:1.6}
.hdr{background:linear-gradient(135deg,#1e3a5f,#1a4731);padding:24px 32px}
.hdr h1{font-size:20px;font-weight:700;color:#fff;margin-bottom:4px}
.hdr p{font-size:12px;color:#94a3b8}
.wrap{max-width:1400px;margin:0 auto;padding:20px 24px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}
.card{background:#1e293b;border-radius:12px;padding:18px 20px;border:1px solid #334155}
.card h2{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em}
.chart-wrap{position:relative;height:320px}.chart-wrap-sm{position:relative;height:240px}
.state-big{display:flex;align-items:center;gap:20px;padding:8px 0}
.state-circle{width:78px;height:78px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:#fff;flex-shrink:0}
.state-info h3{font-size:24px;font-weight:800;margin-bottom:4px}.state-info p{font-size:12px;color:#94a3b8;line-height:1.7}
.kpi-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.kpi{background:#0f172a;border-radius:8px;padding:10px 12px;text-align:center}
.kpi .val{font-size:18px;font-weight:700;margin-bottom:2px}.kpi .lbl{font-size:10.5px;color:#64748b}
.green{color:#22c55e}.red{color:#ef4444}.yellow{color:#eab308}.blue{color:#60a5fa}
.badge{display:inline-block;padding:2px 8px;border-radius:6px;color:#fff;font-size:11px;font-weight:600}
table{width:100%;border-collapse:collapse;font-size:12px}
th{background:#0f172a;padding:7px 10px;text-align:left;color:#64748b;font-weight:600;border-bottom:1px solid #334155;position:sticky;top:0}
td{padding:6px 10px;border-bottom:1px solid #1e293b}tr:hover td{background:#0f172a}
.alert{background:#1e3a5f;border:1px solid #3b82f6;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#93c5fd}
.ok{background:#13241a;border:1px solid #22c55e;color:#86efac}"""

def kpis(ms,mb):
    g=lambda c:'green' if c else 'yellow'
    return f"""<div class="kpi-grid">
      <div class="kpi"><div class="val {g(ms['cagr']>mb['cagr'])}">{ms['cagr']:+.2f}%</div><div class="lbl">CAGR model</div></div>
      <div class="kpi"><div class="val blue">{mb['cagr']:+.2f}%</div><div class="lbl">CAGR B&H</div></div>
      <div class="kpi"><div class="val green">{ms['sharpe']:.2f}</div><div class="lbl">Sharpe</div></div>
      <div class="kpi"><div class="val green">{ms['sortino']:.2f}</div><div class="lbl">Sortino</div></div>
      <div class="kpi"><div class="val {g(abs(ms['mdd'])<abs(mb['mdd']))}">{ms['mdd']:+.1f}%</div><div class="lbl">Max DD</div></div>
      <div class="kpi"><div class="val green">{ms['calmar']:.2f}</div><div class="lbl">Calmar</div></div>
    </div><div style="margin-top:8px;font-size:10px;color:#64748b">NAV: <strong style="color:#22c55e">{ms['final']:.1f} tỷ</strong> · B&H {mb['final']:.1f} tỷ · DD recovery max {ms['ddur']} phiên</div>"""

# ── comparison table (DT5G-CR vs DT5G vs B&H) ───────────────────────────────
END=df["time"].iloc[-1]
def pmet(col,a):
    s=df[(df["time"]>=a)&(df["time"]<=END)].reset_index(drop=True)
    return metrics(INIT*s[col].values/s[col].values[0],s["time"])
PERIODS=[("Toàn kỳ 2000+",df["time"].iloc[0]),("Từ 2011",pd.Timestamp("2011-01-01")),("Modern 2014+",pd.Timestamp("2014-01-01"))]
cmp_rows=""
for label,a in PERIODS:
    mm=pmet("nav_macro",a); md=pmet("nav_base",a); mb=pmet("bh",a)
    cell=lambda m,c:f"<td class='{c}'>{m['cagr']:+.2f}% · Sh {m['sharpe']:.2f} · DD {m['mdd']:.1f}% · {m['final']:.1f}B</td>"
    cmp_rows+=f"<tr><td><strong>{label}</strong></td>{cell(mm,'green')}{cell(md,'yellow')}{cell(mb,'blue')}</tr>"

# ── SYSTEM HTML ─────────────────────────────────────────────────────────────
print("[3] Writing dt5g_cr_system.html...")
ep_rows="".join(f"<tr><td>{a.date()}</td><td>{t.date()}</td><td>{b.date()}</td><td class='red'>{tr*100:+.1f}%</td></tr>"
                for a,t,b,tr in episodes)
rec=("⚠ MACRO CAP đang hoạt động — giảm tỷ trọng" if cur_cap!=9 else
     f"Duy trì tỷ trọng <strong>{STATE_ALLOC_S[cur_state]}</strong> theo trạng thái {STATE_NAMES[cur_state]}")
html=f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DT5G-CR — Market System</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style></head><body>
<div class="hdr"><h1>⚡ DT5G-CR — Market System <span style="font-size:13px;color:#94a3b8;font-weight:400">(DT5G + Crisis-Release overlay)</span></h1>
<p>DT5G (DT 4-gate + macro) + overlay nhả CRISIS chưa-xác-nhận về NEUTRAL khi giá hồi +3% · giá VNINDEX THẬT từ BigQuery · 2000–{cur_date} · 1 tỷ VND · <a href="dt5g_cr_transitions.html" style="color:#60a5fa">xem transitions →</a></p></div>
<div class="wrap">
<div class="grid2">
  <div class="card"><h2>Trạng thái hiện tại — {cur_date}</h2>
    <div class="state-big">
      <div class="state-circle" style="background:{STATE_COLOR[cur_state]}">{STATE_NAMES[cur_state]}</div>
      <div class="state-info"><h3 style="color:{STATE_COLOR[cur_state]}">{STATE_NAMES[cur_state]}</h3>
        <p>Phân bổ cổ phiếu: <strong style="color:{STATE_COLOR[cur_state]}">{STATE_ALLOC_S[cur_state]}</strong><br>
        VNINDEX: <strong>{cur_close:.2f}</strong><br>
        Macro cap: <strong class="{'red' if cur_cap!=9 else 'green'}">{'ĐANG CAP' if cur_cap!=9 else 'Không (bình thường)'}</strong></p></div>
    </div>
    <div class="alert">💡 <strong>Khuyến nghị:</strong> {rec}</div>
  </div>
  <div class="card ok" style="background:#13241a;border-color:#22c55e"><h2 style="color:#86efac">✔ Kiểm chứng dữ liệu thật</h2>
    <p style="font-size:12px;line-height:1.9">
    • Giá VNINDEX: <strong>tav2_bq.ticker</strong> (ticker='VNINDEX') — {n:,} phiên thật<br>
    • DT4 state: <strong>tav2_bq.vnindex_5state_dt_4gate</strong><br>
    • DT5G macro: SBV refi + US VIX/SPX + breadth gate (cap-commit K=7)<br>
    • <strong>Crisis-Release overlay</strong>: nhả CRISIS→NEUTRAL khi (≥{CR_K} phiên) & (giá ≥ mức vào +{CR_MARGIN:.0%}, giữ {CR_HOLD} phiên) & không macro<br>
    • Nhân quả, không look-ahead · mọi dòng ngày: <strong>data/dt5g_cr_daily.csv</strong></p>
  </div>
</div>
<div class="grid3">
  <div class="card"><h2>Toàn kỳ 2000–nay</h2>{kpis(mfull,mbh)}</div>
  <div class="card"><h2>Từ 2011</h2>{kpis(m11s,m11b)}</div>
  <div class="card"><h2>Modern 2014–nay</h2>{kpis(m14s,m14b)}</div>
</div>
<div class="card" style="margin-bottom:16px"><h2>So sánh gộp — DT5G-CR vs DT5G vs B&amp;H (CAGR · Sharpe · MaxDD · NAV cuối)</h2>
  <table><tr><th>Giai đoạn</th><th class="green">DT5G-CR (model)</th><th class="yellow">DT5G (no overlay)</th><th class="blue">VNINDEX Buy&amp;Hold</th></tr>
  {cmp_rows}</table>
  <div style="margin-top:8px;font-size:11px;color:#64748b">Mỗi giai đoạn re-base 1 tỷ. Overlay nhả {int(released.sum())} phiên CRISIS chưa-xác-nhận về NEUTRAL.</div>
</div>
<div class="grid2">
  <div class="card"><h2>NAV — DT5G-CR vs DT5G vs Buy&Hold (log)</h2><div class="chart-wrap"><canvas id="cNav"></canvas></div></div>
  <div class="card"><h2>Drawdown (%)</h2><div class="chart-wrap"><canvas id="cDD"></canvas></div></div>
</div>
<div class="grid2">
  <div class="card"><h2>Lợi nhuận theo năm: Model vs B&H</h2><div class="chart-wrap"><canvas id="cAnn"></canvas></div></div>
  <div class="card"><h2>Phân bố trạng thái (% phiên)</h2><div class="chart-wrap"><canvas id="cDist"></canvas></div></div>
</div>
<div class="grid2">
  <div class="card"><h2>Các đợt sụt giảm lớn nhất (model NAV)</h2>
    <table><tr><th>Bắt đầu</th><th>Đáy</th><th>Hồi phục</th><th>DD đáy</th></tr>{ep_rows}</table></div>
  <div class="card"><h2>Hoạt động hệ thống</h2>
    <p style="font-size:13px;line-height:2">
    Tổng transitions: <strong style="color:#60a5fa">{ntr}</strong> ({ntr/((df['time'].iloc[-1]-df['time'].iloc[0]).days/365.25):.1f}/năm)<br>
    Do MACRO: <strong style="color:#f97316">{n_macro_tr}</strong> · do Crisis-Release: <strong style="color:#eab308">{n_cr_tr}</strong><br>
    NAV cuối model: <strong class="green">{mfull['final']:.1f} tỷ</strong> (B&H {mbh['final']:.1f} tỷ)<br>
    MaxDD model: <strong class="green">{mfull['mdd']:.1f}%</strong> vs B&H <strong class="red">{mbh['mdd']:.1f}%</strong></p></div>
</div>
</div>
<script>
const D={dates_js};
function mk(id,type,data,opts){{new Chart(document.getElementById(id),{{type:type,data:data,options:Object.assign({{responsive:true,maintainAspectRatio:false,interaction:{{intersect:false,mode:'index'}},plugins:{{legend:{{labels:{{color:'#94a3b8',boxWidth:12,font:{{size:11}}}}}}}}}},opts||{{}})}});}}
const gx={{ticks:{{color:'#64748b',maxTicksLimit:10,font:{{size:10}}}},grid:{{color:'#1e293b'}}}};
mk('cNav','line',{{labels:D,datasets:[
 {{label:'DT5G-CR',data:{navm_js},borderColor:'#22c55e',borderWidth:1.5,pointRadius:0,tension:0}},
 {{label:'DT5G',data:{navd_js},borderColor:'#eab308',borderWidth:1,pointRadius:0,tension:0,borderDash:[4,3]}},
 {{label:'Buy&Hold',data:{bh_js},borderColor:'#60a5fa',borderWidth:1,pointRadius:0,tension:0}}]}},
 {{scales:{{x:gx,y:{{type:'logarithmic',ticks:{{color:'#64748b',font:{{size:10}}}},grid:{{color:'#1e293b'}}}}}}}});
mk('cDD','line',{{labels:D,datasets:[
 {{label:'DT5G-CR',data:{dd_js},borderColor:'#22c55e',backgroundColor:'rgba(34,197,94,.12)',fill:true,borderWidth:1,pointRadius:0}},
 {{label:'Buy&Hold',data:{ddbh_js},borderColor:'#ef4444',borderWidth:1,pointRadius:0}}]}},
 {{scales:{{x:gx,y:gx}}}});
mk('cAnn','bar',{{labels:{ann_years},datasets:[
 {{label:'Model',data:{ann_sys},backgroundColor:'#22c55e'}},
 {{label:'B&H',data:{ann_bh},backgroundColor:'#60a5fa'}}]}},{{scales:{{x:gx,y:gx}}}});
mk('cDist','doughnut',{{labels:['CRISIS','BEAR','NEUTRAL','BULL','EX-BULL'],datasets:[
 {{data:{dist_js},backgroundColor:['#ef4444','#f97316','#eab308','#22c55e','#3b82f6']}}]}},
 {{scales:{{}},cutout:'55%'}});
</script></body></html>"""
with open(os.path.join(WORKDIR,"dt5g_cr_system.html"),"w",encoding="utf-8") as f: f.write(html)

# ── TRANSITIONS HTML ────────────────────────────────────────────────────────
print("[4] Writing dt5g_cr_transitions.html...")
def badge(s): return f"<span class='badge' style='background:{STATE_COLOR[s]}'>{STATE_NAMES[s]}</span>"
trows="".join(
    f"<tr><td>{t['date']}</td><td>{badge(t['frm'])} → {badge(t['to'])}</td>"
    f"<td>{STATE_ALLOC_S[t['to']]}</td><td>{t['close']:.2f}</td>"
    f"<td style=\"color:{'#eab308' if t['drv'].startswith('Crisis-release') else ('#f97316' if t['drv'].startswith('MACRO') else '#94a3b8')}\">{t['drv']}</td></tr>"
    for t in reversed(trans))
tjs=("const D=__D__,P=__P__,SC=__SC__;"
     "new Chart(document.getElementById('cPrice'),{type:'line',data:{labels:D,datasets:[{"
     "label:'VNINDEX',data:P,borderWidth:1.5,pointRadius:0,tension:0,"
     "segment:{borderColor:ctx=>SC[ctx.p0DataIndex]}}]},"
     "options:{responsive:true,maintainAspectRatio:false,plugins:{legend:{display:false}},"
     "scales:{x:{ticks:{color:'#64748b',maxTicksLimit:12,font:{size:10}},grid:{color:'#1e293b'}},"
     "y:{type:'logarithmic',ticks:{color:'#64748b',font:{size:10}},grid:{color:'#1e293b'}}}}});")
tjs=tjs.replace("__D__",dates_js).replace("__P__",price_js).replace("__SC__",seg_color_js)
thtml=f"""<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DT5G-CR — Transitions</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>{CSS}</style></head><body>
<div class="hdr"><h1>🔄 DT5G-CR — State Transitions</h1>
<p>VNINDEX thật tô màu theo trạng thái · {ntr} transitions (2000–{cur_date}) · {n_macro_tr} do macro · {n_cr_tr} do crisis-release · <a href="dt5g_cr_system.html" style="color:#60a5fa">← system overview</a></p></div>
<div class="wrap">
<div class="card" style="margin-bottom:16px"><h2>VNINDEX (thật) tô màu theo trạng thái DT5G-CR</h2>
  <div style="margin-bottom:8px">{' '.join(f'<span class="badge" style="background:{STATE_COLOR[s]}">{STATE_NAMES[s]} {STATE_ALLOC_S[s]}</span>' for s in [1,2,3,4,5])}</div>
  <div class="chart-wrap" style="height:380px"><canvas id="cPrice"></canvas></div></div>
<div class="card"><h2>Bảng transitions ({ntr}) — mới nhất trước</h2>
  <div style="max-height:560px;overflow:auto">
  <table><tr><th>Ngày</th><th>Chuyển trạng thái</th><th>Phân bổ</th><th>VNINDEX</th><th>Nguyên nhân</th></tr>
  {trows}</table></div></div>
</div>
<script>{tjs}</script></body></html>"""
with open(os.path.join(WORKDIR,"dt5g_cr_transitions.html"),"w",encoding="utf-8") as f: f.write(thtml)

print("\n"+"="*78)
print(f"  DT5G-CR 2000-now: CAGR {mfull['cagr']:+.2f}%  Sharpe {mfull['sharpe']:.2f}  "
      f"MaxDD {mfull['mdd']:.1f}%  NAV {mfull['final']:.1f}B  (B&H {mbh['final']:.1f}B)")
print(f"  vs DT5G (no overlay): CAGR {metrics(df['nav_base'].values,df['time'])['cagr']:+.2f}%  "
      f"NAV {metrics(df['nav_base'].values,df['time'])['final']:.1f}B")
print(f"  Transitions {ntr} ({n_macro_tr} macro, {n_cr_tr} crisis-release); released {int(released.sum())} CRISIS days")
print("="*78)
print("  → dt5g_cr_transitions.html\n  → dt5g_cr_system.html\n  → data/dt5g_cr_daily.csv")
print("DONE.")
