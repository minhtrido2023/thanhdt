#!/usr/bin/env bash
# Duyệt 1 plan giao dịch ĐÃ SẴN orders[] đầy đủ (không merge gì thêm) — set approved_by,
# atomic write, kèm sanity-check (không trùng ticker, Sigma ban >= Sigma mua) truoc khi ghi.
#
# Khac approve_plan_with_jit.sh (script truoc): script do MERGE jit_unpark_proposal vao
# orders[] — neu orders[] DA merge san (nhu plan DollarBill tao hom nay), chay lai no se
# merge TRUNG LAN 2 (nhan doi lenh ban 1 so ma). Script nay KHONG merge gi, chi verify + duyet.
#
# DUNG:
#   bin/approve_plan_simple.sh SpaceX 2026-08-07 "user (John) - Discord, duyet DRI+L1+L2 gop"
#   bin/approve_plan_simple.sh ZaloPay 2026-08-07 "user (John) - Discord, duyet DRI+L1+L2 gop"
#
# Xem truoc, KHONG ghi gi:
#   DRY_RUN=1 bin/approve_plan_simple.sh SpaceX 2026-08-07 "..."

set -euo pipefail

ACCOUNT="${1:?usage: approve_plan_simple.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
PLAN_DATE="${2:?usage: approve_plan_simple.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
APPROVED_BY="${3:?usage: approve_plan_simple.sh <account> <date YYYY-MM-DD> <approved-by-text>}"
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
if not orders:
    print("⚠ orders[] rỗng — không có gì để duyệt.", file=sys.stderr)
    sys.exit(2)

# Kiểm "đã merge 2 lần" — THU HẸP 2026-08-11 (job Taylor_20260810_185646), cùng lớp báo động
# giả vừa vá ở `preflight_check.sh` nhánh (a):
#   · so theo **(side, ticker)**, không theo mình `ticker`: 1 lệnh MUA + 1 lệnh BÁN cùng mã
#     không phải dấu hiệu merge 2 lần;
#   · và chỉ tính lệnh **thuộc miền bước gộp**: `mike/bin/merge_park_orders.py` CỐ Ý giữ lệnh
#     bán của writer khác cùng mã (bất biến I5) ⇒ sau merge, một mã hợp lệ có thể có 2 lệnh
#     bán. Cổng cũ chặn CỨNG ca đó ⇒ từ chối duyệt một plan hoàn toàn đúng (fail-closed nên
#     không mất tiền, nhưng chặn người duyệt và dạy họ bỏ qua cảnh báo).
# Chữ ký thật của "merge 2 lần" vẫn bị bắt: 2 lệnh CÙNG thuộc miền, cùng (side,ticker).
_MERGE_PLAYS = {"PARK_TRIM", "JIT_UNPARK", "PARK_TRIM+JIT_UNPARK"}


def _merge_domain(o):
    return (o.get("merge_owner") == "park_merge_v1"
            or bool(o.get("merged_from"))
            or str(o.get("play_type", "")).upper() in _MERGE_PLAYS)


_groups = {}
for _o in orders:
    _groups.setdefault((_o.get("side"), _o.get("ticker")), []).append(_o)
dups = {tk for (sd, tk), v in _groups.items()
        if sum(1 for o in v if _merge_domain(o)) > 1}
if dups:
    print(f"❌ TRÙNG LỆNH BÁN PARK trong orders[]: {dups} — ≥2 lệnh cùng (side,ticker) đều "
          f"thuộc miền bước gộp ⇒ nhiều khả năng đã merge 2 lần. DỪNG LẠI, không duyệt.",
          file=sys.stderr)
    sys.exit(2)

buy = [o for o in orders if o.get("side") == "buy"]
sell = [o for o in orders if o.get("side") == "sell"]
buy_total = sum((o.get("total_with_fee_vnd") or o.get("value_vnd") or 0) for o in buy)
sell_gross = sum((o.get("estimated_proceeds_vnd") or o.get("value_vnd") or 0) for o in sell)
sell_fee = sum((o.get("fee_est_vnd") or 0) for o in sell)
sell_net = sell_gross - sell_fee

