import pandas as pd, numpy as np
from scipy import stats
BASE="mike/agents/Taylor/research/fearbuy_blend"
HOLD=375  # sessions ~ 18 months

# ---- 1. V2.4 baseline daily NAV (univpit R3 control) ----
v24f="data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_exp_discC4_control_univpit.csv"
d=pd.read_csv(v24f,low_memory=False)
d=d[d.combined_nav.notna()&d.ymd.notna()].copy()
d['ymd']=pd.to_datetime(d['ymd']); d=d.sort_values('ymd')
v24=d.groupby('ymd')['combined_nav'].last().astype(float)
r_v24=v24.pct_change().fillna(0.0)
cal=v24.index  # trading calendar
print(f"V2.4 baseline: {v24.index[0].date()}..{v24.index[-1].date()} n={len(v24)} CAGR-check")

# ---- 2. prices -> per-ticker daily return, aligned to calendar ----
px=pd.read_csv(f"{BASE}/prices.csv"); px['time']=pd.to_datetime(px['time'])
pv=px.pivot(index='time',columns='ticker',values='Close').sort_index()
pv=pv.reindex(cal).ffill(limit=5)  # align to V2.4 calendar
ret=pv.pct_change()

# ---- 3. qualifying entries: adaptive + ADV>=10B (optionally DE ceiling ex-financials) ----
pan=pd.read_csv(f"{BASE}/panel.csv"); pan['adv_b']=pan['adv_vnd']/1e9; pan['s']=-pan['mkt_dd']
pan['entry_date']=pd.to_datetime(pan['entry_date'])
pbmax=np.clip(1.0-2.0*(pan.s-0.20),0.40,1.0)
FIN_ICB=pan.ICB_Code.astype(str).str.startswith(('85','87','86'))  # banks/insurance/financials/securities
def qualset(advmin=10, de_ceiling=None, apply_de_exfin=False):
    m=(pan.s>=0.20)&(pan.PB<=pbmax)&(pan.adv_b>=advmin)
    if de_ceiling is not None:
        de_ok=(pan.DE<=de_ceiling)|(pan.DE.isna())
        if apply_de_exfin: de_ok=de_ok|FIN_ICB
        m=m&de_ok
    return pan[m].copy()

def map_to_cal(dt):
    idx=cal.searchsorted(dt)
    return cal[min(idx,len(cal)-1)]

def build_sleeve(q, maxconc=None):
    """positions: each name entered at episode date, held HOLD sessions (buy&hold).
       sleeve daily return = value-weighted avg of held positions. maxconc: cap concurrent (cheapest PB)."""
    # entry per (ticker,episode) -> entry cal-date + exit cal-date
    q=q.sort_values(['entry_date','PB'])
    pos=[]
    for _,r in q.iterrows():
        if r.ticker not in ret.columns: continue
        e=map_to_cal(r.entry_date); ei=cal.searchsorted(e)
        xi=min(ei+HOLD,len(cal)-1)
        pos.append(dict(tk=r.ticker,ei=ei,xi=xi,pb=r.PB))
    # build daily sleeve return
    sr=pd.Series(0.0,index=cal); active_days=pd.Series(0,index=cal)
    # value tracking per position
    vals={}
    for k,p in enumerate(pos): vals[k]=dict(**p,val=1.0,started=False)
    for ti in range(len(cal)):
        # determine held set today
        held=[k for k,p in vals.items() if p['ei']<=ti<p['xi']]
        if maxconc is not None and len(held)>maxconc:
            held=sorted(held,key=lambda k:vals[k]['pb'])[:maxconc]  # cheapest PB
        if not held:
            continue
        active_days[cal[ti]]=len(held)
        # each held position updates its value by its daily return; equal $ at entry (val reset when starting)
        day_rets=[]
        for k in held:
            p=vals[k]
            if not p['started']:
                p['started']=True; p['val']=1.0  # equal capital slice at entry
            rr=ret[p['tk']].iloc[ti]
            if pd.isna(rr): rr=0.0
            p['val']*= (1+rr)
            day_rets.append(rr)
        # sleeve daily return = equal-weight (rebalanced) mean of held names' returns
        sr[cal[ti]]=np.nanmean(day_rets)
    return sr, active_days

