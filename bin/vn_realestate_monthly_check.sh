#!/usr/bin/env bash
# vn_realestate_monthly_check.sh — cron wrapper, ngày 6 hàng tháng tối (20:00 ICT).
# Khớp lịch GSO đổi từ 01/08/2024: báo cáo KT-XH tháng công bố ngày 6 tháng kế tiếp
# (trước đó là ngày 29 tháng báo cáo) — 20:00 cho đủ đệm sau giờ công bố hành chính.
# Xem mike/bin/vn_realestate_monthly_check.py cho logic thật.
set -euo pipefail
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$BIN_DIR/../.." && pwd)"
source "$ROOT/wc_env.sh"
exec python3 "$BIN_DIR/vn_realestate_monthly_check.py" "$@"
