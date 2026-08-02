-- Panel ma-ngay cho nghien cuu value x DT5G (cross-sectional).
-- Ngay quan sat = phien GIAO DICH CUOI cua moi thang (lich = tav2_bq.vnindex_5state_dt5g_live).
WITH cal AS (
  SELECT time, state,
         ROW_NUMBER() OVER (PARTITION BY DATE_TRUNC(time, MONTH) ORDER BY time DESC) rn
  FROM tav2_bq.vnindex_5state_dt5g_live
),
obs AS (SELECT time AS d, state FROM cal WHERE rn = 1),
px AS (
  SELECT t.time, t.ticker, t.Close,
         LEAD(t.Close, 20) OVER w AS c20, LEAD(t.time, 20) OVER w AS d20,
         LEAD(t.Close, 60) OVER w AS c60, LEAD(t.time, 60) OVER w AS d60
  FROM tav2_bq.ticker AS t
  WHERE t.time >= DATE '2014-06-01'
  WINDOW w AS (PARTITION BY t.ticker ORDER BY t.time)
)
SELECT o.d, o.state, t.ticker, t.ICB_Code,
       t.Close, t.Price, t.PE, t.PCF, t.EVEB, t.PB, t.PB_MA5Y, t.PB_SD5Y,
       t.Dividend_Min3Y, t.CF_OA_5Y, t.CF_OA_P0, t.CF_OA_P1, t.CF_OA_P2, t.CF_OA_P3,
       t.ROE_Min5Y, t.ROE5Y, t.ROE_Min3Y,
       t.Trading_Value_1M_P50 AS liq,
       px.c20, px.d20, px.c60, px.d60
FROM obs o
JOIN tav2_bq.ticker AS t ON t.time = o.d
JOIN tav2_mike.universe_pit AS u ON u.time = o.d AND u.ticker = t.ticker AND u.in_universe
JOIN px ON px.time = o.d AND px.ticker = t.ticker
WHERE t.time >= DATE '2014-06-01'
