#!/usr/bin/env python3
"""Step 1 gate: what IS `corporate_action.listing_date`?

The dispatch hypothesis is that `listing_date` is the date the ISSUER NOTIFIED THE EXCHANGE — a
pre-event, publicly-certain anchor that would let us run an announcement-style study without
`public_date` (banned in Sprint 1 as WEAK_UNVERIFIED_VINTAGE). Under that hypothesis
`exright_date - listing_date` concentrates near +7..+15 calendar days (HOSE/HNX rules require
notice >= 5 working days before the record date).

This script measures the gap and cross-checks the rival hypothesis: `listing_date` is the date the
NEWLY ISSUED SHARES ARE LISTED (niem yet bo sung) — a POST-event date that equals the matching
`AIS.effective_date`.

Read-only. Dumps every table it measures to out/ so the GATE_REPORT can be recomputed.
"""
from __future__ import annotations

import csv
import os
import shutil
import subprocess

PROJECT = "lithe-record-440915-m9"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
SQLDIR = os.path.join(HERE, "sql")

# Audited taxonomy, reused verbatim from serial_capital_raiser_20260817/build.py (itself lifted
# from ca_lib.ISS_SUBTYPE_BY_METHOD_CODE, Sprint 1). Do not re-derive it here.
SUBTYPE_CASE = """CASE c.issue_method_code
  WHEN 'DIV' THEN 'STOCK_DIVIDEND' WHEN 'Bonus' THEN 'BONUS' WHEN 'Rights' THEN 'RIGHTS'
  WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT' WHEN 'TRANS' THEN 'CONVERTIBLE'
  WHEN 'ICRE' THEN 'CONVERTIBLE' WHEN 'PUBL' THEN 'AUCTION' WHEN 'MERGER' THEN 'MERGER'
  ELSE 'UNKNOWN' END"""

# Same dedup key + survivor rule as sprint4_build.py / serial_capital_raiser build.py: same-day
# rows with DIFFERENT terms are real separate tranches and must not be collapsed.
RAW_CTE = f"""
raw AS (
  SELECT c.ticker, c.exright_date, c.listing_date, c.public_date, c.record_date, c.id,
         c.exercise_ratio, c.event_title_vi, {SUBTYPE_CASE} AS subtype,
         ROW_NUMBER() OVER (PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
             CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING),
             CAST(c.total_value AS STRING)
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `{PROJECT}.tav2_bq.corporate_action` c
  WHERE c.event_code = 'ISS' AND c.event_status = 'executed'
),
ev AS (SELECT * FROM raw WHERE rn = 1 AND subtype <> 'UNKNOWN')
"""


def bq(sql: str, name: str, timeout: int = 900) -> list[dict]:
    """Run read-only SQL through the bq CLI; return rows as dicts.

    `--max_rows` is mandatory: the CLI truncates at 100 rows by default and still exits 0
    (real incident 2026-08-13, `oshares_live`). A truncated read looks exactly like short history.
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
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    if not rows:
        open(path, "w").close()
        return path
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return path


# ---------------------------------------------------------------------------------------------
# M1 — fill rate of listing_date across the WHOLE table, by event_code.
# DATA_DICTIONARY.md (Sprint 1) line 47 claims "100% NULL toan bang". M1 is the correction.
# ---------------------------------------------------------------------------------------------
M1 = f"""
SELECT event_code, COUNT(*) AS n,
       COUNTIF(listing_date IS NOT NULL) AS n_listing,
       ROUND(100 * COUNTIF(listing_date IS NOT NULL) / COUNT(*), 1) AS pct_listing
