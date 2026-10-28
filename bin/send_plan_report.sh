#!/usr/bin/env bash
# send_plan_report.sh — đọc plan T+1 → gửi summary qua Telegram + Discord
# Schedule: 21:00 ICT trading days (cron: 0 14 * * 1-5) + second-chance 23:00 ICT
# (cron: 0 16 * * 1-5, cờ --second-chance).
#
# Verify ARTIFACT thật (file plan có đúng ngày T+1, đúng schema) — KHÔNG tin vào job
# status của dispatch.sh (job có thể báo "timeout" dù plan đã ghi xong, xem sự cố
# 2026-07-01: DollarBill_20260701_103128 timeout nhưng plan_SpaceX_2026-07-02.json
# hợp lệ). Nếu KHÔNG tìm thấy artifact hợp lệ → ESCALATE thật (bus question event,
# Mike tự đọc ở phiên sau) thay vì chỉ gửi 1 tin Telegram rồi im lặng chờ người phát hiện.
#
# --second-chance (thêm 2026-07-13, sự cố kb/INCIDENTS.md 2026-07-13): plan bị sửa/
# re-dispatch SAU giờ gửi 21:00 (vd DollarBill fix lỗi ngày rồi ghi lại 22:17) trước đây
# KHÔNG bao giờ được gửi lại cho user duyệt — nằm im tới ops_health_check 08:20 sáng hôm
# sau (CRITICAL, còn ~35' trước bot 09:05). Chạy lại lúc 23:00 với cờ này:
#   - lần 21:00 đã gửi thành công VÀ plan không đổi         → NO-OP (không gửi trùng)
#   - lần 21:00 đã gửi nhưng plan ĐÃ THAY ĐỔI nội dung      → gửi lại, ghi rõ "bản cập nhật"
#   - lần 21:00 escalate/fail, giờ file đã có/đúng          → gửi (lần đầu user thấy plan)
#   - vẫn thiếu/sai                                          → escalate lần nữa (final call trong đêm)
# Idempotency: marker state/plan_report_sent/<account>_<T+1 date>.json ghi md5 NỘI DUNG
# plan (đã loại các field approval — user duyệt làm plan file đổi là thay đổi lành tính,
# không được kích re-send). Marker chỉ ghi khi đã gửi OK.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"
[ -f "$WC_ROOT/wc_env.sh" ] && source "$WC_ROOT/wc_env.sh" 2>/dev/null || true

# SEND_PLAN_WORKDIR_OVERRIDE / SEND_PLAN_MARKER_DIR: chỉ dùng cho test/dry-run sandbox
# (wc_env.sh export cứng WORKDIR_8L nên không override được bằng env thường).
WORKDIR="${SEND_PLAN_WORKDIR_OVERRIDE:-${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}}"
MARKER_DIR="${SEND_PLAN_MARKER_DIR:-$ROOT/state/plan_report_sent}"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"   # §16: neo ICT tường minh, không tin TZ host
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"

# --account LABEL — mặc định SpaceX để giữ nguyên hành vi cũ khi gọi không kèm cờ. Cron
# thật gọi qua for_each_live_account.sh (lặp mọi account enabled=live/dnse) — xem
# kb/account_onboarding_runbook.md.
ACCOUNT="SpaceX"
SECOND_CHANCE=0
DRY_RUN=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --account) ACCOUNT="$2"; shift 2 ;;
    --second-chance) SECOND_CHANCE=1; shift ;;
    --dry-run) DRY_RUN=1; shift ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# Discord: DollarBill trading-plan channel — tách riêng khỏi Trading Daily (2026-07-01,
# user chỉ đạo) để tránh spam các topic khác khi Mike dispatch DollarBill từ bất kỳ đâu.
DISCORD_PLAN_CHANNEL="plan_approval"

EXPECTED_DATE="$(cd "$WORKDIR" && python3 -c "
import datetime as dt
from zoneinfo import ZoneInfo
from trading_bot.vn_market import next_trading_day
print(next_trading_day(dt.datetime.now(ZoneInfo('Asia/Ho_Chi_Minh')).date()))  # §16: neo ICT, không dùng date.today() trần
" 2>/dev/null)"

# Plan file mới nhất theo mtime (Bill ghi vào data/trade_plans/plan_<account>_<date>.json)
PLAN_FILE="$(ls -t "$WORKDIR"/data/trade_plans/plan_${ACCOUNT}_*.json 2>/dev/null | head -1)"

# --- signal_holds gate (tầng chặn cứng #1, fix lỗi #3 RCA 2026-08-20) ---
# Chạy TRƯỚC khi tính hash + gửi: nếu DollarBill (dù đã có HOLDS_NOTE trong prompt) vẫn để lọt
# 1 order vi phạm hold vào orders[], gate này gỡ nó sang deferred_orders (chưa duyệt) hoặc
# escalate (đã duyệt). Không phụ thuộc LLM nhớ. Fail-safe: gỡ lệnh = chiều an toàn.
if [ -n "$PLAN_FILE" ] && [ -f "$PLAN_FILE" ]; then
  HOLD_OUT="$(cd "$ROOT" && python3 bin/signal_holds.py --enforce "$PLAN_FILE" 2>&1)"
  HOLD_RC=$?
  if [ "$HOLD_RC" = "3" ]; then
    echo "[send_plan_report] signal_holds: ĐÃ GỠ order vi phạm hold khỏi plan $ACCOUNT (sang deferred_orders). Chi tiết: $HOLD_OUT"
    "$ROOT/bin/notify_thread.sh" "$(TZ='Asia/Ho_Chi_Minh' date '+%H:%M %d/%m/%Y')
⚠️ **signal_holds gate đã kích hoạt** — plan $ACCOUNT $EXPECTED_DATE có order vi phạm ranh giới tạm giữ tín hiệu, đã tự GỠ sang deferred_orders trước khi gửi. Nghĩa là tầng sinh plan (DollarBill) để lọt — cần rà lại vì sao. Plan gửi cho anh là bản ĐÃ SỬA." plan_approval >/dev/null 2>&1 || true
  elif [ "$HOLD_RC" = "2" ]; then
    echo "[send_plan_report] signal_holds: plan ĐÃ DUYỆT nhưng chứa order vi phạm hold — KHÔNG tự sửa, escalate. $HOLD_OUT"
    "$ROOT/bin/notify_thread.sh" "$(TZ='Asia/Ho_Chi_Minh' date '+%H:%M %d/%m/%Y')
🛑 **signal_holds gate — CẦN NGƯỜI**: plan $ACCOUNT $EXPECTED_DATE ĐÃ DUYỆT nhưng chứa order vi phạm ranh giới tạm giữ tín hiệu. Gate KHÔNG tự sửa plan đã ký. bot_execute sẽ chặn order này khi chạy, nhưng anh nên kiểm tra lại. $HOLD_OUT" plan_approval >/dev/null 2>&1 || true
  elif [ "$HOLD_RC" != "0" ]; then
    # RC ∉ {0,2,3} = gate CRASH (traceback/import lỗi), KHÔNG được coi là 'sạch' âm thầm
    # (arch-reviewer fail_silent 2026-08-20). bot_execute vẫn chạy gate độc lập lúc 09:05 (backstop),
    # nhưng phải báo to ở đây thay vì nuốt lỗi.
    echo "[send_plan_report] ⚠⚠ signal_holds gate CRASH rc=$HOLD_RC — KHÔNG xác minh được plan có vi phạm hold hay không. $HOLD_OUT"
    "$ROOT/bin/notify_thread.sh" "$(TZ='Asia/Ho_Chi_Minh' date '+%H:%M %d/%m/%Y')
⚠️ **signal_holds gate LỖI (rc=$HOLD_RC)** khi kiểm plan $ACCOUNT $EXPECTED_DATE — KHÔNG xác minh được vi phạm ranh giới tạm giữ. bot_execute sẽ chạy lại gate lúc 09:05 (backstop độc lập), nhưng cần rà signal_holds.py. $HOLD_OUT" plan_approval >/dev/null 2>&1 || true
  fi
fi

