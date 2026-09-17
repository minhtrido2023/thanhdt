SELECT s.id, MIN(s.snapshot_date) first_seen, ARRAY_AGG(s.event_status ORDER BY s.snapshot_date LIMIT 1)[OFFSET(0)] first_status,
 ARRAY_AGG(s.public_date ORDER BY s.snapshot_date LIMIT 1)[OFFSET(0)] first_public_date,
 ARRAY_AGG(FORMAT_TIMESTAMP('%Y-%m-%d %H:%M:%S', s.ingested_at) ORDER BY s.snapshot_date LIMIT 1)[OFFSET(0)] first_ingested_at
FROM tav2_mike.corporate_action_snapshots AS s GROUP BY 1
