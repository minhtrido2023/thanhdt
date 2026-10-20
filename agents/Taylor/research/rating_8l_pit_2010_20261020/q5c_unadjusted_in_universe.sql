WITH p AS (SELECT ticker, time, Price, Close, LAG(Price) OVER w AS p0, LAG(Close) OVER w AS c0, LAG(time) OVER w AS t0
  FROM tav2_pin.ticker_pin_202610 WHERE time BETWEEN '2009-12-01' AND '2014-12-31' WINDOW w AS (PARTITION BY ticker ORDER BY time)),
e AS (SELECT * FROM p WHERE time >= '2010-01-01' AND (ABS(SAFE_DIVIDE(Close,c0)-1) > 0.20))
SELECT e.ticker, e.time, e.t0, DATE_DIFF(e.time,e.t0,DAY) AS gap_d, e.p0, e.Price, e.c0, e.Close,
  ROUND(SAFE_DIVIDE(e.Price,e.p0)-1,3) AS rp, ROUND(SAFE_DIVIDE(e.Close,e.c0)-1,3) AS rc, u.in_universe
FROM e JOIN tav2_mike.universe_pit AS u ON u.ticker=e.ticker AND u.time=e.time
WHERE u.in_universe ORDER BY e.time
