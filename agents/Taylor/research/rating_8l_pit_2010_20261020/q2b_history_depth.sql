WITH f AS (
  SELECT ticker, time, ROIC_Min3Y, ROIC_Min5Y, ROE_Min3Y, ROE_Min5Y, ROIC3Y, ROIC5Y, CF_OA_5Y,
    ROW_NUMBER() OVER (PARTITION BY ticker ORDER BY time) - 1 AS n_prior,
    MIN(time) OVER (PARTITION BY ticker) AS first_q
  FROM tav2_bq.ticker_financial)
SELECT EXTRACT(YEAR FROM time) AS yr, COUNT(*) AS n,
  ROUND(AVG(n_prior),1) AS avg_prior_q,
  ROUND(COUNTIF(n_prior < 12)/COUNT(*),3) AS frac_lt12q,
  ROUND(COUNTIF(n_prior < 20)/COUNT(*),3) AS frac_lt20q,
  ROUND(COUNTIF(n_prior < 12 AND ROIC_Min3Y IS NOT NULL)/COUNT(*),3) AS frac_min3y_on_lt12q,
  ROUND(COUNTIF(n_prior < 20 AND ROIC_Min5Y IS NOT NULL)/COUNT(*),3) AS frac_min5y_on_lt20q,
  ROUND(COUNTIF(n_prior < 4 AND ROIC_Min3Y IS NOT NULL)/COUNT(*),3) AS frac_min3y_on_lt4q,
  ROUND(COUNTIF(ROIC_Min5Y = ROIC_Min3Y)/COUNTIF(ROIC_Min3Y IS NOT NULL),3) AS frac_roicmin5_eq_min3,
  ROUND(COUNTIF(ROIC5Y = ROIC3Y)/COUNTIF(ROIC3Y IS NOT NULL),3) AS frac_roic5_eq_3,
  ROUND(COUNTIF(ROE_Min5Y = ROE_Min3Y)/COUNTIF(ROE_Min3Y IS NOT NULL),3) AS frac_roemin5_eq_min3,
  MIN(first_q) AS min_first_q
FROM f WHERE time BETWEEN '2008-01-01' AND '2016-12-31' GROUP BY yr ORDER BY yr
