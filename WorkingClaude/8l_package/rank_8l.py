#!/usr/bin/env python3
"""
rank_8l.py — composite 8L score → prioritized top-N ranking
============================================================
Scores every ticker in data/unified_screener.csv with a ROUTE-AWARE 8L composite
(each company graded by its correct lens, then placed on a common 0-100 scale),
and ranks them. Weights encode this research stream's validated findings:
  - cheapness (L1) + engine/runway COMPOUNDER>>YIELD>>LOWROIC (L2/L6)
  - cash-machine ◆ (L3), moat via ROE proxy (L4)
  - contrarian dislocation = buy fear (deep dd rewarded for quality & cyclicals)
  - banks: NPL-gate + coverage/CAR/ROE + PB-vs-ROE cheapness (own lens)
  - cyclicals: commodity-trough (low pctile) + dislocation + low PB (own lens)
  - VALUE_TRAP penalised; SPECIAL_SITUATION scored separately (event risk)
Input: data/unified_screener.csv, data/engine_class.csv
Output: data/rank_8l.{md,csv}
"""
import warnings; warnings.filterwarnings("ignore")
import sys, os, os, re
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
WORKDIR=os.environ.get("WORKDIR_8L", r"/home/trido/thanhdt/WorkingClaude")
S=pd.read_csv(os.path.join(WORKDIR,"data","unified_screener.csv"))
# drop names the screener gated out (insolvency/falling-knife, bank AVOID, commodity-peak AVOID)
_drop=S["action"].astype(str).str.startswith("AVOID")|(S["verdict"]=="DISTRESSED")
print(f"excluded {int(_drop.sum())} gated names: "+", ".join(S[_drop]['ticker'].tolist()))
S=S[~_drop].reset_index(drop=True)
try:
    E=pd.read_csv(os.path.join(WORKDIR,"data","engine_class.csv")).set_index("ticker")
except Exception: E=pd.DataFrame()
try:
    MC=pd.read_csv(os.path.join(WORKDIR,"data","margin_cycle_detector.csv")).set_index("ticker")["cycle"].to_dict()
except Exception: MC={}

def num(pat,s,d=np.nan):
    m=re.search(pat,str(s));
    return float(m.group(1)) if m else d

def parse(r):
    s=r["detail"]; out={}
    out["PE"]=num(r"PE([\d.]+)",s); out["pe_z"]=num(r"pe_z([+-][\d.]+)",s)
    out["PEG"]=num(r"PEG([\d.]+)",s); out["ROE"]=num(r"ROE(\d+)%",s)
    out["dd"]=num(r"dd([+-]?\d+)%",s); out["PB"]=num(r"PB([\d.]+)",s)
    out["pb_z"]=num(r"pb_z([+-][\d.]+)",s)
    out["pctile"]=num(r"pctile([\d.]+)",s)
    cfy=num(r"CFOyld([+-]?\d+)%",s); out["cfo_yield"]=cfy/100 if pd.notna(cfy) else np.nan
    ul=num(r"UnRev/MV (\d+)%",s); out["un_lvl"]=ul/100 if pd.notna(ul) else np.nan
    uy=num(r"YoY([+-]?\d+)%",s); out["un_yoy"]=uy/100 if pd.notna(uy) else np.nan
    out["NPL"]=num(r"NPL([\d.]+)%",s); out["cov"]=num(r"cov(\d+)%",s)
    out["CAR"]=num(r"CAR(\d+)%",s); out["NPLchg"]=num(r"4qNPL([+-][\d.]+)pp",s)
    return pd.Series(out)

P=S.join(S.apply(parse,axis=1))

def asset_roic(t):
    if t in E.index: return E.loc[t,"asset_cagr"], E.loc[t,"roic5y"]
    return np.nan,np.nan

