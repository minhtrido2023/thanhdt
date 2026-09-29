-- Loi nhuan 12/24 thang o cap CO PHIEU (universe_pit tai chinh ngay day) — kiem chung menh de "gap doi sau 1 nam"
WITH tro AS (SELECT d FROM UNNEST(['2009-02-24','2010-08-25','2012-01-06','2012-11-02','2019-01-03','2020-03-24','2022-11-15']) s, UNNEST([DATE(s)]) d),
uni AS (SELECT u.time, u.ticker FROM `tav2_mike.universe_pit` u JOIN tro ON u.time = tro.d WHERE u.in_universe),
p0  AS (SELECT t.time AS d0, t.ticker, t.Close AS c0 FROM `tav2_bq.ticker` t JOIN uni USING (ticker, time)),
fw  AS (SELECT p0.d0, p0.ticker, p0.c0, t.time, t.Close,
               DATE_DIFF(t.time, p0.d0, DAY) AS lag
        FROM p0 JOIN `tav2_bq.ticker` t ON t.ticker = p0.ticker
        WHERE t.time BETWEEN DATE_ADD(p0.d0, INTERVAL 355 DAY) AND DATE_ADD(p0.d0, INTERVAL 750 DAY)),
r12 AS (SELECT d0, ticker, ANY_VALUE(c0) c0, ARRAY_AGG(Close ORDER BY lag LIMIT 1)[OFFSET(0)] c12 FROM fw WHERE lag BETWEEN 355 AND 385 GROUP BY d0, ticker),
r24 AS (SELECT d0, ticker, ARRAY_AGG(Close ORDER BY lag LIMIT 1)[OFFSET(0)] c24 FROM fw WHERE lag BETWEEN 720 AND 750 GROUP BY d0, ticker)
SELECT r12.d0 AS trough, COUNT(*) n,
  ROUND(APPROX_QUANTILES(SAFE_DIVIDE(c12,c0)-1,100)[OFFSET(50)],3) med12,
  ROUND(APPROX_QUANTILES(SAFE_DIVIDE(c12,c0)-1,100)[OFFSET(75)],3) p75_12,
  ROUND(COUNTIF(SAFE_DIVIDE(c12,c0)-1>=1.0)/COUNT(*),3) pct_double12,
  ROUND(APPROX_QUANTILES(SAFE_DIVIDE(c24,c0)-1,100)[OFFSET(50)],3) med24,
  ROUND(COUNTIF(SAFE_DIVIDE(c24,c0)-1>=1.0)/NULLIF(COUNTIF(c24 IS NOT NULL),0),3) pct_double24
FROM r12 LEFT JOIN r24 USING (d0, ticker) GROUP BY trough ORDER BY trough
