
WITH div AS (
  SELECT ticker, exright_date FROM tav2_bq.corporate_action
  WHERE event_code='DIV' AND event_status='executed' AND exright_date IS NOT NULL
  GROUP BY 1,2),
 iss AS (
  SELECT ticker, exright_date FROM tav2_bq.corporate_action
  WHERE event_code='ISS' AND event_status='executed' AND exright_date IS NOT NULL
  GROUP BY 1,2)
SELECT COUNT(*) n_div_events,
       COUNTIF(EXISTS(SELECT 1 FROM iss i WHERE i.ticker=d.ticker
               AND i.exright_date = d.exright_date)) n_iss_same_day,
       COUNTIF(EXISTS(SELECT 1 FROM iss i WHERE i.ticker=d.ticker
               AND ABS(DATE_DIFF(i.exright_date, d.exright_date, DAY)) <= 5)) n_iss_within_5d,
       COUNTIF(EXISTS(SELECT 1 FROM iss i WHERE i.ticker=d.ticker
               AND ABS(DATE_DIFF(i.exright_date, d.exright_date, DAY)) <= 21)) n_iss_within_21d
FROM div d
