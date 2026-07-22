"""Rao can noi tai: ngay lech co phai knife-edge cua chinh br_old khong?"""
import os
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
old = pd.read_csv(os.path.join(HERE, "breadth_both.csv"), parse_dates=["time"])[["time", "br_old", "br_new"]].dropna()
new = pd.read_csv(os.path.join(HERE, "breadth_topn.csv"), parse_dates=["time"])
d = old.merge(new, on="time", how="inner").reset_index(drop=True)
fire = (d.br_old >= 0.30).values

# knife-edge cua chuoi cu
ke_fire = d.loc[fire & (d.br_old < 0.32), ["time", "br_old"]]
ke_non = d.loc[~fire & (d.br_old >= 0.28), ["time", "br_old"]]
print(f"fire-cu voi br_old trong [0.30,0.32): {len(ke_fire)}/{fire.sum()} ngay")
print(f"non-fire voi br_old trong [0.28,0.30): {len(ke_non)} ngay")

# cac ngay lech cua br250@0.2880 — br_old cua chung la bao nhieu?
for dt in ["2018-07-05","2020-03-11","2014-05-15","2022-09-19","2022-11-17","2015-05-18","2020-02-04","2015-05-06","2014-05-09","2022-05-11"]:
    row = d[d.time == dt]
    if len(row):
        r = row.iloc[0]
        print(f"{dt}: br_old={r.br_old:.4f} ({'FIRE' if r.br_old>=0.3 else 'non'}) br_new={r.br_new:.4f} br200={r.br200:.4f} br250={r.br250:.4f} br300={r.br300:.4f}")

for c in ["br_new","br100","br150","br200","br250","br300"]:
    print(f"corr(br_old,{c}) = {d.br_old.corr(d[c]):.4f}", end="  ")
print()
# hom nay
print(d.tail(2)[["time","br_old","br200","br250","br300"]].to_string(index=False))
