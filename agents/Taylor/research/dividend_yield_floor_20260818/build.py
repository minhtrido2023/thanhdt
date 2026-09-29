#!/usr/bin/env python3
"""build.py — assemble the PIT trailing-dividend-yield daily panel (PREREG.md §1-§4).

Read-only against BigQuery. Every artifact lands in `out/`. No table/view/cron is created.

Two design choices that matter more than the code
-------------------------------------------------
1. **Trailing yield is built as a STEP FUNCTION, not a range join.** `trailing_div(t)` only
   changes on two kinds of day: an ex-date (a dividend enters the 365-day window) and
   ex-date + 365 (it leaves). Emitting `+D` at `ex` and `-D` at `ex+365` and running a
   cumulative sum over the merged (price-date, step-date) timeline is exact and costs one
   window function; a `BETWEEN t-365 AND t` self-join on a 3M-row panel is not.
   Generalised to five 365-day buckets k=0..4 so the STABLE-3 / STABLE-5 flags of PREREG §2
   come out of the same pass.

2. **The yield denominator is `Price` (raw), the return numerator is `Close` (adjusted).**
   `value_per_share` is nominal VND per share at payment time, so dividing it by the
   back-adjusted `Close` would inflate the yield by every adjustment factor that happens
   AFTER t — look-ahead wearing a plausible mask. Returns are the mirror image: they must be
   measured on the adjusted series. Mixing these up is the single easiest way to fake this
   whole result, so both columns ship and `selfcheck.py` asserts which is used where.
"""
from __future__ import annotations

import csv
import gzip
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SQLDIR = os.path.join(OUT, "sql")
BQ_PROJECT = "lithe-record-440915-m9"

DIV_MIN = "2010-01-01"     # PREREG §2 — dividend history floor
PANEL_START = "2012-06-01"  # >= 365 sessions of lookback before the first study date
STUDY_MIN = "2014-01-01"   # PREREG §4.1 — DT5G starts 2014-01-02
STUDY_MAX = "2026-06-15"


def bq_csv(sql: str, name: str, timeout: int = 3600) -> list[dict]:
    """Run read-only SQL from a file, return list of dict rows.

    `--max_rows` is mandatory: the CLI silently truncates at 100 rows and still exits 0.
    CSV rather than JSON because `--format=json` stringifies every numeric and is ~4x bytes.
    """
    os.makedirs(SQLDIR, exist_ok=True)
    path = os.path.join(SQLDIR, f"{name}.sql")
    with open(path, "w") as fh:
        fh.write(sql)
    cmd = ["bq", "query", "--use_legacy_sql=false", "--format=csv",
           f"--project_id={BQ_PROJECT}", "--max_rows=5000000", "--quiet"]
    with open(path) as fh:
        p = subprocess.run(cmd, stdin=fh, capture_output=True, text=True, timeout=timeout)
    if p.returncode != 0:
        raise RuntimeError(f"bq failed rc={p.returncode} ({name})\n{p.stderr[-3000:]}")
    lines = [ln for ln in p.stdout.splitlines() if ln.strip()]
    return list(csv.DictReader(lines)) if lines else []


