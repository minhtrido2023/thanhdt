SELECT c.event_code, COUNT(*) n,
 COUNTIF(c.first_disclosure_datetime IS NOT NULL) n_fd,
 COUNTIF(c.source_news_id IS NOT NULL) n_sid,
 COUNTIF(c.first_disclosure_datetime IS NOT NULL AND c.source_news_id IS NULL) fd_no_sid,
 COUNTIF(c.first_disclosure_datetime IS NULL AND c.source_news_id IS NOT NULL) sid_no_fd,
 MIN(c.first_disclosure_datetime) min_fd, MAX(c.first_disclosure_datetime) max_fd,
 MIN(c.ingested_at) min_ing, MAX(c.ingested_at) max_ing
FROM tav2_bq.corporate_action AS c GROUP BY 1 ORDER BY 2 DESC
