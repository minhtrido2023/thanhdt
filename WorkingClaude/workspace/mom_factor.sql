-- Daily cross-sectional momentum-factor return (causal): rank by ta_mom at t, realize t->t+1 return.
WITH base AS (
  SELECT t.ticker, t.time, t.Close,
    t.D_RSI, t.D_MACDdiff, t.MA20, t.MA50, t.MA200, t.MA50_T1, t.Close_T1,
    t.HI_3M_T1, t.ID_HI_3Y, t.D_RSI_Max1W, t.Volume_3M_P50, t.Volume, t.Price,
    LEAD(t.Close,1) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_next
  FROM tav2_bq.ticker_prune AS t
  WHERE t.D_RSI IS NOT NULL
),
scored AS (
  SELECT ticker, time,
    SAFE_DIVIDE(c_next, Close)-1 AS ret_fwd1,
    ( IF(D_RSI>0.50,25,0)+IF(Close>MA50 AND MA50>MA200,25,0)
    + IF(Volume>=Volume_3M_P50*1.3 AND Close>Close_T1,20,0)+IF(D_MACDdiff>0,15,0)
    + IF(Close>MA20,15,0)+IF(D_RSI>0.75,5,0)+IF(D_RSI<0.30,-10,0)
    + IF(ID_HI_3Y<=5,8,0)+IF(D_RSI_Max1W>0.65,5,0)
    + IF(MA50_T1>0 AND MA50>MA50_T1,5,0)+IF(MA50_T1>0 AND MA50>MA50_T1*1.005,5,0)
    + IF(MA50_T1>0 AND MA50<MA50_T1,-5,0)+IF(HI_3M_T1>0 AND Close/HI_3M_T1<0.85,-10,0) ) AS ta_mom
  FROM base
  WHERE c_next IS NOT NULL AND Volume_3M_P50*COALESCE(Price,Close)>=1e9
),
ranked AS (
  SELECT time, ret_fwd1, ta_mom,
    NTILE(5) OVER (PARTITION BY time ORDER BY ta_mom) AS q
  FROM scored
)
SELECT time,
  AVG(IF(q=5,ret_fwd1,NULL)) AS top_ret,
  AVG(IF(q=1,ret_fwd1,NULL)) AS bot_ret,
  AVG(IF(q=5,ret_fwd1,NULL)) - AVG(IF(q=1,ret_fwd1,NULL)) AS mom_factor_ret,
  COUNT(*) AS n
FROM ranked
GROUP BY time HAVING n>=20 ORDER BY time
