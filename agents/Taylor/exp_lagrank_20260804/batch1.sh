#!/bin/bash
# Batch 1 — the CAPITAL-CONSTRAINED legs (NAV 1B) that attempt-1 got killed mid-run.
D=/home/trido/thanhdt/WorkingClaude/mike/agents/Taylor/exp_lagrank_20260804
E=mike/agents/Taylor/exp_lagrank_20260804/engine_lagrank.py
$D/run.sh L0b_copyctrl1B   "$E" NAV_TOTAL_B=1 &
for k in dnpr surprise pahl3 fill blend; do
  $D/run.sh A_${k}_w0_1B   "$E" NAV_TOTAL_B=1 LAGRANK_KEY=$k LAGRANK_WINDOW=0 &
done
wait
echo BATCH1_DONE
