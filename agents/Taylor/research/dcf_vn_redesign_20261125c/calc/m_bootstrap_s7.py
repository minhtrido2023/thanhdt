# -*- coding: utf-8 -*-
"""m_bootstrap_s7.py [V3.1 mục 6] CI bootstrap theo NĂM LỊCH (khối năm, B=2000, seed 20261125) cho hiệu CAGR giữa các chiến lược S7 và EW / E/P.
Đọc bt2_monthly_<tên>.csv (cột ret = lợi suất tháng ròng phí). Điểm ước lượng = CAGR tính lại từ cùng chuỗi (đối chiếu bt2_summary ALL). Ghi OUT/s7_bootstrap.json."""
import os, json, numpy as np, pandas as pd
OUT = os.environ["OUT_DIR"]; B = 2000
def load(n):
    m = pd.read_csv(os.path.join(OUT, f"bt2_monthly_{n}.csv")); return m.set_index("ym").ret
def cagr(r): return float(np.prod(1 + r.values) ** (12 / len(r)) - 1)
PAIRS = [("S7_ENS1w_f1", "EW_f1"), ("S7_ENS2_f1", "EW_f1"), ("S7_D0_f1", "EW_f1"), ("S7_EPN_f1", "EW_f1"), ("S7_EPN_E2_f1", "EW_f1"),
         ("S7_ENS1w_f1", "S7_EPN_f1"), ("S7_ENS2_f1", "S7_EPN_E2_f1"), ("S7_D0_f1", "S7_EPN_f1")]
summ = pd.read_csv(os.path.join(OUT, "bt2_summary.csv")); summ = summ[summ.era == "ALL"].set_index("strategy").cagr
res = {}; rng = np.random.RandomState(20261125)
for a, b in PAIRS:
    ra, rb = load(a), load(b); ix = ra.index.intersection(rb.index); ra, rb = ra[ix], rb[ix]
    yrs = np.array([x[:4] for x in ix]); uy = sorted(set(yrs)); byy = {y: (ra[yrs == y].values, rb[yrs == y].values) for y in uy}
    d = np.empty(B)
    for i in range(B):
        pk = rng.choice(len(uy), len(uy), replace=True); xa = np.concatenate([byy[uy[j]][0] for j in pk]); xb = np.concatenate([byy[uy[j]][1] for j in pk])
        d[i] = (np.prod(1 + xa) ** (12 / len(xa)) - 1) - (np.prod(1 + xb) ** (12 / len(xb)) - 1)
    pt = cagr(ra) - cagr(rb)
    res[f"{a} - {b}"] = {"diff_pp": round(100 * pt, 2), "ci95_pp": [round(100 * float(np.percentile(d, 2.5)), 2), round(100 * float(np.percentile(d, 97.5)), 2)], "share_boot_gt0": round(float((d > 0).mean()), 3),
                         "n_months": int(len(ix)), "n_years": len(uy), "check_cagr_a_vs_summary": [round(100 * cagr(ra), 2), round(100 * float(summ[a]), 2)]}
json.dump(res, open(os.path.join(OUT, "s7_bootstrap.json"), "w"), indent=1, ensure_ascii=False); print(json.dumps(res, indent=1, ensure_ascii=False))
