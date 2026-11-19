"""A4: nowcast KQKD 12 họ — đúng PREREG.md (md5 556059d1…). Tái dùng common.py (px/univ/fin) của commodity_cycle_te_20261026.
Chế độ --counts: chỉ in số họ×quý (kiểm cấu trúc, không tính IC)."""
import sys, json, glob, numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/commodity_cycle_te_20261026')
from common import px, univ, fin, W
COUNTS='--counts' in sys.argv
C=pd.read_parquet('commodity_snapshot_20261119.parquet'); C['observation_date']=pd.to_datetime(C.observation_date)
C=C.pivot_table(index='observation_date',columns='metric_key',values='value').sort_index()
Mc=pd.read_parquet('macro_snapshot_20261119.parquet'); Mc['observation_date']=pd.to_datetime(Mc.observation_date)
Mc=Mc.pivot_table(index='observation_date',columns='series_key',values='value').sort_index()
def qmean(s,minn):
    s=s.dropna(); m=s.resample('QE').mean(); n=s.resample('QE').count(); return m.where(n>=minn)
def qmon(s,how):  # series tháng: cần đủ 3 tháng
    s=s.dropna(); g=s.resample('QE'); v=g.mean() if how=='mean' else g.sum(); return v.where(g.count()==3)
fx=Mc[['vn_usdvnd','cn_usdcny']].dropna(how='all').ffill(limit=7)
sig={}
# 1 thép
st,io,ck=qmean(C.steel,40),qmean(C.iron_ore_cny,40),qmean(C.coke,40); S=st-1.6*io-0.5*ck
sig[1]=(S-S.shift(4))/st.shift(4)
# 2 heo
h=pd.read_csv(f'{W}/data/hog_price_vn.csv'); h['date']=pd.to_datetime(h.date); hog=h.groupby('date').price_vnd_kg.mean().sort_index()
d=pd.DataFrame({'corn':C.corn,'sbm':C.soybean_meal_cny}).join(fx,how='outer').ffill(limit=7)
feed=0.65*d.corn/100/25.4*d.vn_usdvnd+0.25*d.sbm/1000*d.vn_usdvnd/d.cn_usdcny
hq=qmean(hog,10)  # PREREG_ADDENDUM A1: giá heo tuần trước 2024; fq=qmean(feed,40); Mg=hq-2.8*fq
sig[2]=(Mg-Mg.shift(4))/hq.shift(4)
# 3, 4
for k,key in [(3,'yellow_phosphorus'),(4,'caustic_soda')]:
    q=qmean(C[key],40); sig[k]=np.log(q/q.shift(4))
# 5 polyester
pf,pt,eg=qmean(C.polyester_staple_fiber,40),qmean(C.pta,40),qmean(C.ethylene_glycol,40); S=pf-0.86*pt-0.34*eg
sig[5]=(S-S.shift(4))/pf.shift(4)
# 6 PVC (dấu −)
q=qmean(C.polyvinyl,40); sig[6]=-np.log(q/q.shift(4))
# 7 bán lẻ
sig[7]=qmon(Mc.vn_retail_sales_yoy,'mean')/100
# 8 môi giới
tv=pd.concat([pd.read_parquet(f,columns=['time','Trading_Value']) for f in sorted(glob.glob(f'{W}/data/bq_cache/ticker/*.parquet'))])
tv['time']=pd.to_datetime(tv.time); g=tv.groupby('time').Trading_Value.sum(); g=g[g>0]
q=qmean(g,40); sig[8]=np.log(q/q.shift(4))
# 9,10,11
for k,v in [(9,Mc.vn_tourist_arrivals),(10,Mc.vn_exports+Mc.vn_imports),(11,Mc.vn_car_registrations)]:
    q=qmon(v,'sum'); sig[k]=np.log(q/q.shift(4))
# 12 ngân hàng
ib=Mc.vn_interbank_3m.dropna(); pol=Mc.vn_policy_rate.dropna().reindex(ib.index.union(Mc.vn_policy_rate.dropna().index)).ffill().reindex(ib.index)
sp=qmean(ib-pol,40); bd=qmean(Mc.vn_bond_10y,40)
sig[12]=-((sp-sp.shift(4))+(bd-bd.shift(4)))
# ---- panel (khuôn b2_nowcast.py)
P=px(); U=univ(); F=fin(); idx=P.index
def at(dd):
    i=idx.searchsorted(dd); return idx[i] if i<len(idx) else None