# md5 NỘI DUNG plan, loại các field approval (approved_by/mafee_authorized/approv*/mafee_*/
# requires_user_approval) — duyệt plan ghi thêm field vào file là thay đổi lành tính,
# second-chance không được coi đó là "plan đổi" mà gửi lại lúc 23:00.
plan_content_hash() {
  local f="$1"
  [ -n "$f" ] && [ -f "$f" ] || { echo ""; return; }
  python3 - "$f" << 'PYHASH' 2>/dev/null || echo ""
import sys, json, hashlib
with open(sys.argv[1]) as fh:
    plan = json.load(fh)
if isinstance(plan, dict):
    plan = {k: v for k, v in plan.items()
            if not (k.startswith("approv") or k.startswith("mafee") or k == "requires_user_approval")}
print(hashlib.md5(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest())
PYHASH
}

MARKER_FILE=""
[ -n "$EXPECTED_DATE" ] && MARKER_FILE="$MARKER_DIR/${ACCOUNT}_${EXPECTED_DATE}.json"
CUR_HASH="$(plan_content_hash "$PLAN_FILE")"
PLAN_CHANGED_AFTER_SEND=0

if [ "$SECOND_CHANCE" = "1" ] && [ -n "$MARKER_FILE" ] && [ -f "$MARKER_FILE" ]; then
  SENT_HASH="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("content_md5",""))' "$MARKER_FILE" 2>/dev/null || echo "")"
  if [ -n "$CUR_HASH" ] && [ "$CUR_HASH" = "$SENT_HASH" ]; then
    echo "[send_plan_report] second-chance NO-OP — plan $ACCOUNT $EXPECTED_DATE đã gửi thành công trước đó và không đổi (md5 $CUR_HASH) — $NOW_ICT"
    exit 0
  fi
  PLAN_CHANGED_AFTER_SEND=1
fi

# --- Vị thế đổi SAU khi lập plan (rủi ro Q5, HƯỚNG NHẸ — user duyệt 2026-10-04): CHỈ CỜ, KHÔNG chặn.
# plan_position_drift_check.py đọc DNSE sống, so với bản đọc đầu của plan (~19:03) và mốc phiên —
# credit corp-action muộn (BID 08-14 lô thứ hai 20:15) ⇒ khối ⚠️ riêng; không đổi ⇒ đúng 1 dòng ✅.
# FAIL-SOFT nhưng KHÔNG im lặng: script lỗi/treo/in rỗng ⇒ dòng "KHÔNG KIỂM ĐƯỢC" kèm lỗi thật
# (§29), report vẫn gửi. Sandbox selfcheck (SEND_PLAN_WORKDIR_OVERRIDE) không chạm DNSE thật trừ khi
# test tự cấp SEND_PLAN_DRIFT_CMD (đường dẫn 1 file thực thi giả).
DRIFT_BLOCK=""
DRIFT_CMD=""
if [ -n "${SEND_PLAN_DRIFT_CMD:-}" ]; then
  DRIFT_CMD="$SEND_PLAN_DRIFT_CMD"
elif [ -z "${SEND_PLAN_WORKDIR_OVERRIDE:-}" ]; then
  DRIFT_CMD="$ROOT/bin/plan_position_drift_check.py"
fi
if [ -n "$DRIFT_CMD" ]; then
  DRIFT_ARGS=(--account "$ACCOUNT" --report-block)
  [ "$DRY_RUN" = "1" ] && DRIFT_ARGS+=(--no-bus --no-state)
  DRIFT_ERR="$(mktemp)"
  DRIFT_TMO="${SEND_PLAN_DRIFT_TIMEOUT:-120}"
  DRIFT_BLOCK="$(timeout "$DRIFT_TMO" python3 "$DRIFT_CMD" "${DRIFT_ARGS[@]}" 2>"$DRIFT_ERR")"
  DRIFT_RC=$?
  # stderr của bước kiểm (bus/state/sổ lệnh lỗi, log kết nối DNSE) LUÔN vào log của job này.
  sed 's/^/[drift] /' "$DRIFT_ERR" >&2
  if { [ "$DRIFT_RC" -ne 0 ] && [ "$DRIFT_RC" -ne 2 ]; } || [ -z "$DRIFT_BLOCK" ]; then
    _derr="$(tail -n 2 "$DRIFT_ERR" | tr '\n' ' ' | cut -c1-200)"
    [ "$DRIFT_RC" = "124" ] && _derr="treo quá ${DRIFT_TMO}s (timeout) ${_derr}"
    DRIFT_BLOCK="⚠️ **Vị thế sau plan ($ACCOUNT): KHÔNG KIỂM ĐƯỢC** — plan_position_drift_check rc=$DRIFT_RC, ${DRIFT_BLOCK:+in: $(echo "$DRIFT_BLOCK" | head -1 | cut -c1-120), }lỗi: ${_derr:-<không có stderr>}. Tự xem vị thế DNSE các mã có sự kiện quyền trước khi duyệt."
  fi
  rm -f "$DRIFT_ERR"
fi
export DRIFT_BLOCK

# --- Lịch vào lệnh + DD book LAG khớp CODE (job Taylor_20261021_114050, user duyệt 21/10): CHỈ CỜ,
# KHÔNG chặn gửi. lag_plan_calendar_check.py so lag_analysis/orders LAG của ĐÚNG file plan sắp gửi
# (và plan account kia cùng ngày nếu có) với filter_lag_entry_window.py chạy offline ⇒ ✅ 1 dòng, hoặc ⛔ kèm MÃ
# nguyên nhân (ca 24-27/07: entry thứ Bảy, 2 account 2 lịch). rc 0/1/3 đều in khối; rc khác/rỗng ⇒
# "KHÔNG KIỂM ĐƯỢC" kèm lỗi thật (§29). Sandbox selfcheck không chạy trừ khi cấp SEND_PLAN_LAGCAL_CMD.
LAGCAL_BLOCK=""
LAGCAL_CMD=""
if [ -n "${SEND_PLAN_LAGCAL_CMD:-}" ]; then
  LAGCAL_CMD="$SEND_PLAN_LAGCAL_CMD"
elif [ -z "${SEND_PLAN_WORKDIR_OVERRIDE:-}" ]; then
  LAGCAL_CMD="$ROOT/bin/lag_plan_calendar_check.py"
fi
if [ -n "$LAGCAL_CMD" ] && [ -n "$PLAN_FILE" ]; then
  LAGCAL_ERR="$(mktemp)"
  LAGCAL_BLOCK="$(timeout "${SEND_PLAN_LAGCAL_TIMEOUT:-60}" python3 "$LAGCAL_CMD" --plan "$PLAN_FILE" \
    --report-block 2>"$LAGCAL_ERR")"
  LAGCAL_RC=$?
  sed 's/^/[lagcal] /' "$LAGCAL_ERR" >&2
  if { [ "$LAGCAL_RC" -ne 0 ] && [ "$LAGCAL_RC" -ne 1 ] && [ "$LAGCAL_RC" -ne 3 ]; } || [ -z "$LAGCAL_BLOCK" ]; then
    _lerr="$(tail -n 2 "$LAGCAL_ERR" | tr '\n' ' ' | cut -c1-200)"
    [ "$LAGCAL_RC" = "124" ] && _lerr="treo quá ${SEND_PLAN_LAGCAL_TIMEOUT:-60}s (timeout) ${_lerr}"
    LAGCAL_BLOCK="⚠️ **Lịch LAG ($ACCOUNT): KHÔNG KIỂM ĐƯỢC** — lag_plan_calendar_check rc=$LAGCAL_RC, lỗi: ${_lerr:-<không có stderr>}. Tự đối chiếu entry_date với filter_lag_entry_window.py trước khi duyệt."
  fi
  rm -f "$LAGCAL_ERR"
fi
export LAGCAL_BLOCK

# --- Cổng nhất quán LAG + cảnh báo ứng viên LAG hợp lệ bị hoãn đúng phiên chuẩn (user duyệt
# 2026-10-21, Taylor_20261021_102832 REPORT §5.2/5.3). CHỈ CẢNH BÁO (WARN + bus + Discord Trading
# Daily, idempotent theo plan_date) — KHÔNG chặn gửi plan: chặn 21:00 làm user không thấy plan để
# duyệt, tệ hơn gửi kèm khối đỏ. FAIL-SOFT nhưng không im lặng: script lỗi ⇒ dòng "KHÔNG KIỂM ĐƯỢC".
# Sandbox selfcheck (SEND_PLAN_WORKDIR_OVERRIDE) không chạy trừ khi test tự cấp SEND_PLAN_LAGCHK_CMD.
LAGCHK_BLOCK=""
LAGCHK_CMD=""
if [ -n "${SEND_PLAN_LAGCHK_CMD:-}" ]; then
  LAGCHK_CMD="$SEND_PLAN_LAGCHK_CMD"
elif [ -z "${SEND_PLAN_WORKDIR_OVERRIDE:-}" ]; then
  LAGCHK_CMD="$ROOT/bin/lag_plan_consistency_check.py"
fi
if [ -n "$LAGCHK_CMD" ] && [ -n "$PLAN_FILE" ] && [ -f "$PLAN_FILE" ]; then
  LAGCHK_ARGS=(--account "$ACCOUNT" --plan-file "$PLAN_FILE" --report-block)
  [ "$DRY_RUN" = "1" ] && LAGCHK_ARGS+=(--dry-run)
  LAGCHK_ERR="$(mktemp)"
  LAGCHK_BLOCK="$(timeout "${SEND_PLAN_LAGCHK_TIMEOUT:-150}" python3 "$LAGCHK_CMD" "${LAGCHK_ARGS[@]}" 2>"$LAGCHK_ERR")"
  LAGCHK_RC=$?
  sed 's/^/[lagchk] /' "$LAGCHK_ERR" >&2
  if { [ "$LAGCHK_RC" -ne 0 ] && [ "$LAGCHK_RC" -ne 2 ]; } || [ -z "$LAGCHK_BLOCK" ]; then
    _lerr="$(tail -n 2 "$LAGCHK_ERR" | tr '\n' ' ' | cut -c1-200)"
    LAGCHK_BLOCK="⚠️ **Cổng nhất quán LAG ($ACCOUNT): KHÔNG KIỂM ĐƯỢC** — rc=$LAGCHK_RC, lỗi: ${_lerr:-<không có stderr>}. Tự đối chiếu lag_analysis với orders[]/deferred_orders[] trước khi duyệt."
  fi
  rm -f "$LAGCHK_ERR"
fi
export LAGCHK_BLOCK

# --- Nowcast KQKD theo hàng hoá cho mã producer trong plan (job Taylor_20261026_095926, user duyệt 26/10).
# DISPLAY-ONLY, CHỈ ZaloPay (account vận hành nội bộ — cùng tiền lệ _hit_details_block() của eod_trading_report.sh;
# SpaceX là báo cáo nhà đầu tư, KHÔNG thêm). FAIL-OPEN tuyệt đối: lỗi/treo/rỗng => không có khối, không chặn gửi,
# không thêm phụ thuộc cho 21:00 (timeout cứng 20s). Sandbox selfcheck không chạy trừ khi cấp SEND_PLAN_NOWCAST_CMD.
NOWCAST_BLOCK=""
NOWCAST_CMD=""
if [ "$ACCOUNT" = "ZaloPay" ]; then
  if [ -n "${SEND_PLAN_NOWCAST_CMD:-}" ]; then
    NOWCAST_CMD="$SEND_PLAN_NOWCAST_CMD"
  elif [ -z "${SEND_PLAN_WORKDIR_OVERRIDE:-}" ]; then
    NOWCAST_CMD="$ROOT/bin/commodity_nowcast_block.py"
  fi
fi
if [ -n "$NOWCAST_CMD" ] && [ -n "$PLAN_FILE" ] && [ -f "$PLAN_FILE" ]; then
  NOWCAST_ERR="$(mktemp)"
  NOWCAST_BLOCK="$(timeout -k 5 20 python3 "$NOWCAST_CMD" --plan-file "$PLAN_FILE" 2>"$NOWCAST_ERR")" \
    || { echo "[nowcast] rc=$? (124=timeout) -> bỏ khối, báo cáo vẫn gửi" >&2; NOWCAST_BLOCK=""; }
  sed 's/^/[nowcast] /' "$NOWCAST_ERR" >&2
  rm -f "$NOWCAST_ERR"
fi
export NOWCAST_BLOCK

RESULT=$(cd "$WORKDIR" && SEND_PLAN_MIKE_BIN="$ROOT/bin" python3 - "$PLAN_FILE" "$EXPECTED_DATE" "$TODAY" "$NOW_ICT" "$ACCOUNT" << 'PY'
import sys, json, os, re

plan_file, expected_date, today, now_ict, acct = sys.argv[1:6]

def escalate(reason, detail=""):
    print("ESCALATE")
    print(reason)
    print(detail)

if not plan_file:
    escalate("no_plan_file", f"Không có file plan_{acct}_*.json nào trong data/trade_plans/.")
    sys.exit(0)

try:
    with open(plan_file) as f:
        plan = json.load(f)
except Exception as e:
    escalate("plan_unparseable", f"{plan_file}: {e}")
    sys.exit(0)

plan_date = plan.get("plan_date", plan.get("date"))
if expected_date and plan_date != expected_date:
    escalate("plan_date_stale",
              f"File mới nhất ({plan_file}) có plan_date={plan_date!r}, kỳ vọng {expected_date!r} "
              f"(T+1 từ hôm nay {today}). DollarBill có thể chưa chạy hoặc bị lỗi chiều nay.")
    sys.exit(0)

if "orders" not in plan:
    escalate("plan_missing_orders", f"{plan_file}: thiếu field 'orders' — schema không hợp lệ.")
    sys.exit(0)

# --- Valid plan found: render THÂN THIỆN (user feedback 2026-07-07: report cũ "khá khó
# hiểu" — không rõ account nào, không rõ VÌ SAO plan như vậy). Áp cùng văn phong với
# session_announce/heartbeat: account nổi bật, hành động + lý do bằng tiếng người,
# trạng thái duyệt + chuyện gì xảy ra tiếp theo. ---
date   = plan_date or "?"
state  = plan.get("state_name", plan.get("market_state", plan.get("state", "?")))
src    = plan.get("state_source", "")
nav_b  = plan.get("nav_basis") if isinstance(plan.get("nav_basis"), dict) else {}
nav    = (nav_b.get("active_nav_vnd") or nav_b.get("nav_vnd") or nav_b.get("account_nav")
          or plan.get("nav_basis_vnd") or plan.get("nav_estimate"))
# `.get(..., [])` only guards a MISSING key — "orders": null (present, value None) is
# schema-valid per the check above but used to crash the price-gate below (arch-reviewer
# 2026-07-30 found this replaying a synthetic fixture: TypeError -> empty $RESULT -> silent
# no-send that still writes the "sent OK" marker, disarming the 23:00 second-chance).
orders = plan.get("orders") or []
if not isinstance(orders, list):
    escalate("plan_orders_not_list", f"{plan_file}: 'orders' không phải list ({type(orders).__name__}).")
    sys.exit(0)
summary = plan.get("summary", {}) if isinstance(plan.get("summary"), dict) else {}
action  = summary.get("action", "HOLD" if not orders else "TRADE")
reasons = summary.get("reasons") or []
approved = plan.get("approved_by")
requires = plan.get("requires_user_approval", False)

# --- Content-verification gates (Wags audit 2026-07-30, P1 — catches plan ZaloPay 2026-07-10:
# 2/4 orders priced off a stale BQ close, +5.7% off, passed every gate that existed at the time
# because they only check SHAPE (file exists, right date, has 'orders'), never whether the
# numbers inside are actually right. This is the one artifact gate that sits in front of the
# human approver — a shape-correct/content-wrong plan renders identically to a good one, so
# "user approved it" is not an independent check unless the numbers were verified first. ---

# 1c: identity asserts — cheap, catch gross mismatches (wrong account/state baked into a plan).
plan_account = plan.get("account")
if plan_account and plan_account != acct:
    escalate("plan_account_mismatch",
             f"{plan_file}: plan['account']={plan_account!r} nhưng đang gửi cho account "
             f"{acct!r} — plan có thể bị lẫn giữa 2 account.")
    sys.exit(0)

# So TRẠNG THÁI (số nguyên 0-4), KHÔNG so `state_source` (Wags 2026-08-11).
# `state_source` là prose TỰ DO do bên sinh plan viết — cùng một nguồn được ghi ít nhất 2
# cách khác nhau ('DT5G_macro' và 'deploy_golive_dt5g_v4/golive_state_today.json (…qua
# get_gated_state)'), và bản chú thêm provenance ('DT5G_macro (…, published_at …)') so bằng
# `!=` với 'DT5G_macro' luôn ra LỆCH. Kết quả: gate báo động giả, CHẶN việc gửi plan, nên
# user không nhận được plan để duyệt → sáng hôm sau bot từ chối chạy (đã cắn 08-07 và
# 08-10/11: 30 lệnh lỡ phiên). Cùng lớp lỗi với 2026-07-15 MAFEE_NOT_AUTH — check fail cứng
# trên field không có schema thì mọi lần đúng đều thành RED giả; fix đúng là sửa CHECKER cho
# khớp tín hiệu THẬT. `state` là int có nghĩa xác định, đúng thứ "plan sinh từ state cũ"
# muốn bắt: plan dựng trên regime khác regime DT5G hôm nay. Chặt hơn bản cũ chứ không lỏng
# hơn — bản cũ so nhãn nên KHÔNG BAO GIỜ bắt được lệch state thật.
def _as_state_int(v):
    if isinstance(v, bool):
        return None
    if isinstance(v, int):
        return v
    if isinstance(v, str) and v.strip().lstrip("-").isdigit():
        return int(v.strip())
    return None

# Fail-open ĐƯỢC PHÉP, fail-open CÂM thì KHÔNG (arch-review coord-2026-08-11, cùng yêu cầu
# arch-reviewer đặt ra cho gate giá ở dòng ~213: price_verify_note). `plan['state']` là literal
# GÕ TAY ở bên sinh plan (build_plans_*.py) — một bản builder quên field / ghi 'NEUTRAL' là gate
# này chết lặng vĩnh viễn trong khi report render y hệt như đã đối chiếu, tức đổi một RED giả ồn
# ào lấy một GREEN giả câm. Mọi nhánh bỏ qua đều PHẢI để lại dấu vết trong chính report.
STATE_NAMES = {1: "CRISIS", 2: "BEAR", 3: "NEUTRAL", 4: "BULL", 5: "EX-BULL"}
state_verify_note = ""
try:
    with open("deploy_golive_dt5g_v4/golive_state_today.json") as f:
        golive = json.load(f)
    plan_state = _as_state_int(plan.get("state"))
    golive_state = _as_state_int(golive.get("state"))
    # Thiếu/không phải số ở bất kỳ vế nào → BỎ QUA assert, không chặn (fail-open có chủ đích:
    # đây là gate phụ, gate approval ở executor mới là lớp chặn tiền thật) — nhưng NÓI RA.
    # state=-1 là sentinel PROBE (thấy thật ở plan_main_*.json), KHÔNG phải một regime 1-5 —
    # so nó với golive thì LUÔN lệch. Hôm nay main không nằm trong live_dnse_labels() nên chưa
    # cắn, nhưng onboard một account PROBE là gate này thành RED giả chặn plan ngay ngày đầu.
    if plan_state is not None and plan_state < 0:
        state_verify_note = (
            f"⚠️ plan.state={plan_state} (PROBE, không phải regime 1-5) — KHÔNG đối chiếu được "
            f"với DT5G hôm nay (golive.state={golive.get('state')!r}), không chặn plan")
    elif plan_state is None or golive_state is None:
        state_verify_note = (
            f"⚠️ CHƯA đối chiếu được state plan vs DT5G hôm nay (plan.state="
            f"{plan.get('state')!r}, golive.state={golive.get('state')!r} — cần số nguyên ở cả "
            f"hai vế): không chặn plan, người duyệt tự kiểm regime trước khi duyệt")
    elif plan_state != golive_state:
        escalate("plan_state_mismatch",
                 f"{plan_file}: state={plan_state} nhưng golive_state_today.json (nguồn DT5G "
                 f"thật hôm nay, as_of={golive.get('as_of')!r}) nói state={golive_state} — plan "
                 f"có thể được sinh từ state cũ.")
        sys.exit(0)
    else:
        state_verify_note = (
            f"✅ state={plan_state} ({STATE_NAMES.get(plan_state, '?')}) khớp "
            f"golive_state_today.json (as_of={golive.get('as_of')})")
        # Đại lượng được VERIFY (state, int) và đại lượng được HIỂN THỊ cho người duyệt
        # (state_name, chuỗi) là hai literal gõ tay cạnh nhau: state=3/state_name='BULL' qua
        # được gate mà người duyệt vẫn đọc sai regime. Chỉ CẢNH BÁO, không chặn.
        _shown = str(plan.get("state_name") or plan.get("market_state") or "").strip().upper()
        _expect = STATE_NAMES.get(plan_state)
        if _expect and _shown and _shown.replace("_", "-") != _expect:
            state_verify_note += (
                f" — ⚠️ NHƯNG nhãn plan hiển thị là {_shown!r} trong khi state={plan_state} "
                f"nghĩa là {_expect!r}: hai field trong cùng plan mâu thuẫn, đọc theo state")
except FileNotFoundError:
    # không phải nguồn bắt buộc; thiếu file thì bỏ qua assert này, không chặn plan
    state_verify_note = ("⚠️ CHƯA đối chiếu được state plan vs DT5G hôm nay: không có "
                         "deploy_golive_dt5g_v4/golive_state_today.json — không chặn plan, "
                         "người duyệt tự kiểm regime")
except Exception as _e:
    state_verify_note = (f"⚠️ CHƯA đối chiếu được state plan vs DT5G hôm nay ({type(_e).__name__}: "
                         f"{_e}) — không chặn plan, người duyệt tự kiểm regime")

# 1a: price-plausibility gate — so giá ref mỗi lệnh với giá đóng cửa DNSE THẬT hôm nay (nguồn
# plan BẮT BUỘC phải đã dùng — coding_guidelines §6 "same-day data: DNSE API, never BigQuery").
# KHÔNG fallback BQ: sync_bq_cache_daily.sh chạy 23:45, SAU cả lúc DollarBill sinh plan (19:00)
# lẫn lúc script này chạy (21:00) — BQ chưa hề có giá đóng cửa hôm nay tại 2 thời điểm đó, đúng
# cái bẫy đã gây ra sự cố 07-10 (BQ lặng lẽ trả về giá phiên trước). Bất đối xứng có chủ đích:
# CHẶN khi có tín hiệu lệch giá rõ ràng (bảo vệ tiền), nhưng KHÔNG chặn khi DNSE tạm không trả
# lời được (tránh biến 1 lần API chập chờn buổi tối thành dừng hẳn việc gửi plan mỗi ngày) — chỉ
# im lặng bỏ qua khi TOÀN BỘ orders không xác minh được (báo hiệu DNSE outage thật, không phải
# lỗi giá), còn lệch giá xác nhận được ở dù chỉ 1 lệnh vẫn chặn. Verified/skipped count được
# ghi lại (price_verify_note bên dưới) và IN VÀO report — arch-reviewer 2026-07-30 chỉ ra bản
# đầu fail-open ÂM THẦM (0/N verify vẫn render y hệt N/N verify), đúng kiểu lỗi "self-report
# không kèm bằng chứng" mà chính gate này được viết ra để chặn.
#
# 3% CHƯA PHẢI ngưỡng đã hiệu chỉnh kỹ — đo nhanh trên lịch sử: ~1.7% số lệnh (6/362 kể từ
# 06-25) lệch >3% so giá đóng cửa NGÀY SINH plan, phần lớn do plan được lập giữa phiên (vd
# ref_price_source "DNSE_G1_latest_trade_09:24") chứ không phải lỗi nguồn giá — tức threshold
# này CÓ rủi ro false-positive thật trên ngày biến động mạnh/HNX-UPCOM biên độ rộng. Chấp nhận
# đánh đổi này lúc đầu (chặn nhầm 1 ngày còn rẻ hơn gửi nhầm giá), nhưng nếu false-positive xảy
# ra thật, đây là chỗ đầu tiên cần xem lại — không phải bug, là tham số cần tinh chỉnh thêm.
PRICE_TOLERANCE = 0.03

def _order_price(o):
    # Khớp ĐÚNG chuỗi fallback renderer dùng bên dưới (ref_price -> mtm_price_ref -> price) —
    # bản đầu CHỈ đọc ref_price nên là no-op với plan ZaloPay (dùng mtm_price_ref), tái lập lại
    # đúng sự cố 07-10 mà gate này được viết ra để chặn (arch-reviewer 2026-07-30 phát hiện
    # bằng cách replay lại file plan thật của 07-10, không phải fixture giả).
    p = o.get("ref_price", o.get("mtm_price_ref", o.get("price")))
    return p if isinstance(p, (int, float)) else None

buy_sell_orders = [o for o in orders if isinstance(o, dict) and _order_price(o) is not None]
price_verify_note = ""
if buy_sell_orders:
    tickers = sorted({o.get("ticker") for o in buy_sell_orders if o.get("ticker")})
    dnse_prices = {}
    try:
        sys.path.insert(0, os.getcwd())
        from trading_bot.brokers import get_dnse_client
        client = get_dnse_client()
        for tk in tickers:
            try:
                r = client.close_price(tk)
            except Exception:
                continue
            entries = (r or {}).get("prices") or []
            g1 = next((e for e in entries
                       if e.get("boardId") == "G1" and e.get("closePrice")), None)
            if g1:
                dnse_prices[tk] = float(g1["closePrice"]) * 1000
    except Exception:
        dnse_prices = {}

    implausible = []
    verified_n = 0
    for o in buy_sell_orders:
        tk = o.get("ticker")
        dp = dnse_prices.get(tk)
        if dp is None or not dp:
            continue  # không xác minh được lệnh này riêng lẻ (kể cả G1 closePrice=0 thật, đã
                       # thấy trực tiếp lúc test — coi như chưa xác minh, không suy diễn) — không
                       # chặn, chỉ bỏ qua, nhưng vẫn tính vào verified_n=0 cho lệnh đó
        else:
            verified_n += 1
            ref_p = _order_price(o)
            diff = abs(ref_p - dp) / dp
            if diff > PRICE_TOLERANCE:
                implausible.append(
                    f"{o.get('side','?')} {tk}: giá plan={ref_p:,.0f}đ vs DNSE close "
                    f"thật={dp:,.0f}đ (lệch {diff*100:.1f}%)")
    price_verify_note = (
        f"✅ giá đã xác minh {verified_n}/{len(buy_sell_orders)} lệnh có giá so DNSE close hôm nay"
        f"{f' (trên tổng {len(orders)} lệnh)' if len(buy_sell_orders) != len(orders) else ''}" if verified_n
        else f"⚠️ KHÔNG xác minh được giá lệnh nào so DNSE ({len(buy_sell_orders)}/{len(orders)} lệnh có giá cần kiểm) — "
             f"DNSE có thể đang gặp sự cố hoặc giá đóng cửa chưa có, không chặn plan nhưng cần "
             f"người tự đối chiếu giá trước khi duyệt")
    if implausible:
        escalate("plan_price_implausible",
                 f"{plan_file}: {len(implausible)}/{len(buy_sell_orders)} lệnh có giá lệch "
                 f">{PRICE_TOLERANCE*100:.0f}% so giá đóng cửa DNSE thật hôm nay — nghi dùng "
                 f"nhầm nguồn giá cũ/BQ (đúng dạng sự cố 07-10). Chi tiết: " + "; ".join(implausible))
        sys.exit(0)

# ── CAPIT: Σ lệnh mua thật vs VND mục tiêu đã publish (WARN, KHÔNG chặn) ────────────────
# Sự cố 07-21 (finding Taylor_20260731_154624): plan SpaceX nhân `capit_size` HAI LẦN (lấy
# weight_pct=15,0 của CSV — vốn ĐÃ = capit_size/n — nhân lên tổng vốn CAPIT vốn ĐÃ × capit_size)
# ⇒ deploy 254,4tr thay vì 348,4tr, thiếu 87,1tr (~27%). Plan tự ghi chú "chênh do rounding lots"
# nên KHÔNG ai để ý; làm tròn lô chỉ giải thích 6,8tr. Không cổng nào đối chiếu Σ VND với mục
# tiêu ⇒ sai 27% đi qua im lặng. Đây là đối chiếu đó, đặt ở BƯỚC DUYỆT (21:00, trước khi user
# bấm duyệt) chứ không ở executor 09:05 — chỗ duy nhất còn sửa được.
# WARN-only có chủ đích: chênh lớn có thể ĐÚNG (trần %ADV cắt, thiếu cash, mua chia nhiều phiên)
# — máy không phân biệt được, người duyệt phân biệt được. Ngưỡng 10% > làm tròn lô điển hình
# (<5% ở lô 100 với giá 2 chữ số) nhưng << 27% của sự cố thật.
capit_note = ""
capit_cov_gap = False     # rổ CAPIT có mã KHÔNG có lệnh ⇒ ✅ "khớp" KHÔNG có nghĩa đã triển khai đủ vốn
_capit_buys = [o for o in orders if isinstance(o, dict)
               and str(o.get("book", "")).upper() == "CAPIT"
               and str(o.get("side", "")).lower() in ("buy", "mua", "b")]
if _capit_buys:
    try:
        # python này chạy sau `cd "$WORKDIR"` (dòng RESULT=$(...)), nên đường dẫn tương đối
        _st = json.load(open(os.path.join("data", "golive_v23_status.json"), encoding="utf-8"))
        _tg = ((_st.get("capit_slot_targets") or {}).get(acct)) or {}
        # ĐÒN BẨY CAPIT (2026-08-03, arch-reviewer F3): khi `capit_margin_lever` ĐANG BẬT cho
        # account này, lệnh được sizing theo slot ĐÃ NHÂN f — đối chiếu với slot GỐC sẽ báo
        # lệch ~+30% và in ra đúng câu "nghi nhân capit_size hai lần". Tức là cổng bảo vệ sự
        # cố 07-21 sẽ kêu SAI ngay phiên đầu tiên có đòn bẩy, dạy người duyệt bỏ qua nó — và
        # lần sau lỗi THẬT cũng bị bỏ qua. Mốc so phải cùng cơ sở với mốc đã sizing.
        # Đọc `capit_lever` của CHÍNH artifact này (không đọc trading_rules.json): mục tiêu đã
        # publish và cờ bật/tắt phải đến từ cùng một ảnh chụp, nếu không hai nguồn lệch nhau
        # lại thành một cách sai mới.
        _lv = _st.get("capit_lever") or {}
        _lv_on = (_lv.get("active") is True and acct in (_lv.get("accounts") or []))
        _slot = _tg.get("capit_slot_target_vnd_levered") if _lv_on else None
        _basis = ""
        if _lv_on and _slot:
            _basis = (f" [đòn bẩy CAPIT ĐANG BẬT f={_lv.get('f')} gói {_lv.get('loan_package_id')}"
                      f" — mốc so là slot ĐÃ nhân f]")
        elif _lv_on:
            # Bật nhưng thiếu trường levered ⇒ nói thẳng là không đối chiếu được, KHÔNG lặng lẽ
            # rơi về slot gốc (rơi về sẽ in ra một cảnh báo sai với vẻ chắc chắn).
            _basis = (" [⚠️ đòn bẩy BẬT nhưng artifact thiếu `capit_slot_target_vnd_levered` — "
                      "đối chiếu dưới đây dùng slot GỐC nên lệch dương ~f là BÌNH THƯỜNG, "
                      "không phải lỗi sizing]")
        if not _slot:
            _slot = _tg.get("capit_slot_target_vnd")
        # PHỦ RỔ (Taylor A3, 2026-08-04): mốc so là `_slot × SỐ LỆNH TRONG PLAN`, nên một plan
        # viết THIẾU MÃ vẫn ra lệch 0% và hiện ✅ — đo được: 3/5 mã đúng cỡ slot → "✅ khớp
        # mục tiêu" trong khi 40% vốn không được triển khai. Rổ có bao nhiêu tên thì
        # `n_capit_basket` đã publish sẵn; chỉ là chưa ai đọc. Thiếu mã có thể ĐÚNG (đã giữ
        # đủ, trần %ADV = 0, DD loại) nên đây là một DÒNG THÔNG TIN, không đổi ngưỡng.
        _nb = _st.get("n_capit_basket") or 0
        _cov = ""
        if _nb and len(_capit_buys) < _nb:
            _cov = (f" [phủ {len(_capit_buys)}/{_nb} mã của rổ — {_nb - len(_capit_buys)} mã "
                    f"KHÔNG có lệnh; mốc so trên chỉ tính số mã CÓ trong plan, nên lệch ~0% "
                    f"KHÔNG có nghĩa đã triển khai đủ vốn]")
        if _slot:
            _actual = sum(float(o.get("actual_vnd") or 0)
                          or float(o.get("qty") or o.get("quantity") or 0) * float(_order_price(o) or 0)
                          for o in _capit_buys)
            _target = float(_slot) * len(_capit_buys)
            _dev = (_actual - _target) / _target if _target > 0 else 0.0
            _basis += _cov
            capit_cov_gap = bool(_cov)
            if abs(_dev) > 0.10:
                capit_note = (f"⚠️ CAPIT: Σ lệnh mua {_actual/1e6:,.0f}tr vs mục tiêu "
                              f"{_target/1e6:,.0f}tr ({len(_capit_buys)} mã × "
                              f"{_slot/1e6:,.1f}tr) — lệch {_dev*100:+.1f}%. Nếu KHÔNG do trần "
                              f"%ADV/thiếu cash thì kiểm tra đã nhân capit_size hai lần chưa "
                              f"(lỗi thật 07-21). Nguồn mục tiêu: golive_v23_status.json "
                              f"`capit_slot_targets`.{_basis}")
            else:
                capit_note = (f"✅ CAPIT: Σ lệnh mua {_actual/1e6:,.0f}tr khớp mục tiêu "
                              f"{_target/1e6:,.0f}tr (lệch {_dev*100:+.1f}%){_basis}")
        else:
            # PHIÊN TOP-UP (Taylor A3, 2026-08-04). `capit_slot_targets` CHỈ được publish khi
            # `capit_signal_today=true`; trong một episode đang mở thì hầu hết phiên là
            # top-up (đo 2026-08-04: episode CAPIT-2026-07-20 mở, capit_sessions_held=11,
            # capit_slot_targets={}) ⇒ nhánh "không đối chiếu được" bên dưới là chỗ MỌI plan
            # top-up rơi vào. Đúng cảnh báo sai chỗ: cổng sinh ra để canh cỡ deploy lại tối
            # đúng lúc deploy đang diễn ra. Mốc so đúng cho top-up KHÔNG phải slot VND mà là
            # `capit_episode_remaining_qty` (số CP CÒN THIẾU/mã/account) — engine đã publish
            # sẵn (golive_recommend_v23.py `**capit_ep`), chỉ chưa ai đọc.
            _rem = ((_st.get("capit_episode_remaining_qty") or {}).get(acct)) or {}
            if _st.get("capit_episode_open") and _rem:
                _over, _out, _tot_q, _tot_r = [], [], 0, 0
                for _o in _capit_buys:
                    _tk = str(_o.get("ticker") or _o.get("symbol") or "").upper()
                    _q = int(float(_o.get("qty") or _o.get("quantity") or 0))
                    _tot_q += _q
                    if _tk not in _rem:
                        _out.append(_tk)
                        continue
                    _r = int(_rem[_tk])
                    _tot_r += _r
                    if _q > _r:
                        _over.append(f"{_tk} {_q}cp > còn thiếu {_r}cp")
                _ep = _st.get("capit_episode_id") or "?"
                if _over or _out:
                    capit_note = (f"⚠️ CAPIT top-up (episode {_ep}): "
                                  + ("MUA VƯỢT phần còn thiếu: " + "; ".join(_over) + ". "
                                     if _over else "")
                                  + ("mã KHÔNG thuộc rổ episode: " + ", ".join(_out) + ". "
                                     if _out else "")
                                  + "Nguồn: golive_v23_status.json `capit_episode_remaining_qty`.")
                else:
                    capit_note = (f"✅ CAPIT top-up (episode {_ep}): {len(_capit_buys)} lệnh "
                                  f"{_tot_q:,}cp ≤ phần còn thiếu {_tot_r:,}cp, không mã nào "
                                  f"vượt. (Ngày tín hiệu mới có `capit_slot_targets`; phiên "
                                  f"top-up đối chiếu theo số CP còn thiếu.)")
            else:
                capit_note = ("⚠️ CAPIT: có lệnh CAPIT nhưng status chưa publish "
                              "`capit_slot_targets` cho account này VÀ không có episode mở để "
                              "đối chiếu — KHÔNG đối chiếu được cỡ deploy, người duyệt tự kiểm "
                              "Σ VND vs NAV_book_LAG × capit_size.")
    except Exception as _e:      # fail-open: không chặn plan vì một dòng đối chiếu
        capit_note = f"⚠️ CAPIT: không đối chiếu được cỡ deploy ({type(_e).__name__}: {_e})"

# ── ĐÒN BẨY MARGIN: nêu BẬT LOẠT, cổng duyệt RIÊNG (user chốt 2026-08-03) ───────────────
# "Khi DollarBill tạo plan dùng margin tôi sẽ phải đồng ý duyệt thì hệ thống mới được phép
# vận hành" — nên một plan có vay KHÔNG được lẫn vào dòng duyệt plan thường lệ. Khối này
# hiện Σ tiền vay + đúng lệnh phải chạy để duyệt riêng. Nguồn số = `preview_margin_day()`,
# CÙNG hàm mà `approve_margin_day.py` dùng để ghi trần vào bản duyệt và CÙNG cổng mà
# `apply_capit_lever` áp lúc 09:05 ⇒ số user thấy == số bị ràng buộc, không có bản sao
# công thức nào trôi khỏi nhau. Fail-open có ghi rõ: một dòng báo cáo không được chặn plan.
margin_note = []
try:
    from trading_bot.plan import preview_margin_day, margin_day_approval, CAPIT_LEVER_APPROVED_F
    import contextlib as _cl0, io as _io0      # load_plan in '[CEILING FAIL-SAFE] …' ra stdout — stdout này là kênh RESULT (làm render_crashed)
    with _cl0.redirect_stdout(_io0.StringIO()):
        _pv = preview_margin_day(acct, date)
    if _pv.get("error"):
        pass                     # không đọc được plan qua load_plan ⇒ im lặng, gate 09:05 vẫn đủ
    elif not _pv["orders"] and _pv.get("reasons"):
        # Plan ĐÃ sizing theo đòn bẩy nhưng đòn bẩy sẽ KHÔNG được cấp (công tắc tắt, artifact
        # từ chối…). Trước đây khối này im lặng ở nhánh đó, nên người duyệt 21:00 chỉ thấy
        # cảnh báo "lệch +30%" của cổng 07-21 — vốn quy sai nguyên nhân sang "nhân capit_size
        # hai lần". Đây đúng là phát hiện #3a của vòng 2, dịch sang tầng báo cáo
        # (arch-reviewer vòng 3 #7).
        _r = [r for r in _pv["reasons"] if "sizing" in r.lower() or "active" in r.lower()]
        if _r:
            margin_note.append("⚠️ **Plan có dấu hiệu đã sizing theo ĐÒN BẨY nhưng phiên sẽ "
                               f"chạy bằng VỐN TỰ CÓ** — khối lượng tính cho {CAPIT_LEVER_APPROVED_F:g}× "
                               "vốn mà chỉ có 1,0× vốn; triệu chứng sẽ là WAIT_CASH, không phải "
                               "lỗi rõ.")
            for _x in _r[:2]:
                margin_note.append(f"   · {_x}")
    elif _pv["orders"]:
        _rec, _aerr = margin_day_approval(acct, date)
        margin_note.append(
            f"🔺 **PLAN NÀY CÓ DÙNG MARGIN** — {len(_pv['orders'])} lệnh CAPIT "
            f"({', '.join(_pv['tickers'])}), Σ giá trị {_pv['total_vnd']/1e6:,.1f}tr, "
            f"**tiền VAY dự kiến ~{_pv['borrow_vnd']/1e6:,.1f}tr** "
            f"(f={_pv['lever_f']}, gói {_pv['loan_package_id']}).")
        if _rec is not None:
            margin_note.append(
                f"   ✅ Đòn bẩy ĐÃ ĐƯỢC DUYỆT RIÊNG cho phiên này "
                f"({_rec.get('approved_by')}) — trần Σ "
                f"{float(_rec.get('max_lever_total_vnd') or 0)/1e6:,.1f}tr.")
        else:
            margin_note.append(
                f"   ✅ **Đồng ý plan = duyệt margin tự động** — khi anh duyệt plan, Mike tự "
                f"tạo bản duyệt margin cho {len(_pv['orders'])} lệnh này. Không cần chạy tay.")
            margin_note.append(
                f"   Không duyệt plan ⇒ bot TỰ GỠ đòn bẩy và chạy bằng VỐN TỰ CÓ (không "
                f"chặn lệnh). [{_aerr}]")
except Exception as _e:          # fail-open: không chặn plan vì một dòng báo cáo
    margin_note = [f"⚠️ ĐÒN BẨY: không kiểm được trạng thái duyệt margin "
                   f"({type(_e).__name__}: {_e}) — nếu plan có lệnh CAPIT, kiểm tay trước 09:05."]

# ── PARK L1 (trim) + L2 (JIT unpark): HIỆN RÕ, KHÔNG GIẤU (user John chốt 2026-08-06) ───
# Lỗ hổng đã lặp 2 lần: cả `park_trim_proposal` (L1) lẫn `jit_unpark_proposal` (L2) đều LIVE,
# sinh lệnh BÁN THẬT và quyết định cỡ lệnh MUA thật, nhưng report duyệt plan không hề nhắc
# tới ⇒ (1) 08-05 lệnh trim PARK không ai duyệt vì user không biết nó tồn tại; (2) plan
# 08-07 hiện "MUA SSI 3100cp = 75,3tr" trong khi cash chỉ 4,8tr — đọc riêng lệnh mua thì
# tưởng DollarBill mua liều/thiếu tiền, trong khi thực tế L2 bán 12 mã PARK bù đủ và lệnh
# khớp NGUYÊN (status=FUNDED_BY_JIT).
# Khối này CHỈ ĐỌC artifact có sẵn trong plan — compute_park_trim.py / compute_jit_unpark.py
# vẫn là nguồn số DUY NHẤT, không tính lại gì ở đây (§6 provenance).
def _as_dict(x):
    return x if isinstance(x, dict) else {}

def _num(x):
    return float(x) if isinstance(x, (int, float)) else 0.0

_PT_SELLABLE_RE = re.compile(r"khả năng bán < 1 lô .*sellable ([\d,]+)cp")


def _pt_sellable_lt_lot(b):
    """Số cp bán được (int) nếu lý do chặn L1 là 'trần/khả năng bán < 1 lô' VÀ sellable < 1 lô (100cp,
    tức nguyên nhân là hiện vật chứ không phải trần ADV); ngược lại None."""
    m = _PT_SELLABLE_RE.search(str(b.get("reason") or ""))
    if not m:
        return None
    n = int(m.group(1).replace(",", ""))
    return n if n < 100 else None


def _tr(v):
    return f"{v/1e6:,.1f}tr"

def _note_text(note, budget=300):
    """Render 1 note cho report. Note mang cảnh báo ⚠️ THẬT ⇒ hiện ĐẦY ĐỦ, KHÔNG cắt (§4 style
    guide: bất thường thật thì mở rộng đầy đủ, không tóm tắt) — arch-review 2026-09-29 round 2+3
    bắt liên tiếp 2 cách cắt khác nhau (từ đầu chuỗi, rồi cắt từ vị trí ⚠️ đầu tiên) đều LỠ cảnh
    báo trên note thật (700 ký tự, 2 dấu ⚠️ cách nhau 333 ký tự — ca ZaloPay 2026-09-29:
    park_trim_proposal.notes[0]). Chunking Discord (notify_thread.sh, 1900 ký tự/tin) đủ rộng nên
    không cần cắt vì lý do độ dài kênh gửi. Note KHÔNG có ⚠️ (ca hiển thị thông tin thường, không
    phải cảnh báo) vẫn cắt ở `budget` + '…' để không phá layout report."""
    s = str(note)
    if "⚠️" in s:
        return s
    return s if len(s) <= budget else s[:budget] + "…"

def _route(txt, warn=False):
    """Dòng chẩn đoán: có ⚠️ thật HOẶC warn=True (decision không thuộc nhóm yên ổn đã biết) ⇒ WARN, còn lại ⇒ INFO."""
    (WARN if (warn or "⚠️" in txt) else INFO).append(txt)

def _o_val(o):
    """VND của 1 lệnh đề xuất. plan ZaloPay KHÔNG ghi `value_vnd` trong park_trim/jit orders
    (SpaceX có) ⇒ fallback qty × ref_price, cùng chuỗi fallback renderer dùng cho orders[]."""
    v = _num(o.get("value_vnd") or o.get("est_value_vnd"))
    if v:
        return v
    return (_num(o.get("qty") or o.get("quantity"))
            * _num(o.get("ref_price") or o.get("mtm_price_ref") or o.get("price")))

park_trim  = _as_dict(plan.get("park_trim_proposal"))
jit_prop   = _as_dict(plan.get("jit_unpark_proposal"))
pt_dec     = str(park_trim.get("decision") or "")
jit_dec    = str(jit_prop.get("decision") or "")
pt_orders  = [o for o in (park_trim.get("orders") or []) if isinstance(o, dict)]
jit_orders = [o for o in (jit_prop.get("orders") or []) if isinstance(o, dict)]
jit_amends = [a for a in (jit_prop.get("buy_amendments") or []) if isinstance(a, dict)]

# merge_park_orders.py đánh dấu proposal đã trở thành một phần của orders[].  Từ lúc cron
# merge chạy mỗi ngày, render cả orders[] lẫn hai mục proposal khiến người duyệt thấy cùng
# một lệnh BÁN PARK hai lần, dù executor chỉ đọc orders[] một lần.  Marker là hợp đồng của
# writer duy nhất; thiếu/hỏng marker thì giữ cách hiển thị cũ (an toàn: không giấu lệnh).
def _already_merged(prop):
    return str(prop.get("_merged_into_orders") or "").startswith("✅ ĐÃ MERGE")

pt_merged = _already_merged(park_trim)
jit_merged = _already_merged(jit_prop)
pt_report_orders = [] if pt_merged else pt_orders
jit_report_orders = [] if jit_merged else jit_orders

def _amend_for(o):
    """Khớp 1 lệnh trong orders[] với buy_amendments. Plan THẬT (cả SpaceX lẫn ZaloPay
    2026-08-07) KHÔNG ghi `order_id` vào orders[] trong khi amendment CÓ (`BUY-SSI-LAG-01`)
    ⇒ khớp order_id trước, rồi mới rơi về ticker."""
    oid = str(o.get("order_id") or "")
    tk  = str(o.get("ticker") or "").upper()
    if oid:
        for a in jit_amends:
            if str(a.get("order_id") or "") == oid:
                return a
    if tk:
        for a in jit_amends:
            if str(a.get("ticker") or "").upper() == tk:
                return a
    return None

def _sells_for(a):
    """Các lệnh bán PARK tài trợ cho đúng lệnh mua này (for_order_id, fallback for_ticker)."""
    oid = str(a.get("order_id") or "")
    tk  = str(a.get("ticker") or "").upper()
    sel = [o for o in jit_orders if oid and str(o.get("for_order_id") or "") == oid]
    if not sel and tk:
        sel = [o for o in jit_orders if str(o.get("for_ticker") or "").upper() == tk]
    return sel

def _fund_phrase(sells):
    if not sells:
        return "KHÔNG bán được mã PARK nào"
    n_tk = len({str(s.get("ticker") or "").upper() for s in sells})
    return f"bán {n_tk} mã PARK tổng {_tr(sum(_o_val(s) for s in sells))}"

def _tickers_line(os_):
    return " · ".join(
        f"{str(o.get('ticker') or '?')} {int(_num(o.get('qty') or o.get('quantity'))):,}cp "
        f"({_tr(_o_val(o))})" for o in os_)

# ── BỐ CỤC (kb/plan_report_style_guide.md §7, user 27/10: "đọc xong biết phần nào cần đọc"):
#   HDR  tiêu đề + trạng thái duyệt + bối cảnh (luôn có, ≤3 dòng)
#   ACT  việc phải LÀM/QUYẾT trước 9:05 (chuyển Trứng vàng, margin, đề xuất bán PARK cần duyệt riêng)
#   ORD  LỆNH (mỗi lệnh 1 dòng + tối đa 2 dòng phụ: định giá, thanh khoản/FA)
#   WARN cảnh báo ⚠️/⛔ (chỉ khi có bất thường thật — xác nhận thuần BỎ HẲN theo §4)
#   INFO ghi chú ℹ️ không cần quyết định
# Mục rỗng KHÔNG in tiêu đề ⇒ ngày yên ổn plan chỉ còn HDR + LỆNH.
HDR, ACT, ORD, WARN, INFO = [], [], [], [], []
lines = ORD      # code lệnh bên dưới append vào ORD; các khối khác append thẳng vào bucket của nó

_WD_VN = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
try:
    import datetime as _dtm
    _d = _dtm.date.fromisoformat(str(date)[:10])
    date_s = f"{_WD_VN[_d.weekday()]} {_d.day:02d}/{_d.month:02d}"
except Exception:
    date_s = str(date)
HDR.append(f"📋 **PLAN T+1 · {date_s} · {acct}**")
HDR.append("@@STATUS@@")      # điền ở cuối (cần đếm cảnh báo)

nav_str = f"{nav/1e6:,.1f}tr" if isinstance(nav, (int, float)) else "n/a"
_ctx = f"NAV {nav_str} · Regime {state}"
# DT gate: CHỈ hiện khi có candidate đang tích luỹ (đó mới là "có xu hướng mới đang hình thành");
# 'ổn định' = xác nhận thuần ⇒ bỏ (§4). Bỏ P(xác nhận), mốc badzone: số tham khảo đổi chậm, đã có
# trong EOD report (dna_report).
try:
    from dna_report import get_dt_gate_clock, build_dt_gate_line, STATE_MAP as _SMAP
    _c = get_dt_gate_clock()
    if _c and _c.get("active"):
        _cn = _SMAP.get(_c["cand"], ("?",))[0]
        # badge 🟢/🟡/🔴 lấy từ dòng chuẩn của dna_report (ngưỡng định nghĩa MỘT chỗ); 🟢 = bình thường ⇒ không hiện
        _gl = (build_dt_gate_line(html=False) or "").split("\n")[0]
        _bd = "🔴 " if "🔴" in _gl else ("🟡 " if "🟡" in _gl else "")
        _ctx += (f" · {_bd}DT5G candidate {_cn} {_c['k']}/{_c['need']} "
                 f"(còn {_c['need'] - _c['k']} phiên để commit)")
except Exception:
    pass
HDR.append(_ctx)

# Các kiểm tra nguồn trạng thái: chỉ ⚠️ mới vào WARN (đã là hành vi của state_verify_note từ 29/09).
if state_verify_note and "⚠️" in state_verify_note:
    WARN.append(state_verify_note.lstrip())
# Nguồn cổng get_gated_state() của bản publish plan này dựa vào (retro 2026-10-11 Pattern I, user
# duyệt 2026-10-12): khác DT5G_macro ⇒ MỘT dòng ⚠️, không chặn. Nguồn = golive_state_today.json;
# bằng chứng nguyên nhân = data/gate_source_alert.json do bước kiểm 19:00 ghi (bin/gate_source_check.py).
# DT5G_macro ⇒ chuỗi rỗng. Lỗi ⇒ NÓI RA trong report, không bỏ qua câm.
try:
    _gs_bin = os.environ.get("SEND_PLAN_MIKE_BIN")
    if _gs_bin and _gs_bin not in sys.path:
        sys.path.insert(1, _gs_bin)
    from gate_source_check import plan_report_line as _gate_src_line
    _gs_line = _gate_src_line(os.getcwd())
except Exception as _e:
    _gs_line = (f"⚠️ KHÔNG kiểm được nguồn cổng DT5G của bản publish hôm nay ({type(_e).__name__}: "
                f"{_e}) — không chặn plan, tự xem trường source trong golive_state_today.json")
if _gs_line:
    WARN.append(_gs_line)

# Đòn bẩy margin: quyết định riêng ⇒ ACT (đứng đầu).
for _m in margin_note:
    ACT.append(_m)

# ── TRỨNG VÀNG: việc phải làm trước 9:05 nếu mua > tiền mặt ────────────────────────────────
# Fail-open: lỗi đọc file → bỏ dòng, không chặn report. Đủ tiền = xác nhận thuần ⇒ KHÔNG in.
_egg_line_shown = False
try:
    import os as _os
    _nav_file = _os.path.join(
        _os.getcwd(), "data", "execution_logs", f"active_nav_{acct}.json"
    )
    _nav_live: dict = {}
    if _os.path.exists(_nav_file):
        with open(_nav_file) as _f:
            _nav_live = json.load(_f)
    _egg_vnd  = float(_nav_live.get("egg_assets") or 0)
    _cash_avail = float(_nav_live.get("cash_available_vnd") or 0)
    _buy_orders = [o for o in orders if str(o.get("side", "")).lower() in ("buy", "mua", "b")]
    _total_buy_vnd = sum(
        float(o.get("value_vnd") or o.get("est_value_vnd") or 0)
        or float(o.get("qty") or o.get("quantity") or 0) * float(o.get("ref_price") or o.get("mtm_price_ref") or 0)
        for o in _buy_orders
    )
    # JIT proceeds: if JIT is decided, PARK sells partially fund buys
    _jit_proceeds = 0.0
    if str(plan.get("jit_unpark_proposal", {}).get("decision") or "") == "JIT":
        _jit_proceeds = sum(
            float(o.get("value_vnd") or o.get("est_value_vnd") or 0)
            or float(o.get("qty") or o.get("quantity") or 0) * float(o.get("ref_price") or o.get("mtm_price_ref") or 0)
            for o in (plan.get("jit_unpark_proposal", {}).get("orders") or [])
            if isinstance(o, dict)
        )
    # Mức rút = giá TRẦN đuổi mua, không phải giá tham chiếu (sự cố 2026-10-26: SCL ref 31.100 khớp 32.300 +3,8%
    # ⇒ sức mua cạn ~0,3tr trước lệnh cuối, cảnh báo thiếu tiền bật sau 13:00). Egg rút trong ngày, không phí ⇒
    # dư vài tr chỉ tốn lãi egg 1 ngày, thiếu thì lệnh cuối không đặt được.
    try:
        import contextlib as _cl, io as _io          # load_config() in cảnh báo khoá lạ ra stdout — stdout này là kênh RESULT
        from trading_bot.config import load_config as _lc
        with _cl.redirect_stdout(_io.StringIO()), _cl.redirect_stderr(_io.StringIO()):
            _chase = float(_lc().get("chase_cap_vol_ceil", 0.04))
    except Exception:
        _chase = 0.04
    _fee = 0.00097
    # Lệnh có trần cứng KHÔNG đuổi quá trần ⇒ giá tối đa = min(ref×(1+chase), trần). Trần lấy từ CHÍNH hàm load_plan
    # dùng (`resolve_buy_ceiling`: luật A / fail-safe / luật cũ) — không tự min() hai field (arch-review 27/10:
    # luật A không kẹp theo anchor; fail-safe không anchor thì BỎ trần). Cùng quy tắc `_buy_cost_price` của plan_funding_gate.
    def _o_val(o):
        return (float(o.get("value_vnd") or o.get("est_value_vnd") or 0)
                or float(o.get("qty") or o.get("quantity") or 0) * float(o.get("ref_price") or o.get("mtm_price_ref") or 0))

    try:
        from trading_bot.no_chase_ceiling import resolve_buy_ceiling as _rbc
    except Exception:
        _rbc = None                                   # không import được ⇒ coi như không có trần ⇒ đệm +chase% (an toàn: đòi nhiều hơn)

    def _o_ceiling(o):
        if _rbc is None:
            return None
        try:
            with _cl.redirect_stdout(_io.StringIO()), _cl.redirect_stderr(_io.StringIO()):
                c, _ = _rbc(dict(o), plan_date=plan.get("plan_date"))
            return c if c and c > 0 else None
        except Exception:
            return None

    _ceil_used = []

    def _o_max_cost(o):
        rp = float(o.get("ref_price") or o.get("mtm_price_ref") or 0)
        c = _o_ceiling(o)
        if rp > 0 and c:
            _ceil_used.append(c)
            return float(o.get("qty") or o.get("quantity") or 0) * min(rp * (1.0 + _chase), c)
        return _o_val(o) * (1.0 + _chase)
    _buy_ceiling = sum(_o_max_cost(o) for o in _buy_orders) * (1.0 + _fee)
    _shortfall = max(0.0, _buy_ceiling - _cash_avail - _jit_proceeds)
    if _egg_vnd > 0 and _total_buy_vnd > 0 and _shortfall > 0:
        ACT.append(
            f"🥚 **Chuyển {-(-_shortfall // 100_000) / 10:,.1f}tr từ Trứng vàng → cash trước 9:05 ICT** "
            f"(bot nhắc mỗi 15' từ 8:30). Σ mua {_total_buy_vnd/1e6:,.1f}tr → tối đa {_buy_ceiling/1e6:,.1f}tr "
            f"({'giá mỗi lệnh = min(giá tham chiếu +%.0f%%, trần cứng)' % (_chase*100) if _ceil_used else 'đệm đuổi giá +%.0f%%' % (_chase*100)} & phí) "
            f"− tiền mặt {_cash_avail/1e6:,.1f}tr"
            + (f" − JIT-bán PARK {_jit_proceeds/1e6:,.1f}tr" if _jit_proceeds > 0 else "")
            + f" · Trứng vàng hiện {_egg_vnd/1e6:,.1f}tr."
        )
        _egg_line_shown = True
except Exception:
    pass

# Transition context nếu có (ZaloPay Option A) — thông tin, không cần quyết định.
tsched = plan.get("transition_schedule") or []
tday = next((t for t in tsched if t.get("date") == date), None)
if tday:
    INFO.append(f"🔄 Lộ trình chuyển đổi danh mục: ngày {tday.get('day')}/{len(tsched)} theo kế hoạch Option A đã duyệt")

# plan['notes'][]: CHỈ note DollarBill mở đầu bằng ⚠️/🛑 mới lên report (hợp đồng viết note — xem
# kb/context_planning_mini.md "Viết note trong plan"). Phần còn lại là nhật ký lập plan, nằm trong file.
for _pn in (plan.get("notes") or []):
    if isinstance(_pn, str) and _pn.lstrip().startswith(("⚠", "🛑")):
        WARN.append(_pn.strip())

if orders:
    # DCF check (Pha 2, informational — user directive 2026-07-15: PHẢI hiển thị trong text
    # duyệt plan, không chỉ nằm trong JSON). Echo field dcf_check nếu plan có; BUY thiếu field
    # (plan DollarBill hiện không populate) → tự tính fallback từ cache local (KHÔNG BQ live).
    # Fail-safe toàn phần: import/tính lỗi → bỏ dòng DCF, KHÔNG chặn report duyệt plan.
    try:
        from trading_bot.strategies import (_dcf_check_for_order, format_dcf_check,
                                            log_dcf_history)
    except Exception:
        _dcf_check_for_order = format_dcf_check = log_dcf_history = None
    # Due-diligence tổng hợp cho MỌI lệnh MUA (mandate user 2026-07-21) — thanh khoản/universe/
    # cơ học tín hiệu/cờ bất thường/FA thô. skip_dcf=True vì dòng DCF đã echo riêng ngay trên.
    # as_dict=True (27/10): renderer tự gộp 3 dòng DD/FA/cờ thành 1 dòng gọn; cờ ĐỎ vẫn do
    # format_dd_check() của module sinh (cùng câu chữ + cùng đòi dd_override_reason).
    try:
        from trading_bot.due_diligence import run_due_diligence, format_dd_check
    except Exception:
        run_due_diligence = format_dd_check = None
    buys  = [o for o in orders if str(o.get("side","")).lower() in ("buy","mua","b")]
    sells = [o for o in orders if str(o.get("side","")).lower() in ("sell","ban","s")]
    # §2 kb/plan_report_style_guide.md: N lệnh PARK_TRIM cùng lý do (cùng target_park, cùng
    # ngày) ⇒ 1 câu áp dụng chung sau vòng lặp, KHÔNG lặp nguyên văn theo từng lệnh (ca thật
    # 2026-09-29: 19/19 lệnh lặp y hệt).
    _pt_trim_tickers = [o.get("ticker","?") for o in sells
                        if str(o.get("play_type", "")).upper() == "PARK_TRIM"]

    def _ord_val(o):
        v = o.get("est_value_vnd", o.get("est_value"))
        if isinstance(v, (int, float)):
            return float(v)
        q, p = o.get("quantity", o.get("qty")), o.get("ref_price", o.get("mtm_price_ref", o.get("price")))
        return float(q) * float(p) if isinstance(q, (int, float)) and isinstance(p, (int, float)) else None

    _sum_buy = sum(v for v in (_ord_val(o) for o in buys) if v)
    _sum_sell = sum(v for v in (_ord_val(o) for o in sells) if v)
    _ord_title = (f"**🎯 LỆNH — {len(buys)} mua"
                  + (f" Σ {_sum_buy/1e6:,.1f}tr" if _sum_buy else "")
                  + f" · {len(sells)} bán"
                  + (f" Σ {_sum_sell/1e6:,.1f}tr" if _sum_sell else "") + "**")
    if pt_report_orders or jit_report_orders:
        ACT.append(f"➕ Ngoài {len(orders)} lệnh trên, còn **{len(pt_report_orders) + len(jit_report_orders)} "
                   f"lệnh BÁN PARK đề xuất** (L1 trim {len(pt_report_orders)} + L2 JIT {len(jit_report_orders)}) — "
                   f"CẦN DUYỆT RIÊNG, chi tiết ở mục dưới.")
    # "đã xác minh N/N" (TOÀN BỘ lệnh) mỗi ngày không cần giải thích — chỉ hiện khi CHƯA xác minh đủ
    # (verified_n < tổng, gồm cả 0/N lẫn PARTIAL vd 1/9) — arch-review 2026-09-29: KHÔNG dùng "⚠️"
    # in text làm proxy (PARTIAL từng render y hệt FULL).
    if price_verify_note and verified_n < len(buy_sell_orders):
        WARN.append(price_verify_note)
    # capit_note: ✅ (khớp mục tiêu) = xác nhận thuần ⇒ bỏ; ⚠️ giữ NGUYÊN văn.
    if capit_note and (not capit_note.startswith("✅") or "⚠️" in capit_note or capit_cov_gap):
        WARN.append(capit_note)

    # Note của lệnh do DollarBill (LLM) viết có phần mẫu CỐ ĐỊNH mỗi ngày ("theo
    # filter_lag_entry_window.py", "Nếu regime chuyển BEAR … w_LAG=0") — luật đó nằm ở kb, không
    # phải thông tin của lệnh này. Renderer lọc đúng các câu mẫu đã biết; câu lạ ⇒ GIỮ (fail-visible).
    _STATIC_NOTE = [r"\s*theo filter_lag_entry_window\.py",
                    r"\s*\([^()]*\.py:\d+\)",
                    r"\s*Nếu regime chuyển BEAR[^.]*?allocator[^.]*\.?"]

    def _order_tag_note(o):
        tag = str(o.get("play_type") or o.get("book") or "").strip()
        n = str(o.get("note") or "")
        m = re.match(r"\s*\S+\s+entry ngày\s*(\d+)(?:\s*/\s*(\d+))?(?:\s*/\s*…)?", n)
        if m:
            tag += f" ngày {m.group(1)}" + (f"/{m.group(2)}" if m.group(2) else "")
            n = n[m.end():]
        for _p in _STATIC_NOTE:
            n = re.sub(_p, "", n)
        n = n.strip(" \t—-;.")
        return tag, n

    def _dcf_compact(dcf_s):
        """Bỏ phần chú giải phương pháp của lăng kính thay thế; số + nhãn + ⚠ cần override giữ."""
        s_ = re.sub(r"\s*\[(?:FALLBACK|đã validate)[^\]]*\]", "", dcf_s)
        return s_.replace("DCF: NOT_COMPUTED (", "DCF n/a (").replace(" → thay thế: ", " → ")

    # PARK_TRIM thuần (§2/§7 style guide: nhóm cùng lý do gộp 1 dòng): note rỗng hoặc chỉ là câu mẫu
    # "BÁN PARK gộp: L1 … = qty × giá" (lặp lại số đã có trên dòng lệnh). Lệnh trim mang note KHÁC
    # (đặc biệt ⚠️) vẫn render riêng, không bị gộp nuốt.
    _trim_grp = [o for o in sells
                 if str(o.get("play_type", "")).upper() == "PARK_TRIM"
                 and "⚠️" not in str(o.get("note") or "")
                 and (not str(o.get("note") or "").strip()
                      or str(o.get("note")).lstrip().startswith("BÁN PARK gộp:"))]
    _trim_ids = {id(o) for o in _trim_grp}
    _trim_done = False
    _o_tgt = park_trim.get("target_park")
    _o_tgt_s = f"{float(_o_tgt)*100:.0f}%" if isinstance(_o_tgt, (int, float)) else "?"
    _pt_why = ("park TẮT (0%) ⇒ bán sạch PARK" if isinstance(_o_tgt, (int, float)) and _o_tgt == 0
               else f"giữ PARK ≤ {_o_tgt_s} pool")
    _rest_cnt, _rest_seen = {}, set()
    for _o in orders:
        if id(_o) not in _trim_ids:
            _r = _order_tag_note(_o)[1]
            if _r:
                _rest_cnt[_r] = _rest_cnt.get(_r, 0) + 1
    for o in orders:
        if id(o) in _trim_ids:
            if not _trim_done:
                _trim_done = True
                _gv = sum(v for v in (_ord_val(x) for x in _trim_grp) if v)
                lines.append(f"• **BÁN PARK_TRIM** {len(_trim_grp)} mã" + (f" Σ {_gv/1e6:,.1f}tr" if _gv else "")
                             + " — " + " · ".join(
                                 f"{x.get('ticker','?')} {int(_num(x.get('quantity', x.get('qty')))):,}"
                                 for x in _trim_grp))
                lines.append(f"    ↳ ℹ️ cùng một lý do: {_pt_why} (không liên quan tài trợ lệnh mua).")
            continue
        side_vn = "BÁN" if str(o.get("side","")).lower() in ("sell","ban","s") else "MUA"
        is_buy = side_vn == "MUA"
        ticker = o.get("ticker","?")
        qty    = o.get("quantity", o.get("qty","?"))
        price  = o.get("ref_price", o.get("mtm_price_ref", o.get("price")))
        px = f"{price:,.0f}" if isinstance(price, (int, float)) else "giá TT"
        _v = _ord_val(o)
        val_s = f" ≈ {_v/1e6:,.1f}tr" if _v else ""
        qty_s = f"{qty:,}" if isinstance(qty, int) else str(qty)
        tag, rest = _order_tag_note(o)
        # note mang ⚠️ THẬT ⇒ hiện nguyên văn (không cắt — §4 style guide, ca TV1 2026-08-12).
        lines.append(f"• **{side_vn} {ticker}** {qty_s}cp @ {px}{val_s}" + (f" · {tag}" if tag else ""))
        _ord_idx, _oflag = len(lines) - 1, False
        # Trần cứng không-đuổi-giá: dòng CHUẨN sinh từ field (executor cưỡng chế qua load_plan), KHÔNG phụ thuộc
        # chữ DollarBill viết — 2 account cùng lệnh phải hiện cùng một câu (sự cố lệch SCL 28/10).
        if is_buy:
            _ceil_c = [_num(o.get(k)) for k in ("hard_no_chase_ceiling_vnd", "entry_anchor_price")]
            _ceil_c = [c for c in _ceil_c if c and c > 0]
            if _ceil_c:
                _ceil = min(_ceil_c)
                _over = (f" — giá tham chiếu {price:,.0f} đang CAO hơn trần {(price/_ceil-1)*100:.1f}%"
                         if isinstance(price, (int, float)) and price > _ceil else "")
                lines.append(f"    ↳ 🔒 Trần cứng {_ceil:,.0f} (không đuổi giá): lệnh chỉ khớp nếu giá ≤ {_ceil:,.0f}{_over}")
        # Cùng mã có thể nằm ở nhiều book (VPB: LAG mua/thoát vs PARK) ⇒ mọi cảnh báo theo lệnh ghi rõ [book]
        _tkb = f"{ticker} [{o.get('book') or o.get('play_type') or '?'}]"
        if rest and rest not in _rest_seen:
            _rest_seen.add(rest)
            _same = _rest_cnt.get(rest, 1)
            lines.append(f"    ↳ 📌 {_note_text(rest, budget=240)}"
                         + (f" (chung cho {_same} lệnh cùng loại)" if _same > 1 else ""))
        # Lý do bán PARK_TRIM là ĐỘC LẬP với bất kỳ lệnh mua nào (park-target compliance, không phải
        # tài trợ) — KHÔNG lặp theo từng lệnh (§2 style guide), xem dòng tổng sau vòng lặp.
        # Funding note CHỈ khi có điều cần biết: "đủ tiền mặt" (FUNDED_BY_CASH) = xác nhận thuần ⇒ bỏ.
        if is_buy:
            _a = _amend_for(o)
            if _a:
                _st = str(_a.get("status") or "")
                _fp = _fund_phrase(_sells_for(_a))
                _net = _num(_a.get("jit_proceeds_net_vnd"))
                _net_s = f" (thu ròng {_tr(_net)})" if _net else ""
                _rs = str(_a.get("reason") or "")[:150]
                if _st == "FUNDED_BY_JIT":
                    lines.append(
                        f"    ↳ 💧 **Tiền đâu ra:** {_fp}{_net_s} ⇒ mua NGUYÊN lệnh {_a.get('qty_final')}cp "
                        f"(tiền mặt {_tr(_num(_a.get('cash_before_vnd')))} → "
                        f"{_tr(_num(_a.get('cash_after_vnd')))}); các lệnh bán PARK đó CẦN DUYỆT cùng lệnh mua này.")
                elif _st == "FUNDED_BY_CASH":
                    pass
                elif _st == "SHRINK":
                    WARN.append(
                        f"⚠️ **{_tkb}: lệnh bị CO** {_a.get('qty_plan')}cp → {_a.get('qty_final')}cp "
                        f"dù đã {_fp}{_net_s} — {_rs}")
                    _oflag = True
                elif _st == "DROP":
                    WARN.append(
                        f"⛔ **{_tkb}: lệnh bị BỎ** (kế hoạch {_a.get('qty_plan')}cp) dù đã cố "
                        f"bán PARK — {_rs}")
                    _oflag = True
                elif _st:
                    WARN.append(f"⚠️ {_tkb}: JIT status={_st} — {_rs}")
                    _oflag = True
        if format_dcf_check:
            dcf = o.get("dcf_check")
            if not dcf and is_buy and _dcf_check_for_order and isinstance(price, (int, float)):
                try:
                    dcf = _dcf_check_for_order(ticker, price, date)
                except Exception:
                    dcf = None
            dcf_s = format_dcf_check(dcf, "buy" if is_buy else "sell",
                                     has_override=bool(o.get("dcf_override_reason")),
                                     ticker=ticker)
            if dcf_s:
                lines.append(f"    ↳ {_dcf_compact(dcf_s)}")
                if "cần dcf_override_reason" in dcf_s:
                    WARN.append(f"⚠️ {_tkb}: DCF RICH sâu — cần dcf_override_reason trước khi mua")
                    _oflag = True
                if log_dcf_history:
                    log_dcf_history(ticker, dcf, "send_plan_report", asof=date)
            if is_buy and o.get("dcf_override_reason"):
                lines.append(f"    ↳ lý do override DCF: {str(o['dcf_override_reason'])[:120]}")
        if is_buy and run_due_diligence:
            # dd_override_reason đi vào ctx để cờ đỏ tự biết đã có lý do override hay chưa — thiếu
            # lý do thì hiện "cần dd_override_reason" NGAY tại bước user duyệt plan.
            dd_ctx = {"asof": date, "skip_dcf": True, "side": "buy",
                      "dd_override_reason": o.get("dd_override_reason") or ""}
            if isinstance(price, (int, float)):
                dd_ctx["price"] = price
            _ev = o.get("est_value_vnd", o.get("est_value"))
            if isinstance(_ev, (int, float)):          # chỉ khi plan tự ghi — đổi hiển thị không được bật thêm cờ đỏ
                dd_ctx["est_value_vnd"] = _ev
            _dd = run_due_diligence(ticker, o.get("book") or o.get("play_type"), dd_ctx, as_dict=True)
            if isinstance(_dd, dict):
                _bits, _wbits = [], []
                if _dd.get("error"):
                    _wbits.append(f"DD n/a ({_dd['error']})")
                else:
                    _sm = _dd.get("signal_mechanics")
                    if _sm and str(_sm).startswith("nền YoY dương"):   # nền bình thường = xác nhận thuần
                        _sm = None
                    for _x in (_dd.get("liquidity"), _sm, _dd.get("anomaly")):
                        if not _x:
                            continue
                        (_wbits if ("⚠" in str(_x) or "🔴" in str(_x)) else _bits).append(str(_x))
                    if _dd.get("fundamentals"):
                        _bits.append(str(_dd["fundamentals"]))
                if _bits:
                    lines.append("    ↳ DD: " + " · ".join(_bits))
                for _x in _wbits:                       # cảnh báo DD/thanh khoản/bất thường ⇒ mục CẢNH BÁO
                    WARN.append(f"⚠️ {_tkb}: " + _x.replace("⚠ ", "", 1).lstrip())
                    _oflag = True
                _warn = format_dd_check(_dd, "buy", bool(o.get("dd_override_reason"))) if format_dd_check else ""
                if _warn:
                    WARN.append(f"{_warn.replace('DD cờ đỏ:', 'DD cờ đỏ ' + _tkb + ':', 1)}")
                    _oflag = True
            if o.get("dd_override_reason"):
                lines.append(f"    ↳ lý do override DD: {str(o['dd_override_reason'])[:120]}")
        if _oflag:
            lines[_ord_idx] += " ⚠️"
    if _pt_trim_tickers and not _trim_grp:
        # Không có dòng nhóm (mọi lệnh PARK_TRIM đều mang note riêng) ⇒ lý do chung vẫn phải nói 1 lần.
        # KHÔNG liệt kê lại tên mã (§3 style guide) — đã có ở từng dòng "• BÁN ..." bên trên.
        lines.append(f"    ↳ ℹ️ lệnh BÁN PARK_TRIM ở trên: {_pt_why} (không liên quan tài trợ lệnh mua).")
    # DCF_DISCLAIMER/DD_DISCLAIMER (giải thích PHƯƠNG PHÁP DCF/DD) bỏ khỏi report hàng ngày
    # 2026-09-29 — văn bản cố định; nội dung đầy đủ ở dcf_valuation.DCF_DISCLAIMER / due_diligence.DD_DISCLAIMER.
else:
    _ord_title = "**🎯 LỆNH — không có (HOLD)**"

# ── §29 auto_exit_inject: mã bị CHẶN (không chèn lệnh) hoặc bị CẮT (qty giảm do trần sellable)
# phải hiện ra cho người duyệt, không chỉ nằm trong log stdout của cron (arch-review vòng 3) —
# `capped` qty>0 đã có note "[CAP ...]" ngay trên dòng lệnh trong orders[], khối này bổ sung cho
# ca KHÔNG có lệnh nào để hiện (blocked hoàn toàn, hoặc capped về 0) và tổng hợp lại một chỗ.
# ── CP chờ niêm yết bổ sung (user duyệt 2026-10-07): phần KHOÁ của mã có bằng chứng là CP
# thưởng/cổ tức CP/quyền mua (bin/locked_shares.py — không có lệnh mua gần đây + có sự kiện ISS)
# ⇒ lệnh bán bị cắt về trần sellable là chuyện đã biết, tự hết khi niêm yết, người duyệt không
# phải quyết gì ⇒ GỘP thành 1 dòng ℹ️ thay vì ⚠️ lặp mỗi tối. Không đủ bằng chứng ⇒ giữ ⚠️ cũ.
# Fail-open: lỗi module/đọc file ⇒ _lk_pending rỗng ⇒ hiển thị y như trước.
_lk_pending = {}
try:
    _lk_bin = os.environ.get("SEND_PLAN_MIKE_BIN")
    if _lk_bin and _lk_bin not in sys.path:
        sys.path.insert(1, _lk_bin)
    if os.getcwd() not in sys.path:
        sys.path.insert(1, os.getcwd())          # corp_action_lib nằm ở WC root
    import locked_shares as _lks
    _lk_acct_no = str(plan.get("account_no") or "")
    if _lk_acct_no:
        _lk_res = _lks.classify(_lk_acct_no, today,
                                os.path.join(os.getcwd(), "data", "execution_logs"),
                                os.path.join(os.getcwd(), "data", "corp_actions.json"))
        _lk_pending = _lk_res.get("pending") or {}
except Exception as _e:
    print(f"[locked_shares] bỏ qua, hiển thị như cũ: {type(_e).__name__}: {_e}", file=sys.stderr)
_lk_shown = False

def _lk_info_line(exit_caps):
    """1 dòng ℹ️ gộp mọi mã chờ niêm yết; exit_caps = {ticker: [(book, desired, capped)]}."""
    parts = []
    for _tk, _it in sorted(_lk_pending.items()):
        _d = _lks.describe(_tk, _it)
        for _bk, _want, _got in exit_caps.get(_tk, []):
            _d += f" — lệnh thoát {_bk} {_want}cp chỉ đặt được {_got}cp, phần còn lại tự bán phiên sau"
        parts.append(_d)
    return ("ℹ️ CP chờ niêm yết bổ sung, CHƯA bán được (không cần duyệt gì, tự bán khi giao "
            "dịch được): " + "; ".join(parts) + ".")

_aei_notes = plan.get("auto_exit_inject_notes") or []
if _aei_notes:
    # §29 vòng 4 (arch-review): `_aei_notes[-1]` một mình bị che khi có entry ghi tay
    # (manual:true, do user sửa tay plan sau giờ cron) xuất hiện SAU entry auto có
    # blocked/capped — ca thật ZaloPay 10-02 (entry auto 20:40 rồi entry manual 22:59/23:0x).
    # Entry do auto_exit_inject.py ghi luôn có source="auto_exit_inject" (entry ghi tay thì
    # không) — gộp blocked/capped của MỌI entry auto trong ngày, dedup theo (ticker,book,reason).
    _aei_auto = [n for n in _aei_notes if isinstance(n, dict) and n.get("source") == "auto_exit_inject"]
    _aei_blocked, _aei_blocked_seen = [], set()
    for _n in _aei_auto:
        for b in (_n.get("blocked") or []):
            if not isinstance(b, dict):
                continue
            _k = (b.get("ticker"), b.get("book"), b.get("reason"))
            if _k in _aei_blocked_seen:
                continue
            _aei_blocked_seen.add(_k)
            _aei_blocked.append(b)
    _aei_capped, _aei_capped_seen = [], set()
    for _n in _aei_auto:
        for c in (_n.get("capped") or []):
            if not isinstance(c, dict):
                continue
            _k = (c.get("ticker"), c.get("book"), c.get("desired_qty"), c.get("capped_qty"))
            if _k in _aei_capped_seen:
                continue
            _aei_capped_seen.add(_k)
            _aei_capped.append(c)
    # Entry THỦ CÔNG (user sửa tay plan, schema injected[].capped_from/capped_to — KHÁC field
    # với capped[].desired_qty/capped_qty tự động) cũng có thể mang quyết định CẮT (ca thật VPB
    # 882→600cp, entry manual 22:59). Hiện CẢ hai nguồn trong cùng khối ⚠️ — "ít nhất không để
    # che entry auto" (yêu cầu tối thiểu arch-review vòng 4) nghĩa là union, không phải OR-chọn-1.
    _aei_manual_capped = []
    for _n in _aei_notes:
        if not isinstance(_n, dict) or _n.get("source") == "auto_exit_inject":
            continue
        for _it in (_n.get("injected") or []):
            if isinstance(_it, dict) and _it.get("capped_from") is not None \
               and _it.get("capped_to") is not None:
                _aei_manual_capped.append(_it)
    if _aei_blocked:
        WARN.append(f"⛔ **{len(_aei_blocked)} mã auto-exit (LAG/BAL/CAPIT) BỊ CHẶN, KHÔNG chèn lệnh:**")
        for b in _aei_blocked[:8]:
            _tk_s = b.get("ticker") or "(book-level)"
            WARN.append(f"   • {_tk_s} ({b.get('book','?')}): {str(b.get('reason') or '')[:150]}")
    # Mã cắt do CP chờ niêm yết (bằng chứng ở _lk_pending) ⇒ chuyển sang dòng ℹ️ gộp — CHỈ khi
    # phần cắt được khoá giải thích trọn (locked_shares.split_capped; rights alert NB 25/10: bản
    # cũ hạ mọi cắt của mã có mặt trong _lk_pending ⇒ che ⚠️ của lệnh book khác/lô quyền hết khoá).
    # Lô quyền mua auto_exit đã tách khỏi lệnh (entry auto mới nhất có rights_locked) không được
    # giải thích lại phần cắt (arch-review 25/10 NB1). Lỗi bất kỳ ⇒ giữ ⚠️ hết (fail-loud, NB3).
    _lk_exit = {}
    if _lk_pending:
        try:
            _rl_qty = {}
            for _lk in (next((_n.get("rights_locked") for _n in reversed(_aei_auto)
                              if _n.get("rights_locked")), None) or []):
                if isinstance(_lk, dict):
                    _rl_qty[_lk.get("ticker")] = _rl_qty.get(_lk.get("ticker"), 0) + int(_lk.get("locked_qty") or 0)
            _lk_info, _aei_capped = _lks.split_capped(_aei_capped, _lk_pending, plan.get("orders") or [], _rl_qty)
        except Exception as _e:
            _lk_info = []
            print(f"[locked_shares] split_capped lỗi, giữ mọi ⚠️ cắt: {type(_e).__name__}: {_e}", file=sys.stderr)
        for _tk, _bk, _want, _got in _lk_info:
            _lk_exit.setdefault(_tk, []).append((_bk, _want, _got))
    if _lk_exit:
        INFO.append(_lk_info_line(_lk_exit))
        _lk_shown = True
    if _aei_capped or _aei_manual_capped:
        WARN.append(f"⚠️ **{len(_aei_capped) + len(_aei_manual_capped)} mã auto-exit BỊ CẮT do trần sellable (Σ SELL mọi book):**")
        for c in _aei_capped[:8]:
            WARN.append(f"   • {c.get('ticker','?')} ({c.get('book','?')}): "
                         f"{c.get('desired_qty','?')}cp → {c.get('capped_qty','?')}cp"
                         + (f" — {str(c['rights_diag'])[:220]}" if c.get("rights_diag") else ""))
        for c in _aei_manual_capped[:8]:
            WARN.append(f"   • {c.get('ticker','?')} ({c.get('book','?')}): "
                         f"{c.get('capped_from','?')}cp → {c.get('capped_to','?')}cp (duyệt tay)")
    # B1 vòng 2 (N1): CP quyền mua khoá chờ niêm yết — lấy entry auto MỚI NHẤT có khoá (trạng
    # thái hiện hành, không cộng dồn các lượt chạy lại trong ngày).
    _aei_locked = next((_n.get("rights_locked") for _n in reversed(_aei_auto)
                        if _n.get("rights_locked")), None) or []
    if _aei_locked:
        INFO.append(f"ℹ️ **{len(_aei_locked)} lô CP quyền mua KHOÁ chờ niêm yết (đã khai, tự bán khi broker cho bán):**")
        for lk in _aei_locked[:8]:
            if isinstance(lk, dict):
                INFO.append(f"   • {str(lk.get('reason') or '')[:220]}")

# ── MỤC RIÊNG 1: L1 park_trim_proposal ──────────────────────────────────────────────────
# Ngang hàng với orders[], KHÔNG phải câu phụ trong đoạn văn: đây là lệnh BÁN THẬT cần user
# duyệt riêng (chúng KHÔNG nằm trong orders[] mà bot đọc lúc 09:05).
try:
    if pt_dec == "TRIM" and pt_report_orders:
        _pt_sum = sum(_o_val(o) for o in pt_orders)
        _pt_eng = _num(park_trim.get("trim_proposed_vnd"))
        _tgt = park_trim.get("target_park")
        _tgt_s = f"{float(_tgt)*100:.0f}%" if isinstance(_tgt, (int, float)) else "?"
        ACT.append(f"🅿️ **ĐỀ XUẤT TRIM PARK (L1) — {len(pt_orders)} lệnh BÁN, "
                     f"Σ {_tr(_pt_eng or _pt_sum)} — CẦN DUYỆT RIÊNG**")
        ACT.append(f"   Mục tiêu: đưa PARK về trần {_tgt_s} của pool — PARK hiện "
                     f"{_tr(_num(park_trim.get('park_mv_vnd')))} / pool "
                     f"{_tr(_num(park_trim.get('pool_vnd')))} ⇒ cần trim "
                     f"{_tr(_num(park_trim.get('trim_total_vnd')))}, phiên này đề xuất "
                     f"{_tr(_pt_eng or _pt_sum)}"
                     + (f", còn thiếu {_tr(_num(park_trim.get('trim_shortfall_vnd')))} để phiên sau"
                        if _num(park_trim.get("trim_shortfall_vnd")) else "") + ".")
        ACT.append(f"   BÁN: {_tickers_line(pt_orders)}")
        # Σ engine vs Σ lệnh liệt kê: lệch = plan chép thiếu mã (§6 — không tin 1 con số tự khai)
        if _pt_eng and abs(_pt_sum - _pt_eng) > max(1e5, 0.01 * _pt_eng):
            ACT.append(f"   ⚠️ Σ lệnh liệt kê {_tr(_pt_sum)} ≠ số engine {_tr(_pt_eng)} — "
                         f"plan có thể chép thiếu/thừa mã, kiểm trước khi duyệt.")
        _pt_bl = [b for b in (park_trim.get("blocked") or []) if isinstance(b, dict)]
        if _pt_bl:
            ACT.append("   ⛔ Không trim được: " + "; ".join(
                f"{b.get('ticker','?')} ({str(b.get('reason') or '')[:120]})" for b in _pt_bl[:6]))
        for _n in (park_trim.get("notes") or [])[:2]:
            ACT.append(f"   · {_note_text(_n)}")
        ACT.append("   ⚠️ Các lệnh BÁN này KHÔNG nằm trong danh sách lệnh chính ở trên — "
                     "duyệt riêng thì Mike/Bill mới đưa vào plan thực thi.")
    elif (pt_dec == "BLOCKED_ALL_NAMES" and _lk_pending
          and (_pt_bl_tk := {b.get("ticker") for b in (park_trim.get("blocked") or [])
                             if isinstance(b, dict)})
          and _pt_bl_tk <= set(_lk_pending)
          and _num(park_trim.get("pool_vnd")) > 0
          and _num(park_trim.get("park_mv_vnd")) <= 0.01 * _num(park_trim.get("pool_vnd"))):
        # Mọi mã PARK không bán được đều có phần CP chờ niêm yết VÀ phần PARK còn lại ≤1% pool
        # ⇒ không phải ca cần duyệt; vẫn hiện quy mô để người đọc tự thấy nếu khác thường.
        if not _lk_shown:
            INFO.append(_lk_info_line({}))
            _lk_shown = True
        INFO.append(f"🅿️ Trim PARK (L1): phiên này không bán được — PARK còn "
                     f"{_tr(_num(park_trim.get('park_mv_vnd')))} "
                     f"({_num(park_trim.get('park_mv_vnd')) / _num(park_trim.get('pool_vnd')) * 100:.2f}% pool), "
                     f"chỉ gồm {', '.join(t + '[PARK]' for t in sorted(_pt_bl_tk))} (CP chờ niêm yết / lô lẻ ở dòng ℹ️ trên).")
    elif (pt_dec == "BLOCKED_ALL_NAMES"
          and (_pt_bl_d := [b for b in (park_trim.get("blocked") or []) if isinstance(b, dict)])
          and all(_pt_sellable_lt_lot(b) is not None for b in _pt_bl_d)
          and not any("⚠️" in str(_n) for _n in (park_trim.get("notes") or []))
          and _num(park_trim.get("pool_vnd")) > 0
          and _num(park_trim.get("park_mv_vnd")) <= 0.03 * _num(park_trim.get("pool_vnd"))):
        # Trạng thái, không phải việc cần làm: MỌI mã PARK còn lại đều có số cp bán được (tradeQuantity
        # broker) < 1 lô (cp chưa giao dịch được / lô lẻ) và phần còn lại ≤3% pool ⇒ 1 dòng ℹ️ thay vì
        # "BỊ CHẶN" in đậm lặp mỗi ngày (user duyệt 27/10). Lý do chặn khác (đối soát lệch, ADV lỗi,
        # sellable ≥1 lô nhưng trần ADV chặn) và mọi note ⚠️ vẫn rơi xuống nhánh BLOCKED_* in đậm.
        _pt_pct = _num(park_trim.get("park_mv_vnd")) / _num(park_trim.get("pool_vnd")) * 100
        _pt_names = ", ".join(f"{b.get('ticker', '?')}[PARK] {_pt_sellable_lt_lot(b)}cp"
                              for b in _pt_bl_d[:6]) + " (bán được)"
        INFO.append(f"ℹ️ PARK còn {_tr(_num(park_trim.get('park_mv_vnd')))} ({_pt_pct:.2f}% pool) chưa bán được — "
                    f"{_pt_names}, <1 lô / chưa giao dịch được. Không cần xử lý.")
    elif pt_dec.startswith("BLOCKED_") or pt_dec in ("NO_SELL_POSSIBLE",):
        WARN.append(f"🅿️ **TRIM PARK (L1) BỊ CHẶN — {pt_dec}**: "
                     + ("; ".join(_note_text(n) for n in (park_trim.get("notes") or [])[:2])
                        or "không có lý do kèm theo — kiểm compute_park_trim.py."))
    elif pt_dec and (pt_dec not in ("NO_TRIM", "SKIP_STATE")
                     or any("⚠️" in str(_n) for _n in (park_trim.get("notes") or []))):
        # Suppress CHỈ NO_TRIM/SKIP_STATE ("không cần trim hôm nay" — user 2026-09-29). KHÔNG
        # NO_TRIM_STRUCTURE (arch-review 2026-09-29: đạt được khi PARK VƯỢT TRẦN nhưng không mã
        # nào trim được — cùng tình huống BLOCKED_ALL_NAMES vẫn in đậm, không phải ngày yên ổn).
        # Và dù NO_TRIM/SKIP_STATE, vẫn in nếu notes[] chứa ⚠️ thật (vd 'ENGINE CHƯA ĐỒNG BỘ'
        # compute_park_trim.py:422, hoặc cổ tức QUÁ HẠN :541) — suppress theo decision KHÔNG
        # được nuốt cảnh báo đi kèm.
        # arch-review round 2+3 (2026-09-29): 2 vòng cắt trước (từ đầu chuỗi, rồi từ vị trí ⚠️
        # ĐẦU TIÊN) đều lỡ cảnh báo trên note thật (700 ký tự, 2 dấu ⚠️ cách nhau 333 ký tự — ca
        # ZaloPay 2026-09-29). `_note_text()` nay KHÔNG cắt note mang ⚠️ — hiện toàn văn. Áp dụng
        # ĐỒNG NHẤT ở CẢ 6 chỗ render notes trong file (TRIM/BLOCKED_*/escape-hatch × L1+L2),
        # không chỉ 2 chỗ escape-hatch — note cổ tức được append TRƯỚC mọi nhánh decision
        # (compute_park_trim.py:541, trước :554/:568.../:762) nên cả 6 nhánh đều cần.
        _pt_notes = park_trim.get("notes") or []
        _pt_warn = [n for n in _pt_notes if "⚠️" in str(n)]
        _pt_show = _pt_warn or _pt_notes[:1]
        if not (pt_dec == "TRIM" and pt_merged and not _pt_warn):   # đã merge ⇒ lệnh + lý do nằm ở mục LỆNH
            _route(f"🅿️ L1 trim PARK: {pt_dec}"
                       + (f" — {'; '.join(_note_text(n) for n in _pt_show[:2])}" if _pt_show else ""),
                   warn=pt_dec not in ("TRIM", "NO_TRIM", "SKIP_STATE"))   # NO_TRIM_STRUCTURE/decision lạ ⇒ WARN (§4)
except Exception as _e:      # fail-open: một khối báo cáo không được chặn plan
    WARN.append(f"⚠️ Không render được khối L1 park_trim ({type(_e).__name__}: {_e}) — "
                 f"đọc thẳng `park_trim_proposal` trong file plan trước khi duyệt.")

# ── MỤC RIÊNG 2: L2 jit_unpark_proposal ─────────────────────────────────────────────────
try:
    if jit_dec == "JIT" and (jit_report_orders or jit_amends) and not jit_merged:
        _jit_sum = sum(_o_val(o) for o in jit_orders)
        _for = sorted({str(o.get("for_ticker") or o.get("for_order_id") or "?")
                       for o in jit_orders})
        ACT.append(f"💧 **ĐỀ XUẤT BÁN PARK TÀI TRỢ LỆNH MUA (L2/JIT) — {len(jit_orders)} lệnh "
                     f"BÁN, Σ {_tr(_jit_sum)} — CẦN DUYỆT RIÊNG**")
        if jit_orders:
            ACT.append(f"   Tài trợ cho: {', '.join(_for)}")
            ACT.append(f"   BÁN: {_tickers_line(jit_orders)}")
        for _a in jit_amends:
            _st = str(_a.get("status") or "?")
            _icon = {"FUNDED_BY_JIT": "✅", "FUNDED_BY_CASH": "✅",
                     "SHRINK": "⚠️", "DROP": "⛔"}.get(_st, "⚠️")
            ACT.append(f"   {_icon} MUA {_a.get('ticker','?')}: {_st} — kế hoạch "
                         f"{_a.get('qty_plan')}cp → cuối cùng {_a.get('qty_final')}cp "
                         f"({_tr(_num(_a.get('target_value_final_vnd')))}); "
                         f"{str(_a.get('reason') or '')[:150]}")
        _jt_bl = [b for b in (jit_prop.get("blocked") or []) if isinstance(b, dict)]
        if _jt_bl:
            ACT.append("   ⛔ Không bán được: " + "; ".join(
                f"{b.get('ticker','?')} ({str(b.get('reason') or '')[:120]})" for b in _jt_bl[:6]))
        for _n in (jit_prop.get("notes") or [])[:2]:
            ACT.append(f"   · {_note_text(_n)}")
        ACT.append("   ⚠️ Duyệt lệnh MUA ở trên = duyệt luôn các lệnh BÁN PARK này (không bán "
                     "thì không đủ tiền mua) — nếu KHÔNG muốn bán PARK, phải bỏ/co lệnh mua.")
    elif jit_dec.startswith("BLOCKED_") or jit_dec in ("NO_SELL_POSSIBLE",):
        WARN.append(f"💧 **BÁN PARK TÀI TRỢ (L2/JIT) BỊ CHẶN — {jit_dec}**: "
                     + ("; ".join(_note_text(n) for n in (jit_prop.get("notes") or [])[:2])
                        or "không có lý do kèm theo — kiểm compute_jit_unpark.py.")
                     + " ⇒ lệnh mua có thể THIẾU TIỀN lúc 09:05 (triệu chứng WAIT_CASH).")
    elif jit_dec and (jit_dec not in ("NO_JIT_NEEDED", "NO_TRIGGER")
                      or any("⚠️" in str(_n) for _n in (jit_prop.get("notes") or []))):
        # NO_JIT_NEEDED/NO_TRIGGER = "L2 không chạy vì không có lệnh mua cần tài trợ", đúng
        # thiết kế mọi ngày HOLD/không-mua — bỏ dòng lặp lại vô nghĩa (user 2026-09-29, ca
        # thật: SpaceX 2026-09-30 0 lệnh vẫn in "L2 JIT unpark: NO_TRIGGER" mỗi ngày).
        # arch-review round 2 (2026-09-29): comment bản trước SAI — compute_jit_unpark.py:565-572
        # append ⚠️ 'CẦN RÚT Trứng vàng' NGOÀI `if triggered:` (:481-482) nên vẫn xuất hiện dù
        # decision=NO_JIT_NEEDED (egg đẩy cash qua JIT_TRIGGER_FRAC, any_trigger vẫn False, xem
        # comment :527-537 của chính file đó). Check ⚠️ ở đây KHÔNG phải phòng thủ lý thuyết —
        # đây là đường THẬT, 2 account live đều đang giữ Trứng vàng. `_note_text()` (round 3, xem
        # docstring) hiện TOÀN VĂN note mang ⚠️, không cắt — cùng hàm dùng ở cả 6 chỗ render notes.
        # Note "tới Ncp có thể cần Trứng vàng (≤X)" của từng lệnh mua đã nằm trong dòng 🥚 ACT (cùng nguồn
        # số: Σ mua ở trần đuổi giá − tiền mặt − JIT) ⇒ khi dòng 🥚 đã in thì bỏ để khỏi nói 2 lần (27/10).
        _jt_notes = [n for n in (jit_prop.get("notes") or [])
                     if not (_egg_line_shown and "có thể cần Trứng vàng" in str(n))]
        _jt_warn = [n for n in _jt_notes if "⚠️" in str(n)]
        _jt_show = _jt_warn or _jt_notes[:1]
        if jit_dec not in ("NO_JIT_NEEDED", "NO_TRIGGER") or _jt_warn:
            _route(f"💧 L2 JIT unpark: {jit_dec}"
                   + (f" — {'; '.join(_note_text(n) for n in _jt_show[:2])}" if _jt_show else ""),
                   warn=jit_dec not in ("NO_JIT_NEEDED", "NO_TRIGGER", "JIT"))
except Exception as _e:      # fail-open
    WARN.append(f"⚠️ Không render được khối L2 jit_unpark ({type(_e).__name__}: {_e}) — "
                 f"đọc thẳng `jit_unpark_proposal` trong file plan trước khi duyệt.")

if reasons:
    lines.append("💡 Vì sao:")
    for r in reasons[:6]:
        lines.append(f"  – {r}")

# ── Khối kiểm tra tự động dựng ở shell phía trên (vị thế sau plan / lịch LAG / nhất quán LAG).
# Phân loại THEO BẤT BIẾN, không theo văn bản: khối có ⚠️/⛔/🔴 ⇒ WARN nguyên văn; khối chỉ có ✅ ⇒ BỎ
# (xác nhận thuần, §4); dòng còn lại (vd '⏳ Chờ DD … đứng NGOÀI plan') ⇒ INFO.
_ok_checks = []     # nhãn các kiểm tra tự động đã chạy và sạch ⇒ gộp 1 dòng cuối (không 1 dòng/khối)
for _env, _lbl in (("DRIFT_BLOCK", "vị thế sau plan"), ("LAGCAL_BLOCK", "lịch LAG"),
                   ("LAGCHK_BLOCK", "nhất quán LAG")):
    _bl = [_x for _x in os.environ.get(_env, "").splitlines() if _x.strip()]
    if not _bl:
        continue
    if any(m in "\n".join(_bl) for m in ("⚠️", "⛔", "🔴")):
        WARN.append("\n".join(_bl))     # cả khối = 1 cảnh báo
    else:
        if any(_x.lstrip().startswith("✅") for _x in _bl):
            _ok_checks.append(_lbl)
        INFO.extend(_x for _x in _bl if not _x.lstrip().startswith("✅"))

_nc = os.environ.get("NOWCAST_BLOCK", "").strip()   # nowcast hàng hoá (ZaloPay, display-only, shell phía trên)

# Trạng thái duyệt — LÊN ĐẦU (việc đầu tiên người đọc cần biết), kèm số cảnh báo để biết có cần cuộn xuống.
if approved:
    # approved_by có thể là chuỗi audit dài (ghi đủ căn cứ ủy quyền) — hiển thị gọn,
    # chi tiết đầy đủ vẫn nằm trong file plan.
    approver_short = str(approved).split("(")[0].strip() or str(approved)[:30]
    _status = f"✅ **ĐÃ DUYỆT** ({approver_short}) — bot tự đặt lệnh 09:05, không cần thao tác thêm."
elif requires or orders:
    _status = "⏳ **CHỜ DUYỆT** — nhắn Mike để duyệt (chưa duyệt: bot KHÔNG đặt lệnh, preflight 08:45 báo RED)."
else:
    _status = "✅ HOLD 0 lệnh — không cần duyệt."
_nw = len([w for w in WARN if not w.startswith(" ")])    # mỗi entry WARN = 1 cảnh báo; dòng con thụt đầu dòng không đếm
if _nw:
    _status += f" · ⚠️ **{_nw} cảnh báo** (mục CẢNH BÁO cuối)"
HDR[HDR.index("@@STATUS@@")] = _status

out = list(HDR)
if ACT:
    out += ["", "**🔔 CẦN LÀM / QUYẾT ĐỊNH**"] + ACT
out += ["", _ord_title] + ORD
if WARN:
    out += ["", "**⚠️ CẢNH BÁO**"] + WARN
if INFO:
    out += ["", "**ℹ️ GHI CHÚ** (không cần quyết định)"] + INFO
if _nc:
    out += [""] + _nc.splitlines()
out.append("")
if _ok_checks:
    out.append("✔ Kiểm tự động không bất thường: " + " · ".join(_ok_checks) + ".")
out.append(f"_(DollarBill lập, gửi {today} {now_ict})_")

print("OK")
print("\n".join(out))
PY
)

STATUS="$(echo "$RESULT" | head -1)"

if [ "$STATUS" = "ESCALATE" ]; then
  REASON="$(echo "$RESULT" | sed -n '2p')"
  DETAIL="$(echo "$RESULT" | tail -n +3)"
  SC_TAG=""
  [ "$SECOND_CHANCE" = "1" ] && SC_TAG=" [second-chance 23:00 — lần kiểm tra CUỐI trong đêm, sáng mai chỉ còn ops_health_check 08:20]"
  MSG="🔴 [$TODAY $NOW_ICT] Plan T+1 CHƯA SẴN SÀNG ($REASON)$SC_TAG — $DETAIL Cần Mike hoặc user kiểm tra thủ công, KHÔNG tự phục hồi."
  echo "$MSG"
  if [ "$DRY_RUN" = "0" ]; then
    "$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "$MSG" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
    _QPAYLOAD="{\"reason\":\"$REASON\",\"detail\":$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$DETAIL"),\"expected_date\":\"$EXPECTED_DATE\",\"account\":\"$ACCOUNT\",\"second_chance\":$SECOND_CHANCE,\"checked_at\":\"$TODAY $NOW_ICT\"}"
    # GATE_BLOCK_PLAN_T1_BEGIN — question CÓ CHỦ + HẠN + LỆNH RECOVER, sweep nhắc tới khi marker
    # "đã gửi plan" (artifact do CHÍNH script này ghi khi gửi OK) được ghi SAU lúc mở VÀ md5 khớp
    # plan hiện tại (`probe plan-t1`; marker cũ của lượt 21:00 KHÔNG đóng — arch-review B2) (retro
    # 10-16→10-19 Pattern 1, phương án A 2026-10-20). Hết ngày T+1 ⇒ EXPIRED, 1 tin cuối rồi dừng. Topic THEO NGÀY `plan-t1-not-ready-<ngày T+1>-<ACC>` (vòng 3
    # arch-review B1: topic không ngày `plan-t1-not-ready-<ACC>` là chuỗi con của câu legacy cùng
    # topic ⇒ đóng/mở lây hai chiều; bus thật có 10 câu legacy pending từ 10-16) + payload cũ. Idempotent theo (ACC, ngày T+1): lượt 23:00
    # khi câu 21:xx còn MỞ ⇒ không mở câu thứ hai (ALREADY_OPEN); khi câu đó đã đóng/hết hạn mà plan
    # lại hỏng ⇒ mở câu MỚI key `-r2` (xem dưới). Helper hỏng (không in OPENED/ALREADY_) ⇒ rơi về đúng lệnh post cũ —
    # thà trùng còn hơn mất câu hỏi của account tiền thật.
    _GB_KEY="${EXPECTED_DATE:-$TODAY}-${ACCOUNT}"
    _gb_open() {   # $1=key  $2=topic
      timeout 60 python3 "$ROOT/bin/gate_block_question.py" open --gate plan-t1-not-ready \
        --key "$1" --topic "$2" \
        --owner "Mike (dispatch DollarBill dựng lại plan)" --deadline "${EXPECTED_DATE:-$TODAY}T08:30" \
        --recover "DISPATCH_FROM=Mike $ROOT/bin/dispatch.sh DollarBill \"dựng lại plan T+1 ${EXPECTED_DATE} ${ACCOUNT}: $REASON\" && $ROOT/bin/send_plan_report.sh --account $ACCOUNT --second-chance" \
        --probe "python3 $ROOT/bin/gate_block_question.py probe plan-t1 --account $ACCOUNT --date ${EXPECTED_DATE:-$TODAY} --marker-dir $MARKER_DIR --plan-dir $WORKDIR/data/trade_plans" \
        --expires-at "${EXPECTED_DATE:-$TODAY}T23:59" --max-reminders 30 \
        --reason "Plan T+1 chưa sẵn sàng ($REASON)" --thread "$DISCORD_PLAN_CHANNEL" \
        --remind-every-min 60 --extra "$_QPAYLOAD" 2>&1
    }
    _GB_OUT="$(_gb_open "$_GB_KEY" "plan-t1-not-ready-${_GB_KEY}")"
    echo "$_GB_OUT"
    # ALREADY_CLOSED/ALREADY_EXPIRED: câu cũ đã tắt mà plan lại hỏng (23:00 sau khi 21:45 đóng) ⇒ mở
    # câu MỚI qua helper với key `-r2` (chủ + nhắc + ack riêng; sweep theo dõi). Topic `-r2` đặt
    # TIỀN TỐ (`plan-t1-not-ready-r2-<ngày>-<ACC>`) để KHÔNG chứa topic cũ làm chuỗi con — ack cũ
    # không tắt lây câu mới khỏi CHECK5 (NB-A arch-review vòng 3).
    if printf '%s\n' "$_GB_OUT" | grep -qE '^gate_block_question: ALREADY_(CLOSED|EXPIRED)([[:space:]]|$)'; then
      _GB_OUT="$(_gb_open "${_GB_KEY}-r2" "plan-t1-not-ready-r2-${_GB_KEY}")"
      echo "$_GB_OUT"
    fi
    # Chỉ bỏ qua khi helper XÁC NHẬN có câu hỏi đang sống. Còn lại (helper hỏng, r2 cũng đã tắt) ⇒
    # post trần như cũ — thà trùng còn hơn mất câu hỏi của account tiền thật.
    if ! printf '%s\n' "$_GB_OUT" | grep -qE '^gate_block_question: (OPENED|ALREADY_OPEN|ALREADY_POSTING)([[:space:]]|$)'; then
      "$ROOT/bin/append_event.sh" Mike question "plan-t1-not-ready-${_GB_KEY}" "$_QPAYLOAD" \
        2>/dev/null || true
    fi
    # GATE_BLOCK_PLAN_T1_END
  else
    echo "[send_plan_report] DRY-RUN — không gửi notify/bus."
  fi
  exit 0
