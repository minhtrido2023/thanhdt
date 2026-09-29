#!/usr/bin/env bash
# capture_upcom_vwap_eod.sh — vỏ cron cho mike/bin/capture_upcom_vwap_eod.py.
# Logic ở file .py; vỏ chỉ lo credentials/PATH qua wc_env.sh (đồng nhất với các vỏ khác trong bin/).
set -euo pipefail

# shellcheck source=/dev/null
source /home/trido/thanhdt/WorkingClaude/wc_env.sh

exec python3 /home/trido/thanhdt/WorkingClaude/mike/bin/capture_upcom_vwap_eod.py "$@"
