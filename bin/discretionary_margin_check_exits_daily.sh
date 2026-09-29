#!/usr/bin/env bash
# discretionary_margin_check_exits_daily.sh — vỏ cron cho `discretionary_margin_gate.py check-exits`.
# Logic ở file .py; vỏ chỉ lo credentials/PATH qua wc_env.sh (đồng nhất các vỏ khác trong bin/).
# Chạy sau giờ đóng cửa (14:45/14:50 ICT) để giá DNSE là giá ATC thật, không phải giữa-phiên.
set -euo pipefail

# shellcheck source=/dev/null
source /home/trido/thanhdt/WorkingClaude/wc_env.sh

exec python3 /home/trido/thanhdt/WorkingClaude/mike/bin/discretionary_margin_gate.py check-exits
