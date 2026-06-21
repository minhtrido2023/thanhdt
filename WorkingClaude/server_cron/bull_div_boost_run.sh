#!/usr/bin/env bash
# BullDvg Boost tracker (server port). Daily 15:15 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY bull_div_boost_tracker.py update >> "$WORKDIR_8L/data/bull_div_boost_run.log" 2>&1
