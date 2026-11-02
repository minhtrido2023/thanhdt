import pandas as pd, sys
d = pd.read_csv(sys.argv[1] if len(sys.argv)>1 else 'bq_hydro_peer_pe_r6.csv')
excl = {'PPC','QTP','KHP','TV1'}   # nhiệt điện than x2, phân phối, và chính TV1
for (y, per), g in d.groupby(['y','per']):
    p = g[~g.ticker.isin(excl)].pe_med
    tv = g[g.ticker=='TV1'].pe_med
    print(f"{y} {per}: n={len(p)} median={p.median():.2f} p25={p.quantile(.25):.2f} p75={p.quantile(.75):.2f} | TV1={tv.iloc[0] if len(tv) else float('nan'):.2f}")
