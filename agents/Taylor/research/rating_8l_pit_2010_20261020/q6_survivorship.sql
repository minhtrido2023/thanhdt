WITH ls AS (SELECT ticker, MAX(time) AS last_t, MIN(time) AS first_t FROM tav2_pin.ticker_pin_202610 GROUP BY ticker),
lf AS (SELECT ticker, MAX(time) AS last_f FROM tav2_bq.ticker_financial GROUP BY ticker)
SELECT 'pin202610_price' AS src, COUNT(*) AS n_tk, COUNTIF(last_t < '2026-01-01') AS last_before_2026,
  COUNTIF(last_t < '2020-01-01') AS last_before_2020, MAX(last_t) AS mx, MIN(last_t) AS min_last FROM ls
UNION ALL
SELECT 'ticker_financial', COUNT(*), COUNTIF(last_f < '2026-01-01'), COUNTIF(last_f < '2020-01-01'), MAX(last_f), MIN(last_f) FROM lf
