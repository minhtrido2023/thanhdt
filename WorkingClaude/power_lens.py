#!/usr/bin/env python3
"""power_lens.py — sector lens for POWER (ICB 7535, hydro/thermal): the debt-paydown LIFECYCLE.
Validated (power_lifecycle_ic.py): a power plant = levered infra annuity. PRE-INFLECTION (debt high
BUT FALLING + CFO covering) + cheap PB = the golden buy (2Y +53%/win89% at PB<1.0); debt-free=mature/yield
(re-rated); debt-rising-or-CFO-negative = distress. Generic FA misfires (high debt/neg EPS/neg IntCov early).
Routes ICB 7535 to this lens (like bank_lens). Output: data/power_lens.{md,csv}."""
import warnings; warnings.filterwarnings("ignore")
import sys, os, os, subprocess, tempfile
from io import StringIO
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
PROJECT="lithe-record-440915-m9"; BQ=os.environ.get("BQ_BIN", (r"bq" if os.name=="nt" else "bq"))
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f: f.write(sql); tmp=f.name
    try: r=subprocess.run(f'{"type" if os.name=="nt" else "cat"} "{tmp}" | "{BQ}" query --use_legacy_sql=false --project_id={PROJECT} --format=csv --max_rows=100000',capture_output=True,text=True,timeout=300,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))

d=bq("""
WITH px AS (SELECT t.ticker, t.Close, t.Volume_3M_P50, t.Volume_1M, t.PB, t.PE,
   ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time DESC) rn
   FROM tav2_bq.ticker_1m t WHERE t.ICB_Code=7535 AND t.Close IS NOT NULL),
f AS (SELECT x.ticker, x.STLTDebt_Eq_P0 deq, x.STLTDebt_Eq_P4 deq4,
   (x.CF_OA_P0+x.CF_OA_P1+x.CF_OA_P2+x.CF_OA_P3) cfo_ttm,
   x.NP_P0+x.NP_P1+x.NP_P2+x.NP_P3 np_ttm, x.ROE_Trailing roe, x.IntCov_P0 intcov, x.Revenue_YoY_P0 rev_yoy,
   ROW_NUMBER() OVER(PARTITION BY x.ticker ORDER BY x.time DESC) rn
   FROM tav2_bq.ticker_financial x WHERE x.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker t2 WHERE t2.ICB_Code=7535))
SELECT f.ticker, ROUND(f.deq,3) deq, ROUND(f.deq4,3) deq4, ROUND(f.cfo_ttm/1e9,1) cfo_ttm_bn,
  ROUND(f.np_ttm/1e9,1) np_ttm_bn, ROUND(f.roe*100,1) roe, ROUND(px.PB,2) pb, ROUND(px.PE,1) pe,
  ROUND(f.rev_yoy,3) rev_yoy,
  ROUND(GREATEST(px.Volume_3M_P50,px.Volume_1M)*px.Close/1e9,2) liqB, ROUND(px.Close,0) close
FROM f JOIN px ON px.ticker=f.ticker AND px.rn=1 WHERE f.rn=1""")

# hydro names (rainfall-driven) — hydrology cycle overlay applies only to these, not thermal (fuel/PPA)
HYDRO={"VSH","CHP","SHP","SJD","TBC","TMP","SBA","DRL","GHC","HNA","SEB","S4A","AVC","ISH","SBH","HJS",
       "VPD","DNH","HPD","BHA","NTH","QPH","GSM","SP2","TTE","NED","BSA","BHA","DNC","HIO","UIC","ND2"}

