#!/bin/bash
# orchestrate_d0.sh — job Taylor_20260713_141712. Waits for BQ cache sync to finish+verify,
# then runs harness control + D0 in parallel. Survives the dispatching session being killed.
set -u
cd /home/trido/thanhdt/WorkingClaude
OUT=mike/agents/Taylor/exp_depgate
PYEXE=/home/trido/thanhdt/wc_venv/bin/python

echo "[orch] $(date +%F' '%T) waiting for cache sync (verified=True + no sync procs)" >> $OUT/orchestrate.log
for i in $(seq 1 240); do   # up to 2h
  V=$(python3 -c "import json; print(json.load(open('data/bq_cache/manifest.json')).get('verified'))" 2>/dev/null)
  RUN=$(pgrep -f 'sync_bq_cache' | wc -l)
  if [ "$V" = "True" ] && [ "$RUN" = "0" ]; then break; fi
  if [ "$RUN" = "0" ] && [ "$V" != "True" ]; then
    echo "[orch] $(date +%T) sync exited but verified=$V — waiting 60s then proceeding anyway (data thru 06-19 needed only)" >> $OUT/orchestrate.log
    sleep 60
    RUN2=$(pgrep -f 'sync_bq_cache' | wc -l)
    [ "$RUN2" = "0" ] && break
  fi
  sleep 30
done
V=$(python3 -c "import json; print(json.load(open('data/bq_cache/manifest.json')).get('verified'))" 2>/dev/null)
echo "[orch] $(date +%F' '%T) proceeding: verified=$V" >> $OUT/orchestrate.log

$PYEXE mike/agents/Taylor/run_depgate_variant.py control > $OUT/run_control.log 2>&1 &
P1=$!
$PYEXE mike/agents/Taylor/run_depgate_variant.py D0 > $OUT/run_D0.log 2>&1 &
P2=$!
wait $P1; E1=$?
wait $P2; E2=$?
echo "[orch] $(date +%F' '%T) done control=$E1 D0=$E2" >> $OUT/orchestrate.log
touch $OUT/ORCH_DONE
