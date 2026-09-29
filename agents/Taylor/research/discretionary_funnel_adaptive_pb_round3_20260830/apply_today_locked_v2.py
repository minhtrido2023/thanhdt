#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discretionary_funnel_adaptive_pb_round3_20260830 — áp cutoff+ceiling ĐÃ KHOÁ (cả hai bằng
min-CV mechanical rule) lên dữ liệu hôm nay.

Tái dùng today_cross_section.csv của round 2 (basis universe_pit∩Volume>0, washout/dd52/PB/
pb_pct_rank — không phụ thuộc ceiling, không cần re-query BQ). Chỉ ceiling đổi (1.5 -> 1.2, do
min-CV sensitivity round 3 chọn), cutoff giữ nguyên 70%.
"""
import os
import subprocess
import sys
from io import StringIO

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROUND2 = os.path.normpath(os.path.join(HERE, "..", "discretionary_funnel_adaptive_pb_redo_20260830"))
PROJECT = "lithe-record-440915-m9"
PB_MAX_ABS = 1.0
WASHOUT_MIN = -0.30
DD52_MAX = -0.20

with open(os.path.join(ROUND2, "LOCKED_CUTOFF.txt")) as f:
    LOCKED_CUTOFF = int(f.read().strip())
with open(os.path.join(HERE, "LOCKED_CEILING.txt")) as f:
    LOCKED_CEILING = float(f.read().strip())


def bq_csv(sql):
    p = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", f"--project_id={PROJECT}",
         "--format=csv", "--max_rows=20000"],
        input=sql, capture_output=True, text=True, env=os.environ.copy(), timeout=180,
    )
    if p.returncode != 0:
        raise RuntimeError(f"bq query failed (rc={p.returncode}): stderr={p.stderr!r} stdout={p.stdout!r}")
    return pd.read_csv(StringIO(p.stdout))


def main():
    df = pd.read_csv(os.path.join(ROUND2, "today_cross_section.csv"))
    cohort = df[(df["washout_pct"] <= WASHOUT_MIN) & (df["dd52_pct"] <= DD52_MAX)].copy()

    abs_qualify = cohort["PB"] < PB_MAX_ABS
    or_qualify = abs_qualify | ((cohort["pb_pct_rank"] <= LOCKED_CUTOFF / 100.0) & (cohort["PB"] < LOCKED_CEILING))
    cohort["qualify_abs"] = abs_qualify
    cohort["qualify_or"] = or_qualify
    cohort["qualify_via"] = "none"
    cohort.loc[abs_qualify, "qualify_via"] = "absolute"
    cohort.loc[(~abs_qualify) & or_qualify, "qualify_via"] = "percentile"

    n_abs = int(abs_qualify.sum())
    n_or = int(or_qualify.sum())
    new_names = cohort.loc[cohort["qualify_via"] == "percentile", "ticker"].tolist()

    print(f"cutoff={LOCKED_CUTOFF}% ceiling={LOCKED_CEILING} (both min-CV locked)", file=sys.stderr)
    print(f"washout+dd52 cohort n={len(cohort)}", file=sys.stderr)
    print(f"n_abs(PB<1.0)={n_abs}  n_OR={n_or}  n_new={len(new_names)}", file=sys.stderr)
    print(f"new_names={sorted(new_names)}", file=sys.stderr)

    for tk in ["TV1", "DGC"]:
        row = cohort[cohort["ticker"] == tk]
        if len(row):
            r = row.iloc[0]
            print(f"{tk}: PB={r['PB']:.4f} pct_rank={r['pb_pct_rank']:.4f} qualify_via={r['qualify_via']}", file=sys.stderr)
        else:
            in_full = df[df["ticker"] == tk]
            if len(in_full):
                r = in_full.iloc[0]
                print(f"{tk}: NOT in washout+dd52 cohort today (PB={r['PB']}, washout={r['washout_pct']:.3f}, dd52={r['dd52_pct']:.3f})", file=sys.stderr)
            else:
                print(f"{tk}: not found in universe_pit cross-section today", file=sys.stderr)

    cohort.sort_values("PB").to_csv(os.path.join(HERE, "today_qualify_result_v2.csv"), index=False)

    if new_names:
        tickers_sql = ",".join(f"'{t}'" for t in new_names)
        adv_sql = f"""
SELECT ticker, time, Trading_Value_1M_P50, Trading_Value, Volume_1M_P50, Risk_Rating, ICB_Code
FROM `lithe-record-440915-m9.tav2_bq.ticker_1m`
WHERE ticker IN ({tickers_sql})
QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) = 1
"""
        adv = bq_csv(adv_sql)
        adv.to_csv(os.path.join(HERE, "new_names_adv_v2.csv"), index=False)
        print(adv.to_string(), file=sys.stderr)
    else:
        print("no new names via percentile branch today", file=sys.stderr)


if __name__ == "__main__":
    main()
