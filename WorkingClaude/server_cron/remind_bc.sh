#!/usr/bin/env bash
# 8L BC reminder (server port of remind_bc.bat). One-off 2026-06-06 (PAST — not cron'd).
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY remind_bc.py >> "$WORKDIR_8L/data/remind_bc.log" 2>&1
