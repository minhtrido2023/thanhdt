
SELECT DATE(ingested_at) ingest_date, COUNT(*) n_rows, COUNT(DISTINCT ticker) n_ticker,
       MIN(ingested_at) batch_start, MAX(ingested_at) batch_end,
       MIN(public_date) min_public_date, MAX(public_date) max_public_date,
       COUNTIF(public_date < DATE_SUB(DATE(ingested_at), INTERVAL 30 DAY)) n_public_older_30d
FROM tav2_bq.corporate_action GROUP BY ingest_date ORDER BY ingest_date
