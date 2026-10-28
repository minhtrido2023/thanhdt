"""B2/B3 theo TRIALS_B2B3.md (md5 065ea443): giá TB quý P4 (sunsirs) / sulfur (TE) -> KQKD quý (bản công bố đầu) + phản ứng giá."""
import sys, os, json, pandas as pd, numpy as np
from scipy.stats import spearmanr
O=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,f'{O}/../commodity_cycle_te_20261026')
from common import px, univ, fin, bench
rng=np.random.default_rng(20261026)
d=pd.read_parquet(f'{O}/raw.parquet')
def ser(k): s=d[d.metric_key==k].set_index('observation_date').value.sort_index(); return s[s.index.dayofweek<5]
def qavg(s): a=s.resample('QE').agg(['mean','count']); return a['mean'].where(a['count']>=40)
QP=qavg(ser('yellow_phosphorus')); QS=qavg(ser('sulfur')); QR=qavg(ser('phosphate_rock_cny'))
QSP=(QP-9*QR)  # spread P4 - 9 t quặng (TE CNY/t); điện/than cốc KHÔNG có dữ liệu
C={'P4':np.log(QP/QP.shift(4)),'S':np.log(QS/QS.shift(4)),'SP':np.log(QSP/QSP.shift(4))}
pd.DataFrame({'P4_qavg':QP,'S_qavg':QS,'rock_qavg':QR,'spread':QSP,**{f'c_{k}':v for k,v in C.items()}}).to_csv(f'{O}/b2_qavg.csv')
P=px(); U=univ(); F=fin(); B=bench(P,U); Bc=(1+B).cumprod(); idx=P.index
def at(x): i=idx.searchsorted(x); return idx[i] if i<len(idx) else None
def ret(tk,a,b):
    if a is None or b is None or tk not in P: return np.nan
    x,y=P.at[a,tk],P.at[b,tk]; return y/x-1-(Bc[b]/Bc[a]-1) if x>0 and y>0 else np.nan
GROUPS={'P4':['DGC','PAT'],'S':['DDV','LAS','CSV'],'DESC':['BFC','DPM','DCM','SFG','VAF','NFC']}
rows=[]
for g,tks in GROUPS.items():
  for tk in tks:
    for _,r in F[F.ticker==tk].iterrows():
        qe=r.qend; sig=at(qe+pd.Timedelta(days=2))
        if sig is None or not (r.Release_Date>sig): continue          # PIT: tín hiệu phải có TRƯỚC công bố
        pre_end=idx[idx.searchsorted(r.Release_Date)-1]; t1=at(r.Release_Date+pd.Timedelta(days=1))
        i=idx.get_loc(t1) if t1 is not None else None; e60=idx[i+60] if i is not None and i+60<len(idx) else None
        rows.append(dict(group=g,ticker=tk,quarter=r.quarter,qend=qe,release=r.Release_Date,lag=(r.Release_Date-qe).days,
          cP4=C['P4'].get(qe,np.nan),cS=C['S'].get(qe,np.nan),cSP=C['SP'].get(qe,np.nan),
          rev_yoy=np.log(r.Revenue_P0/r.Revenue_P4) if r.Revenue_P0>0 and r.Revenue_P4>0 else np.nan,
          gpm_d=(r.GPM_P0-r.GPM_P4) if abs(r.GPM_P0)<5 and abs(r.GPM_P4)<5 else np.nan,
          np_d=np.clip((r.NP_P0-r.NP_P4)/r.Revenue_P4,-.5,.5) if r.Revenue_P4>0 else np.nan,
          gpm0=r.GPM_P0,np0=r.NP_P0,rev0=r.Revenue_P0,
          ann=ret(tk,pre_end,t1),post60=ret(tk,t1,e60)))
D=pd.DataFrame(rows); D.to_csv(f'{O}/b2_panel.csv',index=False)
print('panel',D.groupby('group').agg(n=('ticker','size'),q0=('quarter','min'),q1=('quarter','max'),lag_med=('lag','median')).to_string())
def gq(g,x): # gộp theo quý: trung vị nhóm => N = số quý
    return D[D.group==g].groupby('quarter').agg(**{x:(x,'first')},**{y:(y,'median') for y in ['rev_yoy','gpm_d','np_d','ann','post60']},n=('ticker','size')).dropna(subset=[x])
def mbb(df,f,L=4,R=5000):
    df=df.sort_index().reset_index(drop=True); n=len(df); out=[]
    for _ in range(R):
        st=rng.integers(0,max(n-L+1,1),int(np.ceil(n/L))); ix=np.concatenate([np.arange(s,s+L) for s in st])[:n]; ix=ix[ix<n]
        v=f(df.iloc[ix]); 
        if np.isfinite(v): out.append(v)
    return np.percentile(out,[5,95]).round(3).tolist()
