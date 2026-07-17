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
#   tav2_bq.shares_outstanding_live   WARN  — corp-action shares (sửa 2026-07-12, audit Winston_20260712_142100
#                                             H2: cron update_shares_live.sh 18:40 chỉ chạy --scan detection-only,
#                                             KHÔNG BAO GIỜ merge updated_at daily; mốc "~17:44 ICT daily" cũ là
#                                             SAI — đó chỉ là 1 lần xử lý corp-action thủ công tình cờ. Cadence thật
#                                             là event-driven, không phải daily, nên BLOCK trên lag≤2 sẽ false-block
#                                             oan bất cứ khi nào không có corp-action nào cần xử lý tay trong 2 phiên)
#   tav2_bq.custom30v_8l              BLOCK content-age + WARN writer-alive — V2.4 PRODUCTION parking basket
#   tav2_bq.custom30_8l               BLOCK content-age + WARN writer-alive — legacy blend (audit consumers)
#   tav2_bq.risk_rating               WARN  — research-only, KHÔNG consumer production (orphan, stale từ 2025Q4)
#   ticker_financial breadth-probe    WARN  — đếm cohort quý mới trong mùa BCTC (MAX(time) toàn bảng
#                                             bị 1 mã early-filer reset đồng hồ — audit Winston_20260712_122313 F1)
#   earnings_surprise_data.pkl probe  WARN  — content catch-up pkl vs ticker_financial: nguồn LAG live
#                                             candidacy, golive except-path nuốt lỗi im lặng
#                                             (audit Spyros_20260712_131501 M1)
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
MAX_SHARES_LAG=2     # trading days trên DATE(MAX(updated_at)) — WARN-only từ 2026-07-12 (H2, xem dòng 15).
                     # Ngưỡng giữ nguyên =2 (chỉ đổi mode, không đổi số) vì vẫn có ý nghĩa cảnh báo dù
                     # cadence thật event-driven: lag>2 phiên liên tục vẫn đáng ngờ nếu có corp-action
                     # đang chờ xử lý tay, chỉ là không còn đủ căn cứ để BLOCK cả pipeline vì nó.
MAX_REBAL_AGE=98     # calendar days trên MAX(rebal_date) của custom30_8l/custom30v_8l: rebal q2m5 spacing
                     # thực tế 92d (05-02→05-05..., max shift lịch sử 1 ngày: 2024-05-06) + 6d grace.
                     # >98 = kỳ rebal kế tiếp KHÔNG materialize ~1 tuần sau hạn → đúng time-bomb 08-05.
MAX_TABLEMOD_AGE=4   # calendar days trên BQ lastModifiedTime (writer-alive; WARN-only): publisher
                     # papertrade 15:30 ICT daily → bình thường <1d; 4 cho phép miss thứ Sáu + cuối tuần
                     # (Fri chết → Mon age 3 PASS, Tue age 4 WARN). WARN không chặn vì content giữa kỳ
                     # rebal vẫn đúng khi writer mới chết vài ngày — content-age (BLOCK) mới là gate cứng.
MAX_R8L_MOD_AGE=9    # calendar days trên fa_ratings_8l lastModifiedTime (writer-alive; WARN-only):
                     # cron weekly 08:30 ICT thứ Bảy (Winston 2026-07-11) → bình thường <7d; 9 cho phép
                     # 1 lần miss ngắn không chặn oan (dự án re-tune SIGNAL_V11 phụ thuộc bảng này tươi).
