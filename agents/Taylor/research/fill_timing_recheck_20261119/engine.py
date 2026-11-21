import glob, os, sys, numpy as np, pandas as pd
ROOT='/home/trido/thanhdt/WorkingClaude'; OUT=os.path.dirname(os.path.abspath(__file__))
BUY=["11:00","11:15","13:00","13:15","13:30"]; SELL=["09:15","09:30","09:45","10:00"]
def px_at(day,hhmm,hm):
    m=day[hm>=hhmm]
    return m["open"].iloc[0] if len(m) else np.nan
def load_1m():
    rows=[]
    for f in sorted(glob.glob(f"{ROOT}/data/intraday_1m/*.csv")):
        tk=os.path.basename(f)[:-4]; df=pd.read_csv(f,parse_dates=["time"]).sort_values("time")
        df["date"]=df.time.dt.date; df["hm"]=df.time.dt.strftime("%H:%M")
        dc=df.groupby("date")["close"].last(); dates=list(dc.index)
        prev=None
        for i,(d,day) in enumerate(df.groupby("date")):
            pc=prev; prev=day["close"].iloc[-1]
            if len(day)<50: continue
            hm=day["hm"]; op=day["open"].iloc[0]
            r={"tk":tk,"date":pd.Timestamp(d),"prev_close":pc,"open":op,"close":day["close"].iloc[-1],"tv":(day.close*day.volume).sum()}
            for t in BUY+SELL: r["p"+t]=(px_at(day,t,hm)/op-1)*1e4
            m=day[hm<="11:15"]; r["c1115"]=m["close"].iloc[-1] if len(m) else np.nan
            rows.append(r)
    R=pd.DataFrame(rows).sort_values(["tk","date"])
    R["buy"]=R[["p"+t for t in BUY]].mean(axis=1); R["sell"]=R[["p"+t for t in SELL]].mean(axis=1)
    R["ret"]=R["close"]/R["prev_close"]-1
    return R
def boot(s,n=10000,seed=0):
    s=s.dropna(); wk=s.index.to_series().dt.strftime("%G-%V"); g=[v.values for _,v in s.groupby(wk)]
    rng=np.random.default_rng(seed); k=len(g); out=[]
    for _ in range(n):
        idx=rng.integers(0,k,k); out.append(np.concatenate([g[i] for i in idx]).mean())
    return s.mean(),np.percentile(out,2.5),np.percentile(out,97.5),len(s),k
def summarize(R,label,col,res):
    D=R.groupby("date")[col].mean()
    down=R.groupby("date")["ret"].median()<0
    for nm,mask in [("all",slice(None)),("down_days",down.reindex(D.index).fillna(False)),("up_days",~down.reindex(D.index).fillna(False))]:
        s=D[mask] if nm!="all" else D
        if len(s)<10: continue
        m,lo,hi,n,k=boot(s); res.append(dict(set=label,metric=col,subset=nm,mean_bps=round(m,2),ci_lo=round(lo,2),ci_hi=round(hi,2),n_days=n,n_weeks=k))
if __name__=="__main__":
    R=load_1m(); R.to_csv(f"{OUT}/ticker_day_1m.csv",index=False)
    liq=R.groupby("tk")["tv"].median().sort_values(); low5=list(liq.index[:5])
    wins={"A_2023-09_2025-12":("2023-09-11","2025-12-31"),"B_2026-01_2026-06":("2026-01-01","2026-06-12"),"ALL":("2023-09-11","2026-06-12")}
    res=[]
    for w,(a,b) in wins.items():
        X=R[(R.date>=a)&(R.date<=b)].dropna(subset=["buy","sell"])
        for col in ["buy","sell"]+["p"+t for t in BUY+SELL]: summarize(X,w,col,res)
        L=X[X.tk.isin(low5)]
        for col in ["buy","sell"]: summarize(L,w+"|lowliq5",col,res)
    # control leg
    C=R.dropna(subset=["prev_close","c1115"]); C=C[C.prev_close>0]
    ctl={"open_vs_prior":((C.open/C.prev_close-1)*1e4).mean(),"t1115_vs_prior":((C.c1115/C.prev_close-1)*1e4).mean(),"n_tkdays":len(C)}
    pd.DataFrame(res).to_csv(f"{OUT}/results_1m.csv",index=False)
    pd.Series(ctl).to_csv(f"{OUT}/selfcheck_control.csv"); print(pd.DataFrame(res).to_string()); print(ctl); print("lowliq5",low5)
