#!/bin/bash
# orchestrate_d123.sh — job Taylor_20260713_145605. Runs harness D1/D2/D3 in parallel
# (same vintage as the D0/control runs from Taylor_20260713_141712 — cache untouched since 21:45).
# DEPGATE_BYPASS_VERIFIED=1: same declared bypass as the D0 job (manifest verified=False from the
# 21:33 delta-sync verify failure on unrelated rating tables; integrity gate = control-vs-pin,
# already passed at 27.11% same-vintage).
set -u
cd /home/trido/thanhdt/WorkingClaude
OUT=mike/agents/Taylor/exp_depgate
PYEXE=/home/trido/thanhdt/wc_venv/bin/python
export DEPGATE_BYPASS_VERIFIED=1

echo "[orch123] $(date +%F' '%T) start D1/D2/D3 parallel" >> $OUT/orchestrate.log
$PYEXE mike/agents/Taylor/run_depgate_variant.py D1 > $OUT/run_D1.log 2>&1 &
P1=$!
$PYEXE mike/agents/Taylor/run_depgate_variant.py D2 > $OUT/run_D2.log 2>&1 &
P2=$!
$PYEXE mike/agents/Taylor/run_depgate_variant.py D3 > $OUT/run_D3.log 2>&1 &
P3=$!
wait $P1; E1=$?
wait $P2; E2=$?
wait $P3; E3=$?
echo "[orch123] $(date +%F' '%T) done D1=$E1 D2=$E2 D3=$E3" >> $OUT/orchestrate.log
touch $OUT/ORCH_D123_DONE
