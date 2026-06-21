CREATE TEMP TABLE past AS
SELECT time, Close AS close_past, VNINDEX_PE AS pe_past, D_CMF AS cmf_past
FROM `lithe-record-440915-m9.tav2_bq.ticker`
  FOR SYSTEM_TIME AS OF TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 24 HOUR)
WHERE ticker = "VNINDEX" AND time >= "2014-01-01";

WITH now_t AS (
  SELECT time, Close AS close_now, VNINDEX_PE AS pe_now, D_CMF AS cmf_now
  FROM `lithe-record-440915-m9.tav2_bq.ticker`
  WHERE ticker = "VNINDEX" AND time >= "2014-01-01"
)
SELECT
  COUNTIF(ABS(IFNULL(n.close_now,0) - IFNULL(p.close_past,0)) > 0.05) AS n_close_diff,
  COUNTIF(ABS(IFNULL(n.pe_now,0)    - IFNULL(p.pe_past,0))    > 0.001) AS n_pe_diff,
  COUNTIF(ABS(IFNULL(n.cmf_now,0)   - IFNULL(p.cmf_past,0))   > 0.001) AS n_cmf_diff,
  COUNT(*) AS n_total
FROM now_t n
JOIN past p USING (time)
