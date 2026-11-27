WITH me AS (
  SELECT MAX(time) AS time FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker='VNINDEX' AND time >= '2007-01-01'
  GROUP BY DATE_TRUNC(time, MONTH)
)
SELECT t.time, t.ticker, t.Price, t.Close, t.OShares, t.PE, t.PB, t.BVPS, t.ICB_Code,
       t.NP_P0, t.NP_P1, t.NP_P2, t.NP_P3, t.NP_P4, t.ID_Release,
       u.in_universe
FROM `lithe-record-440915-m9.tav2_bq.ticker` t
JOIN me USING(time)
LEFT JOIN `lithe-record-440915-m9.tav2_mike.universe_pit` u
  ON u.ticker=t.ticker AND u.time=t.time
WHERE t.ticker NOT IN ('VNINDEX','VN30') AND t.OShares>0 AND t.Price>0
