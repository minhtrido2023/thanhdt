#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""discretionary_funnel_adaptive_pb_redo_20260830 — bước 5 (áp lên hôm nay) + bước 3 (ADV).

CHỈ chạy SAU KHI cutoff (70%, LOCKED_CUTOFF.txt) và ceiling (1.5) đã khoá xong ở
run_episode_sensitivity.py — không đụng lại 2 tham số đó ở đây, kể cả nếu TV1/DGC không lọt.
"""
import os
import subprocess
import sys
from io import StringIO

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = "lithe-record-440915-m9"
PB_MAX_ABS = 1.0
PB_MAX_CEIL = 1.5
WASHOUT_MIN = -0.30
DD52_MAX = -0.20

with open(os.path.join(HERE, "LOCKED_CUTOFF.txt")) as f:
    LOCKED_CUTOFF = int(f.read().strip())


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
    asof_df = bq_csv("SELECT MAX(time) AS asof FROM `lithe-record-440915-m9.tav2_bq.ticker`")
    asof = str(asof_df["asof"].iloc[0])
    window_start = (pd.Timestamp(asof) - pd.Timedelta(days=460)).date().isoformat()
    print(f"asof={asof} window_start={window_start}", file=sys.stderr)

    with open(os.path.join(HERE, "episode_cohort_query.sql")) as f:
        template = f.read()
    sql = template.replace("{TROUGH}", asof).replace("{WINDOW_START}", window_start)
    df = bq_csv(sql)
    df.to_csv(os.path.join(HERE, "today_cross_section.csv"), index=False)

    cohort = df[(df["washout_pct"] <= WASHOUT_MIN) & (df["dd52_pct"] <= DD52_MAX)].copy()
    cohort.to_csv(os.path.join(HERE, "today_cohort_washout_dd52.csv"), index=False)

    abs_qualify = cohort["PB"] < PB_MAX_ABS
    or_qualify = abs_qualify | ((cohort["pb_pct_rank"] <= LOCKED_CUTOFF / 100.0) & (cohort["PB"] < PB_MAX_CEIL))
    cohort["qualify_abs"] = abs_qualify
    cohort["qualify_or"] = or_qualify
    cohort["qualify_via"] = "none"
    cohort.loc[abs_qualify, "qualify_via"] = "absolute"
    cohort.loc[(~abs_qualify) & or_qualify, "qualify_via"] = "percentile"

    n_abs = int(abs_qualify.sum())
    n_or = int(or_qualify.sum())
    new_names = cohort.loc[cohort["qualify_via"] == "percentile", "ticker"].tolist()

    print(f"asof={asof} washout+dd52 cohort n={len(cohort)}", file=sys.stderr)
    print(f"n_abs(PB<1.0)={n_abs}  n_OR(cutoff={LOCKED_CUTOFF}%,ceil=1.5)={n_or}  n_new={len(new_names)}", file=sys.stderr)
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
                print(f"{tk}: not found in universe_pit cross-section today (delisted/excluded/no data)", file=sys.stderr)

    cohort.sort_values("PB").to_csv(os.path.join(HERE, "today_qualify_result.csv"), index=False)

    # ADV cho MOI ten qualify qua nhanh percentile (khong chi 4 ma CTCK)
    if new_names:
        tickers_sql = ",".join(f"'{t}'" for t in new_names)
        adv_sql = f"""
SELECT ticker, time, Trading_Value_1M_P50, Trading_Value, Volume_1M_P50, Risk_Rating
FROM `lithe-record-440915-m9.tav2_bq.ticker_1m`
WHERE ticker IN ({tickers_sql})
QUALIFY ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) = 1
"""
        adv = bq_csv(adv_sql)
        adv.to_csv(os.path.join(HERE, "new_names_adv.csv"), index=False)
        print(adv.to_string(), file=sys.stderr)
    else:
        print("no new names via percentile branch today", file=sys.stderr)


if __name__ == "__main__":
    main()
