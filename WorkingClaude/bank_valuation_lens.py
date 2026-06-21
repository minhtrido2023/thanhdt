#!/usr/bin/env python3
"""
bank_valuation_lens.py — bank-specific valuation screen (ICB 8355)
==================================================================
Banks need their own model: earnings are leveraged off book equity, so P/E and
generic PEG mislead. The right cheapness gauge is P/B RELATIVE TO ROE
(justified-P/B logic: a bank earning higher sustainable ROE deserves higher P/B;
it's cheap if P/B is low for its ROE). Key metrics:
  ROE_Trailing / ROE5Y / ROE_Min5Y  (profitability + through-cycle floor = asset-quality proxy)
  PB, pb_z (cheap vs own 5Y history)
  ROE/PB                            (earnings yield on book — higher = cheaper-for-quality)
  PB-vs-ROE residual (cross-section): regress PB~ROE across banks; negative = cheap for its ROE
  NP_yoy                            (earnings growth ~ credit growth)
Classify CHEAP_BANK = (pb_z<-0.3 OR residual<0) AND ROE5Y decent AND not earnings-collapsing.
Face validity: MBB 2017 vs now (the +10x).
Output: data/bank_valuation_lens.md
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
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# latest snapshot for all banks (ICB 8355), liquid
df=bq("""WITH banks AS (SELECT DISTINCT t.ticker FROM tav2_bq.ticker t WHERE t.ICB_Code=8355),
latest AS (SELECT t.ticker, MAX(t.time) mx FROM tav2_bq.ticker t JOIN banks b USING(ticker) WHERE t.PB IS NOT NULL GROUP BY t.ticker)
SELECT t.ticker, ROUND(t.Close,0) Close, ROUND(t.PE,1) PE, ROUND(t.PB,2) PB,
  ROUND((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2) pb_z,
  ROUND(t.ROE5Y*100,1) ROE5Y, ROUND(t.ROE_Min5Y*100,1) ROEmin5,
  ROUND(SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1,3) np_yoy,
  ROUND(t.Volume_3M_P50*t.Close/1e9,1) liqB
FROM tav2_bq.ticker t JOIN latest l ON l.ticker=t.ticker AND l.mx=t.time""")
df=df[df["liqB"]>=2].copy()   # liquidity filter
df["roe_pb"]=df["ROE5Y"]/df["PB"]            # earnings yield on book (higher=cheaper)
# cross-sectional PB~ROE residual (cheap-for-its-ROE)
d=df.dropna(subset=["PB","ROE5Y"])
b=np.polyfit(d["ROE5Y"],d["PB"],1)
df["pb_fit"]=b[0]*df["ROE5Y"]+b[1]
df["pb_resid"]=df["PB"]-df["pb_fit"]         # negative = cheaper than ROE justifies
df["cheap"]=((df["pb_z"]<-0.3)|(df["pb_resid"]<0)) & (df["ROE5Y"]>=14) & (df["np_yoy"]>-0.1)
df=df.sort_values("pb_resid")  # cheapest-for-ROE first

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Bank valuation lens (ICB 8355) — P/B-vs-ROE framework, latest snapshot")
P("cheap-for-quality = low pb_z (vs own history) OR negative PB-vs-ROE residual (cheap for its ROE)")
P(f"cross-section fit: PB ≈ {b[0]:.3f}·ROE5Y + {b[1]:.2f}")
P("")
P(f"{'tkr':<6}{'PB':>6}{'pb_z':>6}{'ROE5Y':>7}{'ROEmin':>7}{'ROE/PB':>7}{'PBresid':>8}{'NPyoy':>7}{'liqB':>6}  cheap?")
P("-"*72)
for _,r in df.iterrows():
    P(f"{r['ticker']:<6}{r['PB']:>6.2f}{r['pb_z']:>6.2f}{r['ROE5Y']:>6.1f}%{r['ROEmin5']:>6.1f}%{r['roe_pb']:>7.1f}{r['pb_resid']:>+8.2f}{r['np_yoy']*100:>+6.0f}%{r['liqB']:>6.0f}  {'YES' if r['cheap'] else ''}")
P("")
P(f"CHEAP banks (cheap-for-ROE + ROE≥14% + not collapsing): {', '.join(df[df['cheap']]['ticker'].tolist())}")
P("")
# MBB face validity 2017 vs now
P("## Face validity — MBB the +10x (2017 → now): bought cheap-PB + high ROE compounding")
mbb=bq("""SELECT t.time, ROUND(t.Close,0) Close, ROUND(t.PB,2) PB, ROUND(t.PE,1) PE, ROUND(t.ROE5Y*100,1) ROE5Y
FROM tav2_bq.ticker t WHERE t.ticker='MBB' AND t.time IN (DATE'2017-01-03',DATE'2019-01-02',DATE'2021-01-04',DATE'2023-01-03',DATE'2026-05-29') ORDER BY t.time""")
P(f"{'date':<12}{'Close':>8}{'PB':>6}{'PE':>6}{'ROE5Y':>7}")
for _,r in mbb.iterrows():
    P(f"{str(r['time']):<12}{r['Close']:>8.0f}{r['PB']:>6.2f}{r['PE']:>6.1f}{r['ROE5Y']:>6.1f}%")
if len(mbb)>=2:
    P(f"  → price {mbb['Close'].iloc[-1]/mbb['Close'].iloc[0]:.1f}x since 2017; PB then {mbb['PB'].iloc[0]} (cheap) → re-rate + ROE compounding")
P("")
P("Read: cheap bank = LOW P/B for its ROE (negative resid) + high stable ROE + credit growth.")
P("PE is secondary; PEG misleads (bank growth=balance-sheet, not the same as industrials).")
df.to_csv(os.path.join(WORKDIR,"data","bank_valuation_lens.csv"),index=False)
with open(os.path.join(WORKDIR,"data","bank_valuation_lens.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("\nSaved data/bank_valuation_lens.{md,csv}")
