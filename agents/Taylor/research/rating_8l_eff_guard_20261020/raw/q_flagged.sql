WITH f AS (
  SELECT t.ticker, t.quarter, t.time, t.Release_Date,
    LAST_DAY(DATE(CAST(SUBSTR(t.quarter,1,4) AS INT64), CAST(SUBSTR(t.quarter,6,1) AS INT64)*3, 1)) AS qend,
    CAST(SUBSTR(t.quarter,1,4) AS INT64)*4 + CAST(SUBSTR(t.quarter,6,1) AS INT64) AS qidx
  FROM tav2_bq.ticker_financial AS t WHERE t.time >= '2014-06-01'),
p AS (SELECT a.*, b.Release_Date AS prev_rd, b.quarter AS prev_q
      FROM f AS a LEFT JOIN f AS b ON a.ticker=b.ticker AND b.qidx=a.qidx-1)
SELECT ticker, quarter, qend, time, Release_Date, prev_q, prev_rd,
  Release_Date <= prev_rd AS c_prev, Release_Date < qend AS c_qend
FROM p WHERE Release_Date <= prev_rd OR Release_Date < qend
ORDER BY quarter, ticker
