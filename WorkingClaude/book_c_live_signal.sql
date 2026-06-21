-- Book C VALUE signal (live screen, copy vào BQ console)
-- Signal: PB+PE composite rank, quality gate ROIC5Y>=8% + FSCORE>=5
-- Universe: ticker_1m, liq>=10B/day
-- Output: top quintile (20%) = Book C picks today

WITH quality_universe AS (
  SELECT
    t.time, t.ticker, t.Close,
    t.PB, t.PE, t.ROIC5Y, t.FSCORE, t.ROE_Min5Y,
    t.Trading_Value_1M_P50 / 1e9                    AS liq_B,
    t.ICB_Code, t.Risk_Rating,
    -- rank within quality-filtered universe (same-day, cross-sectional)
    PERCENT_RANK() OVER (ORDER BY t.PB ASC)          AS pb_rank,
    PERCENT_RANK() OVER (ORDER BY t.PE ASC)          AS pe_rank,
    COUNT(*) OVER ()                                  AS n_universe
  FROM tav2_bq.ticker_1m AS t
  WHERE t.time = (SELECT MAX(time) FROM tav2_bq.ticker_1m)
    AND t.PB  > 0 AND t.PE > 0 AND t.PE < 100
    AND t.ROIC5Y  >= 0.08          -- quality gate 1: ROIC5Y >= 8%
    AND t.FSCORE  >= 5             -- quality gate 2: Piotroski >= 5
    AND t.Trading_Value_1M_P50 >= 10e9   -- liq >= 10B/day
),
scored AS (
  SELECT *,
    pb_rank + pe_rank                                 AS vscore,
    PERCENT_RANK() OVER (ORDER BY pb_rank+pe_rank ASC) AS value_rank
  FROM quality_universe
)
SELECT
  time, ticker, Close, PB, PE,
  ROUND(ROIC5Y*100,1)  AS ROIC5Y_pct,
  FSCORE,
  ROUND(liq_B,1)        AS liq_B,
  ROUND(pb_rank,3)      AS pb_rank,
  ROUND(pe_rank,3)      AS pe_rank,
  ROUND(vscore,3)       AS vscore,
  n_universe,
  CASE WHEN value_rank <= 0.20 THEN 'PICK'
       WHEN value_rank <= 0.30 THEN 'WATCH'
       ELSE 'OUT' END   AS status
FROM scored
WHERE value_rank <= 0.30
ORDER BY vscore
