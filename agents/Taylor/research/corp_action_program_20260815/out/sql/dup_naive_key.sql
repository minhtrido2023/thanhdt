
WITH g AS (
  SELECT ticker, exright_date, event_code, COUNT(*) n,
         COUNT(DISTINCT IFNULL(CAST(value_per_share AS STRING),'~')) n_distinct_value,
         COUNT(DISTINCT IFNULL(CAST(exercise_ratio AS STRING),'~')) n_distinct_ratio,
         COUNT(DISTINCT IFNULL(issue_method_code,'~')) n_distinct_method
  FROM tav2_bq.corporate_action WHERE exright_date IS NOT NULL GROUP BY 1,2,3)
SELECT event_code, COUNT(*) n_groups, COUNTIF(n>1) n_multi_row_groups,
       SUM(IF(n>1,n,0)) n_rows_in_multi_groups, MAX(n) max_rows_in_group,
       COUNTIF(n>1 AND n_distinct_value=1 AND n_distinct_ratio=1 AND n_distinct_method=1)
         n_groups_all_fields_equal
FROM g GROUP BY event_code ORDER BY n_groups DESC
