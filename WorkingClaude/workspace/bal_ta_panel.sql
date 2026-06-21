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
vni_history AS (SELECT t.time, t.D_RSI FROM tav2_bq.ticker AS t WHERE t.ticker='VNINDEX' AND t.D_RSI IS NOT NULL),
vni_max3m AS (SELECT time, MAX(D_RSI) OVER (ORDER BY time ROWS BETWEEN 59 PRECEDING AND CURRENT ROW) AS rsi_max3m FROM vni_history)
SELECT b.ticker, b.time, EXTRACT(YEAR FROM b.time) yr, s.state AS state5,
  SAFE_DIVIDE(b.c_fwd20,b.Close)-1 AS fwd20,
  SAFE_DIVIDE(b.c_fwd40,b.Close)-1 AS fwd40,
  -- momentum block
  ( IF(b.D_RSI>0.50,25,0) + IF(b.Close>b.MA50 AND b.MA50>b.MA200,25,0)
  + IF(b.Volume>=b.Volume_3M_P50*1.3 AND b.Close>b.Close_T1,20,0) + IF(b.D_MACDdiff>0,15,0)
  + IF(b.Close>b.MA20,15,0) + IF(b.D_RSI>0.75,5,0) + IF(b.D_RSI<0.30,-10,0)
  + IF(v.rsi_max3m>0.65,10,0) + IF(b.ID_HI_3Y<=5,8,0) + IF(b.D_RSI_Max1W>0.65,5,0)
  + IF(b.MA50_T1>0 AND b.MA50>b.MA50_T1,5,0) + IF(b.MA50_T1>0 AND b.MA50>b.MA50_T1*1.005,5,0)
  + IF(b.MA50_T1>0 AND b.MA50<b.MA50_T1,-5,0) + IF(b.HI_3M_T1>0 AND b.Close/b.HI_3M_T1<0.85,-10,0) ) AS ta_mom,
  -- value/quality block
  ( IF(b.PE>0 AND b.PE_MA5Y>0 AND b.PE<b.PE_MA5Y-0.5*b.PE_SD5Y,15,0)
  + IF(b.PE>0 AND b.PE_MA5Y>0 AND b.PE>b.PE_MA5Y+1.0*b.PE_SD5Y,-15,0)
  + IF(b.FSCORE>=8,10,0) + IF(b.NP_P0>b.NP_P4*1.5 AND b.NP_P4>0,8,0)
  + IF(b.NP_P0<b.NP_P4*0.7 AND b.NP_P4>0,-8,0) + IF(b.NP_P0>b.NP_P1*1.2 AND b.NP_P1>0,8,0) ) AS ta_val,
  -- sector block
  ( IF(b.ICB_Code IS NOT NULL AND CAST(FLOOR(b.ICB_Code/1000) AS INT64) IN (8,9),5,0)
  + IF(b.ICB_Code IS NOT NULL AND CAST(FLOOR(b.ICB_Code/1000) AS INT64) IN (4,7),-5,0) ) AS ta_sec
FROM base b
LEFT JOIN vni_max3m v ON v.time=b.time
LEFT JOIN tav2_bq.vnindex_5state_dt5g_live s ON s.time=b.time
WHERE b.Volume_3M_P50*COALESCE(b.Price,b.Close)>=1e9
  AND b.c_fwd20 IS NOT NULL AND s.state IS NOT NULL
