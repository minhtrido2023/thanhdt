import numpy as np, pandas as pd
from scipy import stats as st
snap="mike/agents/Taylor/research/orb_reeval_20260925/vn30f1m_live_snapshot_20260925.csv"
f=pd.read_csv(snap); f["time"]=pd.to_datetime(f["time"])
f["date"]=f["time"].dt.date.astype(str); f["hm"]=f["time"].dt.strftime("%H:%M")
days=[]
for d,g in f.groupby("date"):
    if d<"2026-06-09" or d>"2026-09-24": continue
    g=g.sort_values("time").reset_index(drop=True)
    op=g[g["hm"]<="09:30"]; segd=g[(g["hm"]>"09:30")&(g["hm"]<="14:30")]
    if not(len(op)>=10 and len(segd)>0 and g["hm"].iloc[-1]>="14:25"): continue
    entry=op["close"].iloc[-1]
    days.append(dict(date=d,or_ret=entry/g["close"].iloc[0]-1,entry=entry,post=g[g["hm"]>"09:30"].reset_index(drop=True)))
def sim(exit_hm,stop,tc,min_or):
    recs=[]
    for dd in days:
        if abs(dd["or_ret"])<min_or: continue
        sig=np.sign(dd["or_ret"])
        if sig==0: continue
        entry=dd["entry"]; seg=dd["post"][dd["post"]["hm"]<=exit_hm]
        if len(seg)==0: continue
        ex=seg["close"].iloc[-1]; stp=False
        if stop is not None:
            if sig>0:
                if (seg["low"]<=entry*(1-stop)).any(): ex=entry*(1-stop); stp=True
            else:
                if (seg["high"]>=entry*(1+stop)).any(): ex=entry*(1+stop); stp=True
        recs.append(dict(date=dd["date"],pnl=sig*(ex/entry-1)-tc,stopped=stp))
    return pd.DataFrame(recs)
o=sim("14:00",0.007,0.00025,0.002); d=sim("14:30",None,0.00025,0.0)
t,p=st.ttest_1samp(o["pnl"],0); print(f"ORIG forward: n={len(o)} mean {o['pnl'].mean()*1e4:+.2f}bps sd {o['pnl'].std()*1e4:.1f} t={t:+.3f} p={p:.3f}")
rng=np.random.default_rng(7); bs=np.array([rng.choice(o['pnl'].values,len(o),replace=True).mean() for _ in range(20000)])
print(f"  bootstrap mean 95% CI [{np.percentile(bs,2.5)*1e4:+.2f},{np.percentile(bs,97.5)*1e4:+.2f}]bps  P(mean>=0)={(bs>=0).mean():.3f}")
sel=set(o["date"]); dd=d.set_index("date")
insel=dd.loc[[x for x in dd.index if x in sel],"pnl"]; outsel=dd.loc[[x for x in dd.index if x not in sel],"pnl"]
print(f"DEPLOY split by |OR|>=0.2%: in n={len(insel)} mean {insel.mean()*1e4:+.2f}bps | out n={len(outsel)} mean {outsel.mean()*1e4:+.2f}bps")
tt,pp=st.ttest_ind(insel,outsel,equal_var=False); print(f"  Welch in vs out: t={tt:+.2f} p={pp:.3f}")
for tag,r in [("exit14:00 NO stop |OR|>=.2%",sim("14:00",None,0.00025,0.002)),
              ("exit14:30 stop0.7% |OR|>=.2%",sim("14:30",0.007,0.00025,0.002)),
              ("exit14:00 stop0.7% all-days",sim("14:00",0.007,0.00025,0.0))]:
    print(f"  ablation {tag:<30} n={len(r):>3} mean {r['pnl'].mean()*1e4:>+7.2f}bps cum {((1+r['pnl']).prod()-1)*100:>+6.2f}%")
print(f"stops: {int(o['stopped'].sum())}/{len(o)}; mean khi stopped {o[o['stopped']]['pnl'].mean()*1e4:+.1f}bps | khong stop {o[~o['stopped']]['pnl'].mean()*1e4:+.1f}bps")
print(f"cum ORIG {((1+o['pnl']).prod()-1)*100:+.2f}%")
