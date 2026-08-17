#!/usr/bin/env python3
"""Build the two read-only panels this program needs. No table/view is created.

Panel A (`out/q1_events.csv`)  — one executed ISS event, session-indexed Close around exright_date.
Panel B (`out/q2_panel.csv`)   — month-end (ticker, date) valuation snapshot + raiser state + fwd ret.
Panel V (`out/vnindex.csv`)    — VNINDEX daily Close, the BHAR benchmark leg.

Design is locked in PREREG.md; this file only executes it. Two invariants worth naming because
breaking either is silent:
  * `Close` is the ADJUSTED series and is used for RETURNS ONLY. `PE`/`PB` are read as stored
    (already on the raw `Price` basis, registry `valuation_pe_pb_pcf_ps.md` bẫy (4)) and are never
    rescaled. No expression mixes the two bases.
  * horizons are counted in the TICKER'S OWN sessions via ROW_NUMBER, not in calendar days, so a
    suspension shortens nothing silently.
"""
from __future__ import annotations

import csv
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SQLDIR = os.path.join(OUT, "sql")
PROJECT = "lithe-record-440915-m9"

# Price history starts early enough that a 2010-01 panel row has a full 500-session lookback.
PX_START = "2007-01-01"
# Q1 anchors: 2010 onward so the 3Y-lookback logic and the dense corp-action era line up with Q2.
Q1_MIN, Q1_MAX = "2010-01-01", "2026-06-15"
# Q2 monthly panel window (month-ends).
Q2_MIN, Q2_MAX = "2010-01-01", "2026-05-31"

# Audited taxonomy, reused verbatim from ca_lib.ISS_SUBTYPE_BY_METHOD_CODE (Sprint 1).
SUBTYPE_CASE = """CASE c.issue_method_code
  WHEN 'DIV' THEN 'STOCK_DIVIDEND' WHEN 'Bonus' THEN 'BONUS' WHEN 'Rights' THEN 'RIGHTS'
  WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT' WHEN 'TRANS' THEN 'CONVERTIBLE'
  WHEN 'ICRE' THEN 'CONVERTIBLE' WHEN 'PUBL' THEN 'AUCTION' WHEN 'MERGER' THEN 'MERGER'
  ELSE 'UNKNOWN' END"""

RAISE_SET = ("RIGHTS", "PRIVATE_PLACEMENT", "AUCTION")
WIDE_SET = RAISE_SET + ("ESOP", "CONVERTIBLE")


def _in(vals: tuple[str, ...]) -> str:
    return "(" + ",".join(f"'{v}'" for v in vals) + ")"


def bq(sql: str, name: str, timeout: int = 3600) -> list[dict]:
    """Run read-only SQL through the bq CLI; return rows as dicts.

    `--max_rows` is mandatory: the CLI truncates at 100 rows by default and still exits 0
    (real incident 2026-08-13, `oshares_live`). A truncated read looks exactly like a short history.
    """
    os.makedirs(SQLDIR, exist_ok=True)
    path = os.path.join(SQLDIR, name + ".sql")
    with open(path, "w") as fh:
        fh.write(sql)
    exe = shutil.which("bq") or "/home/trido/google-cloud-sdk/bin/bq"
    env = os.environ.copy()
    env["PATH"] = "/home/trido/google-cloud-sdk/bin:" + env.get("PATH", "")
    env.setdefault("CLOUDSDK_CONFIG", "/home/trido/thanhdt/gcloud_dtienthanh")
    with open(path) as fh:
        p = subprocess.run(
            [exe, "query", "--use_legacy_sql=false", "--format=csv",
             f"--project_id={PROJECT}", "--max_rows=5000000", "--quiet"],
            stdin=fh, text=True, capture_output=True, timeout=timeout, env=env)
    if p.returncode:
        raise RuntimeError(f"bq rc={p.returncode} [{name}]\n{p.stdout[-3000:]}\n{p.stderr[-3000:]}")
    lines = [x for x in p.stdout.splitlines() if x.strip()]
    return list(csv.DictReader(lines)) if lines else []


def dump(name: str, rows: list[dict]) -> str:
    path = os.path.join(OUT, name)
    if not rows:
        open(path, "w").close()
        return path
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return path


