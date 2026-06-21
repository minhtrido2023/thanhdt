#!/usr/bin/env python3
"""
bank_lens_v2.py — bank screen with REAL ratios from vnstock (VCI)
=================================================================
Upgrades bank_valuation_lens.py from BQ-proxies (ROE_Min, OwnEq_Cap) to REAL
bank metrics: NPL, coverage (LLR/NPL), CAR, NIM, CIR, CASA, loan growth.
Five bank-correct axes (percentile-ranked within the bank universe):
  Asset quality : low NPL + high coverage
  Capital       : high CAR (annual report)
  Profitability : high NIM + low CIR + high CASA (cheap funding moat)
  Valuation     : ROE/PB (earnings yield on book — cheap-for-quality) + PB-vs-ROE residual
  Growth        : loan growth
Composite = quality(asset+capital+profit) + value; flag red (high NPL / low CAR / low coverage).
Pulls latest QUARTER for NPL/NIM/CASA/CIR/coverage/loanG/ROE/PB; latest ANNUAL for CAR.
Output: data/bank_lens_v2.md + .csv
"""
import warnings; warnings.filterwarnings("ignore")
import sys, logging
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
logging.disable(logging.CRITICAL)  # silence vnstock network warnings
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
            df=df.copy()
            # flatten MultiIndex + DEDUPE columns (vnstock returns dup "Cost to Income Ratio")
            df.columns=[c if isinstance(c,str) else c[-1] for c in df.columns]
            df=df.loc[:, ~pd.Index(df.columns).duplicated()]
            break
        except Exception as e:
            if attempt==retries-1: print(f"  [skip {tk}] {repr(e)[:70]}"); return None
            time.sleep(4)
    try:
        q=df[df["lengthReport"].isin([1,2,3,4])].sort_values(["yearReport","lengthReport"])
        ann=df[df["lengthReport"]==5].sort_values("yearReport")
        if len(q)==0: return None
        last=q.iloc[-1]
        car=np.nan
        if len(ann) and C_CAR in ann.columns:
            carv=ann[ann[C_CAR]>0][C_CAR]
            car=carv.iloc[-1] if len(carv) else np.nan
        g=lambda c: last[c] if c in last.index and pd.notna(last[c]) else np.nan
        return {"ticker":tk,"yr":int(last["yearReport"]),"q":int(last["lengthReport"]),
            "NIM":g(C_NIM),"NPL":g(C_NPL),"CAR":car,"CASA":g(C_CASA),
            "coverage":abs(g(C_COV)),"CIR":abs(g(C_CIR)),"loanG":g(C_LG),
            "ROE":g(C_ROE),"PB":g(C_PB)}
    except Exception as e:
        print(f"  [skip {tk}] {repr(e)[:80]}"); return None

rows=[]
for i,tk in enumerate(BANKS):
    r=pull(tk)
    if r:
        rows.append(r)
        print(f"  {tk}: NPL={r['NPL']*100:.2f}% CAR={(r['CAR']*100 if pd.notna(r['CAR']) else float('nan')):.1f}% NIM={r['NIM']*100:.2f}% ROE={r['ROE']*100:.1f}% PB={r['PB']:.2f}", flush=True)
    if i<len(BANKS)-1: time.sleep(3)  # pace requests to avoid reset/rate-limit
df=pd.DataFrame(rows)
if len(df)==0:
    print("\nNO DATA pulled (network/DNS to VCI unavailable). Try again later or via a networked host."); sys.exit(0)
df.to_csv(os.path.join(WORKDIR,"data","bank_lens_v2_raw.csv"),index=False)
print(f"\n[pulled {len(df)}/{len(BANKS)} banks]")

# percentile ranks (higher=better); invert NPL & CIR
def rk(s,asc=True): return s.rank(pct=True) if asc else (1-s.rank(pct=True))
df["q_assetq"]=(rk(df["NPL"],asc=False)+rk(df["coverage"]))/2
df["q_capital"]=rk(df["CAR"])
df["q_profit"]=(rk(df["NIM"])+rk(df["CIR"],asc=False)+rk(df["CASA"]))/3
df["roe_pb"]=df["ROE"]/df["PB"]
# PB-vs-ROE residual (cheap-for-ROE)
d=df.dropna(subset=["PB","ROE"]); b=np.polyfit(d["ROE"],d["PB"],1)
df["pb_resid"]=df["PB"]-(b[0]*df["ROE"]+b[1])
df["q_value"]=(rk(df["roe_pb"])+rk(df["pb_resid"],asc=False))/2
df["q_growth"]=rk(df["loanG"])
df["QUALITY"]=df[["q_assetq","q_capital","q_profit"]].mean(axis=1)
df["SCORE"]=0.6*df["QUALITY"]+0.4*df["q_value"]
df["red_flag"]=np.where((df["NPL"]>0.03)|(df["coverage"]<0.7)|((df["CAR"]<0.09)&df["CAR"].notna()),"⚠","")
df=df.sort_values("SCORE",ascending=False)

lines=[]; P=lambda s="":(print(s),lines.append(s))
P("# Bank lens v2 — REAL ratios (vnstock/VCI), latest quarter")
P(f"universe {len(df)} banks | value fit PB≈{b[0]:.3f}·ROE+{b[1]:.2f}")
P("")
P(f"{'tkr':<5}{'NPL%':>6}{'cov%':>6}{'CAR%':>6}{'NIM%':>6}{'CIR%':>6}{'CASA%':>6}{'loanG%':>7}{'ROE%':>6}{'PB':>5}{'ROE/PB':>7}{'SCORE':>6} flag")
P("-"*84)
for _,r in df.iterrows():
    P(f"{r['ticker']:<5}{r['NPL']*100:>6.2f}{r['coverage']*100:>6.0f}"
      f"{(r['CAR']*100 if pd.notna(r['CAR']) else float('nan')):>6.1f}{r['NIM']*100:>6.2f}{r['CIR']*100:>6.0f}"
      f"{r['CASA']*100:>6.0f}{r['loanG']*100:>+7.1f}{r['ROE']*100:>6.1f}{r['PB']:>5.2f}{r['roe_pb']*100 if r['roe_pb']<1 else r['roe_pb']:>7.1f}{r['SCORE']:>6.2f} {r['red_flag']}")
P("")
P("Top-quality (asset+capital+profit): "+", ".join(df.sort_values('QUALITY',ascending=False).head(6)['ticker']))
P("Cheapest-for-ROE (value): "+", ".join(df.sort_values('q_value',ascending=False).head(6)['ticker']))
P("Best combined (0.6 quality + 0.4 value): "+", ".join(df.head(6)['ticker']))
P("Red flags (NPL>3% | coverage<70% | CAR<9%): "+", ".join(df[df['red_flag']!='']['ticker'].tolist() or ['none']))
P("")
P("Note: CAR = latest ANNUAL (quarterly not disclosed). coverage/CIR sign-corrected. Real vnstock data.")
df.to_csv(os.path.join(WORKDIR,"data","bank_lens_v2.csv"),index=False)
with open(os.path.join(WORKDIR,"data","bank_lens_v2.md"),"w",encoding="utf-8") as f: f.write("\n".join(lines))
P("Saved data/bank_lens_v2.{md,csv}")
