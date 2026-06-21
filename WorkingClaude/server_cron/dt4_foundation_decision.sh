#!/usr/bin/env bash
# DT4-vs-TQ34b foundation A/B decision review (server port). One-off 2026-05-29 (PAST — not cron'd).
# Windows MessageBox popup dropped (no GUI on server).
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
$VENV_PY pt_dt4_vs_tq34b_ab.py > "$WORKDIR_8L/data/dt4_foundation_decision_run.log" 2>&1
cp -f "$WORKDIR_8L/data/pt_dt4_vs_tq34b_ab_report.md" "$WORKDIR_8L/data/DT4_FOUNDATION_DECISION.md" 2>/dev/null
