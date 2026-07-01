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

REPORT="$(python3 - "$PLAN_FILE" "$STATE_FILE" "$ACCOUNT" "$PLAN_DATE" << 'PYEOF'
import sys, json

plan_file, state_file, account, plan_date = sys.argv[1:5]

with open(plan_file, encoding='utf-8') as f:
    plan = json.load(f)
with open(state_file, encoding='utf-8') as f:
    state = json.load(f)

orders_by_id = {o['id']: o for o in plan.get('orders', [])}
parents = state.get('parents', {})

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
PYEOF
)"

echo "$REPORT"
"$ROOT/bin/notify_thread.sh" "$REPORT" "$TRADING_THREAD" 2>/dev/null || true
"$ROOT/bin/append_event.sh" Mafee status "eod-trading-report" \
  "{\"account\":\"$ACCOUNT\",\"plan_date\":\"$PLAN_DATE\"}" 2>/dev/null || true