def write_gz(rows: list[dict], path: str, fields: list[str] | None = None) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty {path}")
    fields = fields or list(rows[0].keys())
    with gzip.open(path, "wt", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def write_csv(rows: list[dict], path: str) -> None:
    if not rows:
        raise RuntimeError(f"refusing to write empty {path}")
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


# ============================================================================================
# SQL
# ============================================================================================
# Economic dedup key for DIV, identical to Sprint 1 §7.1 / Sprint 2 (registry Bay 3): collapsing
# on (ticker, ex-date) alone silently halves a company paying two tranches on one ex-date.
DIV_DEDUP = f"""
  SELECT c.ticker, c.exright_date AS ex, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{BQ_PROJECT}.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV'
    AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL
    AND c.value_per_share > 0
"""

DIV_EVENTS = f"""
WITH dd AS ({DIV_DEDUP})
SELECT ticker, ex AS ex_date, SUM(value_per_share) AS div_total, COUNT(*) AS n_tranche
FROM dd WHERE rn = 1 AND ex >= DATE '{DIV_MIN}'
GROUP BY ticker, ex
ORDER BY ticker, ex
"""

# First trading day per ticker over the WHOLE table (not the panel window) — PREREG §4.1 item 3
# needs "3 years of price history before t", which a panel censored at PANEL_START cannot answer.
FIRST_DT = f"""
SELECT t.ticker, MIN(t.time) AS first_dt, COUNT(*) AS n_rows
FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
WHERE t.Close IS NOT NULL AND t.Close > 0
GROUP BY t.ticker
"""

# Equal-weighted point-in-time universe return (verbatim shape from Sprint 2 `EWUNIV`).
# Membership is required at BOTH ends of each daily return so a name entering/leaving the
# universe cannot manufacture one. |ret| > 50% is a broken price row, not a session.
EWUNIV = f"""
WITH u AS (
  SELECT up.time, up.ticker FROM `{BQ_PROJECT}.tav2_mike.universe_pit` AS up
  WHERE up.in_universe AND up.time >= DATE '{PANEL_START}'
),
p AS (
  SELECT t.ticker, t.time, t.Close,
         LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_prev,
         LAG(t.time)  OVER (PARTITION BY t.ticker ORDER BY t.time) AS t_prev
  FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '{PANEL_START}' AND t.Close IS NOT NULL AND t.Close > 0
),
r AS (
  SELECT p.time AS dt, p.ticker, p.Close / p.c_prev - 1 AS ret
  FROM p
  JOIN u        ON u.ticker = p.ticker AND u.time = p.time
  JOIN u AS upv ON upv.ticker = p.ticker AND upv.time = p.t_prev
  WHERE p.c_prev IS NOT NULL AND p.c_prev > 0
)
SELECT dt, AVG(IF(ABS(ret) <= 0.5, ret, NULL)) AS ew_ret,
       AVG(ret) AS ew_ret_raw, COUNT(*) AS n_names, COUNTIF(ABS(ret) > 0.5) AS n_impossible
FROM r GROUP BY dt ORDER BY dt
"""

VNINDEX = f"""
SELECT t.time AS dt, t.Close AS c
FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
WHERE t.ticker = 'VNINDEX' AND t.time >= DATE '{PANEL_START}' AND t.Close > 0
ORDER BY t.time
"""

DT5G = f"""
SELECT time AS dt, state FROM `{BQ_PROJECT}.tav2_bq.vnindex_5state_dt5g_live` ORDER BY time
"""

# ---- the panel ------------------------------------------------------------------------------
# `steps`: five 365-day buckets. Event D at ex enters bucket k on ex+365k and leaves on
# ex+365(k+1)  =>  bucket k is active at t iff  t-365(k+1) < ex <= t-365k  (PREREG §2, exact).
# Ordering the cumulative sum by (d, is_px) with step rows first makes the ex-date itself count,
# which is the PIT-correct boundary: from the ex-session on, the price has already adjusted down
# and the entitlement is fixed.
PANEL = f"""
WITH dd AS ({DIV_DEDUP}),
ev AS (
  SELECT ticker, ex, SUM(value_per_share) AS dv
  FROM dd WHERE rn = 1 AND ex >= DATE '{DIV_MIN}'
  GROUP BY ticker, ex
),
steps_raw AS (
  SELECT ticker, DATE_ADD(ex, INTERVAL 365 * b DAY) AS d, b AS bk, dv, 1 AS ct
  FROM ev, UNNEST([0,1,2,3,4]) AS b
  UNION ALL
  SELECT ticker, DATE_ADD(ex, INTERVAL 365 * (b + 1) DAY) AS d, b AS bk, -dv, -1 AS ct
  FROM ev, UNNEST([0,1,2,3,4]) AS b
),
steps AS (
  SELECT ticker, d,
         SUM(IF(bk=0, dv, 0)) AS s_dv0, SUM(IF(bk=0, ct, 0)) AS s_ct0,
         SUM(IF(bk=1, ct, 0)) AS s_ct1, SUM(IF(bk=2, ct, 0)) AS s_ct2,
         SUM(IF(bk=3, ct, 0)) AS s_ct3, SUM(IF(bk=4, ct, 0)) AS s_ct4
  FROM steps_raw GROUP BY ticker, d
),
-- every exright_date of ANY corp-action for the ticker: PREREG §4.2 disqualifies those rows
-- because `ticker.Price` can sit at the T-1 reference frame exactly there (registry TRAP).
exd AS (
  SELECT DISTINCT ticker, exright_date AS d
  FROM `{BQ_PROJECT}.tav2_bq.corporate_action`
  WHERE exright_date IS NOT NULL
),
px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Low, t.High, t.Volume, t.PE, t.PB, t.DY,
         t.ICB_Code,
         SAFE_DIVIDE(t.Close, LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret
  FROM `{BQ_PROJECT}.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '{PANEL_START}' AND t.time <= DATE '{STUDY_MAX}'
    AND t.Close IS NOT NULL AND t.Close > 0 AND t.ticker != 'VNINDEX'
),
pxw AS (
  SELECT ticker, time, Close, Price, Low, High, Volume, PE, PB, DY, ICB_Code, ret,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time) AS si,
         STDDEV(ret) OVER (PARTITION BY ticker ORDER BY time
                           ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS rvol60,
         AVG(Volume * Price) OVER (PARTITION BY ticker ORDER BY time
                           ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS advnd60,
         LEAD(Close,  20) OVER (PARTITION BY ticker ORDER BY time) AS c_p20,
         LEAD(time,   20) OVER (PARTITION BY ticker ORDER BY time) AS d_p20,
         LEAD(Close,  60) OVER (PARTITION BY ticker ORDER BY time) AS c_p60,
         LEAD(time,   60) OVER (PARTITION BY ticker ORDER BY time) AS d_p60,
         LEAD(Close, 120) OVER (PARTITION BY ticker ORDER BY time) AS c_p120,
         LEAD(time,  120) OVER (PARTITION BY ticker ORDER BY time) AS d_p120,
         MIN(Close) OVER (PARTITION BY ticker ORDER BY time
                          ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING) AS minc60,
         MAX(Close) OVER (PARTITION BY ticker ORDER BY time
                          ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING) AS maxc60,
         COUNT(Close) OVER (PARTITION BY ticker ORDER BY time
                            ROWS BETWEEN 1 FOLLOWING AND 60 FOLLOWING) AS n_fwd60
  FROM px
),
tl AS (
  SELECT ticker, time AS d, 1 AS is_px,
         0.0 AS s_dv0, 0 AS s_ct0, 0 AS s_ct1, 0 AS s_ct2, 0 AS s_ct3, 0 AS s_ct4,
         si, Close, Price, Low, High, Volume, PE, PB, DY, ICB_Code, ret, rvol60, advnd60,
         c_p20, d_p20, c_p60, d_p60, c_p120, d_p120, minc60, maxc60, n_fwd60
  FROM pxw
  UNION ALL
  SELECT ticker, d, 0 AS is_px,
         s_dv0, s_ct0, s_ct1, s_ct2, s_ct3, s_ct4,
         NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
         NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL
  FROM steps
),
cum AS (
  SELECT ticker, d, is_px, si, Close, Price, Low, High, Volume, PE, PB, DY, ICB_Code, ret,
         rvol60, advnd60, c_p20, d_p20, c_p60, d_p60, c_p120, d_p120, minc60, maxc60, n_fwd60,
         SUM(s_dv0) OVER w AS div0,
         SUM(s_ct0) OVER w AS n0, SUM(s_ct1) OVER w AS n1, SUM(s_ct2) OVER w AS n2,
         SUM(s_ct3) OVER w AS n3, SUM(s_ct4) OVER w AS n4
  FROM tl
  WINDOW w AS (PARTITION BY ticker ORDER BY d, is_px ROWS UNBOUNDED PRECEDING)
)
SELECT c.ticker, c.d AS dt, c.si, c.Close AS close, c.Price AS price, c.Low AS low,
       c.High AS high, c.Volume AS volume, c.PE AS pe, c.PB AS pb, c.DY AS dy,
       c.ICB_Code AS icb, c.ret, c.rvol60, c.advnd60,
       c.c_p20, c.d_p20, c.c_p60, c.d_p60, c.c_p120, c.d_p120,
       c.minc60, c.maxc60, c.n_fwd60,
       ROUND(c.div0, 6) AS div0, c.n0, c.n1, c.n2, c.n3, c.n4,
       IF(x.d IS NULL, 0, 1) AS is_exdate
FROM cum AS c
JOIN `{BQ_PROJECT}.tav2_mike.universe_pit` AS u
  ON u.ticker = c.ticker AND u.time = c.d AND u.in_universe
LEFT JOIN exd AS x ON x.ticker = c.ticker AND x.d = c.d
WHERE c.is_px = 1
  AND c.d BETWEEN DATE '{STUDY_MIN}' AND DATE '{STUDY_MAX}'
  AND c.Price IS NOT NULL AND c.Price > 0
  -- PREREG §2: keep only STABLE-3 rows and clean NON-PAYER rows; the grey zone is dropped
  -- rather than assigned to whichever group would be convenient.
  AND ((c.n0 >= 1 AND c.n1 >= 1 AND c.n2 >= 1) OR (c.n0 = 0 AND c.n1 = 0 AND c.n2 = 0))
ORDER BY c.ticker, c.d
"""


def main() -> int:
    os.makedirs(OUT, exist_ok=True)
    summary: dict = {"built_at_utc": datetime.now(timezone.utc).isoformat(),
                     "study_window": [STUDY_MIN, STUDY_MAX], "div_min": DIV_MIN,
                     "panel_start": PANEL_START}

    print("[1/6] DIV events (deduped)")
    ev = bq_csv(DIV_EVENTS, "q1_div_events")
    write_gz(ev, os.path.join(OUT, "div_events.csv.gz"))
    summary["n_div_events"] = len(ev)
    summary["n_div_tickers"] = len({r["ticker"] for r in ev})
    print(f"      {len(ev)} events / {summary['n_div_tickers']} tickers")

    print("[2/6] first trading day per ticker")
    fd = bq_csv(FIRST_DT, "q2_first_dt")
    write_csv(fd, os.path.join(OUT, "first_dt.csv"))
    summary["n_tickers_all"] = len(fd)

    print("[3/6] EW universe_pit benchmark")
    ew = bq_csv(EWUNIV, "q3_ew_universe")
    write_csv(ew, os.path.join(OUT, "bench_ew.csv"))
    summary["n_bench_days"] = len(ew)

    print("[4/6] VNINDEX")
    vn = bq_csv(VNINDEX, "q4_vnindex")
    write_csv(vn, os.path.join(OUT, "vnindex.csv"))

    print("[5/6] DT5G state (vnindex_5state_dt5g_live — NOT the base table)")
    st = bq_csv(DT5G, "q5_dt5g")
    write_csv(st, os.path.join(OUT, "dt5g.csv"))
    summary["n_state_days"] = len(st)

    print("[6/6] daily panel (this is the slow one)")
    pn = bq_csv(PANEL, "q6_panel")
    write_gz(pn, os.path.join(OUT, "panel.csv.gz"))
    summary["n_panel_rows"] = len(pn)
    summary["n_panel_tickers"] = len({r["ticker"] for r in pn})
    stable = sum(1 for r in pn if int(r["n0"]) >= 1 and int(r["n1"]) >= 1 and int(r["n2"]) >= 1)
    summary["n_panel_rows_stable3"] = stable
    summary["n_panel_rows_nonpayer"] = len(pn) - stable
    print(f"      {len(pn)} rows / {summary['n_panel_tickers']} tickers "
          f"({stable} STABLE-3, {len(pn)-stable} NON-PAYER)")

    with open(os.path.join(OUT, "build_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2)
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
