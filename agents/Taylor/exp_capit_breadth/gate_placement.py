"""Neu chon C-conserv br250: gate dat o dau cho robust? + margin knife-edge cua cac config."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
old = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"])[["time", "br_old", "br_new"]].dropna()
new = pd.read_csv(os.path.join(HERE, "breadth_topn.csv"), parse_dates=["time"])
d = old.merge(new, on="time", how="inner").reset_index(drop=True)
fire = (d.br_old >= 0.30).values

for col in ["br_new", "br250"]:
    v = d[col].values
    hi = v[~fire].max()                      # max non-fire
    keep = v[fire][v[fire] > hi]             # fire days retained under conservative gate
    nxt = keep.min()
    print(f"{col}: max_nonfire={hi:.4f} | fire nho nhat GIU LAI={nxt:.4f} | "
          f"khoang trong=({hi:.4f},{nxt:.4f}) rong {nxt-hi:.4f} | gate trung diem={round((hi+nxt)/2,4)}")
