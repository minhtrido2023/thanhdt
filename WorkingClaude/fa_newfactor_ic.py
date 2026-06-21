#!/usr/bin/env python3
"""
fa_newfactor_ic.py
==================
Tests candidate NEW fundamental factors for direction #2 (dilution / accruals /
fraud red-flags). For each: standalone IC vs forward profit_3M, AND *incremental*
IC after controlling for the current composite (partial rank-correlation) — a new
factor only earns its place if it predicts beyond what the existing axes already say.

Candidates:
  net_issuance : OShares YoY growth (lag-4 quarters). Documented NEGATIVE predictor
                 (Pontiff-Woodgate). VN dilutes heavily (rights/ESOP/stock dividends)
                 and the Shareholder axis only sees dividends, not dilution.
  accruals     : NP_P0/totalAsset_P0 − CF_OA_P0  (Sloan accruals / assets).
                 High accruals = earnings not backed by cash → NEGATIVE predictor.
  redflag_cnt  : Beneish-lite count of {DSO surge, inventory surge, GPM decline,
                 leverage up} — blow-up screen. Higher = worse → NEGATIVE.

Baseline composite = EW5 (quality+stability+cash+shareholder+growth), the winner
from fa_ic_composites.py (drops negative-IC health & valuation).

IS 2014-19 / OOS 2020+ split. Output: data/fa_newfactor_ic.md
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"
BQ_BIN=r"bq"
EW5=["quality","stability","cash","shareholder","growth"]

SQL="""
SELECT f.ticker, f.quarter, f.time,
  f.OShares, f.totalAsset_P0, f.NP_P0, f.CF_OA_P0,
  f.DSO_P0, f.DSO_P4, f.DIO_P0, f.DIO_P4,
  f.GPM_P0, f.GPM_P4, f.Debt_Eq_P0, f.Debt_Eq_P4
