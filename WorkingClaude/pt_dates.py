# -*- coding: utf-8 -*-
"""Auto-detect safe END_DATE for paper-trade sims.

Returns min of (today-1, lagged_pos_ov max, 5state max, BQ ticker max).
intraday_full.pkl is NOT a hard cap — sim falls back to T+1 Open when missing.
"""
import os, pickle
import pandas as pd
from datetime import datetime

WORKDIR = r"/home/trido/thanhdt/WorkingClaude"
START_DATE = "2026-04-01"  # paper-trade window start (canonical)


def detect_end_date(bq_check=False) -> str:
    cands = [pd.Timestamp(datetime.now().date()) - pd.Timedelta(days=1)]
    try:
        with open(os.path.join(WORKDIR, "data/lagged_pos_ov.pkl"), "rb") as f:
            ov = pickle.load(f)
        cands.append(pd.to_datetime(ov["time"]).max())
    except Exception:
        pass
    if bq_check:
        try:
            import subprocess
            r = subprocess.run(
                ["bq", "query", "--use_legacy_sql=false",
                 "--project_id=lithe-record-440915-m9", "--format=csv",
                 "SELECT MAX(s.time) FROM tav2_bq.vnindex_5state_dt5g_live AS s"],
                capture_output=True, text=True, timeout=30)
            lines = [l for l in r.stdout.splitlines() if l and not l.startswith("f0_")]
            if lines:
                cands.append(pd.Timestamp(lines[0]))
        except Exception:
            pass
    return min(cands).strftime("%Y-%m-%d")


if __name__ == "__main__":
    print(f"START_DATE={START_DATE}")
    print(f"END_DATE={detect_end_date(bq_check=True)}")
