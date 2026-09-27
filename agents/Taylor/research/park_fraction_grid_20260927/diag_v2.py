#!/usr/bin/env python3
"""Diagnostics AFTER the PREREG v2 decision rule has been applied — reported, NOT used to
re-decide. Purpose: say honestly HOW thin the margin is and where E[Calmar] gets its shape."""
import numpy as np, pandas as pd, glob
exec(open("paired_v2.py").read().split("# ---------- (1)")[0])   # reuse loaders/metrics
rng = np.random.default_rng(SEED); nblk = int(np.ceil(N/L)); off = np.arange(L)
C=np.empty((B,12)); D=np.empty((B,12)); K=np.empty((B,12))
for b in range(B):
    st = rng.integers(0,N,nblk); ix = ((st[:,None]+off[None,:])%N).ravel()[:N]
    C[b],_,D[b],K[b] = metrics(R[ix])
EK=K.mean(0); MK=np.median(K,0)
print("\n=== DIAGNOSTIC (post-decision, not a re-decision) ===")
print(f"{'x':>5} {'E[Calmar]':>9} {'med[Calmar]':>11} {'gap vs E-max':>12} {'gap vs med-max':>14}")
for i in range(4):
    print(f"{XS[i]:5.2f} {EK[i]:9.4f} {MK[i]:11.4f} {EK.max()-EK[i]:12.4f} {MK[:4].max()-MK[i]:14.4f}")
print(f"\nE[Calmar] gap 0% vs 30% = {EK[0]-EK[3]:.4f}  (prereg tie threshold 0.0300)")
print(f"  -> 30% is excluded from the tie group by {abs(EK[0]-EK[3])-0.03:.4f} Calmar. Knife edge.")
print(f"median[Calmar] argmax within 0-30% = x {XS[:4][np.argmax(MK[:4])]:.2f}  "
      f"(mean argmax = x {XS[:4][np.argmax(EK[:4])]:.2f})")
print(f"\nPaired head-to-head 0% vs 30% on the SAME 4000 paths:")
print(f"  P(Calmar_30 > Calmar_0) = {(K[:,3]>K[:,0]).mean():.3f}")
print(f"  P(CAGR_30  > CAGR_0)    = {(C[:,3]>C[:,0]).mean():.3f}")
print(f"  P(MaxDD_30 better than MaxDD_0) = {(D[:,3]>D[:,0]).mean():.3f}")
print(f"  mean dCAGR(30-0) = {(C[:,3]-C[:,0]).mean()*100:+.2f}pp   "
      f"mean dMaxDD(30-0) = {(D[:,3]-D[:,0]).mean()*100:+.2f}pp")
