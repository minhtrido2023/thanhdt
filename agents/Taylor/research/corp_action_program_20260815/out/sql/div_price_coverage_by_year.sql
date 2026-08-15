
WITH d AS (
  SELECT ticker, exright_date FROM tav2_bq.corporate_action
  WHERE event_code='DIV' AND event_status='executed' AND exright_date IS NOT NULL GROUP BY 1,2)
SELECT EXTRACT(YEAR FROM d.exright_date) year, COUNT(*) n_div_events,
       COUNTIF(t.time IS NOT NULL) n_with_price_on_exday,
       ROUND(100*COUNTIF(t.time IS NOT NULL)/COUNT(*),1) pct_with_price,
       COUNTIF(u.in_universe) n_in_universe_pit,
       ROUND(100*COUNTIF(u.in_universe)/COUNT(*),1) pct_in_universe_pit
FROM d
LEFT JOIN tav2_bq.ticker AS t ON t.ticker=d.ticker AND t.time=d.exright_date
LEFT JOIN tav2_mike.universe_pit AS u ON u.ticker=d.ticker AND u.time=d.exright_date
GROUP BY year ORDER BY year
