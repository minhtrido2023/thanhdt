# -*- coding: utf-8 -*-
"""l_oshares_xcheck.py [V3 NB-1] đối chiếu N (nhánh E/BVPS và OS* của panel) với oshares_live.oshares_at(live=False) tại ngày công bố ('known').
Mẫu: tối đa 400 dòng in_universe 2014+ nhánh E/BVPS (seed 20261125) + 200 dòng OS làm đối chứng. Ghi out/oshares_xcheck.json/csv."""
import os, sys, json, numpy as np, pandas as pd
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
import datetime as _dt, oshares_live as OL, oshares_pit as OP
OUT = os.environ.get("OUT_DIR") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "out")
p = pd.read_parquet(os.path.join(OUT, "panel2.parquet"), columns=["ticker", "known", "N", "N_how", "in_universe", "src", "time"])
p = p[(p.in_universe) & (p.src == "BQ") & (p.time >= "2014-01-01")]
rng = np.random.default_rng(20261125)
def smp(h, n):
    d = p[p.N_how == h]; return d.iloc[rng.permutation(len(d))[:n]]
S = pd.concat([smp("E/BVPS", 80), smp("OS", 30)]).copy(); S["known"] = pd.to_datetime(S.known)
res = []; _C = OP.fetch_cache(sorted(S.ticker.unique()), _dt.date(2026, 11, 25)); print('cache', type(_C), flush=True)
for k, g in S.groupby(S.known.dt.date):
    try:
        r = OL.oshares_at(sorted(g.ticker.unique()), str(k), _cache=_C)
    except Exception as e:
        r = {}; print("ERR", k, repr(e)[:120], flush=True)
    for _, x in g.iterrows():
        v = (r.get(x.ticker) or {}); res.append({"ticker": x.ticker, "known": str(k), "N": x.N, "how": x.N_how, "live_value": v.get("value"), "live_method": v.get("method")})
R = pd.DataFrame(res); R["dup"] = R.duplicated(["ticker", "known", "how"], keep="first"); n_raw = R.groupby("how").size().to_dict()   # [V3.1 mục 4] khử dòng trùng (cùng mã, cùng ngày công bố, nhiều tháng panel)
R = R[~R.dup].drop(columns="dup").reset_index(drop=True); R.to_csv(os.path.join(OUT, "oshares_xcheck.csv"), index=False)
out = {"n_raw_before_dedupe": n_raw}
for h, g in R.groupby("how"):
    ok = g.live_value.notna() & (g.live_value > 0); d = np.abs(np.log(g.N[ok] / g.live_value[ok]))
    out[h] = {"n": int(len(g)), "n_live_value": int(ok.sum()), "n_AIS_EXACT": int((g.live_method == "AIS_EXACT").sum()), "share_refused": float(1 - ok.mean()), "share_absdiff_gt5pct": float((d > np.log(1.05)).mean()) if ok.any() else None,
              "share_absdiff_gt15pct": float((d > np.log(1.15)).mean()) if ok.any() else None, "median_absdiff": float(d.median()) if ok.any() else None,
              "methods": g.live_method.value_counts(dropna=False).to_dict()}
json.dump(out, open(os.path.join(OUT, "oshares_xcheck.json"), "w"), indent=1, ensure_ascii=False, default=str); print(json.dumps(out, ensure_ascii=False, indent=1, default=str))

E = R[(R.how == "E/BVPS") & (R.live_method == "AIS_EXACT")].copy(); E["N_over_live"] = E.N / E.live_value
print("AIS_EXACT E/BVPS:\n", E[["ticker", "known", "N", "live_value", "N_over_live"]].round(3).to_string(index=False))
E.to_csv(os.path.join(OUT, "oshares_xcheck_ais_exact.csv"), index=False)
