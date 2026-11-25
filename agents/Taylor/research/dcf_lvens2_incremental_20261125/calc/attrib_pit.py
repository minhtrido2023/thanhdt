# -*- coding: utf-8 -*-
"""attrib_pit.py — phân rã lệch lv_ENS2 (PIT vs vp2) trên mã in_universe: dòng có mc/E khác (N_next look-ahead / BCTC công bố sau D) vs phần còn lại
(beta HEDf + trung vị MULT trôi do route & dòng ngoài universe). Dùng: python attrib_pit.py '<glob>' OUT.json"""
import sys, glob, json
import numpy as np, pandas as pd
VP2 = "/home/trido/thanhdt/WorkingClaude/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c/out_F/vp2.parquet"
vp = pd.read_parquet(VP2, columns=["ticker", "ym", "mc", "E", "route", "in_universe", "lv_ENS2", "known"])
res = []
for fp in sorted(glob.glob(sys.argv[1])):
    a = pd.read_parquet(fp); ym = a.ym.iloc[0]
    m = a.merge(vp[vp.ym == ym], on="ticker", suffixes=("", "_v"))
    m = m[m.in_universe_v]
    d = (m.lv_ENS2 - m.lv_ENS2_v).abs()
    mcd = (np.log(m.mc / m.mc_v).abs() > 1e-12) | (m.E != m.E_v) | (m.known != m.known_v)
    rtd = m.route != m.route_v
    rest = ~mcd & ~rtd
    q = lambda s: {"n": int(len(s)), "n_gt_1e-9": int((s > 1e-9).sum()), "n_gt_1e-3": int((s > 1e-3).sum()), "n_gt_0.05": int((s > 0.05).sum()),
                   "p50": float(s.median()) if len(s) else 0.0, "p95": float(s.quantile(.95)) if len(s) else 0.0, "max": float(s.max()) if len(s) else 0.0}
    r = {"ym": ym, "file": fp.split("/")[-1], "univ_all": q(d), "rows_mc_or_filing_diff": q(d[mcd]), "rows_route_diff": q(d[rtd & ~mcd]), "rest_drift": q(d[rest]),
         "mc_diff_tickers": [{"t": t, "dlog_mc": round(float(np.log(x / y)), 4), "n_next_used_v31": None, "dENS2": round(float(z), 4), "known": str(k.date()), "known_vp2": str(kv.date())}
                             for t, x, y, z, k, kv in zip(m[mcd].ticker, m[mcd].mc, m[mcd].mc_v, d[mcd], m[mcd].known, m[mcd].known_v)],
         "route_diff_tickers": sorted(m[rtd].ticker)}
    res.append(r)
    print(f"{ym}: univ n={r['univ_all']['n']} >1e-3:{r['univ_all']['n_gt_1e-3']} >0.05:{r['univ_all']['n_gt_0.05']} p50={r['univ_all']['p50']:.2g} | "
          f"mc/BCTC khác: n={r['rows_mc_or_filing_diff']['n']} max={r['rows_mc_or_filing_diff']['max']:.3f} | route khác: {r['route_diff_tickers']} | "
          f"trôi còn lại: n={r['rest_drift']['n']} >1e-3:{r['rest_drift']['n_gt_1e-3']} p95={r['rest_drift']['p95']:.2g} max={r['rest_drift']['max']:.3g}")
json.dump(res, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