print(f"== {path} ==")
print(f"orders[]: {len(orders)} lệnh ({len(buy)} mua, {len(sell)} bán)")
for o in buy:
    print(f"  MUA {o['ticker']:6s} {o.get('qty'):>6} cp @ {o.get('ref_price',0):>10,.0f}đ  "
          f"priority={o.get('priority')}")
cash_before = (plan.get("nav_basis") or {}).get("available_cash_before_vnd")
cash_src = "nav_basis.available_cash_before_vnd"
if cash_before is None:
    cash_before = (plan.get("orders_summary") or {}).get("available_cash_before_vnd")
    cash_src = "orders_summary.available_cash_before_vnd (fallback)"
if cash_before is None:
    cash_before = 0
    cash_src = "KHÔNG CÓ trong plan — fallback 0 (không đoán số)"
funding_total = cash_before + sell_net

print(f"  Σ MUA (+phí) = {buy_total:,.0f} VND")
print(f"  Σ BÁN ròng (−phí) = {sell_net:,.0f} VND ({len(sell)} lệnh)")
print(f"  Tiền mặt sẵn có = {cash_before:,.0f} VND  [{cash_src}]")
print(f"  Σ NGUỒN TÀI TRỢ (tiền mặt + bán ròng) = {funding_total:,.0f} VND")
if funding_total < buy_total:
    print(f"❌ NGUỒN TÀI TRỢ ({funding_total:,.0f}) < Σ MUA ({buy_total:,.0f}) — KHÔNG đủ tiền "
          f"tài trợ. DỪNG LẠI, không duyệt.", file=sys.stderr)
    sys.exit(2)
print(f"  ✅ NGUỒN TÀI TRỢ >= Σ MUA (chênh lệch +{funding_total-buy_total:,.0f} VND)")

if plan.get("approved_by") not in (None, ""):
    print(f"❌ plan ĐÃ CÓ approved_by={plan.get('approved_by')!r} — không ghi đè.",
          file=sys.stderr)
    sys.exit(2)

if dry_run:
    print("\n[DRY_RUN=1] KHÔNG ghi gì.")
    sys.exit(0)

plan["approved_by"] = approved_by
plan["approved_at"] = dt.datetime.now(ICT).isoformat(timespec="seconds")
tmp = path + ".tmp"
with open(tmp, "w", encoding="utf-8") as f:
    json.dump(plan, f, ensure_ascii=False, indent=2)
os.replace(tmp, path)
print(f"\n✅ ĐÃ GHI approved_by={approved_by!r} approved_at={plan['approved_at']}")
PYEOF
RC=$?

if [[ "$RC" -ne 0 || "$DRY_RUN" == "1" ]]; then
  exit "$RC"
fi

"$MIKE_ROOT/bin/append_event.sh" Mike decision "plan-approval-${ACCOUNT}-${PLAN_DATE}" \
  "{\"account\":\"${ACCOUNT}\",\"date\":\"${PLAN_DATE}\",\"approved_by\":\"${APPROVED_BY}\",\"decided_by\":\"user\"}" \
  || echo "⚠ append_event.sh lỗi — bus event không ghi được, báo lại kênh duyệt plan bằng tay."

"$MIKE_ROOT/bin/notify_thread.sh" \
  "✅ **DUYỆT PLAN** — ${ACCOUNT} · ${PLAN_DATE}. Người duyệt: ${APPROVED_BY}" \
  plan_approval \
  || echo "⚠ notify_thread.sh lỗi — Discord không nhận được, báo lại kênh duyệt plan bằng tay."

echo "Xong. Bot sẽ tự nhận trong lần retry/khởi động kế tiếp."
