
WITH daily AS (
  SELECT
    t.time, t.ticker, t.ICB_Code AS icb,
    SAFE_DIVIDE(LEAD(t.Close, 60) OVER w, t.Close) - 1 AS fwd_3m,
    SAFE_DIVIDE(LEAD(t.Close, 20) OVER w, t.Close) - 1 AS fwd_1m,
    COALESCE(t.Price, t.Close) * t.Volume AS liq,
    t.PB, t.PE,
    SAFE_DIVIDE(t.PB - t.PB_MA5Y, NULLIF(t.PB_SD5Y, 0)) AS pb_z,
    t.ROIC5Y, t.FSCORE, t.ROE_Min5Y, t.D_RSI, t.D_CMF,
    SAFE_DIVIDE(t.Close, NULLIF(t.MA200, 0)) - 1 AS mom_200,
    t.C_L1M,
    ROW_NUMBER() OVER (PARTITION BY t.ticker, EXTRACT(YEAR FROM t.time),
                       EXTRACT(MONTH FROM t.time) ORDER BY t.time) AS rn_month
  FROM tav2_bq.ticker_prune AS t
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)
)
SELECT d.time, d.ticker, d.icb, d.fwd_3m, d.fwd_1m, d.liq, d.pb_z, d.PB, d.PE,
       d.ROIC5Y, d.FSCORE, d.ROE_Min5Y, d.D_RSI, d.D_CMF, d.mom_200, d.C_L1M
FROM daily AS d
WHERE d.rn_month = 1 AND d.time >= "2014-01-01" AND d.fwd_3m IS NOT NULL
  AND d.ticker != "VNINDEX" AND d.liq >= 1e9
ORDER BY d.time, d.ticker
