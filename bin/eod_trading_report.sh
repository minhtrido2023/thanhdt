#!/usr/bin/env bash
# eod_trading_report.sh [--account LABEL] [--date YYYY-MM-DD]
# Báo cáo tổng kết giao dịch cuối ngày: số lệnh, mua/bán, giá khớp TB, tổng giá trị.
# Đọc plan (ticker/side/ref_price) + state.json (giá khớp thực từng child order).
# Schedule: 15:00 ICT trading days (cron: 0 8 * * 1-5), sau khi phiên chiều đã đóng (~14:50).
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WC_ROOT="$(cd "$ROOT/.." && pwd)"

ACCOUNT="SpaceX"
PLAN_DATE="$(TZ='Asia/Ho_Chi_Minh' date +%Y-%m-%d)"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --account) ACCOUNT="$2"; shift 2 ;;
    --date)    PLAN_DATE="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

TRADING_THREAD="1522576692638388364"  # Trading report (đổi từ Trading Daily 2026-07-03, theo yêu cầu user)

PLAN_FILE="$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json"
STATE_FILE="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_state.json"

# --- Gate DT4 (candidate streak clock) — bối cảnh CẤP THỊ TRƯỜNG (không theo account) ---
# Tái dùng build_dt_gate_line() của dna_report.py (html=False → text sạch cho Discord
# markdown, không thẻ <i>/<b>). Chỉ dùng ở case HOLD-day + full-render (không chèn vào
# cảnh báo lỗi vận hành case 1/3 để không làm loãng cảnh báo). Fail-safe: mọi lỗi (thiếu
# BQ cred / thiếu CSV hazard / import lỗi) → in "" → bỏ qua dòng lặng lẽ, KHÔNG crash report.
# 2 account chạy report riêng cùng ngày sẽ hiện dòng này 2 lần — chấp nhận được (info thị trường).
_dt_gate_line() {
  cd "$WC_ROOT" && timeout 120 python3 -c "
import sys
sys.path.insert(0, '$WC_ROOT')
try:
    from dna_report import build_dt_gate_line, build_neutral_base_line
    line = build_dt_gate_line(html=False)
    if line:
        print('🛰️ ' + line)
        # Tần suất lịch sử NEUTRAL→BEAR/CRISIS (base-rate DT5G, KHÔNG phải dự báo —
        # nhãn nằm sẵn trong hàm). Tự None khi state không phải NEUTRAL → bỏ dòng.
        nb = build_neutral_base_line(html=False)
        if nb:
            print('  ↳ ' + nb)
except Exception:
    pass
" 2>/dev/null || true
}
# Trả về block (có newline dẫn đầu) khi có dữ liệu, "" khi lỗi/không có. Gọi LAZY — chỉ
# ở case HOLD-day + full-render, tránh chạy BQ trong nhánh cảnh báo lỗi (case 1/3).
# Có thể nhiều dòng (gate + base-rate) — prefix đã gắn sẵn từng dòng trong python.
_dt_gate_block() {
  local out; out="$(_dt_gate_line)"
  [ -n "$out" ] && printf '\n%s' "$out"
}

# Mọi ngày PHẢI có 1 dòng báo cho account này — "im lặng" không phân biệt được với hệ
# thống chết (user 2026-07-07). Trước đây "plan hoặc state thiếu" gộp chung 1 case rồi bỏ
# qua — bug thật hôm nay: plan HOLD (0 lệnh) khiến bot_execute.py thoát ngay KHÔNG tạo
# state file → bị coi như "không có phiên" → SpaceX không có report dù bot chạy đúng kế
# hoạch. Giờ tách 3 case rõ ràng, luôn gửi 1 trong 3:
N_ORDERS_TODAY="?"
if [ -f "$PLAN_FILE" ]; then
  N_ORDERS_TODAY="$(python3 -c "import json; print(len(json.load(open('$PLAN_FILE')).get('orders', [])))" 2>/dev/null || echo "?")"
