#!/usr/bin/env python3
"""
oil_pvd_anticip_gas.py
======================
(1) PVD anticipation: does VALUATION (P/B) lead EARNINGS (GPM) re: oil?
    - cross-corr oil[t-lag] vs GPM[t]  (earnings lag, known ~6Q)
    - cross-corr oil[t-lag] vs PB[t]   (price lag — expect short if mkt anticipates)
    - lead/lag PB vs GPM: corr(PB[t], GPM[t+k]) — k>0 => PB LEADS earnings
(2) GAS framework: gas selling price linked to FO (oil) w/ trailing avg -> short lag.
    - cross-corr NP/GPM/Rev vs oil; expect peak lag ~1-2Q (<< PVD's 4-6Q), minimal inventory.
Alignment fix: ticker_financial.time = Release_Date -> merge oil/PB on `quarter` label.
PB taken at end of the REPORTING calendar quarter (not release date).
Output: data/oil_pvd_anticip_gas.md
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
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f:
        f.write(sql); tmp=f.name
    try:
        r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                         f'--project_id={PROJECT} --format=csv --max_rows=500000',
                         capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0 or not r.stdout.strip(): raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

def xcorr(a,b,lags):
    """corr(a[t], b[t-lag]) for lag in lags (lag>0 => b leads a / a lags b)."""
    out=[]
    for L in lags:
        if L>0:  x,y=a[L:],b[:-L]
        elif L<0: x,y=a[:L],b[-L:]
        else:    x,y=a,b
        m=np.isfinite(x)&np.isfinite(y)
        out.append(np.corrcoef(x[m],y[m])[0,1] if m.sum()>10 else np.nan)
    return out

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    # Brent quarterly avg
    br=pd.read_csv(os.path.join(WORKDIR,"data","brent_monthly_full.csv"))
    br["month"]=pd.PeriodIndex(br["month"],freq="M"); br=br.set_index("month").sort_index()
    bq_avg=br["brent"].groupby(br.index.asfreq("Q")).mean()
    bq_avg.index=bq_avg.index.astype(str)
    B=bq_avg.rename("brent_avg").rename_axis("q").reset_index()

    def panel(tk):
        # quarterly PB at end of each CALENDAR quarter
        pbq=bq(f"""
          WITH x AS (
            SELECT FORMAT_DATE('%Y',t.time)||'Q'||CAST(EXTRACT(QUARTER FROM t.time) AS STRING) AS q,
                   t.time, t.PB, t.Close,
                   ROW_NUMBER() OVER (PARTITION BY EXTRACT(YEAR FROM t.time),EXTRACT(QUARTER FROM t.time)
                                      ORDER BY t.time DESC) rn
            FROM tav2_bq.ticker AS t WHERE t.ticker='{tk}' AND t.time>='2013-10-01')
          SELECT q, PB, Close FROM x WHERE rn=1 ORDER BY q""")
        fin=bq(f"""SELECT t.quarter AS q, t.Revenue_P0,t.NP_P0,t.GPM_P0,t.NPM_P0
                   FROM tav2_bq.ticker_financial AS t WHERE t.ticker='{tk}' ORDER BY t.time""")
        d=fin.merge(B,on="q",how="left").merge(pbq,on="q",how="left")
        # order by quarter chronologically
        d["yr"]=d["q"].str[:4].astype(int); d["qn"]=d["q"].str[-1].astype(int)
        d=d.sort_values(["yr","qn"]).reset_index(drop=True)
        return d

    # ============ (1) PVD anticipation ============
    pvd=panel("PVD"); pvd=pvd[pvd["yr"]>=2014].reset_index(drop=True)
    P("# (1) PVD — Thi truong co DINH GIA TRUOC do tre loi nhuan khong?")
    P("Cross-corr voi gia dau: oil[t-lag] vs (GPM ket qua) va (PB dinh gia).")
    P("Neu PB bam dau o lag NGAN hon GPM -> thi truong di TRUOC fundamentals.")
    P("")
    lags=list(range(0,9))
    cg=xcorr(pvd["GPM_P0"].values, pvd["brent_avg"].values, lags)
    cp=xcorr(pvd["PB"].values,     pvd["brent_avg"].values, lags)
    P(f"{'lag(Q)':<8}"+"".join(f"{L:>6}" for L in lags))
    P(f"{'GPM~oil':<8}"+"".join(f"{v:>+6.2f}" for v in cg)+f"   dinh lag {lags[int(np.nanargmax(cg))]}Q")
    P(f"{'PB ~oil':<8}"+"".join(f"{v:>+6.2f}" for v in cp)+f"   dinh lag {lags[int(np.nanargmax(cp))]}Q")
    P("")
    # does PB lead GPM? corr(PB[t], GPM[t+k]); k>0 means PB today vs FUTURE gpm
    leads=list(range(-2,9))
    cl=xcorr(pvd["GPM_P0"].values, pvd["PB"].values, leads)  # corr(GPM[t],PB[t-lag]) lag>0 => PB leads GPM
    P("PB co DAN DAT loi nhuan? corr(GPM[t], PB[t-k]); k>0 = PB di truoc GPM k quy:")
    P(f"{'k(Q)':<8}"+"".join(f"{L:>6}" for L in leads))
    P(f"{'corr':<8}"+"".join(f"{v:>+6.2f}" for v in cl)+f"   dinh k={leads[int(np.nanargmax(cl))]}Q")
    kbest=leads[int(np.nanargmax(cl))]
    P(f"-> PB dan dat GPM ~{kbest} quy." if kbest>0 else "-> PB khong dan dat ro.")
    P("")
    P("Quy te PVD (PB vs GPM vs oil) — chu y PB xoay som hon GPM:")
    P(f"{'q':<8}{'brent':>7}{'PB':>6}{'GPM%':>6}")
    for _,r in pvd.iterrows():
        if r["yr"]>=2015:
            P(f"{r['q']:<8}{r['brent_avg']:>7.0f}{r['PB']:>6.2f}{r['GPM_P0']*100:>6.0f}")
    P("")

    # ============ (2) GAS framework ============
    gas=panel("GAS"); gas=gas[gas["yr"]>=2014].reset_index(drop=True)
    P("# (2) GAS — gia ban khi neo FO (dau) co tre, ton kho thap")
    P("Cross-corr NP/GPM/Rev/NPM vs oil[t-lag]; ky vong dinh lag NGAN (~1-2Q).")
    P("")
    P(f"{'lag(Q)':<8}"+"".join(f"{L:>6}" for L in lags))
    for metric,lab in [("NP_P0","NP"),("GPM_P0","GPM"),("NPM_P0","NPM"),("Revenue_P0","Rev")]:
        c=xcorr(gas[metric].values, gas["brent_avg"].values, lags)
        P(f"{lab:<8}"+"".join(f"{v:>+6.2f}" for v in c)+f"   dinh lag {lags[int(np.nanargmax(c))]}Q")
    P("")
    # GAS inventory check: does intra-quarter oil direction matter? (expect weak)
    # bucket NP by oil level instead (level-driven)
    gas["oil_bucket"]=pd.qcut(gas["brent_avg"],3,labels=["dau THAP","dau TB","dau CAO"])
    P("GAS NP trung binh theo MAT BANG dau (level-driven, khong phai huong):")
    P(f"{'bucket':<10}{'nQ':>4}{'brent_tb':>9}{'NP_tb(bn)':>11}{'GPM_tb':>8}")
    for lab in ["dau THAP","dau TB","dau CAO"]:
        g=gas[gas["oil_bucket"]==lab]
        if len(g)==0: continue
        P(f"{lab:<10}{len(g):>4}{g['brent_avg'].mean():>9.0f}{g['NP_P0'].mean()/1e9:>11.0f}{g['GPM_P0'].mean()*100:>7.0f}%")
    P("")
    P("Quy te GAS (oil vs NP vs GPM):")
    P(f"{'q':<8}{'brent':>7}{'NP_bn':>8}{'GPM%':>6}{'PB':>6}")
    for _,r in gas.iterrows():
        if r["yr"]>=2018:
            P(f"{r['q']:<8}{r['brent_avg']:>7.0f}{r['NP_P0']/1e9:>8.0f}{r['GPM_P0']*100:>6.0f}{r['PB']:>6.2f}")

    out=os.path.join(WORKDIR,"data","oil_pvd_anticip_gas.md")
    with open(out,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    P(f"\nSaved {out}")

if __name__=="__main__": main()
