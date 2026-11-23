CREATE TEMP TABLE steps AS
SELECT * FROM (SELECT t.ticker, t.time AS step_date, t.OShares AS os, LAG(t.OShares) OVER (PARTITION BY t.ticker ORDER BY t.time) AS prev_os
  FROM tav2_bq.ticker AS t WHERE t.time >= '2013-06-01' AND t.OShares > 0)
WHERE prev_os > 0 AND ABS(os/prev_os-1) >= 0.05;
CREATE TEMP TABLE ev AS
SELECT c.ticker, c.exright_date AS d, 1+c.exercise_ratio AS r FROM tav2_bq.corporate_action AS c
 WHERE c.event_code='ISS' AND c.event_status!='not_executed' AND c.exright_date IS NOT NULL AND c.exercise_ratio>0;
CREATE TEMP TABLE m AS
SELECT * FROM (SELECT s.ticker, s.step_date, s.os/s.prev_os AS ratio, e.d AS exdate, DATE_DIFF(s.step_date, e.d, DAY) AS lag_d,
  ROW_NUMBER() OVER (PARTITION BY s.ticker, s.step_date ORDER BY ABS(DATE_DIFF(s.step_date, e.d, DAY))) rn
FROM steps s JOIN ev e ON e.ticker=s.ticker AND ABS(DATE_DIFF(s.step_date,e.d,DAY))<=150 AND ABS((s.os/s.prev_os)/e.r-1)<0.02)
WHERE rn=1 AND ABS(lag_d)>3 AND step_date>='2014-01-01';
CREATE TEMP TABLE rk AS SELECT t.ticker,t.time,RANK() OVER (PARTITION BY t.time ORDER BY t.Price*t.OShares DESC) AS rk
 FROM tav2_bq.ticker AS t WHERE t.time>='2013-06-01' AND t.OShares>0 AND t.Price>0 AND t.ticker!='VNINDEX';
CREATE TEMP TABLE w AS
SELECT m.ticker, m.step_date, m.exdate, m.lag_d, m.ratio, t.time, r.rk
FROM m JOIN tav2_bq.ticker AS t ON t.ticker=m.ticker AND t.time BETWEEN LEAST(m.step_date,m.exdate) AND DATE_SUB(GREATEST(m.step_date,m.exdate), INTERVAL 1 DAY)
JOIN rk r ON r.ticker=t.ticker AND r.time=t.time WHERE t.OShares>0 AND t.Price>0;
SELECT EXTRACT(YEAR FROM time) y, COUNT(*) stock_days, COUNT(DISTINCT CONCAT(ticker,CAST(step_date AS STRING))) events,
  COUNTIF(rk<=100) days_top100, COUNTIF(rk<=30) days_top30, COUNTIF(rk<=100 AND ABS(lag_d)>=20) days_top100_lag20
FROM w GROUP BY y ORDER BY y;
SELECT ticker, step_date, exdate, lag_d, ROUND(ratio,2) ratio, MIN(rk) best_rank, COUNT(*) days FROM w WHERE rk<=100 AND time>='2026-06-01' AND ABS(lag_d)>=10 GROUP BY 1,2,3,4,5 ORDER BY step_date DESC LIMIT 20;
SELECT ticker, step_date, exdate, lag_d, ROUND(ratio,2) ratio, MIN(rk) best_rank, COUNT(*) days FROM w WHERE rk<=30 AND time>='2023-01-01' AND ABS(lag_d)>=20 GROUP BY 1,2,3,4,5 ORDER BY days DESC LIMIT 12;
