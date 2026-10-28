"""B2: giá TB quý hàng hoá (TE daily, biết từ qend+1 phiên) -> KQKD quý đó (công bố sau) + phản ứng giá quanh công bố."""
import pandas as pd, numpy as np, json
from scipy.stats import spearmanr
from common import *
rng=np.random.default_rng(20261026)
T=te(); P=px(); U=univ(); F=fin(); B=bench(P,U); Bc=(1+B).cumprod()
M=cmap(('A','B'))
# giá TB theo quý lịch; chỉ quý có >=40 quan sát (đủ phiên) — quý đầu 2016Q4 bị loại tự nhiên
qa=T.resample('QE').mean(); qn=T.resample('QE').count()
qa=qa.where(qn>=40)
idx=P.index
def at(d):  # phiên đầu tiên >= d
    i=idx.searchsorted(d); return idx[i] if i<len(idx) else None
def ret(tk,d0,d1):
    if d0 is None or d1 is None: return np.nan
    a,b=P.at[d0,tk],P.at[d1,tk]
    return b/a-1-(Bc[d1]/Bc[d0]-1) if a>0 and b>0 else np.nan
rows=[]
for _,m in M.iterrows():
    s=qa[m.te_metric_key]
    yoy=np.log(s/s.shift(4)); qoq=np.log(s/s.shift(1))
    f=F[F.ticker==m.ticker]
    for _,r in f.iterrows():
        qe=r.qend
        if qe not in s.index or pd.isna(yoy.get(qe)) : continue
        sig_day=at(qe+pd.Timedelta(days=2))          # TE cập nhật 23:00 ICT => trễ >=1 phiên sau obs cuối quý
        if sig_day is None or r.Release_Date<=sig_day: continue   # chỉ giữ khi tín hiệu có TRƯỚC công bố
        if sig_day not in U.index or not U.at[sig_day,m.ticker] if m.ticker in U.columns else True: continue
        pre_end=idx[idx.searchsorted(r.Release_Date)-1]       # phiên cuối trước ngày công bố
        te_=at(r.Release_Date+pd.Timedelta(days=1))           # vào lệnh: phiên đầu SAU ngày công bố
        i=idx.get_loc(te_) if te_ is not None else None
        e60=idx[i+60] if i is not None and i+60<len(idx) else None
        rev=np.log(r.Revenue_P0/r.Revenue_P4) if r.Revenue_P0>0 and r.Revenue_P4>0 else np.nan
        rows.append(dict(ticker=m.ticker,family=m.family,sign=m.sign,tier=m.tier,quarter=r.quarter,qend=qe,release=r.Release_Date,
            lag_days=(r.Release_Date-qe).days,c_yoy=yoy[qe]*m.sign,c_qoq=qoq[qe]*m.sign,
            rev_yoy=rev, gpm_d=(r.GPM_P0-r.GPM_P4) if abs(r.GPM_P0)<5 and abs(r.GPM_P4)<5 else np.nan,
            np_d=(r.NP_P0-r.NP_P4)/r.Revenue_P4 if r.Revenue_P4>0 else np.nan,
            np_qd=(r.NP_P0-r.NP_P1)/r.Revenue_P1 if r.Revenue_P1>0 else np.nan,
            pre=ret(m.ticker,sig_day,pre_end), ann=ret(m.ticker,pre_end,te_), post60=ret(m.ticker,te_,e60)))
D=pd.DataFrame(rows)
for c in ['np_d','np_qd']: D[c]=D[c].clip(-0.5,0.5)
D.to_csv('b2_panel.csv',index=False)
print('panel rows',len(D),'tickers',D.ticker.nunique(),'quarters',D.quarter.nunique(), 'lag median',D.lag_days.median())
# family-quarter aggregation (N độc lập = họ x quý)
G=D.groupby(['family','tier','quarter']).agg(c_yoy=('c_yoy','first'),c_qoq=('c_qoq','first'),**{k:(k,'median') for k in ['rev_yoy','gpm_d','np_d','np_qd','pre','ann','post60']},n=('ticker','count')).reset_index()
G['IS']=G.quarter<'2023Q1'
G.to_csv('b2_famq.csv',index=False)
def ic(g,x,y):
    g=g[[x,y]].dropna(); 
    return (spearmanr(g[x],g[y])[0], len(g)) if len(g)>=8 else (np.nan,len(g))
out=[]
for (fam,tier),g in G.groupby(['family','tier']):
    for x,y in [('c_yoy','rev_yoy'),('c_yoy','gpm_d'),('c_yoy','np_d'),('c_qoq','np_qd'),('c_yoy','pre'),('c_yoy','ann'),('c_yoy','post60')]:
        r,n=ic(g,x,y); ri,ni=ic(g[g.IS],x,y); ro,no=ic(g[~g.IS],x,y)
        out.append(dict(family=fam,tier=tier,x=x,y=y,ic=r,n=n,ic_IS=ri,n_IS=ni,ic_OOS=ro,n_OOS=no))
O_=pd.DataFrame(out); O_.to_csv('b2_ic_family.csv',index=False)
pd.set_option('display.width',250)
print(O_.pivot_table(index=['tier','family'],columns='y',values='ic').round(2).to_string())
print(O_.pivot_table(index=['tier','family'],columns='y',values='n').to_string())
# pooled tier A: rank-IC trung bình theo họ, bootstrap theo QUÝ (giữ tương quan chéo họ cùng quý)
A=G[G.tier=='A'].copy()
def pooled(A,x,y):
    A=A.dropna(subset=[x,y]).copy()
    A['rx']=A.groupby('family')[x].rank(pct=True)-.5; A['ry']=A.groupby('family')[y].rank(pct=True)-.5
    est=np.corrcoef(A.rx,A.ry)[0,1]
    qs=A.quarter.unique(); bs=[]
    byq={q:A[A.quarter==q] for q in qs}
    for _ in range(5000):
        s=pd.concat([byq[q] for q in rng.choice(qs,len(qs))]); bs.append(np.corrcoef(s.rx,s.ry)[0,1])
    # permutation: xáo c trong từng họ theo khối quý -> phá liên hệ thời gian
    perm=[]
    for _ in range(2000):
        B_=A.copy(); B_['rx']=B_.groupby('family').rx.transform(lambda v: np.roll(v.values, rng.integers(1,len(v))))
        perm.append(np.corrcoef(B_.rx,B_.ry)[0,1])
    p=(np.sum(np.abs(perm)>=abs(est))+1)/(len(perm)+1)
    return dict(x=x,y=y,ic=round(est,3),ci90=[round(np.percentile(bs,5),3),round(np.percentile(bs,95),3)],p_circshift=round(p,4),n_famq=len(A),n_quarters=len(qs),n_fam=A.family.nunique())
res=[]
for x,y in [('c_yoy','rev_yoy'),('c_yoy','gpm_d'),('c_yoy','np_d'),('c_qoq','np_qd'),('c_yoy','pre'),('c_yoy','ann'),('c_yoy','post60')]:
    for lab,sub in [('ALL',A),('IS',A[A.IS]),('OOS',A[~A.IS])]:
        r=pooled(sub,x,y); r['split']=lab; res.append(r); print(r)
json.dump(res,open('b2_pooled.json','w'),indent=1,default=str)
