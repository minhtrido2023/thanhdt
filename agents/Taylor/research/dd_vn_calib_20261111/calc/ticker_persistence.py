# -*- coding: utf-8 -*-
"""ticker_persistence.py — lệch FV/P bền theo mã (REPORT §2). Run: $DNA_PYEXE ticker_persistence.py"""
import os, json, numpy as np, pandas as pd
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
p = pd.read_parquet(os.path.join(OUT, "panel.parquet")); p = p[p["ok"] & (p["rating"] <= 3)].copy()
p["lr"] = np.log(p.FV / p.P0)
t = p.groupby("ticker").agg(n=("lr", "size"), med=("lr", "median"), fneg=("lr", lambda s: (s < 0).mean()))
t = t[t.n >= 4]
gm = p.groupby("ticker").lr.transform("mean")
p = p.sort_values(["ticker", "asof"]); p["lr4"] = p.groupby("ticker").lr.shift(-4)
o = {"n_tickers_ge4q": len(t), "frac_med_FVP_lt_0.75": float((np.exp(t.med) < 0.75).mean()),
     "frac_med_FVP_gt_1.33": float((np.exp(t.med) > 1.33).mean()), "frac_FVltP_ge80pct": float((t.fneg >= 0.8).mean()),
     "between_ticker_var_share": float(1 - ((p.lr - gm) ** 2).sum() / ((p.lr - p.lr.mean()) ** 2).sum()),
     "autocorr_4q": float(p[["lr", "lr4"]].corr().iloc[0, 1])}
json.dump(o, open(os.path.join(OUT, "ticker_persistence.json"), "w"), indent=1); print(o)
