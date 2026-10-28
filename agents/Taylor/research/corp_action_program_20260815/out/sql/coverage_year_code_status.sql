
SELECT EXTRACT(YEAR FROM public_date) year, event_code, event_status,
       COUNT(*) n_rows, COUNT(DISTINCT ticker) n_ticker,
       COUNTIF(exright_date IS NOT NULL) n_with_exright
FROM tav2_bq.corporate_action GROUP BY 1,2,3 ORDER BY 1,2,3
