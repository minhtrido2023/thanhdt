#!/usr/bin/env bash
# Layer 3 v4 shadow tracker (server port). Daily 15:30 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/layer3_v4_shadow_cron.log"
echo "=== $(date) ===" >> "$LOG"
$VENV_PY layer3_v4_shadow.py update >> "$LOG" 2>&1
echo "--- alert:" >> "$LOG"
$VENV_PY layer3_v4_shadow.py alert >> "$LOG" 2>&1
