import sys,os,pandas as pd,numpy as np
sys.path.insert(0,'/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/fill_timing_recheck_20261119')
import engine
from engine import BUY,SELL
W=os.path.dirname(os.path.abspath(__file__))
EXT='/home/trido/thanhdt/WorkingClaude/data/intraday_1m_ext_20261119'
def mkroot(name,src):
    d=f"{W}/{name}/data/intraday_1m"; os.makedirs(d,exist_ok=True)
    for f in os.listdir(src):
        pd.read_csv(f"{src}/{f}",parse_dates=["time"]).pipe(lambda x:x[x.time.dt.date>=pd.Timestamp("2026-06-12").date()]).to_csv(f"{d}/{f}",index=False)
    return f"{W}/{name}"
engine.ROOT=mkroot("_root_new",EXT)
Rn=engine.load_1m()
engine.ROOT=mkroot("_root_old","/home/trido/thanhdt/WorkingClaude/data/intraday_1m")
Ro=engine.load_1m()
# control 06-12
cols=["p"+t for t in BUY+SELL]+["buy","sell"]
a=Ro[Ro.date=="2026-06-12"].set_index("tk")[cols]; b=Rn[Rn.date=="2026-06-12"].set_index("tk")[cols]
dd=(b-a).abs(); dd.to_csv(f"{W}/selfcheck_0612_old_vs_new.csv"); print("control 06-12 |Δ| bps: max %.2f mean %.2f n_tk %d"%(dd.max().max(),dd.mean().mean(),len(dd)))
print(dd[["buy","sell"]].round(2).T.to_string())
R=Rn[Rn.date>"2026-06-12"].dropna(subset=["buy","sell"]); R.to_csv(f"{W}/ticker_day_oos.csv",index=False)
print("OOS days",R.date.nunique(),"tickers",R.tk.nunique(),"tk-days",len(R),"weeks",R.date.dt.strftime("%G-%V").nunique())
low5=list(pd.read_csv('/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/fill_timing_recheck_20261119/ticker_day_1m.csv').groupby("tk")["tv"].median().sort_values().index[:5]); print("low5",low5)
res=[]
for col in ["buy","sell"]+cols[:-2]: engine.summarize(R,"OOS",col,res)
for col in ["buy","sell"]: engine.summarize(R[R.tk.isin(low5)],"OOS|lowliq5",col,res)
# halves
dts=sorted(R.date.unique()); mid=dts[len(dts)//2]
for nm,X in [("OOS_H1",R[R.date<mid]),("OOS_H2",R[R.date>=mid])]:
    for col in ["buy","sell"]: engine.summarize(X,nm,col,res)
Z=pd.DataFrame(res); Z.to_csv(f"{W}/results_oos.csv",index=False); print(Z.to_string())
dn=(R.groupby("date")["ret"].median()<0); print("down-day share %.3f (n=%d)"%(dn.mean(),len(dn)))
# vn proxy: median cross-sectional cum return
print("tickers n per day min/max",R.groupby("date").tk.nunique().min(),R.groupby("date").tk.nunique().max())
