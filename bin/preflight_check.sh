#!/usr/bin/env bash
# preflight_check.sh — kiểm tra sẵn sàng trước khi bot thực thi lệnh.
# Chạy 08:45 ICT mỗi ngày giao dịch (cron: 45 1 * * 1-5).
# Exit 0 = GREEN (mọi thứ OK). Exit 1 = RED (có vấn đề, bot KHÔNG nên chạy).
# Luôn post kết quả vào Discord trading thread.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
[ -f "$ROOT/../wc_env.sh" ] && source "$ROOT/../wc_env.sh" 2>/dev/null || true

WORKDIR="${WORKDIR_8L:-/home/trido/thanhdt/WorkingClaude}"
TODAY="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
NOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +'%H:%M ICT')"
DOW_ICT="$(TZ='Asia/Ho_Chi_Minh' date +%u)"   # 1=thứ Hai … 7=CN
# Trading Daily — mọi nội dung giao dịch hàng ngày gộp về 1 thread cố định (không phụ thuộc
# session Mike gần nhất mở từ thread nào).
TRADING_DAILY_THREAD="trading_daily"

# --account LABEL — mặc định SpaceX để giữ nguyên hành vi cũ khi gọi không kèm cờ (vd tay).
# Cron thật gọi qua for_each_live_account.sh (lặp mọi account enabled=live/dnse) — thêm
# account mới vào secrets/trading_bot_accounts.json là script này tự chạy cho account đó,
# không cần sửa gì ở đây. Xem kb/account_onboarding_runbook.md.
ACCOUNT="SpaceX"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --account) ACCOUNT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

FAILED=0
LINES=()

_ok()   { LINES+=("✅ $1"); }
_warn() { LINES+=("⚠️  $1"); }
_fail() { LINES+=("❌ $1"); FAILED=1; }

# ── 1. BOT_STOP kill-switch ───────────────────────────────────────────────────
if [ -f "$WORKDIR/data/BOT_STOP" ]; then
  _fail "BOT_STOP tồn tại — bot bị khoá thủ công. Xoá file để mở khoá."
else
  _ok "BOT_STOP: CLEAR"
fi

# ── 2. Plan hôm nay tồn tại + đã approve ─────────────────────────────────────
PLAN_FILE="$WORKDIR/data/trade_plans/plan_${ACCOUNT}_${TODAY}.json"
# fallback: plan_<account>_<date>.json nếu tên khác
if [ ! -f "$PLAN_FILE" ]; then
  PLAN_FILE="$(ls -t "$WORKDIR"/data/plan_${ACCOUNT}_${TODAY}.json \
                      "$WORKDIR"/data/trade_plans/plan_${ACCOUNT}_${TODAY}.json \
                      "$WORKDIR"/data/plan_${ACCOUNT}_*_${TODAY}.json 2>/dev/null | head -1 || true)"
fi

if [ -z "${PLAN_FILE:-}" ] || [ ! -f "${PLAN_FILE:-}" ]; then
  _fail "Plan $ACCOUNT $TODAY KHÔNG TÌM THẤY — DollarBill chưa lập plan hoặc BQ stale."
