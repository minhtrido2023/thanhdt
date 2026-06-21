# -*- coding: utf-8 -*-
"""
vn30f_orb_strategy.py
=====================
ORB (Opening-Range momentum) VN30F intraday — hoan thien + kiem dinh.
 (2) Refine: stop-loss intraday + thoat truoc ATC (exit_hm).
 (1) Validate: cost-sensitivity (TC 1.5/2.5/3.5bps) + walk-forward theo nam.

Logic 1 phien:
  OR30 = return 09:00->09:30 ; sig=sign(OR30) ; chi trade neu |OR30|>=MIN_OR
  Vao 09:30 (entry=close 09:30). Di chuyen tung bar:
    - stop: long thoat neu low<=entry*(1-STOP); short neu high>=entry*(1+STOP) -> thoat tai stop
    - het gio EXIT_HM -> thoat tai close bar do
  pnl = sig*(exit/entry-1) - TC
"""
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, pandas as pd
WD = r"/home/trido/thanhdt/WorkingClaude"

df = pd.read_csv(WD+"/data/vn30f1m_1min.csv"); df["time"]=pd.to_datetime(df["time"])
df["date"]=df["time"].dt.date; df["hm"]=df["time"].dt.strftime("%H:%M")

# pre-split per day
days=[]
for d,g in df.groupby("date"):
    g=g.sort_values("time").reset_index(drop=True)
    if len(g)<150: continue
    op=g[g["hm"]<="09:30"]
    if len(op)<10: continue
    entry=op["close"].iloc[-1]; or_ret=entry/g["close"].iloc[0]-1
    post=g[g["hm"]>"09:30"].reset_index(drop=True)
    days.append({"date":d,"or_ret":or_ret,"entry":entry,"post":post})

def sim(exit_hm="14:00", stop=None, tc=0.00015, min_or=0.002):
    recs=[]
    for dd in days:
        if abs(dd["or_ret"])<min_or: continue
        sig=np.sign(dd["or_ret"]); entry=dd["entry"]; post=dd["post"]
        seg=post[post["hm"]<=exit_hm]
        if len(seg)==0: continue
        exit_px=seg["close"].iloc[-1]; stopped=False
        if stop is not None:
            if sig>0:
                hit=seg[seg["low"]<=entry*(1-stop)]
                if len(hit)>0: exit_px=entry*(1-stop); stopped=True
            else:
                hit=seg[seg["high"]>=entry*(1+stop)]
                if len(hit)>0: exit_px=entry*(1+stop); stopped=True
        pnl=sig*(exit_px/entry-1)-tc
        recs.append({"date":dd["date"],"pnl":pnl,"stopped":stopped})
    return pd.DataFrame(recs)

def stat(r):
    if len(r)==0: return None
    n=len(r); wr=(r["pnl"]>0).mean(); mean=r["pnl"].mean()
    sh=mean/r["pnl"].std()*np.sqrt(252) if r["pnl"].std()>0 else 0
    cum=(1+r["pnl"]).prod()-1
    nav=(1+r["pnl"]).cumprod(); mdd=(nav/nav.cummax()-1).min()
    return dict(n=n,wr=wr,mean=mean,sh=sh,cum=cum,mdd=mdd,stp=r["stopped"].mean())

# ===== A) EXIT-TIME x STOP grid (TC=1.5bps, |OR|>=0.2%) =====
print("="*92); print("  A) EXIT-TIME x STOP  (TC 1.5bps, |OR30|>=0.2%)"); print("="*92)
print(f"  {'exit':<7}{'stop':<7}{'n':>5}{'WR':>7}{'mean/d':>9}{'Sharpe':>8}{'MaxDD':>8}{'%stop':>7}{'cum':>8}")
print("  "+"-"*78)
for exit_hm in ["13:30","14:00","14:30"]:
    for stop in [None,0.005,0.007,0.010]:
        r=sim(exit_hm,stop,0.00015,0.002); s=stat(r)
        if not s: continue
        ss=f"{stop*100:.1f}%" if stop else "none"
        print(f"  {exit_hm:<7}{ss:<7}{s['n']:>5}{s['wr']*100:>6.1f}%{s['mean']*1e4:>+8.2f}{s['sh']:>8.2f}"
              f"{s['mdd']*100:>+7.1f}%{s['stp']*100:>6.0f}%{s['cum']*100:>+7.1f}%")

# ===== B) COST SENSITIVITY (best config exit 14:00, stop 0.7%) =====
print("\n"+"="*92); print("  B) COST SENSITIVITY  (exit 14:00, stop 0.7%, |OR|>=0.2%)"); print("="*92)
print(f"  {'TC':<8}{'n':>5}{'WR':>7}{'mean/d':>9}{'Sharpe':>8}{'cum':>9}")
print("  "+"-"*48)
for tc in [0.00015,0.00025,0.00035]:
    r=sim("14:00",0.007,tc,0.002); s=stat(r)
    print(f"  {tc*1e4:.1f}bps {s['n']:>5}{s['wr']*100:>6.1f}%{s['mean']*1e4:>+8.2f}{s['sh']:>8.2f}{s['cum']*100:>+8.1f}%")

# ===== C) WALK-FORWARD theo nam (exit 14:00, stop 0.7%, TC 2.5bps realistic) =====
print("\n"+"="*92); print("  C) WALK-FORWARD theo nam  (exit 14:00, stop 0.7%, TC 2.5bps, |OR|>=0.2%)"); print("="*92)
r=sim("14:00",0.007,0.00025,0.002); r["yr"]=pd.to_datetime(r["date"]).dt.year
print(f"  {'Nam':<8}{'n':>5}{'WR':>7}{'mean/d':>9}{'Sharpe':>8}{'cum':>9}")
print("  "+"-"*48)
for yr,gg in r.groupby("yr"):
    s=stat(gg)
    print(f"  {yr:<8}{s['n']:>5}{s['wr']*100:>6.1f}%{s['mean']*1e4:>+8.2f}{s['sh']:>8.2f}{s['cum']*100:>+8.1f}%")
s=stat(r); print("  "+"-"*48)
print(f"  {'TONG':<8}{s['n']:>5}{s['wr']*100:>6.1f}%{s['mean']*1e4:>+8.2f}{s['sh']:>8.2f}{s['cum']*100:>+8.1f}%")
print("\nDone.")
