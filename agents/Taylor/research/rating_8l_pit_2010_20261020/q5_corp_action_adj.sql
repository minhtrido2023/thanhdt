WITH p AS (
  SELECT ticker, time, Price, Close,
    LAG(Price) OVER w AS p0, LAG(Close) OVER w AS c0
  FROM tav2_pin.ticker_pin_202610 WHERE time BETWEEN '2009-12-01' AND '2014-12-31'
  WINDOW w AS (PARTITION BY ticker ORDER BY time)),
e AS (SELECT *, SAFE_DIVIDE(Price,p0)-1 AS rp, SAFE_DIVIDE(Close,c0)-1 AS rc FROM p WHERE time >= '2010-01-01')
SELECT EXTRACT(YEAR FROM time) AS yr,
  COUNTIF(rp < -0.20) AS n_price_drop20_ca,
  COUNTIF(rp < -0.20 AND ABS(rc) <= 0.15) AS n_ca_adjusted_ok,
  COUNTIF(rp < -0.20 AND rc < -0.20) AS n_ca_close_also_drop,
  COUNTIF(ABS(rc) > 0.20) AS n_close_jump20_any
FROM e GROUP BY yr ORDER BY yr
