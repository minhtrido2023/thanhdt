#!/usr/bin/env bash
# bq_freshness_check.sh — kiểm tra freshness các bảng BQ → nếu fresh chạy pipeline EOD
#
# Luồng 17:30 ICT (cron: 30 10 * * 1-5):
#   → STALE: cảnh báo Telegram + Discord stale-alert channel, dừng, block DollarBill
#   → FRESH: publish_gated_state → golive_recommend → push_to_bq → dispatch DollarBill lập plan
#
# Tables checked:
#   tav2_bq.ticker_prune              — daily EOD price (pipeline step H)
#   tav2_bq.vnindex_5state_dt5g_live  — DT5G regime (pipeline step G)
#   tav2_bq.ticker_financial          — quarterly fundamentals (pipeline step H financial)
#
# Usage: bin/bq_freshness_check.sh [--quiet]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true

QUIET="${1:-}"
PROJECT="lithe-record-440915-m9"
MAX_PRICE_LAG=2      # trading days: cho phép gap weekend/nghỉ lễ
MAX_STATE_LAG=2      # trading days cho DT5G regime
MAX_FIN_LAG=30       # calendar days: financial data cập nhật theo quý
TODAY="$(date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"
FAILED=0

WORKDIR="${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}"
PY="${DNA_PYEXE:-python3}"

# Discord channels (giờ Việt Nam — ICT)
DISCORD_STALE_CHANNEL="1521181579408572536"   # EOD alert channel (stale / lỗi)

_check() {
  local label="$1" table="$2" col="$3" max_lag_days="$4" lag_unit="$5"
  local query result lag_days

  if [ "$lag_unit" = "trading" ]; then
    query="SELECT COUNTIF(v.time > (SELECT MAX(t.${col}) FROM \`${PROJECT}.${table}\` AS t))
                   AS gap_days
           FROM \`${PROJECT}.tav2_bq.ticker\` AS v
           WHERE v.ticker='VNINDEX' AND v.time >= (SELECT MAX(t.${col}) FROM \`${PROJECT}.${table}\` AS t)"
  else
    query="SELECT DATE_DIFF(CURRENT_DATE('Asia/Ho_Chi_Minh'),
                            MAX(t.${col}), DAY) AS gap_days
           FROM \`${PROJECT}.${table}\` AS t"
  fi

  result=$(bq query --use_legacy_sql=false --project_id="$PROJECT" \
    --format=csv --quiet "$query" 2>/dev/null | tail -1)
  lag_days="${result:-999}"
  lag_days=$(printf "%.0f" "$lag_days" 2>/dev/null || echo 999)

  if [ "$lag_days" -le "$max_lag_days" ] 2>/dev/null; then
    [ -z "$QUIET" ] && echo "OK   $label: lag=${lag_days}${lag_unit}d (≤${max_lag_days})"
    return 0
  else
    local alert_msg="⚠️ BQ STALE ($TODAY $NOW_ICT): $label lag=${lag_days}${lag_unit}d (>${max_lag_days}). Pipeline EOD có thể bị skip / step G-H fail. Kiểm tra pipeline log."
    echo "FAIL $label: lag=${lag_days}${lag_unit}d (>${max_lag_days}) — bảng STALE"
    "$ROOT/bin/notify.sh" "$alert_msg" 2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "$alert_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    FAILED=1
    return 1
  fi
}

_run_pipeline() {
  local label="$1" script="$2"
  echo; echo "--- $label ---"
  if $PY "$script"; then
    echo "  [ok] $label"
  else
    echo "  [WARN exit $?] $label — tiếp tục pipeline"
  fi
}

echo "=== BQ Freshness Check — $TODAY $NOW_ICT ==="

_check "ticker_prune (EOD price)"         "tav2_bq.ticker_prune"              "time"  $MAX_PRICE_LAG  "trading"  || true
_check "vnindex_5state_dt5g_live (DT5G)"  "tav2_bq.vnindex_5state_dt5g_live"  "time"  $MAX_STATE_LAG  "trading"  || true
_check "ticker_financial (fundamentals)"  "tav2_bq.ticker_financial"           "time"  $MAX_FIN_LAG    "calendar" || true

if [ "$FAILED" -ne 0 ]; then
  STALE_SUMMARY="⛔ BQ STALE $TODAY $NOW_ICT — DollarBill bị BLOCK, không lập plan hôm nay. Kiểm tra: mike/logs/bq_freshness.log"
  "$ROOT/bin/notify_thread.sh" "$STALE_SUMMARY" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  echo "=== FAILED — alert đã gửi Telegram + Discord ==="
  exit 1
fi

echo "=== ALL FRESH — chạy EOD pipeline ==="
cd "$WORKDIR"

_run_pipeline "[pipeline-1] publish_gated_state"      deploy_golive_dt5g_v4/publish_gated_state.py
_run_pipeline "[pipeline-2] golive_recommend_v23"     deploy_golive_dt5g_v4/golive_recommend_v23.py
_run_pipeline "[pipeline-3] push_recommend_v23_to_bq" mike/agents/Mafee/push_recommend_v23_to_bq.py

echo; echo "--- [pipeline-4] dispatch DollarBill lập plan T+1 ---"
"$ROOT/bin/dispatch.sh" DollarBill \
  "Lập plan T+1 cho tài khoản SpaceX. Đọc DT5G từ deploy_golive_dt5g_v4/golive_state_today.json và recommend output mới nhất trong data/. Ghi plan vào data/plan_SpaceX_<ngày_mai>.json. Ngày hôm nay: $TODAY (ICT)." \
  --bg 2>/dev/null || echo "  [WARN] dispatch DollarBill fail — check mike/logs/"

echo; echo "=== EOD PIPELINE DONE — $(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT') ==="