fi

if [ ! -f "$PLAN_FILE" ]; then
  # Case 1: KHÔNG TÌM THẤY file plan — script này KHÔNG phân biệt tự động được giữa
  # (i) lỗi thật (DollarBill fail 17:30/19:30) và (ii) quyết định CHỦ ĐỘNG không lập plan
  # (vd ZaloPay 2026-07-14: transition xong 07-13, không phát sinh lệnh — bản cũ khẳng
  # định chắc "KHÔNG phải ngày nghỉ bình thường" là kết luận sai, fix 2026-07-14).
  # Không có bằng chứng → nêu cả 2 khả năng, để người đọc xác nhận, không buộc kết luận.
  MSG="🟡 **EOD $ACCOUNT ($PLAN_DATE)** — KHÔNG TÌM THẤY file plan hôm nay. 2 khả năng: (i) CHỦ ĐỘNG không lập plan cho account này (quyết định HOLD có chủ đích — bình thường), hoặc (ii) DollarBill lỗi lúc 17:30/19:30 hôm qua. Kiểm tra plan channel / bus để xác nhận là chủ động hay lỗi — báo cáo này không đủ bằng chứng tự kết luận."
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mafee status "eod-trading-report" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"delivered_via\":\"no_plan_alert\"}" 2>/dev/null || true
  exit 0
elif [ "$N_ORDERS_TODAY" = "0" ]; then
  # Case 2: HOLD hợp lệ (0 lệnh) — không cần state file (bot_execute.py thoát sớm đúng
  # thiết kế). Vẫn báo NAV để xác nhận hệ thống sống + số đúng, không phải im lặng.
  # grep -v [dnse]: lọc log kết nối broker debug (connect()/token) — không thuộc về
  # report client-facing, giữ minh bạch/gọn (user 2026-07-07).
  NAV_SECTION="$(python3 "$ROOT/bin/daily_nav_snapshot.py" --account "$ACCOUNT" --date "$PLAN_DATE" 2>&1 | grep -v '^\[dnse\]')"
  MSG="📊 **EOD Trading Report — $ACCOUNT ($PLAN_DATE)**
✅ HOLD — kế hoạch hôm nay không có lệnh nào (đúng thiết kế, không phải lỗi). Bot đã trực phiên đồng bộ trạng thái.

$NAV_SECTION$(_dt_gate_block)"
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mafee status "eod-trading-report" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"delivered_via\":\"hold_day\"}" 2>/dev/null || true
  exit 0
elif [ ! -f "$STATE_FILE" ]; then
  # Case 3: CÓ lệnh trong plan nhưng KHÔNG có state file — bot chưa từng chạy/crash trước
  # khi ghi state đầu tiên. Vấn đề thật, khác hẳn case 1/2.
  MSG="🔴 **EOD $ACCOUNT ($PLAN_DATE)** — Plan có $N_ORDERS_TODAY lệnh nhưng KHÔNG có state file thực thi. Bot có thể chưa chạy được lần nào hôm nay (kiểm tra run_bot.sh log / bot_heartbeat) — cần xem ngay."
  echo "$MSG"
  "$ROOT/bin/notify_thread.sh" "$MSG" "$TRADING_THREAD" 2>/dev/null || true
  "$ROOT/bin/append_event.sh" Mafee error "eod-trading-report" \
    "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"delivered_via\":\"missing_state_alert\"}" 2>/dev/null || true
  exit 0
fi
# Case 4 (bình thường: có lệnh + có state) rơi xuống phần render đầy đủ bên dưới.

REPORT="$(python3 - "$PLAN_FILE" "$STATE_FILE" "$ACCOUNT" "$PLAN_DATE" "$WC_ROOT" << 'PYEOF'
import sys, json, os

plan_file, state_file, account, plan_date, wc_root = sys.argv[1:6]

