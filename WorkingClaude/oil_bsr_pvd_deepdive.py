#!/usr/bin/env python3
"""
oil_bsr_pvd_deepdive.py — two mechanism deep-dives
==================================================
(1) BSR — tach LAI/LO TON KHO (inventory, theo HUONG dau trong quy) khoi
    BIEN LOC/CRACK (level). Hoi quy GPM/NP ~ brent_avg + oil_QoQ_change(end-of-q),
    bucket theo huong dau trong quy, uoc luong swing VND do ton kho.
(2) PVD — do DO TRE backlog: cross-correlation GPM/NP/Revenue vs Brent o lag 0..8 quy,
    tim lag dinh; bang theo TUNG CHU KY gian khoan (ngay dau xoay vs ngay PVD xoay).
Output: data/oil_bsr_pvd_deepdive.md
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

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))

    # ---- Brent quarterly stats ----
    br=pd.read_csv(os.path.join(WORKDIR,"data","brent_monthly_full.csv"))
    br["month"]=pd.PeriodIndex(br["month"],freq="M"); br=br.set_index("month").sort_index()
    q=br.index.asfreq("Q")
    bq_avg=br["brent"].groupby(q).mean().rename("brent_avg")
    bq_end=br["brent"].groupby(q).last().rename("brent_end")   # last month price in quarter
    B=pd.concat([bq_avg,bq_end],axis=1)
    B["brent_prev_end"]=B["brent_end"].shift(1)
    B["oil_qoq"]=B["brent_end"]/B["brent_prev_end"]-1          # intra/over-quarter end move -> inventory driver
    B["oil_yoy"]=B["brent_avg"].pct_change(4)
    B.index=B.index.astype(str)              # PeriodIndex(Q) -> '2014Q1' style
    B=B.reset_index(names="q")

    def getfin(tk):
        # NOTE: ticker_financial.time = Release_Date (~1Q after quarter-end), so we merge
        # Brent on the REPORTING-quarter label `quarter` (e.g. '2022Q2'), not Period(time).
        d=bq(f"""SELECT t.time,t.quarter,t.Revenue_P0,t.NP_P0,t.GPM_P0,t.NPM_P0
                 FROM tav2_bq.ticker_financial AS t WHERE t.ticker='{tk}' ORDER BY t.time""")
        d["time"]=pd.to_datetime(d["time"])
        d=d.merge(B[["q","brent_avg","brent_end","oil_qoq","oil_yoy"]],
                  left_on="quarter",right_on="q",how="left")
        return d

    # =========================================================
    # (1) BSR inventory vs crack
    # =========================================================
    bsr=getfin("BSR").dropna(subset=["GPM_P0","brent_avg"]).copy()
    bsr["GP_bn"]=bsr["Revenue_P0"]*bsr["GPM_P0"]/1e9
    P("# BSR — tach LAI/LO TON KHO khoi BIEN LOC (crack)")
    P("oil_qoq = % thay doi gia dau (cuoi quy vs cuoi quy truoc) = dong luc ton kho.")
    P("brent_avg = mat bang gia (proxy moi truong crack).")
    P("")
    # regression GPM ~ a + b1*brent_avg + b2*oil_qoq
    d=bsr.dropna(subset=["oil_qoq"])
    X=np.column_stack([np.ones(len(d)),d["brent_avg"].values,d["oil_qoq"].values])
    y=d["GPM_P0"].values
    beta,_,_,_=np.linalg.lstsq(X,y,rcond=None)
    yhat=X@beta; r2=1-np.sum((y-yhat)**2)/np.sum((y-y.mean())**2)
    # partial R2: drop each regressor
    def partial(cols):
        Xs=np.column_stack([np.ones(len(d))]+[d[c].values for c in cols])
        b,_,_,_=np.linalg.lstsq(Xs,y,rcond=None); yh=Xs@b
        return 1-np.sum((y-yh)**2)/np.sum((y-y.mean())**2)
    r2_lvl=partial(["brent_avg"]); r2_inv=partial(["oil_qoq"])
    P(f"GPM ~ {beta[0]:+.3f} {beta[1]:+.5f}*brent_avg {beta[2]:+.3f}*oil_qoq   (R2 tong={r2:.2f}, n={len(d)})")
    P(f"  chi LEVEL (crack proxy):     R2={r2_lvl:.2f}")
    P(f"  chi OIL_QOQ (ton kho):       R2={r2_inv:.2f}")
    P(f"  -> he so oil_qoq {beta[2]:+.3f}: dau +10% trong quy => GPM {beta[2]*0.10*100:+.1f}pp")
    P("")
    # bucket by oil direction
    d["dir"]=pd.cut(d["oil_qoq"],[-1,-0.10,0.10,5],labels=["DAU GIAM >10%","DI NGANG","DAU TANG >10%"])
    P(f"{'huong dau trong quy':<16}{'nQ':>4}{'GPM_tb':>9}{'NPM_tb':>9}{'NP_tb(bn)':>11}{'GP_tb(bn)':>11}{'%quy LO':>9}")
    for lab in ["DAU GIAM >10%","DI NGANG","DAU TANG >10%"]:
        g=d[d["dir"]==lab]
        if len(g)==0: continue
        lossrate=(g["NP_P0"]<0).mean()*100
        P(f"{lab:<16}{len(g):>4}{g['GPM_P0'].mean()*100:>8.1f}%{g['NPM_P0'].mean()*100:>8.1f}%"
          f"{g['NP_P0'].mean()/1e9:>11.0f}{g['GP_bn'].mean():>11.0f}{lossrate:>8.0f}%")
    P("-> CRACK (level brent_avg) chi phoi BIEN goc (R2 0.56); HUONG dau (ton kho) chi phoi DUOI:")
    P("   moi quy dau SAP >10% deu ke lo/sat lo (NRV trich lap ton kho), dau VOT = lai dot bien.")
    P("")
    P("Cac quy cuc tri (theo oil_qoq):")
    P(f"{'quarter':<9}{'oil_qoq':>9}{'brent_avg':>10}{'GPM':>7}{'NP_bn':>8}")
    ext=pd.concat([d.nsmallest(4,"oil_qoq"),d.nlargest(4,"oil_qoq")]).sort_values("q")
    for _,r in ext.iterrows():
        P(f"{r['quarter']:<9}{r['oil_qoq']*100:>+8.0f}%{r['brent_avg']:>10.0f}{r['GPM_P0']*100:>6.0f}%{r['NP_P0']/1e9:>8.0f}")
    P("")
    # estimate inventory-attributable NP swing (VND) for extreme quarters
    P("Uoc luong PHAN NP do ton kho (~ b2*oil_qoq*Revenue, gop xap xi):")
    for _,r in ext.iterrows():
        inv=beta[2]*r["oil_qoq"]*r["Revenue_P0"]/1e9
        P(f"  {r['quarter']}: oil {r['oil_qoq']*100:+.0f}% -> ~{inv:+.0f} bn (NP thuc {r['NP_P0']/1e9:+.0f} bn)")
    P("")

    # =========================================================
    # (2) PVD backlog lag
    # =========================================================
    pvd=getfin("PVD")
    pvd=pvd[pvd["time"]>="2013-10-01"].dropna(subset=["GPM_P0","brent_avg"]).reset_index(drop=True)
    P("# PVD — do TRE backlog theo chu ky gian khoan")
    P("Cross-correlation: corr( metric[t], Brent_avg[t-lag] ) cho lag 0..8 quy.")
    P("Lag dinh = so quy loi nhuan PVD tre sau gia dau (do hop dong day-rate cham).")
    P("")
    P(f"{'lag(quy)':<9}"+ "".join(f"{L:>6}" for L in range(0,9)))
    for metric,lab in [("GPM_P0","GPM"),("NPM_P0","NPM"),("NP_P0","NP"),("Revenue_P0","Rev")]:
        ser=pvd[metric].values; oil=pvd["brent_avg"].values
        row=[]
        for L in range(0,9):
            if L==0: a,b=ser,oil
            else: a,b=ser[L:],oil[:-L]
            m=np.isfinite(a)&np.isfinite(b)
            row.append(np.corrcoef(a[m],b[m])[0,1] if m.sum()>10 else np.nan)
        best=int(np.nanargmax(row))
        P(f"{lab:<9}"+"".join(f"{v:>+6.2f}" for v in row)+f"   <- dinh lag {best}Q")
    P("")
    # per-cycle turning points (manual oil cycle anchors) vs PVD GPM turns
    P("## Theo tung chu ky (GPM la tin hieu sach nhat, NP nhieu boi FX/JV)")
    P("Dau xoay (avg) vs PVD GPM xoay:")
    cyc=[
     ("Dau DINH 2014Q2 (~111) -> PVD GPM dinh","2014Q2 oil peak","PVD GPM ~20% giu den 2015Q3, roi do"),
     ("Dau DAY 2016Q1 (~34)  -> PVD GPM DAY","2016Q1 oil trough","PVD GPM DAY 2017Q1 (-2%) ~ tre 4Q; lo 2017Q1/2018Q1"),
     ("Dau HOI 2016-2018 (34->81)","oil recovers ~2yr","PVD GPM chi nhuc nhich 2019 (~13%) ~ tre 8-12Q"),
     ("Dau SAP COVID 2020Q2 (~29)","2020 crash","PVD GPM ep ve 8% 2020-2022, lo rong 2022"),
     ("Dau HOI 2020Q2->2022Q2 (29->122)","oil recovers","PVD GPM PHUC HOI manh tu 2023Q2 (18->24%) ~ tre 8-12Q"),
     ("Dau VOT 2026Q1 (66->103)","2026 spike","PVD GPM 2026Q1 chi 19% (chua phan anh) -> ky vong hich 2026H2-2027"),
    ]
    for a,b,c in cyc: P(f"- {a}\n    {c}")
    P("")
    # show PVD GPM trajectory vs brent for visual
    P("Quy te (PVD GPM vs Brent avg, 2014+):")
    P(f"{'quarter':<9}{'brent_avg':>10}{'GPM':>7}{'NPM':>7}{'NP_bn':>8}")
    for _,r in pvd[pvd['time']>='2014-01-01'].iloc[::1].iterrows():
        pass
    show=pvd[pvd['time']>='2014-01-01']
    for _,r in show.iterrows():
        P(f"{r['quarter']:<9}{r['brent_avg']:>10.0f}{r['GPM_P0']*100:>6.0f}%{r['NPM_P0']*100:>6.0f}%{r['NP_P0']/1e9:>8.0f}")

    out=os.path.join(WORKDIR,"data","oil_bsr_pvd_deepdive.md")
    with open(out,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    P(f"\nSaved {out}")

if __name__=="__main__": main()
