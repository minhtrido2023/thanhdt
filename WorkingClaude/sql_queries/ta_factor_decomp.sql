-- Per-factor decomposition: does each factor improve forward returns vs. not?
-- For each factor, compare avg/hit rates when factor fires vs. when it doesn't

WITH base AS (
  SELECT
    IF(ABS(t.profit_1M) > 200, NULL, t.profit_1M) AS p1m,
    IF(ABS(t.profit_3M) > 400, NULL, t.profit_3M) AS p3m,

    (t.D_RSI_T1 <= 0.35 AND t.D_RSI > t.D_RSI_T1 + 0.05)               AS f_reversal,
    (t.D_CMB_XFast <= 2 AND t.D_MACDdiff > 0)                          AS f_momentum,
    (t.C_L1M BETWEEN 1.00 AND 1.06 AND t.Close > t.VAP1W)              AS f_position,
    (t.Volume >= t.Volume_3M_P50 * 1.3 AND t.Close > t.Close_T1)       AS f_volume,
    (t.Close > t.MA50 OR (t.Close > t.MA20 AND t.MA20 > t.MA20_T1))    AS f_trend,
    (t.D_CMB_Peak_T1 < -0.3)                                           AS f_bonus_bottom,
    (t.D_RSI > 0.75)                                                   AS f_overbought,
    (t.D_RSI > 0.50 AND t.D_RSI <= 0.75)                               AS f_strong_rsi,
    (t.Close > t.MA50 AND t.MA50 > t.MA200)                            AS f_uptrend,
    (t.D_RSI > 0.40 AND t.D_MACDdiff > 0 AND t.Close > t.MA20)         AS f_strong_combo
  FROM tav2_bq.ticker_prune AS t
  WHERE t.time BETWEEN DATE '2014-01-01' AND DATE '2026-01-16'
    AND t.profit_3M IS NOT NULL
)

SELECT factor, fires, n,
       ROUND(AVG(p1m), 2) AS avg_p1m,
       ROUND(AVG(p3m), 2) AS avg_p3m,
       ROUND(APPROX_QUANTILES(p3m, 100)[OFFSET(50)], 2) AS med_p3m,
       ROUND(COUNTIF(p3m > 0)  / COUNTIF(p3m IS NOT NULL) * 100, 1) AS hit_p3m_pos,
       ROUND(COUNTIF(p3m > 10) / COUNTIF(p3m IS NOT NULL) * 100, 1) AS hit_p3m_gt10,
       ROUND(COUNTIF(p3m > 20) / COUNTIF(p3m IS NOT NULL) * 100, 1) AS hit_p3m_gt20
FROM (
  SELECT 'reversal' AS factor, f_reversal AS fires, p1m, p3m FROM base
  UNION ALL SELECT 'momentum', f_momentum, p1m, p3m FROM base
  UNION ALL SELECT 'position', f_position, p1m, p3m FROM base
  UNION ALL SELECT 'volume',   f_volume,   p1m, p3m FROM base
  UNION ALL SELECT 'trend',    f_trend,    p1m, p3m FROM base
  UNION ALL SELECT 'bonus_bottom', f_bonus_bottom, p1m, p3m FROM base
  UNION ALL SELECT 'overbought_RSI>0.75', f_overbought, p1m, p3m FROM base
  UNION ALL SELECT 'strong_RSI 0.5-0.75', f_strong_rsi, p1m, p3m FROM base
  UNION ALL SELECT 'uptrend_MA50>MA200', f_uptrend, p1m, p3m FROM base
  UNION ALL SELECT 'strong_combo',   f_strong_combo,    p1m, p3m FROM base
) AS unioned, UNNEST([STRUCT(0 AS dummy)])
GROUP BY factor, fires, n
HAVING n > 0
ORDER BY factor, fires DESC;