fi

if [ "$STATUS" != "OK" ]; then
  # $RESULT rỗng/không đúng format (arch-reviewer 2026-07-30: "orders": null từng crash python
  # heredoc TypeError trước khi in được dòng nào — traceback ra stderr, $RESULT rỗng) KHÔNG
  # được coi ngầm là thành công. Trước đây rơi xuống nhánh "đã gửi OK" phía dưới, ghi marker
  # "đã gửi" dù KHÔNG gửi gì thật — làm mất second-chance 23:00 trong im lặng tuyệt đối.
  MSG="🔴 [$TODAY $NOW_ICT] Plan T+1 LỖI KHÔNG XÁC ĐỊNH (render_crashed, status='${STATUS:-<rỗng>}') — script bên trong crash hoặc trả kết quả không đúng format, xem log. Cần Mike/user kiểm tra thủ công, KHÔNG tự phục hồi. Plan CHƯA được coi là đã gửi."
  echo "$MSG"
  if [ "$DRY_RUN" = "0" ]; then
    "$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true
    "$ROOT/bin/notify_thread.sh" "$MSG" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
    "$ROOT/bin/append_event.sh" Mike question "plan-t1-render-crashed-${ACCOUNT}" \
      "{\"status\":\"${STATUS}\",\"expected_date\":\"$EXPECTED_DATE\",\"account\":\"$ACCOUNT\",\"checked_at\":\"$TODAY $NOW_ICT\"}" \
      2>/dev/null || true
  fi
  exit 1
