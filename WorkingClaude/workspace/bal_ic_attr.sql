WITH base AS (
  SELECT t.ticker, t.time, t.Close,
    t.D_RSI, t.D_MACDdiff, t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
    t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W,
    t.PE, t.PE_MA5Y, t.PE_SD5Y, t.FSCORE,
    t.NP_P0, t.NP_P1, t.NP_P4, t.ICB_Code, t.Volume_3M_P50, t.Volume, t.Price,
    LEAD(t.Close, 20) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd20,
    LEAD(t.Close, 40) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd40
  FROM tav2_bq.ticker_prune AS t
  WHERE t.D_RSI IS NOT NULL
),
vni_history AS (
  SELECT t.time, t.D_RSI FROM tav2_bq.ticker AS t
  WHERE t.ticker='VNINDEX' AND t.D_RSI IS NOT NULL
),
vni_max3m AS (
  SELECT time, MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m
  FROM vni_history
),
panel AS (
  SELECT b.ticker, b.time, s.state AS state5,
    SAFE_DIVIDE(b.c_fwd20, b.Close) - 1 AS fwd20,
    SAFE_DIVIDE(b.c_fwd40, b.Close) - 1 AS fwd40,
    CAST(b.D_RSI > 0.50 AS INT64) AS t_rsi50,
    CAST(b.Close > b.MA50 AND b.MA50 > b.MA200 AS INT64) AS t_mastack,
    CAST(b.Volume >= b.Volume_3M_P50*1.3 AND b.Close > b.Close_T1 AS INT64) AS t_volsurge,
    CAST(b.D_MACDdiff > 0 AS INT64) AS t_macd,
    CAST(b.Close > b.MA20 AS INT64) AS t_ma20,
    CAST(b.D_RSI > 0.75 AS INT64) AS t_rsi75,
    CAST(b.D_RSI < 0.30 AS INT64) AS t_rsi30,
    CAST(b.PE>0 AND b.PE_MA5Y>0 AND b.PE < b.PE_MA5Y-0.5*b.PE_SD5Y AS INT64) AS t_pecheap,
    CAST(b.PE>0 AND b.PE_MA5Y>0 AND b.PE > b.PE_MA5Y+1.0*b.PE_SD5Y AS INT64) AS t_perich,
    CAST(v.rsi_max3m > 0.65 AS INT64) AS t_vnirsi,
    CAST(b.ID_HI_3Y <= 5 AS INT64) AS t_near3yhi,
    CAST(b.D_RSI_Max1W > 0.65 AS INT64) AS t_rsimax1w,
    CAST(b.FSCORE >= 8 AS INT64) AS t_fscore8,
    CAST(b.NP_P0 > b.NP_P4*1.5 AND b.NP_P4>0 AS INT64) AS t_npyoy_str,
    CAST(b.NP_P0 < b.NP_P4*0.7 AND b.NP_P4>0 AS INT64) AS t_npyoy_wk,
    CAST(b.ICB_Code IS NOT NULL AND CAST(FLOOR(b.ICB_Code/1000) AS INT64) IN (8,9) AS INT64) AS t_secbank,
    CAST(b.ICB_Code IS NOT NULL AND CAST(FLOOR(b.ICB_Code/1000) AS INT64) IN (4,7) AS INT64) AS t_sec47,
    CAST(b.MA50_T1>0 AND b.MA50 > b.MA50_T1 AS INT64) AS t_ma50up,
    CAST(b.MA50_T1>0 AND b.MA50 > b.MA50_T1*1.005 AS INT64) AS t_ma50up2,
    CAST(b.MA50_T1>0 AND b.MA50 < b.MA50_T1 AS INT64) AS t_ma50dn,
    CAST(b.HI_3M_T1>0 AND b.Close/b.HI_3M_T1 < 0.85 AS INT64) AS t_dd3m,
    CAST(b.NP_P0 > b.NP_P1*1.2 AND b.NP_P1>0 AS INT64) AS t_npqoq
  FROM base b
  LEFT JOIN vni_max3m v ON v.time = b.time
  LEFT JOIN tav2_bq.vnindex_5state_dt5g_live s ON s.time = b.time
  WHERE b.Volume_3M_P50*COALESCE(b.Price,b.Close) >= 1e9
)
SELECT state5, COUNT(*) n, AVG(fwd20) avg_fwd20,
  CORR(t_rsi50,fwd20) ic_rsi50, CORR(t_mastack,fwd20) ic_mastack,
  CORR(t_volsurge,fwd20) ic_volsurge, CORR(t_macd,fwd20) ic_macd,
  CORR(t_ma20,fwd20) ic_ma20, CORR(t_rsi75,fwd20) ic_rsi75,
  CORR(t_rsi30,fwd20) ic_rsi30, CORR(t_pecheap,fwd20) ic_pecheap,
  CORR(t_perich,fwd20) ic_perich, CORR(t_vnirsi,fwd20) ic_vnirsi,
  CORR(t_near3yhi,fwd20) ic_near3yhi, CORR(t_rsimax1w,fwd20) ic_rsimax1w,
  CORR(t_fscore8,fwd20) ic_fscore8, CORR(t_npyoy_str,fwd20) ic_npyoy_str,
  CORR(t_npyoy_wk,fwd20) ic_npyoy_wk, CORR(t_secbank,fwd20) ic_secbank,
  CORR(t_sec47,fwd20) ic_sec47, CORR(t_ma50up,fwd20) ic_ma50up,
  CORR(t_ma50up2,fwd20) ic_ma50up2, CORR(t_ma50dn,fwd20) ic_ma50dn,
  CORR(t_dd3m,fwd20) ic_dd3m, CORR(t_npqoq,fwd20) ic_npqoq
FROM panel
WHERE fwd20 IS NOT NULL AND state5 IS NOT NULL
GROUP BY state5 ORDER BY state5
