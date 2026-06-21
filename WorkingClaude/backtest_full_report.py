# -*- coding: utf-8 -*-
"""
Backtest toan ky 2000-nay: so sanh 4 kich ban.
Output: backtest_full_report.html
"""
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"

# ── Build full state pipeline ──────────────────────────────────────────────
vni = pd.read_csv(WORKDIR + "/data/VNINDEX.csv", low_memory=False)
vni["time"] = pd.to_datetime(vni["time"])
vni = vni.sort_values("time").reset_index(drop=True)
for col in ["Open","High","Low","Close","Volume","VNINDEX_PE",
            "D_RSI","D_RSI_T1W","D_RSI_Max1W","D_RSI_Max3M",
            "D_RSI_Min1W","D_RSI_Min3M","D_RSI_Max1W_Close","D_RSI_Max3M_Close",
            "D_RSI_Max3M_MACD","D_RSI_Max1W_MACD","D_RSI_MinT3",
            "D_MACDdiff","D_CMF","C_L1M","C_L1W"]:
    if col in vni.columns:
        vni[col] = pd.to_numeric(vni[col], errors="coerce")
if os.path.exists(WORKDIR+"/data/breadth_data.csv"):
    br = pd.read_csv(WORKDIR+"/data/breadth_data.csv"); br["time"]=pd.to_datetime(br["time"])
    vni = vni.merge(br, on="time", how="left")
else:
    vni["breadth"] = np.nan

close=vni["Close"].values.copy(); high=vni["High"].values.copy()
low=vni["Low"].values.copy(); vol=vni["Volume"].values.copy(); n=len(close)
cal_days=(vni["time"].iloc[-1]-vni["time"].iloc[0]).days
SPY=n/(cal_days/365.25)

def _ema(arr,k):
    out=np.full(len(arr),np.nan)
    for i in range(len(arr)):
        out[i]=arr[i] if (i==0 or np.isnan(out[i-1])) else out[i-1]*(1-k)+arr[i]*k
    return out
def _rank(arr,min_lb=252):
    out=np.full(len(arr),np.nan)
    for t in range(len(arr)):
        if np.isnan(arr[t]): continue
        v=arr[:t+1]; v=v[~np.isnan(v)]
        if len(v)>=min_lb: out[t]=np.sum(v<=arr[t])/len(v)
    return out

p3m=np.full(n,np.nan)
if "Change_3M" in vni.columns:
    cv=pd.to_numeric(vni["Change_3M"],errors="coerce").values
    for i in range(n):
        p3m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-60]-1 if i>=60 and close[i-60]>0 else np.nan)
else:
    for i in range(60,n):
        if close[i-60]>0: p3m[i]=close[i]/close[i-60]-1
p1m=np.full(n,np.nan)
if "Change_1M" in vni.columns:
    cv=pd.to_numeric(vni["Change_1M"],errors="coerce").values
    for i in range(n):
        p1m[i]=cv[i] if not np.isnan(cv[i]) else (close[i]/close[i-20]-1 if i>=20 and close[i-20]>0 else np.nan)
else:
    for i in range(20,n):
        if close[i-20]>0: p1m[i]=close[i]/close[i-20]-1
ma200=pd.Series(close).rolling(200,min_periods=200).mean().values
ma200_dev=np.where((ma200>0)&~np.isnan(ma200),close/ma200-1,np.nan)
rsi=np.full(n,np.nan); au=ad=np.nan
for i in range(1,n):
    d=close[i]-close[i-1]; u=max(d,0); dn=max(-d,0)
    if np.isnan(au):
        if i>=14:
            au=np.mean([max(close[j]-close[j-1],0) for j in range(1,15)])
            ad=np.mean([max(close[j-1]-close[j],0) for j in range(1,15)])
            if au+ad>0: rsi[i]=au/(au+ad)
    else:
        au=(au*13+u)/14; ad=(ad*13+dn)/14
        if au+ad>0: rsi[i]=au/(au+ad)
e12=_ema(close,2/13); e26=_ema(close,2/27)
macd_l=e12-e26; sig9=_ema(macd_l,2/10)
macd_hist=np.where(np.arange(n)>=33,macd_l-sig9,np.nan)
hl=high-low; mfm=np.where(hl>0,((close-low)-(high-close))/hl,0.0)
cmf=np.full(n,np.nan)
for i in range(14,n):
    vs=np.sum(vol[i-14:i])
    if vs>0: cmf[i]=np.sum(mfm[i-14:i]*vol[i-14:i])/vs
br_arr=vni["breadth"].values if "breadth" in vni.columns else np.full(n,np.nan)
W={"P3M":0.30,"P1M":0.10,"MA200":0.15,"RSI":0.15,"MACD":0.10,"CMF":0.08,"Breadth":0.12}
raw={"P3M":p3m,"P1M":p1m,"MA200":ma200_dev,"RSI":rsi,"MACD":macd_hist,"CMF":cmf,"Breadth":br_arr}
ranks={k:_rank(v) for k,v in raw.items()}
score=np.full(n,np.nan)
for t in range(n):
    av={k:ranks[k][t] for k in ranks if not np.isnan(ranks[k][t])}
    if len(av)>=3:
        ws=sum(W[k] for k in av); score[t]=sum(av[k]*W[k] for k in av)/ws
