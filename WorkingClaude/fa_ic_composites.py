#!/usr/bin/env python3
"""
fa_ic_composites.py
===================
Follow-up to fa_ic_audit.py. The audit found health (IC -0.039) and valuation
(IC -0.028) have NEGATIVE predictive power yet carry 18% combined weight.
Test whether dropping/re-weighting them improves the composite IC — with an
IS (2014-2019) / OOS (2020+) split so the conclusion isn't in-sample noise.

Composites compared (all rank-mean of axis percentile scores):
  CUR7    : current hand weights 18/18/18/15/13/8/10
  EW7     : equal weight all 7
  EW5     : equal weight, DROP health + valuation
  CORE4   : equal weight quality+stability+cash+shareholder (drop growth too — growth low IC)
  ICW     : sign-aware: include only positive-IC axes, weight ∝ IS-IC (fit on IS only)
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os, subprocess, tempfile
from io import StringIO
import numpy as np, pandas as pd

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
PROJECT = "lithe-record-440915-m9"
BQ_BIN  = r"bq"
AXES = ["quality","stability","cash","shareholder","growth","health","valuation"]
CURW = {"quality":.18,"stability":.18,"cash":.18,"shareholder":.15,"growth":.13,"health":.08,"valuation":.10}


def bq_query(sql):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".sql", delete=False, encoding="utf-8") as f:
        f.write(sql); tmp=f.name
    try:
        cmd=(f'type "{tmp}" | "{BQ_BIN}" query --use_legacy_sql=false '
             f'--project_id={PROJECT} --format=csv --max_rows=10000000')
        r=subprocess.run(cmd,capture_output=True,text=True,timeout=900,shell=True)
    finally:
        try: os.unlink(tmp)
        except: pass
    return pd.read_csv(StringIO(r.stdout.strip()))


def ic(x,y):
    x=pd.Series(np.asarray(x,float)); y=pd.Series(np.asarray(y,float))
    m=(~x.isna())&(~y.isna())
    if m.sum()<30: return np.nan
    return float(np.corrcoef(x[m].rank(),y[m].rank())[0,1])


def composite(df, weights):
    cols=[f"score_{a}" for a in weights]; w=np.array([weights[a] for a in weights])
    return (df[cols].values*w).sum(axis=1)/w.sum()


def main():
    df=pd.read_csv(os.path.join(WORKDIR,"data/fundamental_rating_all.csv"))
    df["time"]=pd.to_datetime(df["time"])
    df=df.dropna(subset=["profit_3M"]).copy()
    IS=df[df["time"]<"2020-01-01"]; OOS=df[df["time"]>="2020-01-01"]
    print(f"IS 2014-19 n={len(IS):,} | OOS 2020+ n={len(OOS):,}\n")

    # IS-fit IC weights (positive-IC axes only)
    is_ic={a:ic(IS[f"score_{a}"],IS["profit_3M"]) for a in AXES}
    pos={a:v for a,v in is_ic.items() if v>0}
    print("IS per-axis IC:  "+"  ".join(f"{a[:4]}={is_ic[a]:+.3f}" for a in AXES))
    print(f"Positive-IC axes (used by ICW): {list(pos)}\n")

    comps={
        "CUR7":  CURW,
        "EW7":   {a:1 for a in AXES},
        "EW5":   {a:1 for a in AXES if a not in("health","valuation")},
        "CORE4": {a:1 for a in ("quality","stability","cash","shareholder")},
        "ICW":   pos,
    }
    print(f"{'composite':<8}{'IS_IC':>9}{'OOS_IC':>9}{'ALL_IC':>9}   axes")
    print("-"*60)
    for name,w in comps.items():
        df["_c"]=composite(df,w); IS["_c"]=composite(IS,w); OOS["_c"]=composite(OOS,w)
        print(f"{name:<8}{ic(IS['_c'],IS['profit_3M']):>+9.4f}"
              f"{ic(OOS['_c'],OOS['profit_3M']):>+9.4f}"
              f"{ic(df['_c'],df['profit_3M']):>+9.4f}   {len(w)}ax: {','.join(a[:4] for a in w)}")
    print()
    # Decile spread (top - bottom decile median profit_3M) for best vs current, OOS
    print("OOS decile spread (top10% − bottom10% median profit_3M):")
    for name in ["CUR7","EW5","CORE4","ICW"]:
        w=comps[name]; OOS["_c"]=composite(OOS,w)
        d=OOS.copy(); d["dec"]=pd.qcut(d["_c"].rank(method="first"),10,labels=False)
        top=d[d["dec"]==9]["profit_3M"].median(); bot=d[d["dec"]==0]["profit_3M"].median()
        print(f"  {name:<8} top={top:+6.2f}%  bot={bot:+6.2f}%  spread={top-bot:+6.2f}pp")


if __name__=="__main__":
    main()
