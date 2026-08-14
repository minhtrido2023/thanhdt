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
    from trading_bot.plan import preview_margin_day, margin_day_approval
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
                               "chạy bằng VỐN TỰ CÓ** — khối lượng tính cho 1,3× vốn mà chỉ "
                               "có 1,0× vốn; triệu chứng sẽ là WAIT_CASH, không phải lỗi rõ.")
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
                f"   ⛔ **CẦN DUYỆT RIÊNG CHO ĐÒN BẨY** (khác với duyệt plan thường): {_aerr}")
            margin_note.append(
                f"   Duyệt xong, Mike chạy: `python3 mike/bin/approve_margin_day.py "
                f"--account {acct} --date {date} --approved-by \"...\"`. Không duyệt ⇒ bot TỰ "
                f"GỠ đòn bẩy và chạy {len(_pv['orders'])} lệnh này bằng VỐN TỰ CÓ (không chặn "
                f"lệnh).")
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

def _tr(v):
    return f"{v/1e6:,.1f}tr"

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

lines = [f"📋 **Kế hoạch giao dịch ngày mai {date} — Account {acct}**"]
for _m in margin_note:
    lines.append(_m)

src_vn = " (nguồn DT5G đầy đủ)" if src == "DT5G_macro" else (f" (nguồn {src})" if src else "")
nav_str = f"{nav:,.0f}đ" if isinstance(nav, (int, float)) else "n/a"
lines.append(f"🧭 Thị trường: {state}{src_vn} · NAV cơ sở: {nav_str}")
# Đặt CẠNH dòng thị trường (không nằm trong nhánh `if orders:`) — plan HOLD cũng phải nói rõ
# đã/chưa đối chiếu được regime, đó là ca gate câm dễ lọt nhất.
if state_verify_note:
    lines.append(f"   {state_verify_note}")

# DT4-gate candidate streak clock — đã wire vào eod_trading_report.sh (2026-07-10) nhưng
# CHƯA vào plan T+1 report này (khoảng trống user phát hiện 2026-08-11). Tái dùng
# build_dt_gate_line() của dna_report.py (KHÔNG re-implement, §2/§3) — cùng 1 hàm, cùng
# cache 5', chỉ khác điểm gọi. Fail-safe: lỗi BQ/import → bỏ dòng, không chặn report.
try:
    from dna_report import build_dt_gate_line
    _dt_line = build_dt_gate_line(html=False)
    if _dt_line:
        lines.append("🛰️ " + _dt_line)
except Exception:
    pass

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
    if pt_orders or jit_orders:
        lines.append(f"   ➕ Ngoài {len(orders)} lệnh trên, plan còn **{len(pt_orders) + len(jit_orders)} "
                     f"lệnh BÁN PARK đề xuất** (L1 trim {len(pt_orders)} + L2 JIT {len(jit_orders)}) — "
                     f"xem 2 mục riêng ở cuối, CẦN DUYỆT.")
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
        # Funding note NGAY CẠNH lệnh mua — user đọc lệnh mua riêng lẻ không được phép hoảng
        # vì tưởng thiếu tiền (SSI 75,3tr vs cash 4,8tr, plan 08-07).
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
                        f"      ↳ 💧 **Tiền đâu ra:** lệnh này được tài trợ bằng cách {_fp}"
                        f"{_net_s} ⇒ mua NGUYÊN lệnh {_a.get('qty_final')}cp "
                        f"(tiền mặt {_tr(_num(_a.get('cash_before_vnd')))} → "
                        f"{_tr(_num(_a.get('cash_after_vnd')))}). Chi tiết ở mục L2 bên dưới — "
                        f"các lệnh bán PARK đó CẦN DUYỆT cùng lệnh mua này.")
                elif _st == "FUNDED_BY_CASH":
                    lines.append(f"      ↳ 💧 Tiền đâu ra: đủ tiền mặt sẵn có, KHÔNG cần bán PARK.")
                elif _st == "SHRINK":
                    lines.append(
                        f"      ↳ ⚠️ **Lệnh bị CO** {_a.get('qty_plan')}cp → {_a.get('qty_final')}cp "
                        f"dù đã {_fp}{_net_s} — {_rs}")
                elif _st == "DROP":
                    lines.append(
                        f"      ↳ ⛔ **Lệnh bị BỎ** (kế hoạch {_a.get('qty_plan')}cp) dù đã cố "
                        f"bán PARK — {_rs}")
                elif _st:
                    lines.append(f"      ↳ ⚠️ JIT status={_st} — {_rs}")
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
            # dd_override_reason đi vào ctx để dòng cờ đỏ tự biết đã có lý do override hay chưa
            # (mirror has_override của format_dcf_check) — thiếu lý do thì hiện "cần
            # dd_override_reason" NGAY tại bước user duyệt plan, đúng chỗ quyết định.
            dd_ctx = {"asof": date, "skip_dcf": True, "side": "buy",
                      "dd_override_reason": o.get("dd_override_reason") or ""}
            if isinstance(price, (int, float)):
                dd_ctx["price"] = price
            if isinstance(val, (int, float)):
                dd_ctx["est_value_vnd"] = val
            dd_s = run_due_diligence(ticker, o.get("book") or o.get("play_type"), dd_ctx)
            if dd_s:
                for dl in str(dd_s).splitlines():
                    lines.append(f"      ↳ {dl.strip()}")
                dd_shown = True
            if o.get("dd_override_reason"):
                lines.append(f"      ↳ lý do override DD: {str(o['dd_override_reason'])[:120]}")
    if dcf_shown and DCF_DISCLAIMER:
        lines.append(f"ℹ️ _{DCF_DISCLAIMER}_")
    if dd_shown and DD_DISCLAIMER:
        lines.append(f"ℹ️ _{DD_DISCLAIMER}_")