MAP=pd.read_csv('map_v2.csv',dtype=str); MAP=MAP[MAP.status=='IN']
MAP=MAP[MAP.a4_family.fillna('').str.match(r'^\d+')]
rows=[]
for _,m in MAP.iterrows():
    k=int(m.a4_family.split('-')[0]); desc='-' in m.a4_family; s=sig[k].dropna(); lag=max(2,int(m.pit_lag_days))
    for _,r in F[F.ticker==m.ticker].iterrows():
        qe=r.qend
        if qe not in s.index: continue
        sd=at(qe+pd.Timedelta(days=lag))
        if sd is None or pd.isna(r.Release_Date) or r.Release_Date<=sd: continue
        if m.ticker not in U.columns or sd not in U.index or not U.at[sd,m.ticker]: continue
        rows.append(dict(ticker=m.ticker,fam=k,desc=desc,quarter=r.quarter,qend=qe,sig_day=sd,release=r.Release_Date,c=s[qe],
            rev_yoy=np.log(r.Revenue_P0/r.Revenue_P4) if r.Revenue_P0>0 and r.Revenue_P4>0 else np.nan,
            gpm_d=(r.GPM_P0-r.GPM_P4) if abs(r.GPM_P0)<5 and abs(r.GPM_P4)<5 else np.nan,
            np_d=np.clip((r.NP_P0-r.NP_P4)/r.Revenue_P4,-.5,.5) if r.Revenue_P4>0 else np.nan))
D=pd.DataFrame(rows); D.to_csv('a4_panel.csv',index=False)
G=D.groupby(['fam','desc','quarter']).agg(c=('c','first'),np_d=('np_d','median'),rev_yoy=('rev_yoy','median'),gpm_d=('gpm_d','median'),n=('ticker','count')).reset_index().sort_values(['fam','desc','quarter'])
G.to_csv('a4_famq.csv',index=False)
if COUNTS:
    print(G.dropna(subset=['c','np_d']).groupby(['fam','desc']).agg(n=('quarter','count'),q0=('quarter','min'),q1=('quarter','max'),tick=('n','median')).to_string()); sys.exit()
rng=np.random.default_rng(20261119)
def sp_(x,y): return spearmanr(x,y)[0]
def stats(g,y):
    g=g.dropna(subset=['c',y]); n=len(g); x,yv=g.c.values,g[y].values
    if n<12: return dict(n=n,ic=sp_(x,yv) if n>=3 else np.nan,note='không đủ N')
    ic=sp_(x,yv)
    nb=int(np.ceil(n/4)); bs=[]
    for _ in range(5000):
        st=rng.integers(0,n,nb); ii=np.concatenate([(np.arange(s0,s0+4))%n for s0 in st])[:n]; bs.append(sp_(x[ii],yv[ii]))
    sh=[sp_(np.roll(x,k),yv) for k in range(1,n)]; p=(1+np.sum(np.abs(sh)>=abs(ic)-1e-12))/n
    h=n//2
    return dict(n=n,ic=ic,ci5=np.nanpercentile(bs,5),ci95=np.nanpercentile(bs,95),p=p,ic_h1=sp_(x[:h],yv[:h]),ic_h2=sp_(x[h:],yv[h:]),q0=g.quarter.iloc[0],q1=g.quarter.iloc[-1])
out=[]
for (k,desc),g in G.groupby(['fam','desc']):
    for y in ['np_d','rev_yoy','gpm_d']:
        r=stats(g,y); r.update(fam=k,desc=desc,y=y); out.append(r)
R=pd.DataFrame(out)
main=R[(R.y=='np_d')&(~R.desc)].set_index('fam').reindex(range(1,13))
pv=main.p.fillna(1.0).copy(); pv[4]=1.0
o=np.argsort(pv.values); m=12; qv=np.empty(m); ranked=pv.values[o]*m/np.arange(1,m+1)
qv[o]=np.minimum.accumulate(ranked[::-1])[::-1]; main['bh_q']=np.minimum(qv,1)
main['GO']=(main.ic>=0.25)&(main.ci5>0)&(main.ic_h1>0)&(main.ic_h2>0)&(main.bh_q<0.10)&(main.n>=12)
main.loc[4,'GO']=False
R.to_csv('a4_results.csv',index=False); main.to_csv('a4_main_np_d.csv')
pd.set_option('display.width',250); print(main.round(3).to_string())
print(R[R.y!='np_d'].pivot_table(index=['fam','desc'],columns='y',values='ic').round(3).to_string())
print(R[(R.y=='np_d')&(R.desc)].round(3).to_string())
json.dump(dict(go=[int(i) for i in main.index[main.GO]],main=main.reset_index().to_dict('records')),open('a4_results.json','w'),indent=1,default=str)
