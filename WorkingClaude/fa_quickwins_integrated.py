#!/usr/bin/env python3
"""
fa_quickwins_integrated.py — integrated test of the 2 FA quick wins
===================================================================
Same harness/altitude as fa_bank_integrated.py (v11 BA-core classify, realized
profit_3M), now testing:
  EW5     : drop health+valuation axes → recompute composite → re-tier A/B/C/D/E
  RF      : redflag_cnt≥3 exclusion overlay on the BASELINE 7-axis tiers
            (Beneish-lite blow-up screen → force AVOID)

CRITICAL given today's bank-model reversal: the BA-core book uses FA INVERTED
(needs C/D for MEGA/MOMENTUM). EW5 re-tiers everyone, so it can shuffle names
across the C/D gate just like the bank model did — must integrated-test, not
trust IC. RF only EXCLUDES, so its risk is removing winners.

Baseline = 7-axis tier from fundamental_rating_all.csv (as-of joined to daily).
Uses cached daily rows from fa_bank_integrated.py (data/_fa_bank_integrated_raw.csv).
Vectorized classifier (np.select) — runs in seconds.
Output: data/fa_quickwins_integrated.md
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
TIERS=[("A",.90,1.01),("B",.70,.90),("C",.40,.70),("D",.15,.40),("E",-.01,.15)]
BA_CORE={"MEGA","MOMENTUM","MOMENTUM_N","MOMENTUM_S","DEEP_VALUE_RECOVERY"}

RF_SQL="""
SELECT f.ticker, f.quarter, f.time,
  f.DSO_P0,f.DSO_P4,f.DIO_P0,f.DIO_P4,f.GPM_P0,f.GPM_P4,f.Debt_Eq_P0,f.Debt_Eq_P4
