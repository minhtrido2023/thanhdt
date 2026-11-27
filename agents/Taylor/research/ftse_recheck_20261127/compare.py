import pandas as pd, numpy as np
o=pd.read_csv("orig_results_table.csv").set_index("metric"); c=pd.read_csv("control/results_table.csv").set_index("metric"); n=pd.read_csv("now/results_table.csv").set_index("metric")
print("rows", len(o), len(c), len(n), "| same index:", list(o.index)==list(c.index)==list(n.index))
d=[(m,k,o.at[m,k],c.at[m,k]) for m in o.index for k in o.columns if not ((pd.isna(o.at[m,k]) and pd.isna(c.at[m,k])) or (o.at[m,k]==c.at[m,k] if isinstance(o.at[m,k],(bool,np.bool_)) else np.isclose(float(o.at[m,k]),float(c.at[m,k]),rtol=1e-9,atol=1e-9)))]
print("control cells differing:", len(d))
for x in d: print("  ",x)
for m in o.index:
    a,b=o.loc[m],n.loc[m]
    print(f"{m}|{a.pre60:.4g}>{a.post:.4g} d={a.change:.4g} [{a.plc_p5:.4g},{a.plc_p95:.4g}] {a.outside_5_95}|{b.pre60:.4g}>{b.post:.4g} d={b.change:.4g} [{b.plc_p5:.4g},{b.plc_p95:.4g}] pct={b.pctile_of_actual:.1f} N={b.n_placebo} {b.outside_5_95} seas[{b.seas_min:.4g},{b.seas_max:.4g}]")
