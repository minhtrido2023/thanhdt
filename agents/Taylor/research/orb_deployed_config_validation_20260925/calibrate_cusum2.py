# -*- coding: utf-8 -*-
"""calibrate_cusum2.py -- mo rong grid h + thu thiet ke CUSUM nham vao dich XA hon
(H1 = dao dau) de xem co to hop nao vua giu FPR thap vua phat hien nhanh khong."""
import sys, io, json, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
import numpy as np, orb_core as C
rng = np.random.default_rng(11)
pre = C.sim(C.build_days(C.load_bars()))
pre = pre[pre["date"] < C.LIVE_START]["net"].values
MU0, SD = float(pre.mean()), float(pre.std(ddof=1)); resid = pre - MU0

def arl(mu, h, k, B=30000, maxn=6000):
    S = np.zeros(B); done = np.zeros(B, bool); n = np.full(B, maxn, float)
    for i in range(1, maxn+1):
        x = mu + resid[rng.integers(0, len(resid), size=B)]
        S = np.maximum(0.0, S - (x - k)/SD)
        hit = (~done) & (S > h); n[hit] = i; done |= hit
        if done.all(): break
    return float(n.mean())

out = {}
for lbl, mu1 in [("H1: mu=0 (edge chet)", 0.0), ("H1: mu=-mu0 (edge dao dau)", -MU0)]:
    k = (MU0 + mu1)/2.0
    print(f"\n{'='*92}\n  Thiet ke {lbl} | k = {k*1e4:+.2f}bps | delta = {(MU0-mu1)/SD:.3f} sigma\n{'='*92}")
    print(f"  {'h':>6}{'ARL0 (in-control)':>20}{'ARL1 (detect)':>16}{'FPR/250ph':>11}{'FPR/60ph':>10}{'ARL0/ARL1':>11}")
    print("  "+"-"*74)
    rows=[]
    for h in [5,7,10,14,18,22,28,35,45,60]:
        a0 = arl(MU0,h,k); a1 = arl(mu1,h,k)
        f250 = 1-np.exp(-250/a0); f60 = 1-np.exp(-60/a0)
        rows.append(dict(h=h,arl0=a0,arl1=a1,fpr250=f250,fpr60=f60,ratio=a0/max(a1,1e-9)))
        print(f"  {h:>6}{a0:>20.0f}{a1:>16.0f}{f250*100:>10.1f}%{f60*100:>9.1f}%{a0/max(a1,1e-9):>11.2f}")
    out[lbl]=rows
json.dump(out, open("cusum_arl_extended.json","w"), indent=1, default=float)
print("\n  KET LUAN: xem ty so ARL0/ARL1. CUSUM chi huu dung khi ty so nay LON (>>3):")
print("  ty so ~1.5-2 nghia la bao dong khi hong va bao dong khi KHONG hong xay ra gan nhu nhu nhau.")
