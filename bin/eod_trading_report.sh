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

TRADING_THREAD="1521470705563340910"  # Trading Daily

PLAN_FILE="$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json"
STATE_FILE="$WC_ROOT/data/execution_logs/exec_${ACCOUNT}_${PLAN_DATE}_state.json"

if [ ! -f "$PLAN_FILE" ] || [ ! -f "$STATE_FILE" ]; then
  MSG="ℹ️ [$PLAN_DATE] Không có phiên giao dịch nào cho $ACCOUNT hôm nay (plan hoặc state file không tồn tại) — bỏ qua EOD report."
  echo "$MSG"
  exit 0
fi

REPORT="$(python3 - "$PLAN_FILE" "$STATE_FILE" "$ACCOUNT" "$PLAN_DATE" "$WC_ROOT" << 'PYEOF'
import sys, json, os

plan_file, state_file, account, plan_date, wc_root = sys.argv[1:6]

with open(plan_file, encoding='utf-8') as f:
    plan = json.load(f)
with open(state_file, encoding='utf-8') as f:
    state = json.load(f)

orders_by_id = {o['id']: o for o in plan.get('orders', [])}
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
if os.path.exists(dnse_raw_file):
    reconciled = True
    latest_by_oid = {}
    with open(dnse_raw_file, encoding='utf-8') as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
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
        'pct': pct, 'avg_price': avg_price, 'value': value_filled
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

echo "$REPORT"
"$ROOT/bin/notify_thread.sh" "$REPORT" "$TRADING_THREAD" 2>/dev/null || true
"$ROOT/bin/append_event.sh" Mafee status "eod-trading-report" \
  "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\"}" 2>/dev/null || true

# Phương án B (user duyệt 2026-07-02): kiểm toán độc lập CÓ ĐIỀU KIỆN — chỉ kích hoạt
# risk-auditor khi đối soát cơ học phía trên đã phát hiện lệch, không chạy tốn kém mỗi
# ngày. Dispatch headless (không phải Agent() — cron không có phiên Claude sống).
MISMATCH_FILE="$WC_ROOT/data/execution_logs/eod_mismatch_${ACCOUNT}_${PLAN_DATE}.json"
if [ -f "$MISMATCH_FILE" ]; then
  _discord_thread="1521470705563340910"
  "$ROOT/bin/notify_thread.sh" "🔍 Phát hiện lệch đối soát — tự động kích hoạt kiểm toán độc lập (risk-auditor)..." "$_discord_thread" 2>/dev/null || true
  DISPATCH_FROM=Mafee "$ROOT/bin/dispatch.sh" Spyros \
    "$(cat <<PROMPT
EOD reconciliation vừa phát hiện LỆCH giữa state nội bộ và broker thật cho account $ACCOUNT ngày $PLAN_DATE (xem chi tiết: $MISMATCH_FILE). Bạn là risk-auditor — kiểm toán độc lập việc này:
1. Đọc $MISMATCH_FILE để biết chính xác mã nào lệch bao nhiêu.
2. Tự đối chiếu lại độc lập từ dnse_raw_${PLAN_DATE}.jsonl + state.json + plan gốc — xác nhận số liệu đúng như file mismatch báo, KHÔNG tin sẵn.
3. Điều tra nguyên nhân khả dĩ: có process bot_execute.py chạy trùng không (kiểm tra log run_bot*/autoheal* quanh thời điểm), hay lý do khác (cancel/reprice, modify-order quirk DNSE, lỗi đồng bộ khác)?
4. Đánh giá tác động: lệch làm portfolio vượt giới hạn trading_rules.json nào không (concentration, gross exposure)?
5. Kết luận rõ: đây có phải sự cố NGHIÊM TRỌNG cần escalate ngay cho user, hay là sai lệch nhỏ/false-positive của chính cơ chế đối soát (vd do lệnh bị modify đổi order id, dedup sai)?
Báo cáo ngắn gọn lên bus + Discord Trading Daily thread (1521470705563340910). Đây là kiểm toán READ-ONLY — không sửa code/state/lệnh gì.
PROMPT
)" --bg --timeout 900 2>&1 || true
fi