FROM `{PROJECT}.tav2_bq.corporate_action`
GROUP BY event_code ORDER BY n DESC
"""

# ---------------------------------------------------------------------------------------------
# M2 — signed gap distribution per ISS subtype.
# `gap_ex_minus_listing` uses the DISPATCH's sign convention: positive => listing_date precedes
# ex-date (the exchange-notification hypothesis). Negative => listing_date follows the ex-date.
# ---------------------------------------------------------------------------------------------
M2 = f"""
WITH {RAW_CTE},
g AS (
  SELECT subtype, ticker, exright_date, listing_date,
         DATE_DIFF(exright_date, listing_date, DAY) AS gap
  FROM ev
)
SELECT subtype,
  COUNT(*) AS n_events,
  COUNT(DISTINCT ticker) AS n_issuers,
  COUNTIF(listing_date IS NULL) AS n_null_listing,
  COUNTIF(exright_date IS NULL) AS n_null_exright,
  COUNTIF(gap IS NOT NULL) AS n_both,
  COUNTIF(gap > 0) AS n_listing_before_ex,
  COUNTIF(gap = 0) AS n_listing_eq_ex,
  COUNTIF(gap < 0) AS n_listing_after_ex,
  COUNTIF(gap BETWEEN 3 AND 30) AS n_gap_in_3_30,
  ROUND(100 * COUNTIF(gap BETWEEN 3 AND 30) / NULLIF(COUNTIF(gap IS NOT NULL), 0), 1)
    AS pct_gap_in_3_30,
  APPROX_QUANTILES(gap, 100)[OFFSET(5)]  AS p05_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(25)] AS p25_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(50)] AS median_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(75)] AS p75_gap,
  APPROX_QUANTILES(gap, 100)[OFFSET(95)] AS p95_gap
FROM g GROUP BY subtype ORDER BY n_events DESC
"""

# ---------------------------------------------------------------------------------------------
# M3 — rival-hypothesis test. Does ISS.listing_date coincide with an AIS ("Niem yet bo sung" =
# additional listing) effective_date for the SAME ticker? Exact match, and within +/-3 days to
# absorb vendor rounding. A high match rate identifies listing_date as a POST-event listing date.
# ---------------------------------------------------------------------------------------------
M3 = f"""
WITH {RAW_CTE},
ais AS (
  SELECT ticker, effective_date FROM `{PROJECT}.tav2_bq.corporate_action`
  WHERE event_code = 'AIS' AND effective_date IS NOT NULL
),
j AS (
  SELECT e.subtype, e.ticker, e.exright_date, e.listing_date,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = e.ticker
             AND a.effective_date = e.listing_date) AS ais_exact,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = e.ticker
             AND ABS(DATE_DIFF(a.effective_date, e.listing_date, DAY)) <= 3) AS ais_pm3
  FROM ev e WHERE e.listing_date IS NOT NULL
)
SELECT subtype, COUNT(*) AS n_with_listing,
  COUNTIF(ais_exact) AS n_ais_exact,
  ROUND(100 * COUNTIF(ais_exact) / COUNT(*), 1) AS pct_ais_exact,
  COUNTIF(ais_pm3) AS n_ais_pm3,
  ROUND(100 * COUNTIF(ais_pm3) / COUNT(*), 1) AS pct_ais_pm3
FROM j GROUP BY subtype ORDER BY n_with_listing DESC
"""

# ---------------------------------------------------------------------------------------------
# M4 — the 20-event manual cross-check sample the dispatch asked for. Deterministic pick
# (FARM_FINGERPRINT ordering, no RAND()) so a re-run reproduces the same tickers/dates.
# Stratum A = |gap| in [5,15]; stratum B = |gap| > 30. RIGHTS + PRIVATE_PLACEMENT only.
# ---------------------------------------------------------------------------------------------
M4 = f"""
WITH {RAW_CTE},
g AS (
  SELECT subtype, ticker, exright_date, listing_date, public_date, record_date, event_title_vi,
         DATE_DIFF(exright_date, listing_date, DAY) AS gap_ex_minus_listing
  FROM ev
  WHERE subtype IN ('RIGHTS', 'PRIVATE_PLACEMENT') AND listing_date IS NOT NULL
    AND exright_date IS NOT NULL
),
s AS (
  SELECT *,
    CASE WHEN ABS(gap_ex_minus_listing) BETWEEN 5 AND 15 THEN 'A_gap_small_5_15'
         WHEN ABS(gap_ex_minus_listing) > 30 THEN 'B_gap_large_gt30' END AS stratum
  FROM g
),
r AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY stratum
             ORDER BY FARM_FINGERPRINT(CONCAT(ticker, CAST(exright_date AS STRING)))) AS rk
  FROM s WHERE stratum IS NOT NULL
)
SELECT stratum, ticker, subtype, exright_date, listing_date, record_date, public_date,
       gap_ex_minus_listing, event_title_vi
