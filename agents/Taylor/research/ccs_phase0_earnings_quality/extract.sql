WITH funda AS (
  SELECT
    ticker, time, quarter, Release_Date,
    CAST(SUBSTR(quarter,1,4) AS INT64)*4 + CAST(SUBSTR(quarter,6,1) AS INT64) - 1 AS quarter_num,
    NP_P0, CF_OA_P0, totalAsset_P0,
    GPM_P0, GPM_P1, GPM_P2, GPM_P3, GPM_P4, GPM_P5, GPM_P6, GPM_P7,
    DSO_P0, DSO_P4, DIO_P0, DIO_P4, Revenue_YoY_P0,
    Debt_Eq_P0, FinLev_P0, StDebt_P0, LtDebt_P0,
    ROE_Min3Y, CF_OA_3Y
  FROM `lithe-record-440915-m9.tav2_bq.ticker_financial`
  WHERE Release_Date IS NOT NULL AND quarter IS NOT NULL
),
fwd AS (
  SELECT
    f.ticker, f.time, f.quarter, f.Release_Date, f.quarter_num,
    f.NP_P0, f.CF_OA_P0, f.totalAsset_P0,
    f.GPM_P0, f.GPM_P1, f.GPM_P2, f.GPM_P3, f.GPM_P4, f.GPM_P5, f.GPM_P6, f.GPM_P7,
    f.DSO_P0, f.DSO_P4, f.DIO_P0, f.DIO_P4, f.Revenue_YoY_P0,
    f.Debt_Eq_P0, f.FinLev_P0, f.StDebt_P0, f.LtDebt_P0,
    f.ROE_Min3Y, f.CF_OA_3Y,
    f1.NP_P0 AS NP_q1, f2.NP_P0 AS NP_q2, f3.NP_P0 AS NP_q3, f4.NP_P0 AS NP_q4,
    u.time AS uni_time, u.in_universe
  FROM funda f
  LEFT JOIN funda f1 ON f1.ticker=f.ticker AND f1.quarter_num=f.quarter_num+1
  LEFT JOIN funda f2 ON f2.ticker=f.ticker AND f2.quarter_num=f.quarter_num+2
  LEFT JOIN funda f3 ON f3.ticker=f.ticker AND f3.quarter_num=f.quarter_num+3
  LEFT JOIN funda f4 ON f4.ticker=f.ticker AND f4.quarter_num=f.quarter_num+4
  LEFT JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
    ON u.ticker = f.ticker
   AND u.time <= f.Release_Date
   AND u.time >= DATE_SUB(f.Release_Date, INTERVAL 7 DAY)
  QUALIFY ROW_NUMBER() OVER (PARTITION BY f.ticker, f.quarter_num ORDER BY u.time DESC) = 1
)
SELECT
  ticker, time, quarter, Release_Date, quarter_num,
  EXTRACT(YEAR FROM Release_Date) AS release_year,
  NP_P0, NP_q1, NP_q2, NP_q3, NP_q4,
  CASE WHEN NP_P0 > 0 AND NP_q1 IS NOT NULL AND NP_q2 IS NOT NULL
       THEN IF((NP_q1+NP_q2)/2.0 >= 0.8*NP_P0, 1, 0) END AS persist_2q,
  CASE WHEN NP_P0 > 0 AND NP_q1 IS NOT NULL AND NP_q2 IS NOT NULL AND NP_q3 IS NOT NULL AND NP_q4 IS NOT NULL
       THEN IF((NP_q1+NP_q2+NP_q3+NP_q4)/4.0 >= 0.8*NP_P0, 1, 0) END AS persist_4q,
  -- T1 accruals
  SAFE_DIVIDE(NP_P0 - CF_OA_P0, totalAsset_P0) AS accr_q,
  -- T2 gross margin trajectory (8-pt slope, x=0..7 with 0=oldest P7 .. 7=current P0)
  CASE WHEN GPM_P0 IS NOT NULL AND GPM_P1 IS NOT NULL AND GPM_P2 IS NOT NULL AND GPM_P3 IS NOT NULL
        AND GPM_P4 IS NOT NULL AND GPM_P5 IS NOT NULL AND GPM_P6 IS NOT NULL AND GPM_P7 IS NOT NULL
  THEN (
    -- slope = cov(x,y)/var(x), x=0..7 fixed -> var(x)=42 (population), mean_x=3.5
    ( (0-3.5)*GPM_P7 + (1-3.5)*GPM_P6 + (2-3.5)*GPM_P5 + (3-3.5)*GPM_P4
    + (4-3.5)*GPM_P3 + (5-3.5)*GPM_P2 + (6-3.5)*GPM_P1 + (7-3.5)*GPM_P0 ) / 42.0
  ) END AS slope_gpm,
  -- T3 working capital red flag
  CASE WHEN DSO_P0 IS NOT NULL AND DSO_P4 IS NOT NULL AND DSO_P4 != 0
        AND DIO_P0 IS NOT NULL AND DIO_P4 IS NOT NULL AND DIO_P4 != 0
        AND Revenue_YoY_P0 IS NOT NULL
  THEN GREATEST(
    (DSO_P0/DSO_P4 - 1) - Revenue_YoY_P0,
    (DIO_P0/DIO_P4 - 1) - Revenue_YoY_P0
  ) END AS wc_score,
  -- T4 debt structure
  Debt_Eq_P0, FinLev_P0,
  SAFE_DIVIDE(StDebt_P0, StDebt_P0+LtDebt_P0) AS st_debt_ratio,
  -- golden floor cols for overlap check
  ROE_Min3Y, CF_OA_3Y,
  in_universe, uni_time AS uni_asof_time
FROM fwd
WHERE in_universe IS TRUE
ORDER BY ticker, quarter_num