else
  # stderr KHÔNG bị nuốt (arch-review coord-2026-08-07): khối này crash ⇒ PLAN_INFO rỗng ⇒
  # dòng RED không có lý do, và người đọc không phân biệt được "plan xấu" với "checker hỏng".
  _PF_ERR="$(mktemp)"
  PLAN_INFO=$(python3 - "$PLAN_FILE" 2>"$_PF_ERR" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
approved  = d.get("approved_by") or d.get("approved_by_user")
mafee_ok  = d.get("mafee_authorized", False)
mode      = d.get("mode", "?")
n_orders  = len(d.get("orders", []))
nav_b     = (d.get("nav_basis") or {}).get("account_nav", 0) / 1e9
est_val   = sum(o.get("est_value_vnd", o.get("est_value", 0)) for o in d.get("orders", [])) / 1e9
state_nm  = d.get("state_name", d.get("state", "?"))
src       = d.get("state_source", "?")
rc        = d.get("risk_checks", {})
rc_ok     = all("PASS" in str(v) or "CLEAR" in str(v) or "HEALTHY" in str(v) or "VALID" in str(v) or "N/A" in str(v)
                for v in rc.values()) if rc else None
flags = []

# ── Bất biến lệnh (thêm 2026-08-07, sự cố plan 08-07 bán trùng lô JIT_UNPARK) ──
# a) MERGE_STALE_SRC: lệnh mang `merged_from` nghĩa là bước gộp đã cộng MỌI lệnh cùng
#    (side,ticker) vào nó. Còn sót lệnh nguồn cùng (side,ticker) = bước gộp thêm lệnh gộp
#    nhưng quên xoá lệnh gốc → gửi 2 lần. Ngày 08-07 lỗi này để lọt 1.200cp (SpaceX) +
#    400cp (ZaloPay) bán thừa, không tầng nào chặn.
# b) SELL_GT_SELLABLE: tổng qty BÁN 1 mã vượt `sellable_at_calc` mà chính plan ghi ra.
#
# THU HẸP nhánh (a) 2026-08-11 (job Taylor_20260810_185646) — báo động giả thật:
#   `mike/bin/merge_park_orders.py` CỐ Ý giữ nguyên lệnh bán của writer khác cùng mã (bất
#   biến I5 "không đánh rơi lệnh ngoài vùng sở hữu"; ca S3 của selfcheck merge). Sau merge,
#   một mã hợp lệ có 2 lệnh bán — lệnh merge (mang `merged_from`) + lệnh ngoài vùng — và
#   nhánh (a) nguyên bản đọc thành "còn sót lệnh nguồn" ⇒ preflight ĐỎ dù MỌI bất biến
#   merge đều PASS. Đỏ giả lặp lại = tầng dưới học cách bỏ qua nó, đúng cách một lưới an
#   toàn chết trong im lặng.
#
# Điều kiện mới: chỉ báo khi CÓ ≥2 lệnh **thuộc miền của bước gộp** trong cùng (side,ticker)
# — đó mới là chữ ký "gộp rồi nhưng quên xoá nguồn". Lệnh của writer khác (book khác, không
# mang nhãn PARK/JIT) đứng cạnh lệnh merge KHÔNG còn bị tính.
#   · Giữ nguyên độ phủ sự cố 08-07: lệnh sót ngày đó là `SELL-JIT-PARK-<mã>-01`
#     (`play_type=JIT_UNPARK`) ⇒ vẫn nằm trong miền ⇒ vẫn bị bắt (selfcheck #1/#3/#8/#11).
#   · Nhánh (b) SELL_GT_SELLABLE KHÔNG đổi một chữ. Đó mới là nhánh chặn RỦI RO TIỀN (bán
#     vượt lô sở hữu) và nó vẫn chạy trên MỌI lệnh, kể cả lệnh do merge sinh ra — lý do
#     chính khiến thu hẹp (a) là an toàn: (a) là heuristic cấu trúc, (b) là trần thật.
_orders = d.get("orders", [])
# qty có thể là chuỗi ("100") tuỳ writer plan — so sánh chuỗi với số sẽ TypeError và giết cả
# khối (arch-review coord-2026-08-07). Ép kiểu; giá trị KHÔNG ép được thì báo cờ chứ không
# lặng lẽ coi là 0 (0 làm bất biến (b) tính thiếu và đọc ra "sạch").
_bad_qty = []
def _q(o):
    v = o.get("qty", o.get("quantity")) or 0
    try:
        return int(float(v))
    except (TypeError, ValueError):
        _bad_qty.append(str(o.get("id") or o.get("ticker") or "?"))
        return 0
_MERGE_PLAYS = {"PARK_TRIM", "JIT_UNPARK", "PARK_TRIM+JIT_UNPARK"}
def _merge_domain(o):
    """Lệnh này có thuộc miền bước gộp L1/L2 không (⇒ đáng lẽ đã bị gộp/xoá)?"""
    return (o.get("merge_owner") == "park_merge_v1"
            or bool(o.get("merged_from"))
            or str(o.get("play_type", "")).upper() in _MERGE_PLAYS)
_by_key = {}
for _o in _orders:
    # side chuẩn hoá về chữ thường: 'SELL' viết hoa từng làm nhánh (b) im lặng không chạy.
    _by_key.setdefault((str(_o.get("side") or "").lower(), _o.get("ticker")), []).append(_o)
_stale = sorted({k[1] for k, v in _by_key.items()
                 if len(v) > 1 and any(o.get("merged_from") for o in v)
                 and sum(1 for o in v if _merge_domain(o)) > 1})
if _stale: flags.append("MERGE_STALE_SRC:" + ",".join(_stale))
_over = []
for (_side, _tk), _os in _by_key.items():
    if _side != "sell": continue
    # (… or {}) chứ KHÔNG phải .get(k, {}): merged_from=null có thật trong plan ⇒ default
    # không được dùng ⇒ None.get() AttributeError giết cả khối (idiom giống dòng approved).
    _cap = max(((o.get("merged_from") or {}).get("sellable_at_calc") or 0) for o in _os)
    if _cap and sum(_q(o) for o in _os) > _cap:
        _over.append(f"{_tk}({sum(_q(o) for o in _os)}>{_cap})")
if _over: flags.append("SELL_GT_SELLABLE:" + ",".join(sorted(_over)))
if _bad_qty: flags.append("BAD_QTY:" + ",".join(sorted(set(_bad_qty))))

# Plan HOLD (0 lệnh) không có gì để thực thi — approval chỉ bắt buộc khi có lệnh thật.
# mafee_authorized KHÔNG còn là fail-flag: không có code path nào ghi field này (INCIDENTS
# 2026-07-06), gate thực thi thật (trading_bot/plan.py approval_block_reason) chỉ đọc
# approved_by — flag cứng ở đây tạo RED giả lặp lại cho plan đã duyệt thật (07-06, 07-15).
# Vẫn hiển thị giá trị mafee ở dòng kết quả để đối chiếu khi field có mặt.
if n_orders > 0:
    if not approved:   flags.append("NOT_APPROVED")
if mode != "live": flags.append(f"mode={mode}")
if rc_ok is False: flags.append("RISK_CHECK_FAIL")
print(f"{approved}|{mafee_ok}|{mode}|{n_orders}|{est_val:.3f}|{state_nm}|{src}|{'|'.join(flags) if flags else 'OK'}")
PY
  )

  IFS='|' read -r _approved _mafee _mode _n_orders _est _state_nm _src _flags <<< "$PLAN_INFO"

  if [ -z "$PLAN_INFO" ]; then
    _fail "Plan $ACCOUNT $TODAY: khối kiểm plan/bất biến lệnh CRASH, KHÔNG kết luận được gì về plan — $(tr '\n' ' ' < "$_PF_ERR" | tail -c 300)"
  elif [ "$_flags" = "OK" ]; then
    _ok "Plan $ACCOUNT $TODAY: $_n_orders lệnh, ~${_est}B VND, state=$_state_nm ($_src), approved=$_approved mafee=$_mafee"
  else
    _fail "Plan $ACCOUNT $TODAY: $_flags — orders=$_n_orders approved=$_approved mafee=$_mafee"
  fi
  rm -f "$_PF_ERR"
