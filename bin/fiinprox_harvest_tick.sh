#!/usr/bin/env bash
# fiinprox_harvest_tick.sh — cron wrapper (3 lần/giờ) cho hàng đợi harvest FiinPro-X trial.
# Logic thật + luật chống giới hạn: mike/bin/fiinprox_harvest_tick.py
set -euo pipefail
BIN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$BIN_DIR/../.." && pwd)"
source "$ROOT/wc_env.sh"
exec python3 "$BIN_DIR/fiinprox_harvest_tick.py" "${@:-tick}"
