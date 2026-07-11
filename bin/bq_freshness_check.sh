#!/usr/bin/env bash
# bq_freshness_check.sh — kiểm tra freshness các bảng BQ → nếu fresh chạy pipeline EOD
#
# Luồng 19:00 ICT (cron: 0 12 * * 1-5 — dời từ 17:30, 2026-07-10: daily_refresh_v34b_linux.sh
# (tính DT5G của hôm nay) chạy 18:30, cần chạy SAU nó chứ không phải trước — trước đây chạy
# ở 17:30 nghĩa là luôn đọc DT5G của HÔM QUA, mỗi ngày, vì bản hôm nay chưa kịp tính):
#   → STALE: cảnh báo Telegram + Discord stale-alert channel, dừng, block DollarBill
#   → FRESH: publish_gated_state → golive_recommend → push_to_bq → dispatch DollarBill lập plan
#
# Tables checked (BLOCK = stale ⇒ chặn pipeline + DollarBill; WARN = alert Discord, không chặn):
#   tav2_bq.ticker_prune              BLOCK — daily EOD price (pipeline step H)
#   tav2_bq.vnindex_5state_dt5g_live  BLOCK — DT5G regime (pipeline step G)
#   tav2_bq.ticker_financial          BLOCK — quarterly fundamentals (pipeline step H financial)
#   tav2_bq.ticker_1m                 BLOCK — live screening snapshot (thêm 2026-07-11, audit Winston_20260711_031745 #3)
#   tav2_bq.shares_outstanding_live   BLOCK — corp-action shares (writer corp_action_update_shares_live ~17:44 ICT daily)
#   tav2_bq.custom30v_8l              BLOCK content-age + WARN writer-alive — V2.4 PRODUCTION parking basket
#   tav2_bq.custom30_8l               BLOCK content-age + WARN writer-alive — legacy blend (audit consumers)
#   tav2_bq.risk_rating               WARN  — research-only, KHÔNG consumer production (orphan, stale từ 2025Q4)
#
# Usage: bin/bq_freshness_check.sh [--quiet]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true

QUIET="${1:-}"
PROJECT="lithe-record-440915-m9"
MAX_PRICE_LAG=2      # trading days: cho phép gap weekend/nghỉ lễ
MAX_STATE_LAG=0      # trading days cho DT5G regime — SIẾT 2→1 (2026-07-10) rồi 1→0
                     # (2026-07-11, audit Winston_20260710_173031): gate so sánh bằng -le
                     # nên MAX_STATE_LAG=1 vẫn cho lag=1 PASS — đúng case "state trễ 1 ngày
                     # cần chặn DollarBill" mà lần siết 07-10 nhắm tới lại là NO-OP (xảy ra
                     # thật tối 07-10: daily_refresh 18:30 miss, check 19:00 vẫn ALL FRESH,
                     # DollarBill lập plan trên state 07-09). daily_refresh giờ chạy 18:30
                     # + precheck ingest riêng → ngày bình thường lag=0; lag>=1 (trading-day)
                     # là bất thường → FAIL + block. Giữ -le, chỉ đổi ngưỡng (PRICE=2/FIN=90
                     # đang đúng ngữ nghĩa -le, không đụng).
MAX_FIN_LAG=90       # calendar days: financial data quarterly (Q1 results ~Apr, gap có thể 60-85 ngày)
# --- Ngưỡng cho các bảng mở rộng 2026-07-11 (audit Winston_20260711_031745 #3 — bài học
# "custom30v_8l writer chết âm thầm 3 tuần"; mọi ngưỡng calibrate bằng query BQ thật, không bịa):
MAX_1M_LAG=2         # trading days: ticker_1m cùng ingest upstream với ticker_prune → cùng ngưỡng PRICE=2
MAX_SHARES_LAG=2     # trading days trên DATE(MAX(updated_at)): writer corp_action chạy ~17:44 ICT daily
                     # (verify 07-11: max updated_at = 07-10 17:44 ICT) → lag bình thường = 0; cho phép 2
                     # để 1 outage transient (writer đã có retry 3x) không chặn oan plan; ≥3 = writer chết.
