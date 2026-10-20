WITH f AS (
  SELECT ticker, time, quarter, Release_Date,
    LAST_DAY(DATE(CAST(SUBSTR(quarter,1,4) AS INT64), CAST(SUBSTR(quarter,6,1) AS INT64)*3, 1)) AS qend,
    LAG(Release_Date) OVER (PARTITION BY ticker ORDER BY time) AS rd_prev
  FROM tav2_bq.ticker_financial WHERE time BETWEEN '2008-01-01' AND '2019-12-31'),
b AS (SELECT Release_Date, COUNT(*) AS n_same FROM f WHERE Release_Date IS NOT NULL GROUP BY Release_Date)
SELECT EXTRACT(YEAR FROM f.time) AS yr, COUNT(*) AS n,
  ROUND(COUNTIF(f.Release_Date IS NULL)/COUNT(*),3) AS rd_null,
  ROUND(COUNTIF(f.Release_Date = f.time)/COUNTIF(f.Release_Date IS NOT NULL),3) AS rd_eq_time,
  ROUND(COUNTIF(f.Release_Date < f.qend)/COUNT(*),4) AS rd_lt_qend,
  ROUND(COUNTIF(f.Release_Date <= f.rd_prev)/COUNT(*),4) AS rd_le_prev,
  ROUND(COUNTIF(b.n_same >= 50)/COUNT(*),3) AS rd_in_batch50,
  ROUND(COUNTIF(b.n_same >= 100)/COUNT(*),3) AS rd_in_batch100,
  APPROX_QUANTILES(DATE_DIFF(f.Release_Date, f.qend, DAY), 10)[OFFSET(1)] AS lag_p10,
  APPROX_QUANTILES(DATE_DIFF(f.Release_Date, f.qend, DAY), 10)[OFFSET(5)] AS lag_p50,
  APPROX_QUANTILES(DATE_DIFF(f.Release_Date, f.qend, DAY), 10)[OFFSET(9)] AS lag_p90,
  MAX(DATE_DIFF(f.Release_Date, f.qend, DAY)) AS lag_max
FROM f LEFT JOIN b USING (Release_Date) GROUP BY yr ORDER BY yr
