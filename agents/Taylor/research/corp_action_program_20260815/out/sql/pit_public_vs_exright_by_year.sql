
SELECT event_code, EXTRACT(YEAR FROM exright_date) year, COUNT(*) n,
       COUNTIF(public_date >= exright_date) n_pub_not_before_ex,
       ROUND(100*COUNTIF(public_date >= exright_date)/COUNT(*),2) pct_bad
FROM tav2_bq.corporate_action WHERE exright_date IS NOT NULL AND public_date IS NOT NULL AND event_code IN ('DIV','ISS')
GROUP BY 1,2 ORDER BY 1,2
