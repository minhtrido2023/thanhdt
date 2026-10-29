-- Độ trễ nguồn cho sự kiện TĂNG VỐN (ISS) — đo trên vintage append-only, không trên bảng upsert.
-- first_seen = snapshot đầu tiên thấy id; pub0/fd0/ratio0 = giá trị ở vintage ĐẦU (trước khi vendor ghi đè).
-- objid_ts = 8 hex đầu của id (ObjectId) = thời điểm VENDOR tạo record (giả định định dạng ObjectId — kiểm ở REPORT).
WITH v AS (
  SELECT s.id, s.ticker, s.issue_method_code m, s.snapshot_date, s.public_date, s.first_disclosure_datetime fd,
         s.exright_date, s.exercise_ratio, s.issue_status_code st, s.event_status, s.ingested_at,
         ROW_NUMBER() OVER (PARTITION BY s.id ORDER BY s.snapshot_date) rn
  FROM tav2_mike.corporate_action_snapshots AS s WHERE s.event_code = "ISS"),
f AS (SELECT * EXCEPT(rn) FROM v WHERE rn = 1),
cur AS (SELECT c.id, c.public_date pub_now, c.exright_date ex_now, c.ingested_at ing_now, c.issue_status_code st_now,
               c.first_disclosure_datetime fd_now, c.exercise_ratio ratio_now FROM tav2_bq.corporate_action AS c WHERE c.event_code="ISS")
SELECT f.id, f.ticker, f.m, f.st, f.snapshot_date first_seen, f.public_date pub0, DATE(f.fd, "Asia/Ho_Chi_Minh") fd0,
       DATE(TIMESTAMP_SECONDS(CAST(CONCAT("0x", SUBSTR(f.id,1,8)) AS INT64)), "Asia/Ho_Chi_Minh") objid_d,
       f.exright_date ex0, cur.ex_now, cur.pub_now, DATE(cur.fd_now, "Asia/Ho_Chi_Minh") fd_now, DATE(cur.ing_now, "Asia/Ho_Chi_Minh") ing_now,
       cur.st_now, f.exercise_ratio ratio0, cur.ratio_now
FROM f JOIN cur USING (id)
WHERE f.snapshot_date > "2026-08-17" OR f.ticker IN ("SCL","MBB","VIB","DSC")
