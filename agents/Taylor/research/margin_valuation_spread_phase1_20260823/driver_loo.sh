#!/bin/bash
W=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_phase1_20260823
tr '|' '\t' < "$W/joblist_loo.txt" > "$W/_jobs_loo.tsv"
run_one(){ tag="${1%%$'\t'*}"; env="${1#*$'\t'}"; "$W/run_p1.sh" "$tag" $env; }
export -f run_one; export W
xargs -d '\n' -I{} -P 5 bash -c 'run_one "$@"' _ {} < "$W/_jobs_loo.tsv"
echo "LOO_DONE $(date -u +%FT%TZ)" > "$W/logs/_LOO_DONE"
