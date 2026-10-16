
WITH g AS (
  SELECT ticker, exright_date, issue_method_code,
         IFNULL(CAST(exercise_ratio AS STRING),'~') ratio,
         IFNULL(CAST(issue_volumn AS STRING),'~') volumn, COUNT(*) n
  FROM tav2_bq.corporate_action WHERE event_code='ISS' AND exright_date IS NOT NULL GROUP BY 1,2,3,4,5)
SELECT COUNT(*) n_groups, COUNTIF(n>1) n_residual_dup_groups,
       SUM(IF(n>1,n,0)) n_residual_dup_rows, MAX(n) max_rows_in_group
FROM g
