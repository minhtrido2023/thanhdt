#!/usr/bin/env bash
# Ngu Hanh shadow tracker (server port). Daily 15:30 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/ngu_hanh_shadow_daily.log"
$VENV_PY ngu_hanh_shadow_tracker.py >> "$LOG" 2>&1
{ echo; echo "===================================================="; echo; } >> "$LOG"
