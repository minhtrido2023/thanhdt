
WITH g AS (
  SELECT ticker, exright_date, STRING_AGG(DISTINCT event_code ORDER BY event_code) codes,
         COUNT(DISTINCT event_code) n_codes, COUNT(*) n_rows
  FROM tav2_bq.corporate_action WHERE exright_date IS NOT NULL AND event_status='executed' GROUP BY 1,2)
SELECT codes, COUNT(*) n_ticker_date_groups, SUM(n_rows) n_rows
FROM g WHERE n_codes>1 GROUP BY codes ORDER BY n_ticker_date_groups DESC
