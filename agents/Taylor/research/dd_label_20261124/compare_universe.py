#!/usr/bin/env python3
"""So nhãn MỚI (lịch sử chính mã, bin/dd_history_label.py) với nhãn CŨ 'so với universe' (thiết kế D2 §6 bị
quant-skeptic R2/D2 (b) bác: giá/tâm của mã đặt lên phân phối TRUNG VỊ UNIVERSE giá/(k_univ×proxy), cơ sở
TB5Y Big-4, k_univ = trung vị tâm/proxy của sổ). Đọc output D2 đã khoá, không tính lại D2.
Chạy: $DNA_PYEXE compare_universe.py  → out/compare_vs_universe_2026-11-20.csv + out/summary_E.json
"""
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
MIKE = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(MIKE, "bin"))
sys.dont_write_bytecode = True
import dd_history_label as L  # noqa: E402

D2O = os.path.join(MIKE, L.RES, "rerun", "D2", "out")
OUT = os.path.join(HERE, "out")
new = pd.read_csv(os.path.join(OUT, "dd_history_label_all_2026-11-20.csv"))
lv = pd.read_csv(os.path.join(D2O, "g3_level_monthly_d2.csv"), parse_dates=["time"]).set_index("time")
d2 = json.load(open(os.path.join(D2O, "d2_results.json")))
last = lv.index.max()
w10 = lv[(lv.index > last - pd.DateOffset(years=10)) & (lv.index < last)]
rows = []
for _, r in new.iterrows():
    rec = {"ticker": r.ticker, "pc_asof": r.pc_asof, "label_new": r.label, "pct_fade_new": r.pct_fade,
           "pct_hold_new": r.pct_hold}
    for v in ("fade", "hold"):
        k = d2["calib"]["by_basis"][f"avg5_{v}"]["k"]
        rec[f"pct_{v}_univ"] = L.pct_rank(w10[f"pv_avg5_b4_{v}"] / k, r.pc_asof)
    tf, th = L.tercile(rec["pct_fade_univ"]), L.tercile(rec["pct_hold_univ"])
    rec["label_univ_old"] = L.combine(tf, th)
    rec["same"] = rec["label_univ_old"] == r.label
    rows.append(rec)
C = pd.DataFrame(rows)
C.to_csv(os.path.join(OUT, "compare_vs_universe_2026-11-20.csv"), index=False, float_format="%.6g")
rho = float(pd.Series(C.pc_asof).corr(C.pct_hold_new, method="spearman"))
rho_u = float(pd.Series(C.pc_asof).corr(C.pct_hold_univ, method="spearman"))
summ = {"n": int(len(C)), "dist_new": new.label.value_counts().to_dict(),
        "dist_univ_old": C.label_univ_old.value_counts().to_dict(), "n_same_label": int(C.same.sum()),
        "spearman_pc_asof_vs_pct_hold_new": rho, "spearman_pc_asof_vs_pct_hold_univ": rho_u,
        "n_warn_peak": int(new.warn.fillna("").str.contains("ĐỈNH").sum()),
        "n_insufficient": int((new.label == "KHÔNG ĐỦ LỊCH SỬ").sum()),
        "n_months_min": int(new[["n_fade", "n_hold"]].min(axis=1).min()),
        "n_eff_hold_median": float(new.n_eff_hold.median()),
        "n_eff_hold_range": [float(new.n_eff_hold.min()), float(new.n_eff_hold.max())],
        "k_hold_range": [float(new.k_hold.min()), float(new.k_hold.max())],
        "k_fade_range": [float(new.k_fade.min()), float(new.k_fade.max())],
        "k_univ": {v: d2["calib"]["by_basis"][f"avg5_{v}"]["k"] for v in ("fade", "hold")}}
json.dump(summ, open(os.path.join(OUT, "summary_E.json"), "w"), ensure_ascii=False, indent=1, sort_keys=True)
print(json.dumps(summ, ensure_ascii=False, indent=1, sort_keys=True))
print(C[["ticker", "pc_asof", "label_new", "label_univ_old", "pct_fade_univ", "pct_hold_univ"]].to_string(index=False))
