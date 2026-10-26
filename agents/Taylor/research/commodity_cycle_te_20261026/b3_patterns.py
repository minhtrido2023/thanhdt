"""B3 theo PREREG-3 (commit da1681489). 13 trial: H-a 8, H-b 3, H-c 1, H-d 1."""
import pandas as pd, numpy as np, json, glob
from scipy.stats import spearmanr
from common import *
SEED=20261026; rng=np.random.default_rng(SEED)
T=te(); P=px(); U=univ().reindex(P.index).fillna(False); B=bench(P,U); Bc=(1+B).cumprod()
M=cmap(('A',)); FAM=M.groupby('family').agg(key=('te_metric_key','first'),tks=('ticker',list))
idx=P.index; Pf=P.ffill()
PE=pd.concat([pd.read_parquet(f,columns=['ticker','time','PE']) for f in sorted(glob.glob(f'{W}/data/bq_cache/ticker/*.parquet'))])
PE['time']=pd.to_datetime(PE.time); PE=PE.pivot_table(index='time',columns='ticker',values='PE').reindex(idx)
def nth_after(d,n=2):
    i=idx.searchsorted(d,side='right')+n-1; return i if i<len(idx) else None
def basket_x(tks,i0,h):
    if i0 is None or i0+h>=len(idx): return np.nan
    t0,t1=idx[i0],idx[i0+h]; mem=[t for t in tks if t in U.columns and U.at[t0,t]]
    if not mem: return np.nan
    r=[Pf.at[t1,t]/Pf.at[t0,t]-1 for t in mem if Pf.at[t0,t]>0]
    return np.mean(r)-(Bc[t1]/Bc[t0]-1)
def stock_x(t,i0,h):
    if i0+h>=len(idx): return np.nan
    t0,t1=idx[i0],idx[i0+h]; a,b=Pf.at[t0,t],Pf.at[t1,t]
    return b/a-1-(Bc[t1]/Bc[t0]-1) if a>0 else np.nan
def split(d): return 'IS' if d<pd.Timestamp('2023-01-01') else 'OOS'
NEW={'steel_cn','dry_bulk','container'}
res={}
# ---------------- H-a
def clusters(ev):
    ev=ev.sort_values('i0').copy(); c=0; last=-10**9; cl=[]
    for i in ev.i0:
        if i-last>=126: c+=1
        cl.append(c); last=i
    ev['cl']=cl; return ev
def cl_stats(ev,col='X'):
    g=ev.groupby('cl')[col].mean().dropna(); n=len(g)
    if n<2: return dict(n_ev=len(ev),n_cl=n,mean=g.mean() if n else np.nan)
    bs=[rng.choice(g.values,n).mean() for _ in range(10000)]
    perm=[(g.values*rng.choice([-1,1],n)).mean() for _ in range(10000)]
    p=(np.sum(np.array(perm)>=g.mean())+1)/10001
    return dict(n_ev=len(ev),n_cl=n,mean=round(g.mean(),4),median=round(g.median(),4),ci90=[round(np.percentile(bs,5),4),round(np.percentile(bs,95),4)],p1=round(p,4),pos=f"{(g>0).sum()}/{n}",MDE=round(2.5*g.std()/np.sqrt(n),4))
grid=[]; allev={}
for th in (1.05,1.10):
  for L in (126,252):
    for h in (63,126):
      evs=[]
      for fam,r in FAM.iterrows():
        s=T[r.key].dropna(); R=s/s.rolling(L).mean(); last=-10**9
        for j in range(1,len(R)):
            if R.iloc[j]>=th and R.iloc[j-1]<th and not np.isnan(R.iloc[j-1]):
                d=R.index[j]; i0=nth_after(d)
                if i0 is None or i0-last<252: continue
                last=i0
                if idx[i0]<pd.Timestamp('2017-01-01'): continue
                evs.append(dict(family=fam,d=d,i0=i0,entry=idx[i0],X=basket_x(r.tks,i0,h)))
      ev=pd.DataFrame(evs).dropna(subset=['X']); ev=clusters(ev); ev['split']=ev.entry.map(split)
      st=cl_stats(ev); st.update(th=th,L=L,h=h)
      # baseline: mọi tháng (phiên thứ 2 mỗi tháng) cùng họ, cùng h
      bl=[]
      for fam,r in FAM.iterrows():
          for me in pd.date_range('2017-01-01',idx[-1],freq='ME'):
              i0=nth_after(me); x=basket_x(r.tks,i0,h) if i0 else np.nan
              if not np.isnan(x): bl.append(dict(family=fam,X=x))
      bl=pd.DataFrame(bl); fams=ev.family.unique()
      st['baseline']=round(bl[bl.family.isin(fams)].X.mean(),4)
      st['IS']=round(clusters(ev[ev.split=='IS']).pipe(lambda e:e.groupby('cl').X.mean().mean()),4)
      st['OOS']=round(clusters(ev[ev.split=='OOS']).pipe(lambda e:e.groupby('cl').X.mean().mean()),4)
      st['NEW_fams']=cl_stats(clusters(ev[ev.family.isin(NEW)]))
      st['LOFO_min']=round(min(clusters(ev[ev.family!=f]).groupby('cl').X.mean().mean() for f in ev.family.unique()),4)
      grid.append(st); allev[(th,L,h)]=ev
      print('H-a',th,L,h,{k:st[k] for k in ['n_ev','n_cl','mean','ci90','p1','baseline','IS','OOS','LOFO_min']},'NEW',st['NEW_fams'].get('mean'),st['NEW_fams'].get('n_cl'))
