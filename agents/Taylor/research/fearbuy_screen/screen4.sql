WITH vni AS (
  SELECT x.time, x.Close AS vni_close,
    MAX(x.Close) OVER (ORDER BY x.time ROWS BETWEEN 251 PRECEDING AND CURRENT ROW) AS vni_hi1y,
    LEAD(x.Close, 250) OVER (ORDER BY x.time) AS vni_fwd12,
    LEAD(x.Close, 500) OVER (ORDER BY x.time) AS vni_fwd24
  FROM tav2_bq.ticker x WHERE x.ticker="VNINDEX"
),
uni AS (SELECT u.time, u.ticker FROM tav2_mike.universe_pit u WHERE u.in_universe=TRUE),
base AS (
  SELECT t.ticker, t.time, t.Close, t.PB, t.NP_P0, t.CF_OA_P0, t.ICB_Code, t.ROE_Min3Y,
    t.Debt_Eq_P0, t.NPM_P0,
    LEAD(t.Close, 250) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd12,
    LEAD(t.Close, 500) OVER (PARTITION BY t.ticker ORDER BY t.time) AS c_fwd24
  FROM tav2_bq.ticker t WHERE t.PB IS NOT NULL AND t.PB > 0
)
SELECT b.ticker, b.time AS entry_date, EXTRACT(YEAR FROM b.time) AS yr, b.ICB_Code,
  ROUND(b.PB,3) AS PB, ROUND(b.ROE_Min3Y,3) AS ROE_Min3Y,
  ROUND(b.Debt_Eq_P0,3) AS DE, ROUND(b.NPM_P0,4) AS NPM,
  ROUND(v.vni_close/v.vni_hi1y - 1,3) AS mkt_dd,
  ROUND(b.c_fwd12/b.Close - v.vni_fwd12/v.vni_close, 4) AS ex12,
  ROUND(b.c_fwd24/b.Close - v.vni_fwd24/v.vni_close, 4) AS ex24,
  ROUND(b.c_fwd12/b.Close - 1, 4) AS r12, ROUND(b.c_fwd24/b.Close - 1, 4) AS r24
FROM base b
JOIN uni u ON u.ticker=b.ticker AND u.time=b.time
JOIN vni v ON v.time=b.time
WHERE b.PB < 1.0 AND b.NP_P0 > 0 AND b.CF_OA_P0 > 0 AND (v.vni_close/v.vni_hi1y - 1) < -0.20
ORDER BY b.time, b.ticker