# --------------------------------------------------------------------------------------------
# Shared event CTE. Dedup key + survivor rule identical to sprint4_build.py's RAW CTE: same-day
# rows with DIFFERENT terms are real separate tranches (ledger A1/A2) and must not be collapsed.
# --------------------------------------------------------------------------------------------
EVENTS_CTE = f"""
raw AS (
  SELECT c.ticker, c.exright_date, c.id, c.public_date, c.exercise_ratio, c.issue_volumn,
         c.total_value, {SUBTYPE_CASE} AS subtype,
         ROW_NUMBER() OVER (PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
             CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING),
             CAST(c.total_value AS STRING)
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{PROJECT}.tav2_bq.corporate_action` c
  WHERE c.event_code = 'ISS' AND c.event_status = 'executed' AND c.exright_date IS NOT NULL
),
ev_all AS (SELECT * FROM raw WHERE rn = 1 AND subtype <> 'UNKNOWN')
"""

# Session-indexed price frame. `si` is the ticker's own session number.
PX_CTE = f"""
px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.ICB_Code,
         SAFE_DIVIDE(t.Close, LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret,
         ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time) AS si
  FROM `{PROJECT}.tav2_bq.ticker` t
  WHERE t.time >= DATE '{PX_START}' AND t.Close > 0 AND t.ticker <> 'VNINDEX'
)
"""

# --------------------------------------------------------------------------------------------
# Panel A — Q1 long-run BHAR event panel
# --------------------------------------------------------------------------------------------
# Offsets: -500/-250 for the far placebo and the pre-trend, 0 for entry, +250/+500/+750 outcomes.
Q1_SQL = f"""
WITH {EVENTS_CTE},
{PX_CTE},
ev AS (
  SELECT ticker, exright_date AS t0, subtype,
         COUNT(*) AS n_components,
         SUM(SAFE_CAST(exercise_ratio AS FLOAT64)) AS ratio_total,
         SUM(SAFE_CAST(issue_volumn AS FLOAT64)) AS issue_volume,
         SUM(SAFE_CAST(total_value AS FLOAT64)) AS total_value
  FROM ev_all
  WHERE exright_date BETWEEN DATE '{Q1_MIN}' AND DATE '{Q1_MAX}'
  GROUP BY ticker, t0, subtype
),
-- PIT universe gate: in_universe must be TRUE on the anchor date itself.
gated AS (
  SELECT e.* FROM ev e
  JOIN `{PROJECT}.tav2_mike.universe_pit` u
    ON u.ticker = e.ticker AND u.time = e.t0 AND u.in_universe
),
anchored AS (
  SELECT g.*, p.si AS si0 FROM gated g JOIN px p ON p.ticker = g.ticker AND p.time = g.t0
),
w AS (
  SELECT a.*, p.si - a.si0 AS k, p.time AS dt, p.Close, p.Price, p.Volume, p.ICB_Code, p.ret
  FROM anchored a JOIN px p
    ON p.ticker = a.ticker AND p.si BETWEEN a.si0 - 500 AND a.si0 + 750
)
SELECT ticker, t0, ANY_VALUE(subtype) AS subtype,
       ANY_VALUE(n_components) AS n_components, ANY_VALUE(ratio_total) AS ratio_total,
       ANY_VALUE(issue_volume) AS issue_volume, ANY_VALUE(total_value) AS total_value,
       MAX(IF(k = -500, Close, NULL)) AS c_m500, MAX(IF(k = -500, dt, NULL)) AS d_m500,
       MAX(IF(k = -250, Close, NULL)) AS c_m250, MAX(IF(k = -250, dt, NULL)) AS d_m250,
       MAX(IF(k =    0, Close, NULL)) AS c_0,    MAX(IF(k =    0, dt, NULL)) AS d_0,
       MAX(IF(k =  250, Close, NULL)) AS c_250,  MAX(IF(k =  250, dt, NULL)) AS d_250,
       MAX(IF(k =  500, Close, NULL)) AS c_500,  MAX(IF(k =  500, dt, NULL)) AS d_500,
       MAX(IF(k =  750, Close, NULL)) AS c_750,  MAX(IF(k =  750, dt, NULL)) AS d_750,
       MAX(IF(k =   -1, ICB_Code, NULL)) AS icb,
       AVG(IF(k BETWEEN -60 AND -6, Price * Volume, NULL)) AS adv60,
       STDDEV(IF(k BETWEEN -60 AND -1, ret, NULL)) AS rvol60,
       EXP(SUM(IF(k BETWEEN -126 AND -21, LN(1 + ret), 0))) - 1 AS mom6m,
       COUNTIF(k >= 0) AS n_sessions_fwd
FROM w
GROUP BY ticker, t0
ORDER BY ticker, t0
"""

