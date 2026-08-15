
WITH div_dedup AS (
  SELECT c.ticker, c.exright_date AS ex_date, c.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.ticker, c.exright_date, c.dividend_year, c.dividend_stage_vi
           ORDER BY c.public_date DESC, c.id DESC) AS rn
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action` AS c
  WHERE c.event_code = 'DIV' AND c.event_status = 'executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share > 0
),
ev AS (
  SELECT ticker, ex_date, SUM(value_per_share) AS div_total
  FROM div_dedup WHERE rn = 1
  GROUP BY ticker, ex_date
  HAVING ex_date BETWEEN DATE '2014-01-01' AND DATE '2026-06-30'
),
px AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.PE, t.PB, t.ICB_Code,
         SAFE_DIVIDE(t.Close, LAG(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time)) - 1 AS ret,
         ROW_NUMBER() OVER (PARTITION BY t.ticker ORDER BY t.time) AS si
  FROM `lithe-record-440915-m9.tav2_bq.ticker` AS t
  WHERE t.time >= DATE '2013-01-01'
    AND t.Close IS NOT NULL AND t.Close > 0
    AND t.ticker IN (SELECT DISTINCT ticker FROM ev)
),
anchor AS (
  SELECT e.ticker, e.ex_date, e.div_total, p.si AS si0
  FROM ev AS e
  JOIN px AS p ON p.ticker = e.ticker AND p.time = e.ex_date
),
w AS (
  SELECT a.ticker, a.ex_date, a.div_total, p.si - a.si0 AS k,
         p.time AS dt, p.Close, p.Price, p.Volume, p.PE, p.PB, p.ICB_Code, p.ret
  FROM anchor AS a
  JOIN px AS p ON p.ticker = a.ticker AND p.si BETWEEN a.si0 - 260 AND a.si0 + 62
)
SELECT
  ticker, ex_date, ANY_VALUE(div_total) AS div_total,
  MAX(IF(k = -250, Close, NULL)) AS c_m250,
  MAX(IF(k = -250, dt,    NULL)) AS d_m250,
  MAX(IF(k = -230, Close, NULL)) AS c_m230,
  MAX(IF(k = -230, dt,    NULL)) AS d_m230,
  MAX(IF(k = -126, Close, NULL)) AS c_m126,
  MAX(IF(k = -41,  Close, NULL)) AS c_m41,
  MAX(IF(k = -40,  Close, NULL)) AS c_m40,
  MAX(IF(k = -40,  dt,    NULL)) AS d_m40,
  MAX(IF(k = -21,  Close, NULL)) AS c_m21,
  MAX(IF(k = -21,  dt,    NULL)) AS d_m21,
  MAX(IF(k = -20,  Close, NULL)) AS c_m20,
  MAX(IF(k = -20,  dt,    NULL)) AS d_m20,
  MAX(IF(k = -1,   Close, NULL)) AS c_m1,
  MAX(IF(k = -1,   Price, NULL)) AS p_m1,
  MAX(IF(k = -1,   dt,    NULL)) AS d_m1,
  MAX(IF(k = -1,   PE,    NULL)) AS pe_m1,
  MAX(IF(k = -1,   PB,    NULL)) AS pb_m1,
  MAX(IF(k = -1,   ICB_Code, NULL)) AS icb,
  MAX(IF(k = 0,    Close, NULL)) AS c_0,
  MAX(IF(k = 0,    dt,    NULL)) AS d_0,
  MAX(IF(k = 0,    Volume,NULL)) AS v_0,
  MAX(IF(k = 1,    Close, NULL)) AS c_1,
  MAX(IF(k = 1,    dt,    NULL)) AS d_1,
  MAX(IF(k = 1,    Price, NULL)) AS p_1,
  MAX(IF(k = 2,    Close, NULL)) AS c_2,
  MAX(IF(k = 2,    Price, NULL)) AS p_2,
  MAX(IF(k = 3,    Close, NULL)) AS c_3,
  MAX(IF(k = 3,    Price, NULL)) AS p_3,
  MAX(IF(k = 5,    Close, NULL)) AS c_5,
  MAX(IF(k = 5,    dt,    NULL)) AS d_5,
  MAX(IF(k = 10,   Close, NULL)) AS c_10,
  MAX(IF(k = 10,   dt,    NULL)) AS d_10,
  MAX(IF(k = 20,   Close, NULL)) AS c_20,
  MAX(IF(k = 20,   dt,    NULL)) AS d_20,
  MAX(IF(k = 60,   Close, NULL)) AS c_60,
  MAX(IF(k = 60,   dt,    NULL)) AS d_60,
  AVG(IF(k BETWEEN -60 AND -6, Volume, NULL))          AS advol_60,
  AVG(IF(k BETWEEN -60 AND -6, Volume * Price, NULL))  AS advnd_60,
  AVG(IF(k BETWEEN  1 AND  5,  Volume, NULL))          AS vol_p1_5,
  STDDEV(IF(k BETWEEN -60 AND -1, ret, NULL))          AS rvol_60,
  COUNTIF(k BETWEEN -60 AND -1)                        AS n_pre_sessions
FROM w
GROUP BY ticker, ex_date
ORDER BY ticker, ex_date
