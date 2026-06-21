#!/usr/bin/env bash
# BullDvg Boost 12-month report (server port). One-off: 2027-05-19 15:30 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY bull_div_boost_tracker.py report > "$WORKDIR_8L/data/bull_div_boost_report_run.log" 2>&1
