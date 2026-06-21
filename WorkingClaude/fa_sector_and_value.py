#!/usr/bin/env python3
"""
fa_sector_and_value.py
======================
Rounds out directions #1 (bank sub-model) and #4 (Quality×Value).

#1 — Does the generic FA composite work WORSE for financials (ICB sector 8)?
     If IC for sector-8 << IC for the rest, that empirically confirms banks need a
     dedicated sub-model (generic ROIC/GPM/CF_OA axes are meaningless for banks).
     (The codebase already hacks a sector-8 override in recommend_holistic.py.)

#4 — valuation axis has NEGATIVE IC overall. Test whether value works CONDITIONALLY:
     within quality terciles, does cheap beat expensive? And a quality×cheapness 2x2
     forward-return grid. If cheap only wins among high-quality names, that argues for
     a Greenblatt-style interaction (quality-gated value) rather than an additive axis.
"""
import warnings; warnings.filterwarnings("ignore")
import sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import os
import numpy as np, pandas as pd

WORKDIR=r"/home/trido/thanhdt/WorkingClaude"

def ic(x,y):
    x=pd.Series(np.asarray(x,float)); y=pd.Series(np.asarray(y,float))
    m=(~x.isna())&(~y.isna())
    if m.sum()<30: return (np.nan,int(m.sum()))
    return (float(np.corrcoef(x[m].rank(),y[m].rank())[0,1]),int(m.sum()))

def main():
    lines=[]; P=lambda s="":(print(s),lines.append(s))
    df=pd.read_csv(os.path.join(WORKDIR,"fundamental_rating_all.csv"))
    df["time"]=pd.to_datetime(df["time"])
    df=df.dropna(subset=["profit_3M"]).copy()
    df["sector"]=(df["ICB_Code"]//1000).astype("Int64")

    P("# Directions #1 (bank gap) and #4 (conditional value)")
    P("")
    # ── #1: per-sector IC of total_score ──────────────────────────────────
    P("## #1 — FA composite IC by ICB sector (does it fail for financials?)")
    P("")
    SEC={0:"?",1:"O&G",2:"Materials",3:"Industrials",4:"ConsGoods",
         5:"Health",6:"ConsSvc",7:"Telecom",8:"Financials",9:"Tech/Utl"}
    P(f"{'sector':<14}{'N':>7}{'IC_total':>10}{'IC_qual':>9}{'IC_val':>9}{'med_p3M':>9}")
    P("-"*58)
    for s in sorted([x for x in df["sector"].dropna().unique()]):
        g=df[df["sector"]==s]
        if len(g)<100: continue
        rt,_=ic(g["total_score"],g["profit_3M"])
        rq,_=ic(g["score_quality"],g["profit_3M"])
        rv,_=ic(g["score_valuation"],g["profit_3M"])
        nm=SEC.get(int(s),str(int(s)))
        P(f"{nm:<14}{len(g):>7,}{rt:>+10.4f}{rq:>+9.4f}{rv:>+9.4f}{g['profit_3M'].median():>8.2f}%")
    fin=df[df["sector"]==8]; rest=df[df["sector"]!=8]
    rf,_=ic(fin["total_score"],fin["profit_3M"]); rr,_=ic(rest["total_score"],rest["profit_3M"])
    P("-"*58)
    P(f"{'FINANCIALS':<14}{len(fin):>7,}{rf:>+10.4f}")
    P(f"{'NON-FIN':<14}{len(rest):>7,}{rr:>+10.4f}")
    P(f"  → gap = {rf-rr:+.4f} (negative = FA composite weaker for banks/financials)")
    P("")

    # ── #4: conditional value within quality terciles ─────────────────────
    P("## #4 — Does value work CONDITIONALLY? (valuation IC within quality terciles)")
    P("")
    df["q_ter"]=pd.qcut(df["score_quality"].rank(method="first"),3,labels=["LowQ","MidQ","HighQ"])
    P(f"{'quality tercile':<16}{'IC_valuation':>14}{'N':>8}")
    P("-"*38)
    for t in ["LowQ","MidQ","HighQ"]:
        g=df[df["q_ter"]==t]
        rv,n=ic(g["score_valuation"],g["profit_3M"])
        P(f"{t:<16}{rv:>+14.4f}{n:>8,}")
    P("")
    P("(valuation axis: higher score = cheaper after the INV sign-flip in fundamental_rating.")
    P(" positive IC within a tercile = cheap predicts higher return there.)")
    P("")
    # 2x2 quality x cheapness forward-return grid
    P("### Quality × Cheapness 2×2 (median profit_3M)")
    df["q_hi"]=df["score_quality"]>=df["score_quality"].median()
    df["v_hi"]=df["score_valuation"]>=df["score_valuation"].median()  # high = cheap
    P(f"{'':<14}{'Expensive':>12}{'Cheap':>12}")
    for qh,qlab in [(True,"HighQuality"),(False,"LowQuality")]:
        row=f"{qlab:<14}"
        for vh in [False,True]:
            g=df[(df["q_hi"]==qh)&(df["v_hi"]==vh)]["profit_3M"]
            row+=f"{g.median():>11.2f}%" if len(g) else f"{'·':>12}"
        P(row)
    P("")
    P("Greenblatt hypothesis: 'HighQuality+Cheap' should be best; 'LowQuality+Cheap'")
    P("(the value trap) should be worst or near-worst — explaining valuation's negative")
    P("standalone IC (dominated by cheap junk).")
    P("")
    with open(os.path.join(WORKDIR,"data","fa_sector_value.md"),"w",encoding="utf-8") as fh:
        fh.write("\n".join(lines))
    P("Saved data/fa_sector_value.md")

if __name__=="__main__":
    main()
