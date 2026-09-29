SELECT DATE(c.ingested_at) ing_date, DATE(c.first_disclosure_datetime) >= '2026-09-01' fd_recent,
 EXTRACT(HOUR FROM c.first_disclosure_datetime) hr_utc, COUNT(*) n
FROM tav2_bq.corporate_action AS c WHERE c.first_disclosure_datetime IS NOT NULL AND DATE(c.first_disclosure_datetime) >= '2026-08-01'
GROUP BY 1,2,3 ORDER BY 1,2,3
