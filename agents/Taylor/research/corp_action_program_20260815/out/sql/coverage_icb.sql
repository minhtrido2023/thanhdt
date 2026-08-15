
SELECT IFNULL(icb_code_lv1,'<NULL>') icb_code_lv1, event_code, COUNT(*) n_rows,
       COUNT(DISTINCT ticker) n_ticker
FROM tav2_bq.corporate_action GROUP BY 1,2 ORDER BY n_rows DESC
