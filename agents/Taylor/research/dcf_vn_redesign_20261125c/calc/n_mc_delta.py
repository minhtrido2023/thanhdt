# -*- coding: utf-8 -*-
"""n_mc_delta.py [V3.1 mục 1] đo mc mới (Price thô × N bước theo sự kiện cổ phiếu) so mc cũ (MC_rel × Close/close_rel) trên panel2.parquet. Ghi OUT/mc_fix_delta.json."""
import os, json, numpy as np, pandas as pd
OUT = os.environ["OUT_DIR"]; p = pd.read_parquet(os.path.join(OUT, "panel2.parquet"), columns=["ticker", "ym", "in_universe", "mc", "mc_old", "src"])
u = p[p.in_universe & (p.ym >= "2014-01")]; d = np.log(u.mc / u.mc_old).abs()
vnm = p[(p.ticker == "VNM") & (p.ym == "2019-06")].iloc[0]
json.dump({"rows_in_universe_2014plus": int(len(u)), "share_abs_dlog_gt_0.2pct": float((d > 0.002).mean()), "rows_gt_0.2pct": int((d > 0.002).sum()), "tickers_gt_0.2pct": int(u[d > 0.002].ticker.nunique()),
           "tickers_total": int(u.ticker.nunique()), "share_abs_dlog_gt_10pct": float((d > 0.10).mean()), "median_abs_dlog": float(d.median()),
           "VNM_2019-06": {"mc_old": float(vnm.mc_old), "mc_new": float(vnm.mc), "dlog": float(np.log(vnm.mc / vnm.mc_old))}}, open(os.path.join(OUT, "mc_fix_delta.json"), "w"), indent=1)
print(open(os.path.join(OUT, "mc_fix_delta.json")).read())
