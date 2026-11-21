import pandas as pd, numpy as np, json
df=pd.read_pickle('/tmp/pf_df.pkl'); df=df.sort_values(['ticker','time'])
g=df.groupby('ticker')
df['mx']=g['r'].transform(lambda x:x.abs().shift(1).rolling(250,min_periods=120).max())
df['O1']=g['Open'].shift(-1); df['C10']=g['Close'].shift(-11)
df['V10']=df.V.groupby(df.ticker).shift(-11); df['VO1']=df.VO.groupby(df.ticker).shift(-1)
df['h10']=df.C10/df.O1-1-(df.V10/df.VO1-1)
df['tv']=df.Price*df.Volume
out={}
hose=df.mx.between(.065,.0725)
defs={'D1_floor7':hose&(df.r<=-.064),'D2_ext_dn_any_ge7':(df.r<=-.07)&df.mx.notna(),'D3_hose_dn5':hose&(df.r<=-.05)}
tr=pd.to_datetime
for k,m in defs.items():
    e=df[m&df.in_universe&df.h10.notna()&(df.tv>2e9)]  # >2 ty VND GTGD/ngay (prelim liquidity)
    d=e.groupby('time').agg(n=('r','size'),h=('h10','mean')).reset_index()
    # broad-selloff days: n>=10
    for thr in (1,10,20):
        s=d[d.n>=thr].copy()
        s['new']=(s.time.diff().dt.days.fillna(99)>7)  # ~5 sessions
        s['cl']=s.new.cumsum()
        c=s.groupby('cl').agg(t0=('time','min'),n=('n','sum'),h=('h','mean'))
        for era,(a,b) in {'IS':('2014-01-01','2019-12-31'),'OOS':('2020-01-01','2026-12-31')}.items():
            cc=c[(c.t0>=a)&(c.t0<=b)]
            out[f'{k}|n>={thr}|{era}']=dict(clusters=len(cc),events=int(cc.n.sum()),sd_bps=round(cc.h.std()*1e4,0) if len(cc)>2 else None)
for k,v in out.items(): print(k,v)
json.dump(out,open('/tmp/pf_counts.json','w'))
