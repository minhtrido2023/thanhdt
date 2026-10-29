# Mọi ISS public_date 2025-01-01..nay (bảng hiện tại) + first_seen trên snapshot + ngày ObjectId.
WITH fs AS (SELECT s.id, MIN(s.snapshot_date) first_seen,
              ARRAY_AGG(s.public_date ORDER BY s.snapshot_date LIMIT 1)[OFFSET(0)] pub0
            FROM tav2_mike.corporate_action_snapshots AS s WHERE s.event_code="ISS" GROUP BY s.id)
SELECT c.id, c.ticker, c.issue_method_code m, c.issue_status_code st, c.event_status,
       c.public_date pub_now, fs.pub0, DATE(c.first_disclosure_datetime, "Asia/Ho_Chi_Minh") fd,
       DATE(TIMESTAMP_SECONDS(CAST(CONCAT("0x", SUBSTR(c.id,1,8)) AS INT64)), "Asia/Ho_Chi_Minh") objid_d,
       fs.first_seen, c.exright_date ex, c.record_date rec, DATE(c.ingested_at, "Asia/Ho_Chi_Minh") ing,
       c.exercise_ratio ratio, c.issue_volumn vol, c.total_value tv
FROM tav2_bq.corporate_action AS c LEFT JOIN fs USING (id)
WHERE c.event_code="ISS" AND c.public_date >= "2025-01-01"
