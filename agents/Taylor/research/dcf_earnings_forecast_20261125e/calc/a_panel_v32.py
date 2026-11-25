# -*- coding: utf-8 -*-
"""a_panel_v32.py — PRELOCK_J4 §1: vá mc 'bước N sớm' của V3.1.
In: ../../dcf_earnings_forecast_20261125d/in_snapshot_v31/vp2.parquet. Out: ../out_panel/vp2.parquet, mc_fix32.json"""
import os, json
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); D = os.path.join(HERE, ".."); OUT = os.path.join(D, "out_panel"); os.makedirs(OUT, exist_ok=True)
SRC = os.path.join(D, "..", "dcf_earnings_forecast_20261125d", "in_snapshot_v31", "vp2.parquet")
vp = pd.read_parquet(SRC)
assert (vp.known <= vp.time).all(), "PIT violation"
dlr = np.log(vp.Close / vp.Price) - np.log(vp.close_rel / vp.price_rel)
ln = np.log(vp.N_next / vp.N)
sevent = dlr.abs() > 0.003
nn_ok = vp.N_next.notna() & (ln.abs() > 0.01)
step31 = sevent & nn_ok                                   # luật V3.1 (tái lập)
step32 = step31 & (ln > 0.01) & (dlr >= 0.5 * ln)         # luật V3.2
N31 = np.where(step31, vp.N_next, vp.N); N32 = np.where(step32, vp.N_next, vp.N)
mc31_re = np.where(np.isfinite(vp.Price * N31) & (vp.Price > 0), vp.Price * N31, vp.mc_old)
mc32 = np.where(np.isfinite(vp.Price * N32) & (vp.Price > 0), vp.Price * N32, vp.mc_old)
LOG = {"src": SRC, "V31_reproduce_maxabs_dlog": float(np.nanmax(np.abs(np.log(mc31_re / vp.mc.values))))}
assert LOG["V31_reproduce_maxabs_dlog"] < 1e-9, LOG
shift = np.log(vp.mc.values / mc32)                       # lv mới = lv cũ + log(mc31/mc32)
iu = vp.in_universe & (vp.ym.astype(str) >= "2014-01")
chg = np.abs(shift) > 1e-9
LOG.update({"rows_total": int(len(vp)), "rows_step31": int(step31.sum()), "rows_step32": int(step32.sum()),
            "rows_changed_all": int(chg.sum()), "rows_changed_in_univ_2014p": int((chg & iu).sum()), "n_in_univ_2014p": int(iu.sum()),
            "share_changed_in_univ_2014p": float((chg & iu).sum() / iu.sum()),
            "p50_abs_shift_changed": float(np.median(np.abs(shift[chg]))) if chg.any() else 0.0})
for c in [c for c in vp.columns if c.startswith("lv_")]:
    vp[c] = vp[c] + shift
vp["mc_v31"] = vp.mc; vp["mc"] = mc32
vp["ep"] = vp.np_ttm / vp.mc; vp["bp"] = vp.E / vp.mc; vp["sp"] = vp.rev_ttm / vp.mc; vp["ev"] = vp.mc + vp.debt.fillna(0) - vp.cash.fillna(0)
cases = []
for t, a, b in (("ACG", "2022-01", "2022-04"), ("ABI", "2025-06", "2025-10"), ("TCB", "2024-04", "2024-07")):
    x = vp[(vp.ticker == t) & vp.ym.astype(str).between(a, b)]
    cases += [{"ticker": t, "ym": str(r.ym), "mc_v31_ty": round(r.mc_v31 / 1e9), "mc_v32_ty": round(r.mc / 1e9), "mc_old_ty": round(r.mc_old / 1e9)} for r in x.itertuples()]
LOG["cases"] = cases
vp.to_parquet(os.path.join(OUT, "vp2.parquet"))
json.dump(LOG, open(os.path.join(OUT, "mc_fix32.json"), "w"), indent=1, ensure_ascii=False); print(json.dumps(LOG, indent=1, ensure_ascii=False))
