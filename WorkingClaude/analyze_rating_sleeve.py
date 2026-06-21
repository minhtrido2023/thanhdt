#!/usr/bin/env python3
"""analyze_rating_sleeve.py — (A) does the rating x PB-floor value sleeve ADD to v11/v12.1 (momentum)?

Builds a monthly equal-weight basket of the COMBINED signal (rating-proxy + pb_z<=-1 + book-trustworthy)
forward-1M returns, then measures: (1) correlation with v11 & v12.1 monthly returns, (2) whether a
blended ensemble (momentum + small sleeve) improves Calmar/MaxDD. Thesis: the sleeve is contrarian
(anti-correlated with momentum) so it should help risk-adjusted return, esp. in correction years.
"""
import warnings; warnings.filterwarnings("ignore")
import os, sys, subprocess, tempfile
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
from io import StringIO
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"

def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except Exception: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

SLEEVE_SQL="""
WITH dd AS (
  SELECT t.ticker, t.time, DATE_TRUNC(t.time, MONTH) mo,
    (t.ROIC3Y>=0.10 AND t.ROE_Min3Y>=0.05
     AND SAFE_DIVIDE(t.PB-t.PB_MA5Y,NULLIF(t.PB_SD5Y,0))<=-1.0
     AND t.ROE_Min5Y>=0) AS sig,
    SAFE_DIVIDE(LEAD(t.Close,21) OVER w, t.Close)-1 AS f1m
  FROM tav2_bq.ticker t WHERE t.time>="2014-01-01"
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)
),
me AS (SELECT *, ROW_NUMBER() OVER (PARTITION BY ticker, mo ORDER BY time DESC) rn FROM dd)
SELECT mo, COUNTIF(sig) n_sig,
  AVG(IF(sig AND f1m BETWEEN -0.95 AND 5, f1m, NULL)) AS sleeve_ret
FROM me WHERE rn=1
GROUP BY mo ORDER BY mo
"""

def perf(monthly):
    """monthly = pd.Series of monthly returns. Returns CAGR, MaxDD, Calmar, Sharpe (annualized)."""
    nav=(1+monthly.fillna(0)).cumprod()
    yrs=len(monthly)/12.0
    cagr=nav.iloc[-1]**(1/yrs)-1
    dd=(nav/nav.cummax()-1).min()
    sharpe=monthly.mean()/monthly.std()*np.sqrt(12) if monthly.std()>0 else np.nan
    return cagr, dd, (cagr/abs(dd) if dd<0 else np.nan), sharpe

def main():
    sl=bq(SLEEVE_SQL); sl["mo"]=pd.to_datetime(sl["mo"]).dt.to_period("M"); sl=sl.set_index("mo")
    # sleeve: when no signal names that month -> cash (0 return)
    sl["sleeve_ret"]=sl["sleeve_ret"].fillna(0.0)
    print(f"sleeve months: {len(sl)} | months with >=1 signal: {(sl['n_sig']>0).sum()} | "
          f"avg basket size when active: {sl[sl.n_sig>0]['n_sig'].mean():.0f}")

    nav=pd.read_csv(os.path.join(WORKDIR,"data","5sys_prodspec_201401_202605.csv"))
    nav["time"]=pd.to_datetime(nav["time"]); nav=nav.set_index("time")
    mo_nav=nav[["V1_V11_TQ34b","V4_V121_ENS_TQ34b","VNI"]].resample("ME").last()
    mret=mo_nav.pct_change().rename(columns={"V1_V11_TQ34b":"v11","V4_V121_ENS_TQ34b":"v121","VNI":"vni"})
    mret.index=mret.index.to_period("M")
    df=mret.join(sl["sleeve_ret"], how="inner").dropna(subset=["v11","v121"])
    df["sleeve_ret"]=df["sleeve_ret"].fillna(0.0)

    print("\n=== Correlation (monthly returns) ===")
    print(f"  sleeve vs v11 : {df['sleeve_ret'].corr(df['v11']):+.2f}")
    print(f"  sleeve vs v12.1: {df['sleeve_ret'].corr(df['v121']):+.2f}")
    print(f"  sleeve vs VNI : {df['sleeve_ret'].corr(df['vni']):+.2f}")
    print(f"  v11 vs v12.1  : {df['v11'].corr(df['v121']):+.2f}  (reference)")

    print("\n=== Standalone perf (monthly, 2014-now) — CAGR / MaxDD / Calmar / Sharpe ===")
    for name,col in [("v11","v11"),("v12.1","v121"),("sleeve","sleeve_ret"),("VNI","vni")]:
        c,d,cal,sh=perf(df[col]); print(f"  {name:<7} {c*100:6.1f}% / {d*100:6.1f}% / {cal:4.2f} / {sh:4.2f}")

    print("\n=== Blended ensemble (momentum + value sleeve) ===")
    for base,bcol in [("v11","v11"),("v12.1","v121")]:
        print(f"  -- base {base} --")
        for w in [0.0,0.10,0.15,0.20,0.30]:
            blend=(1-w)*df[bcol]+w*df["sleeve_ret"]
            c,d,cal,sh=perf(blend)
            print(f"    {int((1-w)*100)}/{int(w*100)}  CAGR {c*100:5.1f}%  MaxDD {d*100:6.1f}%  Calmar {cal:4.2f}  Sharpe {sh:4.2f}")

    # correction-year check
    print("\n=== Correction years (where momentum lagged) — sleeve vs v11 annual return ===")
    ann=df[["v11","v121","sleeve_ret","vni"]].groupby(df.index.year).apply(lambda g:(1+g).prod()-1)
    for y in [2018,2020,2022,2024]:
        if y in ann.index:
            r=ann.loc[y]; print(f"  {y}: v11 {r['v11']*100:+5.1f}%  v12.1 {r['v121']*100:+5.1f}%  sleeve {r['sleeve_ret']*100:+5.1f}%  VNI {r['vni']*100:+5.1f}%")
    df.to_csv(os.path.join(WORKDIR,"data","rating_sleeve_analysis.csv"))
    print("\nsaved data/rating_sleeve_analysis.csv")

if __name__=="__main__": main()
