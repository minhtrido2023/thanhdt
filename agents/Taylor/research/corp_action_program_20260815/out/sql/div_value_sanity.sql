
WITH d AS (
  SELECT c.ticker, c.exright_date, SUM(c.value_per_share) div_per_share
  FROM tav2_bq.corporate_action c WHERE c.event_code='DIV' AND c.event_status='executed'
    AND c.exright_date IS NOT NULL AND c.value_per_share IS NOT NULL GROUP BY 1,2),
 px AS (SELECT t.ticker, t.time, t.Price AS px_raw FROM tav2_bq.ticker AS t WHERE t.Price > 0),
 cum AS (
  SELECT d.ticker, d.exright_date,
         ARRAY_AGG(p.px_raw ORDER BY p.time DESC LIMIT 1)[OFFSET(0)] cum_price_raw
  FROM d JOIN px p ON p.ticker=d.ticker AND p.time < d.exright_date
       AND p.time >= DATE_SUB(d.exright_date, INTERVAL 15 DAY)
  GROUP BY 1,2)
SELECT COUNT(*) n_div_ticker_dates,
       COUNTIF(d.div_per_share <= 0) n_non_positive_value,
       COUNTIF(c.cum_price_raw IS NULL) n_no_cum_price,
       COUNTIF(c.cum_price_raw IS NOT NULL AND d.div_per_share > c.cum_price_raw) n_div_gt_price,
       COUNTIF(c.cum_price_raw IS NOT NULL AND d.div_per_share > 0.5*c.cum_price_raw)
         n_div_gt_half_price,
       COUNTIF(c.cum_price_raw < 1000) n_cum_price_below_1000vnd,
       ROUND(APPROX_QUANTILES(SAFE_DIVIDE(d.div_per_share, c.cum_price_raw),1000)[OFFSET(500)],5)
         p50_gross_yield,
       ROUND(APPROX_QUANTILES(SAFE_DIVIDE(d.div_per_share, c.cum_price_raw),1000)[OFFSET(990)],5)
         p99_gross_yield
FROM d LEFT JOIN cum c USING (ticker, exright_date)