# Dùng trading_bot.plan.load_plan() thay vì tự json.load() + dictcomp trực tiếp trên orders
# thô — plan_file có thể ở schema v2+ (DollarBill's combined-trim, dùng priority/mtm_price_ref
# thay vì id/ref_price). load_plan() đã có sẵn shim normalize (trading_bot/plan.py) — tự parse
# ở đây từng bị crash KeyError 'id' hôm 2026-07-06 (xem kb/INCIDENTS.md) đúng plan v2 mà
# bot_execute.py xử lý bình thường vì nó qua load_plan() còn script này thì không.
sys.path.insert(0, wc_root)
from trading_bot.plan import load_plan as _load_plan

plan_obj = _load_plan(plan_date, account=account)
with open(state_file, encoding='utf-8') as f:
    state = json.load(f)

orders_by_id = {o.id: {'ticker': o.ticker, 'side': o.side, 'qty': o.qty, 'ref_price': o.ref_price,
                       'dcf_check': getattr(o, 'dcf_check', None)}
                for o in plan_obj.orders}

# DCF check echo (Pha 2, informational — user directive 2026-07-15: hiện trong MỌI report
# mua/bán). Echo field từ plan; BUY thiếu field → tính fallback từ cache local với ref_price
# + as-of plan_date (khớp đúng số report duyệt plan tối hôm trước, KHÔNG dùng giá EOD).
# Fail-safe: lỗi import/tính → không có dòng DCF, report vẫn nguyên vẹn.
try:
    from trading_bot.strategies import (_dcf_check_for_order, format_dcf_check,
                                        log_dcf_history)
    from dcf_valuation import DCF_DISCLAIMER
except Exception:
    _dcf_check_for_order = format_dcf_check = log_dcf_history = None
    DCF_DISCLAIMER = ''

def _dcf_str(o):
    if not format_dcf_check:
        return ''
    dcf = o.get('dcf_check')
    if not dcf and o.get('side') == 'buy' and _dcf_check_for_order \
            and isinstance(o.get('ref_price'), (int, float)) and o.get('ref_price'):
        try:
            dcf = _dcf_check_for_order(o.get('ticker'), o.get('ref_price'), plan_date)
        except Exception:
            dcf = None
    s = format_dcf_check(dcf, o.get('side') or 'buy', ticker=o.get('ticker'))
    if s and log_dcf_history:
        log_dcf_history(o.get('ticker'), dcf, 'eod_trading_report', asof=plan_date)
    return s
plan = {'orders': list(orders_by_id.values())}
parents = state.get('parents', {})

# ---- Đối soát fill THẬT (broker) vs state.json nội bộ ------------------------
# state.json["parents"][*]["filled"] bị CAP ở qty_plan (xem Executor._sync_fills:
# `ps["filled"] = min(total, o.qty)`) — nếu có 2 tiến trình cùng khớp 1 lệnh (như
# sự cố double-buy 2026-07-02), state.json vẫn báo "đúng 100% kế hoạch", che mất
# sự cố hoàn toàn. Đối soát trực tiếp với dnse_raw_{date}.jsonl (log thô từ DNSE,
# account-agnostic theo ngày) để phát hiện lệch — không phụ thuộc vào state nội bộ
# của chính tiến trình có thể đã bị lỗi.
plan_tickers = {o.get('ticker') for o in plan.get('orders', [])}
dnse_raw_file = os.path.join(wc_root, 'data', 'execution_logs', f'dnse_raw_{plan_date}.jsonl')
real_filled_by_ticker = {}
reconciled = False
# Lấy account_no cho account này để filter dnse_raw (file chung cả SpaceX+ZaloPay)
_target_account_no = None
try:
    _secrets_file = os.path.join(wc_root, 'secrets', 'trading_bot_accounts.json')
    with open(_secrets_file, encoding='utf-8') as _sf:
        _s = json.load(_sf)
    _accts_list = _s.get('accounts', [])
    if isinstance(_accts_list, list):
        _acct = next((a for a in _accts_list if a.get('label') == account), None)
        if _acct:
            _target_account_no = _acct.get('account_id') or _acct.get('account_no')
    elif isinstance(_accts_list, dict):
        _acct = _accts_list.get(account) or {}
        _target_account_no = _acct.get('account_id') or _acct.get('account_no')
