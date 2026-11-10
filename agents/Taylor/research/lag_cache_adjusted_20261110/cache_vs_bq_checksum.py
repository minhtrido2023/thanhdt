import duckdb, pandas as pd
D='mike/agents/Taylor/research/lag_cache_adjusted_20261110/data/'
b=pd.read_csv(D+'bq_live_checksum_ty.csv')
c=duckdb.connect()
l=c.sql("select ticker, year(time) y, count(*) n, sum(Close) sc, sum(Open) so, sum(Volume_3M_P50) sv from 'data/bq_cache/ticker/*.parquet' where Close>0 group by 1,2").df()
m=b.merge(l,on=['ticker','y'],how='outer',suffixes=('_bq','_lc'),indicator=True)
print(m._merge.value_counts())
x=m[m._merge=='both']
for col in ['n','sc','so','sv']:
    r=(x[col+'_lc']/x[col+'_bq']-1).abs()
    bad=x[r>1e-6]
    print(col,'mismatch ticker-years',len(bad),'by year',bad.y.value_counts().sort_index().to_dict())
print(m[m._merge!='both'].groupby(['_merge','y']).size().to_string())
bad=x[((x.sc_lc/x.sc_bq-1).abs()>1e-6)]
print(bad.sort_values('y')[['ticker','y','n_bq','n_lc','sc_bq','sc_lc']].head(30).to_string())
bad.to_csv(D+'cache_vs_bq_close_mismatch.csv',index=False)
