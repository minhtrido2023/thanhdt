#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discretionary_funnel_adaptive_pb_redo_20260830 — bước 2 (cutoff, ĐỘC LẬP với TV1/DGC).

Chạy episode_cohort_query.sql cho 7 episode dd52<=-20% (trough dates, cùng bộ đã dùng ở
discretionary_sleeve_correlation_risk_20260830.md), tính sensitivity curve n_OR(cutoff) trên
GRID ĐẦY ĐỦ 10..90 (step 10) — KHÔNG dùng bất kỳ dữ liệu ngày hôm nay (2026-08-30) ở bước này.

Cơ sở percentile: universe_pit ∩ Volume>0 cùng ngày (đã khoá ở §1 report, TRƯỚC khi chạy script
này) — KHÔNG lặp lại việc thử "universe_pit vs full-listed" (đã bị quant-skeptic REFUTED là
circular). Script này CHỈ chọn cutoff, không đụng lại quyết định cơ sở.

Tiêu chí chọn cutoff: STABILITY qua episode (không neo bất kỳ ticker cụ thể nào). Với mỗi bước
cutoff c, đo marginal growth-rate g(c) = (n_OR(c) - n_OR(c-10))/n_abs mỗi episode, rồi tính hệ số
biến thiên CV(c) = std(g)/mean(g) qua 7 episode — cutoff có CV thấp nhất là cutoff mà percentile
threshold hoạt động ỔN ĐỊNH/DỰ ĐOÁN ĐƯỢC nhất qua các chu kỳ khác nhau (không phải chỉ tình cờ ăn
may ở 1-2 episode). Đây là quy tắc thống kê thuần, không tham chiếu ticker nào.
"""
import os
import subprocess
import sys
from io import StringIO

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "lithe-record-440915-m9"

EPISODES = [
    ("2007-04", "2009-02-24"),
    ("2009-11", "2010-08-25"),
    ("2011-05", "2012-01-06"),
    ("2012-08", "2012-11-02"),
    ("2018-05", "2019-01-03"),
    ("2020-03", "2020-03-24"),
    ("2022-05", "2022-11-15"),
]

PB_MAX_ABS = 1.0
PB_MAX_CEIL = 1.5          # trần chống-trôi — round-number heuristic value-investing, không tuned
WASHOUT_MIN = -0.30
DD52_MAX = -0.20
CUTOFFS = list(range(10, 100, 10))  # 10..90, grid đầy đủ (bản cũ chỉ có 30-60)


def bq_csv(sql):
    # SQL truyền qua STDIN, không qua argv — argv bắt đầu bằng "--" (comment SQL) bị absl flag
    # parser của bq.py nuốt nhầm thành flag dù đã có "--" end-of-flags marker (đã tự bắt được
    # lỗi này khi chạy trực tiếp, xem log job).
    env = os.environ.copy()
    p = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
         "--format=csv", "--max_rows=20000"],
        input=sql, capture_output=True, text=True, env=env, timeout=180,
    )
    if p.returncode != 0:
        raise RuntimeError(f"bq query failed (rc={p.returncode}): stderr={p.stderr!r} stdout={p.stdout!r}")
    return pd.read_csv(StringIO(p.stdout))


def main():
    with open(os.path.join(HERE, "episode_cohort_query.sql")) as f:
        template = f.read()

    rows = []
    for label, trough in EPISODES:
        window_start = (pd.Timestamp(trough) - pd.Timedelta(days=460)).date().isoformat()
        sql = template.replace("{TROUGH}", trough).replace("{WINDOW_START}", window_start)
        print(f"[{label}] querying trough={trough} window_start={window_start} ...", file=sys.stderr)
        df = bq_csv(sql)
        df["episode"] = label
        df["trough"] = trough
        out_csv = os.path.join(HERE, f"episode_{label}_cross_section.csv")
        df.to_csv(out_csv, index=False)
        rows.append(df)
        print(f"[{label}] {len(df)} rows -> {out_csv}", file=sys.stderr)

    full = pd.concat(rows, ignore_index=True)
    full.to_csv(os.path.join(HERE, "all_episodes_cross_section.csv"), index=False)

    # Cohort = washout>=30% AND dd52<=-20%, y hệt production funnel definition
    cohort = full[(full["washout_pct"] <= WASHOUT_MIN) & (full["dd52_pct"] <= DD52_MAX)].copy()
    cohort.to_csv(os.path.join(HERE, "cohort_washout_dd52.csv"), index=False)

    sens_rows = []
    for label, _ in EPISODES:
        sub = cohort[cohort["episode"] == label]
        n_abs = int((sub["PB"] < PB_MAX_ABS).sum())
        n_total = len(sub)
        row = {"episode": label, "n_cohort": n_total, "n_abs_pb_lt1": n_abs}
        for c in CUTOFFS:
            qualify = (sub["PB"] < PB_MAX_ABS) | (
                (sub["pb_pct_rank"] <= c / 100.0) & (sub["PB"] < PB_MAX_CEIL)
            )
            row[f"n_OR_p{c}"] = int(qualify.sum())
        sens_rows.append(row)
    sens = pd.DataFrame(sens_rows)
    sens.to_csv(os.path.join(HERE, "sensitivity_full_grid.csv"), index=False)

    # Marginal growth-rate per 10pp step per episode, normalized by n_abs (>0 guard)
    marg_rows = []
    prev_col = "n_abs_pb_lt1"
    for c in CUTOFFS:
        col = f"n_OR_p{c}"
        for _, r in sens.iterrows():
            n_abs = r["n_abs_pb_lt1"]
            if n_abs == 0:
                continue
            g = (r[col] - r[prev_col]) / n_abs
            marg_rows.append({"cutoff": c, "episode": r["episode"], "marginal_growth": g})
        prev_col = col
    marg = pd.DataFrame(marg_rows)
    marg.to_csv(os.path.join(HERE, "marginal_growth_by_cutoff_episode.csv"), index=False)

    stability = marg.groupby("cutoff")["marginal_growth"].agg(["mean", "std", "count"])
    stability["cv"] = stability["std"] / stability["mean"].abs()
    stability.to_csv(os.path.join(HERE, "cutoff_stability_cv.csv"))
    print(stability, file=sys.stderr)

    best_cutoff = stability["cv"].idxmin()
    print(f"\n>>> LOCKED cutoff by min-CV stability rule: {best_cutoff}%", file=sys.stderr)
    with open(os.path.join(HERE, "LOCKED_CUTOFF.txt"), "w") as f:
        f.write(f"{best_cutoff}\n")


if __name__ == "__main__":
    main()
