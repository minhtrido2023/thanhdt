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
TODAY="$(date +%Y-%m-%d)"
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
DISCORD_PLAN_CHANNEL="1521183164364754974"

EXPECTED_DATE="$(cd "$WORKDIR" && python3 -c "
import datetime as dt
from trading_bot.vn_market import next_trading_day
print(next_trading_day(dt.date.today()))
" 2>/dev/null)"

# Plan file mới nhất theo mtime (Bill ghi vào data/trade_plans/plan_<account>_<date>.json)
PLAN_FILE="$(ls -t "$WORKDIR"/data/trade_plans/plan_${ACCOUNT}_*.json 2>/dev/null | head -1)"

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

RESULT=$(cd "$WORKDIR" && python3 - "$PLAN_FILE" "$EXPECTED_DATE" "$TODAY" "$NOW_ICT" "$ACCOUNT" << 'PY'
import sys, json

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
orders = plan.get("orders", [])
summary = plan.get("summary", {}) if isinstance(plan.get("summary"), dict) else {}
action  = summary.get("action", "HOLD" if not orders else "TRADE")
reasons = summary.get("reasons") or []
approved = plan.get("approved_by")
requires = plan.get("requires_user_approval", False)

lines = [f"📋 **Kế hoạch giao dịch ngày mai {date} — Account {acct}**"]

src_vn = " (nguồn DT5G đầy đủ)" if src == "DT5G_macro" else (f" (nguồn {src})" if src else "")
nav_str = f"{nav:,.0f}đ" if isinstance(nav, (int, float)) else "n/a"
lines.append(f"🧭 Thị trường: {state}{src_vn} · NAV cơ sở: {nav_str}")

# Transition context nếu có (ZaloPay Option A)
tsched = plan.get("transition_schedule") or []
tday = next((t for t in tsched if t.get("date") == date), None)
if tday:
    lines.append(f"🔄 Lộ trình chuyển đổi danh mục: ngày {tday.get('day')}/{len(tsched)} theo kế hoạch Option A đã duyệt")

if orders:
    # DCF check (Pha 2, informational — user directive 2026-07-15: PHẢI hiển thị trong text
    # duyệt plan, không chỉ nằm trong JSON). Echo field dcf_check nếu plan có; BUY thiếu field
    # (plan DollarBill hiện không populate) → tự tính fallback từ cache local (KHÔNG BQ live).
    # Fail-safe toàn phần: import/tính lỗi → bỏ dòng DCF, KHÔNG chặn report duyệt plan.
    try:
        from trading_bot.strategies import (_dcf_check_for_order, format_dcf_check,
                                            log_dcf_history)
        from dcf_valuation import DCF_DISCLAIMER
    except Exception:
        _dcf_check_for_order = format_dcf_check = log_dcf_history = None
        DCF_DISCLAIMER = ""
    dcf_shown = False
    buys  = [o for o in orders if str(o.get("side","")).lower() in ("buy","mua","b")]
    sells = [o for o in orders if str(o.get("side","")).lower() in ("sell","ban","s")]
    lines.append(f"🎯 Hành động: **{len(orders)} lệnh** ({len(sells)} bán, {len(buys)} mua):")
    for o in orders:
        side_vn = "BÁN" if str(o.get("side","")).lower() in ("sell","ban","s") else "MUA"
        is_buy = side_vn == "MUA"
        ticker = o.get("ticker","?")
        qty    = o.get("quantity", o.get("qty","?"))
        price  = o.get("ref_price", o.get("mtm_price_ref", o.get("price")))
        px = f"~{price:,.0f}đ" if isinstance(price, (int, float)) else "giá thị trường"
        val = o.get("est_value_vnd", o.get("est_value"))
        val_s = f" (~{val/1e6:,.1f}tr)" if isinstance(val, (int, float)) else ""
        note = o.get("note", "")
        note_s = f" — {note[:90]}" if note else ""
        lines.append(f"  • {side_vn} {ticker} {qty}cp @ {px}{val_s}{note_s}")
        if format_dcf_check:
            dcf = o.get("dcf_check")
            if not dcf and is_buy and _dcf_check_for_order and isinstance(price, (int, float)):
                try:
                    dcf = _dcf_check_for_order(ticker, price, date)
                except Exception:
                    dcf = None
            dcf_s = format_dcf_check(dcf, "buy" if is_buy else "sell",
                                     has_override=bool(o.get("dcf_override_reason")))
            if dcf_s:
                lines.append(f"      ↳ {dcf_s}")
                dcf_shown = True
                if log_dcf_history:
                    log_dcf_history(ticker, dcf, "send_plan_report", asof=date)
            if is_buy and o.get("dcf_override_reason"):
                lines.append(f"      ↳ lý do override DCF: {str(o['dcf_override_reason'])[:120]}")
    if dcf_shown and DCF_DISCLAIMER:
        lines.append(f"ℹ️ _{DCF_DISCLAIMER}_")
else:
    lines.append(f"🎯 Hành động: **GIỮ NGUYÊN (HOLD)** — không có lệnh nào ngày mai.")

if reasons:
    lines.append("💡 Vì sao:")
    for r in reasons[:6]:
        lines.append(f"  – {r}")

if approved:
    # approved_by có thể là chuỗi audit dài (ghi đủ căn cứ ủy quyền) — hiển thị gọn,
    # chi tiết đầy đủ vẫn nằm trong file plan.
    approver_short = str(approved).split("(")[0].strip() or str(approved)[:30]
    lines.append(f"✅ Trạng thái: ĐÃ DUYỆT ({approver_short}) — bot tự thực thi 09:05 sáng mai, không cần thao tác gì thêm.")
elif requires or orders:
    lines.append("⏳ Trạng thái: **CHỜ DUYỆT** — chưa duyệt thì preflight 08:45 báo RED và bot KHÔNG đặt lệnh. Duyệt bằng cách nhắn Mike.")
else:
    lines.append("✅ Trạng thái: HOLD 0 lệnh — không cần duyệt, bot trực phiên đồng bộ trạng thái.")

lines.append(f"_(DollarBill lập, gửi {today} {now_ict})_")

print("OK")
print("\n".join(lines))
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
    "$ROOT/bin/append_event.sh" Mike question "plan-t1-not-ready-${ACCOUNT}" \
      "{\"reason\":\"$REASON\",\"detail\":$(python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "$DETAIL"),\"expected_date\":\"$EXPECTED_DATE\",\"account\":\"$ACCOUNT\",\"second_chance\":$SECOND_CHANCE,\"checked_at\":\"$TODAY $NOW_ICT\"}" \
      2>/dev/null || true
  else
    echo "[send_plan_report] DRY-RUN — không gửi notify/bus."
  fi
  exit 0
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
