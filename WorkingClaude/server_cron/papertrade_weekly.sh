#!/usr/bin/env bash
# Weekly paper-trade report (server port). Sunday 16:00 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/papertrade_weekly_run_$(date +%F).log"
echo "Weekly report — $(date)" > "$LOG"
$VENV_PY papertrade_weekly_report.py >> "$LOG" 2>&1
echo "Done $(date +%T)" >> "$LOG"