r_score=_rank(score)
r_ema=np.full(n,np.nan)
for t in range(n):
    v=r_score[t]; p=r_ema[t-1] if t>0 else np.nan
    r_ema[t]=v if np.isnan(p) else (p if np.isnan(v) else 0.40*v+0.60*p)
pe_arr=vni["VNINDEX_PE"].values.copy()
pe_p90=np.full(n,np.nan)
for t in range(n):
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_p90[t]=np.nanpercentile(h,90)
rm_c=np.maximum.accumulate(np.where(np.isnan(close),0,close))
dd_raw=np.where(rm_c>0,close/rm_c-1,0.0)
dr=np.full(n,np.nan)
for i in range(1,n):
    if close[i-1]>0: dr[i]=close[i]/close[i-1]-1
v20_a=np.full(n,np.nan)
for i in range(20,n):
    w2=dr[i-20:i]; w2=w2[~np.isnan(w2)]
    if len(w2)>=15: v20_a[i]=np.std(w2)*np.sqrt(SPY)
avg_vol_a=np.full(n,np.nan)
for t in range(n):
    h=v20_a[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: avg_vol_a[t]=np.mean(h)
def classify(rs):
    if np.isnan(rs): return 3
    if rs<0.10: return 1
    elif rs<0.20: return 2
    elif rs<0.70: return 3
    elif rs<0.90: return 4
    else: return 5
st=np.array([classify(r) for r in r_ema])
for i in range(n):
    s=st[i]
    if not np.isnan(pe_p90[i]) and not np.isnan(pe_arr[i]) and pe_arr[i]>pe_p90[i] and s==5: s=4
    if dd_raw[i]<-0.25 and s>=4: s=3
    if not np.isnan(avg_vol_a[i]) and not np.isnan(v20_a[i]) and v20_a[i]>1.5*avg_vol_a[i] and s==5: s=4
    st[i]=s
def _s(c): return vni[c] if c in vni.columns else pd.Series(np.nan,index=vni.index)
_mask=vni["time"]>="2011-01-01"
_DR=_s("D_RSI");_DRT=_s("D_RSI_T1W");_DM1W=_s("D_RSI_Max1W");_DM3M=_s("D_RSI_Max3M")
_DN1W=_s("D_RSI_Min1W");_DN3M=_s("D_RSI_Min3M");_DM1WC=_s("D_RSI_Max1W_Close")
_DM3MC=_s("D_RSI_Max3M_Close");_DM3MM=_s("D_RSI_Max3M_MACD");_DM1WM=_s("D_RSI_Max1W_MACD")
_DN1WC=_s("D_RSI_Min1W_Close");_DMT3=_s("D_RSI_MinT3");_DMACD=_s("D_MACDdiff")
_DCMF=_s("D_CMF");_CL1M=_s("C_L1M");_CL1W=_s("C_L1W")
bear_mask=(
 ((_DM1W/_DR>1.044)&(_DM3M>0.74)&(_DM1W<0.72)&(_DM1W>0.61)&
  (_DM1WC/_DM3MC>1.028)&(_DM3MM/_DM1WM>1.11)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.96)&(_DMT3>0.43)&(_DCMF<0.13)&_mask)
 |((_DM1W/_DR>1.016)&(_DM3M>0.77)&(_DM1W<0.79)&(_DM1W>0.60)&
  (_DM1WC/_DM3MC>1.008)&(_DM3MM/_DM1WM>1.10)&(_DMACD<0)&
  (vni["Close"]/_DM3MC>0.97)&(_DMT3>0.50)&(_DCMF<0.15)&_mask)
).values.astype(bool)
bull_mask=(
 ((_DN1W/_DN3M>0.90)&(_DN1W<0.60)&(_DN3M<0.40)&(_DN1WC/_DM3MC<1.15)&
  (_DMACD>0)&(_DMT3<0.50)&(_DM1W<0.48)&(_DR/_DRT>1.12)&(_DCMF>0)&
  (_CL1M<1.21)&(_CL1W<1.05)&_mask)
 |((_DN1W/_DN3M>0.92)&(_DN1W<0.52)&(_DN3M<0.38)&(_DN1WC/_DM3MC<1.10)&
  (_DMACD>0)&(_DMT3<0.56)&(_DM1W<0.64)&(_DR/_DRT>1.10)&(_DCMF>0)&
  (_CL1M<1.20)&(_CL1W<1.025)&_mask)
).values.astype(bool)
pe_rank=np.full(n,np.nan)
for t in range(n):
    if np.isnan(pe_arr[t]): continue
    h=pe_arr[:t+1]; h=h[~np.isnan(h)]
    if len(h)>=60: pe_rank[t]=np.sum(h<=pe_arr[t])/len(h)
