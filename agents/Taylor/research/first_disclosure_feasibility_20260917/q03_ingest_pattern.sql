SELECT c.event_code, TIMESTAMP_TRUNC(c.ingested_at, HOUR) ing_hour, COUNT(*) n,
 COUNTIF(c.first_disclosure_datetime IS NOT NULL) n_fd, COUNTIF(c.source_news_id IS NOT NULL) n_sid
FROM tav2_bq.corporate_action AS c GROUP BY 1,2 ORDER BY 2,1
