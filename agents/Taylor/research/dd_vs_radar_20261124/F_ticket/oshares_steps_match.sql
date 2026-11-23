CREATE TEMP TABLE steps AS
SELECT * FROM (
  SELECT t.ticker, t.time AS step_date, t.OShares AS os, LAG(t.OShares) OVER (PARTITION BY t.ticker ORDER BY t.time) AS prev_os
  FROM tav2_bq.ticker AS t WHERE t.time >= '2008-01-01' AND t.OShares > 0)
WHERE prev_os > 0 AND ABS(os/prev_os-1) >= 0.05;
CREATE TEMP TABLE ev AS
SELECT c.ticker, c.exright_date AS d, 1+c.exercise_ratio AS r, 'ISS' AS k FROM tav2_bq.corporate_action AS c
 WHERE c.event_code='ISS' AND c.event_status!='not_executed' AND c.exright_date IS NOT NULL AND c.exercise_ratio>0;
CREATE TEMP TABLE m AS
SELECT s.ticker, s.step_date, s.os/s.prev_os AS ratio, e.d AS exdate, DATE_DIFF(s.step_date, e.d, DAY) AS lag_d,
  ROW_NUMBER() OVER (PARTITION BY s.ticker, s.step_date ORDER BY ABS(DATE_DIFF(s.step_date, e.d, DAY))) rn
FROM steps s JOIN ev e ON e.ticker=s.ticker AND ABS(DATE_DIFF(s.step_date,e.d,DAY))<=150 AND ABS((s.os/s.prev_os)/e.r-1)<0.02;
SELECT
  (SELECT COUNT(*) FROM steps) AS n_steps,
  (SELECT COUNT(*) FROM steps WHERE step_date>='2014-01-01') AS n_steps_2014p,
  COUNT(*) AS matched,
  COUNTIF(ABS(lag_d)<=3) AS within3,
  COUNTIF(lag_d<-3) AS early,
  COUNTIF(lag_d>3) AS late,
  APPROX_QUANTILES(lag_d,5) AS q_lag
FROM m WHERE rn=1;
SELECT EXTRACT(YEAR FROM step_date) AS y, COUNT(*) n, COUNTIF(ABS(lag_d)<=3) ok, COUNTIF(lag_d<-3) early, COUNTIF(lag_d>3) late, ROUND(AVG(lag_d),1) mean_lag
FROM m WHERE rn=1 GROUP BY y ORDER BY y;
SELECT ticker, step_date, ROUND(ratio,3) ratio, exdate, lag_d FROM m WHERE rn=1 AND step_date>='2025-06-01' AND ABS(lag_d)>3 ORDER BY step_date DESC LIMIT 25;
