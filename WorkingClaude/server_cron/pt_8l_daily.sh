#!/usr/bin/env bash
# 8L daily EOD orchestrator (server port of pt_8l_daily.bat). Runs ~17:45 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
TODAY=$(date +%F)
LOG="$WORKDIR_8L/data/pt_8l_daily_${TODAY}.log"
run(){ echo "[$(date +%T)] $*" >> "$LOG"; "$@" >> "$LOG" 2>&1; }

{ echo "===================================================="
  echo "8L daily ranking + alert (server) — $(date)"
  echo "===================================================="; } > "$LOG"

run $VENV_PY rating_8l.py
run $VENV_PY unified_screener.py
run $VENV_PY rank_8l.py
run $VENV_PY dna_card.py
run $VENV_PY vn30_8l.py
run $VENV_PY rank_8l_daily_alert.py
run $VENV_PY cheap_pb_floor.py
echo "[7] snapshot rank_8l" >> "$LOG"
$VENV_PY -c "import bot_8l_commands as b; print(b.snapshot_today())" >> "$LOG" 2>&1

echo "Done $(date)" >> "$LOG"
