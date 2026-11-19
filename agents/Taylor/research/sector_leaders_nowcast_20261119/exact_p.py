"""Bổ sung sau khi chạy run.py (khai trong REPORT 'Lệch PREREG'): p dịch vòng CHÍNH XÁC bằng liệt kê mọi k∈[4,nq-4]
(run.py rút 2000 lần từ chỉ 29 giá trị k ⇒ p sàn 0,0005 là ảo), + LOFO họ, + tách pha theo họ. Chỉ đọc panel_famq.csv."""
import os, sys, json, numpy as np, pandas as pd
O=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(O,'..','commodity_cycle_te_20261026'))
from common import te, cmap
D=pd.read_csv(os.path.join(O,'panel_famq.csv')); M=cmap(('A',)); T=te()
qa=T.resample('QE').mean().where(T.resample('QE').count()>=40)
Q=sorted(D.quarter.unique()); nq=len(Q); qp={q:i for i,q in enumerate(Q)}
cg={}
for f in D.family.unique():
    m=M[M.family==f]; s=qa[m.te_metric_key.iloc[0]]; y=np.log(s/s.shift(4))*m.sign.iloc[0]
    cg[f]=np.array([y.get(pd.Period(q,'Q').end_time.normalize(),np.nan) for q in Q])
def pic(G,x,y):
    G=G.dropna(subset=[x,y]).copy(); G['rx']=G.groupby('family')[x].rank(pct=True)-.5; G['ry']=G.groupby('family')[y].rank(pct=True)-.5
    return float(np.corrcoef(G.rx,G.ry)[0,1])
sg=lambda d: np.sign(d.c)
TR={'T1_dIC_np':(lambda d:pic(d,'c','npL')-pic(d,'c','npR'),['npL','npR']),
 'T2_np_down':(lambda d:float((d.npL-d.npR)[d.c<0].mean()),['npL','npR']),
 'T3_np_up':(lambda d:float((d.npL-d.npR)[d.c>0].mean()),['npL','npR']),
 'T4_H0_vsR':(lambda d:float((sg(d)*(d.H0L-d.H0R)).mean()),['H0L','H0R']),
 'T5_H1_vsR':(lambda d:float((sg(d)*(d.H1L-d.H1R)).mean()),['H1L','H1R']),
 'T6_H3_vsR':(lambda d:float((sg(d)*(d.H3L-d.H3R)).mean()),['H3L','H3R']),
 'T7_H0_vsU':(lambda d:float((sg(d)*(d.H0L-d.H0U)).mean()),['H0L','H0U']),
 'T8_H1_vsU':(lambda d:float((sg(d)*(d.H1L-d.H1U)).mean()),['H1L','H1U']),
 'T9_H3_vsU':(lambda d:float((sg(d)*(d.H3L-d.H3U)).mean()),['H3L','H3U'])}
out=[]
for k_,(f,need) in TR.items():
    d=D.dropna(subset=need+['c']); est=f(d); null=[]
    for k in range(4,nq-3):
        d2=d.copy(); d2['c']=[np.roll(cg[fa],k)[qp[q]] for fa,q in zip(d2.family,d2.quarter)]; null.append(f(d2.dropna(subset=['c'])))
    null=np.array(null); p=(np.sum(np.abs(null)>=abs(est))+1)/(len(null)+1)
    lofo={fa:f(d[d.family!=fa]) for fa in sorted(d.family.unique())}
    per={fa:f(d[d.family==fa]) if k_ not in('T1_dIC_np',) else None for fa in sorted(d.family.unique())}
    out.append(dict(trial=k_,est=est,n_shift=len(null),p_exact=p,null_absmax=float(np.abs(null).max()),lofo=lofo,per_family=per))
R=pd.DataFrame(out).sort_values('p_exact').reset_index(drop=True); m=len(R)
R['bh_q_exact']=np.minimum.accumulate((R.p_exact*m/(np.arange(m)+1))[::-1])[::-1].clip(upper=1)
R['bonf38_exact']=(R.p_exact*38).clip(upper=1); R=R.sort_values('trial')
# tách pha theo họ cho T6/T9 (mô tả)
ph=[]
for fa,g in D.groupby('family'):
    for h,c in [('H3','R'),('H3','U')]:
        sp=g[f'{h}L']-g[f'{h}{c}']; ph.append(dict(family=fa,h=h,vs=c,up=sp[g.c>0].mean(),down=sp[g.c<0].mean(),n_up=int((g.c>0).sum()),n_down=int((g.c<0).sum())))
# năm đóng góp cho T9 pha xuống
dn=D[D.c<0].assign(sp=lambda x:x.H3L-x.H3U).groupby('year').sp.agg(['mean','count'])
json.dump(dict(exact=R.to_dict('records'),phase_by_family=ph,T9_down_by_year=dn.reset_index().to_dict('records')),open(os.path.join(O,'results_exact.json'),'w'),indent=1,default=float)
pd.set_option('display.width',250)
print(R[['trial','est','n_shift','p_exact','bh_q_exact','bonf38_exact','null_absmax']].round(4).to_string())
for r in R.itertuples(): print(r.trial,'LOFO',{k:round(v,4) for k,v in r.lofo.items()},'PER',{k:(round(v,4) if v is not None else None) for k,v in r.per_family.items()})
print(pd.DataFrame(ph).round(4).to_string()); print(dn.round(4).to_string())