MAX_REBAL_AGE=98     # calendar days trên MAX(rebal_date) của custom30_8l/custom30v_8l: rebal q2m5 spacing
                     # thực tế 92d (05-02→05-05..., max shift lịch sử 1 ngày: 2024-05-06) + 6d grace.
                     # >98 = kỳ rebal kế tiếp KHÔNG materialize ~1 tuần sau hạn → đúng time-bomb 08-05.
MAX_TABLEMOD_AGE=4   # calendar days trên BQ lastModifiedTime (writer-alive; WARN-only): publisher
                     # papertrade 15:30 ICT daily → bình thường <1d; 4 cho phép miss thứ Sáu + cuối tuần
                     # (Fri chết → Mon age 3 PASS, Tue age 4 WARN). WARN không chặn vì content giữa kỳ
                     # rebal vẫn đúng khi writer mới chết vài ngày — content-age (BLOCK) mới là gate cứng.
MAX_RR_QAGE=135      # calendar days từ NGÀY CUỐI QUÝ của MAX(quarter) trong risk_rating: 1 quý (92d)
                     # + 43d grace tính toán. GIẢ ĐỊNH (không chắc cadence gốc — chọn chặt theo dispatch):
                     # quý mới phải có rating trong ~1.5 tháng sau khi quý trước kết thúc. WARN-only:
                     # bảng orphan (verify 07-11: MAX(quarter)=2025Q4 — ĐÃ stale ~2 quý; consumer duy nhất
                     # = sync_bq_cache/preflight cache list, KHÔNG có consumer production trong chuỗi
                     # chọn-mã) → block sẽ chặn oan DollarBill vì 1 bảng research chết.
TODAY="$(date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"
FAILED=0
WARNED=0

WORKDIR="${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}"
PY="${DNA_PYEXE:-python3}"

# T+1 ngày giao dịch THẬT (bỏ T7/CN + lễ) — tính SẴN bằng code, KHÔNG để DollarBill (LLM)
# tự suy ra "ngày mai" (sự cố thật 2026-07-10: dispatch thứ Sáu 07-10 tự tính "ngày mai" =
# 07-11 thứ Bảy, không phải ngày giao dịch, thay vì đúng T+1 = 07-13 thứ Hai, cả 2 lần
# dispatch trong ngày đều sai — xem kb/INCIDENTS.md 2026-07-10 "DollarBill sinh sai ngày T+1").
NEXT_TRADING_DAY="$(cd "$WORKDIR" && python3 -c "
from trading_bot.vn_market import next_trading_day
import datetime as dt
print(next_trading_day(dt.date.today()))
" 2>/dev/null)"
if [ -z "$NEXT_TRADING_DAY" ]; then
  echo "FATAL: không tính được NEXT_TRADING_DAY (next_trading_day() lỗi) — dừng, không dispatch DollarBill với ngày rỗng" >&2
  exit 1
fi

# Discord: Trading Daily thread — mọi nội dung giao dịch hàng ngày gộp về 1 topic.
DISCORD_STALE_CHANNEL="1521470705563340910"

