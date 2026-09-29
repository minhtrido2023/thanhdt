WITH x AS (
 SELECT s.id, s.ticker, s.event_code, s.snapshot_date, s.first_disclosure_datetime fd, s.source_news_id sid,
  LAG(s.first_disclosure_datetime) OVER (PARTITION BY s.id ORDER BY s.snapshot_date) prev_fd,
  LAG(s.source_news_id) OVER (PARTITION BY s.id ORDER BY s.snapshot_date) prev_sid,
  LAG(s.snapshot_date) OVER (PARTITION BY s.id ORDER BY s.snapshot_date) prev_snap
 FROM tav2_mike.corporate_action_snapshots AS s WHERE s.snapshot_date >= '2026-09-15')
SELECT * FROM x WHERE prev_snap IS NOT NULL AND (
 IFNULL(CAST(fd AS STRING),'~') != IFNULL(CAST(prev_fd AS STRING),'~') OR IFNULL(sid,'~') != IFNULL(prev_sid,'~'))
ORDER BY snapshot_date, ticker
