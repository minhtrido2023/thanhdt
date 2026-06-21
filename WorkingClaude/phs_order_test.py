# -*- coding: utf-8 -*-
"""Test đặt/hủy lệnh PHS FLEX — 1 lệnh LO mua 100 CP giá SÀN (không khớp) rồi hủy.

⚠ Chỉ chạy được khi PHS đã cấp client_id/client_secret riêng (điền vào
data/phs_credentials.json) — cặp mặc định bị chặn đặt lệnh (-700003).

Chạy TRONG GIỜ GIAO DỊCH (9:00–14:45, tốt nhất 9:20+ phiên liên tục):

  python phs_order_test.py --otp 123456       # Smart OTP từ app PHS
  python phs_order_test.py                    # otp_token cache còn hạn thì chạy thẳng

Tùy chọn: --symbol HPG --qty 100 --keep (không hủy) --force (ngoài giờ vẫn gửi).
"""

import argparse
import json
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from phs_flex_api import FlexError
from trading_bot.brokers import PHSBroker
from trading_bot.vn_market import session_phase


def main():
    ap = argparse.ArgumentParser(description="Test đặt/hủy lệnh PHS (giá sàn)")
    ap.add_argument("--symbol", default="HPG")
    ap.add_argument("--qty", type=int, default=100)
    ap.add_argument("--otp", default=None, help="Smart OTP từ app PHS")
    ap.add_argument("--keep", action="store_true", help="KHÔNG tự hủy lệnh")
    ap.add_argument("--force", action="store_true", help="chạy cả ngoài giờ giao dịch")
    args = ap.parse_args()

    phase, _ = session_phase()
    if phase in ("PRE", "CLOSED", "LUNCH") and not args.force:
        sys.exit(f"❌ ngoài giờ giao dịch (phiên: {phase}) — chạy 9:00–14:45 "
                 f"ngày giao dịch, hoặc --force.")

    b = PHSBroker(otp=args.otp, label="ordertest").connect()
    if not b.client.otp_token:
        sys.exit("❌ chưa có otp_token — chạy lại với --otp <Smart OTP>.")

    q = b.get_quote(args.symbol)
    if not (q and q.ok() and q.floor):
        sys.exit(f"❌ không lấy được giá sàn của {args.symbol}: {q}")
    floor = int(q.floor)
    print(f"\n{args.symbol}: last={q.last:,.0f} sàn={floor:,} trần={q.ceiling:,.0f} "
          f"→ đặt MUA {args.qty} @ {floor:,} (giá sàn, gần như không khớp)")

    # 1) ĐẶT
    try:
        oid = b.place_order(args.symbol, args.qty, "buy", price=floor)
    except (FlexError, RuntimeError) as e:
        pay = getattr(e, "payload", None)
        hint = ("\n   → vẫn là lỗi -700003: PHS chưa kích hoạt client_id/secret "
                "cho đặt lệnh." if pay and "700003" in str(pay) else "")
        sys.exit(f"❌ PLACE FAIL: {e}{hint}")
    print(f"✅ PLACE OK — orderId = {oid}")

    # 2) POLL trạng thái
    for _ in range(5):
        time.sleep(2)
        ups = b.poll_orders()
        if oid in ups:
            print(f"   sổ lệnh: status='{ups[oid].status}' filled={ups[oid].filled_qty}")
            break

    if args.keep:
        print("ℹ --keep: giữ lệnh, tự hủy trên app PHS nếu cần.")
        return 0

    # 3) HỦY + xác nhận
    try:
        r = b.cancel_order(oid)
        print(f"✅ CANCEL gửi OK — resp: {json.dumps(r, ensure_ascii=False)[:200]}")
    except (FlexError, RuntimeError) as e:
        sys.exit(f"❌ CANCEL FAIL: {e} — HỦY TAY trên app PHS ngay!")
    for _ in range(5):
        time.sleep(2)
        ups = b.poll_orders()
        if oid in ups and ups[oid].is_dead:
            print(f"✅ CONFIRMED — status cuối: '{ups[oid].status}'")
            print("\n🎉 TEST PASS: đặt + hủy lệnh PHS hoạt động.")
            return 0
    print("⚠ chưa xác nhận được trạng thái hủy — kiểm tra sổ lệnh app PHS "
          "+ data/execution_logs/phs_raw_*.jsonl")
    return 1


if __name__ == "__main__":
    sys.exit(main())