FROM tav2_bq.ticker_financial AS f
WHERE f.time >= "2013-01-01"
ORDER BY f.ticker, f.time
"""

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
             f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=900,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0: raise RuntimeError((r.stdout or r.stderr)[:600])
    return pd.read_csv(StringIO(r.stdout.strip()))

def ic(x,y):
    x=pd.Series(np.asarray(x,float)); y=pd.Series(np.asarray(y,float))
    m=(~x.isna())&(~y.isna())
    if m.sum()<30: return (np.nan,int(m.sum()))
    return (float(np.corrcoef(x[m].rank(),y[m].rank())[0,1]),int(m.sum()))

def partial_ic(factor, control, target):
    """IC of factor vs target after removing the part explained by control (all rank-space)."""
    d=pd.DataFrame({"f":factor,"c":control,"y":target}).dropna()
    if len(d)<50: return (np.nan,len(d))
    fr=d["f"].rank(); cr=d["c"].rank(); yr=d["y"].rank()
    # residualize fr on cr
    b=np.polyfit(cr,fr,1); resid=fr-(b[0]*cr+b[1])
    return (float(np.corrcoef(resid,yr)[0,1]),len(d))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    raw=bq_query(SQL)
    raw["time"]=pd.to_datetime(raw["time"])
    raw=raw.sort_values(["ticker","time"]).reset_index(drop=True)

    # net issuance: OShares YoY via lag-4 quarterly rows per ticker
    raw["OShares_L4"]=raw.groupby("ticker")["OShares"].shift(4)
    raw["net_issuance"]=raw["OShares"]/raw["OShares_L4"]-1
    raw["net_issuance"]=raw["net_issuance"].clip(-0.5,3.0)

    # accruals / assets = NI/assets - CFO/assets  (CF_OA_P0 already = CFO/assets)
    raw["accruals"]=raw["NP_P0"]/raw["totalAsset_P0"]-raw["CF_OA_P0"]
    raw["accruals"]=raw["accruals"].clip(-0.5,0.5)

    # Beneish-lite redflags
    dsi=raw["DSO_P0"]/raw["DSO_P4"]; dii=raw["DIO_P0"]/raw["DIO_P4"]
    raw["redflag_cnt"]=( (dsi>1.30).astype(int)
                        +(dii>1.30).astype(int)
                        +(raw["GPM_P0"]<raw["GPM_P4"]).astype(int)
                        +(raw["Debt_Eq_P0"]>raw["Debt_Eq_P4"]*1.10).astype(int) )

    NEW=["net_issuance","accruals","redflag_cnt"]
    keep=["ticker","quarter"]+NEW
    nf=raw[keep].copy()

    # merge with FA composite + profit_3M
    fa=pd.read_csv(os.path.join(WORKDIR,"fundamental_rating_all.csv"))
    fa["time"]=pd.to_datetime(fa["time"])
    df=fa.merge(nf,on=["ticker","quarter"],how="left").dropna(subset=["profit_3M"]).copy()
    w=np.ones(len(EW5))
    df["ew5"]=(df[[f"score_{a}" for a in EW5]].values*w).sum(1)/w.sum()

    IS=df[df["time"]<"2020-01-01"]; OOS=df[df["time"]>="2020-01-01"]
    P("# New-factor IC test (direction #2: dilution / accruals / fraud)")
    P("")
    P(f"merged rows w/ profit_3M = {len(df):,} | IS={len(IS):,} OOS={len(OOS):,}")
    P("expected sign: all three NEGATIVE (higher issuance/accruals/redflags → worse)")
    P("")
    P("## Standalone IC vs profit_3M")
    P(f"{'factor':<14}{'IS_IC':>9}{'OOS_IC':>9}{'ALL_IC':>9}{'cover%':>8}")
    P("-"*49)
    for f in NEW:
        rho_is,_=ic(IS[f],IS["profit_3M"]); rho_oos,_=ic(OOS[f],OOS["profit_3M"])
        rho_all,n=ic(df[f],df["profit_3M"]); cov=100*df[f].notna().mean()
        P(f"{f:<14}{rho_is:>+9.4f}{rho_oos:>+9.4f}{rho_all:>+9.4f}{cov:>7.1f}%")
    P("")
    P("## Incremental IC after controlling for EW5 composite (partial rank-corr)")
    P("(this is the real test: does the factor predict BEYOND existing axes?)")
    P(f"{'factor':<14}{'partial_IS':>12}{'partial_OOS':>13}{'partial_ALL':>13}")
    P("-"*52)
    for f in NEW:
        pis,_=partial_ic(IS[f],IS["ew5"],IS["profit_3M"])
        poos,_=partial_ic(OOS[f],OOS["ew5"],OOS["profit_3M"])
        pall,_=partial_ic(df[f],df["ew5"],df["profit_3M"])
        P(f"{f:<14}{pis:>+12.4f}{poos:>+13.4f}{pall:>+13.4f}")
    P("")
    P("## Combined: EW5 vs EW5 + best new factors (sign-corrected, equal weight)")
    # sign-correct: subtract negative factors (rank). Build augmented composite.
    for f in NEW:
        df[f"r_{f}"]=df.groupby("quarter")[f].rank(pct=True)
    df["r_ew5"]=df.groupby("quarter")["ew5"].rank(pct=True)
    # augmented = mean(r_ew5, 1-r_issuance, 1-r_accruals, 1-r_redflag)
    df["aug"]=df[["r_ew5"]].assign(
        a=1-df["r_net_issuance"], b=1-df["r_accruals"], c=1-df["r_redflag_cnt"]
    ).mean(axis=1)
    OOSx=df[df["time"]>="2020-01-01"]; ISx=df[df["time"]<"2020-01-01"]
    for name,col in [("EW5","r_ew5"),("EW5+new3","aug")]:
        ri,_=ic(ISx[col],ISx["profit_3M"]); ro,_=ic(OOSx[col],OOSx["profit_3M"]); ra,_=ic(df[col],df["profit_3M"])
        P(f"  {name:<10} IS={ri:+.4f}  OOS={ro:+.4f}  ALL={ra:+.4f}")
    P("")
    P("## Tail-risk test (correct metric for a blow-up SCREEN, not a ranker)")
    P("For each factor: bucket rows, report crash prob P(profit_3M<-20%), 5th pctile, median.")
    P("A valid exclusion screen → worst bucket has materially higher crash prob / fatter left tail.")
    P("")
    for f in NEW:
        d=df.dropna(subset=[f]).copy()
        if f=="redflag_cnt":
            d["bk"]=d[f].clip(0,4).astype(int); buckets=sorted(d["bk"].unique()); lab=lambda b:f"flags={b}"
        else:
            d["bk"]=pd.qcut(d[f].rank(method="first"),5,labels=False); buckets=[0,1,2,3,4]
            lab=lambda b:f"Q{b+1}"+(" (low)" if b==0 else " (high)" if b==4 else "")
        P(f"### {f}")
        P(f"{'bucket':<12}{'N':>7}{'crash%':>9}{'p5':>9}{'median':>9}")
        for b in buckets:
            g=d[d["bk"]==b]["profit_3M"]
            if len(g)<30: continue
            crash=100*(g<-20).mean()
            P(f"{lab(b):<12}{len(g):>7,}{crash:>8.1f}%{np.percentile(g,5):>8.1f}%{g.median():>8.2f}%")
        P("")
    with open(os.path.join(WORKDIR,"data","fa_newfactor_ic.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_newfactor_ic.md")

if __name__=="__main__":
    main()
