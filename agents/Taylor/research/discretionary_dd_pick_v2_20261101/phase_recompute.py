#!/usr/bin/env python3
"""Tái tính theo PHA tháng (job Taylor_20261101_135046) từ quick_pit_variants_out.csv + quick_pit_panel.csv.
Chạy: python3 -I phase_recompute.py  (đọc CSV cạnh file, không chạm BQ). Bootstrap trung vị 2000 lần, seed 0/pha."""
import os
import numpy as np
import pandas as pd
H = os.path.dirname(os.path.abspath(__file__))
o = pd.read_csv(os.path.join(H, "quick_pit_variants_out.csv"), parse_dates=["asof"])
p = pd.read_csv(os.path.join(H, "quick_pit_panel.csv"), parse_dates=["asof"])
PH = {"1/4/7/10": [1, 4, 7, 10], "2/5/8/11": [2, 5, 8, 11], "3/6/9/12": [3, 6, 9, 12]}
for name, ms in PH.items():
    pm = p[p["asof"].dt.month.isin(ms)]
    print(f"[{name}] fresh_rate={pm['fresh'].mean():.3f} rows={len(pm)} months={pm['asof'].nunique()}")
    for v, g in o.groupby("variant", sort=False):
        q = g[g["asof"].dt.month.isin(ms)]["d_vs_rest"].to_numpy()
        rng = np.random.default_rng(0)
        bs = [np.median(rng.choice(q, len(q))) for _ in range(2000)]
        print(f"  {v:8s} N={len(q)} median={np.median(q)*100:+.2f}pp hit={np.mean(q>0):.2f} "
              f"CI95=[{np.percentile(bs,2.5)*100:+.2f},{np.percentile(bs,97.5)*100:+.2f}]")
