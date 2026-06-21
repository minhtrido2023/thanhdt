#!/usr/bin/env bash
# Weekly paper-trade report to Telegram (server port). Friday 15:30 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/paper_trade_weekly_$(date +%F).log"
echo "===== Paper-trade weekly report started $(date) =====" >> "$LOG"
$VENV_PY paper_trade_weekly_report.py >> "$LOG" 2>&1
echo "===== Exit code: $? at $(date +%T) =====" >> "$LOG"
find "$WORKDIR_8L/data" -maxdepth 1 -name 'paper_trade_weekly_*.log' -mtime +60 -delete 2>/dev/null