def score_row(r):
    t=r["ticker"]; route=r["route"]; v=r["verdict"]; eng=str(r["engine"]); comp={}
    liq=r["liqB"] if pd.notna(r["liqB"]) else 0
    # ---- liquidity (deployability, modest; applies to all) — liqB is momentum-aware = max(3M-med,1M) ----
    comp["liq"]=8 if liq>=50 else 6 if liq>=10 else 4 if liq>=4 else 2 if liq>=2 else 0
    # rising-liquidity bonus (user/TV1): don't drop good names whose liquidity climbs on strong results
    if "liq RISING" in str(r["detail"]): comp["liq_rising"]=2
    if route=="COMPOUNDER":
        ac,roic=asset_roic(t); is_ap="ASSET_PLAY" in eng
        if is_ap:
            # L8 asset-play NAV = deferred-rev BACKLOG (primary, IC-validated +0.13–0.22@1Y, orthogonal to PB)
            #                   + P/B floor (secondary, IC≈0 but = asset margin-of-safety / land-bank value).
            # Additive handles both sub-types: pre-sold-backlog (NTC/SIP/IDC) AND land-bank-cheap-book (DTD/LHG).
            ul=r["un_lvl"]
            backlog=20 if (pd.notna(ul) and ul>=0.50) else 15 if (pd.notna(ul) and ul>=0.25) else 10 if (pd.notna(ul) and ul>=0.12) else 5 if (pd.notna(ul) and ul>=0.05) else 0
            uy=r["un_yoy"]   # pace = DURABILITY flag only (IC≈0 for return): backlog running off → small caution
            if backlog>0 and pd.notna(uy) and uy<-0.10: backlog-=2
            pb=r["PB"]; pb_floor=8 if (pd.notna(pb) and 0<pb<1.0) else 5 if (pd.notna(pb) and pb<1.3) else 2 if (pd.notna(pb) and pb<1.7) else 0
            comp["L8_backlog"]=backlog; comp["L8_pbfloor"]=pb_floor
            if v=="VALUE_TRAP": comp["L8_trap"]=-10
        else:
            # L1 valuation (PE/PEG, TTM growth)
            base={"CHEAP_QUALITY":25,"CHEAP_1lens":12,"NOT_CHEAP":2,"VALUE_TRAP":-15,"SPECIAL_SITUATION":8}.get(v,0)
            pez=r["pe_z"]; zbon=np.clip(-pez,-1,2)*5 if pd.notna(pez) else 0           # cheaper-than-own-history
            peg=r["PEG"]; pegbon=8 if (pd.notna(peg) and 0<peg<=0.5) else 5 if (pd.notna(peg) and 0<peg<=1) else 0
            comp["L1_value"]=base+zbon+pegbon
            # L1 cash-yield (IC-validated, orthogonal to PB; floor 0 so reinvesting compounders aren't penalised)
            cfy=r["cfo_yield"]
            comp["L1_cash"]=10 if (pd.notna(cfy) and cfy>=0.20) else 7 if (pd.notna(cfy) and cfy>=0.12) else 4 if (pd.notna(cfy) and cfy>=0.07) else 1 if (pd.notna(cfy) and cfy>=0.03) else 0
            if pd.notna(cfy) and cfy>=0.12 and "◆" in eng: comp["L1_cash"]+=3   # confirms cheap genuine cash-machine
            # refinement #1: HYBRID-IP backlog bonus — non-asset-play compounder w/ meaningful deferred-lease
            # (UnRev/MktCap≥10%, e.g. VGC ~70% IP profit) carries land/IP NAV BEYOND operating earnings.
            # Bonus on top (not a lens flip) — operating value already credited via L1_value/cash.
            ulh=r["un_lvl"]
            if pd.notna(ulh) and ulh>=0.10: comp["L8_hybrid"]=8 if ulh>=0.30 else 5 if ulh>=0.15 else 3
        # L2/L6 engine + runway
        comp["L2_engine"]={"COMPOUNDER":22,"YIELD":8,"LOWROIC_GROWTH":3}.get(eng.split()[0].replace("◆","") if eng and eng!="-" else "-",6)
        comp["L6_runway"]=8 if (pd.notna(ac) and ac>0.12) else 5 if (pd.notna(ac) and ac>0.05) else 1 if (pd.notna(ac) and ac>0) else -2
        # L3 cash-machine
        comp["L3_cash"]=10 if "◆" in eng else 0
        # L4 moat (ROE proxy)
        roe=r["ROE"]; comp["L4_moat"]=15 if (pd.notna(roe) and roe>=30) else 10 if (pd.notna(roe) and roe>=18) else 5 if (pd.notna(roe) and roe>=12) else 0
        # contrarian dislocation (buy fear in quality)
        dd=r["dd"]; comp["dislocation"]=8 if (pd.notna(dd) and dd<=-30) else 5 if (pd.notna(dd) and dd<=-20) else 2 if (pd.notna(dd) and dd<=-10) else 0
        # L5 margin-cycle: peak margin = cyclically-inflated EPS (penalty); crushed margin = revert↑ opportunity.
        # Read from BOTH the margin_cycle CSV AND the screener detail (latter includes injected freight-rate
        # cyclicals like HAH whose NPM-percentile peak the commodity-only detector misses).
        dets=str(r["detail"])
        if MC.get(t)=="MARGIN_PEAK" or "MARGIN_PEAK" in dets: comp["L5_margin"]=-12
        elif MC.get(t)=="MARGIN_BOTTOM" or "MARGIN_BOTTOM" in dets: comp["L5_margin"]=+8
        # paired-peer overlay: INFO-ONLY flag (no score penalty). GPM-corr test (gpm_corr.py) showed
        # margin co-movement is WEAK even same-input (BMP-NTP ΔGPM +0.09 contemp; only +0.33 at 1q lag),
        # so it's a WATCH note (shown in screener detail), not a confirmed penalty. Revisit after observing
        # whether next-quarter margin compression actually follows the lead peer.
        pass
    elif route=="BANK":
        gate=v
        comp["gate"]={"CLEAN":40,"WATCH":15,"AVOID":-20}.get(gate,0)
        npl=r["NPL"]; comp["npl"]=15 if npl<1 else 12 if npl<1.5 else 8 if npl<2 else 4 if npl<2.5 else 2 if npl<3 else -5
        cov=r["cov"]; comp["coverage"]=10 if cov>=150 else 8 if cov>=100 else 5 if cov>=80 else 2 if cov>=50 else 0
        car=r["CAR"]; comp["CAR"]=6 if car>=14 else 5 if car>=12 else 3 if car>=10 else 1
        roe=r["ROE"]; comp["roe"]=10 if roe>=20 else 8 if roe>=17 else 5 if roe>=14 else 2 if roe>=10 else 0
        ch=r["NPLchg"]; comp["npl_trend"]=8 if ch<=-0.4 else 5 if ch<0 else -3 if ch>0.3 else 0
        pb=r["PB"]; rpb=(roe/pb) if (pd.notna(pb) and pb>0) else 0
        comp["pb_vs_roe"]=10 if rpb>=15 else 7 if rpb>=12 else 4 if rpb>=10 else 1   # ROE%/PB
    elif route=="CYCLICAL":
        comp["regime"]={"TROUGH_BUY":45,"cmdty_CHEAP":30,"ELEVATED-SUPPORTED":18,"cmdty_MID":10,
                        "cmdty_PEAK":-5,"SPECIAL_SITUATION":12}.get(v.split("(")[0],8)
        pct=r["pctile"]; comp["cmdty_pctile"]=round((1-pct)*20,1) if pd.notna(pct) else 0  # trough=high
        dd=r["dd"]; comp["dislocation"]=15 if (pd.notna(dd) and dd<=-30) else 12 if (pd.notna(dd) and dd<=-25) else 8 if (pd.notna(dd) and dd<=-20) else 4 if (pd.notna(dd) and dd<=-10) else 0
        pb=r["PB"]; comp["PB"]=-10 if (pd.notna(pb) and pb<=0) else 10 if (pd.notna(pb) and 0<pb<0.9) else 6 if (pd.notna(pb) and pb<1.2) else 3 if (pd.notna(pb) and pb<1.6) else 0
        # follow-up #2: cyclical-route asset-plays (rubber land-banks PHR/DPR) carry land/IP NAV beyond the
        # commodity cycle → add a MODEST backlog credit (secondary to the commodity read).
        if "ASSET_PLAY" in eng:
            ul=r["un_lvl"]
            if pd.notna(ul) and ul>0.02:
                comp["L8_backlog"]=10 if ul>=0.25 else 6 if ul>=0.12 else 3 if ul>=0.05 else 0
    elif route=="SUGAR":
        # TREND cyclical (sugar_cyclical.py): reward GOOD-regime + dip-in-uptrend; penalize WEAK downcycle.
        # Inverts the CYCLICAL branch (which rewards low pctile/trough) — for sugar low pctile = value-trap.
        comp["regime"]={"TREND_DIP_BUY":40,"TREND_UP":28,"WEAK_FADING":-5,"DOWNCYCLE_LOW":-12,
                        "SPECIAL_SITUATION":8}.get(str(v).split("(")[0].strip(),0)
        pct=r["pctile"]; comp["cmdty_trend"]=round(pct*15,1) if pd.notna(pct) else 0   # HIGH pctile=strength
        dd=r["dd"]
        if "TREND" in str(v):   # dip-buy rewarded ONLY in an up-regime; in WEAK a deep dd is a falling knife
            comp["dip"]=10 if (pd.notna(dd) and dd<=-25) else 6 if (pd.notna(dd) and dd<=-15) else 2 if (pd.notna(dd) and dd<=-8) else 0
        roe=r["ROE"]; comp["roe"]=8 if (pd.notna(roe) and roe>=25) else 5 if (pd.notna(roe) and roe>=15) else 2 if (pd.notna(roe) and roe>=10) else 0
        pb=r["PB"]; comp["PB"]=8 if (pd.notna(pb) and 0<pb<1.2) else 5 if (pd.notna(pb) and pb<1.8) else 2 if (pd.notna(pb) and pb<2.5) else 0
    elif route=="POWER":
        # debt-paydown LIFECYCLE (validated power_lifecycle_ic.py): PRE_INFLECTION+cheap = 2Y +53%/win89%;
        # debt-free=mature/yield (re-rated); debt-rising/CFO-neg=distress. Score by lifecycle stage + ROE + PB.
        comp["lifecycle"]={"PRE_INFLECTION_CHEAP":45,"PRE_INFLECTION":40,"PRE_INFLECTION_RICH":25,
                           "MID_CYCLE":18,"MATURE_YIELD":15,"DEBT_STRESS":-12,"UNKNOWN":0}.get(str(v),0)
        roe=r["ROE"]; comp["roe"]=10 if (pd.notna(roe) and roe>=20) else 7 if (pd.notna(roe) and roe>=15) else 4 if (pd.notna(roe) and roe>=10) else 0
        pb=r["PB"]; comp["PB"]=12 if (pd.notna(pb) and 0<pb<1.0) else 7 if (pd.notna(pb) and pb<1.5) else 3 if (pd.notna(pb) and pb<2) else 0
    score=sum(comp.values())
    return pd.Series({"score":round(score,1),**{f"_{k}":round(v,1) for k,v in comp.items()}})

