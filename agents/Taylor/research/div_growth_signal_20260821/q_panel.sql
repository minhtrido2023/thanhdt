-- Panel div_growth_signal × forward BHAR — job Taylor_20260821_111228, spec = PREREG.md
WITH
cuts AS (                       -- phien cuoi moi thang lich theo lich VNINDEX
  SELECT MAX(time) AS t
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker = 'VNINDEX' AND time >= '2014-01-01'
  GROUP BY DATE_TRUNC(time, MONTH)
),
vni AS (
  SELECT time, Close AS v0,
         LEAD(Close, 20) OVER (ORDER BY time) AS v20,
         LEAD(Close, 60) OVER (ORDER BY time) AS v60
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker = 'VNINDEX' AND time >= '2013-06-01'
),
px AS (
  SELECT ticker, time, Close, Price, ICB_Code,
         LEAD(Close, 20) OVER (PARTITION BY ticker ORDER BY time) AS c20,
         LEAD(Close, 60) OVER (PARTITION BY ticker ORDER BY time) AS c60,
         LEAD(Price, 20) OVER (PARTITION BY ticker ORDER BY time) AS p20,
         LEAD(Price, 60) OVER (PARTITION BY ticker ORDER BY time) AS p60
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE time >= '2013-06-01' AND ticker <> 'VNINDEX'
),
div_raw AS (
  SELECT ticker, exright_date AS ex, value_per_share, public_date, dividend_year,
         dividend_stage_vi, id
  FROM `lithe-record-440915-m9.tav2_bq.corporate_action`
  WHERE event_code = 'DIV' AND event_status = 'executed'
    AND exright_date IS NOT NULL AND value_per_share > 0
),
-- PIT: khu trung lap TRONG pham vi ban ghi da cong bo tai t (PREREG §2)
div_pit AS (
  SELECT c.t, d.ticker, d.ex, d.value_per_share,
         ROW_NUMBER() OVER (
           PARTITION BY c.t, d.ticker, d.ex, d.dividend_year, d.dividend_stage_vi
           ORDER BY d.public_date DESC, d.id DESC) AS rn
  FROM div_raw d
  CROSS JOIN cuts c
  WHERE COALESCE(d.public_date, d.ex) <= c.t
    AND d.ex <= c.t
    AND d.ex > DATE_SUB(c.t, INTERVAL 1460 DAY)
),
div_agg AS (
  SELECT t, ticker,
    IFNULL(SUM(IF(ex > DATE_SUB(t, INTERVAL 365 DAY), value_per_share, 0)), 0) AS div0,
    COUNTIF(ex > DATE_SUB(t, INTERVAL 365 DAY)) AS n0,
    COUNTIF(ex <= DATE_SUB(t, INTERVAL  365 DAY) AND ex > DATE_SUB(t, INTERVAL  730 DAY)) AS n1,
    COUNTIF(ex <= DATE_SUB(t, INTERVAL  730 DAY) AND ex > DATE_SUB(t, INTERVAL 1095 DAY)) AS n2,
    IFNULL(SUM(IF(ex <= DATE_SUB(t, INTERVAL 1095 DAY) AND ex > DATE_SUB(t, INTERVAL 1460 DAY),
                  value_per_share, 0)), 0) AS div3,
    COUNTIF(ex <= DATE_SUB(t, INTERVAL 1095 DAY) AND ex > DATE_SUB(t, INTERVAL 1460 DAY)) AS n3
  FROM div_pit WHERE rn = 1
  GROUP BY t, ticker
)
SELECT
  c.t, u.ticker,
  IFNULL(a.div0, 0) AS div0, IFNULL(a.div3, 0) AS div3,
  IFNULL(a.n0, 0) AS n0, IFNULL(a.n1, 0) AS n1, IFNULL(a.n2, 0) AS n2, IFNULL(a.n3, 0) AS n3,
  p.Close AS close_t, p.Price AS price_t,
  SAFE_DIVIDE(p.c20, p.Close) - 1 - (SAFE_DIVIDE(v.v20, v.v0) - 1) AS bhar20_close,
  SAFE_DIVIDE(p.c60, p.Close) - 1 - (SAFE_DIVIDE(v.v60, v.v0) - 1) AS bhar60_close,
  SAFE_DIVIDE(p.p20, p.Price) - 1 - (SAFE_DIVIDE(v.v20, v.v0) - 1) AS bhar20_price,
  SAFE_DIVIDE(p.p60, p.Price) - 1 - (SAFE_DIVIDE(v.v60, v.v0) - 1) AS bhar60_price,
  p.ICB_Code AS icb_code,
  s.state AS dt5g_state
FROM cuts c
JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
  ON u.time = c.t AND u.in_universe
JOIN px p ON p.ticker = u.ticker AND p.time = c.t
JOIN vni v ON v.time = c.t
LEFT JOIN div_agg a ON a.t = c.t AND a.ticker = u.ticker
LEFT JOIN `lithe-record-440915-m9.tav2_bq.vnindex_5state_dt5g_live` s ON s.time = c.t
WHERE p.Close > 0 AND p.Price > 0
ORDER BY c.t, u.ticker