else:
    lines.append(f"🎯 Hành động: **GIỮ NGUYÊN (HOLD)** — không có lệnh nào ngày mai.")

# ── MỤC RIÊNG 1: L1 park_trim_proposal ──────────────────────────────────────────────────
# Ngang hàng với orders[], KHÔNG phải câu phụ trong đoạn văn: đây là lệnh BÁN THẬT cần user
# duyệt riêng (chúng KHÔNG nằm trong orders[] mà bot đọc lúc 09:05).
try:
    if pt_dec == "TRIM" and pt_orders:
        _pt_sum = sum(_o_val(o) for o in pt_orders)
        _pt_eng = _num(park_trim.get("trim_proposed_vnd"))
        _tgt = park_trim.get("target_park")
        _tgt_s = f"{float(_tgt)*100:.0f}%" if isinstance(_tgt, (int, float)) else "?"
        lines.append(f"🅿️ **ĐỀ XUẤT TRIM PARK (L1) — {len(pt_orders)} lệnh BÁN, "
                     f"Σ {_tr(_pt_eng or _pt_sum)} — CẦN DUYỆT RIÊNG**")
        lines.append(f"   Mục tiêu: đưa PARK về trần {_tgt_s} của pool — PARK hiện "
                     f"{_tr(_num(park_trim.get('park_mv_vnd')))} / pool "
                     f"{_tr(_num(park_trim.get('pool_vnd')))} ⇒ cần trim "
                     f"{_tr(_num(park_trim.get('trim_total_vnd')))}, phiên này đề xuất "
                     f"{_tr(_pt_eng or _pt_sum)}"
                     + (f", còn thiếu {_tr(_num(park_trim.get('trim_shortfall_vnd')))} để phiên sau"
                        if _num(park_trim.get("trim_shortfall_vnd")) else "") + ".")
        lines.append(f"   BÁN: {_tickers_line(pt_orders)}")
        # Σ engine vs Σ lệnh liệt kê: lệch = plan chép thiếu mã (§6 — không tin 1 con số tự khai)
        if _pt_eng and abs(_pt_sum - _pt_eng) > max(1e5, 0.01 * _pt_eng):
            lines.append(f"   ⚠️ Σ lệnh liệt kê {_tr(_pt_sum)} ≠ số engine {_tr(_pt_eng)} — "
                         f"plan có thể chép thiếu/thừa mã, kiểm trước khi duyệt.")
        _pt_bl = [b for b in (park_trim.get("blocked") or []) if isinstance(b, dict)]
        if _pt_bl:
            lines.append("   ⛔ Không trim được: " + "; ".join(
                f"{b.get('ticker','?')} ({str(b.get('reason') or '')[:120]})" for b in _pt_bl[:6]))
        for _n in (park_trim.get("notes") or [])[:2]:
            lines.append(f"   · {str(_n)[:300]}")
        lines.append("   ⚠️ Các lệnh BÁN này KHÔNG nằm trong danh sách lệnh chính ở trên — "
                     "duyệt riêng thì Mike/Bill mới đưa vào plan thực thi.")
    elif pt_dec.startswith("BLOCKED_") or pt_dec in ("NO_SELL_POSSIBLE",):
        lines.append(f"🅿️ **TRIM PARK (L1) BỊ CHẶN — {pt_dec}**: "
                     + ("; ".join(str(n)[:200] for n in (park_trim.get("notes") or [])[:2])
                        or "không có lý do kèm theo — kiểm compute_park_trim.py."))
    elif pt_dec:
        lines.append(f"🅿️ L1 trim PARK: {pt_dec}"
                     + (f" — {str((park_trim.get('notes') or [''])[0])[:180]}"
                        if park_trim.get("notes") else ""))