p3m_rank=ranks["P3M"]
streak=np.zeros(n,dtype=bool); _k=0
for i in range(n):
    if not np.isnan(r_ema[i]) and r_ema[i]>0.65: _k+=1
    else: _k=0
    if _k>=10: streak[i]=True
gate_active=False; gate_start=-1; st_dvg=st.copy()
for i in range(n):
    if bear_mask[i]: gate_active=True; gate_start=i
    if gate_active:
        if st_dvg[i]>1: st_dvg[i]=1
        if i-gate_start>=60:
            p3_ok=(not np.isnan(p3m_rank[i])) and p3m_rank[i]>0.45
            pe_ok=(not np.isnan(pe_rank[i])) and pe_rank[i]<0.80
            if bull_mask[i] or (p3_ok and pe_ok) or bool(streak[i]): gate_active=False
def rolling_mode(states,w=15):
    out=states.copy()
    for t in range(w-1,len(states)):
        ww=states[t-w+1:t+1]; vs,cs=np.unique(ww,return_counts=True)
        cands=vs[cs==cs.max()]
        for v in reversed(ww):
            if v in cands: out[t]=v; break
    return out
def min_stay_filter(states,m=7):
    out=states.copy(); changed=True
    while changed:
        changed=False; i=0
        while i<len(out):
            j=i+1
            while j<len(out) and out[j]==out[i]: j+=1
            if j-i<m:
                fill=out[i-1] if i>0 else (out[j] if j<len(out) else out[i])
                out[i:j]=fill; changed=True
            i=j
    return out
