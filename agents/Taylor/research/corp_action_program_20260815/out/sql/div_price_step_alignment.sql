
WITH clean AS (
  SELECT c.ticker, c.exright_date, SUM(c.value_per_share) div_per_share
  FROM tav2_bq.corporate_action c
  WHERE c.event_code='DIV' AND c.event_status='executed' AND c.exright_date IS NOT NULL
    AND c.value_per_share IS NOT NULL AND c.exright_date >= '2014-01-01'
    AND NOT EXISTS (SELECT 1 FROM tav2_bq.corporate_action x WHERE x.ticker=c.ticker AND x.event_code='ISS'
                    AND x.event_status='executed'
                    AND ABS(DATE_DIFF(x.exright_date, c.exright_date, DAY)) <= 3)
  GROUP BY 1,2),
 px AS (
  SELECT t.ticker, t.time, SAFE_DIVIDE(t.Price, t.Close) r, t.Price AS px_raw
  FROM tav2_bq.ticker AS t WHERE t.time >= '2013-12-01' AND t.Close > 0 AND t.Price IS NOT NULL),
 bef AS (
  SELECT cl.ticker, cl.exright_date,
         ARRAY_AGG(STRUCT(p.r AS r, p.px_raw AS c) ORDER BY p.time DESC LIMIT 1)[OFFSET(0)] b
  FROM clean cl JOIN px p ON p.ticker=cl.ticker
       AND p.time < cl.exright_date AND p.time >= DATE_SUB(cl.exright_date, INTERVAL 15 DAY)
  GROUP BY 1,2),
 aft AS (
  SELECT cl.ticker, cl.exright_date,
         ARRAY_AGG(STRUCT(p.r AS r) ORDER BY p.time ASC LIMIT 1)[OFFSET(0)] a
  FROM clean cl JOIN px p ON p.ticker=cl.ticker
       AND p.time > cl.exright_date AND p.time <= DATE_ADD(cl.exright_date, INTERVAL 15 DAY)
  GROUP BY 1,2),
 j AS (
  SELECT cl.ticker, cl.exright_date, cl.div_per_share, bef.b.r r_before, bef.b.c cum_price_raw,
         aft.a.r r_after
  FROM clean cl LEFT JOIN bef USING (ticker, exright_date)
                LEFT JOIN aft USING (ticker, exright_date))
SELECT COUNT(*) n_clean_div_events,
       COUNTIF(r_before IS NOT NULL AND r_after IS NOT NULL) n_measurable,
       COUNTIF(r_before > r_after*1.00005) n_ratio_stepped_down,
       COUNTIF(ABS(SAFE_DIVIDE(r_before, r_after)
                   - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share)) <= 0.002)
         n_step_matches_dividend_0p2pct,
       COUNTIF(ABS(SAFE_DIVIDE(r_before, r_after)
                   - SAFE_DIVIDE(cum_price_raw, cum_price_raw - div_per_share)) <= 0.01)
         n_step_matches_dividend_1pct,
       COUNTIF(r_before IS NOT NULL AND r_after IS NOT NULL
               AND ABS(r_before - r_after) < 0.00001) n_no_step_at_all
FROM j
