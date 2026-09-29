#!/bin/bash
W=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/margin_valuation_spread_phase1_20260823
tail -n +3 "$W/joblist.txt" | tr '|' '\t' > "$W/_jobs_variants.tsv"
run_one() {
  tag="${1%%$'\t'*}"; env="${1#*$'\t'}"
  "$W/run_p1.sh" "$tag" $env
}
export -f run_one; export W
parallel_n=6
cat "$W/_jobs_variants.tsv" | xargs -d '\n' -I{} -P $parallel_n bash -c 'run_one "$@"' _ {}
echo "ALL_DONE $(date -u +%FT%TZ)" > "$W/logs/_DRIVER_DONE"
