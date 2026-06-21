#!/usr/bin/env bash
# Paper-trade simulator daily (server port of paper_trade_run.bat). Daily 14:55 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY paper_trade_daily.py >> "$WORKDIR_8L/data/paper_trade_cron.log" 2>&1
