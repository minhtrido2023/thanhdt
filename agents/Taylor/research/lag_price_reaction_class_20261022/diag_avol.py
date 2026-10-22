#!/usr/bin/env python3
"""HẬU KIỂM (không phải trial, khai trong REPORT): AVOL thấp có phải proxy thanh khoản kém không?
Đọc event_features.csv của reaction_study.py. Bootstrap cụm-mùa, seed 20261022."""
import os, numpy as np, pandas as pd
D = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(f"{D}/event_features.csv", parse_dates=["entry"])
cut = 0.34096  # P33 IS từ study_stdout (0.3410)
lo = (df["AVOL"] <= cut).values
pit = (df["in_pit"] == True).values
IS = (df["entry"].dt.year <= 2019).values
print(f"AVOL thấp n={lo.sum()} | AVOL==0 (V[d0]=0) {int((df['AVOL']==0).sum())} = {(df.loc[lo,'AVOL']==0).mean()*100:.1f}% nhóm thấp")
print(f"tỷ lệ in_universe_pit: nhóm thấp {pit[lo].mean()*100:.1f}% | nhóm còn lại {pit[~lo & df['AVOL'].notna().values].mean()*100:.1f}%")
rng = np.random.default_rng(20261022)
def dstat(mask, name):
    s = df.loc[mask, "season"].values; y = df.loc[mask, "Y"].values; ex = lo[mask]
    us, ci = np.unique(s, return_inverse=True); ns = len(us)
    sE = np.bincount(ci, y*ex, ns); nE = np.bincount(ci, ex.astype(float), ns)
    sK = np.bincount(ci, y*~ex, ns); nK = np.bincount(ci, (~ex).astype(float), ns)
    d = sE.sum()/nE.sum() - sK.sum()/nK.sum()
    bs = []
    for _ in range(2000):
        b = rng.integers(0, ns, ns); bs.append(sE[b].sum()/max(nE[b].sum(),1) - sK[b].sum()/max(nK[b].sum(),1))
    bs = np.array(bs)
    print(f"  {name:<28} n={mask.sum():5d} n_thấp={ex.sum():4d} mùa={ns} Δ={d*100:+.2f}pp CI95[{np.percentile(bs,2.5)*100:+.2f},{np.percentile(bs,97.5)*100:+.2f}] "
          f"mean_thấp={y[ex].mean()*100:.2f}% mean_giữ={y[~ex].mean()*100:.2f}%")
print("Δ AVOL:loại_THẤP theo tập con:")
dstat(np.ones(len(df), bool), "toàn bộ")
dstat(pit, "in_universe_pit")
dstat(pit & IS, "in_pit · IS")
dstat(pit & ~IS, "in_pit · OOS")
dstat(~pit, "ngoài universe_pit")
nz = (df["AVOL"] != 0).values
dstat(nz, "bỏ V[d0]=0")
dstat(pit & nz, "in_pit & V[d0]>0")
yrs = df["entry"].dt.year.values
print("LOYO trong in_pit:", " ".join(f"{k}:{(df.Y[pit&lo&(yrs!=k)].mean()-df.Y[pit&~lo&(yrs!=k)].mean())*100:+.2f}" for k in np.unique(yrs)))
