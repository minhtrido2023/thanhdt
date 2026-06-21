#!/usr/bin/env python3
"""
pt_capitulation_shadow.py — LIVE shadow paper-trade of the DT5G x 8L capitulation overlay
===============================================================================
Runs ALONGSIDE (never modifies) the V4/V5 paper-trade books. Models the capitulation
SLEEVE in isolation: a 50B reserve that sits in cash, deploys into the 8L quality+golden
basket on a washout signal, holds 60 trading days, returns to cash. Its forward NAV is
the out-of-sample evidence for the overlay decision.

Decided rule v2 (2026-06-10, supersedes 2026-06-04; see crisis_playbook.md §0b/§1):
  level  : oversold breadth (% prune D_RSI<0.30) >= 30%  (gate lowered 40->30: cliff is ~30%)
  sizing : size = base x grind; base by STATE: CRISIS 1.00 · NEUTRAL 0.75 · BULL/EXB 0.50 ·
           BEAR 0.50 only if (VNINDEX dd52w > -25% or VIX cooling) else 0 (win-24% zone, skip);
           grind = 0.50 if a prior washout fired 20-90 sessions ago else 1.00
  hold   : 60 trading days, then sell -> cash (reset)
  basket : equal-weight quality (ROE_Min5Y>=12 & ROIC5Y>=10 & FSCORE>=6) + golden
           (pb_z<-1) fallback -> quality+cheap -> quality, liq>=2B, no live redflag.

Point-in-time: the basket is FROZEN at the signal date (entry prices logged) = no hindsight.
Outputs: data/pt_capitulation_{state.json, logs.csv, baskets.csv}
"""
import os, sys, io, json, subprocess
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd

W=r"/home/trido/thanhdt/WorkingClaude"; PROJECT="lithe-record-440915-m9"
SDK_BIN=r"C:\Users\hotro\AppData\Local\Google\Cloud SDK\google-cloud-sdk\bin"
SEED=50_000_000_000.0; HOLD_TD=60; COST=0.003; WASHOUT=0.30   # gate v2 (2026-06-10): cliff ~30%, see playbook §0b; HOLD stays 60td (NEUTRAL move back-loaded, 40d = worst exit point)
STATE_NAME={1:"CRISIS",2:"BEAR",3:"NEUTRAL",4:"BULL",5:"EX-BULL"}
ST=os.path.join(W,"data","pt_capitulation_state.json")
LOG=os.path.join(W,"data","pt_capitulation_logs.csv")
BKT=os.path.join(W,"data","pt_capitulation_baskets.csv")

def bq(sql):
    env=dict(os.environ)
    o=subprocess.run(["bq","query","--use_legacy_sql=false",f"--project_id={PROJECT}",
        "--format=csv","--max_rows=5000"," ".join(sql.split())],capture_output=True,text=True,env=env)
    if o.returncode!=0: raise RuntimeError(o.stdout+o.stderr)
    return pd.read_csv(io.StringIO(o.stdout))

# ---- 1. latest regime + breadth history (grind detection) -------------------
hist=bq("""WITH daily AS (
  SELECT p.time, AVG(CASE WHEN p.D_RSI<0.3 THEN 1.0 ELSE 0 END) oversold
  FROM tav2_bq.ticker_prune p WHERE p.Close_T1>0 GROUP BY p.time)
 SELECT d.time, s.state, d.oversold FROM daily d
 JOIN tav2_bq.vnindex_5state_dt5g_live s USING(time)
 ORDER BY d.time DESC LIMIT 120""").sort_values("time").reset_index(drop=True)
today=str(hist.iloc[-1]["time"]); state=int(hist.iloc[-1]["state"]); oversold=float(hist.iloc[-1]["oversold"])
prior=hist.iloc[:-1]; pw=prior[prior["oversold"]>=WASHOUT]
grind=False
if len(pw):
    pos_ago=(len(hist)-1)-pw.index.max(); grind=20<=pos_ago<=90
fired = oversold>=WASHOUT
# v2.1 state routing (2026-06-10, playbook §0b/§1): CRISIS 1.0 / NEUTRAL 0.75 / BULL,EXB 0.5 /
# BEAR 0.5 only if (VNINDEX dd52w > -25% or DOMESTIC rv10-cooling >=15% off 30d peak) else 0.
# VIX dropped as threshold (US thermometer, decoupling + domestic-shock blind spots) — advisory only.
base = {1: 1.0, 3: 0.75, 4: 0.5, 5: 0.5}.get(state, 0.5)
if state == 2:
    try:
        vni = bq("""SELECT t.time, t.Close FROM tav2_bq.ticker AS t
                    WHERE t.ticker='VNINDEX' ORDER BY t.time DESC LIMIT 260""").sort_values("time")
        closes = vni["Close"].astype(float)
        dd_now = (float(closes.iloc[-1]) / float(closes.max()) - 1) * 100
        rv10 = closes.pct_change().rolling(10).std() * np.sqrt(252) * 100
        vn_cooling = bool(rv10.iloc[-1] <= rv10.rolling(30).max().iloc[-1] * 0.85)
    except Exception:
        dd_now, vn_cooling = -99.0, False
    base = 0.5 if (dd_now > -25 or vn_cooling) else 0.0
size = base*(0.5 if grind else 1.0)