# _check <label> <table> <colexpr> <max_lag> <trading|calendar> [BLOCK|WARN]
#   colexpr = biểu thức SQL đầy đủ với alias `t.` (vd "t.time", "DATE(t.updated_at)",
#   hoặc expr đổi quarter-string thành DATE) — cho phép check bảng không có cột DATE thô.
#   BLOCK (default) = stale ⇒ FAILED=1, Telegram + Discord, chặn pipeline/DollarBill.
#   WARN = stale ⇒ WARNED+=1, chỉ Discord Trading Daily (không Telegram, không chặn) —
#   dùng cho bảng research/early-warning mà việc block plan vì nó là phản ứng quá tay.
_check() {
  local label="$1" table="$2" colexpr="$3" max_lag_days="$4" lag_unit="$5" mode="${6:-BLOCK}"
  local query result lag_days

  if [ "$lag_unit" = "trading" ]; then
    query="SELECT COUNTIF(v.time > (SELECT MAX(${colexpr}) FROM \`${PROJECT}.${table}\` AS t))
                   AS gap_days
           FROM \`${PROJECT}.tav2_bq.ticker\` AS v
           WHERE v.ticker='VNINDEX' AND v.time >= (SELECT MAX(${colexpr}) FROM \`${PROJECT}.${table}\` AS t)"
  else
    query="SELECT DATE_DIFF(CURRENT_DATE('Asia/Ho_Chi_Minh'),
                            MAX(${colexpr}), DAY) AS gap_days
           FROM \`${PROJECT}.${table}\` AS t"
  fi

  result=$(bq query --use_legacy_sql=false --project_id="$PROJECT" \
    --format=csv --quiet "$query" 2>/dev/null | tail -1)
  lag_days="${result:-999}"
  lag_days=$(printf "%.0f" "$lag_days" 2>/dev/null || echo 999)

  if [ "$lag_days" -le "$max_lag_days" ] 2>/dev/null; then
    [ -z "$QUIET" ] && echo "OK   $label: lag=${lag_days}${lag_unit}d (≤${max_lag_days})"
    return 0
  elif [ "$mode" = "WARN" ]; then
    local warn_msg="🟡 BQ WARN ($TODAY $NOW_ICT): $label lag=${lag_days}${lag_unit}d (>${max_lag_days}) — không chặn pipeline, nhưng bảng này đang stale. Kiểm tra writer."
    echo "WARN $label: lag=${lag_days}${lag_unit}d (>${max_lag_days}) — stale, non-blocking"
    "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
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

# _check_lastmod <label> <dataset.table> <max_age_calendar_days>
#   Writer-alive check qua BQ lastModifiedTime (metadata, không tốn query slot). WARN-only:
#   bắt "publisher chết âm thầm" trong vài ngày thay vì đợi content-age nổ ở kỳ rebal kế
#   (bài học custom30v_8l chết 06-18, mtime cache local luôn tươi vì sync re-download đêm).
_check_lastmod() {
  local label="$1" table="$2" max_age_days="$3"
  local ms age_days
  ms=$(bq show --format=prettyjson "${PROJECT}:${table}" 2>/dev/null \
       | python3 -c "import json,sys; print(json.load(sys.stdin).get('lastModifiedTime',0))" 2>/dev/null)
  ms="${ms:-0}"
  if [ "$ms" -gt 0 ] 2>/dev/null; then
    age_days=$(( ( $(date +%s) - ms / 1000 ) / 86400 ))
  else
    age_days=999   # metadata không đọc được = coi như đáng ngờ (fail-safe), báo WARN
  fi

  if [ "$age_days" -le "$max_age_days" ]; then
    [ -z "$QUIET" ] && echo "OK   $label: last-modified ${age_days}d trước (≤${max_age_days})"
    return 0
  else
    local warn_msg="🟡 BQ WRITER-DEAD? ($TODAY $NOW_ICT): $label chưa được ghi ${age_days}d (>${max_age_days}). Publisher (papertrade_daily [6]/[6b]) có thể đã chết — content còn đúng tới kỳ rebal kế tiếp, sửa TRƯỚC khi thành data sai."
    echo "WARN $label: last-modified ${age_days}d (>${max_age_days}) — writer nghi chết, non-blocking"
    "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
    return 0
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

_check "ticker_prune (EOD price)"         "tav2_bq.ticker_prune"              "t.time"  $MAX_PRICE_LAG  "trading"  || true
_check "vnindex_5state_dt5g_live (DT5G)"  "tav2_bq.vnindex_5state_dt5g_live"  "t.time"  $MAX_STATE_LAG  "trading"  || true
_check "ticker_financial (fundamentals)"  "tav2_bq.ticker_financial"          "t.time"  $MAX_FIN_LAG    "calendar" || true
# --- mở rộng 2026-07-11 (audit Winston_20260711_031745 #3) ---
_check "ticker_1m (live screening)"       "tav2_bq.ticker_1m"                 "t.time"  $MAX_1M_LAG     "trading"  || true
_check "shares_outstanding_live (corp-action)" "tav2_bq.shares_outstanding_live" "DATE(t.updated_at)" $MAX_SHARES_LAG "trading" || true
_check "custom30v_8l content (V2.4 PARK rebal-age)" "tav2_bq.custom30v_8l"    "t.rebal_date" $MAX_REBAL_AGE "calendar" || true
_check "custom30_8l content (blend rebal-age)"      "tav2_bq.custom30_8l"     "t.rebal_date" $MAX_REBAL_AGE "calendar" || true
# risk_rating không có cột DATE — đổi MAX(quarter) '2025Q4' thành ngày cuối quý rồi đo tuổi.
_check "risk_rating (research, orphan)"   "tav2_bq.risk_rating" \
  "LAST_DAY(DATE(CAST(SUBSTR(t.quarter,1,4) AS INT64), CAST(SUBSTR(t.quarter,6,1) AS INT64)*3, 1))" \
  $MAX_RR_QAGE "calendar" WARN || true
_check_lastmod "custom30v_8l writer-alive"  "tav2_bq.custom30v_8l"  $MAX_TABLEMOD_AGE || true
_check_lastmod "custom30_8l writer-alive"   "tav2_bq.custom30_8l"   $MAX_TABLEMOD_AGE || true

[ "$WARNED" -gt 0 ] && echo "NOTE: $WARNED WARN non-blocking (đã post Discord Trading Daily) — pipeline vẫn chạy"

if [ "$FAILED" -ne 0 ]; then
  STALE_SUMMARY="⛔ BQ STALE $TODAY $NOW_ICT — DollarBill bị BLOCK, không lập plan hôm nay. Kiểm tra: mike/logs/bq_freshness.log"
  "$ROOT/bin/notify_thread.sh" "$STALE_SUMMARY" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  echo "=== FAILED — alert đã gửi Telegram + Discord ==="
  exit 1
fi

echo "=== ALL FRESH — chạy EOD pipeline ==="
cd "$WORKDIR"

# Mốc thời gian gate xác nhận fresh — mọi artifact DollarBill sẽ đọc phải được ghi SAU mốc này
# (audit Taylor_20260711_031821 F5: _run_pipeline fail chỉ WARN rồi vẫn tiếp tục ⇒ nếu
# publish_gated_state/golive_recommend chết, DollarBill vẫn được dispatch và đọc file CŨ —
# writer/reader split y hệt class bug DT5G path 06-21. Assertion mtime = die-trước-dispatch,
# cùng pattern post-chain assertion của daily_refresh_v34b_linux.sh, Winston_20260711_023903.)
PIPELINE_START_EPOCH="$(date +%s)"

_run_pipeline "[pipeline-1] publish_gated_state"      deploy_golive_dt5g_v4/publish_gated_state.py
_run_pipeline "[pipeline-2] golive_recommend_v23"     deploy_golive_dt5g_v4/golive_recommend_v23.py
_run_pipeline "[pipeline-3] push_recommend_v23_to_bq" mike/agents/Mafee/push_recommend_v23_to_bq.py

# _assert_fresh_artifact <label> <path> — file phải tồn tại và mtime >= PIPELINE_START_EPOCH,
# nếu không: alert + exit 1 (KHÔNG dispatch DollarBill với artifact stale).
_assert_fresh_artifact() {
  local label="$1" path="$2" mtime
  mtime="$(stat -c %Y "$path" 2>/dev/null || echo 0)"
  if [ "$mtime" -lt "$PIPELINE_START_EPOCH" ]; then
    local msg="⛔ ARTIFACT STALE $TODAY — $label ($path) mtime $(date -d @"$mtime" +'%F %T' 2>/dev/null || echo 'MISSING') < gate start $(date -d @"$PIPELINE_START_EPOCH" +'%F %T'). Pipeline step ghi file này đã FAIL — DollarBill bị BLOCK, không lập plan với dữ liệu cũ. Check mike/logs/bq_freshness.log"
    "$ROOT/bin/notify_thread.sh" "$msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    echo "=== FAILED (artifact stale: $label) — alert đã gửi, DollarBill KHÔNG được dispatch ==="
    exit 1
  fi
  echo "  [fresh-ok] $label (mtime >= gate start)"
}
_assert_fresh_artifact "golive_state_today.json (DT5G state DollarBill đọc)" \
  "$WORKDIR/deploy_golive_dt5g_v4/golive_state_today.json"
_assert_fresh_artifact "golive_v23_recommendations (recommend output DollarBill đọc)" \
  "$(ls -1t "$WORKDIR"/deploy_golive_dt5g_v4/out/golive_v23_recommendations_*.csv 2>/dev/null | head -1)"

# [pipeline-4] dispatch DollarBill lập plan T+1 — lặp qua MỌI account live (enabled=true,
# mode=live, broker=dnse trong secrets/trading_bot_accounts.json), không hardcode SpaceX —
# thêm account mới vào file đó là tự động có plan T+1, không cần sửa gì ở đây. Xem
# kb/account_onboarding_runbook.md.
LIVE_LABELS="$(cd "$WORKDIR" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))")"
for ACCT in $LIVE_LABELS; do
  echo; echo "--- [pipeline-4] dispatch DollarBill lập plan T+1 cho $ACCT ---"
  HAS_EXCL="$(cd "$WORKDIR" && python3 -c "
from trading_bot.config import load_config, load_accounts
p = next(a for a in load_accounts(load_config()) if a['label'] == '$ACCT')
print('yes' if p.get('excluded_tickers') else 'no')
" 2>/dev/null)"
  NAV_NOTE=""
  if [ "$HAS_EXCL" = "yes" ]; then
    NAV_NOTE=" Tài khoản này có excluded_tickers (vị thế legacy ngoài rebalancing) — dùng \`bin/compute_active_nav.py --account $ACCT\` để lấy NAV khả dụng làm cơ sở sizing, KHÔNG dùng tổng NAV account."
  fi
  "$ROOT/bin/dispatch.sh" DollarBill \
    "Lập plan T+1 cho tài khoản $ACCT. Đọc DT5G từ deploy_golive_dt5g_v4/golive_state_today.json và recommend output mới nhất trong data/. Ghi plan vào data/plan_${ACCT}_${NEXT_TRADING_DAY}.json — dùng ĐÚNG NGUYÊN VĂN ngày $NEXT_TRADING_DAY (đã tính sẵn bằng next_trading_day(), bỏ T7/CN/lễ) làm plan_date và tên file, TUYỆT ĐỐI KHÔNG tự suy ra 'ngày mai' bằng cách cộng 1 vào ngày hôm nay (sự cố thật 2026-07-10: dispatch thứ Sáu tự tính '07-11' là ngày mai, nhưng đó là thứ Bảy không phải ngày giao dịch, đúng ra phải là 07-13 thứ Hai). Ngày hôm nay: $TODAY (ICT).${NAV_NOTE} YÊU CẦU VĂN PHONG (user 2026-07-07): kết thúc final message bằng 3-5 dòng tóm tắt DỄ HIỂU cho người đọc không chuyên — bắt buộc nêu rõ: Account nào · plan ngày nào · hành động chính (HOLD hay mấy lệnh gì) · VÌ SAO 1-2 câu · trạng thái duyệt — vì message này được đăng nguyên văn vào Discord plan channel. Lệnh MUA size bằng tiền bán cùng ngày: trừ phí 0.075% + chừa biên giá, đừng size khít ref price. BẮT BUỘC VỀ GIÁ THAM CHIẾU (user 2026-07-09, tái diễn nhiều lần): mtm_price_ref/ref_price của MỌI mã trong plan phải lấy từ DNSE live quote (dnse_api.py secdef/latest_trade — giá đóng cửa THẬT hôm nay $TODAY) — TUYỆT ĐỐI KHÔNG dùng giá đóng cửa BQ ('ticker'/'ticker_1m' close) làm ref_price, vì BQ cache local chỉ sync đêm 23:45 ICT nên tại giờ bạn chạy (~19:00) BQ cache luôn trễ ít nhất 1 ngày giao dịch — dùng BQ ở đây LUÔN cho ra giá sai/cũ, không phải thỉnh thoảng. Sự cố thật đã xảy ra: plan ZaloPay 07-10 có 2/4 mã (BID, MBB) dùng nhầm 'BQ close 07-08' lệch tới +5.7% so với giá đóng cửa thật 07-09, trong khi 2 mã còn lại dùng đúng DNSE live. Nếu DNSE live quote lỗi/thiếu cho 1 mã nào đó, ghi rõ note 'THIẾU GIÁ LIVE — cần kiểm tra tay' thay vì âm thầm dùng BQ thay thế." \
    --bg 2>/dev/null || echo "  [WARN] dispatch DollarBill cho $ACCT fail — check mike/logs/"
done

echo; echo "=== EOD PIPELINE DONE — $(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT') ==="