def circ(df,x,y,R=2000):
    df=df[[x,y]].dropna(); e=spearmanr(df[x],df[y])[0]; xs=df[x].values
    pr=[spearmanr(np.roll(xs,rng.integers(1,len(xs))),df[y])[0] for _ in range(R)]
    return e,(np.sum(np.abs(pr)>=abs(e))+1)/(R+1)
def test(name,g,x,y,sign):
    G=gq(g,x)[[x,y]].dropna()
    if len(G)<8: return dict(trial=name,n_q=len(G),note='N<8')
    e,p=circ(G,x,y); ci=mbb(G,lambda s: spearmanr(s[x],s[y])[0] if s[x].nunique()>2 else np.nan)
    IS=G[G.index<'2023Q1']; OS=G[G.index>='2023Q1']
    f=lambda s: round(spearmanr(s[x],s[y])[0],3) if len(s)>=5 else None
    return dict(trial=name,group=g,x=x,y=y,exp_sign=sign,ic=round(e,3),ci90_mbb=ci,p_circ=round(p,4),n_q=len(G),q0=G.index.min(),q1=G.index.max(),ic_IS=f(IS),n_IS=len(IS),ic_OOS=f(OS),n_OOS=len(OS))
R=[]
for nm,g,x,y,s in [('N1','P4','cP4','rev_yoy',1),('N2','P4','cP4','gpm_d',1),('N3','P4','cP4','np_d',1),
                   ('N4','S','cS','rev_yoy',1),('N5','S','cS','gpm_d',-1),('N6','S','cS','np_d',-1),
                   ('N8','P4','cSP','np_d',1),
                   ('G1','P4','cP4','ann',1),('G2','P4','cP4','post60',1),('G3','S','cS','ann',-1),('G4','S','cS','post60',-1)]:
    if nm=='N8': # chỉ DGC
        G=D[(D.ticker=='DGC')][['quarter','cSP','np_d']].dropna().set_index('quarter')
        e,p=circ(G,'cSP','np_d') if len(G)>=6 else (np.nan,np.nan)
        R.append(dict(trial=nm,group='DGC',x='cSP',y='np_d',exp_sign=1,ic=round(e,3),p_circ=round(p,4),n_q=len(G),q0=G.index.min(),q1=G.index.max(),corr_level_spread_vs_P4=round(float(np.corrcoef(QSP.dropna(),QP[QSP.dropna().index])[0,1]),3)))
    else: R.append(test(nm,g,x,y,s))
# N7: DGC np_d ~ cP4 + cS (OLS), CI mbb
G7=D[D.ticker=='DGC'][['quarter','cP4','cS','np_d','gpm_d']].dropna().set_index('quarter').sort_index()
def ols(s,y='np_d'):
    X=np.c_[np.ones(len(s)),s.cP4,s.cS]; return np.linalg.lstsq(X,s[y].values,rcond=None)[0]
b=ols(G7); bs=[]
for _ in range(5000):
    n=len(G7); st=rng.integers(0,n-3,int(np.ceil(n/4))); ix=np.concatenate([np.arange(s,s+4) for s in st])[:n]
    bs.append(ols(G7.iloc[ix]))
bs=np.array(bs)
R.append(dict(trial='N7',group='DGC',y='np_d',coef_const=round(b[0],3),coef_P4=round(b[1],3),ci90_P4=np.percentile(bs[:,1],[5,95]).round(3).tolist(),
  coef_S=round(b[2],3),ci90_S=np.percentile(bs[:,2],[5,95]).round(3).tolist(),p_boot_S_ge0=round(float((bs[:,2]>=0).mean()),4),p_boot_P4_le0=round(float((bs[:,1]<=0).mean()),4),n_q=len(G7),q0=G7.index.min(),q1=G7.index.max()))
for r in R:
    if 'p_circ' in r and r.get('p_circ')==r.get('p_circ'): r['p_bonf17']=min(1,round(r['p_circ']*17,4)) if r['trial'].startswith('G') else min(1,round(r['p_circ']*8,4))
desc=[]
for tk in GROUPS['DESC']+GROUPS['S']+GROUPS['P4']:
    s=D[D.ticker==tk]
    for x in ['cP4','cS']:
        for y in ['rev_yoy','gpm_d','np_d']:
            z=s[[x,y]].dropna()
            if len(z)>=8: desc.append(dict(ticker=tk,x=x,y=y,ic=round(spearmanr(z[x],z[y])[0],3),n=len(z)))
pd.DataFrame(desc).to_csv(f'{O}/b2_desc_ticker.csv',index=False)
json.dump(R,open(f'{O}/b2_results.json','w'),indent=1,default=str)
for r in R: print(r)
print(pd.DataFrame(desc).pivot_table(index='ticker',columns=['x','y'],values='ic').round(2).to_string())
