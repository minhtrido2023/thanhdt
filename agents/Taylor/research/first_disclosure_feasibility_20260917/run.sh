#!/bin/bash
# usage: run.sh name  (reads name.sql, writes name.csv)
source /home/trido/thanhdt/WorkingClaude/wc_env.sh >/dev/null 2>&1
D=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/first_disclosure_feasibility_20260917
bq query --quiet --use_legacy_sql=false --project_id=lithe-record-440915-m9 --max_rows=100000 --format=csv "$(cat $D/$1.sql)" > $D/$1.csv
echo "rc=$? rows=$(($(wc -l < $D/$1.csv)-1))"
