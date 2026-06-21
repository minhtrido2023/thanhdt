#!/usr/bin/env python3
"""
rubber_cyclical.py — PROTOTYPE cyclical framework for rubber stocks
===================================================================
Tests the user's cyclical thesis: for commodity cyclicals (rubber plantations),
the master signal is the COMMODITY price (not consistent-quality history). Buy
when commodity is at a GOOD level (elevated vs its own history) AND the stock is
dislocated (deep drawdown / cheap), ideally in market CRISIS/BEAR.

Commodity = world natural rubber (USD/kg, IndexMundi monthly 2006-2026).
Rubber stocks (plantation, rubber = REVENUE not cost): DRI, PHR, DPR, GVR, TRC, HRC.
(DRC excluded — tire maker, rubber is an input/cost = inverse exposure.)

Per-month observation per stock: forward 1Y / 2Y return (from panel Close), bucketed by
  rubber regime: GOOD (price > trailing 36m median) vs WEAK
  stock drawdown: DEEP (dd52<-25%) vs not
  + DT5G state at obs.
Hypothesis: rubber-GOOD × stock-DEEP-drawdown (dislocation while commodity strong)
= best forward returns. Face validity: DRI April-2025 (8390, below par).
Output: data/rubber_cyclical.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile, pickle
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"
RUBBER_TK=["DRI","PHR","DPR","GVR","TRC","HRC"]
STATE={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try:
        r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000',capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    rb=pd.read_csv(os.path.join(WORKDIR,"data","rubber_monthly.csv"))
    rb["month"]=pd.to_datetime(rb["month"])
    rb=rb.sort_values("month").reset_index(drop=True)
    rb["med36"]=rb["usd_per_kg"].rolling(36,min_periods=18).median()
    rb["yoy"]=rb["usd_per_kg"]/rb["usd_per_kg"].shift(12)-1
    rb["good"]=rb["usd_per_kg"]>rb["med36"]   # elevated vs own 3Y history (point-in-time)
    rb["pctile5y"]=rb["usd_per_kg"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())

    # rubber stock daily prices + PB + dd from BQ (panel may lack some; pull direct)
    tickers="','".join(RUBBER_TK)
    df=bq(f"""SELECT t.ticker,t.time,t.Close,t.PB,t.MA200,
      SAFE_DIVIDE(LEAD(t.Close,252) OVER w, t.Close)-1 AS f1y,
      SAFE_DIVIDE(LEAD(t.Close,504) OVER w, t.Close)-1 AS f2y
      FROM tav2_bq.ticker AS t WHERE t.ticker IN ('{tickers}') AND t.Close IS NOT NULL
      WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)""")
    df["time"]=pd.to_datetime(df["time"]); df=df.sort_values(["ticker","time"]).reset_index(drop=True)
    df["hi52"]=df.groupby("ticker")["Close"].transform(lambda x:x.rolling(252,min_periods=60).max())
    df["dd52"]=(df["Close"]/df["hi52"]-1)*100
    df["month"]=df["time"].values.astype("datetime64[M]")
    P("# Rubber cyclical prototype — commodity regime × stock dislocation")
    P("")
    P(f"rubber tickers available: {sorted(df['ticker'].unique())}")
    P(f"rubber price range: {rb['usd_per_kg'].min():.2f}-{rb['usd_per_kg'].max():.2f} USD/kg, latest {rb['usd_per_kg'].iloc[-1]:.2f} ({rb['month'].iloc[-1].date()}), good={bool(rb['good'].iloc[-1])} pctile5y={rb['pctile5y'].iloc[-1]:.2f}")
    P("")

    # DT5G state
    st=bq("SELECT s.time,s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time")
    st["time"]=pd.to_datetime(st["time"])

    # monthly obs per stock (month-end)
    me=df.groupby(["ticker","month"]).tail(1).copy()
    me=me.merge(rb[["month","good","yoy","pctile5y","usd_per_kg"]],on="month",how="left")
    me=pd.merge_asof(me.sort_values("time"),st.sort_values("time"),on="time",direction="backward")
    me=me.dropna(subset=["good"]).copy()
    me["good"]=me["good"].astype(bool); me["deep"]=me["dd52"]<-25

    def cell(g):
        n=len(g.dropna(subset=["f1y"])); n2=len(g.dropna(subset=["f2y"]))
        if n<10: return None
        return (f"{n:>5}{g['f1y'].median()*100:>+9.0f}%{(g['f1y']>0).mean()*100:>7.0f}%"
                f"{g['f2y'].median()*100:>+9.0f}%{(g['f2y']>0).mean()*100:>7.0f}%")

    P("## Forward return by rubber regime × stock dislocation (all rubber stocks pooled)")
    P(f"{'bucket':<26}{'N':>5}{'1Y med':>9}{'1Ywin':>7}{'2Y med':>9}{'2Ywin':>7}")
    P("-"*64)
    for rg,rlab in [(True,"rubber GOOD"),(False,"rubber WEAK")]:
        for dp,dlab in [(True,"+ stock DEEP dd<-25%"),(False,"+ stock normal")]:
            g=me[(me["good"]==rg)&(me["deep"]==dp)]
            c=cell(g)
            if c: P(f"{rlab+' '+dlab:<26}"+c)
    P("")
    # add crisis/bear overlay on the best bucket
    P("## rubber GOOD × deep-dd × market state")
    P(f"{'state':<26}{'N':>5}{'1Y med':>9}{'1Ywin':>7}{'2Y med':>9}{'2Ywin':>7}")
    gb=me[(me["good"])&(me["deep"])]
    for s in [1,2,3,4,5]:
        g=gb[gb["state"]==s]; c=cell(g)
        if c: P(f"{STATE[s]:<26}"+c)
    allc=cell(gb)
    if allc: P(f"{'ALL states':<26}"+allc)
    P("")
    # baseline: all rubber-stock obs regardless
    P("## Baselines")
    for lab,g in [("ALL obs",me),("rubber GOOD (any dd)",me[me['good']]),("rubber WEAK (any dd)",me[~me['good']])]:
        c=cell(g)
        if c: P(f"  {lab:<26}"+c)
    P("")
    # face validity DRI
    P("## Face validity — DRI near the April-2025 dislocation")
    dri=me[(me["ticker"]=="DRI")&(me["time"]>="2024-09-01")&(me["time"]<="2025-07-31")]
    P(f"  {'date':<12}{'Close':>7}{'dd52':>7}{'PB':>6}{'rubber':>8}{'good':>6}{'state':<8}{'f1y':>7}")
    for _,r in dri.iterrows():
        P(f"  {str(r['time'].date()):<12}{r['Close']:>7.0f}{r['dd52']:>+6.0f}%{r['PB']:>6.2f}{r['usd_per_kg']:>8.2f}{str(bool(r['good'])):>6}{STATE.get(r['state'],'?'):<8}{(r['f1y']*100 if pd.notna(r['f1y']) else float('nan')):>+6.0f}%")
    P("")
    P("Read: if 'rubber GOOD × deep-dd' >> baselines (esp. in CRISIS/BEAR), the cyclical")
    P("framework works — buy quality cyclical when commodity strong + price dislocated.")
    P("")
    me.to_csv(os.path.join(WORKDIR,"data","rubber_cyclical_obs.csv"),index=False)
    with open(os.path.join(WORKDIR,"data","rubber_cyclical.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("Saved data/rubber_cyclical.md + data/rubber_cyclical_obs.csv")

if __name__=="__main__":
    main()
