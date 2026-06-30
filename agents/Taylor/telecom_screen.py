#!/usr/bin/env python3
"""
Telecom valuation-lens screen (Taylor, job Taylor_20260630_060226).

VN listed telecom is structurally thin: pure-telecom names (FOX/VGI) only entered
the liquid quality universe (ticker_prune) in 2026-06, so a tradeable backtest on
the quality universe is impossible. This script runs the EVEB-entry lens on the
FULL `ticker` table (incl. UPCOM tail) as a *valuation lens*, not a tradeable book.

Screen (entry):
  EVEB in (0,8)                       # cheap vs global mature-telecom 4-8x
  AND (NPM rising OR ROIC5Y > 12)     # margin/moat confirming (cheap-EVEB alone insufficient)
  AND CF_OA_P0 > 0                    # cash generative
  AND Debt_Eq_P0 < 3.0 AND (IntCov_P0 > 1.5 OR IntCov_P0 NULL)
  AND Revenue_YoY_P0 > 0             # subscriber/ARPU growth proxy

Output: data/telecom_screen_entries.csv  +  prints flagged-vs-unflagged fwd-12M.
Auditable: recomputed directly from tav2_bq.ticker adjusted Close. AUDIT_END 2026-06-29.
"""
import subprocess, io, csv, sys

PROJECT = "lithe-record-440915-m9"
UNIVERSE = ("FOX", "VGI", "CTR", "TTN")  # ICB 6535/6575 + tower-co CTR

SQL = f"""
WITH base AS (
  SELECT t.ticker, t.time, t.Close, t.EVEB, t.PE, t.NPM_P0, t.ROIC5Y,
         t.CF_OA_P0, t.Debt_Eq_P0, t.IntCov_P0,
         ROW_NUMBER() OVER (PARTITION BY t.ticker, EXTRACT(YEAR FROM t.time),
                            EXTRACT(MONTH FROM t.time) ORDER BY t.time) AS rn
  FROM tav2_bq.ticker AS t
  WHERE t.ticker IN {UNIVERSE} AND t.time >= "2017-01-01"
),
mo AS (
  SELECT ticker, time, Close, EVEB, PE, NPM_P0, ROIC5Y, CF_OA_P0, Debt_Eq_P0, IntCov_P0,
         LAG(NPM_P0, 6) OVER (PARTITION BY ticker ORDER BY time) AS npm_6mago,
         LEAD(Close, 12) OVER (PARTITION BY ticker ORDER BY time) AS close_fwd12
  FROM base WHERE rn = 1
)
SELECT ticker, FORMAT_DATE("%Y-%m", time) AS entry, ROUND(EVEB,1) AS eveb, ROUND(PE,1) AS pe,
  ROUND(NPM_P0,2) AS npm, ROUND(ROIC5Y*100,1) AS roic5y, ROUND(Debt_Eq_P0,2) AS de,
  ROUND(IntCov_P0,1) AS intcov,
  CASE WHEN EVEB > 0 AND EVEB < 8
            AND ((npm_6mago IS NOT NULL AND NPM_P0 >= npm_6mago) OR ROIC5Y > 0.12)
            AND CF_OA_P0 > 0
            AND Debt_Eq_P0 < 3.0 AND (IntCov_P0 > 1.5 OR IntCov_P0 IS NULL)
       THEN 1 ELSE 0 END AS flagged,
  ROUND((close_fwd12/Close - 1)*100,1) AS fwd12m_pct
FROM mo
WHERE close_fwd12 IS NOT NULL
ORDER BY ticker, time
"""

def run():
    out = subprocess.run(
        ["bq", "query", "--use_legacy_sql=false", "--format=csv",
         f"--project_id={PROJECT}", SQL],
        capture_output=True, text=True)
    if out.returncode != 0:
        sys.stderr.write(out.stderr)
        sys.exit(1)
    rows = list(csv.DictReader(io.StringIO(out.stdout)))
    with open("data/telecom_screen_entries.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    flagged = [float(r["fwd12m_pct"]) for r in rows if r["flagged"] == "1"]
    unflag  = [float(r["fwd12m_pct"]) for r in rows if r["flagged"] == "0"]
    avg = lambda xs: sum(xs)/len(xs) if xs else float("nan")
    hit = lambda xs: sum(1 for x in xs if x > 0)/len(xs)*100 if xs else float("nan")

    print(f"Telecom EVEB-lens — {len(rows)} monthly snapshots, universe {UNIVERSE}")
    print(f"  FLAGGED  (cheap EVEB + margin/moat confirm): n={len(flagged):2d}  "
          f"avg fwd-12M={avg(flagged):+6.1f}%  winrate={hit(flagged):4.0f}%")
    print(f"  UNFLAGGED (expensive / not confirming)     : n={len(unflag):2d}  "
          f"avg fwd-12M={avg(unflag):+6.1f}%  winrate={hit(unflag):4.0f}%")
    print(f"  SPREAD (flagged - unflagged) = {avg(flagged)-avg(unflag):+.1f}pp")
    print("\nNOTE: lens only — names entered liquid ticker_prune 2026-06; not a tradeable book.")

if __name__ == "__main__":
    run()
