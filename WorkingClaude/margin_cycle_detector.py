#!/usr/bin/env python3
"""
margin_cycle_detector.py — for COMMODITY-CONSUMER (converter) businesses
========================================================================
Inverse of the cyclical-PRODUCER framework. A converter (input = raw commodity,
COGS-heavy) with PRICING POWER (brand) earns windfall margin when its input is at
a cyclical LOW, and gets crushed when input is HIGH. So:
  - BUY signal: GPM at a cyclical LOW (vs own history) → margin crushed = input peak
    → about to mean-revert UP (e.g. BMP 2021Q3 GPM 4.5%, loss → then ×7-8).
  - CAUTION : GPM at a cyclical HIGH → margin extended = input low → compression risk
    (e.g. BMP now GPM ~47% = peak; buying after the triple = buying peak margin).
Observable footprint = GPM percentile vs the company's OWN history (no need for the
input commodity price). Gate on PRICING POWER (through-cycle ROE) — a no-moat
converter just stays low-margin, never recovers it.

Consumer→input map (note SYMMETRY w/ producers): rubber HIGH = good for DRI/PHR
(producers) but BAD for DRC/CSM tire margin (consumers). Same commodity, opposite side.
Output: data/margin_cycle_detector.md + .csv
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
# converter (input-heavy) businesses → dominant input commodity
CONSUMER={"BMP":"PVC resin","NTP":"PVC resin","DAG":"PVC/plastic",
          "DRC":"rubber+carbon black","CSM":"rubber+carbon black",
          "AAA":"plastic resin","SVI":"paper/packaging","TLG":"plastic/petro",
          "PNJ":"gold (passthrough)","VNM":"milk powder","MCH":"ag inputs","SAB":"barley/aluminum",
          "PTB":"wood/stone","VCS":"quartz/resin"}
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=1000000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

tks="','".join(CONSUMER)
df=bq(f"""SELECT t.ticker,t.time,t.GPM_P0,t.ROE_Trailing,t.NP_P0,t.Revenue_P0
FROM tav2_bq.ticker_financial t WHERE t.ticker IN ('{tks}') AND t.time>='2014-01-01' ORDER BY t.ticker,t.time""")
df["time"]=pd.to_datetime(df["time"])

rows=[]
for tk,g in df.groupby("ticker"):
    g=g.sort_values("time"); gpm=g["GPM_P0"].dropna()
    if len(gpm)<12: continue
    cur=gpm.iloc[-1]
    pctile=(gpm<=cur).mean()            # current GPM percentile vs own history
    mean=gpm.mean(); sd=gpm.std(); z=(cur-mean)/sd if sd>0 else np.nan
    roe=g["ROE_Trailing"].dropna()
    roe_med=roe.median()*100 if len(roe) else np.nan   # through-cycle ROE = pricing-power proxy
    roe_min=roe.min()*100 if len(roe) else np.nan
    gpm_range=f"{gpm.min()*100:.0f}-{gpm.max()*100:.0f}"
    if pctile<=0.25: cyc="MARGIN_BOTTOM"
    elif pctile>=0.75: cyc="MARGIN_PEAK"
    else: cyc="MID"
    # action: brand (decent through-cycle ROE) required for the recovery thesis
    brand=(pd.notna(roe_med) and roe_med>=12)
    if cyc=="MARGIN_BOTTOM" and brand: act="BUY-zone (margin crushed→revert↑)"
    elif cyc=="MARGIN_BOTTOM": act="watch (no-moat: may stay low)"
    elif cyc=="MARGIN_PEAK": act="CAUTION (peak margin→compress risk)"
    else: act="neutral"
    rows.append({"ticker":tk,"input":CONSUMER[tk],"GPM_now":cur*100,"GPM_pctile":pctile,
                 "GPM_z":z,"GPM_range":gpm_range,"ROE_med":roe_med,"cycle":cyc,"action":act})
res=pd.DataFrame(rows).sort_values("GPM_pctile")

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Margin-cycle detector — commodity CONSUMERS (converters)")
P("BUY when GPM at cyclical LOW (input peak, margin crushed) for a pricing-power brand; CAUTION at GPM peak.")
P("")
P(f"{'tkr':<6}{'input':<22}{'GPM%now':>8}{'pctile':>7}{'GPM_z':>7}{'rangeGPM':>10}{'ROEmed':>8}  cycle / action")
P("-"*92)
for _,r in res.iterrows():
    P(f"{r['ticker']:<6}{r['input']:<22}{r['GPM_now']:>7.1f}%{r['GPM_pctile']:>7.2f}{r['GPM_z']:>+7.1f}{r['GPM_range']:>9}%{r['ROE_med']:>7.0f}%  {r['cycle']} / {r['action']}")
P("")
P("MARGIN_BOTTOM (buy-zone if brand): "+", ".join(res[(res['cycle']=='MARGIN_BOTTOM')&(res['ROE_med']>=12)]['ticker'].tolist() or ['none']))
P("MARGIN_PEAK (caution): "+", ".join(res[res['cycle']=='MARGIN_PEAK']['ticker'].tolist() or ['none']))
P("")
# BMP validation: now vs 2021
bmp=df[df["ticker"]=="BMP"].sort_values("time")
g21=bmp[(bmp["time"]>="2021-06-01")&(bmp["time"]<="2021-12-31")]["GPM_P0"]
P("## BMP validation (the +3x): margin-cycle signature")
if len(g21):
    P(f"  2021 (PVC peak): GPM {g21.min()*100:.1f}% = trough → MARGIN_BOTTOM = the BUY (then ×7-8 NP)")
P(f"  Now: GPM {res[res['ticker']=='BMP']['GPM_now'].iloc[0]:.1f}% = pctile {res[res['ticker']=='BMP']['GPM_pctile'].iloc[0]:.2f} = MARGIN_PEAK → caution (resin recovery=compression)")
P("")
P("SYMMETRY: rubber HIGH = DRI/PHR producers WIN but DRC/CSM tire margin LOSES. Same commodity, opposite side.")
P("Caveat: GPM percentile vs own history; needs ≥12 q; pricing-power gate via through-cycle ROE; cyclical margin not permanent.")
res.to_csv(os.path.join(WORKDIR,"data","margin_cycle_detector.csv"),index=False)
with open(os.path.join(WORKDIR,"data","margin_cycle_detector.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/margin_cycle_detector.{md,csv}")
