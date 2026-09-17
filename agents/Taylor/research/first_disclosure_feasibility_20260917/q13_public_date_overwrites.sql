WITH x AS (
 SELECT s.id, s.ticker, s.event_code, s.snapshot_date, s.public_date, s.event_status,
  LAG(s.public_date) OVER (PARTITION BY s.id ORDER BY s.snapshot_date) prev_pd
 FROM tav2_mike.corporate_action_snapshots AS s)
SELECT x.id, x.ticker, x.event_code, MIN(x.snapshot_date) first_change_snap,
 ARRAY_AGG(x.prev_pd ORDER BY x.snapshot_date LIMIT 1)[OFFSET(0)] pd_before,
 ARRAY_AGG(x.public_date ORDER BY x.snapshot_date DESC LIMIT 1)[OFFSET(0)] pd_after,
 FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', ANY_VALUE(c.first_disclosure_datetime)) fd_now, ANY_VALUE(c.public_date) pd_now,
 ANY_VALUE(c.exright_date) ex_now, ANY_VALUE(c.event_status) status_now
FROM x JOIN tav2_bq.corporate_action AS c ON c.id=x.id
WHERE x.prev_pd IS NOT NULL AND x.prev_pd != x.public_date
GROUP BY 1,2,3
