"""Grind-outcome diff theo quy uoc UNION (giong recalib_capit_gate.py) de so cong bang voi B."""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
old = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"])[["time", "br_old", "br_new"]].dropna()
new = pd.read_csv(os.path.join(HERE, "breadth_topn.csv"), parse_dates=["time"])
d = old.merge(new, on="time", how="inner").reset_index(drop=True)
fire = (d.br_old >= 0.30).values

def grind(mask):
    idx = np.where(mask)[0]; s = set(idx)
    return {d.time[i]: any((i - b) in s for b in range(20, 91)) for i in idx}
old_g = grind(fire)

for col, gate, tag in [("br_new", 0.3070, "B"), ("br250", 0.2880, "C-mixed"),
                        ("br250", 0.3081, "C-conserv-250"), ("br300", 0.3134, "C-conserv-300")]:
    m = (d[col].values >= gate)
    ng = grind(m)
    diff = [(k.date(), old_g.get(k, "NOFIRE"), ng.get(k, "NOFIRE"))
            for k in sorted(set(old_g) | set(ng)) if old_g.get(k, "NOFIRE") != ng.get(k, "NOFIRE")]
    # tach rieng: flip grind that (fire chung, True<->False) vs fire/mat
    flips = [x for x in diff if x[1] != "NOFIRE" and x[2] != "NOFIRE"]
    print(f"{tag} ({col}@{gate}): union diff = {len(diff)} su kien, trong do GRIND FLIP that (fire ca 2 ben) = {len(flips)}: {flips}")

lowdays = d.nsmallest(5, "n_universe")[["time", "n_universe", "br_old"]]
print("\n5 ngay n_universe thap nhat:\n", lowdays.to_string(index=False))