except Exception:
    pass
if os.path.exists(dnse_raw_file):
    reconciled = True
    latest_by_oid = {}
    with open(dnse_raw_file, encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            # Bỏ qua records của account khác (fix: dnse_raw chứa cả SpaceX+ZaloPay)
            if _target_account_no and rec.get('account_no') and rec.get('account_no') != _target_account_no:
                continue
            kind = rec.get('kind')
            seen = []
            if kind == 'orders':
                seen = rec.get('payload', {}).get('orders') or []
            elif kind == 'place_order':
                r = rec.get('payload', {}).get('resp') or {}
                if r.get('id') is not None:
                    seen = [r]
            for o in seen:
                oid, sym = o.get('id'), o.get('symbol')
                if oid is None or sym not in plan_tickers:
                    continue
                latest_by_oid[oid] = o  # ghi đè -> giữ bản ghi MỚI NHẤT mỗi order id thật
    for o in latest_by_oid.values():
        fq = o.get('fillQuantity') or 0
        if fq > 0:
            sym = o.get('symbol')
            real_filled_by_ticker[sym] = real_filled_by_ticker.get(sym, 0) + fq

state_filled_by_ticker = {}
for oid, p in parents.items():
    o = orders_by_id.get(oid, {})
    sym = o.get('ticker')
    if sym:
        state_filled_by_ticker[sym] = state_filled_by_ticker.get(sym, 0) + p.get('filled', 0)

mismatches = []
if reconciled:
    for sym in plan_tickers:
        real = real_filled_by_ticker.get(sym, 0)
        internal = state_filled_by_ticker.get(sym, 0)
        if real != internal:
            mismatches.append((sym, internal, real, real - internal))

rows = []
tot_value_planned = 0
tot_value_filled = 0
n_buy = n_sell = 0
n_full = n_partial = n_zero = 0

for oid, p in parents.items():
    o = orders_by_id.get(oid, {})
    ticker = o.get('ticker', oid)
    side = o.get('side', '?')
    qty_plan = o.get('qty', 0)
    ref_price = o.get('ref_price', 0)
    filled = p.get('filled', 0)

    if side == 'buy':
        n_buy += 1
    elif side == 'sell':
        n_sell += 1

    fills = [c for c in p.get('children', []) if c.get('filled')]
    if fills:
        avg_price = sum(c['filled'] * c['price'] for c in fills) / sum(c['filled'] for c in fills)
    else:
        avg_price = 0

    value_filled = filled * avg_price
    value_planned = qty_plan * ref_price
    tot_value_planned += value_planned
    tot_value_filled += value_filled

    pct = 100.0 * filled / qty_plan if qty_plan else 0
    if filled == 0:
        n_zero += 1
    elif filled >= qty_plan:
        n_full += 1
    else:
        n_partial += 1

    rows.append({
        'ticker': ticker, 'side': side, 'qty_plan': qty_plan, 'filled': filled,
        'pct': pct, 'avg_price': avg_price, 'value': value_filled, 'dcf': _dcf_str(o)
    })

rows.sort(key=lambda r: -r['value'])

lines = []
lines.append(f"📊 **EOD Trading Report — {account} ({plan_date})**")
if mismatches:
    lines.append("")
    lines.append("🚨 **CẢNH BÁO ĐỐI SOÁT — FILL THẬT (broker) ≠ STATE NỘI BỘ** — "
                  "khả năng có tiến trình chạy trùng hoặc lỗi đồng bộ:")
    for sym, internal, real, diff in sorted(mismatches, key=lambda x: -abs(x[3])):
        lines.append(f"  ⚠️ {sym}: state báo {internal:,} nhưng broker thật khớp "
                      f"{real:,} (lệch {diff:+,})")
    lines.append("👉 Kiểm tra ngay — xem có process bot_execute.py trùng lặp, "
                  "hoặc đối chiếu dnse_raw_{}.jsonl thủ công.".format(plan_date))
    lines.append("")
elif reconciled:
    lines.append("✅ Đối soát broker: fill thật khớp đúng state nội bộ, không lệch.")
    lines.append("")
else:
    lines.append("ℹ️ Không đối soát được (không có dnse_raw log — bình thường nếu account paper).")
    lines.append("")
lines.append(f"Tổng lệnh: **{len(rows)}** ({n_buy} mua / {n_sell} bán) | "
             f"Khớp đủ: {n_full} | Khớp một phần: {n_partial} | Chưa khớp: {n_zero}")
lines.append("")

for r in rows:
    if r['filled'] > 0:
        side_disp = 'MUA' if r['side'] == 'buy' else 'BÁN'
        lines.append(f"• {side_disp} {r['ticker']}: {r['filled']:,}/{r['qty_plan']:,} "
                     f"({r['pct']:.0f}%) @ {r['avg_price']:,.0f}đ → {r['value']/1e6:,.1f}M")
    else:
        side_disp = 'mua' if r['side'] == 'buy' else 'bán'
        lines.append(f"• ⚠️ {side_disp} {r['ticker']}: 0/{r['qty_plan']:,} — KHÔNG khớp")
    if r.get('dcf'):
        lines.append(f"   ↳ {r['dcf']}")

if any(r.get('dcf') for r in rows) and DCF_DISCLAIMER:
    lines.append("")
    lines.append(f"ℹ️ _{DCF_DISCLAIMER}_")

lines.append("")
fill_rate = 100 * tot_value_filled / tot_value_planned if tot_value_planned else 0
lines.append(f"**Tổng giá trị giao dịch: {tot_value_filled/1e6:,.1f}M / kế hoạch {tot_value_planned/1e6:,.1f}M "
             f"({fill_rate:.0f}%)**")

print("\n".join(lines))

# Ghi mismatch ra file máy-đọc-được (nếu có) để bash phía dưới quyết định có kích hoạt
# kiểm toán độc lập hay không — tách khỏi text Discord để không phải parse markdown.
mismatch_file = os.path.join(os.path.dirname(state_file), f'eod_mismatch_{account}_{plan_date}.json')
if mismatches:
    with open(mismatch_file, 'w', encoding='utf-8') as f:
        json.dump({'account': account, 'plan_date': plan_date,
                   'mismatches': [{'ticker': s, 'state_filled': i, 'broker_filled': r, 'diff': d}
                                  for s, i, r, d in mismatches]}, f, ensure_ascii=False, indent=2)
elif os.path.exists(mismatch_file):
    os.remove(mismatch_file)  # ngày trước có lệch, hôm nay sạch -> dọn cờ cũ
PYEOF
)"

