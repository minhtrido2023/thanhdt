import pandas as pd, numpy as np
df=pd.read_csv('episodes_idio.csv')
print("=== Confirmation filter robustness BY YEAR (is it just 2019-20?) ===")
print("year   N_conf  winr_conf | N_noconf winr_noconf   (win = ex24m>0)")
for yr in range(2010,2025):
    s=df[(df.yr==yr)&df.ex24m.notna()]
    if len(s)<10: continue
    c=s[s.r6m>0]; nc=s[s.r6m<=0]
    print(f"{yr}   {len(c):>4}   {(c.ex24m>0).mean()*100 if len(c) else 0:>4.0f}%   |  {len(nc):>4}    {(nc.ex24m>0).mean()*100 if len(nc) else 0:>4.0f}%")

print("\n=== SENSITIVITY: idiosyncratic market gate (mkt within X of 1y high) ===")
# re-derive requires the raw mkt_dd; the panel already applied mkt_dd>=-0.15. Sub-split by mkt_dd bands.
for lo,hi,lbl in [(-0.15,-0.10,'mkt -15..-10% (borderline)'),(-0.10,-0.05,'mkt -10..-5%'),(-0.05,0.01,'mkt -5..0% (truly calm)')]:
    s=df[(df.mkt_dd>=lo)&(df.mkt_dd<hi)&df.ex24m.notna()]
    c=s[s.r6m>0]
    print(f"{lbl:>28}: N={len(s):>4} all_winr={ (s.ex24m>0).mean()*100:>3.0f}%  | conf6m N={len(c):>3} winr={ (c.ex24m>0).mean()*100 if len(c) else 0:>3.0f}%")
