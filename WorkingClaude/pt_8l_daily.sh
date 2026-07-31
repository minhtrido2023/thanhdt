#!/usr/bin/env bash
# pt_8l_daily.sh — Linux port of pt_8l_daily.bat
# 8L EOD: rating -> screener -> rank -> dna cards -> vn30 basket -> surprise alert
# -> cheap-PB-floor alert -> snapshot -> sector-lens monitor. Continue-on-error per step.
# Schedule ~17:45 ICT (before the 18:00 report so rating_8l.csv is fresh for its R column).
#
# Step [9] sector_lens_monitor (added 2026-07-06, job Taylor_20260706_082923; user approved DAILY
# cadence — transitions matter, the script is light so reading daily is cheap): evaluates the
# Group-A sector watchlist (16 names) -> 6 states, alerts state TRANSITIONS + a 8L-rating cross-
# check (rating<=2 golden/strong AND sector-lens BUY = ✓✓ DOUBLE-CONFIRM, two independent systems)
# to the SAME 8L Telegram channel (cfg chat_id via telegram_recommend). It runs AFTER step [1]
# rating_8l so the cross-check reads today's fresh rating_8l.csv. Research/monitor only — touches
# NO production trading (custom30V/BAL/LAG unchanged).
set -uo pipefail
source /home/trido/thanhdt/WorkingClaude/wc_env.sh
export STATE_WORKDIR="$WORKDIR_8L"
PY="$DNA_PYEXE"; cd "$WORKDIR_8L"
LOG="data/pt_8l_daily_$(date +%Y-%m-%d).log"
exec >>"$LOG" 2>&1
echo "===== pt_8l_daily (linux) START $(date) acct=$(gcloud config get-value account 2>/dev/null) ====="

# FAIL vẫn continue-on-error (một step hỏng không được giết cả chain — by design),
# NHƯNG phải đếm + alert cuối chain: trước 2026-07-11 [FAIL] chỉ nằm trong log, không ai
# biết (audit Winston_20260711_031745 #4 — orb_pt chết 4/8 phiên không ai hay).
FAILS=0; FAILED_STEPS=""
run() { echo; echo "--- $1 ---"; local lbl="$1"; shift; if $PY "$@"; then echo "  [ok] $*"; else echo "  [FAIL exit $?] $*"; FAILS=$((FAILS+1)); FAILED_STEPS="$FAILED_STEPS $lbl"; fi; }

# Gọi cuối chain: >0 step FAIL → alert Telegram + Discord Trading Daily (không chặn gì cả,
# chỉ đảm bảo KHÔNG còn fail im lặng). notify lỗi cũng không được làm chain exit≠0.
notify_fails() {
  local chain="$1"
  [ "$FAILS" -eq 0 ] && return 0
  local msg="⚠️ $chain $(date +%F): $FAILS step FAIL:$FAILED_STEPS — chi tiết: grep '\[FAIL' $WORKDIR_8L/$LOG"
  # NOTIFY_BIN/NOTIFY_THREAD_BIN override được qua env — CHỈ dùng cho selfcheck (test hàm
  # thật với stub, không gửi alert thật); production để trống = đường dẫn thật.
  "${NOTIFY_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh}" "$msg" 2>/dev/null || true
  "${NOTIFY_THREAD_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh}" "$msg" "1521470705563340910" 2>/dev/null || true
}

# --- Độ tươi DT5G (audit §14, job Winston_20260731_062642) ------------------------------
# Chain chạy 19:20 còn daily_refresh 18:30 worst-case ~90' ⇒ có thể chạy khi publisher CỦA TA
# chưa xong. rating_8l đọc state cho deposit-tilt (NEUTRAL) và các step alert 8L gửi Telegram
# dựa trên bảng xếp hạng đó — không được âm thầm coi regime hôm qua là regime hôm nay.
# Bằng chứng = golive_state_today.json qua dt5g_freshness.py (CÙNG artifact + CÙNG luật với
# gate bq_freshness_check 19:00). CHỈ CẢNH BÁO, KHÔNG chặn chain (báo trễ > không báo).
DT5G_WARN="$(timeout 60 $PY dt5g_freshness.py --warn-line 2>/dev/null || true)"
if [ -n "$DT5G_WARN" ]; then
  echo; echo "--- [0-fresh] DT5G STALE --- $DT5G_WARN"
  _m="⚠️ pt_8l_daily $(date +%F): $DT5G_WARN Bảng xếp hạng + alert 8L tối nay chạy trên regime CHƯA xác nhận."
  "${NOTIFY_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify.sh}" "$_m" 2>/dev/null || true
  "${NOTIFY_THREAD_BIN:-/home/trido/thanhdt/WorkingClaude/mike/bin/notify_thread.sh}" "$_m" "1521470705563340910" 2>/dev/null || true
else
  echo; echo "--- [0-fresh] DT5G tươi (publisher của ta đã xác nhận hôm nay) ---"
fi

run "[1] rating_8l"            rating_8l.py
run "[2] unified_screener"     unified_screener.py
run "[3] rank_8l"              rank_8l.py
run "[4] dna_card"             dna_card.py
run "[5] vn30_8l"              vn30_8l.py
run "[6] rank_8l_daily_alert"  rank_8l_daily_alert.py
run "[7] cheap_pb_floor"       cheap_pb_floor.py
echo; echo "--- [8] snapshot rank_8l (bot 'new') ---"
if $PY -c "import bot_8l_commands as b; print(b.snapshot_today())"; then
  echo "  [ok] snapshot"
else
  echo "  [FAIL] snapshot"; FAILS=$((FAILS+1)); FAILED_STEPS="$FAILED_STEPS [8]"
fi
run "[9] sector_lens_monitor"  sector_lens_monitor.py --telegram

notify_fails "pt_8l_daily"

find data -name 'pt_8l_daily_*.log' -mtime +30 -delete 2>/dev/null
echo; echo "===== pt_8l_daily (linux) DONE $(date) — FAILS=$FAILS ====="
