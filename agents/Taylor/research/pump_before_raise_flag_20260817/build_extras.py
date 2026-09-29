#!/usr/bin/env python3
"""One read-only BQ pull keyed on the PRIOR program's event set. No table/view is created.

The event definition (dedup rule, survivor rule, `universe_pit` PIT gate, session indexing) is
NOT restated here — `EVENTS_CTE`, `PX_CTE`, `Q1_MIN`, `Q1_MAX` and `bq()` are imported from
`../serial_capital_raiser_20260817/build.py`, so the two programs cannot silently drift onto
different event sets. Selfcheck CC5 asserts the key sets are identical anyway.

Three things this adds, per PREREG §1:
  * fundamentals at k = -1 (last session strictly BEFORE the ex-date) — read AS STORED
  * `beta_raw` — 250-session OLS beta vs VNINDEX over [-250, -1]
  * `rr_beta_bin` — tav2_bq.risk_rating.Beta from the latest quarter STRICTLY BEFORE t0's quarter
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PRIOR = os.path.join(os.path.dirname(HERE), "serial_capital_raiser_20260817")
sys.path.insert(0, PRIOR)

from build import EVENTS_CTE, PX_CTE, PROJECT, Q1_MAX, Q1_MIN, bq, dump  # noqa: E402

OUT = os.path.join(HERE, "out")

# `dump`/`bq` write into the PRIOR program's out/ dir; redirect both to ours.
import build as _b  # noqa: E402

_b.OUT = OUT
_b.SQLDIR = os.path.join(OUT, "sql")

# Beta needs enough overlapping sessions to be a coefficient rather than a rumour. 150 of a
# possible 250 is the floor declared in PREREG; below it the field is NULL, not a small-sample beta.
BETA_MIN_OBS = 150

EXTRAS_SQL = f"""
WITH {EVENTS_CTE},
{PX_CTE},
vni AS (
  SELECT time,
         SAFE_DIVIDE(Close, LAG(Close) OVER (ORDER BY time)) - 1 AS vret
  FROM `{PROJECT}.tav2_bq.ticker`
  WHERE ticker = 'VNINDEX' AND Close > 0
),
ev AS (
  SELECT ticker, exright_date AS t0, subtype
  FROM ev_all
  WHERE exright_date BETWEEN DATE '{Q1_MIN}' AND DATE '{Q1_MAX}'
  GROUP BY ticker, t0, subtype
),
gated AS (
  SELECT e.* FROM ev e
  JOIN `{PROJECT}.tav2_mike.universe_pit` u
    ON u.ticker = e.ticker AND u.time = e.t0 AND u.in_universe
),
-- DISTINCT on (ticker, t0), NOT on (ticker, t0, subtype): the prior program's Q1_SQL ends in
-- `GROUP BY ticker, t0` with ANY_VALUE(subtype), so a ticker with two different ISS subtypes on
-- one ex-date is ONE row there (3,246 -> 2,953). Keying on subtype here would fan the joins out
-- and break CC5. Every field below depends only on (ticker, date), so the collapse loses nothing;
-- `subtype` itself is taken from q1_bhar.csv at merge time, never from this pull.
anchored AS (
  SELECT DISTINCT g.ticker, g.t0, p.si AS si0
  FROM gated g JOIN px p ON p.ticker = g.ticker AND p.time = g.t0
),
-- pre-event window only: [-250, -1]. Nothing at or after the ex-date is read here, by construction.
w AS (
  SELECT a.ticker, a.t0, p.si - a.si0 AS k, p.time AS dt, p.ret
  FROM anchored a JOIN px p
    ON p.ticker = a.ticker AND p.si BETWEEN a.si0 - 250 AND a.si0 - 1
),
beta AS (
  SELECT w.ticker, w.t0,
         COUNT(*) AS beta_n,
         SAFE_DIVIDE(COVAR_POP(w.ret, v.vret), NULLIF(VAR_POP(v.vret), 0)) AS beta_pop,
         CORR(w.ret, v.vret) AS beta_corr
  FROM w JOIN vni v ON v.time = w.dt
  WHERE w.ret IS NOT NULL AND v.vret IS NOT NULL
  GROUP BY 1, 2
),
d_m1 AS (SELECT ticker, t0, MAX(IF(k = -1, dt, NULL)) AS dt_m1 FROM w GROUP BY 1, 2),
fund AS (
  SELECT d.ticker, d.t0, d.dt_m1,
         t.ROIC_Trailing AS roic_trailing, t.FSCORE AS fscore, t.NPM_P0 AS npm_p0,
         t.Debt_Eq_P0 AS debt_eq, t.PE AS pe, t.PB AS pb, t.ICB_Code AS icb_m1
  FROM d_m1 d JOIN `{PROJECT}.tav2_bq.ticker` t
    ON t.ticker = d.ticker AND t.time = d.dt_m1
),
-- risk_rating: DISTINCT is defensive (CLAUDE.md trap #3), and the quarter must be STRICTLY before
-- the calendar quarter containing t0 so no rating computed during the event quarter leaks in.
rr AS (
  SELECT DISTINCT ticker, quarter, Beta AS rr_beta_bin, Dev AS rr_dev_bin,
         Risk_Rating AS rr_rating
  FROM `{PROJECT}.tav2_bq.risk_rating`
  WHERE Beta IS NOT NULL
),
rr_pick AS (
  SELECT ticker, t0, rr_beta_bin, rr_dev_bin, rr_rating, rr_quarter, t0_quarter
  FROM (
    SELECT a.ticker, a.t0, r.rr_beta_bin, r.rr_dev_bin, r.rr_rating,
           r.quarter AS rr_quarter,
           FORMAT('%dQ%d', EXTRACT(YEAR FROM a.t0), EXTRACT(QUARTER FROM a.t0)) AS t0_quarter,
           ROW_NUMBER() OVER (PARTITION BY a.ticker, a.t0 ORDER BY r.quarter DESC) AS rn
    FROM anchored a JOIN rr r ON r.ticker = a.ticker
     AND r.quarter < FORMAT('%dQ%d', EXTRACT(YEAR FROM a.t0), EXTRACT(QUARTER FROM a.t0))
  )
  WHERE rn = 1
)
SELECT a.ticker, a.t0,
       f.dt_m1, f.roic_trailing, f.fscore, f.npm_p0, f.debt_eq, f.pe, f.pb, f.icb_m1,
       b.beta_n, IF(b.beta_n >= {BETA_MIN_OBS}, b.beta_pop, NULL) AS beta_raw, b.beta_corr,
       p.rr_beta_bin, p.rr_dev_bin, p.rr_rating, p.rr_quarter, p.t0_quarter
FROM anchored a
LEFT JOIN fund f ON f.ticker = a.ticker AND f.t0 = a.t0
LEFT JOIN beta b ON b.ticker = a.ticker AND b.t0 = a.t0
LEFT JOIN rr_pick p ON p.ticker = a.ticker AND p.t0 = a.t0
ORDER BY a.ticker, a.t0
"""


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    print("[1/1] event extras (fundamentals @k=-1, 250-session beta, risk_rating bin) ...",
          flush=True)
    rows = bq(EXTRAS_SQL, "extras")
    dump("extras.csv", rows)

    def cov(field: str) -> float:
        return round(sum(1 for r in rows if r.get(field)) / max(len(rows), 1), 4)

    summary = {
        "rows": len(rows),
        "tickers": len({r["ticker"] for r in rows}),
        "coverage_roic_trailing": cov("roic_trailing"),
        "coverage_fscore": cov("fscore"),
        "coverage_beta_raw": cov("beta_raw"),
        "coverage_rr_beta_bin": cov("rr_beta_bin"),
        "coverage_icb_m1": cov("icb_m1"),
    }
    with open(os.path.join(OUT, "extras_summary.json"), "w") as fh:
        json.dump(summary, fh, indent=2, sort_keys=True)
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    sys.exit(main())
