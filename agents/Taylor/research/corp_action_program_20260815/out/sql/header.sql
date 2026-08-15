
SELECT COUNT(*) n_rows, COUNT(DISTINCT id) n_id, COUNT(DISTINCT ticker) n_ticker,
       MIN(public_date) min_public_date, MAX(public_date) max_public_date,
       MIN(exright_date) min_exright, MAX(exright_date) max_exright,
       MIN(ingested_at) min_ingested_at, MAX(ingested_at) max_ingested_at
FROM tav2_bq.corporate_action
