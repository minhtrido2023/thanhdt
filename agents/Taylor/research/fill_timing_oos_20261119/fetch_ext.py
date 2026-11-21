import os,time,sys,json,warnings
warnings.filterwarnings("ignore")
import pandas as pd
from vnstock.explorer.vci import Quote
OUT="/home/trido/thanhdt/WorkingClaude/data/intraday_1m_ext_20261119"; os.makedirs(OUT,exist_ok=True)
TK=["VIX","GEX","MWG","STB","SSI","HPG","VPB","MSN","PVD","DXG","PHR","HT1","VEA","DHA","D2D","NNC"]
log={}
for tk in [t for t in TK if not os.path.exists(f"{OUT}/{t}.csv")]:
    fr=[]
    for a,b in [("2026-06-12","2026-08-15"),("2026-08-15","2026-11-18")]:
        for att in range(4):
            try:
                d=Quote(tk).history(start=a,end=b,interval="1m")
                if d is not None and len(d): fr.append(d)
                break
            except Exception as e:
                log.setdefault(tk,[]).append(f"{a}->{b} att{att}: {repr(e)[:120]}"); time.sleep(5*(att+1))
        time.sleep(1.5)
    if not fr: print("FAIL",tk); continue
    df=pd.concat(fr).drop_duplicates("time").sort_values("time")
    df["time"]=pd.to_datetime(df["time"]); df=df[(df.time>="2026-06-12")&(df.time<"2026-11-19")]
    df[["time","open","high","low","close","volume"]].to_csv(f"{OUT}/{tk}.csv",index=False)
    print("ok",tk,len(df),df.time.min(),df.time.max(),df.time.dt.date.nunique(),flush=True)
json.dump(log,open("fetch_failures.json","w"),indent=1)
