import pandas as pd, numpy as np, os
P='/home/trido/thanhdt/WorkingClaude/mike/kb/projects/'
A=P+'delisted-tickers-survivorship-20261020.d/prices_all/'
O=P+'delisted-tickers-survivorship-20261020.d/prices/'; os.makedirs(O,exist_ok=True)
d=pd.read_csv(P+'delisted-tickers-survivorship-20261020.csv').drop_duplicates('ticker').set_index('ticker')
st=pd.read_csv('stats_all.csv')
REQ=['FLC','ROS','HAI','AMD','GAB','ART','TGG','TTB']
def prep(t):
    x=pd.read_csv(A+t+'.csv',parse_dates=['date']).sort_values('date').reset_index(drop=True)
    x['val']=x.nmValue.fillna(0)+x.ptValue.fillna(0)
    # ngay cuoi tren san goc: ngay cuoi cung floor != UPCOM neu co; neu mat khong doi san thi = ngay cuoi
    orig=x[x.floor.isin(['HOSE','HNX'])]
    lst=orig.date.max() if len(orig) else x.date.max()
    tr=orig[orig.nmVolume>0]
    end=tr.date.max() if len(tr) else lst
    x.attrs['lst']=lst
    return x,end
rows=[]
rank=[]
for t in st[st.n>0].ticker:
    x,end=prep(t); o=x[x.date<=end]
    m60=o.val.rolling(60,min_periods=30).median()
    rank.append((t,m60.max()))
rank=pd.DataFrame(rank,columns=['ticker','peak_med60_orig']).sort_values('peak_med60_orig',ascending=False)
top=[t for t in rank.ticker.head(15)]
sel=list(dict.fromkeys(REQ+top))[:16]
def feat(t):
    x,end=prep(t); o=x[x.date<=end].copy()
    px='adClose'; c=o.set_index('date')[px]
    lst=x.attrs['lst']; r={'ticker':t,'last_listed_orig':lst,'halted_cal_days':(lst-end).days,'px_chg_last_trade_to_listed_end':c.iloc[-1] and (x[x.date==lst].adClose.iloc[0]/c.iloc[-1]-1),'exch_orig':o.floor.iloc[-1] if len(o) else None,'first_date':x.date.min(),'end_orig_date':end,'last_date_any':x.date.max(),
       'floor_last_any':x.floor.iloc[-1],'n_days_orig':len(o)}
    nz=o[o.nmVolume>0]; r['last_trade_vol>0']=end
    r['cover_days_expected_gaps']=int(((o.date.diff().dt.days>10)).sum())
    def back(m):
        s=end-pd.DateOffset(months=m); 
        a=c[c.index<=s]
        return c.iloc[-1]/a.iloc[-1]-1 if len(a) else np.nan
    r['ret_12m']=back(12); r['ret_24m']=back(24)
    w=c[c.index>=end-pd.DateOffset(months=24)]
    r['maxDD_24m']=(w/w.cummax()-1).min() if len(w) else np.nan
    r['maxDD_all']=(c/c.cummax()-1).min()
    r['peak_px_k']=c.max(); r['end_px_k']=c.iloc[-1]
    r['med60_value_end_vnd']=o.val.tail(60).median()
    m60=o.val.rolling(60,min_periods=30).median()
    r['peak_med60_vnd']=m60.max(); r['peak_med60_date']=m60.idxmax() and o.date[m60.idxmax()]
    r['ever_adv5bn']=bool((m60>=5e9).any()); r['first_adv5bn']=o.date[m60[m60>=5e9].index[0]] if (m60>=5e9).any() else pd.NaT
    r['days_adv5bn']=int((m60>=5e9).sum())
    pc=x[x.date>end]
    if len(pc):
        r['post_cut_days']=len(pc); r['post_ret']=x.adClose.iloc[-1]/c.iloc[-1]-1; r['post_med_val_vnd']=pc.val.median()
    # adjustment flags
    ratio=(x.adClose/x.close.replace(0,np.nan)); r['adj_ratio_min']=ratio.min(); r['adj_ratio_max']=ratio.max()
    r['zero_vol_share_last60']=(o.nmVolume.tail(60)==0).mean(); r['limit_down_days_last20']=int((o.pctChange.tail(20)<=-6.5).sum()) if 'pctChange' in o else None
    return r
F=pd.DataFrame([feat(t) for t in sel]).join(d[['cat','reason']],on='ticker')
F.to_csv(P+'delisted-big-vanished-prices-20261020.csv',index=False)
rank.head(60).to_csv('rank_top60.csv',index=False)
for t in sel:
    x,end=prep(t)
    out=x[['date','floor','open','high','low','close','adClose','nmVolume','nmValue','ptVolume','ptValue']].copy()
    out['after_last_trade_orig']=out.date>end
    out.to_csv(O+t+'.csv',index=False)
pd.set_option('display.width',250)
print(sel)
print(F[['ticker','exch_orig','end_orig_date','last_listed_orig','halted_cal_days','last_date_any','ret_12m','ret_24m','maxDD_24m','med60_value_end_vnd','peak_med60_vnd','ever_adv5bn','post_ret']].round(3).to_string())
print(rank.head(25).to_string())
