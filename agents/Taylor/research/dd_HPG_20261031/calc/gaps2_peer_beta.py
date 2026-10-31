# β tuần peers thép VN vs VNINDEX (BQ tav2_bq.ticker, Close điều chỉnh), 2y & 3y; Dimson 1 lag (bù giao dịch mỏng); ADV & % tuần lợi suất 0.
import pandas as pd, numpy as np
d=pd.read_csv('gaps2_peers_px.csv',parse_dates=['time'])
px=d.pivot(index='time',columns='ticker',values='Close').sort_index()
tv=d.pivot(index='time',columns='ticker',values='tv').sort_index()
end=px.index.max(); print('end',end.date())
rows=[]
for yrs in (2,3):
    s=px[px.index>end-pd.DateOffset(years=yrs)]
    w=s.resample('W-FRI').last().pct_change()
    m=w['VNINDEX']
    for t in [c for c in px.columns if c!='VNINDEX']:
        df=pd.concat([w[t],m,m.shift(1)],axis=1,keys=['r','m','m1']).dropna()
        if len(df)<50: continue
        b=np.cov(df.r,df.m)[0,1]/df.m.var()
        X=np.column_stack([np.ones(len(df)),df.m,df.m1]); co=np.linalg.lstsq(X,df.r,rcond=None)[0]
        bd=co[1]+co[2]
        res=df.r-(co[0]+co[1]*df.m+co[2]*df.m1)
        r=np.corrcoef(df.r,df.m)[0,1]
        se=np.std(df.r-b*df.m,ddof=2)/(df.m.std()*np.sqrt(len(df)-1))
        z=(df.r==0).mean()
        adv=tv[t][tv.index>end-pd.DateOffset(months=6)].median()
        rows.append(dict(yrs=yrs,ticker=t,n=len(df),beta=b,se=se,dimson=bd,blume=0.67*b+0.33,corr=r,zero_wk=z,adv6m_med_ty=adv))
o=pd.DataFrame(rows).round(3); print(o.to_string(index=False))
for yrs in (2,3):
    x=o[(o.yrs==yrs)&(o.ticker.isin(['SMC','TVN','VGS','TLH','HMC']))]
    print(yrs,'y median ex-BANNED/POM: beta',x.beta.median(),'dimson',x.dimson.median())
    x=o[(o.yrs==yrs)&(o.ticker.isin(['SMC','TVN','VGS','TLH','HMC','HSG','NKG']))]
    print(yrs,'y median incl HSG/NKG ref: beta',x.beta.median(),'dimson',x.dimson.median())
