import pandas as pd, numpy as np
EXP='/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_market_prob/'

agg=pd.read_csv(EXP+'agg_pepb.csv', parse_dates=['time'])
agg['pe_con']=agg.mcap_pe_all/agg.earn_all
agg['pe_t100']=agg.mcap_pe_t100/agg.earn_t100
agg['pb_con']=agg.mcap_pb_all/agg.book_all
agg['pb_t100']=agg.mcap_pb_t100/agg.book_t100

off=pd.read_csv(EXP+'mkt_pe_daily.csv', parse_dates=['time'])[['time','mkt_pe','vni']]
loc=pd.read_csv('/home/trido/thanhdt/WorkingClaude/data/VNINDEX_pe_only.csv', parse_dates=['time'])[['time','Pe']].rename(columns={'Pe':'pe_loc'})

vni=pd.read_csv(EXP+'vni_close.csv', parse_dates=['time']).rename(columns={'Close':'vni_close'})

df=vni.merge(agg[['time','pe_con','pe_t100','pb_con','pb_t100','n_pe_all','n_pb_all']],on='time',how='left')
df=df.merge(off[['time','mkt_pe']],on='time',how='left').merge(loc,on='time',how='left')
df=df[df.time>='2008-01-01'].reset_index(drop=True)

# official PE combined: BQ mirror where available, else local csv (2014-2016)
df['pe_off']=df.mkt_pe.fillna(df.pe_loc)

print('=== VALIDATION: constructed vs official PE ===')
ov=df.dropna(subset=['pe_off','pe_con'])
print('overlap N=%d %s..%s'%(len(ov),ov.time.min().date(),ov.time.max().date()))
print('corr(level)=%.4f  corr(dlog)=%.4f'%(ov.pe_off.corr(ov.pe_con), np.log(ov.pe_off).diff().corr(np.log(ov.pe_con).diff())))
print('mean ratio con/off=%.4f  median abs err=%.3f pts'%((ov.pe_con/ov.pe_off).mean(), (ov.pe_con-ov.pe_off).abs().median()))
print('last5:'); print(ov.tail(5)[['time','pe_off','pe_con','pe_t100','pb_con','pb_t100']].to_string(index=False))

cur=df.dropna(subset=['pe_con']).iloc[-1]
print('\n=== CURRENT (%s) ==='%cur.time.date())
print('VNINDEX=%.2f  PE_off=%.2f  PE_con=%.2f  PE_t100=%.2f  PB_con=%.3f  PB_t100=%.3f  n_pe=%d n_pb=%d'%(
 cur.vni_close,cur.pe_off,cur.pe_con,cur.pe_t100,cur.pb_con,cur.pb_t100,cur.n_pe_all,cur.n_pb_all))

def pct_rank(s, v):
    s=s.dropna()
    return 100.0*(s<v).mean(), len(s)

end=cur.time
windows={'full_2008+':df.time>='2008-01-01',
         'last_10Y':df.time>=end-pd.DateOffset(years=10),
         'last_5Y':df.time>=end-pd.DateOffset(years=5),
         'last_3Y':df.time>=end-pd.DateOffset(years=3)}
print('\n=== PERCENTILE RANK (100 = dat nhat lich su) ===')
rows=[]
for name,m in windows.items():
    sub=df[m]
    for col,val in [('pe_con',cur.pe_con),('pe_t100',cur.pe_t100),('pb_con',cur.pb_con),('pb_t100',cur.pb_t100),('pe_off',cur.pe_off)]:
        p,n=pct_rank(sub[col],val)
        q=sub[col].dropna().quantile([0.05,0.25,0.5,0.75,0.95])
        rows.append(dict(window=name,metric=col,cur=round(val,3),pctile=round(p,1),N=n,
            p05=round(q.iloc[0],2),p25=round(q.iloc[1],2),p50=round(q.iloc[2],2),p75=round(q.iloc[3],2),p95=round(q.iloc[4],2)))
r=pd.DataFrame(rows); print(r.to_string(index=False))
r.to_csv(EXP+'percentiles.csv',index=False)
df.to_csv(EXP+'daily_panel.csv',index=False)
