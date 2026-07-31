#!/usr/bin/env bash
# Milestone paper-trade report (server port). One-off: 2026-06-30 (mid) + 2026-08-31 (final).
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/papertrade_milestone_run_$(date +%F).log"
echo "Milestone report — $(date)" > "$LOG"
$VENV_PY papertrade_milestone_report.py >> "$LOG" 2>&1
echo "Done $(date +%T)" >> "$LOG"
