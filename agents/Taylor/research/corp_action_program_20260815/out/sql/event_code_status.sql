
SELECT event_code, IFNULL(event_status,'<NULL>') event_status, COUNT(*) n_rows,
       COUNT(DISTINCT ticker) n_ticker, MIN(public_date) min_pub, MAX(public_date) max_pub
FROM tav2_bq.corporate_action GROUP BY 1,2 ORDER BY event_code, n_rows DESC