VNI_SQL = f"""
SELECT time, Close FROM `{PROJECT}.tav2_bq.ticker`
WHERE ticker = 'VNINDEX' AND time >= DATE '{PX_START}' AND Close > 0
ORDER BY time
"""

# --------------------------------------------------------------------------------------------
# Panel B — Q2 monthly cross-section
# --------------------------------------------------------------------------------------------
# `fwd_ret_1m` is computed on the ticker's OWN month-end series BEFORE the universe gate is
# applied, so a name leaving the universe next month still contributes the return of the month we
# held it. Gating first would be survivorship bias in the return leg.
Q2_SQL = f"""
WITH {EVENTS_CTE},
{PX_CTE},
me AS (  -- last session of each calendar month, per ticker
  SELECT ticker, time, Close, Price, Volume,
         DATE_TRUNC(time, MONTH) AS mth,
         ROW_NUMBER() OVER (PARTITION BY ticker, DATE_TRUNC(time, MONTH) ORDER BY time DESC) AS rn_m
  FROM px
),
mend AS (
  SELECT ticker, mth, time AS d_t, Close,
         LEAD(Close) OVER (PARTITION BY ticker ORDER BY mth) AS close_next,
         LEAD(mth)   OVER (PARTITION BY ticker ORDER BY mth) AS mth_next
  FROM me WHERE rn_m = 1
),
rets AS (
  SELECT ticker, mth, d_t, Close,
         -- only a CONSECUTIVE month counts as a 1-month forward return; a gap yields NULL
         IF(mth_next = DATE_ADD(mth, INTERVAL 1 MONTH),
            SAFE_DIVIDE(close_next, Close) - 1, NULL) AS fwd_ret_1m,
         IF(mth_next = DATE_ADD(mth, INTERVAL 1 MONTH), 0, 1) AS fwd_gap
  FROM mend
),
snap AS (  -- valuation + controls read AS STORED on the same session (PIT)
  -- DEVIATION D1: PREREG named ROE_Trailing and Revenue_YoY_P0; neither column exists in
  -- `tav2_bq.ticker` (they live in `ticker_financial`). Substituted the nearest available
  -- same-table columns rather than adding a second join whose PIT semantics I have not audited:
  -- ROIC_Trailing (trailing 4Q), NPM_P0, FSCORE (Piotroski, absorbs part of the growth/quality
  -- axis). Recorded in DEVIATIONS.md.
  SELECT t.ticker, t.time AS d_t, t.PE, t.PB, t.ICB_Code, t.ROIC_Trailing, t.NPM_P0,
         t.FSCORE, t.Debt_Eq_P0
  FROM `{PROJECT}.tav2_bq.ticker` t
  WHERE t.time >= DATE '{Q2_MIN}' AND t.time <= DATE '{Q2_MAX}'
),
advs AS (
  SELECT ticker, time AS d_t,
         AVG(Price * Volume) OVER (PARTITION BY ticker ORDER BY si
                                   ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) AS adv60
  FROM px
),
base AS (
  SELECT r.ticker, r.mth, r.d_t, r.Close, r.fwd_ret_1m, r.fwd_gap,
         s.PE, s.PB, s.ICB_Code, s.ROIC_Trailing, s.NPM_P0, s.FSCORE, s.Debt_Eq_P0, a.adv60
  FROM rets r
  JOIN `{PROJECT}.tav2_mike.universe_pit` u
    ON u.ticker = r.ticker AND u.time = r.d_t AND u.in_universe
  JOIN snap s ON s.ticker = r.ticker AND s.d_t = r.d_t
  LEFT JOIN advs a ON a.ticker = r.ticker AND a.d_t = r.d_t
  WHERE r.mth BETWEEN DATE '{Q2_MIN}' AND DATE '{Q2_MAX}'
),
-- raiser state: PIT by construction, only ex-dates at or before d_t enter the count
cnt AS (
  SELECT b.ticker, b.mth,
    COUNTIF(e.subtype IN {_in(RAISE_SET)}) AS n_raise_3y,
    COUNTIF(e.subtype IN {_in(WIDE_SET)})  AS n_wide_3y,
    COUNT(e.ticker)                        AS n_all_3y
  FROM base b LEFT JOIN ev_all e
    ON e.ticker = b.ticker
   AND e.exright_date >  DATE_SUB(b.d_t, INTERVAL 1095 DAY)
   AND e.exright_date <= b.d_t
  GROUP BY b.ticker, b.mth
),
-- FUTURE-window probe (falsification #3): events strictly AFTER d_t. Never used as a regressor
-- in the primary; it exists to show whether the "discount" is information or firm character.
fut AS (
  SELECT b.ticker, b.mth, COUNTIF(e.subtype IN {_in(RAISE_SET)}) AS n_raise_fwd180
  FROM base b LEFT JOIN ev_all e
    ON e.ticker = b.ticker
   AND e.exright_date >  b.d_t
   AND e.exright_date <= DATE_ADD(b.d_t, INTERVAL 180 DAY)
  GROUP BY b.ticker, b.mth
)
SELECT b.ticker, b.mth, b.d_t, b.Close, b.fwd_ret_1m, b.fwd_gap,
       b.PE, b.PB, b.ICB_Code AS icb, b.ROIC_Trailing, b.NPM_P0, b.FSCORE, b.Debt_Eq_P0, b.adv60,
       c.n_raise_3y, c.n_wide_3y, c.n_all_3y, f.n_raise_fwd180
FROM base b
JOIN cnt c ON c.ticker = b.ticker AND c.mth = b.mth
JOIN fut f ON f.ticker = b.ticker AND f.mth = b.mth
ORDER BY b.mth, b.ticker
"""

