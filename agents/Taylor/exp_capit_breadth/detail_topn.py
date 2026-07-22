"""Chi tiet huong lech + episode + grind cho cac ung vien tot nhat."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
old = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"])[["time", "br_old", "br_new"]].dropna()
new = pd.read_csv(os.path.join(HERE, "breadth_topn.csv"), parse_dates=["time"])
d = old.merge(new, on="time", how="inner").reset_index(drop=True)
fire = (d.br_old >= 0.30).values

def episodes(mask):
    """Gom ngay fire lien ke (<=5 phien cach nhau) thanh episode."""
    idx = np.where(mask)[0]
    eps = []
    for i in idx:
        if eps and i - eps[-1][-1] <= 5: eps[-1].append(i)
        else: eps.append([i])
    return eps

def grind(mask):
    idx = np.where(mask)[0]; s = set(idx)
    return {d.time[i]: any((i - b) in s for b in range(20, 91)) for i in idx}

old_eps = episodes(fire); old_g = grind(fire)
print(f"fire cu: {fire.sum()} ngay / {len(old_eps)} episode")

for col, gate in [("br200", 0.2850), ("br250", 0.2820), ("br250", 0.2880), ("br300", 0.2935)]:
    v = d[col].values; m = (v >= gate)
    lost = d.loc[fire & ~m, "time"].dt.date.tolist()
    added = d.loc[~fire & m, "time"].dt.date.tolist()
    new_eps = episodes(m)
    # episode cu nao mat hoan toan
    lost_ep = [d.time[ep[0]].date() for ep in old_eps if not any(m[i] for i in ep)]
    add_ep = [d.time[ep[0]].date() for ep in new_eps if not any(fire[i] for i in ep)]
    ng = grind(m)
    flips = [(k.date(), old_g[k], ng[k]) for k in sorted(set(old_g) & set(ng)) if old_g[k] != ng[k]]
    print(f"\n== {col} gate'={gate:.4f}: lech {len(lost)+len(added)} ngay "
          f"(MAT {len(lost)} / THEM-GIA {len(added)}) | episode: {len(new_eps)} (cu {len(old_eps)})")
    print(f"   ngay MAT: {lost}")
    print(f"   ngay THEM: {added}")
    print(f"   episode MAT han: {lost_ep} | episode THEM moi: {add_ep}")
    print(f"   grind flip (ngay fire chung): {len(flips)} -> {flips}")
