SELECT s.snapshot_date, COUNT(*) n, COUNTIF(s.first_disclosure_datetime IS NOT NULL) n_fd,
 COUNTIF(s.source_news_id IS NOT NULL) n_sid, MAX(s.ingested_at) max_ing
FROM tav2_mike.corporate_action_snapshots AS s
WHERE s.snapshot_date >= '2026-09-01' GROUP BY 1 ORDER BY 1
