#!/usr/bin/env python3
"""
fa_bank_submodel.py  —  PROTOTYPE bank-specific FA scoring (ICB 8355)
=====================================================================
Direction #3. The generic 7-axis FA model gives banks IC +0.057 (vs non-fin
+0.124) and its quality axis (ROIC/GPM/CF_OA/FSCORE) is meaningless for banks.
This builds a bank-appropriate composite from BQ-available proxies (no NIM/NPL/
CASA/CAR in BQ) and tests whether it beats the generic model on the SAME bank rows.

Bank axes (cross-sectional percentile within each quarter cohort, banks only):
  Profitability 35%  : ROE_Trailing (TTM), ROA_P0            — core bank quality
  Growth        25%  : NP_R, asset growth YoY (credit proxy), Revenue YoY
  Safety/Capital 25% : OwnEq_Cap_P0 (CAR proxy), ROE_Min5Y (thru-cycle floor),
                       -NP_CV (earnings stability)           — substitutes NPL/CAR
  Valuation     15%  : -PB_self_z (cheap vs own history), ROE/PB (justified PB)

Validation: IC vs forward profit_3M (IS 2014-19 / OOS 2020+), tier monotonicity,
head-to-head vs generic total_score on identical rows.
Output: data/fa_bank_submodel.md + fundamental_rating_banks.csv
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

BANK_WEIGHTS={"profit":0.35,"growth":0.25,"safety":0.25,"value":0.15}
TIERS=[("A",.90,1.01),("B",.70,.90),("C",.40,.70),("D",.15,.40),("E",-.01,.15)]

# Pull bank financials joined to the ticker row at-or-before f.time (≤90d), like
# fundamental_rating.py, to get ICB filter + forward profit_3M + valuation history.
SQL="""
WITH joined AS (
  SELECT f.ticker, f.quarter, f.time,
    f.ROE_Trailing, f.ROE5Y, f.ROE_Min5Y, f.ROA_P0,
    f.OwnEq_Cap_P0, f.FinLev_P0,
    f.NP_R, f.Revenue_YoY_P0, f.totalAsset_P0,
    f.PB, f.PB_MA5Y, f.PB_SD5Y,
    f.NP_P0,f.NP_P1,f.NP_P2,f.NP_P3,f.NP_P4,f.NP_P5,f.NP_P6,f.NP_P7,
    t.ICB_Code, t.profit_3M,
    t.Volume_3M_P50*t.Close AS trading_value_1M,
    ROW_NUMBER() OVER (PARTITION BY f.ticker,f.quarter ORDER BY t.time DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker=f.ticker AND t.time<=f.time AND t.time>=DATE_SUB(f.time,INTERVAL 90 DAY)
  WHERE f.time>="2014-01-01" AND t.ICB_Code=8355
    AND t.Volume_3M_P50 IS NOT NULL AND t.Volume_3M_P50*t.Close>=1e9
)
SELECT * EXCEPT(rn) FROM joined WHERE rn=1
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

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    df=bq_query(SQL)
    df["time"]=pd.to_datetime(df["time"])
    df=df.sort_values(["ticker","time"]).reset_index(drop=True)
    P("# Bank FA sub-model PROTOTYPE (ICB 8355)")
    P("")
    P(f"bank-quarter rows {len(df):,} | tickers {df['ticker'].nunique()} "
      f"| {df['time'].min().date()}→{df['time'].max().date()}")

    # ── data hygiene: latest-quarter BS ratios (OwnEq_Cap, FinLev) lag and
    #    arrive as 0 → forward-fill last positive value within ticker so the
    #    safety axis isn't degraded for recent rows / live ranking.
    for c in ["OwnEq_Cap_P0","FinLev_P0"]:
        df[c]=df[c].replace(0,np.nan)
        df[c]=df.groupby("ticker")[c].ffill()

    # ── derived inputs ────────────────────────────────────────────────────
    df["asset_growth"]=df.groupby("ticker")["totalAsset_P0"].pct_change(4).clip(-0.5,2.0)
    NP=[f"NP_P{i}" for i in range(8)]
    a=df[NP].values.astype(float); n=np.sum(~np.isnan(a),axis=1)
    with np.errstate(all="ignore"):
        mu=np.nanmean(a,axis=1); sd=np.nanstd(a,axis=1,ddof=1)
        df["NP_CV"]=np.where(n>=6, sd/np.maximum(np.abs(mu),1e6), np.nan)
    df["NP_CV"]=df["NP_CV"].clip(upper=10)
    df["PB_self_z"]=(df["PB"]-df["PB_MA5Y"])/df["PB_SD5Y"].replace(0,np.nan)
    df["roe_pb"]=df["ROE_Trailing"]/df["PB"].replace(0,np.nan)   # earnings yield on book

    # direction: lower-is-better → negate so higher rank = better
    df["NP_CV_n"]=-df["NP_CV"]; df["FinLev_n"]=-df["FinLev_P0"]; df["PB_self_z_n"]=-df["PB_self_z"]

    AX={"profit":["ROE_Trailing","ROA_P0"],
        "growth":["NP_R","asset_growth","Revenue_YoY_P0"],
        "safety":["OwnEq_Cap_P0","ROE_Min5Y","NP_CV_n"],
        "value":["PB_self_z_n","roe_pb"]}

    for cols in AX.values():
        for c in cols:
            df[f"r_{c}"]=df.groupby("quarter")[c].rank(pct=True,na_option="keep")
    for ax,cols in AX.items():
        df[f"score_{ax}"]=df[[f"r_{c}" for c in cols]].mean(axis=1,skipna=True)

    w=np.array([BANK_WEIGHTS[a] for a in BANK_WEIGHTS]); sc=[f"score_{a}" for a in BANK_WEIGHTS]
    df["bank_score"]=(df[sc].values*w).sum(axis=1)
    df=df.dropna(subset=sc,how="any").copy()
    df["bank_pct"]=df.groupby("quarter")["bank_score"].rank(pct=True)
    def tier_of(p):
        for nm,lo,hi in TIERS:
            if lo<=p<=hi: return nm
        return "E"
    df["bank_tier"]=df["bank_pct"].apply(tier_of)

    have=df.dropna(subset=["profit_3M"]).copy()
    P(f"rows w/ forward profit_3M {len(have):,}")
    P("")

    # ── merge generic total_score for head-to-head ────────────────────────
    gen=pd.read_csv(os.path.join(WORKDIR,"data/fundamental_rating_all.csv"))[["ticker","quarter","total_score","tier"]]
    gen=gen.rename(columns={"tier":"gen_tier"})
    h2h=have.merge(gen,on=["ticker","quarter"],how="inner")

    # ── per-axis IC ───────────────────────────────────────────────────────
    P("## Bank-axis IC vs forward profit_3M")
    P(f"{'axis':<14}{'weight':>8}{'IC':>9}{'N':>7}")
    P("-"*38)
    for ax in BANK_WEIGHTS:
        rho,nn=ic(have[f"score_{ax}"],have["profit_3M"])
        P(f"{ax:<14}{BANK_WEIGHTS[ax]*100:>6.0f}%{rho:>+9.4f}{nn:>7,}")
    P("")

    # ── head-to-head IC: bank model vs generic ───────────────────────────
    P("## Head-to-head IC (identical bank rows): bank sub-model vs generic FA")
    IS=h2h[h2h["time"]<"2020-01-01"]; OOS=h2h[h2h["time"]>="2020-01-01"]
    P(f"{'model':<16}{'IS_IC':>9}{'OOS_IC':>9}{'ALL_IC':>9}{'N':>7}")
    P("-"*50)
    for nm,col in [("bank sub-model","bank_score"),("generic total","total_score")]:
        ri,_=ic(IS[col],IS["profit_3M"]); ro,_=ic(OOS[col],OOS["profit_3M"])
        ra,n=ic(h2h[col],h2h["profit_3M"])
        P(f"{nm:<16}{ri:>+9.4f}{ro:>+9.4f}{ra:>+9.4f}{n:>7,}")
    P("")

    # ── tier monotonicity ─────────────────────────────────────────────────
    P("## Tier monotonicity — median profit_3M (want A>B>C>D>E)")
    def trow(g,col,lab):
        meds=[g[g[col]==t]["profit_3M"].median() for t in ["A","B","C","D","E"]]
        mono="✓" if all(meds[i]>=meds[i+1] for i in range(4)
                         if not(np.isnan(meds[i]) or np.isnan(meds[i+1]))) else "✗"
        return f"{lab:<18}"+"".join(f"{m:>8.2f}" if not np.isnan(m) else f"{'·':>8}" for m in meds)+f"  {mono}"
    P(f"{'model':<18}{'A':>8}{'B':>8}{'C':>8}{'D':>8}{'E':>8}")
    P("-"*60)
    P(trow(have,"bank_tier","bank sub-model"))
    P(trow(h2h,"gen_tier","generic (banks)"))
    P("")

    # ── tercile robustness (3 buckets — better for ~27-bank cross-section) ─
    P("## Tercile robustness — median profit_3M by bank_score tercile (OOS 2020+)")
    oos=have[have["time"]>="2020-01-01"].copy()
    oos["ter"]=oos.groupby("quarter")["bank_score"].transform(
        lambda s: pd.qcut(s.rank(method="first"),3,labels=["Bot","Mid","Top"]) if s.notna().sum()>=6 else np.nan)
    P(f"{'tercile':<10}{'N':>7}{'median':>9}{'mean':>9}{'win%':>8}")
    for t in ["Top","Mid","Bot"]:
        g=oos[oos["ter"]==t]["profit_3M"]
        if len(g): P(f"{t:<10}{len(g):>7,}{g.median():>8.2f}%{g.mean():>8.2f}%{(g>0).mean()*100:>7.1f}%")
    P("")

    # ── current snapshot: latest bank tiers ───────────────────────────────
    latest=df.sort_values("time").groupby("ticker").tail(1).sort_values("bank_score",ascending=False)
    P("## Latest bank ranking (most recent report per bank)")
    P(f"{'tkr':<6}{'quarter':<9}{'tier':<5}{'score':>7}{'ROEtr':>7}{'NP_R':>7}{'OwnEqCap':>9}{'PBz':>7}")
    for _,r in latest.head(25).iterrows():
        P(f"{r['ticker']:<6}{r['quarter']:<9}{r['bank_tier']:<5}{r['bank_score']:>7.3f}"
          f"{r['ROE_Trailing']:>7.3f}{r['NP_R']:>+7.2f}{r['OwnEq_Cap_P0']:>9.3f}"
          f"{(r['PB_self_z'] if not np.isnan(r['PB_self_z']) else 0):>+7.2f}")
    P("")

    out=df[["ticker","quarter","time","ICB_Code","trading_value_1M",
            "score_profit","score_growth","score_safety","score_value",
            "bank_score","bank_pct","bank_tier","profit_3M",
            "ROE_Trailing","ROE_Min5Y","ROA_P0","OwnEq_Cap_P0","NP_R","asset_growth","PB_self_z"]]
    out.to_csv(os.path.join(WORKDIR,"data/fundamental_rating_banks.csv"),index=False)
    with open(os.path.join(WORKDIR,"data","fa_bank_submodel.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved fundamental_rating_banks.csv + data/fa_bank_submodel.md")

if __name__=="__main__":
    main()
