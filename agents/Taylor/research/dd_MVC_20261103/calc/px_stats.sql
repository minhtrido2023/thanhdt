WITH t AS (SELECT k.time, k.Close, k.Price, k.Volume, k.Price*k.Volume/1e9 AS val, ROW_NUMBER() OVER (ORDER BY k.time DESC) rn
           FROM tav2_bq.ticker AS k WHERE k.ticker='MVC' AND k.time>='2025-06-01')
SELECT MAX(IF(rn=1,time,NULL)) last_day, MAX(IF(rn=1,Price,NULL)) last_px,
 ROUND(AVG(IF(rn<=20,val,NULL)),3) adv20, ROUND(AVG(IF(rn<=60,val,NULL)),3) adv60, ROUND(AVG(IF(rn<=120,val,NULL)),3) adv120,
 COUNTIF(rn<=60 AND Volume=0) zero60, MAX(IF(time>='2025-11-03',Price,NULL)) hi12m, MIN(IF(time>='2025-11-03',Price,NULL)) lo12m
FROM t
