import pandas as pd, numpy as np
df=pd.read_pickle('/tmp/pf_df.pkl'); df=df[(df.gap<=5)&df.r.notna()]
# causal empirical band: rolling 250-obs max of |r| per ticker (shifted), bucket
g=df.groupby('ticker')
df['mx']=g['r'].transform(lambda x:x.abs().shift(1).rolling(250,min_periods=120).max())
b=df.dropna(subset=['mx']).copy()
b['cls']=pd.cut(b.mx,[0,.065,.0725,.095,.105,.145,.155,9],labels=['<6.5','~7','7-9.5','~10','10-14.5','~15','>15.5'])
print(b.groupby('y').cls.value_counts(normalize=True).unstack().round(3))
# how close is min r to -band on extremes: share of days r<=-6.5% that sit within 0.3pp of a canonical band
e=b[b.r<=-.06]
for y,gg in e.groupby('y'):
    print(y,len(gg),'near-7%:',round(((gg.r+.07).abs()<.004).mean(),3),'near-10%:',round(((gg.r+.10).abs()<.004).mean(),3),'near-15%:',round(((gg.r+.15).abs()<.004).mean(),3))