NAV_SECTION="$(python3 "$ROOT/bin/daily_nav_snapshot.py" --account "$ACCOUNT" --date "$PLAN_DATE" 2>&1 | grep -v '^\[dnse\]')"

# DC-book NEUTRAL waterfall (paper sleeve) MOVED OUT 2026-07-07 — user mandate: mọi
# paper-trading report gộp về MỘT nhóm (Paper Programs Daily Report,
# bin/paper_programs_daily_report.sh) để tránh trùng lặp giữa các kênh. Nó đã có mặt đầy
# đủ ở đó (registry chương trình #1) — không cần render lại ở đây nữa.

FULL_REPORT="$REPORT

$NAV_SECTION$(_dt_gate_block)"

echo "$FULL_REPORT"
# Báo cáo client-facing KHÔNG được rơi im lặng (sự cố 2026-07-06: topic Trading report bị
# Missing Access — bot mất quyền/thread archive — notify fail bị `|| true` nuốt, user không
# nhận được report ngày và không ai biết). Fallback 2 tầng khi post thất bại: (1) Telegram
# qua notify.sh, (2) Trading Daily thread kèm cảnh báo — và luôn ghi bus event nêu rõ kênh
# nào nhận được.
TRADING_DAILY_THREAD="1521470705563340910"
DELIVERED_VIA="trading_report_thread"
if ! "$ROOT/bin/notify_thread.sh" "$FULL_REPORT" "$TRADING_THREAD" 2>>"$ROOT/logs/eod_notify_errors.log"; then
  DELIVERED_VIA="fallback"
  FALLBACK_HEADER="⚠️ **Topic Trading report đang không truy cập được (bot Missing Access) — gửi tạm qua kênh dự phòng.**"
  "$ROOT/bin/notify.sh" "$FALLBACK_HEADER
