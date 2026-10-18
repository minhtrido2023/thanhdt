
SELECT event_code, COUNT(*) n_with_exright,
       COUNTIF(public_date < exright_date) n_pub_before_ex,
       COUNTIF(public_date = exright_date) n_pub_eq_ex,
       COUNTIF(public_date > exright_date) n_pub_after_ex,
       ROUND(100*COUNTIF(public_date >= exright_date)/COUNT(*),2) pct_pub_not_before_ex,
       MIN(DATE_DIFF(exright_date, public_date, DAY)) min_lead_days,
       APPROX_QUANTILES(DATE_DIFF(exright_date, public_date, DAY),100)[OFFSET(5)] p05_lead_days,
       APPROX_QUANTILES(DATE_DIFF(exright_date, public_date, DAY),100)[OFFSET(50)] p50_lead_days,
       APPROX_QUANTILES(DATE_DIFF(exright_date, public_date, DAY),100)[OFFSET(95)] p95_lead_days,
       MAX(DATE_DIFF(exright_date, public_date, DAY)) max_lead_days
FROM tav2_bq.corporate_action WHERE exright_date IS NOT NULL AND public_date IS NOT NULL
GROUP BY event_code ORDER BY n_with_exright DESC
