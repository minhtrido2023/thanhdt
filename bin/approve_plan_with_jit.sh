#!/usr/bin/env bash
# Duyệt 1 plan giao dịch: merge lệnh bán PARK (jit_unpark_proposal) vào orders[] CÙNG lệnh mua
# đã có sẵn, đảm bảo thứ tự bán-trước-mua-sau (priority=0 cho lệnh bán < priority của lệnh mua
# hiện có trong plan), rồi ghi approved_by. Atomic write (coding_guidelines §5).
#
# Lý do có script riêng thay vì sửa JSON tay/qua LLM Bash trực tiếp: Claude Code auto-mode
# classifier chặn LLM tự thao tác field tiền thật trong 1 lượt hội thoại (2026-08-07). Script
# này KHÔNG cần LLM chạy — user tự chạy trong terminal của mình.
#
# DÙNG:
#   bin/approve_plan_with_jit.sh SpaceX 2026-08-07 "user (John) - Discord, duyet mua DRI + ban PARK JIT tai tro"
#   bin/approve_plan_with_jit.sh ZaloPay 2026-08-07 "user (John) - Discord, duyet mua DRI + ban PARK JIT tai tro"
#
# Xem trước, KHÔNG ghi gì:
#   DRY_RUN=1 bin/approve_plan_with_jit.sh SpaceX 2026-08-07 "..."

set -euo pipefail

ACCOUNT="${1:?usage: approve_plan_with_jit.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
PLAN_DATE="${2:?usage: approve_plan_with_jit.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
APPROVED_BY="${3:?usage: approve_plan_with_jit.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
DRY_RUN="${DRY_RUN:-0}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WC_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MIKE_ROOT="$WC_ROOT/mike"
PLAN_PATH="$WC_ROOT/data/trade_plans/plan_${ACCOUNT}_${PLAN_DATE}.json"

if [[ ! -f "$PLAN_PATH" ]]; then
  echo "❌ không tìm thấy plan: $PLAN_PATH" >&2
  exit 2
fi

python3 - "$PLAN_PATH" "$APPROVED_BY" "$DRY_RUN" <<'PYEOF'
import json, os, sys, datetime as dt
from zoneinfo import ZoneInfo

path, approved_by, dry_run = sys.argv[1], sys.argv[2], sys.argv[3] == "1"
ICT = ZoneInfo("Asia/Ho_Chi_Minh")

with open(path, encoding="utf-8") as f:
    plan = json.load(f)

orders = plan.get("orders", [])
jit_orders = plan.get("jit_unpark_proposal", {}).get("orders", [])

existing_ids = {o.get("id") for o in orders}
# lệnh mua hiện có: đảm bảo lệnh bán chạy TRƯỚC — priority=0 cho bán, giữ nguyên priority mua
buy_priorities = [o.get("priority", 5) for o in orders if o.get("side") == "buy"]
sell_priority = min(buy_priorities, default=1) - 1
if sell_priority < 0:
    sell_priority = 0

added = []
for jo in jit_orders:
    oid = f"SELL-JIT-PARK-{jo['ticker']}-01"
    if oid in existing_ids:
        continue
    added.append({
        "id": oid,
        "ticker": jo["ticker"],
        "side": jo["side"],
        "qty": jo["qty"],
        "ref_price": jo["ref_price"],
        "book": jo.get("book", "PARK"),
        "play_type": jo.get("play_type", "JIT_UNPARK"),
        "priority": sell_priority,
        "note": jo.get("reason", ""),
    })

print(f"== {path} ==")
print(f"orders[] hiện có: {len(orders)} lệnh (mua priority={buy_priorities})")
print(f"jit_unpark_proposal: {len(jit_orders)} lệnh bán PARK")
print(f"sẽ THÊM {len(added)} lệnh bán, priority={sell_priority} (chạy TRƯỚC mua)")
for o in added:
    print(f"  · SELL {o['ticker']:6s} {o['qty']:>6} cp @ {o['ref_price']:>10,.0f}đ  priority={o['priority']}")

if plan.get("approved_by") not in (None, ""):
    print(f"❌ plan ĐÃ CÓ approved_by={plan.get('approved_by')!r} — dừng lại, không ghi đè.",
          file=sys.stderr)
    sys.exit(2)

if not added and not orders:
    print("⚠ không có lệnh nào (mua lẫn bán) — dừng lại.", file=sys.stderr)
    sys.exit(2)

if dry_run:
    print("\n[DRY_RUN=1] KHÔNG ghi gì.")
    sys.exit(0)

plan["orders"] = orders + added
plan["approved_by"] = approved_by
plan["approved_at"] = dt.datetime.now(ICT).isoformat(timespec="seconds")

tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)
os.replace(tmp, path)

total_buy = sum(o.get("total_with_fee_vnd") or o.get("value_vnd") or 0
                for o in plan["orders"] if o.get("side") == "buy")
total_sell = sum(o.get("value_vnd") or 0 for o in plan["orders"] if o.get("side") == "sell")
print(f"\n✅ ĐÃ GHI: {len(plan['orders'])} lệnh tổng ({len(added)} bán mới thêm), "
      f"Σ mua ~{total_buy/1e6:,.1f}tr · Σ bán ~{total_sell/1e6:,.1f}tr")
print(f"approved_by={approved_by!r} approved_at={plan['approved_at']}")
PYEOF
RC=$?

if [[ "$RC" -ne 0 ]]; then
  exit "$RC"
fi

if [[ "$DRY_RUN" == "1" ]]; then
  exit 0
fi

# bus + Discord — dấu vết ai cũng thấy (cùng nguyên tắc approve_margin_day.py)
"$MIKE_ROOT/bin/append_event.sh" Mike decision "plan-approval-with-jit-${ACCOUNT}-${PLAN_DATE}" \
  "{\"account\":\"${ACCOUNT}\",\"date\":\"${PLAN_DATE}\",\"approved_by\":\"${APPROVED_BY}\",\"decided_by\":\"user\"}" \
  || echo "⚠ append_event.sh lỗi — bus event không ghi được, báo lại kênh duyệt plan bằng tay."

"$MIKE_ROOT/bin/notify_thread.sh" \
  "✅ **DUYỆT PLAN (mua+bán JIT)** — ${ACCOUNT} · ${PLAN_DATE}. Người duyệt: ${APPROVED_BY}" \
  plan_approval \
  || echo "⚠ notify_thread.sh lỗi — Discord không nhận được, báo lại kênh duyệt plan bằng tay."

echo "Xong. Bot sẽ tự nhận trong lần retry/khởi động kế tiếp."
