#!/usr/bin/env bash
# auto_update_commodity_wb.sh — monthly World Bank CMO commodity refresh (Linux).
# Pulls the WB "Pink Sheet" monthly Excel and updates data/*_monthly.csv
# (brent/iron_ore/urea/dap/rubber/sugar; caustic_soda estimated). Idempotent —
# only writes series that have a newer month, so re-running is harmless.
# Schedule monthly (early month, with a 2nd attempt in case WB publishes late).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/auto_update_commodity_wb_$(date +%Y-%m).log"
echo "===== WB commodity refresh START $(date) =====" >> "$LOG"
$PY auto_update_commodity_wb.py >> "$LOG" 2>&1
EXIT=$?
echo "===== exit $EXIT at $(date) =====" >> "$LOG"
exit $EXIT