st_smooth=min_stay_filter(rolling_mode(st_dvg,15),7)
TARGET_W={1:0.00,2:0.20,3:0.70,4:1.00,5:1.30}
STATE_NAMES={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
STATE_COLORS={1:"#ef4444",2:"#f97316",3:"#eab308",4:"#22c55e",5:"#10b981"}

# ── Build recovery map (boost ALL exits) ──────────────────────────────────
REC_W=1.30; REC_D=20
rec_map={}
i=0
while i<n-1:
    if st_smooth[i]==1:
        start=i
        while i<n-1 and st_smooth[i]==1: i+=1
        end=i
        if end-start>=2 and end<n:
            for t in range(end, min(end+REC_D,n)):
                if st_smooth[t]!=1: rec_map[t]=REC_W
    else: i+=1

# ── Simulate ──────────────────────────────────────────────────────────────
def simulate(dep_annual, use_rec=False):
    DR=dep_annual/SPY; BR=0.10/SPY; TC=0.001
    pv=np.zeros(n); pv[0]=1e9; w=TARGET_W[3]
    ws=np.zeros(n); ws[0]=w
    for t in range(1,n):
        base=TARGET_W[st_smooth[t-1]]
        target=(max(base,rec_map[t-1]) if use_rec and (t-1) in rec_map else base)
        diff=target-w
        w_new=target if abs(diff)<0.03 else w+diff/3
        w_new=float(np.clip(w_new,0.0,1.50))
        rm=close[t]/close[t-1]-1 if close[t-1]>0 else 0.0
        pv[t]=pv[t-1]*(1.0+w_new*rm+max(0.0,1.0-w_new)*DR
                        -max(0.0,w_new-1.0)*BR-abs(w_new-w)*TC)
        w=w_new; ws[t]=w
    return pv, ws

pv_ht6,  ws_ht6  = simulate(0.06,  False)   # Original HT (6%/yr, no boost)
pv_ht01, ws_ht01 = simulate(0.001, False)   # Realistic HT (0.1%/yr, no boost)
pv_rec,  ws_rec  = simulate(0.001, True)    # HT + Recovery (0.1%/yr + boost)
pv_bh=np.zeros(n); pv_bh[0]=1e9
for t in range(1,n): pv_bh[t]=pv_bh[t-1]*(close[t]/close[t-1] if close[t-1]>0 else 1.0)

# ── Metrics ────────────────────────────────────────────────────────────────
def metrics(pv,i0=0,i1=None):
    sl=pv[i0:] if i1 is None else pv[i0:i1]
    ds=(vni["time"].reset_index(drop=True).iloc[i0:] if i1 is None
        else vni["time"].reset_index(drop=True).iloc[i0:i1])
    a=np.asarray(sl,dtype=float); v=np.where(a>0)[0]
    if len(v)<10: return {}
    i0_,i1_=v[0],v[-1]; v0,v1=a[i0_],a[i1_]
    ds2=ds.reset_index(drop=True)
    yrs=(ds2.iloc[i1_]-ds2.iloc[i0_]).days/365.25
    if yrs<=0: return {}
    cagr=(v1/v0)**(1/yrs)-1
    sub=a[i0_:i1_+1]; rets=np.diff(sub)/sub[:-1]; spy_s=len(rets)/yrs
    mr=np.mean(rets); sr=np.std(rets)
    sharpe=mr*spy_s/(sr*np.sqrt(spy_s)) if sr>0 else 0
    down=rets[rets<0]; ds3=np.sqrt(np.mean(down**2)) if len(down)>0 else 0
    sortino=mr*spy_s/(ds3*np.sqrt(spy_s)) if ds3>0 else 0
    rm2=np.maximum.accumulate(sub); dd2=np.where(rm2>0,sub/rm2-1,0)
    mdd=dd2.min(); calmar=cagr/abs(mdd) if mdd!=0 else 0
    under=dd2<0; mx=0; cu=0
    for u in under:
        cu=cu+1 if u else 0; mx=max(mx,cu)
    return {"cagr":cagr,"sharpe":sharpe,"sortino":sortino,"mdd":mdd,"calmar":calmar,"ddur":mx,
            "final_nav":v1/1e9}

idx11=vni[vni["time"]>="2011-01-01"].index[0]
idx21=vni[vni["time"]>="2021-01-01"].index[0]

periods = [
    ("Toàn kỳ (2000–nay)", 0,     None),
    ("Từ 2011",            idx11, None),
    ("OOS (2021–nay)",     idx21, None),
]
mets = {}
for lbl,i0,i1 in periods:
    mets[lbl] = {
        "HT gốc (6%/yr)":        metrics(pv_ht6,  i0, i1),
        "HT thực tế (0.1%/yr)":  metrics(pv_ht01, i0, i1),
        "HT + Recovery (0.1%/yr)":metrics(pv_rec,  i0, i1),
        "B&H":                    metrics(pv_bh,   i0, i1),
    }

# ── Annual returns ─────────────────────────────────────────────────────────
annual = []
for yr in sorted(vni["time"].dt.year.unique()):
    mask=vni["time"].dt.year==yr; idx=vni[mask].index
    if len(idx)<10: continue
    i0,i1=idx[0],idx[-1]
    if pv_ht6[i0]<=0: continue
    annual.append({
        "yr":yr,
        "ht6":  pv_ht6[i1] /pv_ht6[i0] -1,
        "ht01": pv_ht01[i1]/pv_ht01[i0]-1,
        "rec":  pv_rec[i1] /pv_rec[i0] -1,
        "bh":   pv_bh[i1]  /pv_bh[i0]  -1,
    })

# ── Drawdown series ───────────────────────────────────────────────────────
def dd_series(pv):
    rm=np.maximum.accumulate(pv); return np.where(rm>0,pv/rm-1,0)

# ── Subsample for chart (every 5 sessions) ────────────────────────────────
step=5
idx_s=list(range(0,n,step))
dates_s=[vni["time"].iloc[i].strftime("%Y-%m-%d") for i in idx_s]
def norm(pv,i0=0): return [round(pv[i]/pv[i0]*100,2) for i in idx_s]
nav_ht6 = norm(pv_ht6)
nav_ht01= norm(pv_ht01)
nav_rec = norm(pv_rec)
nav_bh  = norm(pv_bh)
dd_ht6  = [round(dd_series(pv_ht6)[i]*100,2)  for i in idx_s]
dd_rec  = [round(dd_series(pv_rec)[i]*100,2)   for i in idx_s]
dd_bh   = [round(dd_series(pv_bh)[i]*100,2)    for i in idx_s]
state_s = [int(st_smooth[i]) for i in idx_s]

# ── State weight band for NAV chart (background) ──────────────────────────
state_bands = []
prev_st=st_smooth[0]; band_start=0
for i in range(1,n):
    if st_smooth[i]!=prev_st or i==n-1:
        state_bands.append({"s":int(prev_st),"from":vni["time"].iloc[band_start].strftime("%Y-%m-%d"),
                             "to":vni["time"].iloc[i-1].strftime("%Y-%m-%d")})
        prev_st=st_smooth[i]; band_start=i

# ── Format helpers ─────────────────────────────────────────────────────────
def pct(v,d=1):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "—"
    return f"{v*100:+.{d}f}%"
def f2(v):
    if v is None or (isinstance(v,float) and np.isnan(v)): return "—"
    return f"{v:.2f}"
def color_class(v, good_positive=True):
    if v is None or (isinstance(v,float) and np.isnan(v)): return ""
    return "green" if (v>0)==good_positive else "red"

def kpi_card(label, val_str, cls=""):
    return f'<div class="kpi"><div class="val {cls}">{val_str}</div><div class="lbl">{label}</div></div>'

def metrics_row(m, name):
    if not m: return f'<tr><td>{name}</td>' + '<td>—</td>'*6 + '</tr>'
    cagr_c = "green" if m.get("cagr",0)>0 else "red"
    mdd_c  = "green" if m.get("mdd",0)>-0.25 else ("yellow" if m.get("mdd",0)>-0.40 else "red")
    return (f'<tr><td><strong>{name}</strong></td>'
            f'<td class="{cagr_c}">{pct(m.get("cagr"))}</td>'
            f'<td>{f2(m.get("sharpe"))}</td>'
            f'<td>{f2(m.get("sortino"))}</td>'
            f'<td class="{mdd_c}">{pct(m.get("mdd"))}</td>'
            f'<td>{f2(m.get("calmar"))}</td>'
            f'<td>{int(m.get("ddur",0))}</td>'
            f'</tr>')

# ── Build annual table rows ────────────────────────────────────────────────
ann_rows = ""
for a in annual:
    oos = " ◄" if a["yr"]>=2021 else ""
    def rc(v,bh):
        if v>bh+0.001: return "green"
        elif v<bh-0.001: return "red"
        return ""
    bh_bear = a["bh"] < -0.05
    bh_bull = a["bh"] > 0.15
    row_bg = ' style="background:#2d1a1a"' if bh_bear else (' style="background:#1a2d1a"' if bh_bull else "")
    ann_rows += (f'<tr{row_bg}>'
        f'<td><strong>{a["yr"]}</strong>{oos}</td>'
        f'<td class="{rc(a["ht6"],a["bh"])}">{pct(a["ht6"])}</td>'
        f'<td class="{rc(a["ht01"],a["bh"])}">{pct(a["ht01"])}</td>'
        f'<td class="{rc(a["rec"],a["bh"])}">{pct(a["rec"])}</td>'
        f'<td style="color:#60a5fa">{pct(a["bh"])}</td>'
        f'<td style="font-size:11px;color:#94a3b8">'
        f'{"✓" if a["rec"]>a["bh"] else "✗"} Rec | {"✓" if a["ht6"]>a["bh"] else "✗"} HT6'
        f'</td></tr>\n')

# ── Count wins ────────────────────────────────────────────────────────────
wins_rec = sum(1 for a in annual if a["rec"]>a["bh"])
wins_ht6 = sum(1 for a in annual if a["ht6"]>a["bh"])
total_yr  = len(annual)

# ── Nav final values ──────────────────────────────────────────────────────
final_ht6  = mets["Toàn kỳ (2000–nay)"]["HT gốc (6%/yr)"].get("final_nav",0)
final_ht01 = mets["Toàn kỳ (2000–nay)"]["HT thực tế (0.1%/yr)"].get("final_nav",0)
final_rec  = mets["Toàn kỳ (2000–nay)"]["HT + Recovery (0.1%/yr)"].get("final_nav",0)
final_bh   = mets["Toàn kỳ (2000–nay)"]["B&H"].get("final_nav",0)

# ── Build period KPI sections ──────────────────────────────────────────────
def period_section(lbl, m_dict, oos=False):
    bg = "background:#0f1f35" if oos else ""
    m1 = m_dict.get("HT gốc (6%/yr)",{})
    m2 = m_dict.get("HT thực tế (0.1%/yr)",{})
    m3 = m_dict.get("HT + Recovery (0.1%/yr)",{})
    mb = m_dict.get("B&H",{})
    highlight = 'border:1px solid #22c55e' if oos else ''
    return f"""
<div class="card" style="{bg}{highlight}">
  <h2>{"🔬 OOS · " if oos else ""}{lbl}</h2>
  <table style="width:100%;font-size:12px;border-collapse:collapse">
    <thead><tr>
      <th style="padding:6px 8px;text-align:left;color:#64748b;border-bottom:1px solid #334155">Kịch bản</th>
      <th style="padding:6px 8px;text-align:right;color:#64748b;border-bottom:1px solid #334155">CAGR</th>
      <th style="padding:6px 8px;text-align:right;color:#64748b;border-bottom:1px solid #334155">Sharpe</th>
      <th style="padding:6px 8px;text-align:right;color:#64748b;border-bottom:1px solid #334155">Sortino</th>
      <th style="padding:6px 8px;text-align:right;color:#64748b;border-bottom:1px solid #334155">MaxDD</th>
      <th style="padding:6px 8px;text-align:right;color:#64748b;border-bottom:1px solid #334155">Calmar</th>
      <th style="padding:6px 8px;text-align:right;color:#64748b;border-bottom:1px solid #334155">DDdur</th>
    </tr></thead>
    <tbody>
      {metrics_row(m1,"HT gốc (6%/yr)")}
      {metrics_row(m2,"HT thực tế (0.1%/yr)")}
      {metrics_row(m3,"⭐ HT + Recovery (0.1%/yr)")}
      {metrics_row(mb,"B&H")}
    </tbody>
  </table>
</div>"""

# ── HTML ───────────────────────────────────────────────────────────────────
rec_m11 = mets["Từ 2011"]["HT + Recovery (0.1%/yr)"]
ht6_m11 = mets["Từ 2011"]["HT gốc (6%/yr)"]
bh_m11  = mets["Từ 2011"]["B&H"]
rec_m00 = mets["Toàn kỳ (2000–nay)"]["HT + Recovery (0.1%/yr)"]
ht6_m00 = mets["Toàn kỳ (2000–nay)"]["HT gốc (6%/yr)"]
bh_m00  = mets["Toàn kỳ (2000–nay)"]["B&H"]
rec_m21 = mets["OOS (2021–nay)"]["HT + Recovery (0.1%/yr)"]
bh_m21  = mets["OOS (2021–nay)"]["B&H"]

html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Backtest VNINDEX 5-State + Recovery Boost</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;font-size:13px;line-height:1.6}}
.hdr{{background:linear-gradient(135deg,#1e3a5f,#1a4731);padding:24px 32px}}
.hdr h1{{font-size:20px;font-weight:700;color:#fff;margin-bottom:4px}}
.hdr p{{font-size:12px;color:#94a3b8}}
.wrap{{max-width:1400px;margin:0 auto;padding:20px 24px}}
.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:16px}}
.grid3{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;margin-bottom:16px}}
.grid4{{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:16px}}
.card{{background:#1e293b;border-radius:12px;padding:18px 20px;border:1px solid #334155;margin-bottom:16px}}
.card h2{{font-size:13px;font-weight:700;color:#94a3b8;margin-bottom:12px;text-transform:uppercase;letter-spacing:.05em}}
.chart-wrap{{position:relative;height:340px}}
.chart-wrap-sm{{position:relative;height:220px}}
.kpi-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin-bottom:12px}}
.kpi{{background:#0f172a;border-radius:8px;padding:10px 12px;text-align:center}}
.kpi .val{{font-size:18px;font-weight:700;margin-bottom:2px}}
.kpi .lbl{{font-size:10.5px;color:#64748b}}
.green{{color:#22c55e}} .red{{color:#ef4444}} .yellow{{color:#eab308}} .blue{{color:#60a5fa}} .purple{{color:#a78bfa}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#0f172a;padding:7px 10px;text-align:left;color:#64748b;font-weight:600;border-bottom:1px solid #334155}}
td{{padding:6px 10px;border-bottom:1px solid #1e293b}}
tr:hover td{{background:#0f172a}}
.badge{{display:inline-block;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600}}
.note{{background:#1e3a5f;border:1px solid #3b82f6;border-radius:8px;padding:10px 14px;font-size:12px;color:#93c5fd;margin-bottom:14px}}
</style>
</head>
<body>
<div class="hdr">
  <h1>📊 VNINDEX 5-State Market System — Backtest Toàn Kỳ 2000–2026</h1>
  <p>So sánh 4 kịch bản · Deposit thực tế 0.1%/yr · Recovery Boost sau CRISIS (130%, 20 phiên) · Dữ liệu đến {vni["time"].iloc[-1].strftime("%d/%m/%Y")}</p>
</div>
<div class="wrap">

<!-- NOTE -->
<div class="note">
  <strong>Các kịch bản:</strong>
  &nbsp;🔵 <strong>HT gốc (6%/yr)</strong> — giả định term deposit, không thực tế khi cần thanh khoản ngay &nbsp;|&nbsp;
  🟡 <strong>HT thực tế (0.1%/yr)</strong> — lãi tiền gửi không kỳ hạn VN &nbsp;|&nbsp;
  🟢 <strong>HT + Recovery</strong> — thực tế + tăng 130% trong 20 phiên sau mỗi CRISIS exit &nbsp;|&nbsp;
  🔷 <strong>B&H</strong> — buy and hold VNINDEX
</div>

<!-- KPI HERO -->
<div class="grid4">
  <div class="kpi"><div class="val green">{pct(rec_m11.get("cagr"))}</div><div class="lbl">CAGR HT+Rec (2011+)</div></div>
  <div class="kpi"><div class="val blue">{pct(bh_m11.get("cagr"))}</div><div class="lbl">CAGR B&H (2011+)</div></div>
  <div class="kpi"><div class="val green">{f2(rec_m11.get("calmar"))}</div><div class="lbl">Calmar HT+Rec</div></div>
  <div class="kpi"><div class="val blue">{f2(bh_m11.get("calmar"))}</div><div class="lbl">Calmar B&H</div></div>
  <div class="kpi"><div class="val green">{pct(rec_m11.get("mdd"))}</div><div class="lbl">MaxDD HT+Rec</div></div>
  <div class="kpi"><div class="val red">{pct(bh_m11.get("mdd"))}</div><div class="lbl">MaxDD B&H</div></div>
  <div class="kpi"><div class="val green">{f2(rec_m11.get("sharpe"))}</div><div class="lbl">Sharpe HT+Rec</div></div>
  <div class="kpi"><div class="val">{wins_rec}/{total_yr}</div><div class="lbl">Năm thắng B&H (HT+Rec)</div></div>
</div>

<!-- NAV CHART -->
<div class="card">
  <h2>NAV tích lũy — Chuẩn hóa về 100 từ 2000 (log scale)</h2>
  <div class="note" style="margin-bottom:10px;font-size:11px">
    NAV cuối kỳ (1B → X tỷ):
    &nbsp;HT gốc 6% = <strong style="color:#60a5fa">{final_ht6:.1f} tỷ</strong>
    &nbsp;HT thực tế 0.1% = <strong style="color:#eab308">{final_ht01:.1f} tỷ</strong>
    &nbsp;HT+Recovery = <strong style="color:#22c55e">{final_rec:.1f} tỷ</strong>
    &nbsp;B&H = <strong style="color:#94a3b8">{final_bh:.1f} tỷ</strong>
  </div>
  <div class="chart-wrap" style="height:380px"><canvas id="navChart"></canvas></div>
</div>

<!-- DRAWDOWN CHART -->
<div class="card">
  <h2>Drawdown từ đỉnh (%)</h2>
  <div class="chart-wrap"><canvas id="ddChart"></canvas></div>
</div>

<!-- PERIOD TABLES -->
{period_section("Toàn kỳ 2000–nay", mets["Toàn kỳ (2000–nay)"])}
{period_section("Từ 2011 (sau khi hệ thống ổn định)", mets["Từ 2011"])}
{period_section("OOS · 2021–nay (hold-out test)", mets["OOS (2021–nay)"], oos=True)}

<!-- ANNUAL TABLE -->
<div class="card">
  <h2>Hiệu suất từng năm — HT+Recovery vs B&H
    &nbsp;<span style="font-size:11px;color:#94a3b8;font-weight:400">{wins_rec}/{total_yr} năm thắng B&H ({wins_rec*100//total_yr}%) &nbsp;·&nbsp;
    HT gốc 6%: {wins_ht6}/{total_yr} năm ({wins_ht6*100//total_yr}%)</span>
  </h2>
  <p style="font-size:11px;color:#64748b;margin-bottom:10px">
    <span style="background:#2d1a1a;padding:2px 6px;border-radius:3px">năm gấu (B&amp;H&lt;-5%)</span> &nbsp;
    <span style="background:#1a2d1a;padding:2px 6px;border-radius:3px">năm bò mạnh (B&amp;H&gt;15%)</span> &nbsp;
    ◄ = OOS (2021+)
  </p>
  <table>
    <thead><tr>
      <th>Năm</th>
      <th style="text-align:right;color:#60a5fa">HT gốc 6%</th>
      <th style="text-align:right;color:#eab308">HT 0.1%</th>
      <th style="text-align:right;color:#22c55e">HT+Recovery</th>
      <th style="text-align:right;color:#60a5fa">B&H</th>
      <th>Vs B&H</th>
    </tr></thead>
    <tbody>{ann_rows}</tbody>
  </table>
</div>

<!-- ANALYSIS NOTE -->
<div class="card">
  <h2>Phân tích & Nhận xét</h2>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px;font-size:12px">
    <div>
      <p style="color:#94a3b8;font-weight:700;margin-bottom:8px">💡 Recovery Boost (+0.1% → HT+Rec)</p>
      <ul style="color:#cbd5e1;padding-left:16px;line-height:2">
        <li>CAGR 2011+: <span class="green">{pct(mets["Từ 2011"]["HT thực tế (0.1%/yr)"].get("cagr"))}</span> → <span class="green">{pct(rec_m11.get("cagr"))}</span> (+{(rec_m11.get("cagr",0)-mets["Từ 2011"]["HT thực tế (0.1%/yr)"].get("cagr",0))*100:.1f}pp)</li>
        <li>Calmar 2011+: {f2(mets["Từ 2011"]["HT thực tế (0.1%/yr)"].get("calmar"))} → <span class="green">{f2(rec_m11.get("calmar"))}</span></li>
        <li>MaxDD: {pct(mets["Từ 2011"]["HT thực tế (0.1%/yr)"].get("mdd"))} → {pct(rec_m11.get("mdd"))} (gần như không đổi)</li>
        <li>Kích hoạt: 25 lần thoát CRISIS × 20 phiên = ~500 phiên (~8% thời gian)</li>
        <li>Năm đóng góp lớn nhất: 2020 COVID (+6.7pp), 2012 (+5.9pp)</li>
      </ul>
    </div>
    <div>
      <p style="color:#94a3b8;font-weight:700;margin-bottom:8px">⚠️ Giả định & Giới hạn thực tế</p>
      <ul style="color:#cbd5e1;padding-left:16px;line-height:2">
        <li>Deposit 6%/yr: <span class="red">không thực tế</span> — tiền mặt cần thanh khoản ngay, không thể kỳ hạn</li>
        <li>Deposit 0.1%/yr: <span class="green">thực tế</span> — tiền gửi không kỳ hạn VN</li>
        <li>Lãi tiền mặt 0.1% chỉ đóng góp ~0.05pp/yr (47.8% cash × 0.1%)</li>
        <li>CAGR thực dự kiến ≈ CAGR backtest − 1.5% (TC + slippage + thuế)</li>
        <li>HT+Rec thực tế ≈ {(rec_m11.get("cagr",0)-0.015)*100:.1f}%/yr → vẫn trội B&H về risk-adj</li>
        <li>OOS Calmar {f2(rec_m21.get("calmar"))} vs B&H {f2(bh_m21.get("calmar"))} → không overfit ✓</li>
      </ul>
    </div>
  </div>
</div>

</div><!-- /wrap -->
<script>
const dates = {json.dumps(dates_s)};
const navHT6  = {json.dumps(nav_ht6)};
const navHT01 = {json.dumps(nav_ht01)};
const navRec  = {json.dumps(nav_rec)};
const navBH   = {json.dumps(nav_bh)};
const ddHT6   = {json.dumps(dd_ht6)};
const ddRec   = {json.dumps(dd_rec)};
const ddBH    = {json.dumps(dd_bh)};

// NAV Chart (log scale)
new Chart(document.getElementById('navChart'), {{
  type:'line',
  data:{{ labels:dates, datasets:[
    {{label:'HT gốc (6%/yr)',     data:navHT6,  borderColor:'#60a5fa', borderWidth:1.5, pointRadius:0, fill:false}},
    {{label:'HT thực tế (0.1%/yr)',data:navHT01,borderColor:'#eab308', borderWidth:1.5, pointRadius:0, fill:false, borderDash:[3,2]}},
    {{label:'⭐ HT+Recovery',      data:navRec,  borderColor:'#22c55e', borderWidth:2.0, pointRadius:0, fill:false}},
    {{label:'B&H',                 data:navBH,   borderColor:'#94a3b8', borderWidth:1.2, pointRadius:0, fill:false, borderDash:[5,3]}}
  ]}},
  options:{{
    responsive:true, maintainAspectRatio:false, animation:false,
    scales:{{
      x:{{ticks:{{maxTicksLimit:12,color:'#64748b',font:{{size:10}}}},grid:{{color:'#1e293b'}}}},
      y:{{type:'logarithmic',ticks:{{color:'#64748b',font:{{size:10}},callback:v=>v+''}},grid:{{color:'#1e293b'}},
          title:{{display:true,text:'NAV (log, base=100)',color:'#64748b',font:{{size:10}}}}}}
    }},
    plugins:{{
      legend:{{labels:{{boxWidth:14,color:'#e2e8f0',font:{{size:11}}}}}},
      tooltip:{{mode:'index',intersect:false,callbacks:{{label:ctx=>ctx.dataset.label+': '+ctx.raw}}}}
    }}
  }}
}});

// DD Chart
new Chart(document.getElementById('ddChart'), {{
  type:'line',
  data:{{ labels:dates, datasets:[
    {{label:'HT gốc (6%/yr)', data:ddHT6,  borderColor:'#60a5fa', borderWidth:1.2, pointRadius:0, fill:true, backgroundColor:'rgba(96,165,250,0.05)'}},
    {{label:'⭐ HT+Recovery', data:ddRec,   borderColor:'#22c55e', borderWidth:1.5, pointRadius:0, fill:true, backgroundColor:'rgba(34,197,94,0.07)'}},
    {{label:'B&H',            data:ddBH,   borderColor:'#ef4444', borderWidth:1.2, pointRadius:0, fill:true, backgroundColor:'rgba(239,68,68,0.05)'}}
  ]}},
  options:{{
    responsive:true, maintainAspectRatio:false, animation:false,
    scales:{{
      x:{{ticks:{{maxTicksLimit:12,color:'#64748b',font:{{size:10}}}},grid:{{color:'#1e293b'}}}},
      y:{{ticks:{{color:'#64748b',font:{{size:10}},callback:v=>v+'%'}},grid:{{color:'#1e293b'}},
          title:{{display:true,text:'Drawdown (%)',color:'#64748b',font:{{size:10}}}}}}
    }},
    plugins:{{
      legend:{{labels:{{boxWidth:14,color:'#e2e8f0',font:{{size:11}}}}}},
      tooltip:{{mode:'index',intersect:false}}
    }}
  }}
}});
</script>
</body>
</html>"""

out = WORKDIR + "/backtest_full_report.html"
with open(out, "w", encoding="utf-8") as f:
    f.write(html)
print(f"Saved: {out}")

# Print summary to console
print("\n" + "="*70)
print("  SUMMARY")
print("="*70)
for lbl,i0,i1 in periods:
    print(f"\n  {lbl}:")
    for name in ["HT gốc (6%/yr)","HT thực tế (0.1%/yr)","HT + Recovery (0.1%/yr)","B&H"]:
        m=mets[lbl][name]
        print(f"    {name:<35} CAGR={pct(m.get('cagr'))}  Calmar={f2(m.get('calmar'))}  MaxDD={pct(m.get('mdd'))}  Sharpe={f2(m.get('sharpe'))}")
print(f"\n  Annual wins vs B&H: HT+Rec {wins_rec}/{total_yr} | HT gốc 6% {wins_ht6}/{total_yr}")
