#!/usr/bin/env python3
"""
cash_machine_screen.py — "cash machine" quality gate (user insight 2026-05-31)
=============================================================================
User picked VCS(2015)/DGC(2016) early via a trait my frameworks underweighted:
  (1) CFO (cash from operations) > Net Profit, SUSTAINED many consecutive quarters
      → real cash generator, not paper profit / cash sink.  Measure on TTM (4Q) basis
      because single-quarter CFO is noisy (working-capital timing).
  (2) Does NOT raise capital from shareholders (no dilutive equity raises) — only
      dividends / bonus shares. Proxy: shares grow little, OR grow while CASH also
      grows (= bonus shares from retained earnings, not a cash raise).
These define a rare, self-funding compounder — a GATE, not a blended axis.

CASH_MACHINE flag = TTM_CFO/NP ≥ 1 in ≥60% of recent periods AND median TTM ratio ≥ 1
  AND cash balance growing/stable AND not heavily-diluting-while-draining-cash.
Validates on VCS/DGC (should flag pre-multibagger) + screens current quality universe.
Output: data/cash_machine_screen.md + .csv
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
    try: r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=1000000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

# quality universe + always include VCS/DGC for validation
fa=pd.read_csv(os.path.join(WORKDIR,"fa_ratings_lh.csv")).sort_values(["ticker","quarter"])
fa["is_ab"]=fa["tier"].isin(["A","B"]).astype(int); fa["qn"]=fa.groupby("ticker").cumcount()+1
fa["pct_AB"]=fa.groupby("ticker")["is_ab"].cumsum()/fa["qn"]*100
last=fa.groupby("ticker").tail(1)
univ=sorted(set(last[(last["pct_AB"]>=70)&(last["qn"]>=12)&(last["tier"].isin(["A","B"]))]["ticker"]) | {"VCS","DGC"})
tks="','".join(univ)

df=bq(f"""SELECT t.ticker,t.quarter,t.time,t.NP_P0,t.CF_OA_P0,t.Cash_P0,t.OShares,t.totalAsset_P0,t.ROIC5Y
FROM tav2_bq.ticker_financial t WHERE t.ticker IN ('{tks}') AND t.time>='2012-01-01' ORDER BY t.ticker,t.time""")
df["time"]=pd.to_datetime(df["time"])

def analyze(g, asof=None):
    g=g.sort_values("time")
    if asof is not None: g=g[g["time"]<=asof]
    if len(g)<8: return None
    g=g.copy()
    g["ttm_np"]=g["NP_P0"].rolling(4).sum(); g["ttm_cfo"]=g["CF_OA_P0"].rolling(4).sum()
    g["ttm_ratio"]=np.where(g["ttm_np"]>0, g["ttm_cfo"]/g["ttm_np"], np.nan)
    rec=g.dropna(subset=["ttm_ratio"]).tail(8)   # last ~8 TTM periods (~2-3y)
    if len(rec)<4: return None
    pct_ge1=(rec["ttm_ratio"]>=1).mean(); med=rec["ttm_ratio"].median()
    # cash trend over same window
    cash=rec.merge(g[["time","Cash_P0","OShares"]],on="time",how="left") if "Cash_P0" not in rec else rec
    c=rec["Cash_P0"].values; cash_grow=(c[-1]>c[0]) if len(c)>=2 and pd.notna(c[0]) and c[0]!=0 else False
    osh=rec["OShares"].values; dilut=(osh[-1]/osh[0]-1) if len(osh)>=2 and pd.notna(osh[0]) and osh[0]>0 else np.nan
    # heavy dilution while cash NOT growing = likely cash-raise (bad)
    bad_raise=(pd.notna(dilut) and dilut>0.5 and not cash_grow)
    machine=(pct_ge1>=0.6) and (med>=1.0) and cash_grow and (not bad_raise)
    # reinvestment runway: total-asset CAGR over ~4y (16q) + ROIC
    ta=g.dropna(subset=["totalAsset_P0"]); ta=ta[ta["totalAsset_P0"]>0]
    asset_cagr=np.nan
    if len(ta)>=12:
        a0=ta["totalAsset_P0"].iloc[max(0,len(ta)-17)]; a1=ta["totalAsset_P0"].iloc[-1]; n=min(16,len(ta)-1)
        if a0>0: asset_cagr=(a1/a0)**(4/n)-1
    roic=g["ROIC5Y"].dropna().iloc[-1]*100 if g["ROIC5Y"].notna().any() else np.nan
    runway=(pd.notna(asset_cagr) and asset_cagr>0.03)
    roic_ok=(pd.notna(roic) and roic>=12)
    # ENGINE classification (multibagger needs cash + runway + high ROIC)
    if roic_ok and runway: engine="COMPOUNDER"
    elif machine and not runway: engine="YIELD"          # QTP: cash-cow, no growth
    elif runway and not roic_ok: engine="LOWROIC_GROWTH"  # CVT: grows but destroys value
    elif machine: engine="CASH_COW"
    else: engine="-"
    return {"pct_ttm_ge1":pct_ge1,"med_ttm":med,"cash_grow":cash_grow,"dilut_3y":dilut,"machine":machine,
            "asset_cagr":asset_cagr,"roic5y":roic,"engine":engine,
            "cash_now":c[-1] if len(c) else np.nan,"cash_start":c[0] if len(c) else np.nan}

# ---- validate VCS/DGC as-of their pre-run dates ----
lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Cash-machine screen — CFO>NP (TTM) sustained + cash-accumulating + non-dilutive")
P("")
P("## Validation: VCS / DGC as-of pre-multibagger date")
for tk,asof in [("VCS","2015-12-31"),("DGC","2016-09-30")]:
    r=analyze(df[df["ticker"]==tk], pd.Timestamp(asof))
    if r: P(f"  {tk} @ {asof}: TTM_CFO/NP med={r['med_ttm']:.2f}, %periods≥1={r['pct_ttm_ge1']*100:.0f}%, cash {r['cash_start']/1e9:.0f}→{r['cash_now']/1e9:.0f}bn(grow={r['cash_grow']}), dilut3y={r['dilut_3y']*100:+.0f}% → CASH_MACHINE={r['machine']}")
P("")

# ---- current screen ----
rows=[]
for tk,g in df.groupby("ticker"):
    r=analyze(g)
    if r: r["ticker"]=tk; rows.append(r)
res=pd.DataFrame(rows).sort_values(["machine","med_ttm"],ascending=[False,False])
mach=res[res["machine"]]
P(f"## Current CASH MACHINES ({len(mach)} of {len(res)} quality names)")
P(f"{'tkr':<6}{'TTM_CFO/NP':>11}{'%≥1':>6}{'cashGrow':>9}{'dilut3y':>9}{'cash_now(bn)':>13}")
P("-"*56)
for _,r in mach.iterrows():
    P(f"{r['ticker']:<6}{r['med_ttm']:>11.2f}{r['pct_ttm_ge1']*100:>5.0f}%{str(r['cash_grow']):>9}{(r['dilut_3y']*100 if pd.notna(r['dilut_3y']) else float('nan')):>+8.0f}%{r['cash_now']/1e9:>13.0f}")
P("")
P("CASH MACHINES: "+", ".join(mach["ticker"].tolist()))
P("")
P("NOT cash-machine but close (med TTM≥0.9): "+", ".join(res[(~res['machine'])&(res['med_ttm']>=0.9)]['ticker'].tolist()[:15]))
P("")
P("Logic: gate not ranker (rare/precious quality). TTM (4Q) smooths working-capital noise.")
P("Caveat: dilut3y can't fully separate bonus-shares vs cash-raise — cross-checked w/ cash growing.")
P("")
P("## ENGINE classification (multibagger = cash-machine + runway + high ROIC)")
for eng in ["COMPOUNDER","CASH_COW","YIELD","LOWROIC_GROWTH"]:
    g=res[res["engine"]==eng]
    if len(g): P(f"  {eng:<16}: "+", ".join(g.sort_values('roic5y',ascending=False)['ticker'].tolist()))
P("")
P(f"{'tkr':<6}{'engine':<16}{'CFO/NP':>7}{'assetCAGR':>10}{'ROIC5Y':>8}{'cashMach':>9}")
for _,r in res.sort_values(["engine","roic5y"],ascending=[True,False]).iterrows():
    P(f"{r['ticker']:<6}{r['engine']:<16}{r['med_ttm']:>7.2f}{(r['asset_cagr']*100 if pd.notna(r['asset_cagr']) else float('nan')):>+9.0f}%{(r['roic5y'] if pd.notna(r['roic5y']) else float('nan')):>7.0f}%{str(r['machine']):>9}")
res[["ticker","engine","machine","med_ttm","asset_cagr","roic5y","dilut_3y","cash_grow"]].to_csv(os.path.join(WORKDIR,"data","engine_class.csv"),index=False)
res.to_csv(os.path.join(WORKDIR,"data","cash_machine_screen.csv"),index=False)
with open(os.path.join(WORKDIR,"data","cash_machine_screen.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/cash_machine_screen.{md,csv}")
