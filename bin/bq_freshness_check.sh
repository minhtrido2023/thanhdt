#!/usr/bin/env bash
# bq_freshness_check.sh — kiểm tra freshness các bảng BQ → nếu fresh chạy pipeline EOD
#
# Luồng 19:00 ICT (cron: 0 12 * * 1-5 — dời từ 17:30, 2026-07-10: daily_refresh_v34b_linux.sh
# (tính DT5G của hôm nay) chạy 18:30, cần chạy SAU nó chứ không phải trước — trước đây chạy
# ở 17:30 nghĩa là luôn đọc DT5G của HÔM QUA, mỗi ngày, vì bản hôm nay chưa kịp tính):
#   → STALE: cảnh báo Telegram + Discord stale-alert channel, dừng, block DollarBill
#   → FRESH: publish_gated_state → golive_recommend → push_to_bq → dispatch DollarBill lập plan
#            (ngay sau publish: gate_source_check.py báo — KHÔNG chặn — khi nguồn cổng ≠ DT5G_macro)
#
# Tables checked (BLOCK = stale ⇒ chặn pipeline + DollarBill; WARN = alert Discord, không chặn):
#   tav2_bq.ticker_prune              BLOCK — daily EOD price (pipeline step H)
#   tav2_bq.vnindex_5state_dt5g_live  BLOCK — DT5G regime (pipeline step G). ⚠️ MAX(time) của bảng
#                                             KHÔNG đủ: bảng có WRITER THỨ HAI (pipeline kaffa_v2
#                                             của team dữ liệu, ~17:12 ICT) vẫn đẩy MAX(time)=hôm nay
#                                             kể cả khi publisher của ta chết ⇒ có thêm gate
#                                             "publisher-evidence" ngay dưới (2026-07-31,
#                                             Winston_20260731_014953) + monitor dt5g_writer_watch.py
#   tav2_bq.ticker_financial          BLOCK — quarterly fundamentals (pipeline step H financial)
#   tav2_bq.ticker_1m                 BLOCK — live screening snapshot (thêm 2026-07-11, audit Winston_20260711_031745 #3)
#   tav2_bq.shares_outstanding_live   WARN  — corp-action scanner-alive (SỬA LẠI 2026-08-03, user báo cáo
#                                             warning liên tục vô ích — 24 ngày WARN liền 07-10→08-03 dù backlog
#                                             thật sạch). Bản 2026-07-12 (audit Winston_20260712_142100 H2) đã
#                                             đúng khi nhận ra bảng này event-driven (chỉ ghi khi có sự kiện thật),
#                                             nhưng vẫn đo SAI tín hiệu: lag=bao lâu chưa GHI vào bảng BQ — với
#                                             writer event-driven, "chưa ghi" thường xuyên là HOÀN TOÀN BÌNH THƯỜNG
#                                             (không phải "gần die"), không phải chỉ báo sức khoẻ. Giờ đo đúng thứ
#                                             cần biết: scanner (`update_shares_live.py --scan`, cron 18:40 ICT
#                                             hàng ngày) có còn CHẠY không, qua `checked_at` của
#                                             `data/corp_action_backlog.json` (file này được ghi MỖI LẦN scan chạy,
#                                             kể cả khi 0 sự kiện mới). Backlog-tồn-đọng-thật (>7 ngày chưa resolve)
#                                             đã có check RIÊNG đúng chỗ ở `ops_health_check.sh` #6 — không lặp lại.
#   tav2_bq.custom30v_8l              BLOCK content-age + WARN writer-alive — V2.4 PRODUCTION parking basket
#   tav2_bq.custom30_8l               BLOCK content-age + WARN writer-alive — legacy blend (audit consumers)
#   tav2_bq.risk_rating               WARN  — research-only, KHÔNG consumer production (orphan, stale từ 2025Q4)
#   ticker_financial breadth-probe    WARN  — đếm cohort quý mới trong mùa BCTC (MAX(time) toàn bảng
#                                             bị 1 mã early-filer reset đồng hồ — audit Winston_20260712_122313 F1)
#   earnings_surprise_data.pkl probe  WARN  — content catch-up pkl vs ticker_financial: nguồn LAG live
#                                             candidacy, golive except-path nuốt lỗi im lặng
#                                             (audit Spyros_20260712_131501 M1)
#   PNJ BCTC Q3 review-trigger watch  WARN  — PNJ có dòng quarter=2026Q3 trong ticker_financial ⇒ MỘT
#                                             LẦN: bus question + Discord (bin/pnj_q3_review_watch.py)
#
# Bước pipeline (sau khi ALL FRESH): 1 publish_gated_state · 1b universe_pit · 1c universe_pit_quality ·
#   1d refresh_earnings_surprise_pkl (BQ SỐNG → pkl LAG, WARN-only, 2026-10-13) · 2 golive_recommend_v23 ·
#   3 push_recommend_v23_to_bq · 4 dispatch DollarBill
#
# Usage: bin/bq_freshness_check.sh [--quiet]
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true
# Neo TZ ICT KHÔNG ĐIỀU KIỆN: script này chỉ có nghĩa ở ICT (mọi mốc ngày — TODAY, tuổi file,
# next trading day — đều tính theo phiên HOSE giờ ICT). Trước đây chỉ vá khi TZ CHƯA đặt
# (`${TZ:-...}`), nên caller nào export TZ=UTC (cron khác, shell tay) vẫn được tôn trọng ⇒
# sau 17:00 ICT, TODAY (và mọi datetime.now()/date.today() phía dưới thừa hưởng TZ này) lùi
# 1 ngày, gate so as_of/mtime sai ngày (finding code-quality 2026-09-20). Ghi đè vô điều kiện.
export TZ=Asia/Ho_Chi_Minh

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
MAX_SCANNER_IDLE=3   # calendar days trên checked_at của corp_action_backlog.json (SỬA 2026-08-03,
                     # thay MAX_SHARES_LAG — xem giải thích ở khối comment đầu file). Scanner chạy
                     # T2-T6 (cron 40 11 * * 1-5 UTC = 18:40 ICT) — 3 ngày lịch dung sai cuối tuần
                     # (Fri chạy → Mon kỳ vọng, cách nhau đúng 3 ngày lịch) mà không WARN giả.
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
# MORNING MODE (opt-in, 2026-10-15, user duyệt): MIKE_MORNING_RUN=1 ⇒ chạy tay buổi sáng khi BQ xong muộn
# sau chuỗi 18:30 hôm trước. TODAY = PHIÊN gần nhất đã có dữ liệu EOD (bin/expected_session.py, cutoff
# 17:00 ICT) thay vì ngày lịch; NEXT_TRADING_DAY = ngày giao dịch kế tiếp sau phiên đó (= hôm nay).
# Cron KHÔNG đặt biến này ⇒ hành vi 19:00 y nguyên. Mọi cổng khác GIỮ NGUYÊN; chỉ điều kiện mtime của
# publisher DT5G đổi (xem gate dưới): phải >= phiên và <= hôm nay thay vì == hôm nay.
MORNING="${MIKE_MORNING_RUN:-0}"
CAL_TODAY="$(date +%Y-%m-%d)"   # ngày LỊCH (khác TODAY=phiên ở morning mode)
if [ "$MORNING" = "1" ]; then
  _sess="$(python3 "$(dirname "${BASH_SOURCE[0]}")/expected_session.py" --morning 2>/tmp/.expected_session_err.$$)"; _sess_rc=$?
  _sess_err="$(cat /tmp/.expected_session_err.$$ 2>/dev/null)"; rm -f /tmp/.expected_session_err.$$
  TODAY="${_sess%% *}"; MORNING_NEXT="${_sess##* }"
  if [ "$_sess_rc" -ne 0 ] || ! [[ "$TODAY" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ && "$MORNING_NEXT" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
    echo "FATAL: MIKE_MORNING_RUN=1 bị từ chối/lỗi (rc=$_sess_rc, got: '$_sess'): ${_sess_err:-không có stderr} — dừng" >&2
    exit 1
  fi
  echo "MORNING MODE: phiên=$TODAY, plan cho=$MORNING_NEXT (MIKE_MORNING_RUN=1)"
fi
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
[ "$MORNING" = "1" ] && NEXT_TRADING_DAY="$MORNING_NEXT"
if [ -z "$NEXT_TRADING_DAY" ]; then
  echo "FATAL: không tính được NEXT_TRADING_DAY (next_trading_day() lỗi) — dừng, không dispatch DollarBill với ngày rỗng" >&2
  exit 1
fi

# Discord: Trading Daily thread — mọi nội dung giao dịch hàng ngày gộp về 1 topic.
DISCORD_STALE_CHANNEL="trading_daily"   # tên trong kb/discord_channels.json

# _check <label> <table> <colexpr> <max_lag> <trading|calendar> [BLOCK|WARN]
#   colexpr = biểu thức SQL đầy đủ với alias `t.` (vd "t.time", "DATE(t.updated_at)",
#   hoặc expr đổi quarter-string thành DATE) — cho phép check bảng không có cột DATE thô.
#   BLOCK (default) = stale ⇒ FAILED=1, Telegram + Discord, chặn pipeline/DollarBill.
#   WARN = stale ⇒ WARNED+=1, chỉ Discord Trading Daily (không Telegram, không chặn) —
#   dùng cho bảng research/early-warning mà việc block plan vì nó là phản ứng quá tay.
_check() {
  local label="$1" table="$2" colexpr="$3" max_lag_days="$4" lag_unit="$5" mode="${6:-BLOCK}"
  local query result rc lag_days

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
    --format=csv --quiet "$query" 2>&1)
  rc=$?
  lag_days="$(printf '%s\n' "$result" | tail -1)"
  # bq lỗi (auth/quota/network) hoặc output không phải số ⇒ KHÔNG PHẢI bảng stale, đừng báo
  # lag=999/STALE — báo đúng nguyên nhân (§28: tách "không tìm thấy bằng chứng" khỏi "tìm thấy
  # và xấu"). Query thật ra số nguyên/thập phân qua CSV; bất cứ gì khác cần tách 2 case (arch-
  # review coord-2026-09-27 round 1): rc!=0 = KHÔNG kết nối/tra được BQ (auth/quota/network);
  # rc=0 nhưng giá trị không phải số = BQ TRẢ LỜI ĐƯỢC nhưng dữ liệu bất thường (bảng rỗng/cột
  # toàn NULL/schema đổi tên cột) — khác nguyên nhân, khác hướng xử lý, đừng gộp chung một câu
  # "kiểm tra auth/quota/network" (repro: MAX() trên bảng rỗng trả NULL dù bq hoàn toàn khoẻ).
  if [ $rc -ne 0 ] || ! printf '%s' "$lag_days" | grep -qE '^-?[0-9]+(\.[0-9]+)?$'; then
    local errsnip reason fail_msg
    # Lấy từ TOÀN BỘ $result (không phải tail -1 của lag_days) — bq thường wrap lỗi thành
    # nhiều dòng, dòng cuối một mình có thể chỉ còn 1 mảnh vô nghĩa (repro round 1: "southeast1]").
    errsnip="$(printf '%s' "$result" | tr '\n' ' ' | cut -c1-200)"
    if [ $rc -ne 0 ]; then
      reason="bq lỗi kết nối/quyền (rc=$rc, auth/quota/network)"
      fail_msg="⚠️ BQ QUERY FAILED ($TODAY $NOW_ICT): $label — ${reason}: ${errsnip}. KHÔNG PHẢI bảng stale."
    else
      reason="bq trả giá trị không phải số dù rc=0 ('${lag_days}') — bảng rỗng/cột toàn NULL/schema đổi"
      fail_msg="⚠️ BQ DATA BẤT THƯỜNG ($TODAY $NOW_ICT): $label — ${reason}. KHÔNG PHẢI lỗi kết nối BQ, đừng kiểm tra auth/quota — kiểm tra bảng/cột/schema. (raw: ${errsnip})"
    fi
    echo "FAIL $label: ${reason} (raw: ${errsnip})"
    if [ "$mode" = "WARN" ]; then
      "$ROOT/bin/notify_thread.sh" "$fail_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
      WARNED=$((WARNED + 1))
      return 0
    fi
    "$ROOT/bin/notify.sh" "$fail_msg" 2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "$fail_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    FAILED=1
    return 1
  fi
  lag_days=$(printf "%.0f" "$lag_days" 2>/dev/null || echo "$lag_days")

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
  local show_out show_rc ms age_days
  show_out=$(bq show --format=prettyjson "${PROJECT}:${table}" 2>&1)
  show_rc=$?
  if [ $show_rc -ne 0 ]; then
    local errsnip
    errsnip="$(printf '%s' "$show_out" | tr '\n' ' ' | cut -c1-200)"
    local fail_msg="⚠️ BQ QUERY FAILED ($TODAY $NOW_ICT): $label — bq show thất bại (rc=$show_rc): ${errsnip}. KHÔNG PHẢI writer chết, kiểm tra auth/quota/network."
    echo "FAIL $label: BQ QUERY FAILED (rc=$show_rc): ${errsnip}"
    "$ROOT/bin/notify_thread.sh" "$fail_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
    return 0
  fi
  ms=$(printf '%s' "$show_out" \
       | python3 -c "import json,sys; print(json.load(sys.stdin).get('lastModifiedTime',0))" 2>/dev/null)
  ms="${ms:-0}"
  if [ "$ms" -gt 0 ] 2>/dev/null; then
    age_days=$(( ( $(date +%s) - ms / 1000 ) / 86400 ))
  else
    age_days=999   # metadata đọc được nhưng thiếu lastModifiedTime = đáng ngờ thật (fail-safe), báo WARN
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

# _check_price_freeze: phát hiện cột giá THÔ bị ETL upstream copy nguyên từ phiên T-1 trên
# DIỆN RỘNG (2026-09-27, job Taylor_20260927_103434). Vì sao cần một check RIÊNG: cả 3 gate
# giá phía trên đều mù với lỗi này — _check đo MAX(time) (vẫn advance), depth-check đếm số mã
# (vẫn đủ ~250), và cache == live nên không phải lỗi cache. Sự cố thật đã xảy ra 2 lần mà
# KHÔNG có gì kêu: 2026-01-30 (254/256 mã Price[t]==Price[t-1]) và 2025-02-03 (258/258).
#
# NGƯỠNG ĐO TỪ DỮ LIỆU, không bốc số — phân bố 4.171 phiên ticker_prune 2010-01-05→2026-09-25
# (series: mike/agents/Taylor/research/price_freeze_gate_20260927/daily_flat_series_v2.csv,
# script tái lập: .../calibrate.py). Trên 3.174 phiên 2014+:
#   tỉ lệ mã có Price phẳng: p50=0,136  p90=0,216  p99=0,291  p99,9=0,381  → rồi KHOẢNG TRỐNG
#   → 0,755 (2018-01-23) / 0,792 (2018-01-24) / 0,992 (2026-01-30) / 1,000 (2025-02-03).
#   Chọn 0,50 = giữa khoảng trống rỗng [0,381 ; 0,755]; ≈ med + 6,7·robustSD (1,4826·MAD).
#   FP thực đo = 0/3.174 phiên (2014+) và 0/4.171 (2010+); bắt 4/4 phiên bất thường đã biết.
# So sánh cặp = PHIÊN LIỀN KỀ CỦA BẢNG (LAG trên danh sách ngày distinct), KHÔNG phải
# "cách ≤7 ngày lịch": bản đầu dùng ngưỡng ngày lịch đã ÂM THẦM bỏ qua chính phiên đầu sau
# Tết (gap 10-12 ngày) — và 2025-02-03, một trong hai phiên đóng băng thật, RƠI ĐÚNG vào đó.
#
# Hai chữ ký cơ học KHÁC NHAU, hệ quả khác nhau (§29: rẽ nhánh theo bit script vừa ĐỌC được,
# không quy chụp một nguyên nhân):
#   (a) Price phẳng nhưng Close (đã điều chỉnh) VẪN đổi ⇒ lỗi riêng cột Price thô. Close mới
#       là cột production đọc ⇒ WARN, không chặn. Chữ ký 2026-01-30 (222/254), 2025-02-03 (234/258).
#   (b) CẢ Price và Close phẳng ⇒ nguyên dòng giá là bản sao T-1. Bước [pipeline-1b/1c]
#       (build_universe_pit + _quality) và chấm điểm custom30V ngay dưới sẽ ăn dữ liệu chết
#       ⇒ BLOCK. Chữ ký 2018-01-24 (174/221 mã phẳng CẢ HAI cột = 0,787). Ngưỡng 0,50 đo
#       riêng cho metric này trên cùng 3.174 phiên 2014+: p50=0,133 p99=0,286 p99,9=0,353,
#       giá trị lớn nhất KHÔNG thuộc phiên bất thường nào = 0,377 ⇒ 0 FP; chỉ 2018-01-24 vượt.
#       (2018-01-23 AB=0,455 — chữ ký PHA TRỘN, 66/166 mã có Close đổi — nên nó rơi vào nhánh
#       WARN qua metric Price-phẳng 0,755, KHÔNG bị BLOCK. Đó là hành vi ĐÚNG mong muốn.)
MAX_PRICE_FLAT_PCT=50   # % mã có Price[t]==Price[t-1] — xem khối trên, đo từ 4.171 phiên
MIN_FLAT_SAMPLE=50      # < 50 cặp mã so được ⇒ KHÔNG kết luận (nói thẳng), đừng báo động
_check_price_freeze() {
  local q result rc row n_tot n_flat n_cm n_both pct_flat pct_both pct_cm_of_flat d dprev
  q="WITH days AS (
       SELECT DISTINCT time AS d FROM \`${PROJECT}.tav2_bq.ticker_prune\`
       WHERE time >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 60 DAY)),
     dseq AS (SELECT d, LAG(d) OVER (ORDER BY d) AS dprev FROM days),
     last2 AS (SELECT d, dprev FROM dseq ORDER BY d DESC LIMIT 1),
     b AS (
       SELECT ticker, time, Price, Close,
              LAG(Price) OVER (PARTITION BY ticker ORDER BY time) AS p_prev,
              LAG(Close) OVER (PARTITION BY ticker ORDER BY time) AS c_prev,
              LAG(time)  OVER (PARTITION BY ticker ORDER BY time) AS t_prev
       FROM \`${PROJECT}.tav2_bq.ticker_prune\`
       WHERE time >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 60 DAY))
     SELECT COUNT(*) AS n_tot,
            COUNTIF(b.Price = b.p_prev) AS n_flat,
            COUNTIF(b.Price = b.p_prev AND b.Close != b.c_prev) AS n_cm,
            COUNTIF(b.Price = b.p_prev AND b.Close =  b.c_prev) AS n_both,
            CAST(MAX(l.d) AS STRING) AS d, CAST(MAX(l.dprev) AS STRING) AS dprev
     FROM b JOIN last2 AS l ON b.time = l.d AND b.t_prev = l.dprev
     WHERE b.Price IS NOT NULL AND b.p_prev IS NOT NULL
       AND b.Close IS NOT NULL AND b.c_prev IS NOT NULL"

  result=$(bq query --use_legacy_sql=false --project_id="$PROJECT" --format=csv --quiet "$q" 2>&1)
  rc=$?
  row="$(printf '%s\n' "$result" | tail -1)"
  # §28/§29: tách "không tra được BQ" khỏi "tra được nhưng dữ liệu bất thường"; in LỖI THẬT
  # bq vừa trả, không đoán nguyên nhân.
  if [ $rc -ne 0 ] || ! printf '%s' "$row" | grep -qE '^[0-9]+,[0-9]+,[0-9]+,[0-9]+,[0-9-]+,[0-9-]+$'; then
    local errsnip reason
    errsnip="$(printf '%s' "$result" | tr '\n' ' ' | cut -c1-200)"
    if [ $rc -ne 0 ]; then
      reason="bq lỗi kết nối/quyền (rc=$rc, auth/quota/network)"
    else
      reason="bq trả dòng không đúng dạng dù rc=0 ('${row}') — bảng rỗng/đổi schema"
    fi
    echo "SKIP ticker_prune Price-freeze: KHÔNG kết luận được — ${reason} (raw: ${errsnip})"
    "$ROOT/bin/notify_thread.sh" "🟡 BQ CHECK KHÔNG CHẠY ĐƯỢC ($TODAY $NOW_ICT): Price-freeze gate trên ticker_prune — ${reason}. ĐÂY KHÔNG PHẢI kết luận 'dữ liệu sạch', chỉ là không đo được. (raw: ${errsnip})" \
      "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
    return 0
  fi

  IFS=, read -r n_tot n_flat n_cm n_both d dprev <<<"$row"

  # Fail-safe theo hướng KHÔNG báo động giả: quá ít cặp mã so được (mã mới vào universe, phiên
  # đầu sau đợt nghỉ dài mà bảng thiếu ngày liền trước…) ⇒ nói thẳng là không kết luận được.
  if [ "$n_tot" -lt "$MIN_FLAT_SAMPLE" ] 2>/dev/null; then
    echo "SKIP ticker_prune Price-freeze: chỉ ${n_tot} mã có cả $d và $dprev (<${MIN_FLAT_SAMPLE}) — KHÔNG đủ dữ liệu để kết luận, không báo động"
    return 0
  fi

  pct_flat=$(( n_flat * 100 / n_tot ))
  pct_both=$(( n_both * 100 / n_tot ))
  pct_cm_of_flat=0
  [ "$n_flat" -gt 0 ] && pct_cm_of_flat=$(( n_cm * 100 / n_flat ))

  if [ "$pct_both" -gt "$MAX_PRICE_FLAT_PCT" ]; then
    # Chữ ký (b): cả hai cột phẳng ⇒ nguyên dòng giá là bản sao T-1 ⇒ chặn pipeline.
    local msg="⚠️ BQ PRICE FROZEN ($TODAY $NOW_ICT): ticker_prune phiên $d — ${n_both}/${n_tot} mã (${pct_both}%) có CẢ Price VÀ Close y hệt phiên $dprev, vượt ngưỡng ${MAX_PRICE_FLAT_PCT}% (đo từ 3.174 phiên 2014+: p99,9=35%, cao nhất phần thân=46%). Nguyên dòng giá nghi là bản sao T-1 ⇒ build_universe_pit + chấm custom30V sẽ ăn dữ liệu chết. CHẶN pipeline. So sánh: tổng mã Price phẳng ${n_flat}/${n_tot} (${pct_flat}%), trong đó ${n_cm} mã có Close đổi."
    echo "FAIL ticker_prune Price-freeze: both-flat ${n_both}/${n_tot} (${pct_both}%) phiên $d vs $dprev (>${MAX_PRICE_FLAT_PCT}%) — nguyên dòng giá nghi copy T-1"
    "$ROOT/bin/notify.sh" "$msg" 2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "$msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    FAILED=1
    return 1
  fi

  if [ "$pct_flat" -gt "$MAX_PRICE_FLAT_PCT" ]; then
    # Chữ ký (a): Price thô phẳng nhưng Close đã điều chỉnh vẫn đổi ⇒ lỗi cột Price của ETL
    # nguồn. Close mới là cột production đọc ⇒ WARN, không chặn.
    local msg="🟡 BQ WARN — Price THÔ đóng băng ($TODAY $NOW_ICT): ticker_prune phiên $d — ${n_flat}/${n_tot} mã (${pct_flat}%) có Price y hệt phiên $dprev, vượt ngưỡng ${MAX_PRICE_FLAT_PCT}% (đo từ 3.174 phiên 2014+: p99,9=38%, khoảng trống 38%→76%). Trong số đó ${n_cm}/${n_flat} mã (${pct_cm_of_flat}%) có Close (đã điều chỉnh) VẪN đổi ⇒ đúng chữ ký lỗi RIÊNG cột Price thô của ETL nguồn (giống 2026-01-30: 222/254; 2025-02-03: 234/258), KHÔNG phải phiên nghỉ/không giao dịch. Close là cột production đọc nên KHÔNG chặn pipeline; báo upstream sửa cột Price. Both-flat ${n_both}/${n_tot} (${pct_both}%)."
    echo "WARN ticker_prune Price-freeze: Price phẳng ${n_flat}/${n_tot} (${pct_flat}%) phiên $d vs $dprev (>${MAX_PRICE_FLAT_PCT}%), Close vẫn đổi ở ${n_cm}/${n_flat} — lỗi cột Price thô, non-blocking"
    "$ROOT/bin/notify_thread.sh" "$msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
    return 0
  fi

  [ -z "$QUIET" ] && echo "OK   ticker_prune Price-freeze: ${n_flat}/${n_tot} mã Price phẳng (${pct_flat}% ≤${MAX_PRICE_FLAT_PCT}%) phiên $d vs $dprev; both-flat ${n_both}/${n_tot} (${pct_both}%)"
  return 0
}

# _check_corp_action_scanner: thay cho _check cũ trên shares_outstanding_live (xem giải thích
# đầy đủ ở khối comment đầu file, mục "SỬA LẠI 2026-08-03"). Đo scanner có còn chạy qua
# checked_at của corp_action_backlog.json — KHÔNG đo lag ghi bảng BQ (writer event-driven,
# "chưa ghi" không phải tín hiệu bệnh).
_check_corp_action_scanner() {
  local backlog="$WC_ROOT/data/corp_action_backlog.json"
  local age_days
  age_days=$(python3 -c "
import json
from datetime import datetime
try:
    d = json.load(open('$backlog', encoding='utf-8'))
    checked = datetime.fromisoformat(d['checked_at'])
    print((datetime.now() - checked).days)
except Exception:
    print(999)
" 2>/dev/null)
  age_days="${age_days:-999}"

  if [ "$age_days" -le "$MAX_SCANNER_IDLE" ] 2>/dev/null; then
    [ -z "$QUIET" ] && echo "OK   shares_outstanding_live scanner (corp-action): checked_at ${age_days}d trước (≤${MAX_SCANNER_IDLE})"
    return 0
  else
    local warn_msg="🟡 BQ WARN ($TODAY $NOW_ICT): corp-action scanner (update_shares_live.py --scan, cron 18:40 ICT hàng ngày) chưa chạy ${age_days}d (>${MAX_SCANNER_IDLE}) — có thể đã chết. Kiểm tra crontab + logs/update_shares_live.log."
    echo "WARN shares_outstanding_live scanner (corp-action): checked_at ${age_days}d trước (>${MAX_SCANNER_IDLE}) — scanner có thể chết, non-blocking"
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
_check_price_freeze || true
_check "vnindex_5state_dt5g_live (DT5G)"  "tav2_bq.vnindex_5state_dt5g_live"  "t.time"  $MAX_STATE_LAG  "trading"  || true
# --- DT5G PUBLISHER-EVIDENCE gate (2026-07-31, job Winston_20260731_014953) ------------------
# VÌ SAO cần: bảng dt5g_live có WRITER THỨ HAI ngoài luồng — pipeline kaffa_v2 của team dữ liệu
# (/workspace/kaffa_v2, task update_market_regime_state) tự tính DT5G bằng implementation RIÊNG
# và ghi thẳng vào bảng production ~17:12 ICT mỗi ngày (từ 2026-06-08; truy vết đầy đủ:
# mike/agents/Winston/dt5g_live_second_writer_20260729.md). Hệ quả: _check MAX(time) NGAY TRÊN
# bị CHE HOÀN TOÀN — kaffa đẩy MAX(time)=hôm nay lúc 17:12 nên gate PASS kể cả khi publisher
# CỦA TA (daily_refresh step [12], ~18:35) chết sạch. Giả định load-bearing ở
# daily_refresh_v34b_linux.sh:59 ("bảng sẽ không advance nếu chain của ta abort") ĐÃ SAI.
# User quyết 2026-07-31 (PHƯƠNG ÁN B): KHÔNG yêu cầu team dữ liệu đổi bảng, KHÔNG đụng hệ thống
# của họ — ta tự vá gate phía mình + giám sát, và báo họ khi có sự cố.
# CÁCH VÁ: gate bằng BẰNG CHỨNG publisher CỦA TA đã chạy, không bằng nội dung bảng (bảng là thứ
# writer ngoài ghi được, 2 file dưới thì KHÔNG — chỉ publish_gated_state.py ghi chúng):
#   deploy_golive_dt5g_v4/golive_state_today.json  →  as_of == phiên giao dịch mới nhất
#                                                  +  bq_publish_ok == true
#                                                  +  mtime = HÔM NAY (nếu hôm nay là phiên)
# Ngày KHÔNG giao dịch (lễ giữa tuần — cron vẫn chạy T2-T6): bỏ điều kiện mtime, chỉ đòi
# as_of == phiên gần nhất. Không có nó thì gate sẽ chặn oan mọi ngày lễ (step [0] của
# daily_refresh cố tình die khi không có ingest hôm nay ⇒ không có file mới).
# CSV mirror data/vnindex_5state_dt5g_live.csv = WARN chứ không BLOCK: publish BQ có thể OK mà
# export CSV lỗi (publish_gated_state.py bắt riêng exception đó) — lúc đó consumer production
# vẫn đúng, chỉ nhóm script nghiên cứu đọc CSV là cũ ⇒ chặn cả plan vì nó là quá tay.
read -r LAST_TRADING_DAY IS_TRADING_TODAY <<< "$(cd "$WORKDIR" && python3 -c "
from trading_bot.vn_market import is_holiday
import datetime as dt
d = dt.date.fromisoformat('$TODAY')
trading = 0 if (d.weekday() >= 5 or is_holiday(d)) else 1
while d.weekday() >= 5 or is_holiday(d):
    d -= dt.timedelta(days=1)
print(d, trading)
" 2>/dev/null)"
STATE_JSON_F="$WORKDIR/deploy_golive_dt5g_v4/golive_state_today.json"
DT5G_CSV_F="$WORKDIR/data/vnindex_5state_dt5g_live.csv"
dt5g_pub_reason=""
if [ -z "${LAST_TRADING_DAY:-}" ]; then
  dt5g_pub_reason="không tính được phiên giao dịch gần nhất (trading_bot.vn_market lỗi)"
elif [ ! -f "$STATE_JSON_F" ]; then
  dt5g_pub_reason="golive_state_today.json KHÔNG TỒN TẠI — publisher của ta chưa từng chạy"
else
  read -r DT5G_AS_OF DT5G_PUB_OK <<< "$(python3 -c "
import json
d = json.load(open('$STATE_JSON_F', encoding='utf-8'))
print(d.get('as_of', '?'), 'ok' if d.get('bq_publish_ok') else 'FAIL')
" 2>/dev/null)"
  DT5G_JSON_MDATE="$(date -d @"$(stat -c %Y "$STATE_JSON_F")" +%Y-%m-%d 2>/dev/null)"
  if [ "${DT5G_AS_OF:-?}" != "$LAST_TRADING_DAY" ]; then
    dt5g_pub_reason="golive_state_today.json as_of=${DT5G_AS_OF:-?} ≠ phiên gần nhất $LAST_TRADING_DAY"
  elif [ "${DT5G_PUB_OK:-FAIL}" != "ok" ]; then
    dt5g_pub_reason="golive_state_today.json bq_publish_ok=false — publish lên BQ đã HỎNG"
  elif [ "${MORNING:-0}" = "1" ]; then
    # Morning mode: publisher phải chạy SAU phiên (mtime >= phiên) và không ở tương lai (<= hôm nay lịch).
    if [[ "$DT5G_JSON_MDATE" < "$TODAY" || "$DT5G_JSON_MDATE" > "${CAL_TODAY:-$(date +%Y-%m-%d)}" ]]; then
      dt5g_pub_reason="golive_state_today.json mtime=$DT5G_JSON_MDATE ngoài [$TODAY, hôm nay] — publisher của ta KHÔNG chạy sau phiên $TODAY"
    fi
  elif [ "$IS_TRADING_TODAY" = "1" ] && [ "$DT5G_JSON_MDATE" != "$TODAY" ]; then
    dt5g_pub_reason="golive_state_today.json mtime=$DT5G_JSON_MDATE ≠ hôm nay $TODAY — publisher của ta KHÔNG chạy hôm nay"
  fi
fi
if [ -n "$dt5g_pub_reason" ]; then
  pub_msg="⚠️ DT5G PUBLISHER ($TODAY $NOW_ICT): $dt5g_pub_reason. Bảng vnindex_5state_dt5g_live CÓ THỂ vẫn tươi do writer thứ hai (pipeline kaffa_v2 team dữ liệu ~17:12 ICT) — nhưng đó KHÔNG PHẢI state của engine ta công bố. Chặn pipeline/DollarBill. Kiểm tra daily_refresh_v34b_linux.sh step [12] + data/refresh_v34b_linux_${CAL_TODAY:-$TODAY}.log"
  echo "FAIL DT5G publisher-evidence: $dt5g_pub_reason"
  "$ROOT/bin/notify.sh" "$pub_msg" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$pub_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  FAILED=1
else
  [ -z "$QUIET" ] && echo "OK   DT5G publisher-evidence: golive_state_today.json as_of=$DT5G_AS_OF (phiên gần nhất), bq_publish_ok=true, mtime=$DT5G_JSON_MDATE"
  DT5G_CSV_MDATE="$(date -d @"$(stat -c %Y "$DT5G_CSV_F" 2>/dev/null || echo 0)" +%Y-%m-%d 2>/dev/null)"
  if [ "${MORNING:-0}" != "1" ] && [ "$IS_TRADING_TODAY" = "1" ] && [ "$DT5G_CSV_MDATE" != "$TODAY" ]; then
    csv_msg="🟡 DT5G CSV MIRROR ($TODAY $NOW_ICT): data/vnindex_5state_dt5g_live.csv mtime=${DT5G_CSV_MDATE:-MISSING} ≠ hôm nay dù publish BQ OK — export CSV từ BQ đã lỗi. Production (BQ) vẫn ĐÚNG; nhóm script nghiên cứu đọc CSV này đang dùng bản cũ. Không chặn pipeline."
    echo "WARN DT5G csv mirror: mtime=${DT5G_CSV_MDATE:-MISSING} ≠ $TODAY — non-blocking"
    "$ROOT/bin/notify_thread.sh" "$csv_msg" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED + 1))
  else
    [ -z "$QUIET" ] && echo "OK   DT5G csv mirror: mtime=${DT5G_CSV_MDATE:-?}"
  fi
fi
# Giám sát WRITER LẠ (WARN-only, không bao giờ chặn) — xem docstring mike/bin/dt5g_writer_watch.py.
# Lấy mẫu ở đây là mẫu SAU publish của daily_refresh; mẫu QUAN TRỌNG hơn (thấy được writer ngoài
# trước khi ta đè lên) nằm ở đầu daily_refresh_v34b_linux.sh.
python3 "$ROOT/bin/dt5g_writer_watch.py" --label bq-freshness-19h || true
_check "ticker_financial (fundamentals)"  "tav2_bq.ticker_financial"          "t.time"  $MAX_FIN_LAG    "calendar" || true
# --- mở rộng 2026-07-11 (audit Winston_20260711_031745 #3) ---
_check "ticker_1m (live screening)"       "tav2_bq.ticker_1m"                 "t.time"  $MAX_1M_LAG     "trading"  || true
_check_corp_action_scanner || true
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
from zoneinfo import ZoneInfo
today = dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()   # neo ICT tường minh (§16), không phụ thuộc TZ cron
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

# --- PNJ BCTC Q3 review-trigger watch (audit BCTC Q3 finding L2; user duyệt 2026-10-13, job
# Taylor_20261013_125149). PNJ bị loại khỏi 2 account từ 09-30, điều kiện xét lại = "khi PNJ công bố
# BCTC Q3" (kb/current_ops.md) — trước đây chỉ là văn xuôi, không ai canh. Script tự chống lặp bằng
# state file ghi nguyên tử (data/pnj_q3_review_watch_state.json) và fail-closed khi lỗi đọc; ở đây
# chỉ gọi + giới hạn thời gian. KHÔNG đếm vào WARNED, KHÔNG chặn pipeline, KHÔNG đụng excluded_tickers.
if _pnj_out="$(cd "$ROOT" && timeout 60 python3 bin/pnj_q3_review_watch.py ${QUIET:+--quiet} 2>&1)"; then
  [ -n "$_pnj_out" ] && echo "$_pnj_out"
else
  echo "  [WARN] pnj_q3_review_watch.py exit=$? (124 = timeout 60s) — không chặn pipeline. Output thật: ${_pnj_out:-<rỗng>}"
fi
if printf '%s\n' "$_pnj_out" | grep -q '^ALERT pnj-q3-watch:'; then
  # watcher chết lặng = đúng lỗi nó sinh ra để vá (arch-review 13/10 R2) ⇒ báo người, không chỉ log
  "$ROOT/bin/notify_thread.sh" "🔴 pnj_q3_review_watch KHÔNG hoạt động đúng ($TODAY): $(printf '%s\n' "$_pnj_out" | grep -E '^(WARN|ALERT) pnj-q3-watch' | head -3 | cut -c1-600)" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  WARNED=$((WARNED + 1))
fi

[ "$WARNED" -gt 0 ] && echo "NOTE: $WARNED WARN non-blocking (đã post Discord Trading Daily) — pipeline vẫn chạy"

# --- [pipeline-0] nav_exdate_forecast — cảnh báo TRƯỚC corp-action ≤1 PHIÊN trên mã đang giữ
# (L1, quyết định user 2026-09-22 sau lớp lỗi "NAV bị PRICE_XCHECK chặn vì corp-action" tái diễn
# ≥4 lần: PVT 09-08/DGC 09-11/VIB 09-09/VHM 08-05/DRI 09-21 — dữ liệu này đã nằm sẵn trên đĩa từ
# cron corp_action_daily 07:30 nhưng không ai đọc kịp trước khi NAV chạy ~21h. Đọc LẠI
# `upcoming_events_held` đã có, KHÔNG tính gì mới. Read-only + notify — lỗi ở đây KHÔNG được
# chặn pipeline/DollarBill (đây là cảnh báo sớm, không phải gate). CỐ Ý đặt TRƯỚC cổng
# FAILED/exit dưới đây: nav_exdate_forecast.py KHÔNG đọc BQ (chỉ đọc
# data/corp_action_daily/<date>.json + data/execution_logs/active_nav_*.json), NAV cũng KHÔNG
# chạy trong chuỗi này (cron riêng: nav_snapshot_daily.sh/nav_sync_retry.sh) — một ngày BQ
# stale (đã xảy ra thật 2026-09-14) không được phép nuốt mất cảnh báo corp-action đúng ngày hệ
# thống đang trục trặc (arch-review vòng 2, Mike, 2026-09-22).
echo; echo "--- [pipeline-0] nav_exdate_forecast (corp-action ≤1 PHIÊN, mã đang giữ) ---"
(cd "$ROOT" && python3 bin/nav_exdate_forecast.py --alert 2>&1) || \
  echo "  [WARN] nav_exdate_forecast.py lỗi — không chặn pipeline, kiểm tay: mike/bin/nav_exdate_forecast.py"

# [pipeline-3c] cảnh báo QUYỀN MUA của mã ĐANG GIỮ (user duyệt 2026-10-22 09:27 ICT, "Duyệt việc 1"; audit
# Taylor_20261021_165512 REPORT.md B1/B4) — WARN-only, KHÔNG chặn DollarBill, KHÔNG chạm lệnh/NAV/sizing.
# Ba giai đoạn ANNOUNCE (kể cả trạng thái P chưa ngày/giá) / DATED / REMIND ≤3 phiên, mỗi cái dedupe riêng,
# state ghi atomic SAU khi gửi xong (state/rights_issue_alert_state.json). Vị thế đọc từ active_nav_*.json
# (cron 20:15 hôm trước) ⇒ rc=2 nếu không có file nào: KHÔNG kết luận "không giữ mã nào". Bỏ qua morning mode
# (chạy tay) để không nhân đôi tin; gửi Trading Daily nên T7/CN không cần (chuỗi này chỉ chạy T2-T6).
# VỊ TRÍ (arch-review 2026-10-22 B3): ngay SAU [pipeline-0], TRƯỚC cổng FAILED/exit — cùng lý do với [pipeline-0]:
# rights_issue_alert chỉ đọc BQ corporate_action + active_nav_*.json, không phụ thuộc BQ-fresh của chuỗi; đặt SAU
# các `exit 1` thì ngày BQ stale mất cả REMIND (khoá REMIND chứa asof ⇒ mất hẳn, không bù được).
if [ "${MORNING:-0}" != "1" ]; then
  echo; echo "--- [pipeline-3c] rights_issue_alert ---"
  _ra_out="$(timeout "${RIGHTS_ALERT_TIMEOUT_S:-120}" python3 "$ROOT/bin/rights_issue_alert.py" --send 2>&1)"; _ra_rc=$?
  echo "$_ra_out" | tail -20
  # rc 0 = ổn (có/không có cảnh báo). 1 = gửi thất bại (CHƯA ghi state ⇒ tối mai thử lại). 2 = không có file vị thế. 3 = đã gửi nhưng VỊ THẾ CÓ THỂ CŨ (file active_nav cũ hơn phiên trước / thiếu account live).
  if [ "$_ra_rc" -ne 0 ]; then
    [ "$_ra_rc" = "124" ] && _ra_why="treo quá ${RIGHTS_ALERT_TIMEOUT_S:-120}s (timeout); " || _ra_why=""
    "$ROOT/bin/notify_thread.sh" "🟡 RIGHTS ALERT WARN ($TODAY $NOW_ICT): rights_issue_alert rc=$_ra_rc — ${_ra_why}$(echo "$_ra_out" | tail -2 | tr '\n' ' ' | cut -c1-300). rc=3 = đã chạy xong (nếu có quyền mua thì tin đã gửi) nhưng VỊ THẾ CÓ THỂ CŨ (active_nav cũ/thiếu account) — tự kiểm vị thế trên DNSE; rc khác: quyền mua có thể CHƯA được cảnh báo — tự kiểm tav2_bq.corporate_action." "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED+1))
  fi
fi

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

# [pipeline-1] GIỮ nguyên văn stdout của CHÍNH lượt publish này (dòng `[get_gated_state] …` cổng
# tự in) làm bằng chứng cho bước kiểm nguồn cổng ngay dưới: ghi ra FILE THƯỜNG rồi `cat` lại.
# CỐ Ý KHÔNG dùng pipe (`| tee`, `> >(tee …)`): pipe bắt chuỗi 19:00 chờ MỌI tiến trình con cháu
# của publisher còn giữ stdout (publisher → notify.sh → notify_discord.sh → curl; subprocess
# timeout chỉ kill notify.sh, curl mồ côi vẫn giữ đầu ghi) — arch-review 2026-10-12 tái hiện treo.
# File thường không có đầu đọc nào phải chờ EOF. mktemp hỏng ⇒ chạy trần y như trước khi có bước
# kiểm. stderr của publisher KHÔNG đi qua file (ra thẳng như cũ).
if GATE_PUB_OUT="$(mktemp)"; then
  trap '[ "$GATE_PUB_OUT" = /dev/null ] || rm -f "$GATE_PUB_OUT"' EXIT   # cron bị kill giữa chừng không để rác /tmp
  _run_pipeline "[pipeline-1] publish_gated_state"      deploy_golive_dt5g_v4/publish_gated_state.py > "$GATE_PUB_OUT"
  cat "$GATE_PUB_OUT"
else
  GATE_PUB_OUT=/dev/null
  _run_pipeline "[pipeline-1] publish_gated_state"      deploy_golive_dt5g_v4/publish_gated_state.py
fi
# --- GATE-SOURCE check (retro 2026-10-11 Pattern I, user duyệt 2026-10-12 11:01 ICT) ----------
# Bản publish VỪA XONG là bản DollarBill đọc để lập plan T+1. Nguồn khác DT5G_macro (DT4_only /
# DT4_STALE / giá trị lạ / thiếu trường / file hỏng) ⇒ báo NGAY: 1 tin Trading Daily + 1 bus
# error + bằng chứng cho dòng ⚠️ trong báo cáo plan 21:00 (send_plan_report.sh) — trước đây chỉ
# check 13 của ops_health_check.sh kêu lúc 08:20 sáng hôm sau, SAU khi plan đã duyệt.
# CHỈ CẢNH BÁO, KHÔNG CHẶN (DT4_only là fail-closed đúng thiết kế; chặn hay không là quyết định
# của user): không đụng FAILED, không exit. Nguồn DT5G_macro ⇒ gate_source_check.py không in,
# không ghi, không gửi gì. Đặt Ở ĐÂY chứ không ở khối publisher-evidence phía trên: khối đó đọc
# bản publish 18:3x của daily_refresh step [12], bản mà [pipeline-1] vừa GHI ĐÈ.
# Lượt publish không ghi file state ⇒ helper tự bỏ qua, _assert_fresh_artifact bên dưới xử.
python3 "$ROOT/bin/gate_source_check.py" --workdir "$WORKDIR" --publish-log "$GATE_PUB_OUT" \
  --since-epoch "$PIPELINE_START_EPOCH" --alert \
  || echo "  [WARN] gate_source_check.py thoát rc=$? — KHÔNG kiểm được nguồn cổng lượt publish này, không chặn pipeline; kiểm tay trường source trong deploy_golive_dt5g_v4/golive_state_today.json"
[ "$GATE_PUB_OUT" = /dev/null ] || rm -f "$GATE_PUB_OUT"

# [pipeline-1a] gap-fill universe_pit/_quality cho các phiên THIẾU trước hôm nay (WARN-only, 2026-10-15).
# Sự cố 2026-10-15: phiên 14/10 không được build (chuỗi hôm đó bị chặn) ⇒ golive_recommend_v23
# assert_universe_covers dừng ⇒ DollarBill không lập plan T+1. Cổng đó ĐÚNG và giữ nguyên; bước
# này chỉ lấp chỗ thiếu bằng chính builder (cùng B8, append-only). Lỗi/quá MAX_GAPS ⇒ chỉ cảnh báo,
# vì cổng thật nằm ở golive (chặn nếu panel vẫn thiếu phiên). Chạy TRƯỚC 1b để thứ tự phiên tăng dần.
echo; echo "--- [pipeline-1a] universe gap-fill (< $TODAY) ---"
_gap_out="$(timeout "${UNIVERSE_GAP_FILL_TIMEOUT_S:-900}" $PY mike/bin/universe_gap_fill.py --today "$TODAY" 2>&1)"
_gap_rc=$?
echo "$_gap_out"
if [ "$_gap_rc" -ne 0 ]; then
  _gap_why="$(echo "$_gap_out" | grep -E '✗|Traceback|Error' | tail -2 | tr '\n' ' ')"
  [ "$_gap_rc" -eq 124 ] && _gap_why="timeout ${UNIVERSE_GAP_FILL_TIMEOUT_S:-900}s (bị kill; an toàn vì job_id tiền định)"
  echo "  [WARN exit $_gap_rc] [pipeline-1a] universe gap-fill — tiếp tục; golive sẽ chặn nếu panel còn thiếu phiên"
  "$ROOT/bin/notify_thread.sh" "🟡 UNIVERSE GAP-FILL WARN ($TODAY $NOW_ICT): lấp phiên thiếu của universe_pit exit $_gap_rc — ${_gap_why:-không có dòng lỗi, xem mike/logs/bq_freshness.log}. Pipeline vẫn chạy; golive_recommend_v23 sẽ dừng nếu panel còn thiếu phiên." "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
fi

# [pipeline-1b] build universe_pit — BLOCK on real fail.
# build_universe_pit.py exit 1 cả khi: (a) fail thật, (b) B8_DUPLICATE (data đã có = idempotent).
# Phân biệt bằng BQ count: n>0 sau exit≠0 → idempotent OK; n=0 → fail thật → BLOCK.
# Thứ tự bắt buộc: ticker FRESH (đã BLOCK ở trên) → build universe_pit → build quality → golive_recommend_v23.
# (Taylor_20260722_100814: golive_recommend_v23 crash vì assert_universe_covers() raise RuntimeError khi thiếu 1 phiên)
echo; echo "--- [pipeline-1b] build_universe_pit ($TODAY) ---"
if $PY mike/bin/build_universe_pit.py --date "$TODAY"; then
  echo "  [ok] [pipeline-1b] build_universe_pit"
else
  _pit_n=$(bq query --use_legacy_sql=false --project_id="$PROJECT" --format=csv --quiet \
    "SELECT COUNT(*) FROM \`${PROJECT}.tav2_mike.universe_pit\` WHERE time='$TODAY'" \
    2>/dev/null | tail -1 | tr -d '[:space:]')
  if [ "${_pit_n:-0}" -gt 0 ] 2>/dev/null; then
    echo "  [ok-skip] [pipeline-1b] build_universe_pit — data đã có từ trước (${_pit_n} rows, idempotent)"
  else
    _pit_err="⛔ BUILD FAIL $TODAY $NOW_ICT — build_universe_pit.py exit≠0 + universe_pit[$TODAY] rỗng → golive_recommend_v23 sẽ crash (assert_universe_covers). DollarBill bị BLOCK. Check mike/logs/bq_freshness.log"
    "$ROOT/bin/notify.sh" "$_pit_err" 2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "$_pit_err" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    echo "=== FAILED (build_universe_pit — universe_pit[$TODAY] rỗng) — DollarBill KHÔNG được dispatch ==="
    exit 1
  fi
fi

# [pipeline-1c] build universe_pit_quality — BLOCK on fail.
# Phụ thuộc: universe_pit[$TODAY] đã có (bước trên). SKIP_EXISTING → exit 0 (idempotent đúng).
echo; echo "--- [pipeline-1c] build_universe_pit_quality ($TODAY) ---"
if $PY mike/bin/build_universe_pit_quality.py --date "$TODAY"; then
  echo "  [ok] [pipeline-1c] build_universe_pit_quality"
else
  _pq_err="⛔ BUILD FAIL $TODAY $NOW_ICT — build_universe_pit_quality.py exit≠0 → universe_pit_quality[$TODAY] thiếu → golive_recommend_v23/custom30V bị ảnh hưởng. DollarBill bị BLOCK. Check mike/logs/bq_freshness.log"
  "$ROOT/bin/notify.sh" "$_pq_err" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$_pq_err" "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
  echo "=== FAILED (build_universe_pit_quality) — DollarBill KHÔNG được dispatch ==="
  exit 1
fi

# [pipeline-1d] làm mới data/earnings_surprise_data.pkl từ BQ SỐNG ngay trước golive (audit BCTC Q3
# finding L1; user duyệt 2026-10-13, job Taylor_20261013_125149). golive lấy sự kiện LAG mới từ pkl
# này, mà bản 15:30 (refresh_lagged_caches.py [3]) đọc qua BQ_LOCAL_CACHE = cache sync 23:45 ĐÊM
# TRƯỚC ⇒ BCTC ingest ~16:36 hôm nay chỉ tới golive ở 19:00 NGÀY MAI (đo 10-13: pkl 15:30 = 58.233
# dòng/max 08-21 = y hệt parquet cache; BQ sống đã có KBC 2026Q3). Bước này bỏ hẳn phiên trễ đó.
# WARN-only: lỗi/timeout/dữ liệu đáng ngờ ⇒ script GIỮ pkl 15:30 (ghi nguyên tử, không bao giờ để
# pkl nửa vời) và golive vẫn chạy như trước khi có bước này. Đo thật 10-13: ~14-15s/lượt (3 lượt),
# RSS ~316MB; timeout 90s. CỐ Ý không dùng _run_pipeline để phân biệt được timeout (rc=124) và
# đẩy WARN lên Discord — hỏng ở đây nghĩa là LAG lặng lẽ quay về trễ 1 phiên giữa mùa BCTC.
# Probe lag-pkl ở trên đo pkl TRƯỚC bước này ⇒ vẫn canh độc lập đường làm mới 15:30.
LAG_PKL_REFRESH_TIMEOUT_S="${LAG_PKL_REFRESH_TIMEOUT_S:-90}"   # env override CHỈ cho selfcheck
echo; echo "--- [pipeline-1d] refresh_earnings_surprise_pkl (BQ sống → pkl LAG) ---"
_pkl_t0="$(date +%s)"
if _pkl_out="$(timeout "$LAG_PKL_REFRESH_TIMEOUT_S" $PY refresh_earnings_surprise_pkl.py 2>&1)"; then
  echo "$_pkl_out" | tail -3
  echo "  [ok] [pipeline-1d] refresh_earnings_surprise_pkl ($(( $(date +%s) - _pkl_t0 ))s)"
else
  _pkl_rc=$?
  echo "$_pkl_out" | tail -5
  _pkl_why="$(echo "$_pkl_out" | tail -1)"
  [ "$_pkl_rc" -eq 124 ] && _pkl_why="timeout ${LAG_PKL_REFRESH_TIMEOUT_S}s (bị kill; file tạm mồ côi sẽ được dọn ở lượt sau)"
  echo "  [WARN exit $_pkl_rc] [pipeline-1d] refresh_earnings_surprise_pkl — GIỮ pkl 15:30, tiếp tục pipeline ($(( $(date +%s) - _pkl_t0 ))s)"
  "$ROOT/bin/notify_thread.sh" "🟡 LAG PKL REFRESH WARN ($TODAY $NOW_ICT): bước làm mới earnings_surprise_data.pkl từ BQ sống trước golive KHÔNG xong (exit $_pkl_rc) — golive vẫn chạy trên pkl 15:30 (cache đêm trước), tức BCTC ingest hôm nay sẽ tới LAG trễ 1 phiên như trước 10-13. Lý do thật: ${_pkl_why:-<không có output>}. Không chặn plan." "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
fi

_run_pipeline "[pipeline-2] golive_recommend_v23"     deploy_golive_dt5g_v4/golive_recommend_v23.py

# Sổ append-only các ứng viên LAG bị loại ở tầng tín hiệu (Taylor_20260803_035250 việc 3).
# CỐ Ý không dùng _run_pipeline: đây KHÔNG phải bước sinh artifact mà DollarBill đọc, chỉ là
# theo dõi — không được đếm vào WARN pipeline, và `|| true` để tuyệt đối không chặn chuỗi lập
# plan T+1 dù có hỏng. Phải chạy NGAY SAU pipeline-2 vì nó đọc data/golive_v23_status.json,
# file bị GHI ĐÈ mỗi lần golive chạy (không có lịch sử — đó chính là lỗ hổng nó vá).
# Lý do tồn tại + mốc rà soát: mike/kb/projects/lag-adv-filter-tracking.md
(cd "$WORKDIR" && python3 lag_liq_ledger.py) || true

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

# [pipeline-3b] gói DD LAG trước plan (user duyệt 2026-10-21 23:28 ICT; design Taylor_20261021_151302,
# arch-review vòng 1+2) — WARN-only, KHÔNG chặn DollarBill: thiếu gói ⇒ cổng coi là NO_PACK ⇒ mã LAG đứng
# NGOÀI plan (fail-closed sẵn ở lag_plan_consistency_check). CHỈ chạy vòng 19:00 T2-T6 của cron:
#  · MORNING mode (vòng CN `sunday_plan_round.sh` dùng morning+force, chạy tay buổi sáng) và T7/CN BỎ QUA —
#    anomaly_scan chỉ chạy T2-T6 08:20 ⇒ file anomaly cũ ⇒ ANOMALY_NA hàng loạt ⇒ gói CLEARED hôm trước bị
#    ghi đè thành FLAG và ack thành ACK_STALE (kb/ops_runbook.md § Cổng DD trước plan LAG, arch-review vòng 2).
#    Gói thứ Sáu còn hiệu lực cho plan thứ Hai (PACK_ASOF_MAX_DAYS=7).
_dd_dow="$(TZ='Asia/Ho_Chi_Minh' date +%u)"
if [ "${MORNING:-0}" = "1" ] || [ "$_dd_dow" -ge 6 ]; then
  echo; echo "--- [pipeline-3b] lag_dd_pack: BỎ QUA (morning mode hoặc T7/CN) — gói DD đã có giữ nguyên ---"
else
  echo; echo "--- [pipeline-3b] lag_dd_pack ---"
  _dd_out="$(timeout "${LAG_DD_PACK_TIMEOUT_S:-420}" python3 "$ROOT/bin/lag_dd_pack.py" --notify 2>&1)"; _dd_rc=$?
  echo "$_dd_out" | tail -20
  # rc 0 = có gói, 2 = có mã FLAG (bình thường). Khác ⇒ cảnh báo, KHÔNG dừng chuỗi.
  if [ "$_dd_rc" -ne 0 ] && [ "$_dd_rc" -ne 2 ]; then
    [ "$_dd_rc" = "124" ] && _dd_why="treo quá ${LAG_DD_PACK_TIMEOUT_S:-420}s (timeout); " || _dd_why=""
    "$ROOT/bin/notify_thread.sh" "🟡 LAG DD PACK WARN ($TODAY $NOW_ICT): lag_dd_pack rc=$_dd_rc — ${_dd_why}$(echo "$_dd_out" | tail -2 | tr '\n' ' ' | cut -c1-300). Mã LAG không có gói sẽ ĐỨNG NGOÀI plan." "$DISCORD_STALE_CHANNEL" 2>/dev/null || true
    WARNED=$((WARNED+1))
  fi
fi


# [pipeline-4] dispatch DollarBill lập plan T+1 — lặp qua MỌI account live (enabled=true,
# mode=live, broker=dnse trong secrets/trading_bot_accounts.json), không hardcode SpaceX —
# thêm account mới vào file đó là tự động có plan T+1, không cần sửa gì ở đây. Xem
# kb/account_onboarding_runbook.md.
LIVE_LABELS="$(cd "$WORKDIR" && python3 -c "from trading_bot.config import live_dnse_labels; print(' '.join(live_dnse_labels()))")"
# Phí/chiều cho prompt DollarBill — đọc từ hằng số đo thật (aria-F1 CONFIRMED 2026-09-13), không
# hardcode lại. Import hỏng ⇒ in lỗi thật và trỏ DollarBill tới file hằng số thay vì bịa một con số.
if _fee_out="$(cd "$ROOT/bin" 2>&1 && python3 -c 'from dnse_fee_rates import FEE_RATE_BUY_PCT as f; print(f"{f:g}")' 2>&1)"; then
  FEE_NOTE="${_fee_out}%/chiều (bin/dnse_fee_rates.py)"
else
  echo "  [WARN] không đọc được bin/dnse_fee_rates.py — Lỗi thật: $_fee_out"
  FEE_NOTE="theo FEE_RATE_BUY_PCT trong mike/bin/dnse_fee_rates.py"
fi

MORNING_NOTE=""
if [ "${MORNING:-0}" = "1" ]; then
  MORNING_NOTE=" ⚠️ CHẠY TAY BUỔI SÁNG (MIKE_MORNING_RUN=1): dữ liệu/DT5G/recommend là của PHIÊN $TODAY (không phải ngày lịch ${CAL_TODAY}); plan này dành cho CHÍNH ngày $NEXT_TRADING_DAY. ${MIKE_MORNING_NOTE_TAIL:-BẮT BUỘC đặt requires_user_approval=true cho mọi lệnh và nói rõ trong summary rằng đây là plan chạy tay buổi sáng cần user duyệt trước 08:45 ICT; chuỗi inject lệnh thoát theo thời gian (auto_exit_inject) và gửi plan có thể CHƯA chạy cho ngày này.}"
fi
for ACCT in $LIVE_LABELS; do
  echo; echo "--- [pipeline-4] dispatch DollarBill lập plan T+1 cho $ACCT ---"
  # MORNING-SKIP-BEGIN (arch-review 2026-10-15 B2): morning mode KHÔNG ghi đè plan đích đã tồn tại
  # (có thể đã duyệt/đang chạy; run_bot 13:00 resume đọc file này). Ép: MIKE_MORNING_FORCE=1.
  if [ "${MORNING:-0}" = "1" ] && [ -e "$WORKDIR/data/trade_plans/plan_${ACCT}_${NEXT_TRADING_DAY}.json" ] \
     && [ "${MIKE_MORNING_FORCE:-0}" != "1" ]; then
    echo "  [SKIP-MORNING] plan_${ACCT}_${NEXT_TRADING_DAY}.json ĐÃ TỒN TẠI — không ghi đè (ép: MIKE_MORNING_FORCE=1)"
    continue
  fi
  # MORNING-SKIP-END
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
  # EGG_NOTE — VÔ ĐIỀU KIỆN cho MỌI account (fix bất đối xứng 2026-08-20, RCA
  # research/plan_pipeline_3loi_rca_20260820.md lỗi #2). Trước đây chỉ account có
  # excluded_tickers/offbook mới được trỏ tới compute_active_nav.py (nơi lộ egg.totalValue),
  # nên ZaloPay 'thấy' egg và mua VPI trong khi SpaceX 'không thấy' và ghi 'thiếu tiền' —
  # hai account áp cùng luật (context_planning_mini.md §egg.totalValue) ra hai kết quả khác nhau
  # CHỈ vì prompt khác nhau. egg.totalValue là field balances API LIVE cho MỌI account
  # (live từ 2026-08-18), không liên quan gì tới excluded_tickers/offbook.
  EGG_NOTE=" TRỨNG VÀNG (egg.totalValue) — BẮT BUỘC KIỂM TRA cho tài khoản này TRƯỚC KHI kết luận bất kỳ mã nào 'thiếu tiền/không đủ tiền/sức mua ~0': chạy \`bin/compute_active_nav.py --account $ACCT\` và đọc dòng 'Trứng vàng'. egg.totalValue là vốn CHỦ SỞ HỮU THẬT (đã cộng vào NAV/active_nav) nhưng KHÔNG nằm trong availableCash/ppse.pp0Buy vì cần lệnh RÚT (redeem), tiền về T+1. Quy tắc diễn đạt (không được vi phạm): nếu 1 mã bị HOLD/hoãn vì availableCash thấp NHƯNG egg đủ bù phần thiếu → TUYỆT ĐỐI KHÔNG viết 'tài khoản thiếu tiền/không đủ tiền'. Viết đúng: 'availableCash tức thời thiếu Xđ NHƯNG egg còn Yđ — nếu muốn mua cần rút egg đêm nay/sáng mai, nếu không gate P0 sẽ tự HOLD (đúng thiết kế)'. ĐỪNG tự ý đề xuất rút egg thay user — chỉ NÊU RÕ lựa chọn đang có. Đây KHÔNG phải cho phép mua: quyết định mua/hoãn tuân theo signal_holds (mục dưới) và ranh giới user, egg chỉ để diễn đạt LÝ DO cho đúng."
  # CAPIT (gated-overflow bear-washout) capital-source note — user quyết định 2026-07-20
  # sau khi Taylor audit readiness (job Taylor_20260720_074025) phát hiện mâu thuẫn công
  # thức vốn (MD "size × free cash" vs paper code "NAV × capit_size", chênh ~100x) và
  # free-cash luôn ≈0 ở NEUTRAL parking. User chốt: NAV × capit_size ĐÚNG ý đồ, nguồn vốn
  # = user tự rút Trứng vàng trong ngày khi CAPIT kích hoạt.
  # Gate note = `capit_signal_today OR capit_episode_open` (2026-07-31): cờ tín hiệu là điều kiện
  # CỦA NGÀY CHẠY, tắt ngay khi breadth rớt dưới gate — trong khi vị thế THẬT vẫn đang giữ. Chỉ
  # gate theo cờ tín hiệu ⇒ prompt DollarBill im lặng hoàn toàn về CAPIT từ 07-29 dù còn 5 mã ở
  # 2 account (sự cố visibility, job Taylor_20260731_025222).
  CAPIT_STATE="$(cd "$WORKDIR" && python3 -c "
import json
try:
    s = json.load(open('data/golive_v23_status.json'))
    # capit_fired -> capit_signal_today (2026-07-31); fallback cho status ghi trước lần đổi tên.
    if s.get('capit_signal_today', s.get('capit_fired')):
        print('fired')
    elif s.get('capit_episode_open'):
        held = s.get('capit_sessions_held')
        print('holding|%s|%s|%s' % (s.get('capit_episode_entry_date') or '?',
                                    '?' if held is None else held,
                                    ','.join(s.get('capit_episode_basket') or []) or '?'))
    else:
        print('no')
except Exception:
    print('no')
" 2>/dev/null)"
  CAPIT_NOTE=""
  if [ "$CAPIT_STATE" = "fired" ]; then
    CAPIT_NOTE=" ⚠️ CAPIT (bear-washout) ĐÃ KÍCH HOẠT hôm nay (golive_v23_status.json capit_signal_today=true) — book CAPIT xuất hiện trong CSV recommend. Công thức vốn ĐÃ CHỐT (user 2026-07-20): size deploy = NAV_book_LAG × capit_size (KHÔNG PHẢI 'size × tiền mặt rảnh' — đó là công thức cũ trong MD, đã sai). Nguồn vốn: user sẽ TỰ RÚT Trứng vàng trong ngày để có tiền mặt sẵn sàng sáng mai — ghi rõ trong plan note số tiền cần rút (nếu cash thật hiện có không đủ), ĐỪNG tự shrink size xuống theo cash hiện tại. Basket CAPIT: hold 60 phiên, stop-exempt, slot-exempt (không tính vào slot BAL/LAG thường) — giữ nguyên các cờ này trong plan."
  elif [ "${CAPIT_STATE%%|*}" = "holding" ]; then
    CAPIT_ENTRY="$(echo "$CAPIT_STATE" | cut -d'|' -f2)"
    CAPIT_SESS="$(echo "$CAPIT_STATE" | cut -d'|' -f3)"
    CAPIT_BASKET="$(echo "$CAPIT_STATE" | cut -d'|' -f4)"
    CAPIT_NOTE=" 📌 CAPIT (bear-washout) ĐANG GIỮ VỊ THẾ — tín hiệu breadth HÔM NAY đã tắt (capit_signal_today=false) nhưng đó chỉ là điều kiện của RIÊNG ngày chạy, KHÔNG có nghĩa đã thoát: episode vào lệnh ${CAPIT_ENTRY}, đã ${CAPIT_SESS} phiên, rổ gốc ${CAPIT_BASKET} (nguồn: capit_episode_open=true trong golive_v23_status.json + data/capit_episode.json). Trong plan: các mã CAPIT là stop-exempt và slot-exempt (KHÔNG tính vào slot BAL/LAG thường, KHÔNG áp stop -20% của BAL). TUYỆT ĐỐI KHÔNG tự sinh lệnh BÁN để 'dọn' rổ CAPIT hay để 'cân' tỷ trọng — exit CAPIT do NGƯỜI quyết định, hệ thống KHÔNG có luật tự bán CAPIT ở đường live. Nếu bạn thấy lý do phải đụng tới 1 mã CAPIT, ghi rõ đề xuất + lý do trong plan note và để user duyệt, đừng tự đưa vào orders."
  fi
  # HOLDS_NOTE — ranh giới tạm giữ tín hiệu (signal_holds), fix lỗi #3 RCA 2026-08-20.
  # Bơm vào prompt để DollarBill biết không mở lệnh vi phạm; gate deterministic (signal_holds.py
  # --check, gọi trong send_plan_report.sh + bot_execute.py) là lớp chặn cứng độc lập.
  HOLDS_NOTE="$(cd "$ROOT" && python3 bin/signal_holds.py --note 2>/dev/null)"
  # CORP_ACTION_NOTE — cùng nguồn/khuôn với [pipeline-0] ở trên, lọc riêng cho $ACCT (mã account
  # này thực sự đang giữ) để DollarBill không nhầm biến động giá dự kiến (ex-date/AIS) với tín
  # hiệu thị trường khi viết plan/summary.
  CORP_ACTION_NOTE="$(cd "$ROOT" && python3 bin/nav_exdate_forecast.py --note "$ACCT" 2>/dev/null)"
  "$ROOT/bin/dispatch.sh" DollarBill \
    "Lập plan T+1 cho tài khoản $ACCT. Đọc DT5G từ deploy_golive_dt5g_v4/golive_state_today.json và recommend output mới nhất trong data/. Ghi plan vào data/plan_${ACCT}_${NEXT_TRADING_DAY}.json — dùng ĐÚNG NGUYÊN VĂN ngày $NEXT_TRADING_DAY (đã tính sẵn bằng next_trading_day(), bỏ T7/CN/lễ) làm plan_date và tên file, TUYỆT ĐỐI KHÔNG tự suy ra 'ngày mai' bằng cách cộng 1 vào ngày hôm nay (sự cố thật 2026-07-10: dispatch thứ Sáu tự tính '07-11' là ngày mai, nhưng đó là thứ Bảy không phải ngày giao dịch, đúng ra phải là 07-13 thứ Hai). Ngày hôm nay: ${CAL_TODAY:-$TODAY} (ICT).${MORNING_NOTE}${NAV_NOTE}${EGG_NOTE}${CAPIT_NOTE}${HOLDS_NOTE}${CORP_ACTION_NOTE} YÊU CẦU VĂN PHONG (user 2026-07-07): kết thúc final message bằng 3-5 dòng tóm tắt DỄ HIỂU cho người đọc không chuyên — bắt buộc nêu rõ: Account nào · plan ngày nào · hành động chính (HOLD hay mấy lệnh gì) · VÌ SAO 1-2 câu · trạng thái duyệt — vì message này được đăng nguyên văn vào Discord plan channel. Lệnh MUA size bằng tiền bán cùng ngày: trừ phí ${FEE_NOTE} + chừa biên giá, đừng size khít ref price. BẮT BUỘC VỀ GIÁ THAM CHIẾU (user 2026-07-09, tái diễn nhiều lần): mtm_price_ref/ref_price của MỌI mã trong plan phải lấy từ DNSE live quote (dnse_api.py secdef/latest_trade — giá đóng cửa THẬT hôm nay $TODAY) — TUYỆT ĐỐI KHÔNG dùng giá đóng cửa BQ ('ticker'/'ticker_1m' close) làm ref_price, vì BQ cache local chỉ sync đêm 23:45 ICT nên tại giờ bạn chạy (~19:00) BQ cache luôn trễ ít nhất 1 ngày giao dịch — dùng BQ ở đây LUÔN cho ra giá sai/cũ, không phải thỉnh thoảng. Sự cố thật đã xảy ra: plan ZaloPay 07-10 có 2/4 mã (BID, MBB) dùng nhầm 'BQ close 07-08' lệch tới +5.7% so với giá đóng cửa thật 07-09, trong khi 2 mã còn lại dùng đúng DNSE live. Nếu DNSE live quote lỗi/thiếu cho 1 mã nào đó, ghi rõ note 'THIẾU GIÁ LIVE — cần kiểm tra tay' thay vì âm thầm dùng BQ thay thế." \
    --bg 2>/dev/null || echo "  [WARN] dispatch DollarBill cho $ACCT fail — check mike/logs/"
done

echo; echo "=== EOD PIPELINE DONE — $(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT') ==="
