WITH vni AS (
  SELECT x.time, x.Close AS vni_close,
    MAX(x.Close) OVER (ORDER BY x.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS vni_hi1y,
    x.Close/LAG(x.Close,63) OVER (ORDER BY x.time)-1 AS vni_r3m,
    LEAD(x.Close, 250) OVER (ORDER BY x.time) AS vni_fwd12,
    LEAD(x.Close, 500) OVER (ORDER BY x.time) AS vni_fwd24,
    LEAD(x.Close, 375) OVER (ORDER BY x.time) AS vni_fwd18
  FROM tav2_bq.ticker x WHERE x.ticker="VNINDEX"
),
uni AS (SELECT u.time, u.ticker FROM tav2_mike.universe_pit u WHERE u.in_universe=TRUE),
fin AS (
  SELECT f.ticker, f.time, f.OShares,
    ROW_NUMBER() OVER (PARTITION BY f.ticker ORDER BY f.time DESC) rn_placeholder
  FROM tav2_bq.ticker_financial f
),
base AS (
  SELECT t.ticker, t.time, t.Close, t.Price, t.PB, t.PE, t.NP_P0, t.CF_OA_P0, t.ICB_Code,
    t.ROE_Min3Y, t.Debt_Eq_P0, t.Volume_1M,
    LEAD(t.Close, 250) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd12,
    LEAD(t.Close, 500) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd24,
    LEAD(t.Close, 375) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd18
  FROM tav2_bq.ticker t WHERE t.PB IS NOT NULL AND t.PB > 0 AND t.PB < 1.6
),
qual AS (
  SELECT b.ticker, b.time, b.Close, b.Price, b.PB, b.PE, b.NP_P0, b.CF_OA_P0, b.ICB_Code,
    b.ROE_Min3Y, b.Debt_Eq_P0, b.Volume_1M,
    b.c_fwd12, b.c_fwd24, b.c_fwd18,
    v.vni_close, v.vni_fwd12, v.vni_fwd24, v.vni_fwd18, v.vni_r3m,
    (v.vni_close/v.vni_hi1y - 1) AS mkt_dd, EXTRACT(YEAR FROM b.time) AS yr,
    (b.Volume_1M * b.Price) AS adv_vnd
  FROM base b
  JOIN uni u ON u.ticker=b.ticker AND u.time=b.time
  JOIN vni v ON v.time=b.time
  WHERE b.NP_P0 > 0 AND b.CF_OA_P0 > 0 AND (v.vni_close/v.vni_hi1y - 1) < -0.15
    AND b.ROE_Min3Y >= 0
),
ranked AS (SELECT q.*, ROW_NUMBER() OVER (PARTITION BY q.ticker, q.yr ORDER BY q.PB ASC) AS rn FROM qual q)
SELECT ticker, time AS entry_date, yr, ICB_Code,
  ROUND(PB,3) AS PB, ROUND(PE,2) AS PE, ROUND(ROE_Min3Y,3) AS ROE_Min3Y, ROUND(Debt_Eq_P0,2) AS DE,
  ROUND(mkt_dd,4) AS mkt_dd, ROUND(vni_r3m,4) AS vni_r3m,
  ROUND(adv_vnd,0) AS adv_vnd, ROUND(Price,0) AS price_unadj,
  ROUND(c_fwd12/Close - vni_fwd12/vni_close, 4) AS ex12,
  ROUND(c_fwd24/Close - vni_fwd24/vni_close, 4) AS ex24,
  ROUND(c_fwd18/Close - vni_fwd18/vni_close, 4) AS ex18,
  ROUND(c_fwd12/Close - 1, 4) AS r12, ROUND(c_fwd24/Close - 1, 4) AS r24, ROUND(c_fwd18/Close - 1, 4) AS r18
FROM ranked WHERE rn=1 ORDER BY entry_date, ticker
