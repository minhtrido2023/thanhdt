#!/bin/bash
# Chạy song song các chân ladder (tối đa J đồng thời). Usage: batch.sh J "TAG ARGS..." ...
A=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/research/live_gap_exec_A
J=$1; shift
B="BASKET_WT=namecap BASKET_SELECT=yieldcombo"
for spec in "$@"; do
  while [ "$(jobs -rp | wc -l)" -ge "$J" ]; do sleep 5; done
  # shellcheck disable=SC2086
  "$A/${RUNLEG:-run_leg.sh}" $spec $B &
  sleep 2
done
wait
