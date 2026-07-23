WITH vni AS (
  SELECT x.time, x.Close AS vni_close,
    MAX(x.Close) OVER (ORDER BY x.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS vni_hi1y,
    LEAD(x.Close, 63)  OVER (ORDER BY x.time) AS vni_f63,
    LEAD(x.Close, 126) OVER (ORDER BY x.time) AS vni_f126,
    LEAD(x.Close, 189) OVER (ORDER BY x.time) AS vni_f189,
    LEAD(x.Close, 250) OVER (ORDER BY x.time) AS vni_f250,
    LEAD(x.Close, 375) OVER (ORDER BY x.time) AS vni_f375,
    LEAD(x.Close, 500) OVER (ORDER BY x.time) AS vni_f500,
    LEAD(x.Close, 630) OVER (ORDER BY x.time) AS vni_f630,
    LEAD(x.Close, 750) OVER (ORDER BY x.time) AS vni_f750
  FROM tav2_bq.ticker x WHERE x.ticker="VNINDEX"
),
uni AS (SELECT u.time, u.ticker FROM tav2_mike.universe_pit u WHERE u.in_universe=TRUE),
base AS (
  SELECT t.ticker, t.time, t.Close, t.PB, t.PE, t.NP_P0, t.CF_OA_P0, t.ICB_Code, t.ROE_Min3Y,
    t.Debt_Eq_P0, t.NPM_P0, t.Volume_1M, t.Price,
    MAX(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS hi1y,
    LEAD(t.Close, 63)  OVER (PARTITION BY t.ticker ORDER BY t.time) AS c63,
    LEAD(t.Close, 126) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c126,
    LEAD(t.Close, 189) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c189,
    LEAD(t.Close, 250) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c250,
    LEAD(t.Close, 375) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c375,
    LEAD(t.Close, 500) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c500,
    LEAD(t.Close, 630) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c630,
    LEAD(t.Close, 750) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c750,
    MIN(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 1 FOLLOWING AND 250 FOLLOWING) AS fmin250,
    MIN(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 1 FOLLOWING AND 500 FOLLOWING) AS fmin500,
    MIN(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 1 FOLLOWING AND 750 FOLLOWING) AS fmin750,
    MAX(t.Close) OVER (PARTITION BY t.ticker ORDER BY t.time ROWS BETWEEN 1 FOLLOWING AND 500 FOLLOWING) AS fmax500
  FROM tav2_bq.ticker t WHERE t.PB IS NOT NULL AND t.PB > 0
),
qual AS (
  SELECT b.*, v.vni_close, v.vni_hi1y,
    v.vni_f63, v.vni_f126, v.vni_f189, v.vni_f250, v.vni_f375, v.vni_f500, v.vni_f630, v.vni_f750,
    (SAFE_DIVIDE(b.Close,b.hi1y) - 1) AS stock_dd,
    (SAFE_DIVIDE(v.vni_close,v.vni_hi1y) - 1) AS mkt_dd,
    EXTRACT(YEAR FROM b.time) AS yr
  FROM base b
  JOIN uni u ON u.ticker=b.ticker AND u.time=b.time
  JOIN vni v ON v.time=b.time
  WHERE b.NP_P0 > 0 AND b.CF_OA_P0 > 0 AND b.ROE_Min3Y >= 0
    AND (SAFE_DIVIDE(b.Close,b.hi1y) - 1) <= -0.40           -- stock crashed >=40% from own 1y high
    AND (SAFE_DIVIDE(v.vni_close,v.vni_hi1y) - 1) >= -0.15    -- market broadly fine (NOT deep crisis)
),
ranked AS (SELECT q.*, ROW_NUMBER() OVER (PARTITION BY q.ticker, q.yr ORDER BY q.stock_dd ASC) AS rn FROM qual q)
SELECT ticker, time AS entry_date, yr, ICB_Code,
  ROUND(PB,3) AS PB, ROUND(PE,2) AS PE, ROUND(ROE_Min3Y,3) AS ROE_Min3Y,
  ROUND(Debt_Eq_P0,3) AS DE, ROUND(NPM_P0,4) AS NPM,
  ROUND(Volume_1M*Price,0) AS adv_vnd,
  ROUND(stock_dd,3) AS stock_dd, ROUND(mkt_dd,3) AS mkt_dd,
  ROUND(SAFE_DIVIDE(c63,Close)-1,4)  AS r3m,  ROUND(SAFE_DIVIDE(c126,Close)-1,4) AS r6m,
  ROUND(SAFE_DIVIDE(c189,Close)-1,4) AS r9m,  ROUND(SAFE_DIVIDE(c250,Close)-1,4) AS r12m,
  ROUND(SAFE_DIVIDE(c375,Close)-1,4) AS r18m, ROUND(SAFE_DIVIDE(c500,Close)-1,4) AS r24m,
  ROUND(SAFE_DIVIDE(c630,Close)-1,4) AS r30m, ROUND(SAFE_DIVIDE(c750,Close)-1,4) AS r36m,
  ROUND(SAFE_DIVIDE(c63,Close) - SAFE_DIVIDE(vni_f63,vni_close),4)  AS ex3m,  ROUND(SAFE_DIVIDE(c126,Close) - SAFE_DIVIDE(vni_f126,vni_close),4) AS ex6m,
  ROUND(SAFE_DIVIDE(c189,Close) - SAFE_DIVIDE(vni_f189,vni_close),4) AS ex9m,  ROUND(SAFE_DIVIDE(c250,Close) - SAFE_DIVIDE(vni_f250,vni_close),4) AS ex12m,
  ROUND(SAFE_DIVIDE(c375,Close) - SAFE_DIVIDE(vni_f375,vni_close),4) AS ex18m, ROUND(SAFE_DIVIDE(c500,Close) - SAFE_DIVIDE(vni_f500,vni_close),4) AS ex24m,
  ROUND(SAFE_DIVIDE(c630,Close) - SAFE_DIVIDE(vni_f630,vni_close),4) AS ex30m, ROUND(SAFE_DIVIDE(c750,Close) - SAFE_DIVIDE(vni_f750,vni_close),4) AS ex36m,
  ROUND(SAFE_DIVIDE(fmin250,Close)-1,4) AS mdd12, ROUND(SAFE_DIVIDE(fmin500,Close)-1,4) AS mdd24, ROUND(SAFE_DIVIDE(fmin750,Close)-1,4) AS mdd36,
  ROUND(SAFE_DIVIDE(fmax500,Close)-1,4) AS mfe24
FROM ranked WHERE rn=1 ORDER BY entry_date, ticker
