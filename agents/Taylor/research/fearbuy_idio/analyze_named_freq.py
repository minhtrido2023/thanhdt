import pandas as pd, numpy as np
df = pd.read_csv('episodes_idio.csv')
named=['PNJ','VEA','DGC','HPG','OGC','OCH','PVX','HVN','FLC','TV1','JVC','FIT']
print("=== Named cases present in idiosyncratic panel? ===")
for t in named:
    s=df[df.ticker==t]
    if len(s)==0: print(f"{t}: absent"); continue
    for _,r in s.iterrows():
        print(f"{t} {r.entry_date} stock_dd={r.stock_dd} mkt_dd={r.mkt_dd} PB={r.PB} r12m={r.r12m} r24m={r.r24m} ex24m={r.ex24m}")

print("\n=== FREQUENCY: idiosyncratic quality-floor episodes per year ===")
by=df.groupby('yr').size()
print(by.to_string())
print(f"mean/yr={by.mean():.1f}  median/yr={by.median():.0f}  (2014+ mean={by[by.index>=2014].mean():.1f})")

print("\n=== WITHIN-YEAR CORRELATION proxy: dispersion of ex24m within a year ===")
# if cases in same year were highly correlated, ex24m (already market-excess) would cluster tightly
g=df[df.ex24m.notna()].groupby('yr')['ex24m']
print("year   N   mean_ex24  std_ex24")
for yr,grp in g:
    if len(grp)>=5:
        print(f"{yr}  {len(grp):>3}   {grp.mean()*100:>7.1f}%  {grp.std()*100:>6.1f}%")
