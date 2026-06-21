#!/usr/bin/env python3
"""test_grind_arm_b.py — does grind arm (b) [breadth still falling] actually discriminate
sharp vs grind, or is it TRUE at every washout (uninformative, as the user suspects)?"""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
D=pd.read_csv(os.path.join(W,"data","daily_comovement_dt5g.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
M=pd.read_csv(os.path.join(W,"data","washout_master_table.csv"),parse_dates=["date"])
b200=D.set_index("time")["pct_above_ma200"]; dates=D["time"].tolist()
def at(d,lag=0):
    i=D.index[D["time"]==pd.Timestamp(d)][0]; j=max(0,i-lag); return float(D["pct_above_ma200"].iloc[j])
rows=[]
for _,r in M.iterrows():
    b0=at(r["date"]); b20=at(r["date"],20); delta=b0-b20
    rows.append(dict(date=r["date"].date(), regime=r["regime"],
        above_ma200=round(b0*100,1), chg20=round(delta*100,1),
        arm_b=delta< -0.02, arm_a_grind=str(r["type"]).startswith("GRIND"),
        basket60=r["basket60"], win=r["basket60"]>0))
T=pd.DataFrame(rows)
print("Per-washout: arm(b) = breadth (% above MA200) still falling >2pp vs 20 td before")
print(T.to_string(index=False))
print(f"\narm(b) TRUE at {T.arm_b.sum()}/{len(T)} washouts  ({100*T.arm_b.mean():.0f}%)")
print(f"  -> if ~all TRUE, it is non-discriminating (user's hypothesis)")
print("\nDoes arm(b) separate winners from losers?")
for lab,g in T.groupby("arm_b"):
    b=g["basket60"].dropna()
    print(f"  arm_b={str(lab):<5} n={len(g)} | basket60 mean {b.mean():5.1f}% / win {100*(b>0).mean():3.0f}% | dates {list(g.date)}")
print("\nFor contrast — arm(a) repeat-washout separation:")
for lab,g in T.groupby("arm_a_grind"):
    b=g["basket60"].dropna()
    print(f"  arm_a={str(lab):<5} n={len(g)} | basket60 mean {b.mean():5.1f}% / win {100*(b>0).mean():3.0f}%")
# overlap: does b add anything beyond a?
only_b = T[T.arm_b & ~T.arm_a_grind]
print(f"\nWashouts flagged by (b) but NOT (a) [what b uniquely adds]: {len(only_b)}")
if len(only_b):
    bb=only_b["basket60"].dropna()
    print(only_b[["date","regime","above_ma200","chg20","basket60","win"]].to_string(index=False))
    print(f"  their outcome: mean {bb.mean():.1f}% / win {100*(bb>0).mean():.0f}%  "
          f"-> if these are WINNERS, (b) wrongly penalizes them")
