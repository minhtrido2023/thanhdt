import sys,numpy as np,pandas as pd
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/fill_timing_recheck_20261119')
from engine import boot,BUY,SELL,ROOT,OUT
P=pd.read_pickle(f"{ROOT}/data/intraday_full.pkl"); rows=[]
for tk,df in P.items():
    df=df.sort_values("time").copy(); df["date"]=df.time.dt.date; df["hm"]=df.time.dt.strftime("%H:%M")
    for d,day in df.groupby("date"):
        if len(day)<15: continue
        hm=day.hm; op=day["open"].iloc[0]
        if day.hm.iloc[0]>"09:30" or op<=0: continue
        r={"tk":tk,"date":pd.Timestamp(d),"close":day.close.iloc[-1],"tv":(day.close*day.volume).sum()}
        ok=True
        for t in BUY+SELL:
            m=day[hm>=t]
            if not len(m): ok=False;break
            r["p"+t]=(m["open"].iloc[0]/op-1)*1e4
        if ok and all(np.isfinite(r["p"+t]) and abs(r["p"+t])<1500 for t in BUY+SELL): rows.append(r)
R=pd.DataFrame(rows).sort_values(["tk","date"]); R["ret"]=R.groupby("tk")["close"].pct_change()
R["buy"]=R[["p"+t for t in BUY]].mean(axis=1); R["sell"]=R[["p"+t for t in SELL]].mean(axis=1)
liq=R.groupby("tk")["tv"].median(); q=liq.quantile(.2); low=set(liq[liq<=q].index)
res=[]
for nm,X in [("all335",R),("lowliq_bottom20pct",R[R.tk.isin(low)])]:
  for w,(a,b) in {"A":("2023-09-11","2025-12-31"),"B":("2026-01-01","2026-05-12"),"ALL":("2023-09-11","2026-05-12")}.items():
    Y=X[(X.date>=a)&(X.date<=b)]
    for col in ["buy","sell"]:
        D=Y.groupby("date")[col].mean(); dn=(Y.groupby("date")["ret"].median()<0).reindex(D.index).fillna(False)
        for sn,s in [("all",D),("down",D[dn]),("up",D[~dn])]:
            if len(s)<10: continue
            m,lo,hi,n,k=boot(s,5000); res.append(dict(panel=nm,win=w,metric=col,subset=sn,mean_bps=round(m,2),ci_lo=round(lo,2),ci_hi=round(hi,2),n_days=n,n_tickers=Y.tk.nunique()))
pd.DataFrame(res).to_csv(f"{OUT}/results_15m_335.csv",index=False); print(pd.DataFrame(res).to_string())
