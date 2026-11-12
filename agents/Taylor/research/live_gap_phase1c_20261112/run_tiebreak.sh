#!/bin/bash
# 11 chân tie-break: cấu hình pin (AUDIT_END 06-19, park 3:0.3, cache 0729 postrestate, IDLE_CARRY_TIER=off), code vá.
cd "$(dirname "$0")"; S=$PWD/sb
X="AUDIT_END=2026-06-19 PARK_STATES=3:0.3 IDLE_CARRY_TIER=off BQ_LOCAL_CACHE=$S/data/bq_cache_asof20260729_postrestate"
./run_leg.sh exp_gap_c3_TB_base $X & for s in 1 2 3 4 5; do ./run_leg.sh exp_gap_c3_TB_s$s $X TIEBREAK_SEED=$s & done; wait
for s in 6 7 8 9 10; do ./run_leg.sh exp_gap_c3_TB_s$s $X TIEBREAK_SEED=$s & done; wait; echo TBDONE
