"""B1 kiểm kê P4 (sunsirs) + sulfur (TE daily): phủ, khe hở, nhảy, đứng giá, thứ trong tuần, độ trễ nạp."""
import pandas as pd, numpy as np, json, os
O=os.path.dirname(os.path.abspath(__file__))
d=pd.read_parquet(f'{O}/raw.parquet'); res={}
for k,src in [('yellow_phosphorus','sunsirs'),('sulfur','trading_economics')]:
    s=d[(d.metric_key==k)&(d.source==src)].set_index('observation_date').value.sort_index()
    g=s.index.to_series().diff().dt.days
    r=np.log(s).diff()
    yr=s.groupby(s.index.year).agg(['count','median','min','max'])
    gaps=g[g>10].sort_values(ascending=False)
    flat=(s.diff()==0).mean()
    big=r[abs(r)>0.10]
    res[k]=dict(source=src,n=int(len(s)),d0=str(s.index.min().date()),d1=str(s.index.max().date()),n_distinct=int(s.nunique()),
        pct_flat_vs_prev=round(float(flat),3),median_gap=float(g.median()),p90_gap=float(g.quantile(.9)),
        n_gaps_gt10d=int(len(gaps)),top_gaps=[(str(i.date()),int(v)) for i,v in gaps.head(12).items()],
        jumps_gt10pct=[(str(i.date()),round(float(v),3)) for i,v in big.items()],
        weekday_counts=s.index.dayofweek.value_counts().sort_index().to_dict(),
        last10=[(str(i.date()),float(v)) for i,v in s.tail(10).items()])
    yr.to_csv(f'{O}/b1_{k}_by_year.csv')
    print(k,json.dumps(res[k],ensure_ascii=False,indent=0)[:3000]); print(yr.to_string())
json.dump(res,open(f'{O}/b1_inventory.json','w'),ensure_ascii=False,indent=1)
