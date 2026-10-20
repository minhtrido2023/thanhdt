WITH f AS (SELECT time, quarter, Release_Date, CAST(SUBSTR(quarter,6,1) AS INT64) AS qn,
  LAST_DAY(DATE(CAST(SUBSTR(quarter,1,4) AS INT64), CAST(SUBSTR(quarter,6,1) AS INT64)*3, 1)) AS qend
  FROM tav2_bq.ticker_financial WHERE Release_Date IS NOT NULL)
SELECT CASE WHEN time < '2012-01-01' THEN 'a_2010-11' WHEN time < '2014-01-01' THEN 'b_2012-13' WHEN time < '2020-01-01' THEN 'c_2014-19' ELSE 'd_2020+' END AS era,
  IF(qn=4,'Q4','Q1-3') AS qt, COUNT(*) AS n,
  ROUND(COUNTIF(DATE_DIFF(Release_Date,qend,DAY) = 32)/COUNT(*),3) AS eq32,
  ROUND(COUNTIF(DATE_DIFF(Release_Date,qend,DAY) < 32)/COUNT(*),3) AS lt32,
  ROUND(COUNTIF(DATE_DIFF(Release_Date,qend,DAY) > 45)/COUNT(*),3) AS gt45,
  ROUND(COUNTIF(DATE_DIFF(Release_Date,qend,DAY) > 60)/COUNT(*),3) AS gt60,
  ROUND(COUNTIF(DATE_DIFF(Release_Date,qend,DAY) > 90)/COUNT(*),3) AS gt90
FROM f WHERE time >= '2010-01-01' GROUP BY era, qt ORDER BY era, qt
