#!/usr/bin/env python3
"""
qt_v4_valuation_lens.py — multi-lens "cheap" screen for the QT v4 quality universe
==================================================================================
Lesson from GAS (dd-only fired cheap but wasn't) and FPT (pe_z stopped firing but
still cheap — benchmark moved, not price): NO single cheap-metric is reliable.
Triangulate 3 lenses + a value-trap guard:
  hist_cheap : pe_z<-1 OR pb_z<-1            (cheap vs own 5Y history; fragile to benchmark revisions)
  peg_cheap  : 0<PEG<=1                       (cheap vs growth; best for GROWTH names; PEG=PE/NPgrowth%)
  abs_cheap  : PE<10 OR PB<1.2                (cheap on absolute level)
  value_trap : NP_yoy<-15%                    (cheap because earnings collapsing → "cheap for a reason")
Classify: GENUINE CHEAP (≥2 lenses, not trap) / CHEAP-1-lens / VALUE TRAP / NOT CHEAP.
Quality universe = fa_ratings_lh pct_AB≥70, ≥12Q, latest A/B. Valuation = BQ latest date.
Output: data/qt_v4_valuation_lens.md + .csv
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
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# quality universe from fa_ratings_lh
fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv"),parse_dates=["time"]).sort_values(["ticker","quarter"])
fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int); fa["qnum"]=fa.groupby("ticker").cumcount()+1
fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qnum"]*100
last=fa.groupby("ticker").tail(1)
univ=last[(last["pct_AB"]>=70)&(last["qnum"]>=12)&(last["tier"].isin(["A","B"]))]["ticker"].tolist()
tks="','".join(univ)

# latest valuation snapshot from BQ
df=bq(f"""WITH latest AS (SELECT t.ticker, MAX(t.time) mx FROM tav2_bq.ticker t WHERE t.ticker IN ('{tks}') AND t.PE IS NOT NULL GROUP BY t.ticker),
hi AS (SELECT t.ticker, MAX(t.Close) hi52 FROM tav2_bq.ticker t WHERE t.ticker IN ('{tks}') AND t.time>=DATE_SUB(DATE '2026-05-29',INTERVAL 365 DAY) GROUP BY t.ticker)
SELECT t.ticker, ROUND(t.PE,1) PE, ROUND((t.PE-t.PE_MA5Y)/NULLIF(t.PE_SD5Y,0),2) pe_z,
  ROUND(t.PB,2) PB, ROUND((t.PB-t.PB_MA5Y)/NULLIF(t.PB_SD5Y,0),2) pb_z,
  ROUND(SAFE_DIVIDE(t.NP_P0,t.NP_P4)-1,3) np_yoy,
  ROUND(t.ROE5Y*100,1) ROE5Y, ROUND(t.Close/NULLIF(hi.hi52,0)-1,2) dd52, t.ICB_Code
FROM tav2_bq.ticker t JOIN latest l ON l.ticker=t.ticker AND l.mx=t.time JOIN hi ON hi.ticker=t.ticker""")

# PEG recompute (robust): PE / (np_yoy*100), only if np_yoy>0 and PE>0
df["growth_pct"]=df["np_yoy"]*100
df["PEG"]=np.where((df["growth_pct"]>0)&(df["PE"]>0), df["PE"]/df["growth_pct"], np.nan)
# lenses
df["hist_cheap"]=(df["pe_z"]<-1)|(df["pb_z"]<-1)
df["peg_cheap"]=(df["PEG"]>0)&(df["PEG"]<=1.0)
df["abs_cheap"]=(df["PE"]<10)|(df["PB"]<1.2)
df["value_trap"]=df["np_yoy"]<-0.15
df["n_lens"]=df[["hist_cheap","peg_cheap","abs_cheap"]].sum(axis=1)
def cls(r):
    if r["value_trap"] and (r["hist_cheap"] or r["abs_cheap"]): return "VALUE_TRAP"
    if r["n_lens"]>=2: return "CHEAP(multi)"
    if r["n_lens"]==1: return "CHEAP(1-lens)"
    return "NOT_CHEAP"
df["verdict"]=df.apply(cls,axis=1)
order={"CHEAP(multi)":0,"CHEAP(1-lens)":1,"VALUE_TRAP":2,"NOT_CHEAP":3}
df["ord"]=df["verdict"].map(order)
df=df.sort_values(["ord","ROE5Y"],ascending=[True,False])

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# QT v4 quality universe — multi-lens valuation screen (latest ~2026-05-29)")
P("lenses: hist=pe_z/pb_z<-1 | peg=0<PE/growth<=1 | abs=PE<10|PB<1.2 | trap=NP_yoy<-15%")
P("")
P(f"{'tkr':<6}{'PE':>6}{'pe_z':>6}{'pb_z':>6}{'PEG':>6}{'NPyoy':>7}{'ROE5Y':>7}{'dd52':>6}  {'lens(h/p/a)':<12}{'VERDICT'}")
P("-"*86)
for _,r in df.iterrows():
    fl=f"{int(r['hist_cheap'])}/{int(r['peg_cheap'])}/{int(r['abs_cheap'])}"
    peg=f"{r['PEG']:.2f}" if pd.notna(r['PEG']) else "  -"
    P(f"{r['ticker']:<6}{r['PE']:>6.1f}{r['pe_z']:>6.2f}{r['pb_z']:>6.2f}{peg:>6}{r['np_yoy']*100:>+6.0f}%{r['ROE5Y']:>6.1f}%{r['dd52']*100:>+5.0f}%  {fl:<12}{r['verdict']}")
P("")
for v in ["CHEAP(multi)","CHEAP(1-lens)","VALUE_TRAP","NOT_CHEAP"]:
    g=df[df["verdict"]==v]
    P(f"{v}: {', '.join(g['ticker'].tolist())}")
df.to_csv(os.path.join(WORKDIR,"data","qt_v4_valuation_lens.csv"),index=False)
with open(os.path.join(WORKDIR,"data","qt_v4_valuation_lens.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("\nSaved data/qt_v4_valuation_lens.{md,csv}")
