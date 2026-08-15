
WITH g AS (
  SELECT ticker, exright_date, dividend_year, dividend_stage_vi, COUNT(*) n,
         COUNT(DISTINCT IFNULL(CAST(value_per_share AS STRING),'~')) n_distinct_value
  FROM tav2_bq.corporate_action WHERE event_code='DIV' AND exright_date IS NOT NULL GROUP BY 1,2,3,4)
SELECT COUNT(*) n_groups, COUNTIF(n>1) n_residual_dup_groups,
       SUM(IF(n>1,n,0)) n_residual_dup_rows, MAX(n) max_rows_in_group,
       COUNTIF(n>1 AND n_distinct_value>1) n_residual_dup_conflicting_value
FROM g
