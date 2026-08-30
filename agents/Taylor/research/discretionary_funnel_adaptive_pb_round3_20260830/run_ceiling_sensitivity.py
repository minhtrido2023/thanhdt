#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discretionary_funnel_adaptive_pb_round3_20260830 — khoá PB_MAX_CEIL bằng ĐÚNG cơ chế đã
dùng cho cutoff (min-CV stability qua 7 episode lịch sử), theo yêu cầu quant-skeptic verify lần 2
(job Taylor_20260830_075523, verify quant-skeptic_20260830_080843, param_overfit="fail" trên
ceiling — không có sensitivity backing, y hệt bản REFUTED gốc).

Đọc lại cohort_washout_dd52.csv + LOCKED_CUTOFF.txt (=70) đã có sẵn từ round 2
(discretionary_funnel_adaptive_pb_redo_20260830/) — KHÔNG re-query BQ (basis/cutoff không đổi,
chỉ ceiling là biến mới). Cutoff giữ NGUYÊN 70% (đã khoá, không mở lại).

Tiêu chí chọn ceiling: giống hệt cutoff — với mỗi bước ceiling e trên lưới 1.2..1.8 (step 0.1),
đo marginal growth-rate g(e) = (n_OR(e) - n_OR(e_prev))/n_abs mỗi episode (n_OR tại cutoff=70%
CỐ ĐỊNH, chỉ ceiling thay đổi; e_prev=1.0 cho điểm lưới đầu tiên 1.2, tương đương baseline
n_abs_pb_lt1 dùng cho cutoff — vì ceiling=1.0 làm nhánh percentile vô nghĩa, trùng nhánh absolute),
rồi CV(e) = std(g)/mean(g) qua 7 episode. Ceiling có CV thấp nhất = ổn định/dự đoán được nhất qua
các chu kỳ — không tham chiếu ticker nào, không tham chiếu dữ liệu hôm nay.
"""
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND2 = os.path.normpath(os.path.join(HERE, "..", "discretionary_funnel_adaptive_pb_redo_20260830"))

PB_MAX_ABS = 1.0
CUTOFF_LOCKED = None  # loaded from round2 LOCKED_CUTOFF.txt below
CEILINGS = [round(1.2 + 0.1 * i, 1) for i in range(7)]  # 1.2..1.8 step 0.1


def main():
    global CUTOFF_LOCKED
    with open(os.path.join(ROUND2, "LOCKED_CUTOFF.txt")) as f:
        CUTOFF_LOCKED = int(f.read().strip())
    print(f"cutoff (locked, round2, unchanged) = {CUTOFF_LOCKED}%", file=sys.stderr)

    cohort = pd.read_csv(os.path.join(ROUND2, "cohort_washout_dd52.csv"))

    sens_rows = []
    for label in cohort["episode"].unique():
        sub = cohort[cohort["episode"] == label]
        n_abs = int((sub["PB"] < PB_MAX_ABS).sum())
        n_total = len(sub)
        row = {"episode": label, "n_cohort": n_total, "n_abs_pb_lt1": n_abs}
        for e in CEILINGS:
            qualify = (sub["PB"] < PB_MAX_ABS) | (
                (sub["pb_pct_rank"] <= CUTOFF_LOCKED / 100.0) & (sub["PB"] < e)
            )
            row[f"n_OR_ceil{e}"] = int(qualify.sum())
        sens_rows.append(row)
    sens = pd.DataFrame(sens_rows)
    sens.to_csv(os.path.join(HERE, "ceiling_sensitivity_full_grid.csv"), index=False)

    marg_rows = []
    prev_col = "n_abs_pb_lt1"
    for e in CEILINGS:
        col = f"n_OR_ceil{e}"
        for _, r in sens.iterrows():
            n_abs = r["n_abs_pb_lt1"]
            if n_abs == 0:
                continue
            g = (r[col] - r[prev_col]) / n_abs
            marg_rows.append({"ceiling": e, "episode": r["episode"], "marginal_growth": g})
        prev_col = col
    marg = pd.DataFrame(marg_rows)
    marg.to_csv(os.path.join(HERE, "marginal_growth_by_ceiling_episode.csv"), index=False)

    stability = marg.groupby("ceiling")["marginal_growth"].agg(["mean", "std", "count"])
    stability["cv"] = stability["std"] / stability["mean"].abs()
    stability.to_csv(os.path.join(HERE, "ceiling_stability_cv.csv"))
    print(stability, file=sys.stderr)

    best_ceiling = stability["cv"].idxmin()
    print(f"\n>>> LOCKED ceiling by min-CV stability rule: {best_ceiling}", file=sys.stderr)
    with open(os.path.join(HERE, "LOCKED_CEILING.txt"), "w") as f:
        f.write(f"{best_ceiling}\n")


if __name__ == "__main__":
    main()
