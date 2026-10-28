import pandas as pd, json
t=pd.DataFrame(json.load(open("SEALED_truth.json")))
r=pd.read_csv("livermore_results.csv")
d=t.merge(r,on="label")
d["pred_up"]=(d.dir=="UP").astype(int)
d["hit"]=(d.pred_up==d.up).astype(int)
d["brier"]=(d.p_up-d.up)**2
d["b1hit"]=(d.b1_up==d.up).astype(int)
d["b2hit"]=(d.b2_up==d.up).astype(float).where(d.b2_up.notna())
def rep(x,name):
    print(f"{name:28s} n={len(x):2d} hit={x.hit.sum():2d} Brier={x.brier.mean():.3f} B1hit={x.b1hit.sum():2d} B2hit={x.b2hit.sum() if x.b2hit.notna().any() else float('nan')} upfrac={x.up.mean():.2f}")
rep(d,"ALL")
rep(d[d.kind=="transition"],"transition")
rep(d[d.kind=="control"],"control")
rep(d[d.recognised==0],"not recognised")
rep(d[d.recognised==1],"recognised (contaminated)")
print(d[["label","kind","date","state","prev","dir","p_up","fwd20","hit","b1_up","b2_up","recognised"]].sort_values("label").to_string(index=False))
d.to_csv("scored.csv",index=False)
