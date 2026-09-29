import sys, os, numpy as np, pandas as pd
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude')
from dsr_pbo_annex import load_nav, daily_logret, moments, dsr, expected_max_sr, cscv_pbo, norm_cdf
B='/home/trido/thanhdt/WorkingClaude/data/v23_golive_audit_2014_now_matpostbull_shrink0_edge_etfliqcustompitg_wtnamecap_advprice_univpit_exp_baley%s.csv'
LEGS=[('ctrl2',0.0),('ey025',0.25),('ey050',0.5),('ey100',1.0)]
nav={}
for t,_ in LEGS:
    p=B%t
    if not os.path.exists(p): print('MISSING',p); continue
    nav[t]=load_nav(p)
def metrics(s):
    r=daily_logret(s); yrs=(s.index[-1]-s.index[0]).days/365.25
    cagr=(s.iloc[-1]/s.iloc[0])**(1/yrs)-1
    dd=(s/s.cummax()-1).min()
    sh=r.mean()/r.std(ddof=1)*np.sqrt(252)
    return dict(cagr=cagr*100, maxdd=dd*100, calmar=cagr/abs(dd), sharpe=sh, final_B=s.iloc[-1]/1e9)
def sub(s,a,b): return s[(s.index>=a)&(s.index<=b)]
rows=[]
for t,lam in LEGS:
    if t not in nav: continue
    s=nav[t]; m=metrics(s)
    mi=metrics(sub(s,'2014-01-01','2019-12-31')); mo=metrics(sub(s,'2020-01-01','2026-06-19'))
    rows.append(dict(leg=t,lam=lam,**m, cagr_IS=mi['cagr'], cagr_OOS=mo['cagr']))
T=pd.DataFrame(rows)
c=T[T.leg=='ctrl2'].iloc[0]
for k in ['cagr','cagr_IS','cagr_OOS','calmar','sharpe','maxdd']:
    T['d_'+k]=T[k]-c[k]
pd.set_option('display.width',240)
print('=== A/B (control = pin R3) ==='); print(T.round(4).to_string(index=False))
T.to_csv('p3_ab_metrics.csv',index=False)
# per-year delta (LOO)
print('\n=== per-year CAGR by leg (%) + delta vs ctrl ===')
yr={}
for t,_ in LEGS:
    if t not in nav: continue
    s=nav[t]; out={}
    for y,g in s.groupby(s.index.year):
        prev=s[s.index<g.index[0]]
        s0=prev.iloc[-1] if len(prev) else g.iloc[0]
        out[y]=(g.iloc[-1]/s0-1)*100
    yr[t]=pd.Series(out)
Y=pd.DataFrame(yr)
for t in Y.columns:
    if t!='ctrl2': Y['d_'+t]=Y[t]-Y['ctrl2']
print(Y.round(2).to_string()); Y.to_csv('p3_peryear.csv')
# DSR + PBO on the best leg vs family
best=T[T.leg!='ctrl'].sort_values('cagr',ascending=False).iloc[0]['leg']
print('\n=== DSR / PBO (best leg = %s, N_trials=3) ==='%best)
rb=daily_logret(nav[best]); rc=daily_logret(nav['ctrl2'])
srs=[]
for t,_ in LEGS:
    if t=='ctrl2' or t not in nav: continue
    r=daily_logret(nav[t]); srs.append(r.mean()/r.std(ddof=1))
sr_hat,g3,g4=moments(rb); Tn=len(rb)
var_sr=np.var(srs,ddof=1) if len(srs)>1 else np.var([sr_hat],ddof=0)
sr0=expected_max_sr(var_sr,3) if var_sr>0 else 0.0
p_unadj,_=dsr(sr_hat,0.0,g3,g4,Tn)
p_defl,stat=dsr(sr_hat,sr0,g3,g4,Tn)
print('sr_hat/obs=%.5f  var_sr(family)=%.3e  SR0(N=3)=%.5f'%(sr_hat,var_sr,sr0))
print('DSR vs 0        = %.6f'%p_unadj)
print('DSR vs SR0(N=3) = %.6f   (nguong 0,95)'%p_defl)
# DSR against the CONTROL's Sharpe (the honest null: "beats the pinned config")
sr_c=rc.mean()/rc.std(ddof=1)
p_vs_ctrl,_=dsr(sr_hat,sr_c,g3,g4,Tn)
print('DSR vs SR_ctrl  = %.6f'%p_vs_ctrl)
M=np.column_stack([daily_logret(nav[t]) for t,_ in LEGS if t in nav])
pbo=cscv_pbo(M,S=16)[0] if M.shape[1]>=2 else np.nan
print('PBO (CSCV S=16, %d cau hinh) = %.4f'%(M.shape[1],pbo))
# block bootstrap of the delta
def cbb(r,L=21,B=4000,seed=12345):
    rng=np.random.default_rng(seed); n=len(r); nb=int(np.ceil(n/L)); out=np.empty(B)
    for b in range(B):
        st=rng.integers(0,n,nb); idx=np.concatenate([(np.arange(s,s+L)%n) for s in st])[:n]
        out[b]=r[idx].sum()
    return out
dlr=rb-rc if len(rb)==len(rc) else None
if dlr is not None:
    yrs=(nav['ctrl2'].index[-1]-nav['ctrl2'].index[0]).days/365.25
    bs=cbb(dlr)/yrs*100
    print('\nBlock bootstrap L=21 tren chuoi delta log-return: diem uoc luong=%.3fpp/nam  CI95=[%.3f, %.3f]  P(d>0)=%.3f'%(dlr.sum()/yrs*100, np.percentile(bs,2.5), np.percentile(bs,97.5), (bs>0).mean()))