# ---- 2. load / seed state ---------------------------------------------------
if os.path.exists(ST):
    stt=json.load(open(ST))
else:
    stt={"mode":"CASH","nav":SEED,"cash":SEED,"entry_date":None,"basket":{},"tier":None,"size":0.0,"last_date":None}

if stt.get("last_date")==today:
    print(f"[{today}] already processed today — no-op."); sys.exit(0)

note=""
# ---- 3. if DEPLOYED: mark to market, exit at 60 td --------------------------
if stt["mode"]=="DEPLOYED":
    tks=list(stt["basket"].keys()); inlist=",".join(f"'{t}'" for t in tks)
    px=bq(f"""WITH lt AS (SELECT p.ticker, MAX(p.time) mx FROM tav2_bq.ticker_prune p
              WHERE p.ticker IN ({inlist}) GROUP BY p.ticker)
              SELECT p.ticker, p.Close FROM tav2_bq.ticker_prune p JOIN lt ON lt.ticker=p.ticker AND lt.mx=p.time""")
    cur=dict(zip(px["ticker"],px["Close"]))
    mtm=sum(b["shares"]*cur.get(t,b["entry_px"]) for t,b in stt["basket"].items())
    nav=stt["cash"]+mtm
    held_td=int(bq(f"SELECT COUNT(*) n FROM tav2_bq.vnindex_5state_dt5g_live WHERE time>DATE '{stt['entry_date']}' AND time<=DATE '{today}'").iloc[0]["n"])
    if held_td>=HOLD_TD:
        proceeds=mtm*(1-COST); stt["cash"]+=proceeds; nav=stt["cash"]
        ret=nav/SEED-1
        note=f"EXIT after {held_td}td: basket {tks} -> cash. sleeve NAV x{nav/SEED:.3f}"
        stt.update(mode="CASH",basket={},tier=None,size=0.0)
    else:
        note=f"HOLDING {held_td}/{HOLD_TD}td · {len(tks)} names · MTM x{nav/SEED:.3f}"
    stt["nav"]=nav

# ---- 4. if CASH and washout fires: deploy point-in-time --------------------
elif fired:
    snap=bq("""WITH latest AS (SELECT MAX(time) mt FROM tav2_bq.ticker_prune)
      SELECT p.ticker, p.Close, SAFE_DIVIDE(p.PB-p.PB_MA5Y,p.PB_SD5Y) pb_z,
             p.ROE_Min5Y, p.ROIC5Y, p.FSCORE,
             COALESCE(p.Price,p.Close)*p.Volume/1e9 liq_bn
      FROM tav2_bq.ticker_prune p, latest WHERE p.time=latest.mt""")
    snap["q"]=(snap.ROE_Min5Y>=0.12)&(snap.ROIC5Y>=0.10)&(snap.FSCORE>=6)
    snap=snap[(snap.liq_bn>=2)&snap.Close.gt(0)]
    q=snap[snap.q]
    g=q[q.pb_z<-1]; c=q[q.pb_z<0]
    pick = g if len(g)>=3 else (c if len(c)>=3 else q)
    pick=pick.sort_values("pb_z").head(15)
    if len(pick)>=3:
        deploy_amt=stt["nav"]*size
        per=deploy_amt/len(pick); stt["basket"]={}
        for _,r in pick.iterrows():
            stt["basket"][r.ticker]={"shares":per/r.Close,"entry_px":float(r.Close),"pb_z":float(r.pb_z)}
        stt["cash"]=stt["nav"]-deploy_amt-deploy_amt*COST
        tier=f"{'CRISIS' if state==1 else 'NONCRISIS'}{'+GRIND' if grind else ''} size={size:.2f}"
        stt.update(mode="DEPLOYED",entry_date=today,tier=tier,size=size)
        note=f"DEPLOY {size*100:.0f}% ({tier}) -> {list(stt['basket'].keys())}"
        bdf=pd.DataFrame([{"event_date":today,"ticker":t,"entry_px":b["entry_px"],"pb_z":b["pb_z"],
                           "weight":round(1/len(pick),3),"size":size,"tier":tier} for t,b in stt["basket"].items()])
        bdf.to_csv(BKT,mode="a",header=not os.path.exists(BKT),index=False)
    else:
        note=f"washout fired ({oversold*100:.0f}%) but <3 eligible names — stay cash"
else:
    note=f"dormant (oversold {oversold*100:.0f}% < {WASHOUT*100:.0f}%)"

# ---- 5. log + persist -------------------------------------------------------
stt["last_date"]=today
row={"date":today,"dt5g_state":state,"regime":STATE_NAME.get(state),"oversold_pct":round(oversold*100,1),
     "fired":fired,"grind":grind,"size":size if fired else 0.0,"mode":stt["mode"],
     "nav":round(stt["nav"]),"nav_x":round(stt["nav"]/SEED,4),"n_holdings":len(stt["basket"]),"note":note}
pd.DataFrame([row]).to_csv(LOG,mode="a",header=not os.path.exists(LOG),index=False)
json.dump(stt,open(ST,"w"),indent=2,default=str)
print(f"[{today}] {STATE_NAME.get(state)}({state}) oversold {oversold*100:.1f}% | {stt['mode']} | x{stt['nav']/SEED:.3f} | {note}")
