#!/usr/bin/env python3
"""
cyclical_multi.py — cyclical framework across commodity groups
==============================================================
Same contrarian-cyclical event study as rubber, now for steel/urea/DAP groups.
Commodity GOOD (price>trailing-36m median) vs WEAK × stock deep-dd → fwd 1Y/2Y.
Hypothesis (from rubber): buy at commodity TROUGH (WEAK) + stock dislocated.
Commodities: rubber(USD/kg), iron_ore(USD/t, steel proxy), urea, dap (USD/t).
Map: rubber→DRI/PHR/DPR/GVR/TRC/HRC ; iron_ore→HPG/HSG/NKG ; urea→DCM/DPM ; dap→DDV/DGC ; caustic_soda→CSV.
DGC note: real product = yellow phosphorus P4 (no clean history); DAP = partial phosphate-chain proxy.
Output: data/cyclical_multi.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"
MAP={"rubber":["DRI","PHR","DPR","GVR","TRC","HRC"],"iron_ore":["HPG","HSG","NKG"],
     "urea":["DCM","DPM"],"dap":["DDV","DGC"],
     "caustic_soda":["CSV"]}  # CSV = chlor-alkali (NaOH); own caustic-soda cycle, NOT dap
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000',capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))
def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    alltk=sorted({t for v in MAP.values() for t in v}); tks="','".join(alltk)
    df=bq(f"""SELECT t.ticker,t.time,t.Close,t.PB,
      SAFE_DIVIDE(LEAD(t.Close,252) OVER w,t.Close)-1 AS f1y,
      SAFE_DIVIDE(LEAD(t.Close,504) OVER w,t.Close)-1 AS f2y
      FROM tav2_bq.ticker AS t WHERE t.ticker IN ('{tks}') AND t.Close IS NOT NULL
      WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)""")
    df["time"]=pd.to_datetime(df["time"]); df=df.sort_values(["ticker","time"]).reset_index(drop=True)
    df["hi52"]=df.groupby("ticker")["Close"].transform(lambda x:x.rolling(252,min_periods=60).max())
    df["dd52"]=(df["Close"]/df["hi52"]-1)*100; df["month"]=df["time"].values.astype("datetime64[M]")
    me_all=df.groupby(["ticker","month"]).tail(1).copy()
    def cell(g):
        n=len(g.dropna(subset=["f1y"]))
        if n<10: return None
        return (f"{n:>5}{g['f1y'].median()*100:>+9.0f}%{(g['f1y']>0).mean()*100:>7.0f}%"
                f"{g['f2y'].median()*100:>+9.0f}%{(g['f2y']>0).mean()*100:>7.0f}%")
    P("# Cyclical framework across commodity groups (contrarian test)")
    P("buckets by commodity regime (price vs trailing-36m median) x stock deep-dd<-25%")
    P("")
    for com,tickers in MAP.items():
        rb=pd.read_csv(os.path.join(WORKDIR,"data",f"{com}_monthly.csv"))
        rb.columns=["month","price"]; rb["month"]=pd.to_datetime(rb["month"]); rb=rb.sort_values("month")
        rb["med36"]=rb["price"].rolling(36,min_periods=18).median()
        rb["good"]=rb["price"]>rb["med36"]
        rb["pctile5y"]=rb["price"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())
        avail=[t for t in tickers if t in me_all["ticker"].unique()]
        me=me_all[me_all["ticker"].isin(avail)].merge(rb[["month","good","price","pctile5y"]],on="month",how="left").dropna(subset=["good"])
        me["good"]=me["good"].astype(bool); me["deep"]=me["dd52"]<-25
        cur=rb.iloc[-1]
        P(f"## {com.upper()}  stocks={avail}  | latest {cur['price']:.0f}, good={bool(cur['good'])}, pctile5y={cur['pctile5y']:.2f} ({rb['month'].iloc[-1].date()})")
        P(f"{'bucket':<24}{'N':>5}{'1Ymed':>9}{'1Ywin':>7}{'2Ymed':>9}{'2Ywin':>7}")
        for rg,rl in [(False,"WEAK"),(True,"GOOD")]:
            for dp,dl in [(True,"+deep dd"),(False,"+normal")]:
                c=cell(me[(me["good"]==rg)&(me["deep"]==dp)])
                if c: P(f"{'commodity '+rl+' '+dl:<24}"+c)
        c=cell(me[~me["good"]]);
        if c: P(f"{'WEAK (any dd)':<24}"+c)
        c=cell(me[me["good"]]);
        if c: P(f"{'GOOD (any dd)':<24}"+c)
        P("")
    P("Read: across groups, if 'commodity WEAK + deep-dd' > 'GOOD', the contrarian")
    P("buy-the-trough pattern generalizes beyond rubber.")
    with open(os.path.join(WORKDIR,"data","cyclical_multi.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("\nSaved data/cyclical_multi.md")
if __name__=="__main__": main()