# Raw event rows in Q1 scope, for the dedup-lineage selfcheck (T3).
LINEAGE_SQL = f"""
WITH {EVENTS_CTE}
SELECT ticker, exright_date, subtype, id FROM ev_all
WHERE exright_date BETWEEN DATE '{Q1_MIN}' AND DATE '{Q1_MAX}'
ORDER BY ticker, exright_date, id
"""

RAWCOUNT_SQL = f"""
SELECT COUNT(*) AS n_raw, COUNT(DISTINCT id) AS n_ids
FROM `{PROJECT}.tav2_bq.corporate_action`
WHERE event_code = 'ISS' AND event_status = 'executed' AND exright_date IS NOT NULL
  AND exright_date BETWEEN DATE '{Q1_MIN}' AND DATE '{Q1_MAX}'
"""


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    summary: dict[str, object] = {}

    print("[1/5] VNINDEX benchmark leg ...", flush=True)
    vni = bq(VNI_SQL, "vnindex")
    dump("vnindex.csv", vni)
    summary["vnindex_sessions"] = len(vni)

    print("[2/5] Q1 event panel ...", flush=True)
    q1 = bq(Q1_SQL, "q1_events")
    dump("q1_events.csv", q1)
    summary["q1_events"] = len(q1)
    summary["q1_tickers"] = len({r["ticker"] for r in q1})

    print("[3/5] event lineage (selfcheck input) ...", flush=True)
    lin = bq(LINEAGE_SQL, "lineage")
    dump("lineage.csv", lin)
    summary["lineage_rows"] = len(lin)
    rc = bq(RAWCOUNT_SQL, "rawcount")
    summary["raw_iss_rows_in_window"] = int(rc[0]["n_raw"]) if rc else None

    print("[4/5] Q2 monthly panel ... (largest pull)", flush=True)
    q2 = bq(Q2_SQL, "q2_panel")
    dump("q2_panel.csv", q2)
    summary["q2_rows"] = len(q2)
    summary["q2_tickers"] = len({r["ticker"] for r in q2})
    summary["q2_months"] = len({r["mth"] for r in q2})

    print("[5/5] summary ...", flush=True)
    with open(os.path.join(OUT, "build_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
