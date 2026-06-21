-- TA Daily Score v2 — Layer 2 of FA+TA combined system
-- Validated on tav2_bq.ticker_prune 2014-2026-01-16 (711k stock-days)
-- Edge: A_90+ in MKT_BULL regime → P3M=+8.56%, hit_gt10=37.4% (vs baseline 5.38% / 30%)
--       A_90+ in MKT_BEAR regime → no edge (skip trading)
--
-- Architecture: Momentum-based, NOT mean-reversion (mean-reversion factors had negative edge)
--
-- Usage:
--   1) For live watchlist: drop the profit_3M filter, restrict to recent dates
--   2) For backtest/eval: keep filter to ensure forward returns available

WITH scored AS (
  SELECT
    t.ticker,
    t.time,
    t.Close,
    t.D_RSI, t.D_MACDdiff, t.MA20, t.MA50, t.MA200,
    t.VNINDEX_RSI, t.VNINDEX_MACDdiff,
    IF(ABS(t.profit_1M) > 200, NULL, t.profit_1M) AS profit_1M,
    IF(ABS(t.profit_2M) > 300, NULL, t.profit_2M) AS profit_2M,
    IF(ABS(t.profit_3M) > 400, NULL, t.profit_3M) AS profit_3M,

    -- Factor scores (validated by per-factor decomposition)
    CASE WHEN t.D_RSI > 0.50                           THEN 25 ELSE 0 END AS s_rsi_strong,
    CASE WHEN t.Close > t.MA50 AND t.MA50 > t.MA200    THEN 25 ELSE 0 END AS s_uptrend,
    CASE WHEN t.Volume >= t.Volume_3M_P50 * 1.3
          AND t.Close > t.Close_T1                     THEN 20 ELSE 0 END AS s_volume,
    CASE WHEN t.D_MACDdiff > 0                         THEN 15 ELSE 0 END AS s_macd_pos,
    CASE WHEN t.Close > t.MA20                         THEN 15 ELSE 0 END AS s_above_ma20,
    CASE WHEN t.D_RSI > 0.75                           THEN  5 ELSE 0 END AS s_bonus_strength,
    CASE WHEN t.D_RSI < 0.30                           THEN -10 ELSE 0 END AS s_penalty_weak,

    -- Market regime
    CASE WHEN t.VNINDEX_RSI > 0.45 AND t.VNINDEX_MACDdiff > 0 THEN 'BULL'
         WHEN t.VNINDEX_RSI > 0.40                            THEN 'NEUTRAL'
         ELSE                                                       'BEAR'
    END AS regime

  FROM tav2_bq.ticker AS t
  WHERE t.time BETWEEN DATE '2014-01-01' AND DATE '2026-01-16'
    AND t.ticker IN (SELECT DISTINCT t2.ticker FROM tav2_bq.ticker_prune AS t2)
    AND t.profit_3M IS NOT NULL
)

SELECT
  *,
  s_rsi_strong + s_uptrend + s_volume + s_macd_pos + s_above_ma20
    + s_bonus_strength + s_penalty_weak AS total_score,
  CASE
    WHEN s_rsi_strong + s_uptrend + s_volume + s_macd_pos + s_above_ma20
       + s_bonus_strength + s_penalty_weak >= 90 AND regime IN ('BULL', 'NEUTRAL') THEN 'BUY_STRONG'
    WHEN s_rsi_strong + s_uptrend + s_volume + s_macd_pos + s_above_ma20
       + s_bonus_strength + s_penalty_weak >= 75 AND regime IN ('BULL', 'NEUTRAL') THEN 'BUY_OK'
    ELSE                                                                                'PASS'
  END AS action
FROM scored;
