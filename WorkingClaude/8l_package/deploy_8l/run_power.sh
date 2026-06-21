#!/usr/bin/env bash
# 8L weekly power-lens refresh (BQ-only, safe anywhere).
set -e
cd "$(dirname "$0")/.."
source deploy_8l/env.sh 2>/dev/null || source env.sh
if [ -f venv/bin/activate ]; then source venv/bin/activate; PY=python; else PY=python3; fi
$PY power_lens.py >> data/cron_power.log 2>&1
