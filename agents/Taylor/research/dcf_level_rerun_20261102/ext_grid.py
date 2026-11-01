# -*- coding: utf-8 -*-
"""Mở rộng NGOÀI PREREG (gắn nhãn extension): lưới 0–3% cho nhóm ổn định, vì g_T* chạm sàn lưới 3,0%."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import level as LV
p = pd.read_parquet(os.path.join(HERE, "data", "panel_live.parquet"))
grid = np.round(np.arange(0.0, 0.0301, 0.0025), 4)
rows = []
for s in (0.0, 0.5):
    for g, m in (("all", np.ones(len(p), bool)), ("stable", ~p.unstable.values), ("unstable", p.unstable.values)):
        L = {c: LV.level(p, LV.fv(p, p.os_live.values, s, c), m) for c in grid}
        D = pd.DataFrame(L); Ly = D.groupby(D.index.year).mean()
        full, is_, oos, lo, hi = LV.calib(Ly)
        rows.append({"path": "live", "s": s, "group": g, "gT_full": full, "gT_IS": is_, "gT_OOS": oos, "loyo_min": lo, "loyo_max": hi,
                     "mean_log_PFV_at_0": float(Ly[0.0].mean()), "mean_log_PFV_at_3.0": float(Ly[0.03].mean())})
R = pd.DataFrame(rows); R.to_csv(os.path.join(HERE, "out", "ext_grid_below3.csv"), index=False)
print(R.round(4).to_string(index=False))
