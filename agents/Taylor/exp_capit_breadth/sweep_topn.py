"""G4-huong-C — sweep breadth top-N thanh khoan (job Taylor_20260722_094530).

Trials khai bao TRUOC: N in {100,150,200,250,300}. Tieu chi: tach sach tap fire cu
(br_old>=0.30 tren ticker_prune). gate' = trung diem khoang tach, KHONG tune.
"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
old = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"])[["time", "br_old"]].dropna()
new = pd.read_csv(os.path.join(HERE, "breadth_topn.csv"), parse_dates=["time"])
d = old.merge(new, on="time", how="inner").reset_index(drop=True)
fire = (d.br_old >= 0.30).values
print(f"phien: {len(d)} | ngay fire cu: {fire.sum()}")

for col in ["br100", "br150", "br200", "br250", "br300"]:
    v = d[col].values
    lo, hi = v[fire].min(), v[~fire].max()
    sep = lo - hi
    mid = (lo + hi) / 2
    # so ngay lech neu dung gate = mid
    mism = int(((v >= mid) != fire).sum())
    # gate sai it nhat (de tham khao khi khong tach duoc)
    best = min(((g, int(((v >= g) != fire).sum())) for g in np.arange(0.05, 0.70, 0.0005)), key=lambda x: x[1])
    print(f"{col}: min_fire={lo:.4f} max_nonfire={hi:.4f} gap={sep:+.4f} "
          f"rel_margin={sep/mid if mid else float('nan'):+.3%} | gate_mid={mid:.4f} lech={mism} | "
          f"best_gate={best[0]:.4f} lech_min={best[1]}")
    if sep <= 0:
        # liet ke ngay vi pham gan ranh gioi
        bad_fire = d.loc[fire & (v <= hi), ["time", "br_old", col]]
        bad_non = d.loc[(~fire) & (v >= lo), ["time", "br_old", col]]
        print(f"   fire-cu co {col}<=max_nonfire: {len(bad_fire)} ngay; non-fire co {col}>=min_fire: {len(bad_non)} ngay")
