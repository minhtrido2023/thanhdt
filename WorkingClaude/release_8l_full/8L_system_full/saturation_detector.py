#!/usr/bin/env python3
"""
saturation_detector.py — growth RUNWAY / TAM classifier (user insight 2026-05-31)
=================================================================================
Deepest runway determinant = TAM. Export/global-TAM → durable runway (DGC/VCS);
domestic = S-CURVE: explosive during market-capture, then SATURATES & slows
(MWG smartphones 2014-19, VNM 2007-15, FRT/Long Châu pharma 2022-now); domestic-
structural (HPG, developing-country infra) = long runway b/c country grows.

Detect via revenue-growth TRAJECTORY (TTM revenue; CAGR recent-3y vs prior-3y; the
2nd derivative = accel). Classify:
  DURABLE     : recent CAGR ≥15% AND not decelerating (accel ≥ −5pp)  → runway open
  CAPTURING   : recent CAGR ≥20% (fast, market-capture phase)
  SATURATING  : prior CAGR was ≥15% BUT decelerated hard (accel ≤ −10pp) → S-curve topping
  MATURE/FLAT : both CAGRs <8%  → already saturated / no growth
  MODERATE    : else
+ EXPORT tag (manual, known global exporters) — export+durable = best long runway.
Validates on VNM/MWG/FRT/DGC/VCS/HPG. Output: data/saturation_detector.md + .csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd
PROJECT="lithe-record-440915-m9"; BQ_BIN=r"bq"
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
# known global exporters / large-TAM (manual; BQ has no export%)
EXPORT={"DGC","VCS","FMC","VHC","ANV","MPC","TNG","MSH","STK","TCM","PTB","GIL","FPT","IDI","CMX"}
STRUCTURAL={"HPG","HSG","NKG"}  # domestic but country-growth-driven (infra)
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=2000000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# quality universe + validation examples
fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv")).sort_values(["ticker","quarter"])
fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int); fa["qn"]=fa.groupby("ticker").cumcount()+1
fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qn"]*100
last=fa.groupby("ticker").tail(1)
univ=sorted(set(last[(last["pct_AB"]>=70)&(last["qn"]>=12)&(last["tier"].isin(["A","B"]))]["ticker"]) | {"VNM","MWG","FRT","MSN","DGC","VCS","HPG","PNJ"})
tks="','".join(univ)
df=bq(f"""SELECT t.ticker,t.time,t.Revenue_P0 FROM tav2_bq.ticker_financial t
WHERE t.ticker IN ('{tks}') AND t.time>='2009-01-01' ORDER BY t.ticker,t.time""")
df["time"]=pd.to_datetime(df["time"])

def cagr(a,b,yrs):
    return (a/b)**(1/yrs)-1 if (pd.notna(a) and pd.notna(b) and b>0 and a>0) else np.nan
rows=[]
for tk,g in df.groupby("ticker"):
    g=g.sort_values("time"); rev=g["Revenue_P0"]
    ttm=rev.rolling(4).sum().dropna()
    if len(ttm)<28: continue   # need ~7y
    now=ttm.iloc[-1]; r3=ttm.iloc[-13] if len(ttm)>=13 else np.nan; r6=ttm.iloc[-25] if len(ttm)>=25 else np.nan
    cg_recent=cagr(now,r3,3); cg_prior=cagr(r3,r6,3)
    accel=(cg_recent-cg_prior) if (pd.notna(cg_recent) and pd.notna(cg_prior)) else np.nan
    # classify
    if pd.isna(cg_recent): cls="?"
    elif cg_recent>=0.20: cls="CAPTURING"
    elif cg_recent>=0.15 and (pd.isna(accel) or accel>=-0.05): cls="DURABLE"
    elif pd.notna(cg_prior) and cg_prior>=0.15 and pd.notna(accel) and accel<=-0.10: cls="SATURATING"
    elif cg_recent<0.08 and (pd.isna(cg_prior) or cg_prior<0.08): cls="MATURE/FLAT"
    else: cls="MODERATE"
    tag="EXPORT" if tk in EXPORT else ("STRUCTURAL" if tk in STRUCTURAL else "DOMESTIC")
    rows.append({"ticker":tk,"tag":tag,"cagr_recent3y":cg_recent,"cagr_prior3y":cg_prior,"accel_pp":accel,"runway":cls})
res=pd.DataFrame(rows)
order={"DURABLE":0,"CAPTURING":1,"MODERATE":2,"SATURATING":3,"MATURE/FLAT":4,"?":5}
res["o"]=res["runway"].map(order); res=res.sort_values(["o","tag"])

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Growth RUNWAY / TAM detector — revenue-trajectory (2nd-derivative) + export tag")
P("DURABLE/CAPTURING=runway open | SATURATING=S-curve topping (domestic captured) | MATURE=saturated")
P("")
# validation
P("## Validation (examples)")
for tk in ["VNM","MWG","FRT","DGC","VCS","HPG","MSN","PNJ"]:
    r=res[res["ticker"]==tk]
    if len(r): rr=r.iloc[0]; P(f"  {tk:<5} [{rr['tag']:<10}] recent3y CAGR {(rr['cagr_recent3y']*100 if pd.notna(rr['cagr_recent3y']) else float('nan')):+.0f}% vs prior {(rr['cagr_prior3y']*100 if pd.notna(rr['cagr_prior3y']) else float('nan')):+.0f}% (accel {(rr['accel_pp']*100 if pd.notna(rr['accel_pp']) else float('nan')):+.0f}pp) → {rr['runway']}")
P("")
P(f"{'tkr':<6}{'tag':<11}{'recent3y':>9}{'prior3y':>9}{'accel':>7}  runway")
P("-"*52)
for _,r in res.iterrows():
    P(f"{r['ticker']:<6}{r['tag']:<11}{(r['cagr_recent3y']*100 if pd.notna(r['cagr_recent3y']) else float('nan')):>+8.0f}%{(r['cagr_prior3y']*100 if pd.notna(r['cagr_prior3y']) else float('nan')):>+8.0f}%{(r['accel_pp']*100 if pd.notna(r['accel_pp']) else float('nan')):>+6.0f}  {r['runway']}")
P("")
P("RUNWAY OPEN (DURABLE/CAPTURING): "+", ".join(res[res['runway'].isin(['DURABLE','CAPTURING'])]['ticker'].tolist()))
P("  └ of which EXPORT (best TAM): "+", ".join(res[(res['runway'].isin(['DURABLE','CAPTURING']))&(res['tag']=='EXPORT')]['ticker'].tolist() or ['none']))
P("SATURATING (S-curve topping): "+", ".join(res[res['runway']=='SATURATING']['ticker'].tolist() or ['none']))
P("MATURE/FLAT: "+", ".join(res[res['runway']=='MATURE/FLAT']['ticker'].tolist() or ['none']))
P("")
P("Caveat: revenue-trajectory only (cyclical/event dips muddy recent CAGR, e.g. DGC/VCS event); EXPORT tag manual (BQ no export%); STRUCTURAL=domestic+country-growth (HPG).")
res.drop(columns=["o"]).to_csv(os.path.join(WORKDIR,"data","saturation_detector.csv"),index=False)
with open(os.path.join(WORKDIR,"data","saturation_detector.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/saturation_detector.{md,csv}")
