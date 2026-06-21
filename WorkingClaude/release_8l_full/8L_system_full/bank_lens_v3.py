#!/usr/bin/env python3
"""
bank_lens_v3.py — bank screen with ASSET-QUALITY GATE + NPL TREND (real vnstock data)
=====================================================================================
v2 ranked by score; v3 adds (1) asset-quality as a HARD GATE (a bank's #1 risk is
a bad-debt blowup — quality is pass/fail, not just points), and (2) NPL TREND over
the last ~6 quarters (NPL *rising* is more dangerous than its absolute level).

Gate (evaluated on REAL NPL / coverage / CAR / ROE / NPL-trend):
  AVOID  : NPL>3%  OR coverage<50%  OR CAR<9%  OR ROE<8%   (broken / blow-up risk)
  WATCH  : NPL>2%  OR coverage<80%  OR NPL rising >+0.5pp over 4q  (deteriorating)
  CLEAN  : else (NPL≤2%, cov≥80%, CAR≥9%, ROE≥8%, NPL stable/falling)
Only CLEAN banks are ranked (quality 0.6 + value 0.4); WATCH/AVOID listed separately.
Output: data/bank_lens_v3.md + .csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys, logging
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
logging.disable(logging.CRITICAL)
import os, time
import numpy as np, pandas as pd
from vnstock import Vnstock
WORKDIR=r"/home/trido/thanhdt/WorkingClaude"
BANKS=["VCB","BID","CTG","TCB","MBB","ACB","VPB","VIB","HDB","STB","SHB","TPB","MSB","OCB","LPB","EIB","NAB","SSB"]
C_NIM="Net Interest Margin"; C_NPL="Non-performing Loan Ratio"; C_CAR="Capital Adequacy Ratio"
C_CASA="CASA Ratio"; C_COV="Loan Loss Reserves to NPLs"; C_CIR="Cost to Income Ratio"
C_LG="Loans Growth"; C_ROE="ROE (%)"; C_PB="P/B"

def pull(tk, retries=3):
    for attempt in range(retries):
        try:
            df=Vnstock().stock(symbol=tk, source="VCI").finance.ratio(period="quarter", lang="en", dropna=False)
            df=df.copy(); df.columns=[c if isinstance(c,str) else c[-1] for c in df.columns]
            df=df.loc[:, ~pd.Index(df.columns).duplicated()]; break
        except Exception as e:
            if attempt==retries-1: print(f"  [skip {tk}] {repr(e)[:60]}",flush=True); return None
            time.sleep(4)
    try:
        q=df[df["lengthReport"].isin([1,2,3,4])].sort_values(["yearReport","lengthReport"])
        ann=df[df["lengthReport"]==5].sort_values("yearReport")
        if len(q)==0: return None
        last=q.iloc[-1]; g=lambda c: last[c] if c in last.index and pd.notna(last[c]) else np.nan
        npl_ser=q[C_NPL].dropna().values if C_NPL in q else np.array([])
        npl_now=npl_ser[-1] if len(npl_ser) else np.nan
        npl_4q=npl_ser[-5] if len(npl_ser)>=5 else (npl_ser[0] if len(npl_ser) else np.nan)
        # slope over last up-to-6 quarters (pp per quarter)
        tail=npl_ser[-6:]; slope=np.polyfit(range(len(tail)),tail,1)[0] if len(tail)>=3 else np.nan
        car=np.nan
        if len(ann) and C_CAR in ann.columns:
            cv=ann[ann[C_CAR]>0][C_CAR]; car=cv.iloc[-1] if len(cv) else np.nan
        return {"ticker":tk,"NIM":g(C_NIM),"NPL":npl_now,"NPL_4q":npl_4q,"NPL_slope":slope,
            "CAR":car,"CASA":g(C_CASA),"coverage":abs(g(C_COV)),"CIR":abs(g(C_CIR)),
            "loanG":g(C_LG),"ROE":g(C_ROE),"PB":g(C_PB)}
    except Exception as e:
        print(f"  [skip {tk}] parse {repr(e)[:50]}",flush=True); return None

rows=[]
for i,tk in enumerate(BANKS):
    r=pull(tk)
    if r:
        rows.append(r); ch=(r["NPL"]-r["NPL_4q"])*100 if pd.notna(r["NPL_4q"]) else float("nan")
        print(f"  {tk}: NPL={r['NPL']*100:.2f}% (4q chg {ch:+.2f}pp) cov={r['coverage']*100:.0f}% ROE={r['ROE']*100:.1f}%",flush=True)
    if i<len(BANKS)-1: time.sleep(3)
df=pd.DataFrame(rows)
if len(df)==0: print("NO DATA (network)."); sys.exit(0)
df["NPL_chg4q"]=(df["NPL"]-df["NPL_4q"])*100  # pp change over ~1y
df["rising"]=df["NPL_chg4q"]>0.5

def gate(r):
    if (r["NPL"]>0.03) or (r["coverage"]<0.50) or (pd.notna(r["CAR"]) and r["CAR"]<0.09) or (r["ROE"]<0.08): return "AVOID"
    if (r["NPL"]>0.02) or (r["coverage"]<0.80) or r["rising"]: return "WATCH"
    return "CLEAN"
df["gate"]=df.apply(gate,axis=1)

# rank CLEAN by quality+value
def rk(s,asc=True): return s.rank(pct=True) if asc else (1-s.rank(pct=True))
clean=df[df["gate"]=="CLEAN"].copy()
if len(clean)>=2:
    clean["q_assetq"]=(rk(clean["NPL"],asc=False)+rk(clean["coverage"]))/2
    clean["q_profit"]=(rk(clean["NIM"])+rk(clean["CIR"],asc=False)+rk(clean["CASA"]))/3
    clean["q_cap"]=rk(clean["CAR"])
    clean["roe_pb"]=clean["ROE"]/clean["PB"]
    b=np.polyfit(clean["ROE"],clean["PB"],1); clean["pb_resid"]=clean["PB"]-(b[0]*clean["ROE"]+b[1])
    clean["q_value"]=(rk(clean["roe_pb"])+rk(clean["pb_resid"],asc=False))/2
    clean["QUALITY"]=clean[["q_assetq","q_cap","q_profit"]].mean(axis=1)
    clean["SCORE"]=0.6*clean["QUALITY"]+0.4*clean["q_value"]
    clean=clean.sort_values("SCORE",ascending=False)

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Bank lens v3 — asset-quality GATE + NPL trend (real vnstock data)")
P("GATE: AVOID(NPL>3%|cov<50%|CAR<9%|ROE<8%) WATCH(NPL>2%|cov<80%|NPL rising>+0.5pp/4q) else CLEAN")
P("")
P(f"{'tkr':<5}{'NPL%':>6}{'4qChg':>7}{'cov%':>6}{'CAR%':>6}{'NIM%':>6}{'CASA%':>6}{'ROE%':>6}{'PB':>5}{'gate':>7}")
P("-"*64)
for _,r in df.sort_values(["gate","NPL"]).iterrows():
    P(f"{r['ticker']:<5}{r['NPL']*100:>6.2f}{r['NPL_chg4q']:>+7.2f}{r['coverage']*100:>6.0f}"
      f"{(r['CAR']*100 if pd.notna(r['CAR']) else float('nan')):>6.1f}{r['NIM']*100:>6.2f}{r['CASA']*100:>6.0f}"
      f"{r['ROE']*100:>6.1f}{r['PB']:>5.2f}{r['gate']:>7}")
P("")
if len(clean)>=2:
    P("## CLEAN banks ranked (passed quality gate) — quality 0.6 + value 0.4")
    P(f"{'rank tkr':<10}{'SCORE':>6}{'QUAL':>6}{'VALUE':>6}{'NPL%':>6}{'cov%':>6}{'ROE%':>6}{'PB':>5}")
    for i,(_,r) in enumerate(clean.iterrows(),1):
        P(f"{i:>2} {r['ticker']:<6}{r['SCORE']:>6.2f}{r['QUALITY']:>6.2f}{r['q_value']:>6.2f}{r['NPL']*100:>6.2f}{r['coverage']*100:>6.0f}{r['ROE']*100:>6.1f}{r['PB']:>5.2f}")
P("")
P("CLEAN: "+", ".join(df[df['gate']=='CLEAN']['ticker'].tolist() or ['none']))
P("WATCH: "+", ".join(df[df['gate']=='WATCH']['ticker'].tolist() or ['none']))
P("AVOID: "+", ".join(df[df['gate']=='AVOID']['ticker'].tolist() or ['none']))
P("")
P("NPL rising >+0.5pp over 4q (deteriorating): "+", ".join(df[df['rising']]['ticker'].tolist() or ['none']))
P("Note: real vnstock/VCI. CAR=annual. NPL trend = change vs ~4 quarters ago. Snapshot — recheck quarterly.")
df.to_csv(os.path.join(WORKDIR,"data","bank_lens_v3.csv"),index=False)
with open(os.path.join(WORKDIR,"data","bank_lens_v3.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/bank_lens_v3.{md,csv}")
