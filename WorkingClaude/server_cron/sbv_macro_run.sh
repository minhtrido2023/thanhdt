#!/usr/bin/env bash
# SBV Macro Overlay tracker (server port). Daily 15:20 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY sbv_macro_tracker.py update >> "$WORKDIR_8L/data/sbv_macro_run.log" 2>&1
