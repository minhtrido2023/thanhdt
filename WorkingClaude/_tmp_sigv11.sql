
WITH fa_dated AS (
  SELECT f.ticker, f.time AS f_time, f.tier AS fa_tier,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_f_time
  FROM tav2_bq.fa_ratings AS f
),
fin_dated AS (
  SELECT f.ticker, f.time AS fin_time, f.Revenue_YoY_P0,
    LEAD(f.time) OVER (PARTITION BY f.ticker ORDER BY f.time) AS next_fin_time
  FROM tav2_bq.ticker_financial AS f
),
latest_vni_max3m AS (
  SELECT t.D_RSI AS rsi_latest
  FROM tav2_bq.ticker AS t WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
  ORDER BY t.time DESC LIMIT 1
),
vni_history AS (
  SELECT t.time, t.D_RSI
  FROM tav2_bq.ticker AS t
  WHERE t.ticker = 'VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time,
    MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
ticker_data AS (
  -- ticker canonical
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50
  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '2024-01-01' AND DATE '2024-01-10'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL

  UNION ALL

  -- ticker_1m fallback for dates where ticker has no D_RSI
  SELECT t.ticker, t.time, t.Close, t.Price, t.Volume, t.D_RSI, t.D_MACDdiff,
         t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
         t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
         t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
         t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50
  FROM tav2_bq.ticker_1m AS t
  WHERE t.time BETWEEN DATE '2024-01-01' AND DATE '2024-01-10'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.D_RSI IS NOT NULL
    AND NOT EXISTS (
      SELECT 1 FROM tav2_bq.ticker AS t2
      WHERE t2.time = t.time AND t2.ticker = t.ticker AND t2.D_RSI IS NOT NULL
    )
),
classified AS (
  SELECT t.ticker, t.time, t.Close,
    (CASE WHEN t.D_RSI > 0.50 THEN 25 ELSE 0 END
    + CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200 THEN 25 ELSE 0 END
    + CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1 THEN 20 ELSE 0 END
    + CASE WHEN t.D_MACDdiff > 0 THEN 15 ELSE 0 END
    + CASE WHEN t.Close > t.MA20 THEN 15 ELSE 0 END
    + CASE WHEN t.D_RSI > 0.75 THEN 5 ELSE 0 END
    + CASE WHEN t.D_RSI < 0.30 THEN -10 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE < t.PE_MA5Y - 0.5*t.PE_SD5Y THEN 15 ELSE 0 END
    + CASE WHEN t.PE > 0 AND t.PE_MA5Y > 0 AND t.PE > t.PE_MA5Y + 1.0*t.PE_SD5Y THEN -15 ELSE 0 END
    + CASE WHEN vmax.rsi_max3m > 0.65 THEN 10 ELSE 0 END
    + CASE WHEN t.ID_HI_3Y <= 5 THEN 8 ELSE 0 END
    + CASE WHEN t.D_RSI_Max1W > 0.65 THEN 5 ELSE 0 END
    + CASE WHEN t.FSCORE >= 8 THEN 10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P4 * 1.5 AND t.NP_P4 > 0 THEN 8 ELSE 0 END
    + CASE WHEN t.NP_P0 < t.NP_P4 * 0.7 AND t.NP_P4 > 0 THEN -8 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (8,9) THEN 5 ELSE 0 END
    + CASE WHEN t.ICB_Code IS NOT NULL AND CAST(FLOOR(t.ICB_Code/1000) AS INT64) IN (4,7) THEN -5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 > t.MA50_T1 * 1.005 THEN 5 ELSE 0 END
    + CASE WHEN t.MA50_T1 > 0 AND t.MA50 < t.MA50_T1 THEN -5 ELSE 0 END
    + CASE WHEN t.HI_3M_T1 > 0 AND t.Close / t.HI_3M_T1 < 0.85 THEN -10 ELSE 0 END
    + CASE WHEN t.NP_P0 > t.NP_P1 * 1.2 AND t.NP_P1 > 0 THEN 8 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier='D' THEN 10 ELSE 0 END
    + CASE WHEN CAST(FLOOR(t.ICB_Code/1000) AS INT64)=8 AND fa.fa_tier='A' THEN -10 ELSE 0 END) AS ta,
    s5_ff.state AS state5, fa.fa_tier,
    SAFE_DIVIDE(t.NP_P0, t.NP_P4) - 1 AS np_yoy,
    fin.Revenue_YoY_P0 AS rev_yoy,
    (t.PE - t.PE_MA5Y) / NULLIF(t.PE_SD5Y, 0) AS pe_z,
    (t.D_RSI > 0.90 OR (t.MA20 > 0 AND t.Close / t.MA20 > 1.25)) AS warn_ext,
    t.Volume_3M_P50 * COALESCE(t.Price, t.Close) AS liq,   -- real (unadjusted) traded notional, not back-adjusted Close
    CAST(FLOOR(t.ICB_Code/1000) AS INT64) AS sec,
    rel.days_since_release
  FROM ticker_data AS t
  LEFT JOIN fa_dated AS fa
    ON fa.ticker = t.ticker AND t.time >= fa.f_time
   AND (fa.next_f_time IS NULL OR t.time < fa.next_f_time)
  LEFT JOIN fin_dated AS fin
    ON fin.ticker = t.ticker AND t.time >= fin.fin_time
   AND (fin.next_fin_time IS NULL OR t.time < fin.next_fin_time)
  LEFT JOIN vni_max3m AS vmax ON vmax.time = t.time
  LEFT JOIN (
    SELECT t2.time, ARRAY_AGG(s.state ORDER BY s.time DESC LIMIT 1)[OFFSET(0)] AS state
    FROM (SELECT DISTINCT time FROM ticker_data) AS t2
    LEFT JOIN tav2_bq.vnindex_5state AS s ON s.time <= t2.time
    GROUP BY t2.time
  ) AS s5_ff ON s5_ff.time = t.time
  LEFT JOIN (
    SELECT t2.ticker, t2.time,
      DATE_DIFF(t2.time, MAX(tf.Release_Date), DAY) AS days_since_release
    FROM (SELECT DISTINCT ticker, time FROM ticker_data) AS t2
    LEFT JOIN tav2_bq.ticker_financial AS tf
      ON tf.ticker = t2.ticker AND tf.Release_Date <= t2.time
    GROUP BY t2.ticker, t2.time
  ) AS rel ON rel.ticker = t.ticker AND rel.time = t.time
)
SELECT ticker, time, Close,
  CASE
    WHEN state5 IN (1, 2) THEN 'AVOID_bear'
    WHEN fa_tier = 'E' THEN 'AVOID_faE'
    -- V11 SV_TIGHT Fresh-Q: state 4-5 (BULL) no filter; state 3 (NEUTRAL) ≤60d
    -- State 1 (CRISIS) ≤30d but blocked anyway via AVOID_bear
    WHEN ta >= 170 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MEGA'
    WHEN ta >= 170 AND state5 IN (4,5) THEN 'S_PRO'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('C','D') THEN 'MOMENTUM'
    WHEN ta >= 155 AND state5 IN (4,5) AND fa_tier IN ('A','B') THEN 'MOMENTUM_QUALITY'
    WHEN ta >= 155 AND state5 = 3 AND fa_tier IN ('C','D')
         AND days_since_release IS NOT NULL AND days_since_release <= 60 THEN 'MOMENTUM_N'
    WHEN fa_tier IN ('A','B') AND pe_z < -0.5 AND ta >= 95 AND state5 IN (3,4,5) AND NOT warn_ext THEN 'COMPOUNDER_BUY'
    WHEN fa_tier = 'C' AND ta >= 100 AND state5 IN (4,5) AND ((np_yoy > 0.20) OR (rev_yoy > 0.20)) THEN 'DEEP_VALUE_RECOVERY'
    WHEN ta >= 140 AND state5 IN (4,5) THEN 'MOMENTUM_S'
    WHEN ta >= 125 AND state5 IN (4,5) THEN 'MOMENTUM_A'
    WHEN ta >= 140 AND state5 = 3 THEN 'MOMENTUM_S_N'
    WHEN fa_tier IN ('A','B') AND ta >= 70 AND ta < 130 THEN 'COMPOUNDER_HOLD'
    WHEN fa_tier IN ('A','B') THEN 'WAIT'
    ELSE 'PASS'
  END AS play_type,
  ta, liq, sec, days_since_release, state5
FROM classified WHERE liq >= 1e9
