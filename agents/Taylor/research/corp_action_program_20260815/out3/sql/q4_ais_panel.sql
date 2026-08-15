
WITH ev AS (
SELECT ticker,effective_date ais_date,shares_delta,shares_total_after
FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
WHERE event_code='AIS' AND event_status='executed' AND effective_date IS NOT NULL
  AND effective_date BETWEEN DATE '2014-01-01' AND DATE '2027-06-30'
), px AS (
 SELECT t.ticker,t.time,t.Close,t.Volume,
  ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
 FROM `lithe-record-440915-m9.tav2_bq.ticker` t WHERE t.time>=DATE '2013-01-01' AND t.Close>0
), first_trade AS (
 SELECT e.ticker,e.ais_date,ANY_VALUE(e.shares_delta) shares_delta,
   ANY_VALUE(e.shares_total_after) shares_total_after,MIN(p.time) trading_date
 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time>=e.ais_date
 GROUP BY e.ticker,e.ais_date
), a AS (
 SELECT f.*,p.si si0 FROM first_trade f JOIN px p
 ON p.ticker=f.ticker AND p.time=f.trading_date
), w AS (
 SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Volume FROM a JOIN px p
 ON p.ticker=a.ticker AND p.si BETWEEN a.si0-61 AND a.si0+62
)
SELECT ticker,ais_date,ANY_VALUE(trading_date) trading_date,
 ANY_VALUE(shares_delta) shares_delta,ANY_VALUE(shares_total_after) shares_total_after,
 MAX(IF(k=-1,Close,NULL)) c_m1,MAX(IF(k=-1,dt,NULL)) d_m1,
 MAX(IF(k=0,Close,NULL)) c_0,MAX(IF(k=0,dt,NULL)) d_0,
 MAX(IF(k=5,Close,NULL)) c_5,MAX(IF(k=5,dt,NULL)) d_5,
 MAX(IF(k=20,Close,NULL)) c_20,MAX(IF(k=20,dt,NULL)) d_20,
 MAX(IF(k=60,Close,NULL)) c_60,MAX(IF(k=60,dt,NULL)) d_60,
 MAX(IF(k=0,Volume,NULL)) v_0,AVG(IF(k BETWEEN -60 AND -6,Volume,NULL)) avol_pre,
 AVG(IF(k BETWEEN 0 AND 5,Volume,NULL)) avol_0_5
FROM w GROUP BY ticker,ais_date ORDER BY ticker,ais_date
