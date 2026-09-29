WITH
vni AS (
  SELECT time, Close AS v0,
         LEAD(Close,60) OVER (ORDER BY time) AS v60
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker='VNINDEX' AND time >= '2005-01-01'
),
px AS (
  SELECT ticker, time, Close, Price,
         LEAD(Close,60) OVER (PARTITION BY ticker ORDER BY time) AS Close_f60,
         LEAD(Price,60) OVER (PARTITION BY ticker ORDER BY time) AS Price_f60
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE time >= '2005-01-01' AND ticker <> 'VNINDEX'
),
bh AS (
  SELECT p.ticker, p.time, p.Close, p.Price,
         SAFE_DIVIDE(p.Close_f60,p.Close)-1 - (SAFE_DIVIDE(v.v60,v.v0)-1) AS bhar60_close,
         SAFE_DIVIDE(p.Price_f60,p.Price)-1 - (SAFE_DIVIDE(v.v60,v.v0)-1) AS bhar60_price
  FROM px p JOIN vni v USING(time)
  WHERE p.Close > 0 AND p.Price > 0 AND p.Close_f60 > 0 AND p.Price_f60 > 0
),
ev AS (
  SELECT id, ticker, exright_date, exercise_ratio, icb_code_lv1,
         SAFE_DIVIDE(total_value, issue_volumn) AS issue_price
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
  WHERE event_code='ISS' AND issue_method_code='Rights'
    AND event_status='executed' AND exright_date IS NOT NULL
),
rights_any AS (   -- moi su kien Rights (moi trang thai) co exright_date: dung de loai control
  SELECT ticker, exright_date
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
  WHERE event_code='ISS' AND issue_method_code='Rights' AND exright_date IS NOT NULL
),
ev_t0 AS (         -- phien giao dich tai/lien sau exright_date
  SELECT e.id, MIN(b.time) AS t0
  FROM ev e JOIN bh b
    ON b.ticker = e.ticker
   AND b.time >= e.exright_date
   AND b.time <  DATE_ADD(e.exright_date, INTERVAL 10 DAY)
  GROUP BY e.id
),
icb_map AS (
  SELECT ticker, ANY_VALUE(icb_code_lv1) AS icb
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
  WHERE icb_code_lv1 IS NOT NULL
  GROUP BY ticker
),
u AS (SELECT ticker, time FROM `lithe-record-440915-m9.tav2_mike.universe_pit` WHERE in_universe)
