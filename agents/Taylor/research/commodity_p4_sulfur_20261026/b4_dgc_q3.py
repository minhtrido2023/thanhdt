"""B4: giá Q3/2026 P4 + sulfur ngụ ý gì cho KQKD Q3 DGC. Fit CHỈ trên quý <=2026Q2. Chỉ đọc FORECAST.md đã khoá (không sửa)."""
import os, sys, json, pandas as pd, numpy as np
O=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,f'{O}/../commodity_cycle_te_20261026')
from common import fin
q=pd.read_csv(f'{O}/b2_qavg.csv',index_col=0,parse_dates=True)
F=fin(); g=F[F.ticker=='DGC'].set_index('quarter').sort_index()
# đối chiếu chuỗi BQ sunsirs vs data/phosphorus_weekly.csv (cùng nguồn SunSirs, nạp khác đường)
w=pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/phosphorus_weekly.csv'); print(w.columns.tolist(), len(w))
dc=[c for c in w.columns if 'date' in c.lower() or 'time' in c.lower() or 'week' in c.lower()][0]; vc=[c for c in w.columns if c!=dc and w[c].dtype!=object][0]
w[dc]=pd.to_datetime(w[dc]); w=w.set_index(dc)[vc].sort_index()
d=pd.read_parquet(f'{O}/raw.parquet'); s=d[d.metric_key=='yellow_phosphorus'].set_index('observation_date').value.sort_index()
j=pd.concat([w,s.reindex(w.index,method='ffill')],axis=1,keys=['csv','bq']).dropna(); rel=(j.bq/j.csv-1)
xc=dict(n=len(j),from_=str(j.index.min().date()),median_absdiff_pct=round(float(rel.abs().median()*100),3),p95_absdiff_pct=round(float(rel.abs().quantile(.95)*100),3),max_absdiff_pct=round(float(rel.abs().max()*100),2))
print('crosscheck',xc)
P=pd.read_csv(f'{O}/b2_panel.csv'); P=P[P.ticker=='DGC'].set_index('quarter').sort_index()
fit=P[(P.index>='2019Q1')&(P.index<='2026Q2')]
qq=q.index.to_period('Q').astype(str); q.index=qq
cq=np.log(q.P4_qavg/q.P4_qavg.shift(1))
x_yoy=float(q.loc['2026Q3','c_P4']); x_S=float(q.loc['2026Q3','c_S']); x_qoq=float(cq['2026Q3'])
def ols(X,y): X=np.c_[np.ones(len(X)),X]; b=np.linalg.lstsq(X,y,rcond=None)[0]; e=y-X@b; return b,e.std(ddof=X.shape[1])
f1=fit[['cP4','np_d']].dropna(); b1,s1=ols(f1[['cP4']].values,f1.np_d.values)
f2=fit[['cP4','cS','np_d']].dropna(); b2,s2=ols(f2[['cP4','cS']].values,f2.np_d.values)
# QoQ: np_qd = (NP0-NP1)/DT1
g['np_qd']=(g.NP_P0-g.NP_P1)/g.Revenue_P1; g['cq']=[cq.get(i,np.nan) for i in g.index]
f3=g[(g.index>='2018Q2')&(g.index<='2026Q2')][['cq','np_qd']].dropna(); b3,s3=ols(f3[['cq']].values,f3.np_qd.values)
base=g.loc['2025Q3']; q2=g.loc['2026Q2']
NP25,R25=base.NP_P0/1e9,base.Revenue_P0/1e9; NPq2,Rq2=q2.NP_P0/1e9,q2.Revenue_P0/1e9
def implied(nd,sd,ref_np,ref_rev): return dict(point=round(ref_np+nd*ref_rev,0),band80=[round(ref_np+(nd-1.2816*sd)*ref_rev,0),round(ref_np+(nd+1.2816*sd)*ref_rev,0)])
out=dict(crosscheck_bq_vs_csv=xc,inputs=dict(P4_Q3_26=round(q.loc['2026Q3','P4_qavg']),P4_Q3_25=round(q.loc['2025Q3','P4_qavg']),P4_Q2_26=round(q.loc['2026Q2','P4_qavg']),
   c_P4_yoy=round(x_yoy,3),c_P4_qoq=round(x_qoq,3),S_Q3_26=round(q.loc['2026Q3','S_qavg']),S_Q3_25=round(q.loc['2025Q3','S_qavg']),c_S_yoy=round(x_S,3),
   c_S_hist_max_in_fit=round(float(f2.cS.max()),3),DGC_Q3_25_NP_bn=round(NP25,1),DGC_Q3_25_Rev_bn=round(R25,1),DGC_Q2_26_NP_bn=round(NPq2,1),DGC_Q2_26_Rev_bn=round(Rq2,1),NP_field='ticker_financial.NP_P0 (ban cong bo dau)'),
 M1_yoy_P4=dict(n=len(f1),b=b1.round(3).tolist(),resid_sd=round(s1,3),np_d_hat=round(b1[0]+b1[1]*x_yoy,3),**implied(b1[0]+b1[1]*x_yoy,s1,NP25,R25)),
 M2_yoy_P4_S=dict(n=len(f2),b=b2.round(3).tolist(),resid_sd=round(s2,3),np_d_hat=round(b2[0]+b2[1]*x_yoy+b2[2]*x_S,3),extrapolation=bool(x_S>f2.cS.max()),**implied(b2[0]+b2[1]*x_yoy+b2[2]*x_S,s2,NP25,R25)),
 M3_qoq_P4=dict(n=len(f3),b=b3.round(3).tolist(),resid_sd=round(s3,3),np_qd_hat=round(b3[0]+b3[1]*x_qoq,3),**implied(b3[0]+b3[1]*x_qoq,s3,NPq2,Rq2)),
 locked_forecast_ref=dict(file='../dgc_q3_forecast_20261026/FORECAST.md',md5='d6ea39f404e4058452532fec353732ad',point=320,band50=[270,370],band80=[215,425],note='chi doc doi chieu'))
json.dump(out,open(f'{O}/b4_dgc_q3.json','w'),indent=1,default=float); print(json.dumps(out,indent=1,default=float))
