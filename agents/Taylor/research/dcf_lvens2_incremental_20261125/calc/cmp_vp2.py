# -*- coding: utf-8 -*-
"""cmp_vp2.py — so lvens2_<ym>*.parquet với vp2.parquet (V3.1, md5 3b89e78d40d1ce68a3212223e6cd5b11): số mã, max|Δ| từng cột lv_, route, in_universe.
Dùng: python cmp_vp2.py <glob parquet> [--json OUT]. In một dòng/tháng; liệt kê mã lệch (> 1e-9) hoặc vắng một bên."""
import sys, glob, json, hashlib
import numpy as np, pandas as pd
VP2 = "/home/trido/thanhdt/WorkingClaude/wt-dcf-v3-20261125/agents/Taylor/research/dcf_vn_redesign_20261125c/out_F/vp2.parquet"
COLS = ["lv_D0B", "lv_DDM", "lv_EPV", "lv_MULT", "lv_HEDf", "lv_ENS2"]
files = sorted(glob.glob(sys.argv[1])); out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else None
assert hashlib.md5(open(VP2, "rb").read()).hexdigest() == "3b89e78d40d1ce68a3212223e6cd5b11", "vp2 md5 đổi"
vp = pd.read_parquet(VP2, columns=["ticker", "ym", "time", "route", "in_universe", "n_ENS2"] + COLS)
res = []
for fp in files:
    a = pd.read_parquet(fp); ym = a.ym.iloc[0]; b = vp[vp.ym == ym]
    m = a.merge(b, on="ticker", how="outer", suffixes=("", "_v"), indicator=True)
    both = m[m._merge == "both"]
    r = {"file": fp.split("/")[-1], "ym": ym, "n_new": int(len(a)), "n_vp2": int(len(b)), "only_new": sorted(m[m._merge == "left_only"].ticker)[:20],
         "only_vp2": sorted(m[m._merge == "right_only"].ticker)[:20], "route_diff": int((both.route != both.route_v).sum()),
         "in_univ_diff": int((both.in_universe != both.in_universe_v).sum()), "time_diff": int((both.time != both.time_v).sum())}
    iu = both[both.in_universe_v]
    r["n_univ_ENS2_new"] = int(a[a.in_universe].lv_ENS2.notna().sum()); r["n_univ_ENS2_vp2"] = int(b[b.in_universe].lv_ENS2.notna().sum())
    for c in COLS:
        x, y = both[c].values, both[c + "_v"].values
        nanmis = int((np.isnan(x) != np.isnan(y)).sum()); d = np.abs(x - y); d = d[np.isfinite(d)]
        r[c] = {"max_abs": float(d.max()) if len(d) else 0.0, "n_gt_1e-9": int((d > 1e-9).sum()), "nan_mismatch": nanmis}
    dd = np.abs(both.lv_ENS2 - both.lv_ENS2_v)
    bad = both[(dd > 1e-9) | (both.lv_ENS2.isna() != both.lv_ENS2_v.isna())]
    r["ENS2_bad_tickers"] = [{"t": t, "iu": bool(u), "new": None if np.isnan(p) else round(float(p), 6), "vp2": None if np.isnan(q) else round(float(q), 6),
                              "n_next_used": bool(nn) if "n_next_used" in bad else None}
                             for t, u, p, q, nn in zip(bad.ticker, bad.in_universe_v, bad.lv_ENS2, bad.lv_ENS2_v, bad.get("n_next_used", pd.Series([None] * len(bad))))][:40]
    r["ENS2_bad_in_univ"] = int(bad.in_universe_v.sum())
    r["ENS2_univ_max_abs"] = float(np.nanmax(np.abs(iu.lv_ENS2 - iu.lv_ENS2_v))) if len(iu) else 0.0
    res.append(r)
    print(f"{ym} {r['file']}: n {r['n_new']}/{r['n_vp2']} only_new={len(r['only_new'])} only_vp2={len(r['only_vp2'])} route_diff={r['route_diff']} iu_diff={r['in_univ_diff']} "
          f"ENS2 max|Δ|={r['lv_ENS2']['max_abs']:.3g} n>1e-9={r['lv_ENS2']['n_gt_1e-9']} nanmis={r['lv_ENS2']['nan_mismatch']} bad_in_univ={r['ENS2_bad_in_univ']} "
          f"univ_ENS2_ok {r['n_univ_ENS2_new']}/{r['n_univ_ENS2_vp2']} | " + " ".join(f"{c[3:]}:{r[c]['max_abs']:.2g}/{r[c]['n_gt_1e-9']}/{r[c]['nan_mismatch']}" for c in COLS[:-1]))
if out_json:
    json.dump(res, open(out_json, "w"), ensure_ascii=False, indent=1)
