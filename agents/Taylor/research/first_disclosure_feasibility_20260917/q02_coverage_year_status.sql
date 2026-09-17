SELECT c.event_code, EXTRACT(YEAR FROM COALESCE(c.exright_date, c.effective_date, c.public_date)) yr, c.event_status,
 COUNT(*) n, COUNTIF(c.first_disclosure_datetime IS NOT NULL) n_fd, COUNTIF(c.source_news_id IS NOT NULL) n_sid,
 ROUND(COUNTIF(c.first_disclosure_datetime IS NOT NULL)/COUNT(*),3) pct_fd
FROM tav2_bq.corporate_action AS c GROUP BY 1,2,3 ORDER BY 1,2,3