fi

# ── 3. Macro health ───────────────────────────────────────────────────────────
HEALTH_FILE="$WORKDIR/data/macro_health.json"
if [ ! -f "$HEALTH_FILE" ]; then
  _fail "macro_health.json không tồn tại."
else
  HEALTH=$(python3 - "$HEALTH_FILE" 2>/dev/null <<'PY'
import json, sys, time, os
d = json.load(open(sys.argv[1]))
status = d.get("status","?")
sev    = d.get("sev","?")
src    = d.get("recommended_state_source","?")
mtime  = os.path.getmtime(sys.argv[1])
age_h  = (time.time() - mtime) / 3600
print(f"{status}|{sev}|{src}|{age_h:.1f}")
PY
  )
  IFS='|' read -r _hstatus _hsev _hsrc _hage <<< "$HEALTH"

  # Chấp nhận HEALTHY hoặc DEGRADED (SEV2); từ chối FAILED (SEV1)
  # Ngưỡng tuổi file theo thứ: daily_refresh chạy 18:30 ICT T2-T6 → sáng T3-T6 file ~14h,
  # nhưng sáng thứ Hai bản mới nhất là 18:30 thứ Sáu (~62h) — ngưỡng 68h tránh false-warn
  # lặp lại mỗi thứ Hai (miss thật tối thứ Sáu đã có gate 19:00 bq_freshness_check
  # MAX_STATE_LAG=0 bắt ngay trong tối đó, không cần chờ preflight sáng thứ Hai).
  _max_age_h=20; [ "$DOW_ICT" = "1" ] && _max_age_h=68
  if [ "$_hstatus" = "FAILED" ]; then
    _fail "macro_health=FAILED (SEV1) — DT5G chạy DT4_only. Kiểm tra data pipeline."
  elif [ "$(echo "$_hage > $_max_age_h" | bc -l 2>/dev/null)" = "1" ]; then
    _warn "macro_health OK ($_hstatus) nhưng file cũ ${_hage}h — daily_refresh chưa chạy tối qua?"
    _ok  "State source: $_hsrc"
  else
    _ok "macro_health: $_hstatus ($_hsrc, file ${_hage}h tuổi)"
  fi
fi

# ── 4. Gmail OAuth refresh_token ─────────────────────────────────────────────
GMAIL_TOKEN="$WORKDIR/secrets/gmail_oauth_token.json"
if [ ! -f "$GMAIL_TOKEN" ]; then
  _fail "gmail_oauth_token.json không tồn tại — auto-OTP sẽ thất bại."
