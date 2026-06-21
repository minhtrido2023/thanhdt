#!/usr/bin/env python3
"""
oil_price_supplement.py — isolate the oil-specific price signal
===============================================================
The naive monthly oil-beta is tiny (R2~0) because VNINDEX beta dominates.
Three sharper lenses:
  (A) 2-factor monthly: stock_ret ~ a + bM*VNINDEX_ret + bO*Brent_ret
      -> bO = MARGINAL oil beta after stripping market; tells the oil-specific move.
  (B) Quarterly horizon: stock_qret ~ Brent_qret (less noise than monthly).
  (C) Oil-shock event study: months where |Brent move|>=10% -> mean & spread of
      stock move by group (does volatility AMPLIFY in oil-shock months?).
Output: data/oil_price_supplement.md
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
GROUPS=[
 ("UPSTREAM (573)", ["PVD","PVS","PVB","PVC"]),
 ("REFINE/DISTRIB (533)", ["BSR","PLX","OIL"]),
 ("GAS (7573)", ["GAS","PGS","CNG","PGD","PGC","PVG"]),
 ("FERT/CHEM (1357)", ["DPM","DCM","DGC","CSV"]),
 ("TRANSPORT (2773)", ["PVT","VIP","VTO","GSP","PVP"]),
]
ALL=[t for _,g in GROUPS for t in g]
def bq(sql):
    with tempfile.NamedTemporaryFile(mode="w",suffix=".sql",delete=False,encoding="utf-8") as f:
        f.write(sql); tmp=f.name
    try:
        r=subprocess.run(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
                         f'--project_id={PROJECT} --format=csv --max_rows=5000000',
                         capture_output=True,text=True,timeout=600,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    if r.returncode!=0 or not r.stdout.strip(): raise RuntimeError(r.stderr[:500])
    return pd.read_csv(StringIO(r.stdout.strip()))

def two_factor(y,xm,xo):
    m=np.isfinite(y)&np.isfinite(xm)&np.isfinite(xo)
    y=y[m]; xm=xm[m]; xo=xo[m]; n=len(y)
    if n<24: return (np.nan,np.nan,np.nan,n)
    X=np.column_stack([np.ones(n),xm,xo])
    beta,_,_,_=np.linalg.lstsq(X,y,rcond=None)
    yhat=X@beta; r2=1-np.sum((y-yhat)**2)/np.sum((y-y.mean())**2)
    return (beta[1],beta[2],r2,n)  # bM, bO, r2, n

def simple_beta(y,x):
    m=np.isfinite(y)&np.isfinite(x); y=y[m]; x=x[m]; n=len(y)
    if n<8: return (np.nan,np.nan,n)
    b,a=np.polyfit(x,y,1); yhat=a+b*x
    r2=1-np.sum((y-yhat)**2)/np.sum((y-y.mean())**2)
    return (b,r2,n)

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    tks="','".join(ALL)
    br=pd.read_csv(os.path.join(WORKDIR,"data","brent_monthly_full.csv"))
    br["month"]=pd.PeriodIndex(br["month"],freq="M"); br=br.set_index("month").sort_index()
    br["bret"]=br["brent"].pct_change()

    # monthly close + VNINDEX (last trading day per month)
    px=bq(f"""
      WITH m AS (
        SELECT t.ticker, DATE_TRUNC(t.time,MONTH) AS mo, t.time, t.Close, t.VNINDEX,
          ROW_NUMBER() OVER (PARTITION BY t.ticker,DATE_TRUNC(t.time,MONTH) ORDER BY t.time DESC) rn
        FROM tav2_bq.ticker AS t WHERE t.ticker IN ('{tks}') AND t.Close IS NOT NULL )
      SELECT ticker, mo, Close, VNINDEX FROM m WHERE rn=1 ORDER BY ticker, mo""")
    px["month"]=pd.PeriodIndex(pd.to_datetime(px["mo"]),freq="M")
    px=px.sort_values(["ticker","month"])
    px["sret"]=px.groupby("ticker")["Close"].pct_change()
    px["vret"]=px.groupby("ticker")["VNINDEX"].pct_change()
    px=px.merge(br[["brent","bret"]].reset_index(),on="month",how="left")

    P("# Tin hieu gia DAU rieng (loc beta thi truong) + bien dong")
    P("")
    P("## (A) Oil beta 2 NHAN TO: stock_ret ~ market(VNINDEX) + Brent (monthly)")
    P("bM = beta thi truong, bO = beta dau RIENG sau khi loc market. R2 = giai thich tong.")
    P("")
    P(f"{'tk':<6}{'bMarket':>9}{'bOil':>8}{'R2':>7}{'n':>5}   {'group'}")
    rowsA=[]
    for gname,gtk in GROUPS:
        for tk in gtk:
            d=px[px["ticker"]==tk]
            bM,bO,r2,n=two_factor(d["sret"].values,d["vret"].values,d["bret"].values)
            if not np.isfinite(bO): continue
            P(f"{tk:<6}{bM:>9.2f}{bO:>8.2f}{r2:>7.2f}{n:>5}   {gname}")
            rowsA.append((gname,tk,bM,bO,r2))
        P("")
    A=pd.DataFrame(rowsA,columns=["grp","tk","bM","bO","r2"])
    P("Group median:")
    P(f"{'group':<22}{'bMarket':>9}{'bOil':>8}")
    for gname,_ in GROUPS:
        a=A[A["grp"]==gname]
        if len(a): P(f"{gname:<22}{a['bM'].median():>9.2f}{a['bO'].median():>8.2f}")
    P("")

    # (B) quarterly returns vs quarterly brent return
    px["q"]=px["month"].dt.asfreq("Q")
    qpx=px.groupby(["ticker","q"]).agg(Close=("Close","last")).reset_index()
    qpx["sqret"]=qpx.groupby("ticker")["Close"].pct_change()
    brq=br["brent"].groupby(br.index.asfreq("Q")).mean()
    brqr=brq.pct_change().rename("bqret").reset_index().rename(columns={"month":"q"})
    qpx=qpx.merge(brqr,on="q",how="left")
    P("## (B) Horizon QUY: stock_qret ~ Brent_qret (it nhieu hon monthly)")
    P(f"{'tk':<6}{'beta_q':>8}{'R2':>7}{'nQ':>5}   group")
    rowsB=[]
    for gname,gtk in GROUPS:
        for tk in gtk:
            d=qpx[qpx["ticker"]==tk]
            b,r2,n=simple_beta(d["sqret"].values,d["bqret"].values)
            if not np.isfinite(b): continue
            P(f"{tk:<6}{b:>8.2f}{r2:>7.2f}{n:>5}   {gname}")
            rowsB.append((gname,tk,b,r2))
        P("")
    B=pd.DataFrame(rowsB,columns=["grp","tk","bq","r2"])
    P("Group median quarterly oil beta:")
    for gname,_ in GROUPS:
        b=B[B["grp"]==gname]
        if len(b): P(f"  {gname:<22}{b['bq'].median():>+.2f}  (R2 {b['r2'].median():.2f})")
    P("")

    # (C) oil-shock event study
    br_sh=br.copy(); br_sh["shock"]=br_sh["bret"].abs()>=0.10
    sh_months=set(br_sh.index[br_sh["shock"]])
    P(f"## (C) Event study — {len(sh_months)} thang co |Brent move|>=10%")
    P("So sanh do lon & PHAN TAN buoc gia co phieu trong thang soc dau vs thang thuong.")
    P(f"{'group':<22}{'mean|r|_shock':>14}{'mean|r|_calm':>13}{'amplify x':>11}{'dir_corr':>9}")
    rowsC=[]
    for gname,gtk in GROUPS:
        d=px[px["ticker"].isin(gtk)].dropna(subset=["sret","bret"])
        d["shock"]=d["month"].isin(sh_months)
        ash=d.loc[d["shock"],"sret"].abs().mean()
        acl=d.loc[~d["shock"],"sret"].abs().mean()
        # directional: in shock months, does stock move same sign as oil?
        dd=d[d["shock"]]
        dir_corr=np.sign(dd["sret"]).eq(np.sign(dd["bret"])).mean()
        amp=ash/acl if acl>0 else np.nan
        P(f"{gname:<22}{ash*100:>13.1f}%{acl*100:>12.1f}%{amp:>11.2f}{dir_corr:>9.2f}")
        rowsC.append((gname,ash,acl,amp,dir_corr))
    P("")
    P("amplify x>1 = co phieu bien dong manh hon binh thuong trong thang soc dau;")
    P("dir_corr>0.5 = co phieu nghieng theo HUONG cu soc dau (cung chieu).")

    out=os.path.join(WORKDIR,"data","oil_price_supplement.md")
    with open(out,"w",encoding="utf-8") as f: f.write("\n".join(lines))
    P(f"\nSaved {out}")

if __name__=="__main__": main()
