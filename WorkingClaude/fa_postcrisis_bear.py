#!/usr/bin/env python3
"""
fa_postcrisis_bear.py
=====================
Tests the user's refinement: the CRISIS→BEAR transition, once it STABILIZES, is a
prime long-horizon entry for quality at depressed prices ("mặt bằng giá hấp dẫn").

Entry buckets (by DT5G state path at entry):
  IN_CRISIS        : state==1 (still in the panic)
  POST_CRISIS_BEAR : state==2 AND a CRISIS occurred within the last 90 sessions
                     AND ≥5 sessions since crisis (stabilized, not the flip-flop) ← sweet spot
  BEAR_OTHER       : state==2 with NO crisis in last 90 sessions
  RECOVER_NEUTRAL  : state==3 AND crisis within last 180 sessions (climbing out)
  NEUTRAL_OTHER    : state==3, no recent crisis
  BULL_EXBULL      : state in (4,5)

For each bucket: TOP-FA quintile median forward return at 3M/6M/1Y/2Y + win-rate,
and TOP−BOTTOM spread. Hypothesis ✓ if POST_CRISIS_BEAR shows the best long-horizon
(1Y/2Y) TOP returns — quality bought cheap right after the panic.

Uses cached data/_fa_horizon_raw.csv (FA rows + fwd returns + entry state) and the
DT5G daily series for the sessions-since-crisis path.
Output: data/fa_postcrisis_bear.md
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
HOR=[("f3m","3M"),("f6m","6M"),("f1y","1Y"),("f2y","2Y")]

def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as fh:
        fh.write(sql); tmp=fh.name
    try:
        cmd=(f'"{BQ_BIN}" query --use_legacy_sql=false --project_id={PROJECT} '
             f'--format=csv --max_rows=100000 < "{tmp}"')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    df=pd.read_csv(os.path.join(WORKDIR,"data","_fa_horizon_raw.csv"))
    df["time"]=pd.to_datetime(df["time"])
    for c,_ in HOR: df[c]=df[c].clip(-0.95,5.0)

    # ── DT5G series → sessions_since_crisis per date ──────────────────────
    st=bq_query("SELECT s.time, s.state FROM tav2_bq.vnindex_5state_dt5g_live AS s ORDER BY s.time")
    st["time"]=pd.to_datetime(st["time"]); st=st.sort_values("time").reset_index(drop=True)
    sess=[]; last_crisis=None
    for i,r in st.iterrows():
        if r["state"]==1: last_crisis=i
        sess.append(np.nan if last_crisis is None else i-last_crisis)
    st["sess_since_crisis"]=sess
    # transition dates CRISIS->BEAR for face validity
    st["prev"]=st["state"].shift(1)
    trans=st[(st["prev"]==1)&(st["state"]==2)]["time"]

    df=df.merge(st[["time","sess_since_crisis"]],on="time",how="left")

    def bucket(r):
        s=r["state"]; k=r["sess_since_crisis"]
        if s==1: return "IN_CRISIS"
        if s==2 and pd.notna(k) and 5<=k<=90: return "POST_CRISIS_BEAR"
        if s==2: return "BEAR_OTHER"
        if s==3 and pd.notna(k) and k<=180: return "RECOVER_NEUTRAL"
        if s==3: return "NEUTRAL_OTHER"
        if s in (4,5): return "BULL_EXBULL"
        return "OTHER"
    df["bucket"]=df.apply(bucket,axis=1)

    P("# CRISIS→BEAR stabilizing entry — long-horizon quality opportunity?")
    P("")
    P(f"CRISIS→BEAR transition dates in DT5G ({len(trans)}): "
      + ", ".join(str(d.date()) for d in trans))
    P("")
    P("Bucket sizes (FA-rating entries):")
    for b,n in df["bucket"].value_counts().items(): P(f"  {b:<18}{n:>7,}")
    P("")

    # TOP-FA quintile within bucket (rank total_score inside each bucket)
    for c,nm in HOR:
        sub=df.dropna(subset=[c]).copy()
        sub["qt"]=sub.groupby("bucket")["total_score"].transform(
            lambda x: pd.qcut(x.rank(method="first"),5,labels=False) if x.notna().sum()>=25 else np.nan)
        P(f"## Horizon {nm} — median forward return by entry bucket")
        P(f"{'bucket':<18}{'TOPmed':>9}{'BOTmed':>9}{'spread':>9}{'TOPwin%':>9}{'ALLmed':>9}{'N':>7}")
        P("-"*70)
        order=["IN_CRISIS","POST_CRISIS_BEAR","BEAR_OTHER","RECOVER_NEUTRAL","NEUTRAL_OTHER","BULL_EXBULL"]
        for b in order:
            g=sub[sub["bucket"]==b]
            if len(g)<40: continue
            top=g[g["qt"]==4][c]; bot=g[g["qt"]==0][c]
            if len(top)<8: continue
            P(f"{b:<18}{top.median()*100:>+8.1f}%{bot.median()*100:>+8.1f}%"
              f"{(top.median()-bot.median())*100:>+8.1f}%{(top>0).mean()*100:>8.0f}%"
              f"{g[c].median()*100:>+8.1f}%{len(g):>7,}")
        P("")
    P("Hypothesis ✓ if POST_CRISIS_BEAR TOP med at 1Y/2Y beats other buckets —")
    P("quality bought cheap just after the panic stabilizes = best long-horizon entry.")
    P("")
    with open(os.path.join(WORKDIR,"data","fa_postcrisis_bear.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_postcrisis_bear.md")

if __name__=="__main__":
    main()
