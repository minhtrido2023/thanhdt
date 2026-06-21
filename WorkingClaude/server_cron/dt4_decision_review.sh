#!/usr/bin/env bash
# One-time DT 4-gate vs TQ34b decision reminder (server port). One-off: 2026-06-29 09:00 ICT.
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY dt4_decision_review.py >> "$WORKDIR_8L/data/dt4_decision_review.log" 2>&1
