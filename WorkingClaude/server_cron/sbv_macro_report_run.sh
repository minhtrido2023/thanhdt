#!/usr/bin/env bash
# SBV 12-month report (server port). One-off: 2027-05-19 15:35 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY sbv_macro_tracker.py report > "$WORKDIR_8L/data/sbv_macro_report_run.log" 2>&1
