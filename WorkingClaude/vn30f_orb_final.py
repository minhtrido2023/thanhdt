# -*- coding: utf-8 -*-
"""
vn30f_orb_final.py
==================
Khep vong kiem dinh ORB:
 (A) VOL-TARGET position sizing (thay vai tro stop): size_t = clip(target/vol_{t-1}, lo, hi),
     vol = trailing 10-phien std cua intraday move; target=median -> avg size ~1 (so sanh fixed-1).
 (B) SLIPPAGE thuc te o fill: tick=0.1d (~0.5bps@1940). entry/exit fill lech slip_ticks
     theo huong xau + fee brokerage. Sensitivity slip 0/1/2/3 tick.
 (C) Config cuoi (vol-target + slip 2tick + fee) -> walk-forward theo nam.
Base rule: sign(OR 09:00-09:30), giu den 14:30, KHONG stop, |OR|>=0.2%.
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD = r"/home/trido/thanhdt/WorkingClaude"
TICK = 0.1          # VN30F tick size (diem)
FEE  = 0.00006      # brokerage+tax round-trip ~0.6bps

df = pd.read_csv(WD+"/data/vn30f1m_1min.csv"); df["time"]=pd.to_datetime(df["time"])
df["date"]=df["time"].dt.date; df["hm"]=df["time"].dt.strftime("%H:%M")

days=[]
for d,g in df.groupby("date"):
    g=g.sort_values("time").reset_index(drop=True)
    if len(g)<150: continue
    op=g[g["hm"]<="09:30"]
    if len(op)<10: continue
    entry=op["close"].iloc[-1]
    seg=g[(g["hm"]>"09:30")&(g["hm"]<="14:30")]
    if len(seg)==0: continue
    exitpx=seg["close"].iloc[-1]
    days.append({"date":d,"or_ret":entry/g["close"].iloc[0]-1,"entry":entry,"exit":exitpx})
D=pd.DataFrame(days)
D["sig"]=np.sign(D["or_ret"])
D["move"]=D["exit"]/D["entry"]-1                       # raw intraday move (long)
# trailing vol of the SIGNED strategy move (causal, shift 1)
D["stratmove"]=D["sig"]*D["move"]
D["vol10"]=D["stratmove"].rolling(10).std().shift(1)
TARGET=float(D["vol10"].median())

def run(slip_ticks=2, vol_target=False, min_or=0.002, lo=0.3, hi=2.5):
    sub=D[D["or_ret"].abs()>=min_or].copy()
    recs=[]
    for _,r in sub.iterrows():
        sig=r["sig"]
        # slippage: vao xau hon, ra xau hon
        ef=r["entry"]+sig*slip_ticks*TICK
        xf=r["exit"] -sig*slip_ticks*TICK
        gross=sig*(xf/ef-1)
        if vol_target and not np.isnan(r["vol10"]) and r["vol10"]>0:
            size=min(hi,max(lo, TARGET/r["vol10"]))
        else:
            size=1.0
        pnl=size*(gross-FEE)
        recs.append({"date":r["date"],"pnl":pnl,"size":size})
    return pd.DataFrame(recs)

def stat(r):
    n=len(r); mean=r["pnl"].mean(); sd=r["pnl"].std()
    sh=mean/sd*np.sqrt(252) if sd>0 else 0
    nav=(1+r["pnl"]).cumprod(); mdd=(nav/nav.cummax()-1).min()
    return n,(r["pnl"]>0).mean(),mean,sh,(nav.iloc[-1]-1),mdd

print(f"median trailing-vol (target) = {TARGET*1e4:.1f}bps/day | avg size kiem tra ben duoi")
# ===== A) SLIPPAGE SENSITIVITY: fixed vs vol-target =====
print("\n"+"="*86); print("  A+B) SLIPPAGE x SIZING  (|OR|>=0.2%, exit 14:30, no stop, fee 0.6bps)"); print("="*86)
print(f"  {'sizing':<12}{'slip':<7}{'n':>5}{'WR':>7}{'mean/d':>9}{'Sharpe':>8}{'MaxDD':>8}{'cum':>8}{'avgSize':>8}")
print("  "+"-"*72)
for vt,lbl in [(False,"fixed-1"),(True,"vol-target")]:
    for slip in [0,1,2,3]:
        r=run(slip,vt)
        n,wr,mn,sh,cum,mdd=stat(r)
        print(f"  {lbl:<12}{slip}tick {n:>6}{wr*100:>6.1f}%{mn*1e4:>+8.2f}{sh:>8.2f}{mdd*100:>+7.1f}%{cum*100:>+7.1f}%{r['size'].mean():>8.2f}")

# ===== C) WALK-FORWARD: config cuoi (vol-target, slip 2tick, fee 0.6bps) =====
print("\n"+"="*86); print("  C) WALK-FORWARD config cuoi (vol-target + slip 2tick + fee 0.6bps, |OR|>=0.2%)"); print("="*86)
r=run(2,True); r["yr"]=pd.to_datetime(r["date"]).dt.year
print(f"  {'Nam':<8}{'n':>5}{'WR':>7}{'mean/d':>9}{'Sharpe':>8}{'MaxDD':>8}{'cum':>8}")
print("  "+"-"*56)
for yr,gg in r.groupby("yr"):
    n,wr,mn,sh,cum,mdd=stat(gg)
    print(f"  {yr:<8}{n:>5}{wr*100:>6.1f}%{mn*1e4:>+8.2f}{sh:>8.2f}{mdd*100:>+7.1f}%{cum*100:>+7.1f}%")
n,wr,mn,sh,cum,mdd=stat(r); print("  "+"-"*56)
print(f"  {'TONG':<8}{n:>5}{wr*100:>6.1f}%{mn*1e4:>+8.2f}{sh:>8.2f}{mdd*100:>+7.1f}%{cum*100:>+7.1f}%")

# compare fixed final
rf=run(2,False); _,_,_,shf,cumf,mddf=stat(rf)
print(f"\n  So sanh (slip 2tick): fixed-1 Sharpe {shf:.2f}/cum {cumf*100:+.1f}%/MaxDD {mddf*100:.1f}%"
      f"  vs  vol-target Sharpe {sh:.2f}/cum {cum*100:+.1f}%/MaxDD {mdd*100:.1f}%")
print("\nDone.")
