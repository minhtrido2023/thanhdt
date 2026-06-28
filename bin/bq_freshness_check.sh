#!/usr/bin/env bash
# bq_freshness_check.sh — kiểm tra freshness của các bảng BQ quan trọng
#
# Chạy thủ công hoặc từ watchdog/cron sau 19:00 ICT mỗi ngày giao dịch.
# Exit 0 = tất cả fresh. Exit 1 = có bảng stale (alert đã gửi Telegram).
#
# Tables checked:
#   tav2_bq.ticker_prune       — daily EOD price (pipeline step H)
#   tav2_bq.vnindex_5state_dt5g_live — DT5G regime (pipeline step G)
#   tav2_bq.ticker_financial   — quarterly fundamentals (pipeline step H financial)
#
# Usage: bin/bq_freshness_check.sh [--quiet]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true

QUIET="${1:-}"
PROJECT="lithe-record-440915-m9"
MAX_PRICE_LAG=2      # trading days: allow weekend/holiday gap
MAX_STATE_LAG=2      # trading days for DT5G regime
MAX_FIN_LAG=30       # calendar days: financial data updates quarterly
TODAY="$(date +%Y-%m-%d)"
FAILED=0

_check() {
  local label="$1" table="$2" col="$3" max_lag_days="$4" lag_unit="$5"
  local query result lag_days

  if [ "$lag_unit" = "trading" ]; then
    # Count trading days gap using VNINDEX as the calendar (clustered, cheap)
    query="SELECT COUNTIF(v.time > (SELECT MAX(t.${col}) FROM \`${PROJECT}.${table}\` AS t))
                   AS gap_days
           FROM \`${PROJECT}.tav2_bq.ticker\` AS v
           WHERE v.ticker='VNINDEX' AND v.time >= (SELECT MAX(t.${col}) FROM \`${PROJECT}.${table}\` AS t)"
  else
    # Calendar day gap
    query="SELECT DATE_DIFF(CURRENT_DATE('Asia/Ho_Chi_Minh'),
                            MAX(t.${col}), DAY) AS gap_days
           FROM \`${PROJECT}.${table}\` AS t"
  fi

  result=$(bq query --use_legacy_sql=false --project_id="$PROJECT" \
    --format=csv --quiet "$query" 2>/dev/null | tail -1)
  lag_days="${result:-999}"

  # Strip decimals if any
  lag_days=$(printf "%.0f" "$lag_days" 2>/dev/null || echo 999)

  if [ "$lag_days" -le "$max_lag_days" ] 2>/dev/null; then
    [ -z "$QUIET" ] && echo "OK   $label: lag=${lag_days}${lag_unit}d (≤${max_lag_days})"
    return 0
  else
    echo "FAIL $label: lag=${lag_days}${lag_unit}d (>${max_lag_days}) — bảng STALE"
    "$ROOT/bin/notify.sh" "⚠️ BQ STALE: $label lag=${lag_days}${lag_unit}d (>${max_lag_days}). Pipeline EOD có thể bị skip hoặc step G/H fail. Kiểm tra cron + pipeline log." 2>/dev/null || true
    FAILED=1
    return 1
  fi
}

echo "=== BQ Freshness Check — $TODAY ==="

_check "ticker_prune (EOD price)"         "tav2_bq.ticker_prune"            "time"  $MAX_PRICE_LAG  "trading" || true
_check "vnindex_5state_dt5g_live (DT5G)"  "tav2_bq.vnindex_5state_dt5g_live" "time" $MAX_STATE_LAG  "trading" || true
_check "ticker_financial (fundamentals)"  "tav2_bq.ticker_financial"         "time"  $MAX_FIN_LAG    "calendar" || true

if [ "$FAILED" -eq 0 ]; then
  [ -z "$QUIET" ] && echo "=== ALL OK ==="
  exit 0
else
  echo "=== FAILED — xem alert Telegram ==="
  exit 1
fi
