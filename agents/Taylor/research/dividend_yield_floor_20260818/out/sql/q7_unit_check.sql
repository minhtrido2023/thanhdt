WITH ev AS (
  SELECT * FROM UNNEST([
    STRUCT('VCF' AS tk, DATE '2018-01-08' AS ex, 66000.0 AS dv),
    ('VCF', DATE '2025-09-30', 48000.0), ('VEF', DATE '2025-06-12', 43500.0),
    ('PRC', DATE '2023-03-30', 35000.0), ('TTP', DATE '2024-05-23', 35000.0),
    ('SST', DATE '2020-08-27', 34760.0), ('VEF', DATE '2025-10-22', 33000.0),
    ('SST', DATE '2023-08-18', 27800.0), ('SST', DATE '2021-12-07', 27326.0),
    ('WCS', DATE '2020-07-16', 25800.0), ('WCS', DATE '2020-09-16', 25800.0),
    ('VCF', DATE '2020-10-19', 25000.0), ('VCF', DATE '2021-12-15', 25000.0),
    ('BTH', DATE '2025-11-06', 25000.0), ('VCF', DATE '2024-09-06', 25000.0),
    ('VCF', DATE '2019-08-16', 24000.0), ('SST', DATE '2019-05-07', 20700.0),
    ('FOC', DATE '2021-04-13', 20000.0), ('WCS', DATE '2019-10-09', 20000.0),
    ('SLS', DATE '2024-10-09', 20000.0)
  ])
),
px AS (
  SELECT e.tk, e.ex, e.dv,
    ARRAY_AGG(t.Price ORDER BY t.time DESC LIMIT 1)[OFFSET(0)] AS px_prev,
    ARRAY_AGG(t.time  ORDER BY t.time DESC LIMIT 1)[OFFSET(0)] AS px_dt
  FROM ev AS e
  JOIN `lithe-record-440915-m9.tav2_bq.ticker` AS t
    ON t.ticker = e.tk AND t.time < e.ex AND t.time >= DATE_SUB(e.ex, INTERVAL 30 DAY)
     AND t.Price IS NOT NULL AND t.Price > 0
  GROUP BY e.tk, e.ex, e.dv
),
fin AS (
  SELECT f.ticker, f.time, f.OShares,
    (IFNULL(f.NP_P0,0)+IFNULL(f.NP_P1,0)+IFNULL(f.NP_P2,0)+IFNULL(f.NP_P3,0)) AS np_ttm,
    ROW_NUMBER() OVER (PARTITION BY f.ticker, f.time ORDER BY f.Release_Date DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial` AS f
  WHERE f.OShares IS NOT NULL AND f.OShares > 0
)
SELECT p.tk, p.ex, p.dv, p.px_prev, p.px_dt,
       ROUND(p.dv / p.px_prev, 4) AS div_over_px,
       g.OShares, g.np_ttm,
       ROUND(SAFE_DIVIDE(p.dv * g.OShares, g.np_ttm), 3) AS payout_vs_np_ttm
FROM px AS p
LEFT JOIN (
  SELECT ticker, time, OShares, np_ttm,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time DESC) AS r2
  FROM fin WHERE rn = 1
) AS g ON g.ticker = p.tk AND g.r2 = 1
ORDER BY p.dv DESC
