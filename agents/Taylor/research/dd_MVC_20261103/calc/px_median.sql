WITH t AS (SELECT k.time, k.Price*k.Volume/1e9 AS val, ROW_NUMBER() OVER (ORDER BY k.time DESC) rn
 FROM tav2_bq.ticker AS k WHERE k.ticker='MVC' AND k.time>='2025-06-01')
SELECT APPROX_QUANTILES(IF(rn<=20,val,NULL),100)[OFFSET(50)] med20, APPROX_QUANTILES(IF(rn<=60,val,NULL),100)[OFFSET(50)] med60, APPROX_QUANTILES(IF(rn<=120,val,NULL),100)[OFFSET(50)] med120, AVG(IF(rn<=20,val,NULL)) avg20 FROM t
