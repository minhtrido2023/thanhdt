#!/usr/bin/env bash
# BA-system Telegram notifier (server port). Mon-Fri 18:00 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
LOG="$WORKDIR_8L/data/telegram_run_$(date +%F).log"
echo "===== BA-system Telegram run started $(date) =====" >> "$LOG"
$VENV_PY telegram_recommend.py >> "$LOG" 2>&1
echo "===== Exit code: $? at $(date +%T) =====" >> "$LOG"
# keep last 30 days of logs
find "$WORKDIR_8L/data" -maxdepth 1 -name 'telegram_run_*.log' -mtime +30 -delete 2>/dev/null