fi

SUMMARY="$(echo "$RESULT" | tail -n +2)"

# Ngữ cảnh second-chance: user cần biết đây là bản gửi lại/gửi muộn, không phải report 21:00 thường.
if [ "$PLAN_CHANGED_AFTER_SEND" = "1" ]; then
  SUMMARY="🔁 **PLAN ĐÃ THAY ĐỔI sau lần gửi 21:00** — bản dưới đây là bản MỚI trên đĩa, cần duyệt lại theo bản này (second-chance 23:00):
$SUMMARY"
elif [ "$SECOND_CHANCE" = "1" ]; then
  SUMMARY="🔁 **GỬI MUỘN (second-chance 23:00)** — lần gửi 21:00 không thành công/plan chưa sẵn sàng lúc đó, đây là lần đầu plan này tới tay user:
$SUMMARY"
fi

echo "$SUMMARY"
if [ "$DRY_RUN" = "0" ]; then
  "$ROOT/bin/notify.sh" "$SUMMARY" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$SUMMARY" "$DISCORD_PLAN_CHANNEL" 2>/dev/null || true
fi

# Marker "đã gửi OK cho (account, ngày T+1)" — nguồn idempotency cho second-chance.
# Dry-run KHÔNG ghi marker vào chỗ thật (sẽ làm 23:00 tưởng đã gửi rồi) — chỉ ghi khi
# test tự override SEND_PLAN_MARKER_DIR sang sandbox.
if [ -n "$MARKER_FILE" ] && { [ "$DRY_RUN" = "0" ] || [ -n "${SEND_PLAN_MARKER_DIR:-}" ]; }; then
  mkdir -p "$MARKER_DIR"
  SENT_MODE="normal"; [ "$SECOND_CHANCE" = "1" ] && SENT_MODE="second-chance"
  python3 - "$MARKER_FILE" "$ACCOUNT" "$EXPECTED_DATE" "$PLAN_FILE" "$CUR_HASH" "$SENT_MODE" "$TODAY $NOW_ICT" << 'PYMARK' || true
import sys, json, os, tempfile
marker, acct, pdate, pfile, md5, mode, sent_at = sys.argv[1:8]
rec = {"account": acct, "plan_date": pdate, "plan_file": pfile,
       "content_md5": md5, "mode": mode, "sent_at": sent_at}
fd, tmp = tempfile.mkstemp(dir=os.path.dirname(marker))
with os.fdopen(fd, "w") as fh:
    json.dump(rec, fh, ensure_ascii=False, indent=1)
os.replace(tmp, marker)
PYMARK
  echo "[send_plan_report] marker: $MARKER_FILE (md5 $CUR_HASH)"
fi
echo "[send_plan_report] Done — $NOW_ICT"
