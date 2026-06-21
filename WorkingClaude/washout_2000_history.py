#!/usr/bin/env python3
"""washout_2000_history.py — sharp vs grind washouts across FULL history + 60-session recovery.
Washout = broad oversold breadth: Breadth_MA20 <= 22% (% stocks above 20d MA), calibrated to
reproduce the 12 known prune-oversold>=40% events (2014+). Real cross-sectional breadth exists
2004+; 2000-2003 has only VNINDEX_RSI (RSI<=30 proxy, lower confidence). Recovery = forward
60-session VNINDEX return (index-level; no 8L basket pre-2014)."""
import warnings; warnings.filterwarnings("ignore")
import os, sys
try: sys.stdout.reconfigure(encoding="utf-8")
except Exception: pass
import numpy as np, pandas as pd
W=r"/home/trido/thanhdt/WorkingClaude"
v=pd.read_csv(os.path.join(W,"VNINDEX.csv"),parse_dates=["time"]).sort_values("time").reset_index(drop=True)
v=v[["time","Close","Breadth_MA20","VNINDEX_RSI"]].copy()
C=v["Close"].values; N=len(v)
DECL=20; FWD=60; GRIND_MAX=90

def analyze(mask, label, src):
    idxs=np.where(mask.values)[0]
    # de-cluster: new episode if >=DECL trading days since last washout day
    eps=[]
    for k in idxs:
        if not eps or k-eps[-1][-1] >= DECL: eps.append([k])
        else: eps[-1].append(k)
    rows=[]
    prev_start=None
    for e in eps:
        i0=e[0]
        grind = prev_start is not None and (i0-prev_start) <= GRIND_MAX
        prev_start=i0
        fwd = C[min(i0+FWD,N-1)]/C[i0]-1
        seg=C[i0:min(i0+90,N)]; tmin=int(np.argmin(seg)); further=seg[tmin]/C[i0]-1
        censored = i0+FWD>=N
        rows.append(dict(date=v["time"].iloc[i0].date(), yr=v["time"].iloc[i0].year,
            br20=round(v["Breadth_MA20"].iloc[i0]*100) if pd.notna(v["Breadth_MA20"].iloc[i0]) else None,
            rsi=round(v["VNINDEX_RSI"].iloc[i0]*100) if pd.notna(v["VNINDEX_RSI"].iloc[i0]) else None,
            type="GRIND" if grind else "SHARP",
            fwd60=round(fwd*100,1) if not censored else None,
            days_to_bottom=tmin, further_drop=round(further*100,1), src=src))
    R=pd.DataFrame(rows)
    print(f"\n{'='*78}\n{label}  ({len(R)} washout episodes)\n{'='*78}")
    print(R.to_string(index=False))
    rr=R.dropna(subset=["fwd60"])
    print(f"\n  RECOVERY after 60 sessions (excl. censored):")
    for lab,g in rr.groupby("type"):
        f=g["fwd60"]
        print(f"    {lab:<6} n={len(g):2d} | mean {f.mean():6.1f}% | median {f.median():6.1f}% | win {100*(f>0).mean():3.0f}% "
              f"| further_drop med {g['further_drop'].median():6.1f}% | days_to_bottom med {g['days_to_bottom'].median():.0f}")
    return R

# Primary: real breadth, 2004+
v04=v[v["time"]>="2004-01-01"]
mask_br = v["Breadth_MA20"]<=0.22
mask_br &= v["time"]>="2004-01-01"
R1=analyze(mask_br, "PRIMARY — real breadth (Breadth_MA20<=22%), 2004-2026", "breadth")

# Secondary: RSI proxy for 2000-2003 (no breadth then)
mask_rsi = (v["VNINDEX_RSI"]<=0.30) & (v["time"]<"2004-01-01")
R2=analyze(mask_rsi, "SECONDARY — VNINDEX RSI<=30 proxy, 2000-2003 only (lower confidence)", "rsi")

print("\n"+"#"*78)
print("SHARP vs GRIND — pooled 2004+ (real breadth):")
rr=R1.dropna(subset=["fwd60"])
for lab,g in rr.groupby("type"):
    f=g["fwd60"]; print(f"  {lab}: n={len(g)} recovery60 mean {f.mean():.1f}% / median {f.median():.1f}% / win {100*(f>0).mean():.0f}%")
print("\nGrind episodes (the dangerous repeats):")
print(R1[R1.type=='GRIND'][['date','yr','br20','fwd60','further_drop']].to_string(index=False))
