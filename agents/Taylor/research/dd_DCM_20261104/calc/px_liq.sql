WITH t AS (SELECT k.time, k.Price, k.Volume, k.Price*k.Volume/1e9 AS val, ROW_NUMBER() OVER (ORDER BY k.time DESC) rn
 FROM tav2_bq.ticker AS k WHERE k.ticker='DCM' AND k.time>='2025-06-01')
SELECT MAX(IF(rn=1,time,NULL)) last_day, MAX(IF(rn=1,Price,NULL)) last_px,
 APPROX_QUANTILES(IF(rn<=20,val,NULL),100)[OFFSET(50)] med20, APPROX_QUANTILES(IF(rn<=90,val,NULL),100)[OFFSET(50)] med90,
 APPROX_QUANTILES(IF(rn<=90,Volume,NULL),100)[OFFSET(50)] medvol90, MIN(IF(rn<=90,val,NULL)) min90, AVG(IF(rn<=90,val,NULL)) avg90,
 MIN(IF(rn<=250,Price,NULL)) lo250, MAX(IF(rn<=250,Price,NULL)) hi250 FROM t
