"""Bien the than trong tuyet doi (0 fire gia) cho tung N + ngay universe vuot N."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
old = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"])[["time", "br_old", "br_new"]].dropna()
new = pd.read_csv(os.path.join(HERE, "breadth_topn.csv"), parse_dates=["time"])
d = old.merge(new, on="time", how="inner").reset_index(drop=True)
fire = (d.br_old >= 0.30).values

def episodes(mask):
    idx = np.where(mask)[0]; eps = []
    for i in idx:
        if eps and i - eps[-1][-1] <= 5: eps[-1].append(i)
        else: eps.append([i])
    return eps
old_eps = episodes(fire)

for col in ["br_new", "br200", "br250", "br300"]:
    v = d[col].values
    hi = v[~fire].max()
    g = hi + 1e-9
    lost = d.loc[fire & (v < g), "time"].dt.date.tolist()
    lost_ep = [d.time[ep[0]].date() for ep in old_eps if not any(v[i] >= g for i in ep)]
    print(f"{col} conservative gate'={hi:.4f}+eps: MAT {len(lost)} ngay {lost} | episode MAT han: {lost_ep}")

for n, col in [(200, "br200"), (250, "br250"), (300, "br300")]:
    over = d[d.n_universe >= n]
    print(f"n_universe >= {n} tu ngay: {over.time.iloc[0].date() if len(over) else 'CHUA'} "
          f"({len(over)}/{len(d)} phien)")
print(d.n_universe.describe()[["min","50%","max"]].to_string())
