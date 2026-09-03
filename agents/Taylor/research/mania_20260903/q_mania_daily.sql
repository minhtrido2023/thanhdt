SELECT
  t.time,
  COUNTIF(t.Close > t.MA200) AS n_above_ma200,
  COUNT(*) AS n_total,
  AVG(CASE WHEN t.Risk_Rating <= 2 THEN SAFE_DIVIDE(t.Close, t.Close_T1) - 1 END) AS ret_lowrisk,
  AVG(CASE WHEN t.Risk_Rating >= 5 THEN SAFE_DIVIDE(t.Close, t.Close_T1) - 1 END) AS ret_highrisk,
  COUNTIF(t.Risk_Rating <= 2) AS n_lowrisk,
  COUNTIF(t.Risk_Rating >= 5) AS n_highrisk,
  ANY_VALUE(t.VNINDEX) AS vnindex_close
FROM tav2_bq.ticker AS t
JOIN tav2_mike.universe_pit AS u ON t.ticker = u.ticker AND t.time = u.time AND u.in_universe
WHERE t.time >= '2007-01-01' AND t.MA200 IS NOT NULL
GROUP BY t.time
ORDER BY t.time