allev[(1.05,252,63)].to_csv('b3_Ha_events_main.csv',index=False)
res['H-a']=grid
# ---------------- H-b lead-lag
months=pd.date_range('2016-12-31',idx[-1],freq='ME')
rows=[]
Tf=T.reindex(pd.date_range(T.index[0],T.index[-1],freq='D')).ffill(limit=10)
for fam,r in FAM.iterrows():
    pm=Tf[r.key].reindex(months); c=np.log(pm/pm.shift(1))
    for k,me in enumerate(months):
        if np.isnan(c.iloc[k]): continue
        row=dict(family=fam,m=me,c=c.iloc[k])
        for kk in (1,2,3):
            if k+kk<len(months):
                a=nth_after(months[k+kk-1]); b=nth_after(months[k+kk]) if k+kk<len(months) else None
                row[f's{kk}']=basket_x(r.tks,a,b-a) if a is not None and b is not None else np.nan
        # k=0: cuối tháng m-1 -> cuối tháng m; k=-1: tháng trước đó
        for kk,(m0,m1) in {0:(months[k-1] if k>0 else None,me),-1:(months[k-2] if k>1 else None,months[k-1] if k>0 else None)}.items():
            if m0 is None or m1 is None: row[f's{kk}']=np.nan; continue
            a=idx.searchsorted(m0,side='right')-1; b=idx.searchsorted(m1,side='right')-1
            row[f's{kk}']=basket_x(r.tks,a,b-a)
        rows.append(row)
H=pd.DataFrame(rows); H['split']=H.m.map(split); H.to_csv('b3_Hb_panel.csv',index=False)
def ricp(H,y,nperm=2000):
    Z=H.dropna(subset=['c',y]).copy(); Z['rx']=Z.groupby('family').c.rank(pct=True)-.5; Z['ry']=Z.groupby('family')[y].rank(pct=True)-.5
    est=np.corrcoef(Z.rx,Z.ry)[0,1]; perm=[]
    for _ in range(nperm):
        Q=Z.copy(); Q['rx']=Q.groupby('family').rx.transform(lambda v: np.roll(v.values,rng.integers(6,len(v)-6))); perm.append(np.corrcoef(Q.rx,Q.ry)[0,1])
    ms=Z.m.unique(); byq={q:Z[Z.m==q] for q in ms}; bs=[]
    for _ in range(2000):
        s=pd.concat([byq[q] for q in rng.choice(ms,len(ms))]); bs.append(np.corrcoef(s.rx,s.ry)[0,1])
    return dict(ic=round(est,4),p2=round((np.sum(np.abs(perm)>=abs(est))+1)/(nperm+1),4),p1_pos=round((np.sum(np.array(perm)>=est)+1)/(nperm+1),4),ci90=[round(np.percentile(bs,5),3),round(np.percentile(bs,95),3)],n=len(Z),n_months=len(ms))
hb={}
for y in ['s-1','s0','s1','s2','s3']:
    hb[y]={'ALL':ricp(H,y),'IS':ricp(H[H.split=='IS'],y,500),'OOS':ricp(H[H.split=='OOS'],y,500),
           'LOFO_min':round(min(ricp(H[H.family!=f],y,1)['ic'] for f in H.family.unique()),4),
           'per_family':{f:round(spearmanr(g.c,g[y],nan_policy='omit')[0],3) for f,g in H.groupby('family')}}
    print('H-b',y,hb[y]['ALL'],'IS',hb[y]['IS']['ic'],'OOS',hb[y]['OOS']['ic'],'LOFOmin',hb[y]['LOFO_min'])