MAX_FA_MOD_AGE=9     # calendar days trên fa_ratings lastModifiedTime (writer-alive; WARN-only):
                     # append-only refresh cron weekly 09:15 ICT thứ Bảy (Taylor đề xuất 2026-07-11,
                     # chờ user duyệt). Bảng static từ 05-10 → WARN mỗi ngày cho tới lần cron chạy
                     # thành công đầu tiên — đó là tín hiệu ĐÚNG (SIGNAL_V11 fa_tier đang đọc tier
                     # đóng băng), không phải false alarm. WARN không chặn plan.
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
# --- ticker_prune DEPTH check (2026-07-15, sự cố upstream ghi đè bảng): MAX(time) vẫn
# advance khi bảng bị moi ruột (7-10 mã/ngày từ 07-08 thay vì ~225-265) → lag-check một
# mình mù hoàn toàn, suýt cho DollarBill lập plan trên universe 7 mã. Đếm số mã của
# NGÀY MỚI NHẤT: < MIN_PRUNE_NAMES ⇒ FAIL như stale (block pipeline/DollarBill).
MIN_PRUNE_NAMES=200   # daily_refresh_v34b precheck dùng cùng ngưỡng (bình thường ~225-265)
prune_names=$(bq query --use_legacy_sql=false --project_id="$PROJECT" --format=csv --quiet \
  "SELECT COUNT(DISTINCT t.ticker) FROM \`${PROJECT}.tav2_bq.ticker_prune\` AS t
   WHERE t.time = (SELECT MAX(x.time) FROM \`${PROJECT}.tav2_bq.ticker_prune\` AS x)" \
  2>/dev/null | tail -1 | tr -d '[:space:]')
prune_names="${prune_names:-0}"
if [ "$prune_names" -ge "$MIN_PRUNE_NAMES" ] 2>/dev/null; then
  [ -z "$QUIET" ] && echo "OK   ticker_prune depth: ${prune_names} mã ngày mới nhất (≥${MIN_PRUNE_NAMES})"
else
  depth_msg="⚠️ BQ DEPTH ($TODAY $NOW_ICT): ticker_prune ngày mới nhất chỉ có ${prune_names} mã (<${MIN_PRUNE_NAMES}, bình thường ~225-265) — bảng bị ghi thiếu/moi ruột dù MAX(time) vẫn advance. Chặn pipeline/DollarBill."
  echo "FAIL ticker_prune depth: ${prune_names} mã (<${MIN_PRUNE_NAMES}) — bảng bị ghi thiếu"
  "$ROOT/bin/notify.sh" "$depth_msg" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$depth_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  FAILED=1
fi
_check "vnindex_5state_dt5g_live (DT5G)"  "tav2_bq.vnindex_5state_dt5g_live"  "t.time"  $MAX_STATE_LAG  "trading"  || true
_check "ticker_financial (fundamentals)"  "tav2_bq.ticker_financial"          "t.time"  $MAX_FIN_LAG    "calendar" || true
# --- mở rộng 2026-07-11 (audit Winston_20260711_031745 #3) ---
_check "ticker_1m (live screening)"       "tav2_bq.ticker_1m"                 "t.time"  $MAX_1M_LAG     "trading"  || true
_check "shares_outstanding_live (corp-action)" "tav2_bq.shares_outstanding_live" "DATE(t.updated_at)" $MAX_SHARES_LAG "trading" "WARN" || true
_check "custom30v_8l content (V2.4 PARK rebal-age)" "tav2_bq.custom30v_8l"    "t.rebal_date" $MAX_REBAL_AGE "calendar" || true
_check "custom30_8l content (blend rebal-age)"      "tav2_bq.custom30_8l"     "t.rebal_date" $MAX_REBAL_AGE "calendar" || true
# risk_rating không có cột DATE — đổi MAX(quarter) '2025Q4' thành ngày cuối quý rồi đo tuổi.
_check "risk_rating (research, orphan)"   "tav2_bq.risk_rating" \
  "LAST_DAY(DATE(CAST(SUBSTR(t.quarter,1,4) AS INT64), CAST(SUBSTR(t.quarter,6,1) AS INT64)*3, 1))" \
  $MAX_RR_QAGE "calendar" WARN || true
_check_lastmod "custom30v_8l writer-alive"  "tav2_bq.custom30v_8l"  $MAX_TABLEMOD_AGE || true
_check_lastmod "custom30_8l writer-alive"   "tav2_bq.custom30_8l"   $MAX_TABLEMOD_AGE || true
_check_lastmod "fa_ratings_8l writer-alive" "tav2_bq.fa_ratings_8l" $MAX_R8L_MOD_AGE || true
_check_lastmod "fa_ratings writer-alive"    "tav2_bq.fa_ratings"    $MAX_FA_MOD_AGE  || true

# lag_edge_health.csv local-file mtime probe (Winston_20260712_121456)
# WARN-only: silent-skip path trong edge_health_monitor.py — exception trong lag_edge_health()
# khiến file đóng băng IM LẶNG trong khi step [22] vẫn báo [ok], bq_freshness_check là gate
# cuối bắt được. Cùng ngưỡng MAX_TABLEMOD_AGE=4 (Fri chết→Mon age 3 PASS, Tue age 4 WARN).
LAG_EDGE_FILE="$WORKDIR/data/lag_edge_health.csv"
if [ -f "$LAG_EDGE_FILE" ]; then
  lag_edge_age=$(( ( $(date +%s) - $(stat -c %Y "$LAG_EDGE_FILE") ) / 86400 ))
  if [ "$lag_edge_age" -gt "$MAX_TABLEMOD_AGE" ]; then
    warn_msg="🟡 LOCAL FILE WARN ($TODAY $NOW_ICT): lag_edge_health.csv age=${lag_edge_age}d (>${MAX_TABLEMOD_AGE}) — edge_health_monitor.py có thể đang silent-skip (exception trong lag_edge_health()). Kiểm tra papertrade_daily.sh step [22] log."
    echo "WARN lag_edge_health.csv: age=${lag_edge_age}d (>${MAX_TABLEMOD_AGE}) — stale, non-blocking"
    "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
  else
    [ -z "$QUIET" ] && echo "OK   lag_edge_health.csv: age=${lag_edge_age}d (≤${MAX_TABLEMOD_AGE})"
  fi
else
  warn_msg="🟡 LOCAL FILE WARN ($TODAY $NOW_ICT): lag_edge_health.csv KHÔNG TỒN TẠI — edge_health_monitor chưa từng chạy hoặc đường dẫn sai."
  echo "WARN lag_edge_health.csv: FILE KHÔNG TỒN TẠI — non-blocking"
  "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  WARNED=$((WARNED + 1))
fi

# ticker_financial breadth-probe (Winston_20260712_124928, audit F1 Winston_20260712_122313) —
# WARN-only, CHỈ đánh giá trong mùa BCTC. Gap được vá: _check ticker_financial ở trên đo
# MAX(t.time) TOÀN BẢNG — 1 mã công bố sớm (MBS 2026-07-08) đã reset đồng hồ cho cả bảng,
# vendor stall giữa mùa sẽ im lặng tới MAX_FIN_LAG=90d (fa_ratings gate chỉ silent-skip,
# LAG refill lặng lẽ không xảy ra). Probe: đếm COUNT(DISTINCT ticker) của quý-vừa-kết-thúc,
# so với lịch sử CSV — WARN nếu số này ĐỨNG YÊN >= FIN_BREADTH_STALL_DAYS calendar days,
# TRỪ khi cohort đã ~đầy (>= FIN_BREADTH_SAT_PCT% quý trước — cuối mùa đứng yên là hành vi
# đúng, không phải stall; tránh false-positive khi thực sự không còn gì mới để báo cáo).
# "Trong mùa BCTC" = [quarter_end+10d, quarter_end+62d] (Q2/2026: 07-10 → 08-31; hạn nộp
# BCTC quý VN = 20-30d sau quý, thực tế Q1/2026 hoàn tất ~05-04 = qend+34d ⇒ 62d phủ trọn
# late-filer + đệm). Ngoài mùa: skip hẳn (không query, không WARN — cohort quý cũ đứng yên
# ở ~full là bình thường). Mỗi lần chạy trong mùa append 1 dòng/ngày vào CSV lịch sử —
# vừa là state cho stall-check, vừa là curve tham chiếu cho mùa BCTC sau.
FIN_BREADTH_CSV="$WORKDIR/data/ticker_financial_breadth.csv"
FIN_BREADTH_STALL_DAYS=5   # ~5-7d theo đề xuất audit; 5 = chặt nhất mà vẫn nuốt trọn 1 weekend
                           # + 1 ngày lễ (cron T2-T6: Fri→Wed = 5 calendar days, không false-fire
                           # chỉ vì cuối tuần không có filing mới)
FIN_BREADTH_SAT_PCT=90     # cohort >= 90% số mã quý trước = mùa đã hoàn tất, đứng yên hợp lệ

read -r EXPECTED_Q IN_SEASON <<< "$(python3 -c "
import datetime as dt, calendar
today = dt.date.today()
q_end_month = ((today.month - 1) // 3) * 3   # 0,3,6,9 — tháng cuối của quý VỪA KẾT THÚC
if q_end_month == 0:
    q_end = dt.date(today.year - 1, 12, 31); q_num, q_year = 4, today.year - 1
else:
    q_end = dt.date(today.year, q_end_month, calendar.monthrange(today.year, q_end_month)[1])
    q_num, q_year = q_end_month // 3, today.year
in_season = 1 if q_end + dt.timedelta(days=10) <= today <= q_end + dt.timedelta(days=62) else 0
print(f'{q_year}Q{q_num} {in_season}')
" 2>/dev/null)"

if [ "${IN_SEASON:-0}" = "1" ]; then
  PREV_Q="$(python3 -c "q='$EXPECTED_Q'; y,n=int(q[:4]),int(q[-1]); print(f'{y-1}Q4' if n==1 else f'{y}Q{n-1}')")"
  breadth_row=$(bq query --use_legacy_sql=false --project_id="$PROJECT" --format=csv --quiet "
    SELECT
      (SELECT COUNT(DISTINCT t.ticker) FROM \`${PROJECT}.tav2_bq.ticker_financial\` AS t WHERE t.quarter='${EXPECTED_Q}') AS n_cur,
      (SELECT COUNT(DISTINCT t.ticker) FROM \`${PROJECT}.tav2_bq.ticker_financial\` AS t WHERE t.quarter='${PREV_Q}') AS n_prev" \
    2>/dev/null | tail -1)
  n_cur="${breadth_row%%,*}"; n_prev="${breadth_row##*,}"
  if [ -n "$n_cur" ] && [ "$n_cur" -ge 0 ] 2>/dev/null && [ "$n_prev" -ge 1 ] 2>/dev/null; then
    [ -f "$FIN_BREADTH_CSV" ] || echo "date,quarter,n_tickers,n_prev_quarter" > "$FIN_BREADTH_CSV"
    # 1 dòng/ngày: chạy lại cùng ngày thì thay dòng cũ (giữ số đo mới nhất)
    grep -v "^$TODAY," "$FIN_BREADTH_CSV" > "$FIN_BREADTH_CSV.tmp" 2>/dev/null && mv "$FIN_BREADTH_CSV.tmp" "$FIN_BREADTH_CSV"
    echo "$TODAY,$EXPECTED_Q,$n_cur,$n_prev" >> "$FIN_BREADTH_CSV"
    # dòng GẦN NHẤT cùng quý có tuổi >= STALL_DAYS (so sánh chuỗi YYYY-MM-DD = so sánh ngày);
    # chưa đủ lịch sử (đầu mùa) → ref_n rỗng → PASS (grace period, đúng thiết kế)
    BREADTH_CUTOFF="$(date -d "-${FIN_BREADTH_STALL_DAYS} days" +%Y-%m-%d)"
    ref_n=$(awk -F, -v q="$EXPECTED_Q" -v cut="$BREADTH_CUTOFF" '$2==q && $1<=cut {n=$3} END {print n}' "$FIN_BREADTH_CSV")
    sat_floor=$(( n_prev * FIN_BREADTH_SAT_PCT / 100 ))
    if [ -n "$ref_n" ] && [ "$n_cur" -le "$ref_n" ] 2>/dev/null && [ "$n_cur" -lt "$sat_floor" ]; then
      warn_msg="🟡 FIN BREADTH WARN ($TODAY $NOW_ICT): ticker_financial ${EXPECTED_Q} đứng yên ở ${n_cur} mã suốt >=${FIN_BREADTH_STALL_DAYS}d giữa mùa BCTC (quý trước ${PREV_Q}=${n_prev} mã). Vendor có thể đã stall — check MAX(time) ở trên KHÔNG bắt được case này (1 mã early-filer đã reset đồng hồ cả bảng). Không chặn pipeline; kiểm tra nguồn ticker_financial."
      echo "WARN fin-breadth ${EXPECTED_Q}: n=${n_cur} đứng yên >=${FIN_BREADTH_STALL_DAYS}d (ref=${ref_n}, sat_floor=${sat_floor}) — non-blocking"
      "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
      WARNED=$((WARNED + 1))
    else
      [ -z "$QUIET" ] && echo "OK   fin-breadth ${EXPECTED_Q}: n=${n_cur}/${n_prev} mã (ref>=${FIN_BREADTH_STALL_DAYS}d: ${ref_n:-chưa đủ lịch sử})"
    fi
  else
    # Query breadth fail trong khi _check ticker_financial phía trên vẫn chạy được = bất thường
    # riêng của probe → WARN fail-safe (cùng triết lý age=999 của _check_lastmod), không chặn.
    warn_msg="🟡 FIN BREADTH WARN ($TODAY $NOW_ICT): probe đếm cohort ${EXPECTED_Q} KHÔNG query được (kết quả: '${breadth_row:-rỗng}') — không đo được breadth hôm nay, kiểm tra bq/logs."
    echo "WARN fin-breadth ${EXPECTED_Q}: query fail — non-blocking"
    "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
  fi
else
  [ -z "$QUIET" ] && echo "SKIP fin-breadth: ngoài mùa BCTC (quý roll-in ${EXPECTED_Q:-?}, cửa sổ = qend+10d..qend+62d)"
fi

# earnings_surprise_data.pkl content-freshness probe (Taylor_20260712_135148, audit M1 Spyros_20260712_131501)
# WARN-only: khối LAG trong golive_recommend_v23.py bọc try/except → pkl hỏng chỉ in WARNING vào log
# 19:00, status.json ghi n_lag_upcoming=0 — không phân biệt được với "hôm nay không có sự kiện mới".
# golive giờ ghi thêm lag_source_error vào golive_v23_status.json (except-path, máy đọc được); probe
# này bắt nốt case còn lại: pkl ĐỌC ĐƯỢC nhưng NỘI DUNG đứng yên (refresh [2] chạy "ok" mà không kéo
# được dữ liệu mới → mtime vẫn tươi, phải so content, không so mtime). Cách đo: mỗi ngày ghi cặp
# (MAX(Release_Date) pkl, MAX(Release_Date) ticker_financial BQ — CÙNG filter re-pull của
# refresh_lagged_caches.py [3] để diff = thuần pipeline-lag, không lẫn khác biệt filter) vào CSV
# state; WARN khi pkl HÔM NAY vẫn chưa đuổi kịp bq_max đã thấy >= LAG_PKL_CATCHUP_DAYS ngày trước.
# pkl full re-pull 15:30 ICT daily → healthy luôn đuổi kịp trong 1 phiên; 4 calendar days nuốt trọn
# weekend + 1 miss transient. KHÔNG so diff pkl-vs-bq tức thời cùng ngày: filing mới rơi vào cửa
# 15:30→19:00 làm pkl trễ 1 refresh là hành vi ĐÚNG, mà khoảng lệch Release_Date lúc đó có thể hàng
# tuần (off-season) → false-fire. Đọc pkl bằng $PY (DNA_PYEXE): python3 hệ thống KHÔNG unpickle được
# pkl pandas-3 (L1 Spyros) — pkl unreadable bằng CHÍNH env pipeline = đúng failure-mode golive sẽ
# gặp lúc 19:00, WARN ngay không cần state. Ngoài mùa BCTC cả pkl lẫn BQ đứng yên cùng nhau → diff 0,
# không false-positive → probe chạy quanh năm, không cần season-gate như fin-breadth.
LAG_PKL_FILE="$WORKDIR/data/earnings_surprise_data.pkl"
LAG_PKL_STATE_CSV="$WORKDIR/data/earnings_pkl_freshness.csv"
LAG_PKL_CATCHUP_DAYS=4
lag_pkl_max="$("$PY" -c "
import pickle, pandas as pd
with open('$LAG_PKL_FILE', 'rb') as f:
    d = pickle.load(f)
m = pd.to_datetime(d['Release_Date'], errors='coerce').dropna().max()
print(m.date())
" 2>/dev/null)"
if [ -z "$lag_pkl_max" ]; then
  warn_msg="🟡 LAG PKL WARN ($TODAY $NOW_ICT): earnings_surprise_data.pkl KHÔNG đọc được bằng env pipeline (\$DNA_PYEXE) — golive_recommend_v23 19:00 sẽ rơi except-path: n_lag_upcoming=0 GIẢ, check field lag_source_error trong data/golive_v23_status.json. Kiểm tra papertrade step [2] refresh_lagged_caches / env pandas."
  echo "WARN lag-pkl: KHÔNG đọc được pkl bằng \$PY — non-blocking"
  "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  WARNED=$((WARNED + 1))
else
  lag_bq_max="$(bq query --use_legacy_sql=false --project_id="$PROJECT" --format=csv --quiet "
    SELECT MAX(t.Release_Date) FROM \`${PROJECT}.tav2_bq.ticker_financial\` AS t
    WHERE t.Release_Date IS NOT NULL AND t.Release_Date >= '2009-01-01' AND t.NP_P0 IS NOT NULL" \
    2>/dev/null | tail -1)"
  if echo "$lag_bq_max" | grep -qE '^[0-9]{4}-[0-9]{2}-[0-9]{2}$'; then
    [ -f "$LAG_PKL_STATE_CSV" ] || echo "date,pkl_max_release,bq_max_release" > "$LAG_PKL_STATE_CSV"
    # 1 dòng/ngày: chạy lại cùng ngày thì thay dòng cũ (giữ số đo mới nhất, giống fin-breadth)
    grep -v "^$TODAY," "$LAG_PKL_STATE_CSV" > "$LAG_PKL_STATE_CSV.tmp" 2>/dev/null && mv "$LAG_PKL_STATE_CSV.tmp" "$LAG_PKL_STATE_CSV"
    echo "$TODAY,$lag_pkl_max,$lag_bq_max" >> "$LAG_PKL_STATE_CSV"
    # ref = bq_max của dòng GẦN NHẤT có tuổi >= CATCHUP_DAYS (so chuỗi YYYY-MM-DD = so ngày);
    # chưa đủ lịch sử (mới wire) → ref rỗng → PASS (grace period, đúng thiết kế fin-breadth)
    LAG_PKL_CUTOFF="$(date -d "-${LAG_PKL_CATCHUP_DAYS} days" +%Y-%m-%d)"
    ref_bq_max=$(awk -F, -v cut="$LAG_PKL_CUTOFF" '$1<=cut {r=$3} END {print r}' "$LAG_PKL_STATE_CSV")
    if [ -n "$ref_bq_max" ] && [ "$lag_pkl_max" \< "$ref_bq_max" ]; then
      warn_msg="🟡 LAG PKL WARN ($TODAY $NOW_ICT): earnings_surprise_data.pkl content STALE — max(Release_Date) pkl=$lag_pkl_max vẫn chưa đuổi kịp BQ ticker_financial=$ref_bq_max đã thấy từ >=${LAG_PKL_CATCHUP_DAYS}d trước (re-pull 15:30 healthy đuổi kịp trong 1 phiên). Giữa mùa BCTC = LAG live candidacy mù sự kiện mới (đúng failure-mode gốc R1). Kiểm tra papertrade step [2] refresh_lagged_caches."
      echo "WARN lag-pkl: pkl_max=$lag_pkl_max < bq_max=$ref_bq_max (đã thấy >=${LAG_PKL_CATCHUP_DAYS}d trước) — content stale, non-blocking"
      "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
      WARNED=$((WARNED + 1))
    else
      [ -z "$QUIET" ] && echo "OK   lag-pkl: pkl_max=$lag_pkl_max, bq_max=$lag_bq_max (catch-up ref >=${LAG_PKL_CATCHUP_DAYS}d: ${ref_bq_max:-chưa đủ lịch sử})"
    fi
  else
    warn_msg="🟡 LAG PKL WARN ($TODAY $NOW_ICT): probe không query được MAX(Release_Date) ticker_financial (kết quả: '${lag_bq_max:-rỗng}') — không đo được content-freshness pkl hôm nay, kiểm tra bq/logs."
    echo "WARN lag-pkl: bq query fail — non-blocking"
    "$ROOT/bin/notify_thread.sh" "$warn_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
  fi
fi

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
  OFFBOOK_VND="$(cd "$WORKDIR" && python3 -c "
from trading_bot.config import load_config, load_accounts
p = next(a for a in load_accounts(load_config()) if a['label'] == '$ACCT')
print(int(p.get('manual_offbook_assets_vnd') or 0))
" 2>/dev/null)"
  NAV_NOTE=""
  if [ "$HAS_EXCL" = "yes" ] || [ "${OFFBOOK_VND:-0}" != "0" ]; then
    NAV_NOTE=" Tài khoản này có excluded_tickers (vị thế legacy ngoài rebalancing) và/hoặc manual_offbook_assets_vnd khác 0 — dùng \`bin/compute_active_nav.py --account $ACCT\` để lấy NAV khả dụng làm cơ sở sizing (loại excluded_tickers, CỘNG offbook), KHÔNG dùng tổng NAV account."
  fi
  if [ "${OFFBOOK_VND:-0}" != "0" ]; then
    NAV_NOTE="$NAV_NOTE Tài khoản này có ${OFFBOOK_VND} VNĐ đang gửi ở sản phẩm Trứng vàng DNSE (off-book, KHÔNG lộ qua API — user tự chuyển, tự báo số dư, xem manual_offbook_assets_note/asof trong secrets/trading_bot_accounts.json). Đây KHÔNG PHẢI mất tiền/rút vốn — cash thật trong tài khoản môi giới sẽ thấp hơn NAV tương ứng, ĐỪNG hiểu là lỗ và ĐỪNG tự tạo lệnh BÁN để 'cân bằng lại' xuống theo cash thấp hơn. Khi TÍNH TỶ TRỌNG mục tiêu, dùng active_nav (đã cộng offbook) làm cơ sở như bình thường. Khi SIZE LỆNH MUA thực tế, kiểm tra sức mua THẬT (availableCash/ppse qua DNSE live) — nếu không đủ vì tiền còn nằm trong Trứng vàng, ghi rõ trong plan note 'cần rút X từ Trứng vàng trước khi thực thi' thay vì âm thầm shrink target hoặc bỏ lệnh. Lưu ý thêm (chưa xác minh, đừng giả định): với SpaceX có dấu hiệu ppse/pp0Buy vẫn báo sức mua cao dù availableCash≈0 sau khi chuyển Trứng vàng (job Mafee_20260716_164743) — có thể DNSE tự tính gộp hoặc số liệu trễ, CHƯA xác nhận; nếu size lệnh dựa vào ppse mà thực tế không đủ, broker sẽ tự từ chối lệnh (an toàn), không phải giả định ppse luôn đúng."
  fi
  "$ROOT/bin/dispatch.sh" DollarBill \
    "Lập plan T+1 cho tài khoản $ACCT. Đọc DT5G từ deploy_golive_dt5g_v4/golive_state_today.json và recommend output mới nhất trong data/. Ghi plan vào data/plan_${ACCT}_${NEXT_TRADING_DAY}.json — dùng ĐÚNG NGUYÊN VĂN ngày $NEXT_TRADING_DAY (đã tính sẵn bằng next_trading_day(), bỏ T7/CN/lễ) làm plan_date và tên file, TUYỆT ĐỐI KHÔNG tự suy ra 'ngày mai' bằng cách cộng 1 vào ngày hôm nay (sự cố thật 2026-07-10: dispatch thứ Sáu tự tính '07-11' là ngày mai, nhưng đó là thứ Bảy không phải ngày giao dịch, đúng ra phải là 07-13 thứ Hai). Ngày hôm nay: $TODAY (ICT).${NAV_NOTE} YÊU CẦU VĂN PHONG (user 2026-07-07): kết thúc final message bằng 3-5 dòng tóm tắt DỄ HIỂU cho người đọc không chuyên — bắt buộc nêu rõ: Account nào · plan ngày nào · hành động chính (HOLD hay mấy lệnh gì) · VÌ SAO 1-2 câu · trạng thái duyệt — vì message này được đăng nguyên văn vào Discord plan channel. Lệnh MUA size bằng tiền bán cùng ngày: trừ phí 0.075% + chừa biên giá, đừng size khít ref price. BẮT BUỘC VỀ GIÁ THAM CHIẾU (user 2026-07-09, tái diễn nhiều lần): mtm_price_ref/ref_price của MỌI mã trong plan phải lấy từ DNSE live quote (dnse_api.py secdef/latest_trade — giá đóng cửa THẬT hôm nay $TODAY) — TUYỆT ĐỐI KHÔNG dùng giá đóng cửa BQ ('ticker'/'ticker_1m' close) làm ref_price, vì BQ cache local chỉ sync đêm 23:45 ICT nên tại giờ bạn chạy (~19:00) BQ cache luôn trễ ít nhất 1 ngày giao dịch — dùng BQ ở đây LUÔN cho ra giá sai/cũ, không phải thỉnh thoảng. Sự cố thật đã xảy ra: plan ZaloPay 07-10 có 2/4 mã (BID, MBB) dùng nhầm 'BQ close 07-08' lệch tới +5.7% so với giá đóng cửa thật 07-09, trong khi 2 mã còn lại dùng đúng DNSE live. Nếu DNSE live quote lỗi/thiếu cho 1 mã nào đó, ghi rõ note 'THIẾU GIÁ LIVE — cần kiểm tra tay' thay vì âm thầm dùng BQ thay thế." \
    --bg 2>/dev/null || echo "  [WARN] dispatch DollarBill cho $ACCT fail — check mike/logs/"
done

echo; echo "=== EOD PIPELINE DONE — $(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT') ==="
