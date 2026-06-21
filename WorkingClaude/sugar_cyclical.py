#!/usr/bin/env python3
"""
sugar_cyclical.py — cyclical framework for the Vietnamese SUGAR group
=====================================================================
Same contrarian-cyclical event study as rubber/steel/urea/dap, now for sugar.
Driver = world sugar price (USD/kg, Thai-export anchored). Group = SLS/SBT/LSS/KTS/QNS.

Sugar-specific structural overlay (the key difference vs other commodity groups):
  Vietnam imposed an ANTI-DUMPING (AD) duty of 47.64% on Thai sugar from Jun-2021
  (+ 47.64% anti-circumvention on 5 ASEAN re-routers from Aug-2022), running 5 years
  (review/expiry ~mid-2026). This decoupled the DOMESTIC sugar price UP from world
  price 2022-2024 (cheap Thai imports cut off) -> the 2022-24 profit boom is part
  world-price (2023 global deficit, India export ban) + part PROTECTION premium.
  Smuggled Thai sugar still caps the domestic premium partially (user's point).
  => we test the regime split PRE vs POST protection, not just world-price buckets.

QNS caveat: hybrid (Vinasoy soymilk ~half of profit) -> weaker pure-sugar signal.
Output: data/sugar_cyclical.md
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
TICKERS=["SLS","SBT","LSS","KTS","QNS"]
PROTECT_START=pd.Timestamp("2021-06-01")  # AD duty official

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000',capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    tks="','".join(TICKERS)
    # ---- price series + forward returns ----
    df=bq(f"""SELECT t.ticker,t.time,t.Close,t.PB,
      SAFE_DIVIDE(LEAD(t.Close,252) OVER w,t.Close)-1 AS f1y,
      SAFE_DIVIDE(LEAD(t.Close,504) OVER w,t.Close)-1 AS f2y
      FROM tav2_bq.ticker AS t WHERE t.ticker IN ('{tks}') AND t.Close IS NOT NULL
      WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)""")
    df["time"]=pd.to_datetime(df["time"]); df=df.sort_values(["ticker","time"]).reset_index(drop=True)
    df["hi52"]=df.groupby("ticker")["Close"].transform(lambda x:x.rolling(252,min_periods=60).max())
    df["dd52"]=(df["Close"]/df["hi52"]-1)*100; df["month"]=df["time"].values.astype("datetime64[M]")
    me_all=df.groupby(["ticker","month"]).tail(1).copy()

    # ---- sugar regime ----
    rb=pd.read_csv(os.path.join(WORKDIR,"data","sugar_monthly.csv"))
    rb.columns=["month","price"]; rb["month"]=pd.to_datetime(rb["month"]); rb=rb.sort_values("month")
    rb["med36"]=rb["price"].rolling(36,min_periods=18).median()
    rb["good"]=rb["price"]>rb["med36"]
    rb["pctile5y"]=rb["price"].rolling(60,min_periods=24).apply(lambda x:(x.iloc[-1]>=x).mean())
    cur=rb.iloc[-1]

    def cell(g):
        n=len(g.dropna(subset=["f1y"]))
        if n<8: return None
        return (f"{n:>5}{g['f1y'].median()*100:>+9.0f}%{(g['f1y']>0).mean()*100:>7.0f}%"
                f"{g['f2y'].median()*100:>+9.0f}%{(g['f2y']>0).mean()*100:>7.0f}%")

    P("# SUGAR cyclical framework (Vietnam) — contrarian regime x dislocation test")
    P(f"driver = world sugar USD/kg | latest {cur['price']:.2f}, good(>med36)={bool(cur['good'])}, pctile5y={cur['pctile5y']:.2f} ({rb['month'].iloc[-1].date()})")
    P(f"group = {TICKERS} (QNS hybrid: Vinasoy ~half profit)")
    P(f"AD protection era: from {PROTECT_START.date()} (Thai AD 47.64%, 5y -> review ~mid-2026)")
    P("")

    avail=[t for t in TICKERS if t in me_all["ticker"].unique()]
    me=me_all[me_all["ticker"].isin(avail)].merge(rb[["month","good","price","pctile5y"]],on="month",how="left").dropna(subset=["good"])
    me["good"]=me["good"].astype(bool); me["deep"]=me["dd52"]<-25
    me["protected"]=me["month"]>=PROTECT_START

    P("## A) Group pooled: world-sugar regime x stock deep-dd<-25%")
    P(f"{'bucket':<26}{'N':>5}{'1Ymed':>9}{'1Ywin':>7}{'2Ymed':>9}{'2Ywin':>7}")
    for rg,rl in [(False,"WEAK"),(True,"GOOD")]:
        for dp,dl in [(True,"+deep dd"),(False,"+normal")]:
            c=cell(me[(me["good"]==rg)&(me["deep"]==dp)])
            if c: P(f"{'sugar '+rl+' '+dl:<26}"+c)
    for lab,msk in [("WEAK (any dd)",~me["good"]),("GOOD (any dd)",me["good"]),
                    ("deep-dd (any regime)",me["deep"]),("ALL",me["good"].notna())]:
        c=cell(me[msk])
        if c: P(f"{lab:<26}"+c)
    P("")

    P("## B) Protection-era split (structural overlay unique to sugar)")
    P(f"{'bucket':<26}{'N':>5}{'1Ymed':>9}{'1Ywin':>7}{'2Ymed':>9}{'2Ywin':>7}")
    for pr,pl in [(False,"PRE-protect"),(True,"PROTECTED")]:
        for lab,extra in [("all",me["good"].notna()),("WEAK",~me["good"]),("deep-dd",me["deep"])]:
            c=cell(me[(me["protected"]==pr)&extra])
            if c: P(f"{pl+' '+lab:<26}"+c)
    P("")

    P("## C) Per-ticker: world-sugar regime sensitivity (1Y fwd median)")
    P(f"{'tkr':<6}{'N':>5}{'WEAK_1Y':>9}{'GOOD_1Y':>9}{'deepdd_1Y':>11}{'spread':>8}")
    for t in avail:
        g=me[me["ticker"]==t]
        w=g[~g["good"]]["f1y"].median(); gd=g[g["good"]]["f1y"].median(); dd=g[g["deep"]]["f1y"].median()
        sp=(w-gd) if (pd.notna(w) and pd.notna(gd)) else np.nan
        P(f"{t:<6}{len(g.dropna(subset=['f1y'])):>5}"
          f"{(w*100 if pd.notna(w) else float('nan')):>+8.0f}%{(gd*100 if pd.notna(gd) else float('nan')):>+8.0f}%"
          f"{(dd*100 if pd.notna(dd) else float('nan')):>+10.0f}%{(sp*100 if pd.notna(sp) else float('nan')):>+7.0f}pp")
    P("")
    P("Read: WEAK>GOOD spread positive => contrarian buy-the-trough holds for sugar.")
    P("Protection era warps the world-price signal: domestic premium decoupled 2022-24.")
    with open(os.path.join(WORKDIR,"data","sugar_cyclical.md"),"w",encoding="utf-8") as f:
        f.write("\n".join(lines))
    P("\nSaved data/sugar_cyclical.md")

if __name__=="__main__": main()