$FULL_REPORT" 2>/dev/null || true
  "$ROOT/bin/notify_thread.sh" "$FALLBACK_HEADER
$FULL_REPORT" "$TRADING_DAILY_THREAD" 2>/dev/null || true
fi
"$ROOT/bin/append_event.sh" Mafee status "eod-trading-report" \
  "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\",\"delivered_via\":\"$DELIVERED_VIA\"}" 2>/dev/null || true

# Phương án B (user duyệt 2026-07-02): kiểm toán độc lập CÓ ĐIỀU KIỆN — chỉ kích hoạt
# risk-auditor khi đối soát cơ học phía trên đã phát hiện lệch, không chạy tốn kém mỗi
# ngày. Dispatch headless (không phải Agent() — cron không có phiên Claude sống).
MISMATCH_FILE="$WC_ROOT/data/execution_logs/eod_mismatch_${ACCOUNT}_${PLAN_DATE}.json"
if [ -f "$MISMATCH_FILE" ]; then
  _discord_thread="1522576692638388364"  # Trading report
  "$ROOT/bin/notify_thread.sh" "🔍 Phát hiện lệch đối soát — tự động kích hoạt kiểm toán độc lập (risk-auditor)..." "$_discord_thread" 2>/dev/null || true
  DISPATCH_FROM=Mafee "$ROOT/bin/dispatch.sh" Spyros \
    "$(cat <<PROMPT
EOD reconciliation vừa phát hiện LỆCH giữa state nội bộ và broker thật cho account $ACCOUNT ngày $PLAN_DATE (xem chi tiết: $MISMATCH_FILE). Bạn là risk-auditor — kiểm toán độc lập việc này:
1. Đọc $MISMATCH_FILE để biết chính xác mã nào lệch bao nhiêu.
2. Tự đối chiếu lại độc lập từ dnse_raw_${PLAN_DATE}.jsonl + state.json + plan gốc — xác nhận số liệu đúng như file mismatch báo, KHÔNG tin sẵn.
3. Điều tra nguyên nhân khả dĩ: có process bot_execute.py chạy trùng không (kiểm tra log run_bot*/autoheal* quanh thời điểm), hay lý do khác (cancel/reprice, modify-order quirk DNSE, lỗi đồng bộ khác)?
4. Đánh giá tác động: lệch làm portfolio vượt giới hạn trading_rules.json nào không (concentration, gross exposure)?
5. Kết luận rõ: đây có phải sự cố NGHIÊM TRỌNG cần escalate ngay cho user, hay là sai lệch nhỏ/false-positive của chính cơ chế đối soát (vd do lệnh bị modify đổi order id, dedup sai)?
Báo cáo ngắn gọn lên bus + Discord Trading report topic (1522576692638388364). Đây là kiểm toán READ-ONLY — không sửa code/state/lệnh gì.
PROMPT
)" --bg --timeout 900 2>&1 || true
fi
