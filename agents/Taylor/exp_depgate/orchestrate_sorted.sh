#!/bin/bash
# orchestrate_sorted.sh — job Taylor_20260713_145605. Re-runs control (x2, determinism proof)
# + D1/D2/D3 with the stable-sort bq() patch (see run_depgate_variant_sorted.py header).
set -u
cd /home/trido/thanhdt/WorkingClaude
OUT=mike/agents/Taylor/exp_depgate
PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export DEPGATE_BYPASS_VERIFIED=1
R=mike/agents/Taylor/run_depgate_variant_sorted.py

echo "[orchS] $(date +%F' '%T) start ctlSa/ctlSb/D1S/D2S/D3S parallel" >> $OUT/orchestrate.log
$PYEXE $R control ctlSa > $OUT/run_ctlSa.log 2>&1 &
P1=$!
$PYEXE $R control ctlSb > $OUT/run_ctlSb.log 2>&1 &
P2=$!
$PYEXE $R D1 D1S > $OUT/run_D1S.log 2>&1 &
P3=$!
$PYEXE $R D2 D2S > $OUT/run_D2S.log 2>&1 &
P4=$!
$PYEXE $R D3 D3S > $OUT/run_D3S.log 2>&1 &
P5=$!
wait $P1; E1=$?
wait $P2; E2=$?
wait $P3; E3=$?
wait $P4; E4=$?
wait $P5; E5=$?
echo "[orchS] $(date +%F' '%T) done ctlSa=$E1 ctlSb=$E2 D1S=$E3 D2S=$E4 D3S=$E5" >> $OUT/orchestrate.log
touch $OUT/ORCH_SORTED_DONE
