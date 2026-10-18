
SELECT IFNULL(issue_method_code,'<NULL>') issue_method_code,
       IFNULL(issue_method_name_vi,'<NULL>') issue_method_name_vi,
       COUNT(*) n_rows, COUNTIF(event_status='executed') n_executed,
       COUNTIF(exercise_ratio IS NULL) n_ratio_null,
       COUNTIF(exercise_ratio = 0) n_ratio_zero,
       COUNTIF(exercise_ratio > 0) n_ratio_pos,
       COUNTIF(issue_volumn IS NULL OR issue_volumn = 0) n_volumn_missing_or_zero
FROM tav2_bq.corporate_action WHERE event_code='ISS' GROUP BY 1,2 ORDER BY n_rows DESC
