
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

, px0 AS (
 SELECT t.ticker,t.time,t.Close,t.Price,t.Volume,t.ICB_Code,
   SAFE_DIVIDE(t.Close,LAG(t.Close) OVER(PARTITION BY t.ticker ORDER BY t.time))-1 ret,
   LAG(t.Close,21) OVER(PARTITION BY t.ticker ORDER BY t.time) c_l21,
   LAG(t.Close,126) OVER(PARTITION BY t.ticker ORDER BY t.time) c_l126,
   LEAD(t.Close,20) OVER(PARTITION BY t.ticker ORDER BY t.time) c_f20,
   LEAD(t.time,20) OVER(PARTITION BY t.ticker ORDER BY t.time) d_f20
 FROM `lithe-record-440915-m9.tav2_bq.ticker` t WHERE t.time>=DATE '2013-01-01' AND t.Close>0
), px AS (
 SELECT *,AVG(Price*Volume) OVER(PARTITION BY ticker ORDER BY time ROWS BETWEEN 60 PRECEDING AND 6 PRECEDING) adv60,
   STDDEV(ret) OVER(PARTITION BY ticker ORDER BY time ROWS BETWEEN 60 PRECEDING AND 1 PRECEDING) rvol60,
   SAFE_DIVIDE(c_l21,c_l126)-1 mom6m
 FROM px0
), focal AS (
 SELECT e.ticker,e.ex_date,p.ICB_Code icb,p.adv60,p.rvol60,p.mom6m,
   p.Close focal_c0,p.c_f20 focal_c20,p.d_f20 end_date
 FROM ev e JOIN px p ON p.ticker=e.ticker AND p.time=e.ex_date
), cand0 AS (
 SELECT f.ticker event_ticker,f.ex_date,f.end_date,f.focal_c0,f.focal_c20,
   c.ticker control_ticker,c.adv60,c.rvol60,c.mom6m,c.Close control_c0,ce.Close control_c20,
   SAFE_DIVIDE(LN(NULLIF(c.adv60,0))-LN(NULLIF(f.adv60,0)),
     NULLIF(STDDEV(LN(NULLIF(c.adv60,0))) OVER(PARTITION BY f.ticker,f.ex_date),0)) z_adv,
   SAFE_DIVIDE(c.mom6m-f.mom6m,
     NULLIF(STDDEV(c.mom6m) OVER(PARTITION BY f.ticker,f.ex_date),0)) z_mom,
   SAFE_DIVIDE(c.rvol60-f.rvol60,
     NULLIF(STDDEV(c.rvol60) OVER(PARTITION BY f.ticker,f.ex_date),0)) z_vol
 FROM focal f JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u ON u.time=f.ex_date AND u.in_universe
 JOIN px c ON c.ticker=u.ticker AND c.time=f.ex_date
 JOIN px ce ON ce.ticker=c.ticker AND ce.time=f.end_date
 WHERE c.ticker!=f.ticker AND c.adv60>0 AND f.adv60>0 AND c.rvol60 IS NOT NULL AND c.mom6m IS NOT NULL
   AND SUBSTR(CAST(c.ICB_Code AS STRING),1,1)=SUBSTR(CAST(f.icb AS STRING),1,1)
), ranked AS (
 SELECT *,SQRT(z_adv*z_adv+z_mom*z_mom+z_vol*z_vol) dist,
   ROW_NUMBER() OVER(PARTITION BY event_ticker,ex_date ORDER BY
     z_adv*z_adv+z_mom*z_mom+z_vol*z_vol,control_ticker) rank
 FROM cand0 WHERE ABS(z_adv)<=0.5 AND ABS(z_mom)<=0.5 AND ABS(z_vol)<=0.5
)
SELECT * FROM ranked WHERE rank<=50 ORDER BY event_ticker,ex_date,rank