def classify(r):
    deq,deq4,cfo,pb,roe=r["deq"],r["deq4"],r["cfo_ttm_bn"],r["pb"],r["roe"]
    falling=pd.notna(deq4) and pd.notna(deq) and deq<deq4
    cfo_pos=pd.notna(cfo) and cfo>0
    cheap=pd.notna(pb) and pb<1.2
    if pd.isna(deq): return ("UNKNOWN","WATCH","no debt data")
    # debt-free mature: re-rated annuity → yield/hold (QTP-type)
    if deq<0.3:
        v="MATURE_YIELD"; act="HOLD/yield" if (pd.notna(roe) and roe>=12) else "WATCH"
        return (v,act,f"debt-free (D/E {deq}) ROE{roe:.0f}% PB{pb} → re-rated annuity, dividend play")
    # meaningful debt
    if deq>=0.7 and falling and cfo_pos:
        if pd.notna(pb) and pb<1.0: v="PRE_INFLECTION_CHEAP"; act="BUY-zone"     # validated 2Y +53%/win89%
        elif cheap: v="PRE_INFLECTION"; act="BUY-zone"
        else: v="PRE_INFLECTION_RICH"; act="ACCUMULATE/watch"
        return (v,act,f"D/E {deq}↓(from {deq4}) CFO+{cfo:.0f}bn covering → debt retiring, earnings-surge ahead; PB{pb} ROE{roe:.0f}%")
    if deq>=0.7 and not (falling and cfo_pos):
        why="debt NOT falling" if not falling else "CFO not covering"
        return ("DEBT_STRESS","AVOID-new (verify)",f"D/E {deq} high & {why} (cfo {cfo}) → distress risk not pre-inflection ⚠")
    # mid (0.3-0.7)
    if cheap: return ("MID_CYCLE","ACCUMULATE/watch",f"D/E {deq} mid, PB{pb} cheap ROE{roe:.0f}%")
    return ("MID_CYCLE","WATCH",f"D/E {deq} mid, PB{pb} ROE{roe:.0f}%")

res=d.apply(lambda r: pd.Series(classify(r),index=["verdict","action","detail"]),axis=1)
out=d.join(res)
# overlays: HYDROLOGY cycle (hydro only — validated: confirmed wet-recovery > blind-drought; drought works if also cheap)
# + LIQUIDITY caveat (user: hydro low-liq limits deployability)
def tags(r):
    t=[]
    if r["ticker"] in HYDRO and pd.notna(r["rev_yoy"]):
        ry=r["rev_yoy"]
        if ry>0.15: t.append(f"🌧 wet-recovery tailwind (rev{ry*100:+.0f}% YoY → output up)")
        elif ry<-0.15:
            t.append(f"☀ drought (rev{ry*100:+.0f}%)"+(" + cheap → contrarian-buy" if (pd.notna(r["pb"]) and r["pb"]<1.2) else " — watch, not cheap yet"))
    if pd.notna(r["liqB"]) and r["liqB"]<1: t.append(f"⚠ low-liq {r['liqB']:.1f}B (deployability limited)")
    return " | ".join(t)
out["detail"]=out.apply(lambda r: r["detail"]+(" | "+tags(r) if tags(r) else ""),axis=1)
rank={"BUY-zone":0,"ACCUMULATE/watch":1,"HOLD/yield":2,"WATCH":3,"AVOID-new (verify)":4}
out["ar"]=out["action"].map(rank).fillna(5); out=out.sort_values(["ar","deq"])
out.drop(columns=["ar"]).to_csv(os.path.join(WORKDIR,"data","power_lens.csv"),index=False)
lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Power lens (ICB 7535) — debt-paydown lifecycle")
P(f"universe {len(out)} | validated: PRE-INFLECTION+cheap = 2Y +53%/win89%; debt-free=mature/yield; debt-rising/CFO-neg=distress")
P("")
P(f"{'tkr':<6}{'verdict':<22}{'action':<20}{'liqB':>6}  detail")
for _,r in out.iterrows():
    P(f"{r['ticker']:<6}{r['verdict']:<22}{r['action']:<20}{(r['liqB'] if pd.notna(r['liqB']) else 0):>6.1f}  {r['detail']}")
P("")
P("BUY-zone (pre-inflection): "+(", ".join(out[out.action=='BUY-zone']['ticker']) or "none"))
P("Caveat: hydro=hydrology/drought risk, thermal=fuel/PPA; asset-life (hydro~40-50y, thermal~25-30y) not in BQ; verify CFO genuinely retires debt (not refinancing).")
with open(os.path.join(WORKDIR,"data","power_lens.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/power_lens.{md,csv}")
