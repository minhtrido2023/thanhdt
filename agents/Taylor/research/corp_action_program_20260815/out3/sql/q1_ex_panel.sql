
WITH raw AS (
  SELECT c.*,
    CASE c.issue_method_code WHEN 'DIV' THEN 'STOCK_DIVIDEND'
                             WHEN 'Bonus' THEN 'BONUS' END AS subtype,
    ROW_NUMBER() OVER (
      PARTITION BY c.ticker, c.exright_date, c.issue_method_code,
                   CAST(c.exercise_ratio AS STRING), CAST(c.issue_volumn AS STRING)
      ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` c
  WHERE c.event_code='ISS' AND c.event_status='executed'
    AND c.issue_method_code IN ('DIV','Bonus')
    AND c.exright_date BETWEEN DATE '2014-01-01' AND DATE '2026-06-30'
    AND c.exercise_ratio > 0
), ev AS (
  SELECT ticker, exright_date AS ex_date,
    SUM(exercise_ratio) AS ratio_total,
    SUM(IFNULL(issue_volumn,0)) AS issue_volume,
    MAX(listing_date) AS listing_date,
    COUNT(DISTINCT subtype) AS n_subtypes,
    STRING_AGG(DISTINCT subtype ORDER BY subtype) AS subtype_list,
    COUNT(*) AS n_components
  FROM raw WHERE rn=1 GROUP BY ticker, ex_date
)

, px AS (
  SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
    SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
    ROW_NUMBER() OVER(PARTITION BY t.ticker ORDER BY t.time) si
  FROM `lithe-record-440915-m9.tav2_bq.ticker` t
  WHERE t.time>=DATE '2013-01-01' AND t.Close>0
    AND t.ticker IN (SELECT DISTINCT ticker FROM ev)
), anchor AS (
  SELECT e.*,p.si si0 FROM ev e JOIN px p
    ON p.ticker=e.ticker AND p.time=e.ex_date
), w AS (
  SELECT a.*,p.si-a.si0 k,p.time dt,p.Close,p.Price,p.Volume,p.ICB_Code,p.ret
  FROM anchor a JOIN px p ON p.ticker=a.ticker AND p.si BETWEEN a.si0-260 AND a.si0+62
)
SELECT ticker,ex_date,ANY_VALUE(ratio_total) ratio_total,
  ANY_VALUE(issue_volume) issue_volume,ANY_VALUE(listing_date) listing_date,
  ANY_VALUE(n_subtypes) n_subtypes,ANY_VALUE(subtype_list) subtype_list,
  ANY_VALUE(n_components) n_components,
  MAX(IF(k=-250,Close,NULL)) c_m250, MAX(IF(k=-250,dt,NULL)) d_m250,
  MAX(IF(k=-230,Close,NULL)) c_m230, MAX(IF(k=-230,dt,NULL)) d_m230,
  MAX(IF(k=-40,Close,NULL)) c_m40, MAX(IF(k=-40,dt,NULL)) d_m40,
  MAX(IF(k=-21,Close,NULL)) c_m21, MAX(IF(k=-21,dt,NULL)) d_m21,
  MAX(IF(k=-20,Close,NULL)) c_m20, MAX(IF(k=-20,dt,NULL)) d_m20,
  MAX(IF(k=-1,Close,NULL)) c_m1,MAX(IF(k=-1,Price,NULL)) p_m1,
  MAX(IF(k=-1,dt,NULL)) d_m1,MAX(IF(k=-1,ICB_Code,NULL)) icb,
  MAX(IF(k=0,Close,NULL)) c_0,MAX(IF(k=0,dt,NULL)) d_0,
  MAX(IF(k=0,Volume,NULL)) v_0,
  MAX(IF(k=1,Close,NULL)) c_1,MAX(IF(k=1,Price,NULL)) p_1,
  MAX(IF(k=2,Close,NULL)) c_2,MAX(IF(k=2,Price,NULL)) p_2,
  MAX(IF(k=3,Close,NULL)) c_3,MAX(IF(k=3,Price,NULL)) p_3,
  MAX(IF(k=5,Close,NULL)) c_5,MAX(IF(k=5,dt,NULL)) d_5,
  MAX(IF(k=10,Close,NULL)) c_10,MAX(IF(k=10,dt,NULL)) d_10,
  MAX(IF(k=20,Close,NULL)) c_20,MAX(IF(k=20,dt,NULL)) d_20,
  MAX(IF(k=60,Close,NULL)) c_60,MAX(IF(k=60,dt,NULL)) d_60,
  AVG(IF(k BETWEEN -60 AND -6,Volume,NULL)) avol_pre,
  AVG(IF(k BETWEEN 1 AND 5,Volume,NULL)) avol_0_5,
  APPROX_QUANTILES(IF(k BETWEEN -60 AND -6,Price*Volume,NULL),2)[OFFSET(1)] adtv_pre,
  APPROX_QUANTILES(IF(k BETWEEN 6 AND 60,Price*Volume,NULL),2)[OFFSET(1)] adtv_post,
  COUNTIF(k BETWEEN -60 AND -6 AND IFNULL(Volume,0)=0) zero_pre,
  COUNTIF(k BETWEEN 6 AND 60 AND IFNULL(Volume,0)=0) zero_post,
  STDDEV(IF(k BETWEEN -60 AND -1,ret,NULL)) rvol60,
  EXP(SUM(IF(k BETWEEN -126 AND -21,LN(1+ret),0)))-1 mom6m
FROM w GROUP BY ticker,ex_date ORDER BY ticker,ex_date
