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
DISCORD_PLAN_CHANNEL="plan_approval"

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
import sys, json, os

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

try:
    with open("deploy_golive_dt5g_v4/golive_state_today.json") as f:
        golive = json.load(f)
    plan_src = plan.get("state_source")
    golive_src = golive.get("source")
    if plan_src and golive_src and plan_src != golive_src:
        escalate("plan_state_source_mismatch",
                 f"{plan_file}: state_source={plan_src!r} nhưng golive_state_today.json (nguồn "
                 f"DT5G thật hôm nay) nói {golive_src!r} — plan có thể được sinh từ state cũ.")
        sys.exit(0)
except FileNotFoundError:
    pass  # không phải nguồn bắt buộc; thiếu file thì bỏ qua assert này, không chặn plan
except Exception:
    pass

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
_capit_buys = [o for o in orders if isinstance(o, dict)
               and str(o.get("book", "")).upper() == "CAPIT"
               and str(o.get("side", "")).lower() in ("buy", "mua", "b")]
if _capit_buys:
    try:
        # python này chạy sau `cd "$WORKDIR"` (dòng RESULT=$(...)), nên đường dẫn tương đối
        _st = json.load(open(os.path.join("data", "golive_v23_status.json"), encoding="utf-8"))
        _tg = ((_st.get("capit_slot_targets") or {}).get(acct)) or {}
        _slot = _tg.get("capit_slot_target_vnd")
        if _slot:
            _actual = sum(float(o.get("actual_vnd") or 0)
                          or float(o.get("qty") or o.get("quantity") or 0) * float(_order_price(o) or 0)
                          for o in _capit_buys)
            _target = float(_slot) * len(_capit_buys)
            _dev = (_actual - _target) / _target if _target > 0 else 0.0
            if abs(_dev) > 0.10:
                capit_note = (f"⚠️ CAPIT: Σ lệnh mua {_actual/1e6:,.0f}tr vs mục tiêu "
                              f"{_target/1e6:,.0f}tr ({len(_capit_buys)} mã × "
                              f"{_slot/1e6:,.1f}tr) — lệch {_dev*100:+.1f}%. Nếu KHÔNG do trần "
                              f"%ADV/thiếu cash thì kiểm tra đã nhân capit_size hai lần chưa "
                              f"(lỗi thật 07-21). Nguồn mục tiêu: golive_v23_status.json "
                              f"`capit_slot_targets`.")
            else:
                capit_note = (f"✅ CAPIT: Σ lệnh mua {_actual/1e6:,.0f}tr khớp mục tiêu "
                              f"{_target/1e6:,.0f}tr (lệch {_dev*100:+.1f}%)")
        else:
            capit_note = ("⚠️ CAPIT: có lệnh CAPIT nhưng status chưa publish "
                          "`capit_slot_targets` cho account này — KHÔNG đối chiếu được cỡ deploy, "
                          "người duyệt tự kiểm Σ VND vs NAV_book_LAG × capit_size.")
    except Exception as _e:      # fail-open: không chặn plan vì một dòng đối chiếu
        capit_note = f"⚠️ CAPIT: không đối chiếu được cỡ deploy ({type(_e).__name__}: {_e})"

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
    # Due-diligence tổng hợp cho MỌI lệnh MUA (mandate user 2026-07-21) — thanh khoản/universe/
    # cơ học tín hiệu/cờ bất thường/FA thô. skip_dcf=True vì dòng DCF đã echo riêng ngay trên.
    try:
        from trading_bot.due_diligence import run_due_diligence, DD_DISCLAIMER
    except Exception:
        run_due_diligence = None
        DD_DISCLAIMER = ""
    dcf_shown = False
    dd_shown = False
    buys  = [o for o in orders if str(o.get("side","")).lower() in ("buy","mua","b")]
    sells = [o for o in orders if str(o.get("side","")).lower() in ("sell","ban","s")]
    lines.append(f"🎯 Hành động: **{len(orders)} lệnh** ({len(sells)} bán, {len(buys)} mua):")
    if price_verify_note:
        lines.append(f"   {price_verify_note}")
    if capit_note:
        lines.append(f"   {capit_note}")
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
                                     has_override=bool(o.get("dcf_override_reason")),
                                     ticker=ticker)
            if dcf_s:
                lines.append(f"      ↳ {dcf_s}")
                dcf_shown = True
                if log_dcf_history:
                    log_dcf_history(ticker, dcf, "send_plan_report", asof=date)
            if is_buy and o.get("dcf_override_reason"):
                lines.append(f"      ↳ lý do override DCF: {str(o['dcf_override_reason'])[:120]}")
        if is_buy and run_due_diligence:
            dd_ctx = {"asof": date, "skip_dcf": True}
            if isinstance(price, (int, float)):
                dd_ctx["price"] = price
            if isinstance(val, (int, float)):
                dd_ctx["est_value_vnd"] = val
            dd_s = run_due_diligence(ticker, o.get("book") or o.get("play_type"), dd_ctx)
            if dd_s:
                for dl in str(dd_s).splitlines():
                    lines.append(f"      ↳ {dl.strip()}")
                dd_shown = True
    if dcf_shown and DCF_DISCLAIMER:
        lines.append(f"ℹ️ _{DCF_DISCLAIMER}_")
    if dd_shown and DD_DISCLAIMER:
        lines.append(f"ℹ️ _{DD_DISCLAIMER}_")
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
