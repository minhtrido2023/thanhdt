#!/usr/bin/env python3
"""
fa_horizon_state_ic.py
======================
Tests the long-horizon FA thesis WITH market-state conditioning (DT5G).

Two questions:
  (A) Does FA edge RISE with holding horizon?  IC of FA composite vs forward
      return at 3M / 6M / 1Y / 2Y.  (user: "FA tốt hợp dài hạn hơn ngắn hạn")
  (B) Does market state (DT5G = vnindex_5state_dt5g_live) gate it? Two distinct
      effects, reported separately:
        - RANKING (IC): can FA still rank winners within a state?
        - ABSOLUTE: does the BEST FA tier actually make money, or just "fall less"?
      (user: "cổ tốt chống chịu tốt hơn khi vào bear, nhưng khó vượt crisis —
       FA không cứu được khi tâm lý đè bẹp")

Forward returns computed point-in-time from the ticker Close series (LEAD H
sessions). Entry state = DT5G state on the actual trading day used. No look-ahead:
return is strictly forward; state is as-of entry. Universe = ticker_prune.
Output: data/fa_horizon_state_ic.md
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
STATE={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
HOR=[("f3m","3M"),("f6m","6M"),("f1y","1Y"),("f2y","2Y")]

SQL="""
WITH px AS (
  SELECT t.ticker, t.time, t.Close,
    SAFE_DIVIDE(LEAD(t.Close,63)  OVER w, t.Close)-1 AS f3m,
    SAFE_DIVIDE(LEAD(t.Close,126) OVER w, t.Close)-1 AS f6m,
    SAFE_DIVIDE(LEAD(t.Close,252) OVER w, t.Close)-1 AS f1y,
    SAFE_DIVIDE(LEAD(t.Close,504) OVER w, t.Close)-1 AS f2y
  FROM tav2_bq.ticker AS t
  WHERE t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.Close IS NOT NULL
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)
),
fa AS (
  SELECT f.ticker, f.time AS f_time, f.quarter, f.tier, f.total_score,
    f.score_quality, f.score_stability, f.score_cash, f.score_shareholder, f.score_growth
  FROM tav2_bq.fa_ratings AS f
),
joined AS (
  SELECT fa.*, px.time AS px_time, px.f3m, px.f6m, px.f1y, px.f2y,
    ROW_NUMBER() OVER (PARTITION BY fa.ticker, fa.f_time ORDER BY px.time DESC) AS rn
  FROM fa JOIN px
    ON px.ticker=fa.ticker AND px.time<=fa.f_time AND px.time>=DATE_SUB(fa.f_time, INTERVAL 90 DAY)
)
SELECT j.ticker, j.quarter, j.px_time AS time, j.tier, j.total_score,
  j.score_quality, j.score_stability, j.score_cash, j.score_shareholder, j.score_growth,
  j.f3m, j.f6m, j.f1y, j.f2y, s.state
FROM joined j
LEFT JOIN tav2_bq.vnindex_5state_dt5g_live AS s ON s.time=j.px_time
WHERE j.rn=1
"""

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
             f'--format=csv --max_rows=3000000 < "{tmp}"')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=900,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0: raise RuntimeError((r.stdout or r.stderr)[:800])
    return pd.read_csv(StringIO(r.stdout.strip()))

def ic(x,y):
    x=pd.Series(np.asarray(x,float)); y=pd.Series(np.asarray(y,float))
    m=(~x.isna())&(~y.isna())
    if m.sum()<40: return (np.nan,int(m.sum()))
    return (float(np.corrcoef(x[m].rank(),y[m].rank())[0,1]),int(m.sum()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    cache=os.path.join(WORKDIR,"data","_fa_horizon_raw.csv")
    if os.path.exists(cache):
        df=pd.read_csv(cache)
    else:
        df=bq_query(SQL); df.to_csv(cache,index=False)
    df["ew5"]=df[[f"score_{a}" for a in EW5]].mean(axis=1)
    df["state"]=df["state"].astype("Int64")
    # cap extreme returns (data errors / illiquid)
    for c,_ in HOR: df[c]=df[c].clip(-0.95,5.0)

    P("# FA edge by HORIZON × market state (DT5G)")
    P("")
    P(f"rows {len(df):,} | {df['time'].min()}→{df['time'].max()}")
    for c,nm in HOR:
        P(f"  {nm}: {df[c].notna().sum():,} with fwd return", )
    P("")

    # ── (A) IC by horizon: does FA edge rise with holding time? ───────────
    P("## (A) FA composite IC by horizon (overall) — does edge rise with time held?")
    P(f"{'factor':<14}"+"".join(f"{nm:>9}" for _,nm in HOR))
    P("-"*50)
    for fac,lab in [("total_score","total(7ax)"),("ew5","EW5(5ax)"),("score_quality","quality")]:
        row=f"{lab:<14}"
        for c,_ in HOR:
            rho,n=ic(df[fac],df[c]); row+=f"{rho:>+9.4f}" if not np.isnan(rho) else f"{'·':>9}"
        P(row)
    P("")
    P("Hypothesis ✓ if IC increases left→right (FA predicts long horizon better than short).")
    P("")

    # ── (B1) IC by state × horizon (total_score): ranking power per regime ─
    P("## (B1) RANKING — total_score IC by DT5G state × horizon")
    P("(can FA still rank winners inside each regime?)")
    P(f"{'state':<10}"+"".join(f"{nm:>9}" for _,nm in HOR)+f"{'N':>8}")
    P("-"*60)
    for s in [1,2,3,4,5]:
        g=df[df["state"]==s]
        if len(g)<60: continue
        row=f"{STATE[s]:<10}"
        for c,_ in HOR:
            rho,_=ic(g[fac if False else 'total_score'],g[c]); row+=f"{rho:>+9.4f}" if not np.isnan(rho) else f"{'·':>9}"
        P(row+f"{len(g):>8,}")
    P("")

    # ── (B2) ABSOLUTE — top vs bottom tier forward return by state ─────────
    P("## (B2) ABSOLUTE — does the BEST FA make money, or just fall less?")
    P("median forward return: TOP quintile (best FA) vs BOTTOM quintile, by state")
    for c,nm in HOR:
        sub=df.dropna(subset=[c]).copy()
        if len(sub)<200: continue
        sub["qt"]=sub.groupby("state")["total_score"].transform(
            lambda x: pd.qcut(x.rank(method="first"),5,labels=False) if x.notna().sum()>=10 else np.nan)
        P(f"\n### Horizon {nm}")
        P(f"{'state':<10}{'TOP med':>9}{'BOT med':>9}{'spread':>9}{'TOP win%':>9}{'N':>7}")
        for s in [1,2,3,4,5]:
            g=sub[sub["state"]==s]
            if len(g)<60: continue
            top=g[g["qt"]==4][c]; bot=g[g["qt"]==0][c]
            if len(top)<10 or len(bot)<10: continue
            P(f"{STATE[s]:<10}{top.median()*100:>+8.1f}%{bot.median()*100:>+8.1f}%"
              f"{(top.median()-bot.median())*100:>+8.1f}%{(top>0).mean()*100:>8.0f}%{len(g):>7,}")
    P("")
    P("Read: spread>0 = FA ranks correctly in that regime (resilience). TOP med<0 with")
    P("TOP win%<50 = even best FA loses money → 'FA can't save you' regime (crisis).")
    P("")
    with open(os.path.join(WORKDIR,"data","fa_horizon_state_ic.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_horizon_state_ic.md")

if __name__=="__main__":
    main()