res['H-b']=hb
# ---------------- H-c value trap
rows=[]
A63={fam:T[r.key].dropna().rolling(63).mean().dropna() for fam,r in FAM.iterrows()}
for me in pd.date_range('2019-12-31',idx[-1],freq='ME'):
    if (me+pd.Timedelta(days=1)).month not in (1,7): continue
    i0=nth_after(me)
    if i0 is None or i0+126>=len(idx): continue
    t0=idx[i0]; mem=U.loc[t0]; mem=mem[mem].index
    pe=PE.loc[t0,PE.columns.intersection(mem)]; ey=(1/pe[pe>0]); thr=ey.median()
    for fam,r in FAM.iterrows():
        a=A63[fam][A63[fam].index<=me]
        if len(a)<252*3-63: continue
        pct=(a<=a.iloc[-1]).mean()
        for t in r.tks:
            if t in ey.index and ey[t]>=thr:
                rows.append(dict(family=fam,ticker=t,entry=t0,pct=pct,ey=ey[t],X=stock_x(t,i0,126)))
C=pd.DataFrame(rows).dropna(); C['split']=C.entry.map(split); C.to_csv('b3_Hc_panel.csv',index=False)
def hc_stat(C):
    u=C.groupby(['family','entry']).agg(X=('X','mean'),pct=('pct','first')).reset_index()
    hi,lo=u[u.pct>=.67].X,u[u.pct<=.33].X
    return (hi.mean()-lo.mean(),len(hi),len(lo),u) if len(hi) and len(lo) else (np.nan,len(hi),len(lo),u)
est,nh,nl,u=hc_stat(C); perm=[]
for _ in range(5000):
    q=u.copy(); q['pct']=q.groupby('family').pct.transform(lambda v: rng.permutation(v.values))
    perm.append(q[q.pct>=.67].X.mean()-q[q.pct<=.33].X.mean())
perm=np.array(perm)
hc=dict(diff=round(est,4),n_hi=nh,n_lo=nl,p1_neg=round((np.sum(perm<=est)+1)/5001,4),mean_hi=round(u[u.pct>=.67].X.mean(),4),mean_lo=round(u[u.pct<=.33].X.mean(),4),
        IS=round(hc_stat(C[C.split=='IS'])[0],4),OOS=round(hc_stat(C[C.split=='OOS'])[0],4),
        LOFO=[round(hc_stat(C[C.family!=f])[0],4) for f in C.family.unique()],n_units=len(u),SE=round(np.nanstd(perm),4))
print('H-c',hc); res['H-c']=hc
# ---------------- H-d gap
rows=[]
for fam,r in FAM.iterrows():
    s=T[r.key].dropna(); c63=np.log(s/s.shift(63)).dropna()
    for me in pd.date_range('2017-03-31',idx[-1],freq='ME'):
        if (me+pd.Timedelta(days=1)).month not in (1,4,7,10): continue
        h=c63[c63.index<=me]
        if len(h)<24: continue
        i0=nth_after(me)
        if i0 is None or i0-63<0: continue
        past=basket_x(r.tks,i0-63,63); fwd=basket_x(r.tks,i0,63)
        gap=(h.iloc[-1]>=h.quantile(.67)) and (past<=0)
        rows.append(dict(family=fam,entry=idx[i0],c63=h.iloc[-1],past=past,gap=gap,X=fwd))
G=pd.DataFrame(rows).dropna(subset=['X','past']); G['split']=G.entry.map(split); G.to_csv('b3_Hd_panel.csv',index=False)
def hd_stat(G): return G[G.gap].X.mean()-G[~G.gap].X.mean()
est=hd_stat(G); perm=[]
for _ in range(5000):
    q=G.copy(); q['gap']=q.groupby('family').gap.transform(lambda v: rng.permutation(v.values)); perm.append(hd_stat(q))
perm=np.array(perm)
hd=dict(diff=round(est,4),n_gap=int(G.gap.sum()),n=len(G),p1_pos=round((np.sum(perm>=est)+1)/5001,4),IS=round(hd_stat(G[G.split=='IS']),4),OOS=round(hd_stat(G[G.split=='OOS']),4),
        LOFO=[round(hd_stat(G[G.family!=f]),4) for f in G.family.unique()],SE=round(perm.std(),4),gap_by_fam=G[G.gap].groupby('family').size().to_dict())
print('H-d',hd); res['H-d']=hd
# ---------------- đa kiểm định 13 trial
pv={f"Ha_{g['th']}_{g['L']}_{g['h']}":g['p1'] for g in grid}
for k in ('s1','s2','s3'): pv[f'Hb_{k}']=hb[k]['ALL']['p2']
pv['Hc']=hc['p1_neg']; pv['Hd']=hd['p1_pos']
ks=sorted(pv,key=pv.get); m=len(ks); bh={}
for r_,k in enumerate(ks,1): bh[k]=min(1,pv[k]*m/r_)
for k in reversed(ks[:-1]): pass
res['multiple']={k:dict(p=pv[k],bonf=round(min(1,pv[k]*13),4),bh_q=round(bh[k],4)) for k in ks}
print(json.dumps(res['multiple'],indent=0))
json.dump(res,open('b3_results.json','w'),indent=1,default=str)
