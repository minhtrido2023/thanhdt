
WITH t AS (
  SELECT DATE(TIMESTAMP_SECONDS(CAST(CONCAT('0x',SUBSTR(id,1,8)) AS INT64))) id_created_date,
         public_date, exright_date
  FROM tav2_bq.corporate_action WHERE REGEXP_CONTAINS(id, r'^[0-9a-f]{24}$'))
SELECT id_created_date, COUNT(*) n_rows, MIN(public_date) min_pub, MAX(public_date) max_pub,
       COUNTIF(public_date > id_created_date) n_public_after_id_creation
FROM t GROUP BY 1 ORDER BY n_rows DESC LIMIT 40
