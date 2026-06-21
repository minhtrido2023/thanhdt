#!/usr/bin/env bash
# One-time roster-cleanup review (server port). One-off: 2026-06-30 16:30 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/paper_trade_review_run.log"
echo "===== paper-trade roster review $(date) =====" >> "$LOG"
$VENV_PY paper_trade_review.py >> "$LOG" 2>&1
echo "===== done $(date +%T) =====" >> "$LOG"
