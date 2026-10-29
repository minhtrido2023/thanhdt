# Tỉ lệ pha loãng theo phương thức (2025-26) + pha loãng THU TIỀN tích luỹ 12 tháng/mã (ex trong 365 ngày tới 2026-10-29).
SELECT c.ticker, c.issue_method_code m, c.issue_status_code st, c.exright_date ex, c.exercise_ratio ratio
FROM tav2_bq.corporate_action AS c
WHERE c.event_code="ISS" AND c.public_date >= "2025-01-01" AND c.issue_status_code != "N"
  AND IFNULL(c.event_status, "") != "not_executed"
