
WITH d AS (
  SELECT ticker, exright_date FROM tav2_bq.corporate_action
  WHERE event_code='DIV' AND event_status='executed' AND exright_date IS NOT NULL
    AND exright_date >= '2014-01-01' GROUP BY 1,2)
SELECT EXTRACT(YEAR FROM d.exright_date) year, COUNT(*) n_div_events,
       COUNTIF(u.in_universe) n_in_universe_pit,
       COUNTIF(pr.time IS NOT NULL) n_in_ticker_prune,
       COUNTIF(t.time IS NOT NULL) n_with_any_price
FROM d
LEFT JOIN tav2_mike.universe_pit AS u ON u.ticker=d.ticker AND u.time=d.exright_date
LEFT JOIN tav2_bq.ticker_prune AS pr ON pr.ticker=d.ticker AND pr.time=d.exright_date
LEFT JOIN tav2_bq.ticker AS t ON t.ticker=d.ticker AND t.time=d.exright_date
GROUP BY year ORDER BY year