except Exception as _e:      # fail-open: một khối báo cáo không được chặn plan
    lines.append(f"⚠️ Không render được khối L1 park_trim ({type(_e).__name__}: {_e}) — "
                 f"đọc thẳng `park_trim_proposal` trong file plan trước khi duyệt.")

# ── MỤC RIÊNG 2: L2 jit_unpark_proposal ─────────────────────────────────────────────────
try:
    if jit_dec == "JIT" and (jit_orders or jit_amends):
        _jit_sum = sum(_o_val(o) for o in jit_orders)
        _for = sorted({str(o.get("for_ticker") or o.get("for_order_id") or "?")
                       for o in jit_orders})
        lines.append(f"💧 **ĐỀ XUẤT BÁN PARK TÀI TRỢ LỆNH MUA (L2/JIT) — {len(jit_orders)} lệnh "
                     f"BÁN, Σ {_tr(_jit_sum)} — CẦN DUYỆT RIÊNG**")
        if jit_orders:
            lines.append(f"   Tài trợ cho: {', '.join(_for)}")
            lines.append(f"   BÁN: {_tickers_line(jit_orders)}")
        for _a in jit_amends:
            _st = str(_a.get("status") or "?")
            _icon = {"FUNDED_BY_JIT": "✅", "FUNDED_BY_CASH": "✅",
                     "SHRINK": "⚠️", "DROP": "⛔"}.get(_st, "⚠️")
            lines.append(f"   {_icon} MUA {_a.get('ticker','?')}: {_st} — kế hoạch "
                         f"{_a.get('qty_plan')}cp → cuối cùng {_a.get('qty_final')}cp "
                         f"({_tr(_num(_a.get('target_value_final_vnd')))}); "
                         f"{str(_a.get('reason') or '')[:150]}")
        _jt_bl = [b for b in (jit_prop.get("blocked") or []) if isinstance(b, dict)]
        if _jt_bl:
            lines.append("   ⛔ Không bán được: " + "; ".join(
                f"{b.get('ticker','?')} ({str(b.get('reason') or '')[:120]})" for b in _jt_bl[:6]))
        for _n in (jit_prop.get("notes") or [])[:2]:
            lines.append(f"   · {str(_n)[:300]}")
        lines.append("   ⚠️ Duyệt lệnh MUA ở trên = duyệt luôn các lệnh BÁN PARK này (không bán "
                     "thì không đủ tiền mua) — nếu KHÔNG muốn bán PARK, phải bỏ/co lệnh mua.")
    elif jit_dec.startswith("BLOCKED_") or jit_dec in ("NO_SELL_POSSIBLE",):
        lines.append(f"💧 **BÁN PARK TÀI TRỢ (L2/JIT) BỊ CHẶN — {jit_dec}**: "
                     + ("; ".join(str(n)[:200] for n in (jit_prop.get("notes") or [])[:2])
                        or "không có lý do kèm theo — kiểm compute_jit_unpark.py.")
                     + " ⇒ lệnh mua có thể THIẾU TIỀN lúc 09:05 (triệu chứng WAIT_CASH).")
    elif jit_dec:
        lines.append(f"💧 L2 JIT unpark: {jit_dec}"
                     + (f" — {str((jit_prop.get('notes') or [''])[0])[:180]}"
                        if jit_prop.get("notes") else ""))
except Exception as _e:      # fail-open
    lines.append(f"⚠️ Không render được khối L2 jit_unpark ({type(_e).__name__}: {_e}) — "
                 f"đọc thẳng `jit_unpark_proposal` trong file plan trước khi duyệt.")

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