FROM r WHERE rk <= 10 ORDER BY stratum, rk
"""

# ---------------------------------------------------------------------------------------------
# M5 — the listing_date == exright_date cluster (RIGHTS: ~29% of events). Under the notification
# hypothesis a zero gap is impossible (notice must precede by >=5 working days); under the
# listing hypothesis it is a vendor fallback that copies the ex-date when the true listing date
# is unknown. Dumped whole so the report can characterise it by era.
# ---------------------------------------------------------------------------------------------
M5 = f"""
WITH {RAW_CTE}
SELECT subtype, EXTRACT(YEAR FROM exright_date) AS yr, COUNT(*) AS n,
       COUNTIF(listing_date = exright_date) AS n_eq,
       ROUND(100 * COUNTIF(listing_date = exright_date)
             / NULLIF(COUNTIF(listing_date IS NOT NULL), 0), 1) AS pct_eq
FROM ev WHERE subtype IN ('RIGHTS', 'PRIVATE_PLACEMENT') AND exright_date IS NOT NULL
GROUP BY subtype, yr ORDER BY subtype, yr
"""

# ---------------------------------------------------------------------------------------------
# M6 — every RIGHTS/PP event where listing_date STRICTLY precedes exright_date. These are the
# only rows the notification hypothesis could survive on; small enough to dump in full.
# ---------------------------------------------------------------------------------------------
M6 = f"""
WITH {RAW_CTE}
SELECT subtype, ticker, exright_date, listing_date, record_date, public_date,
       DATE_DIFF(exright_date, listing_date, DAY) AS gap_ex_minus_listing, event_title_vi
FROM ev
WHERE subtype IN ('RIGHTS', 'PRIVATE_PLACEMENT') AND listing_date < exright_date
ORDER BY subtype, exright_date
"""


# ---------------------------------------------------------------------------------------------
# M7 — M3 sharpened. AIS coverage is thin (4.9k rows vs 9.6k ISS rows carrying a listing_date), so
# a raw non-match may just mean "no AIS row exists", not "the dates disagree". M7 conditions on
# the ticker HAVING an AIS row within +/-365d of listing_date, then asks whether it matches.
# The placebo column runs the identical test on `exright_date`: if listing_date really is the
# additional-listing date, it must match AIS far more often than the ex-date does.
# ---------------------------------------------------------------------------------------------
M7 = f"""
WITH {RAW_CTE},
ais AS (
  SELECT ticker, effective_date FROM `{PROJECT}.tav2_bq.corporate_action`
  WHERE event_code = 'AIS' AND effective_date IS NOT NULL
),
cand AS (
  SELECT e.subtype, e.ticker, e.exright_date, e.listing_date
  FROM ev e WHERE e.listing_date IS NOT NULL AND e.exright_date IS NOT NULL
),
scoped AS (
  SELECT c.* FROM cand c
  WHERE EXISTS(SELECT 1 FROM ais a WHERE a.ticker = c.ticker
                 AND ABS(DATE_DIFF(a.effective_date, c.listing_date, DAY)) <= 365)
),
j AS (
  SELECT s.subtype,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = s.ticker
             AND a.effective_date = s.listing_date) AS hit_listing,
    EXISTS(SELECT 1 FROM ais a WHERE a.ticker = s.ticker
             AND a.effective_date = s.exright_date) AS hit_exright
  FROM scoped s
)
SELECT subtype, COUNT(*) AS n_scoped,
  COUNTIF(hit_listing) AS n_hit_listing,
  ROUND(100 * COUNTIF(hit_listing) / COUNT(*), 1) AS pct_hit_listing,
  COUNTIF(hit_exright) AS n_hit_exright_placebo,
  ROUND(100 * COUNTIF(hit_exright) / COUNT(*), 1) AS pct_hit_exright_placebo
FROM j GROUP BY subtype ORDER BY n_scoped DESC
"""


def main() -> None:
    for name, sql in (("m1_fill_by_event_code", M1), ("m2_gap_by_subtype", M2),
                      ("m3_ais_match", M3), ("m4_sample20", M4),
                      ("m5_zero_gap_by_year", M5), ("m6_listing_before_ex", M6),
                      ("m7_ais_match_scoped", M7)):
        rows = bq(sql, name)
        path = dump(name + ".csv", rows)
        print(f"{name}: {len(rows)} rows -> {os.path.relpath(path, HERE)}")


if __name__ == "__main__":
    main()
