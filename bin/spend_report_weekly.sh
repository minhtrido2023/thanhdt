#!/usr/bin/env bash
set -euo pipefail

source /home/trido/thanhdt/WorkingClaude/wc_env.sh

exec "$DNA_PYEXE" /home/trido/thanhdt/WorkingClaude/mike/bin/spend_report_weekly.py "$@"
