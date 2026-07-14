# -*- coding: utf-8 -*-
"""P3: honest inference. Events cluster into EPISODES (overlapping fwd windows) -> block bootstrap.
Plus pb_z confound control within event."""
import numpy as np, pandas as pd
P="/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/probe_capit_div/"
o=pd.read_csv(P+"forward.csv"); o["date"]=pd.to_datetime(o["date"])
# EPISODE = events whose forward windows overlap (gap < 180d) -> one independent block
ed = pd.Series(sorted(o.date.unique()))
epi = (ed.diff().dt.days.fillna(999) >= 180).cumsum()
emap = dict(zip(ed, epi))
o["epi"]=o.date.map(emap)
print("events->episodes:", o.date.nunique(), "->", o.epi.nunique())
for e,g in o.groupby("epi"): print(f"  epi{e}: {[str(x.date()) for x in sorted(g.date.unique())]}")

rng=np.random.default_rng(7)
for hor in ("3M","6M"):
    x=o[o.hor==hor].copy()
    x["hi_dy"]=x.dy3 > x.groupby("date").dy3.transform("median")
    print(f"\n===== {hor} =====")
    for m in ("mdd","ret"):
        # per-EPISODE effect = mean of within-event hi-lo diffs inside that episode
        pr=x.groupby(["date","hi_dy"])[m].mean().unstack().dropna()
        dif=(pr[True]-pr[False]).rename("d").reset_index()
        dif["epi"]=dif.date.map(emap)
        blk=dif.groupby("epi")["d"].mean()
        n=len(blk); t=blk.mean()/(blk.std(ddof=1)/np.sqrt(n))
        # block bootstrap over episodes
        bs=np.array([rng.choice(blk.values,n,replace=True).mean() for _ in range(20000)])
        p=2*min((bs<=0).mean(),(bs>=0).mean())
        print(f"  {m:4s} EPISODE-block: {blk.mean():+6.2f}pp  t={t:5.2f}  N_epi={n}  "
              f"wins={int((blk>0).sum())}/{n}  boot95=[{np.percentile(bs,2.5):+.2f},{np.percentile(bs,97.5):+.2f}]  p={p:.3f}")
    # pb_z confound control: within event, regress m ~ hi_dy + pbz
    import itertools
    for m in ("mdd","ret"):
        z=x.copy()
        z[m+"_dm"]=z[m]-z.groupby("date")[m].transform("mean")           # demean by event
        z["hi_dm"]=z.hi_dy.astype(float)-z.groupby("date").hi_dy.transform("mean")
        z["pbz_dm"]=z.pbz-z.groupby("date").pbz.transform("mean")
        X=np.c_[np.ones(len(z)), z.hi_dm, z.pbz_dm]; y=z[m+"_dm"].values
        b=np.linalg.lstsq(X,y,rcond=None)[0]
        # cluster-robust SE by EPISODE
        res=y-X@b; XtXi=np.linalg.inv(X.T@X); meat=np.zeros((3,3))
        for e in z.epi.unique():
            i=(z.epi==e).values; u=(X[i]*res[i,None]).sum(0); meat+=np.outer(u,u)
        V=XtXi@meat@XtXi; se=np.sqrt(np.diag(V))
        print(f"  {m:4s} FE-event + pbz control, SE clustered by episode: hi_dy coef={b[1]:+6.2f}pp  t={b[1]/se[1]:5.2f}")