FROM tav2_bq.ticker_financial AS f WHERE f.time>="2013-06-01"
"""

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
             f'--format=csv --max_rows=3000000 < "{tmp}"')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0: raise RuntimeError((r.stdout or r.stderr)[:800])
    return pd.read_csv(StringIO(r.stdout.strip()))

def tier_of(p):
    for nm,lo,hi in TIERS:
        if lo<=p<=hi: return nm
    return "E"

def classify_vec(df, tcol, ta):
    """Vectorized port of recommend_holistic.classify_play_type (v11)."""
    t=df[tcol].values; s=df["state5"].values; pe=df["pe_z"].values
    npy=df["np_yoy"].values; rev=df["rev_yoy"].values; warn=df["warn_ext"].astype(bool).values
    isCD=np.isin(t,["C","D"]); isAB=np.isin(t,["A","B"])
    s45=np.isin(s,[4,5]); s3=(s==3); s345=np.isin(s,[3,4,5])
    bear=pd.isna(df["state5"]).values | np.isin(s,[1,2])
    conds=[
        bear,
        t=="E",
        (ta>=170)&s45&isCD,
        (ta>=170)&s45,
        (ta>=155)&s45&isCD,
        (ta>=155)&s45&isAB,
        (ta>=155)&s3&isCD,
        isAB&(pe<-0.5)&(ta>=95)&s345&(~warn),
        (t=="C")&(ta>=100)&s45&(((npy>0.20)&~pd.isna(npy))|((rev>0.20)&~pd.isna(rev))),
        (ta>=140)&s45,
        (ta>=125)&s45,
        (ta>=140)&s3,
        isAB&(ta>=70)&(ta<130),
        isAB,
    ]
    labels=["AVOID_bear","AVOID_faE","MEGA","S_PRO","MOMENTUM","MOMENTUM_QUALITY",
            "MOMENTUM_N","COMPOUNDER_BUY","DEEP_VALUE_RECOVERY","MOMENTUM_S",
            "MOMENTUM_A","MOMENTUM_S_N","COMPOUNDER_HOLD","WAIT"]
    return np.select(conds, labels, default="PASS")

def ta_sector8(ta_base, sector, tier):
    out=ta_base.copy().astype(float)
    out[(sector==8)&(tier=="D")]+=10
    out[(sector==8)&(tier=="A")]-=10
    return out

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    df=pd.read_csv(os.path.join(WORKDIR,"data","_fa_bank_integrated_raw.csv"))
    df["time"]=pd.to_datetime(df["time"]); df=df.sort_values("time").reset_index(drop=True)

    # ── build BASE (7-axis) + EW5 tiers from CSV, as-of join ──────────────
    fa=pd.read_csv(os.path.join(WORKDIR,"data/fundamental_rating_all.csv"))
    fa["time"]=pd.to_datetime(fa["time"])
    fa["ew5"]=fa[[f"score_{a}" for a in EW5]].mean(axis=1)
    fa["ew5_pct"]=fa.groupby("quarter")["ew5"].rank(pct=True)
    fa["ew5_tier"]=fa["ew5_pct"].apply(tier_of)
    rt=fa[["ticker","time","tier","ew5_tier"]].rename(columns={"tier":"base_tier"}).sort_values("time")
    df=pd.merge_asof(df, rt, on="time", by="ticker", direction="backward")

    # ── redflag_cnt, as-of join ───────────────────────────────────────────
    rf=bq_query(RF_SQL); rf["time"]=pd.to_datetime(rf["time"])
    dsi=rf["DSO_P0"]/rf["DSO_P4"]; dii=rf["DIO_P0"]/rf["DIO_P4"]
    rf["redflag_cnt"]=((dsi>1.30).astype(int)+(dii>1.30).astype(int)
                       +(rf["GPM_P0"]<rf["GPM_P4"]).astype(int)
                       +(rf["Debt_Eq_P0"]>rf["Debt_Eq_P4"]*1.10).astype(int))
    rf=rf[["ticker","time","redflag_cnt"]].sort_values("time")
    df=pd.merge_asof(df, rf, on="time", by="ticker", direction="backward")

    P("# Integrated test: 2 FA quick wins (v11 BA-core, realized profit_3M)")
    P("")
    P(f"daily rows {len(df):,} | base_tier cover {df['base_tier'].notna().mean()*100:.0f}% "
      f"| ew5 cover {df['ew5_tier'].notna().mean()*100:.0f}% | redflag cover {df['redflag_cnt'].notna().mean()*100:.0f}%")
    P("")

    # ── classify scenarios ────────────────────────────────────────────────
    df["base_tier"]=df["base_tier"].fillna(df["fa_generic"])  # fallback
    ta_base=ta_sector8(df["ta_base"].values, df["sector"].values, df["base_tier"].values)
    ta_ew5 =ta_sector8(df["ta_base"].values, df["sector"].values, df["ew5_tier"].fillna(df["base_tier"]).values)
    df["play_base"]=classify_vec(df,"base_tier",ta_base)
    df["ew5_t"]=df["ew5_tier"].fillna(df["base_tier"])
    df["play_ew5"]=classify_vec(df,"ew5_t",ta_base*0+ta_ew5)
    # RF overlay on base: force AVOID where redflag_cnt>=3
    df["play_rf"]=np.where(df["redflag_cnt"].fillna(0)>=3, "AVOID_redflag", df["play_base"])

    def stats(mask,label):
        g=df[mask]; n=len(g)
        if n==0: return f"{label:<26}{0:>8}"
        return (f"{label:<26}{n:>8,}{g['p3m'].mean():>9.2f}%{g['p3m'].median():>9.2f}%"
                f"{(g['p3m']>0).mean()*100:>8.1f}%{((1+g['p3m'].mean()/100)**4-1)*100:>10.1f}%")

    P("## FULL BA-core book — annualized = 4 compounded 3M trades")
    P(f"{'scenario':<26}{'N':>8}{'mean':>9}{'median':>9}{'win%':>8}{'annualiz':>10}")
    P("-"*70)
    P(stats(df["play_base"].isin(BA_CORE),"BASELINE 7-axis"))
    P(stats(df["play_ew5"].isin(BA_CORE),"EW5 (drop health+val)"))
    P(stats(df["play_rf"].isin(BA_CORE),"BASE + redflag≥3 excl"))
    P("")
    # OOS
    oos=df["time"]>="2020-01-01"
    P("## FULL BA-core book — OOS 2020+")
    P(f"{'scenario':<26}{'N':>8}{'mean':>9}{'median':>9}{'win%':>8}{'annualiz':>10}")
    P("-"*70)
    P(stats((df["play_base"].isin(BA_CORE))&oos,"BASELINE 7-axis"))
    P(stats((df["play_ew5"].isin(BA_CORE))&oos,"EW5"))
    P(stats((df["play_rf"].isin(BA_CORE))&oos,"BASE + redflag≥3 excl"))
    P("")

    # ── EW5 composition change ────────────────────────────────────────────
    cb=df["play_base"].isin(BA_CORE); ce=df["play_ew5"].isin(BA_CORE)
    P("## EW5 composition change (baseline → EW5)")
    P(f"{'group':<24}{'N':>8}{'mean p3m':>11}{'win%':>8}")
    P("-"*51)
    for nm,m in [("ADDED by EW5",~cb&ce),("REMOVED by EW5",cb&~ce),("kept",cb&ce)]:
        g=df[m]
        P(f"{nm:<24}{len(g):>8,}{(g['p3m'].mean() if len(g) else float('nan')):>10.2f}%"
          f"{((g['p3m']>0).mean()*100 if len(g) else float('nan')):>7.1f}%")
    P("")
    # ── redflag exclusion: what got removed ───────────────────────────────
    excl=cb & (df["redflag_cnt"].fillna(0)>=3)
    g=df[excl]
    P("## redflag≥3 exclusion — profile of BA-core signals it removes")
    if len(g):
        P(f"  removed {len(g):,} signals | mean p3m {g['p3m'].mean():+.2f}% | win {(g['p3m']>0).mean()*100:.1f}%"
          f" | crash<-20%: {100*(g['p3m']<-20).mean():.1f}%")
        kept=df[cb & ~(df['redflag_cnt'].fillna(0)>=3)]
        P(f"  (kept signals: mean {kept['p3m'].mean():+.2f}% | win {(kept['p3m']>0).mean()*100:.1f}%"
          f" | crash<-20%: {100*(kept['p3m']<-20).mean():.1f}%)")
        P("  → exclusion HELPS if removed signals are worse (lower mean/win, higher crash) than kept.")
    P("")
    with open(os.path.join(WORKDIR,"data","fa_quickwins_integrated.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_quickwins_integrated.md")

if __name__=="__main__":
    main()
