WITH univ AS (
  SELECT u.time, u.ticker FROM `lithe-record-440915-m9.tav2_mike.universe_pit` AS u
  WHERE u.in_universe AND u.time BETWEEN DATE '2012-06-01' AND DATE '2026-06-19'
),
px AS (
  SELECT t.ticker, t.time, t.Close, t.High, t.Low, t.Open, t.Volume,
         t.MA20, t.MA50, t.MA200, t.D_RSI, t.D_MACDdiff, t.D_CMF, t.D_CMB,
         t.Volume_3M_P50, t.Volume_1M, t.PE, t.PE_MA5Y, t.PE_SD5Y,
         t.profit_1M, t.profit_2M, t.profit_3M,
         COALESCE(t.Price, t.Close) AS raw_px
  FROM `tav2_bq.ticker` AS t
  WHERE t.time BETWEEN DATE '2012-06-01' AND DATE '2026-06-19'
    AND t.Close IS NOT NULL AND t.Close > 0
    AND t.ticker IN (SELECT DISTINCT ticker FROM univ)
),
vni AS (
  SELECT v.time, v.Close AS vni_close,
    SAFE_DIVIDE(v.Close, LAG(v.Close, 21) OVER (ORDER BY v.time)) - 1 AS vni_r21,
    SAFE_DIVIDE(LAG(v.Close,21) OVER (ORDER BY v.time), LAG(v.Close,252) OVER (ORDER BY v.time)) - 1 AS vni_mom12_1
  FROM `tav2_bq.ticker` AS v WHERE v.ticker = 'VNINDEX'
),
w AS (
  SELECT p.*,
    SAFE_DIVIDE(p.Close, LAG(p.Close,1) OVER (PARTITION BY p.ticker ORDER BY p.time)) - 1 AS r1,
    LAG(p.Close,1)  OVER (PARTITION BY p.ticker ORDER BY p.time) AS c_1,
    LAG(p.Close,21) OVER (PARTITION BY p.ticker ORDER BY p.time) AS c_21,
    LAG(p.Close,252)OVER (PARTITION BY p.ticker ORDER BY p.time) AS c_252,
    LAG(p.Close,63) OVER (PARTITION BY p.ticker ORDER BY p.time) AS c_63,
    MAX(p.High) OVER (PARTITION BY p.ticker ORDER BY p.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi252,
    MIN(p.Low)  OVER (PARTITION BY p.ticker ORDER BY p.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS lo252,
    STDDEV_SAMP(p.Close) OVER (PARTITION BY p.ticker ORDER BY p.time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS sd20,
    COUNT(1) OVER (PARTITION BY p.ticker ORDER BY p.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS nhist
  FROM px AS p
),
w2 AS (
  SELECT w.*,
    -- true range for ATR20
    GREATEST(w.High - w.Low, ABS(w.High - w.c_1), ABS(w.Low - w.c_1)) AS tr
  FROM w
),
w3 AS (
  SELECT w2.*,
    AVG(w2.tr) OVER (PARTITION BY w2.ticker ORDER BY w2.time ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS atr20,
    STDDEV_SAMP(w2.r1) OVER (PARTITION BY w2.ticker ORDER BY w2.time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS vol60,
    -- Kaufman efficiency ratio 60d: |net move| / sum |daily move|
    SUM(ABS(w2.Close - w2.c_1)) OVER (PARTITION BY w2.ticker ORDER BY w2.time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS pathlen60,
    -- FIP: share of positive daily returns over the 12-1 formation window (t-252 .. t-21)
    SUM(CASE WHEN w2.r1 > 0 THEN 1 ELSE 0 END) OVER (PARTITION BY w2.ticker ORDER BY w2.time ROWS BETWEEN 251 PRECEDING AND 21 PRECEDING) AS npos_form,
    SUM(CASE WHEN w2.r1 < 0 THEN 1 ELSE 0 END) OVER (PARTITION BY w2.ticker ORDER BY w2.time ROWS BETWEEN 251 PRECEDING AND 21 PRECEDING) AS nneg_form,
    COUNT(w2.r1)                                OVER (PARTITION BY w2.ticker ORDER BY w2.time ROWS BETWEEN 251 PRECEDING AND 21 PRECEDING) AS nform
  FROM w2
)
SELECT
  w3.ticker, w3.time,
  -- ==== NEW indicators ====
  SAFE_DIVIDE(w3.Close, w3.hi252)                            AS prox52,           -- George-Hwang 52w-high proximity
  SAFE_DIVIDE(w3.c_21, w3.c_252) - 1                         AS mom12_1,          -- Jegadeesh-Titman skip-month
  SAFE_DIVIDE(w3.Close, w3.c_63) - 1                         AS mom3m,
  (SAFE_DIVIDE(w3.c_21, w3.c_252) - 1) - v.vni_mom12_1       AS relmom12_1,       -- market-adjusted momentum
  SAFE_DIVIDE((SAFE_DIVIDE(w3.c_21, w3.c_252) - 1) - v.vni_mom12_1,
              NULLIF(w3.vol60 * SQRT(252), 0))               AS residmom_scaled,  -- Blitz-style risk-scaled residual mom (approx)
  SAFE_DIVIDE(w3.Close - w3.MA50, NULLIF(w3.atr20, 0))       AS trend_atr,        -- ATR-normalised trend
  SAFE_DIVIDE(w3.Close - w3.MA20, NULLIF(2 * w3.sd20, 0))    AS bb_pctb_centered, -- Bollinger %B (centered at 0)
  SAFE_DIVIDE(ABS(w3.Close - w3.c_63), NULLIF(w3.pathlen60,0)) AS eff_ratio60,    -- Kaufman efficiency ratio (ADX substitute)
  CASE WHEN (SAFE_DIVIDE(w3.c_21, w3.c_252) - 1) >= 0 THEN 1 ELSE -1 END
    * SAFE_DIVIDE(w3.nneg_form - w3.npos_form, NULLIF(w3.nform,0))  AS fip,       -- Da-Gurun-Warachka info discreteness
  w3.vol60 * SQRT(252)                                       AS idiovol_ann,      -- Ang et al low-vol
  SAFE_DIVIDE(w3.Volume_1M, NULLIF(w3.Volume_3M_P50,0))      AS volratio,         -- volume confirmation
  w3.D_CMF                                                   AS cmf,              -- existing-but-UNUSED by SIGNAL_V11
  -- ==== indicators SIGNAL_V11 already uses (control group) ====
  w3.D_RSI AS rsi, w3.D_MACDdiff AS macddiff,
  SAFE_DIVIDE(w3.Close, NULLIF(w3.MA50,0)) - 1 AS px_ma50,
  SAFE_DIVIDE(w3.PE - w3.PE_MA5Y, NULLIF(w3.PE_SD5Y,0)) AS pe_z,
  SAFE_DIVIDE(1.0, NULLIF(w3.PE,0)) AS ey,
  -- ==== forward returns: RESEARCH IC ONLY, never a live filter ====
  w3.profit_1M, w3.profit_2M, w3.profit_3M,
  w3.Volume_3M_P50 * w3.raw_px AS adv_vnd,
  w3.nhist
FROM w3 JOIN vni AS v ON v.time = w3.time
WHERE w3.time BETWEEN DATE '2014-01-01' AND DATE '2026-06-19'
  AND w3.nhist >= 252
  AND EXISTS (SELECT 1 FROM univ AS u2 WHERE u2.ticker = w3.ticker AND u2.time = w3.time)
QUALIFY w3.time = MAX(w3.time) OVER (PARTITION BY w3.ticker, DATE_TRUNC(w3.time, MONTH))  -- month-end sampling