else
  HAS_REFRESH=$(python3 -c "
import json
d=json.load(open('$GMAIL_TOKEN'))
print('yes' if d.get('refresh_token') else 'no')
" 2>/dev/null)
  if [ "$HAS_REFRESH" = "yes" ]; then
    _ok "Gmail OAuth: có refresh_token (tự refresh khi cần)"
  else
    _warn "Gmail OAuth: KHÔNG có refresh_token — OTP có thể fail nếu access_token hết hạn."
  fi
fi

# ── 5. BQ freshness (nhanh — check ticker_prune lag + depth) ─────────────────
# Depth (số mã ngày mới nhất) thêm 2026-07-15: sự cố upstream ghi đè ticker_prune còn
# 7-10 mã/ngày trong khi MAX(time) vẫn advance → lag-check một mình bị mù hoàn toàn.
# 2026-07-17: đo trên NGÀY HOÀN CHỈNH gần nhất (time < hôm nay ICT) — upstream ETL có thể
# ghi dở dang partition hôm nay trong phiên (quan sát thật 12:45 ICT: 1-2 mã, lớn dần),
# preflight chạy sáng/trưa nên ref_price/screening dựa trên EOD hôm qua; đo MAX(time) tuyệt
# đối sẽ báo động giả "bảng moi ruột" trên partition đang ghi. bq_freshness_check.sh (19:00,
# cần dữ liệu ngày T đầy đủ) giữ nguyên ngữ nghĩa MAX(time) — đừng đồng bộ hoá 2 chỗ này.
BQ_ROW=$(bq query --use_legacy_sql=false --format=csv --quiet \
  --project_id=lithe-record-440915-m9 \
  "SELECT DATE_DIFF(CURRENT_DATE('Asia/Ho_Chi_Minh'), MAX(t.time), DAY) AS lag,
          COUNT(DISTINCT IF(t.time = (SELECT MAX(x.time) FROM \`lithe-record-440915-m9.tav2_bq.ticker_prune\` AS x WHERE x.time < CURRENT_DATE('Asia/Ho_Chi_Minh')), t.ticker, NULL)) AS names
   FROM \`lithe-record-440915-m9.tav2_bq.ticker_prune\` AS t
   WHERE t.time >= DATE_SUB(CURRENT_DATE('Asia/Ho_Chi_Minh'), INTERVAL 14 DAY)
     AND t.time < CURRENT_DATE('Asia/Ho_Chi_Minh')" \
  2>/dev/null | tail -1 | tr -d '[:space:]' || echo "999,0")
BQ_LAG="${BQ_ROW%%,*}"; BQ_NAMES="${BQ_ROW##*,}"

# Thứ Hai sáng: phiên gần nhất là thứ Sáu → lag=3 ngày lịch là bình thường (không phải stale).
_max_prune_lag=2; [ "$DOW_ICT" = "1" ] && _max_prune_lag=3
_min_prune_names=200   # bình thường ~225-265 mã/ngày; <200 = bảng bị ghi thiếu
if [ "$BQ_LAG" -le "$_max_prune_lag" ] 2>/dev/null && [ "$BQ_NAMES" -ge "$_min_prune_names" ] 2>/dev/null; then
  _ok "BQ ticker_prune: lag=${BQ_LAG}d, ${BQ_NAMES} mã ✓"
elif [ "$BQ_NAMES" -lt "$_min_prune_names" ] 2>/dev/null; then
  _warn "BQ ticker_prune: ngày mới nhất chỉ có ${BQ_NAMES} mã (<${_min_prune_names}, bình thường ~225-265) — bảng bị ghi thiếu/moi ruột dù lag=${BQ_LAG}d; ref_price/screening không tin được."
else
  _warn "BQ ticker_prune: lag=${BQ_LAG}d — giá ref_price trong plan có thể cũ; kiểm tra trước khi đặt lệnh."
fi

# ── Tổng hợp + notify ─────────────────────────────────────────────────────────
echo "=== Preflight $TODAY $NOW_ICT ==="
for line in "${LINES[@]}"; do echo "  $line"; done

if [ "$FAILED" -eq 0 ]; then
  STATUS_ICON="🟢"
  STATUS_TEXT="GREEN — sẵn sàng giao dịch"
else
  STATUS_ICON="🔴"
  STATUS_TEXT="RED — CÓ VẤN ĐỀ, kiểm tra trước khi bot chạy"
fi

MSG="$STATUS_ICON **Preflight $ACCOUNT $TODAY $NOW_ICT** — $STATUS_TEXT"$'\n'
for line in "${LINES[@]}"; do MSG+="$line"$'\n'; done

"$ROOT/bin/notify.sh" "$MSG" 2>/dev/null || true

if [ -n "${TRADING_DAILY_THREAD:-}" ]; then
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_DAILY_THREAD" 2>/dev/null || true
fi

"$ROOT/bin/append_event.sh" Mike status "preflight-${ACCOUNT}-$TODAY" \
  "{\"result\":\"$([ $FAILED -eq 0 ] && echo GREEN || echo RED)\",\"checks\":$(python3 -c "import json; print(json.dumps($(printf '[%s]' "$(IFS=,; printf '"%s",' "${LINES[@]}" | sed 's/,$//') ")))" 2>/dev/null || echo '[]')}" \
  2>/dev/null || true

exit "$FAILED"
