WITH 
raw AS (
 SELECT c.*,
  CASE c.issue_method_code WHEN 'Rights' THEN 'RIGHTS' WHEN 'EMPL' THEN 'ESOP' WHEN 'PP' THEN 'PRIVATE_PLACEMENT' END subtype,
  ROW_NUMBER() OVER(PARTITION BY c.ticker,c.exright_date,c.issue_method_code,
    CAST(c.exercise_ratio AS STRING),CAST(c.issue_volumn AS STRING),CAST(c.total_value AS STRING)
    ORDER BY c.public_date DESC,c.id DESC) rn
 FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
 WHERE c.event_code='ISS' AND c.event_status='executed' AND c.issue_method_code IN ('Rights','EMPL','PP')
), dedup AS (SELECT * FROM raw WHERE rn=1)
, ev AS (
 SELECT ticker,exright_date anchor_date,'RIGHTS' subtype,SUM(exercise_ratio) ratio_total,
  SUM(issue_volumn) issue_volume,SUM(total_value) total_value,COUNT(*) n_components,
  COUNT(DISTINCT ROUND(SAFE_DIVIDE(total_value,issue_volumn),2)) n_prices,
  MAX(listing_date) listing_date
 FROM dedup WHERE subtype='RIGHTS' AND exright_date BETWEEN DATE '2014-01-01' AND DATE '2026-06-30'
 GROUP BY ticker,anchor_date
), px AS (
 SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
  SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
  ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
 FROM `lithe-record-440915-m9.tav2_bq.ticker` t WHERE t.time>=DATE '2013-01-01' AND t.Close>0 AND t.ticker IN(SELECT ticker FROM ev)
), a AS (SELECT e.*,p.si si0 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time=e.anchor_date),
w AS (SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Price,p.Volume,p.ICB_Code,p.ret FROM a JOIN px p ON p.ticker=a.ticker AND p.si BETWEEN a.si0-250 AND a.si0+62)
SELECT ticker,anchor_date,ANY_VALUE(subtype) subtype,ANY_VALUE(ratio_total) ratio_total,ANY_VALUE(issue_volume) issue_volume,
 ANY_VALUE(total_value) total_value,ANY_VALUE(n_components) n_components,ANY_VALUE(n_prices) n_prices,ANY_VALUE(listing_date) listing_date,
 MAX(IF(k=-250,Close,NULL)) c_m250,MAX(IF(k=-250,dt,NULL)) d_m250,MAX(IF(k=-230,Close,NULL)) c_m230,MAX(IF(k=-230,dt,NULL)) d_m230,
 MAX(IF(k=-40,Close,NULL)) c_m40,MAX(IF(k=-40,dt,NULL)) d_m40,MAX(IF(k=-21,Close,NULL)) c_m21,MAX(IF(k=-21,dt,NULL)) d_m21,
 MAX(IF(k=-20,Close,NULL)) c_m20,MAX(IF(k=-20,dt,NULL)) d_m20,MAX(IF(k=-1,Close,NULL)) c_m1,MAX(IF(k=-1,Price,NULL)) p_m1,MAX(IF(k=-1,dt,NULL)) d_m1,
 MAX(IF(k=0,Close,NULL)) c_0,MAX(IF(k=0,dt,NULL)) d_0,MAX(IF(k=0,Volume,NULL)) v_0,
 MAX(IF(k=1,Close,NULL)) c_1,MAX(IF(k=1,Price,NULL)) p_1,MAX(IF(k=2,Close,NULL)) c_2,MAX(IF(k=2,Price,NULL)) p_2,MAX(IF(k=3,Close,NULL)) c_3,MAX(IF(k=3,Price,NULL)) p_3,
 MAX(IF(k=5,Close,NULL)) c_5,MAX(IF(k=5,dt,NULL)) d_5,MAX(IF(k=20,Close,NULL)) c_20,MAX(IF(k=20,dt,NULL)) d_20,MAX(IF(k=60,Close,NULL)) c_60,MAX(IF(k=60,dt,NULL)) d_60,
 AVG(IF(k BETWEEN -60 AND -6,Price*Volume,NULL)) adv60,STDDEV(IF(k BETWEEN -60 AND -1,ret,NULL)) rvol60,
 EXP(SUM(IF(k BETWEEN -126 AND -21,LN(1+ret),0)))-1 mom6m,MAX(IF(k=-1,ICB_Code,NULL)) icb
FROM w GROUP BY ticker,anchor_date ORDER BY ticker,anchor_date