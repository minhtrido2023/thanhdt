#!/usr/bin/env bash
# 8L quarterly paper-trade. Usage: run_quarterly.sh snapshot   |   run_quarterly.sh review --telegram
set -e
cd "$(dirname "$0")/.."
source deploy_8l/env.sh 2>/dev/null || source env.sh
if [ -f venv/bin/activate ]; then source venv/bin/activate; PY=python; else PY=python3; fi
$PY pt_8l_quarterly.py "$@" >> data/cron_quarterly.log 2>&1
