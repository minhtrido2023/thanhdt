#!/usr/bin/env bash
# paper_late_feeds.sh — các bước ĐỌC NGUỒN LIVE của chuỗi paper, tách khỏi papertrade_daily.sh
# (15:30) để chạy SAU khi nguồn thật sự tươi. 20:05 ICT, T2-T6.
#
# LÝ DO TÁCH (job Winston_20260729_103816, đo thật 2026-07-29):
#   - papertrade_daily.sh 15:30 chạy TRƯỚC khi upstream tav2 ingest xong (đo: ticker
#     lastModified 17:23, ticker_prune 17:17 ICT) và TRƯỚC publish DT5G 19:00-19:03.
#     → 2 bước dưới đây, vốn đọc BigQuery LIVE (không qua BQ_LOCAL_CACHE), luôn thấy T-1
#       dù bản thân nguồn đã có T từ chiều.
#   - Đa số step còn lại của chain đọc LOCAL DUCKDB CACHE (data/bq_cache/*.parquet, chỉ sync
#     23:45) → dời giờ trong ngày KHÔNG giúp gì, nên giữ nguyên ở 15:30. Xem
#     kb/cron_registry/papertrade_daily_steps.md (bảng phân loại A/B/C).
#
# [19] crisis_alert_push  — DT5G x 8L capitulation push (Telegram). Tự query BQ live
#      (ticker_prune JOIN vnindex_5state_dt5g_live), KHÔNG đọc artifact của step nào khác
#      → không có ràng buộc thứ tự với chain 15:30. asof = min(max ticker_prune, max dt5g_live);
#      chạy 20:05 → asof = T (trước đây T-1). Im lặng khi DORMANT.
# [21] fetch_bdi_daily    — scrape handybulk.com. Baltic công bố ~13:00 London (~19:00-20:00 ICT)
#      nên bản 15:30 luôn lấy được D-1. CHÚ Ý: bản 15:30 VẪN GIỮ trong papertrade_daily.sh —
#      script chỉ lấy ngày MỚI NHẤT trên trang, nên nếu chỉ chạy 1 lần muộn mà hôm đó trang
#      chưa cập nhật thì ngày đó mất vĩnh viễn. 2 lần chạy/ngày + dedup theo date
#      (drop_duplicates keep=last) = idempotent, không bao giờ thủng chuỗi.
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/paper_late_feeds_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "===== paper_late_feeds START $(TZ='Asia/Ho_Chi_Minh' date +'%Y-%m-%d %H:%M ICT') ====="

FAILS=0; FAILED_STEPS=""
run() {  # giống papertrade_daily.sh: continue-on-error, đếm + alert cuối chain
  echo; echo "--- $1 ---"
  local lbl="$1"; shift
  if $PY "$@"; then echo "  [ok] $*"; else echo "  [FAIL exit $?] $*"; FAILS=$((FAILS+1)); FAILED_STEPS="$FAILED_STEPS $lbl"; fi
}

run "[19] crisis_alert_push" crisis_alert_push.py
run "[21] fetch_bdi_daily"   fetch_bdi_daily.py

if [ "$FAILS" -gt 0 ]; then
  msg="⚠️ paper_late_feeds $(date +%F): $FAILS step FAIL:$FAILED_STEPS — chi tiết: grep '\[FAIL' $WORKDIR_8L/$LOG"
  "${NOTIFY_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh}" "$msg" 2>/dev/null || true
  "${NOTIFY_THREAD_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh}" "$msg" "trading_daily" 2>/dev/null || true
fi

find data -name 'paper_late_feeds_*.log' -mtime +30 -delete 2>/dev/null
echo; echo "===== paper_late_feeds DONE $(TZ='Asia/Ho_Chi_Minh' date +'%Y-%m-%d %H:%M ICT') — FAILS=$FAILS ====="