def metrics(nav):
    nav=nav.dropna()
    yrs=(nav.index[-1]-nav.index[0]).days/365.25
    c=((nav.iloc[-1]/nav.iloc[0])**(1/yrs)-1)*100
    dd=((nav/nav.cummax()-1).min())*100
    r=nav.pct_change().dropna()
    npy=len(r)/yrs
    sh=(r.mean()/r.std())*np.sqrt(npy) if r.std()>0 else np.nan
    dn=r[r<0]; so=(r.mean()/dn.std())*np.sqrt(npy) if len(dn)>0 and dn.std()>0 else np.nan
    return dict(CAGR=c,Sharpe=sh,Sortino=so,MaxDD=dd,Calmar=c/abs(dd) if dd else np.nan)

def blend(sr, w):
    """r_comb = (1-w)*r_v24 + w*r_sleeve on active days; w=0 when sleeve dormant."""
    active=(sr!=0)|(sr.index.isin(sr[sr!=0].index))
    w_t=pd.Series(0.0,index=cal); w_t[sr!=0]=w
    # also keep weight during holding gaps where a name had 0 return that day: use active_days>0 externally
    rc=(1-w_t)*r_v24 + w_t*sr
    nav=(1+rc).cumprod()*v24.iloc[0]
    return nav

def win(nav,y1,y2):
    return metrics(nav[(nav.index.year>=y1)&(nav.index.year<=y2)])

print("\n"+"="*100); print("BASELINE V2.4 (univpit control)"); print("="*100)
mb=metrics(v24); print(f"  FULL   CAGR={mb['CAGR']:.2f}% Sharpe={mb['Sharpe']:.2f} Sortino={mb['Sortino']:.2f} MaxDD={mb['MaxDD']:.1f}% Calmar={mb['Calmar']:.2f}")
print(f"  IS1419 {win(v24,2014,2019)}"); print(f"  OOS20+ {win(v24,2020,2026)}")

for advmin,de,exfin,mc,lab in [
    (10,None,False,None,"adaptive+ADV10B  all-held"),
    (10,None,False,5,"adaptive+ADV10B  maxconc=5"),
    (10,2.5,True,5,"adaptive+ADV10B DE<=2.5(exfin) maxconc=5"),
    (20,None,False,5,"adaptive+ADV20B  maxconc=5"),
]:
    q=qualset(advmin,de,exfin); sr,ad=build_sleeve(q,mc)
    ms=metrics((1+sr[sr!=0]).cumprod()) if (sr!=0).any() else {}
    print("\n"+"="*100); print(f"SLEEVE: {lab}  | qualifying episodes N={len(q)}  | uniq tickers={q.ticker.nunique()}  | active sessions={int((ad>0).sum())}")
    print("="*100)
    print(f"  {'w_sleeve':<10}{'CAGR':>8}{'Sharpe':>8}{'Sortino':>9}{'MaxDD':>8}{'Calmar':>8}   {'dCAGR':>7}{'dMaxDD':>8}")
    for w in [0.0,0.05,0.10,0.15,0.20]:
        nav=blend(sr,w); m=metrics(nav)
        print(f"  {w:<10.2f}{m['CAGR']:>7.2f}%{m['Sharpe']:>8.2f}{m['Sortino']:>9.2f}{m['MaxDD']:>7.1f}%{m['Calmar']:>8.2f}   {m['CAGR']-mb['CAGR']:>+6.2f}{m['MaxDD']-mb['MaxDD']:>+7.1f}")
    # IS/OOS at w=0.10
    nav=blend(sr,0.10)
    print(f"  --- w=0.10 IS/OOS ---  IS {win(nav,2014,2019)}")
    print(f"                         OOS {win(nav,2020,2026)}")