R=P.join(P.apply(score_row,axis=1))
# CALIBRATION: cfo_yield (IC measured cross-sectionally = within-cohort ranking) only applies to
# non-asset-play compounders. Adding it raw would inflate their ABSOLUTE score vs banks/cyclicals
# (which can't be cash-yield-scored) and tilt the route mix. Demean it within the compounder cohort
# so it RE-RANKS compounders among themselves (preserves variation) without cross-route inflation.
if "_L1_cash" in R.columns:
    msk=R["_L1_cash"].notna(); m=R.loc[msk,"_L1_cash"].mean()
    R.loc[msk,"score"]=(R.loc[msk,"score"]-m).round(1)
    print(f"cfo_yield centered within compounder cohort (mean {m:.1f} removed, zero-sum re-rank)")
R=R.sort_values("score",ascending=False).reset_index(drop=True)
R["rank"]=R.index+1

# ---- output ----
cols=["rank","ticker","route","verdict","engine","score","liqB"]
lines=[]; pr=lambda s="":(print(s),lines.append(s))
pr("# 8L composite ranking — route-aware score (snapshot ~2026-05-29, market state NEUTRAL)")
pr(f"scored {len(R)} tickers | weights encode: cheapness + engine/runway + cash-machine + moat + dislocation; banks=NPL-gate+PB/ROE; cyclicals=trough+dislocation+PB")
pr("")
pr(f"{'#':>3} {'tkr':<5}{'route':<11}{'verdict':<20}{'engine':<16}{'score':>6} {'liqB':>6}  components")
for _,r in R.head(35).iterrows():
    comps=" ".join(f"{k[1:]}{r[k]:+.0f}" for k in R.columns if k.startswith("_") and pd.notna(r[k]) and r[k]!=0)
    pr(f"{r['rank']:>3} {r['ticker']:<5}{r['route']:<11}{str(r['verdict'])[:19]:<20}{str(r['engine'])[:15]:<16}{r['score']:>6.1f} {(r['liqB'] if pd.notna(r['liqB']) else 0):>6.0f}  {comps}")
pr("")
pr("## Prioritized TOP-20 (by 8L composite)")
top=R.head(20)
pr("  "+", ".join(f"{r['ticker']}({r['score']:.0f})" for _,r in top.iterrows()))
pr("")
pr("## TOP-20 by route")
for rt in ["BANK","CYCLICAL","SUGAR","COMPOUNDER"]:
    g=top[top["route"]==rt]
    pr(f"  {rt} ({len(g)}): "+", ".join(f"{r['ticker']}({r['score']:.0f})" for _,r in g.iterrows()))
pr("")
pr("Caveat: composite is a PRIORITIZATION aid, not a buy signal. NEUTRAL state (FA/quality edge strongest in CRISIS/BEAR per fa-horizon study). Liquidity small names hard to deploy. SPECIAL_SITUATION (DGC/PAT) carry event risk not in score.")
R[cols+[c for c in R.columns if c.startswith("_")]].to_csv(os.path.join(WORKDIR,"data","rank_8l.csv"),index=False)
with open(os.path.join(WORKDIR,"data","rank_8l.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
pr("Saved data/rank_8l.{md,csv}")
