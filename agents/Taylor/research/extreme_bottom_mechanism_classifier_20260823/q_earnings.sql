-- Bang chung B (§3 PREREG): loi nhuan RO tai q0 / q0+2 / q0+4 quanh moi ARM date.
-- Ro dong bang tai ARM tu tav2_mike.universe_pit (in_universe). Khong dung OShares (TRAP restate).
WITH arms AS (
  SELECT * FROM UNNEST([
    STRUCT('2007-04' AS ep, DATE '2007-04-23' AS arm),
    STRUCT('2009-11', DATE '2009-11-26'),
    STRUCT('2011-05', DATE '2011-05-23'),
    STRUCT('2012-08', DATE '2012-08-27'),
    STRUCT('2018-05', DATE '2018-05-28'),
    STRUCT('2020-03', DATE '2020-03-11'),
    STRUCT('2022-05', DATE '2022-05-13')
  ])
),
uni AS (
  SELECT a.ep, a.arm, u.ticker
  FROM arms a
  JOIN `tav2_mike.universe_pit` u ON u.time = a.arm
  WHERE u.in_universe
),
fin AS (
  SELECT ticker, time, ROE_Trailing,
         NP_P0, NP_P1, NP_P2, NP_P3,
         ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time) AS rn
  FROM `tav2_bq.ticker_financial`
),
anchor AS (           -- q0 = quy tai chinh gan nhat co time <= arm, theo TUNG ma
  SELECT u.ep, u.arm, u.ticker, MAX(f.rn) AS rn0
  FROM uni u JOIN fin f USING (ticker)
  WHERE f.time <= u.arm
  GROUP BY 1,2,3
),
picked AS (
  SELECT a.ep, a.arm, a.ticker, k,
         f.time AS q_time,
         f.ROE_Trailing,
         IF(f.NP_P0 IS NULL OR f.NP_P1 IS NULL OR f.NP_P2 IS NULL OR f.NP_P3 IS NULL,
            NULL, f.NP_P0+f.NP_P1+f.NP_P2+f.NP_P3) AS ttm_np
  FROM anchor a
  CROSS JOIN UNNEST([0,2,4]) AS k
  JOIN fin f ON f.ticker = a.ticker AND f.rn = a.rn0 + k
),
wide AS (
  SELECT ep, arm, ticker,
    MAX(IF(k=0, q_time, NULL)) AS t0,
    MAX(IF(k=4, q_time, NULL)) AS t4,
    MAX(IF(k=0, ROE_Trailing, NULL)) AS roe0,
    MAX(IF(k=2, ROE_Trailing, NULL)) AS roe2,
    MAX(IF(k=4, ROE_Trailing, NULL)) AS roe4,
    MAX(IF(k=0, ttm_np, NULL)) AS np0,
    MAX(IF(k=2, ttm_np, NULL)) AS np2,
    MAX(IF(k=4, ttm_np, NULL)) AS np4
  FROM picked GROUP BY 1,2,3
)
SELECT
  ep, arm,
  COUNT(*) AS n_basket,
  COUNTIF(np0 IS NOT NULL) AS n_np0,
  -- kiem tra khoang cach quy that su la ~12 thang
  APPROX_QUANTILES(DATE_DIFF(t4, t0, MONTH), 100)[OFFSET(50)] AS med_months_q0_to_q4,
  -- M1: median ROE_Trailing muc
  APPROX_QUANTILES(roe0, 100)[OFFSET(50)] AS m1_roe_q0,
  APPROX_QUANTILES(roe2, 100)[OFFSET(50)] AS m1_roe_q2,
  APPROX_QUANTILES(roe4, 100)[OFFSET(50)] AS m1_roe_q4,
  -- M2: median ty le TTM_NP(q+k)/TTM_NP(q0), chi ma co np0>0
  APPROX_QUANTILES(IF(np0>0 AND np2 IS NOT NULL, np2/np0, NULL), 100)[OFFSET(50)] AS m2_ratio_k2,
  APPROX_QUANTILES(IF(np0>0 AND np4 IS NOT NULL, np4/np0, NULL), 100)[OFFSET(50)] AS m2_ratio_k4,
  COUNTIF(np0>0 AND np4 IS NOT NULL) AS n_m2_k4,
  -- M3: % ma co TTM_NP > 0
  SAFE_DIVIDE(COUNTIF(np0>0), COUNTIF(np0 IS NOT NULL)) AS m3_pos_q0,
  SAFE_DIVIDE(COUNTIF(np2>0), COUNTIF(np2 IS NOT NULL)) AS m3_pos_q2,
  SAFE_DIVIDE(COUNTIF(np4>0), COUNTIF(np4 IS NOT NULL)) AS m3_pos_q4
FROM wide
GROUP BY 1,2 ORDER BY 2
