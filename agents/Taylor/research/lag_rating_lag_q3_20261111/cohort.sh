#!/usr/bin/env bash
# Cohort: số dòng fa_ratings_8l thêm mỗi lần re-rate (log) vs số dòng hiện có theo time (=Release_Date).
cd "$(dirname "$0")"
grep -E "OK: refreshed" /home/trido/thanhdt/WorkingClaude/mike/logs/fa_ratings_8l_refresh.log | sed -E 's/.*lastModified ([0-9-]+) ([0-9:]+), rows=([0-9]+).*/\1,\2,\3/' | awk -F, '$1>="2026-10-10"' > refresh_rows.csv
bq query --use_legacy_sql=false --project_id=lithe-record-440915-m9 --format=csv --max_rows=500 "SELECT CAST(time AS STRING) d, COUNT(*) n FROM tav2_bq.fa_ratings_8l WHERE time>='2026-10-10' GROUP BY d ORDER BY d" | tail -n +2 > rows_by_time.csv
awk -F, 'NR==FNR{n[$1]=$2;next} {if(p!=""){print $1","$2","$3-p","(n[$1]+0)} p=$3}' rows_by_time.csv refresh_rows.csv | (echo "refresh_date,refresh_time,rows_added,rows_with_time_eq_date"; cat) > cohort_increments.csv
cat cohort_increments.csv
