# -*- coding: utf-8 -*-
"""Test đặt/hủy lệnh DNSE — 1 lệnh LO mua 100 CP giá SÀN (không khớp) rồi hủy ngay.

Chạy TRONG GIỜ GIAO DỊCH (9:00–14:45, tốt nhất 9:20+ phiên liên tục):

  python dnse_order_test.py --send-otp        # 1) gửi OTP vào email (hạn 2')
  python dnse_order_test.py --otp 123456      # 2) đổi OTP lấy trading-token + chạy test
  python dnse_order_test.py                   # (token cache còn hạn 8h thì chạy thẳng)

Tùy chọn: --symbol HPG --qty 100 --keep (không hủy, tự quản lý lệnh).
An toàn: đặt tại giá SÀN nên gần như không thể khớp; nếu lỡ khớp thì chỉ
mua 100 CP (~2.2M với HPG) — bán lại được, mất phí ~0.07%×2.
"""

import argparse
import json
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dnse_api import DNSEClient, DNSEError
from trading_bot.brokers import DNSEBroker
from trading_bot.vn_market import session_phase


def main():
    ap = argparse.ArgumentParser(description="Test đặt/hủy lệnh DNSE (giá sàn)")
    ap.add_argument("--symbol", default="HPG")
    ap.add_argument("--qty", type=int, default=100)
    ap.add_argument("--send-otp", action="store_true", help="gửi email OTP rồi thoát")
    ap.add_argument("--otp", default=None, help="mã OTP để lấy trading-token")
    ap.add_argument("--keep", action="store_true", help="KHÔNG tự hủy lệnh")
    ap.add_argument("--force", action="store_true", help="chạy cả ngoài giờ giao dịch")
    args = ap.parse_args()

    c = DNSEClient.from_credentials_file()

    if args.send_otp:
        c.send_email_otp()
        print("✅ đã gửi OTP vào email (hạn 2 phút) — chạy lại:  "
              "python dnse_order_test.py --otp <mã>")
        return 0

    phase, _ = session_phase()
    if phase in ("PRE", "CLOSED", "LUNCH") and not args.force:
        sys.exit(f"❌ ngoài giờ giao dịch (phiên: {phase}) — lệnh sẽ bị từ chối. "
                 f"Chạy 9:00–14:45 ngày giao dịch, hoặc --force để thử vẫn gửi.")

    if args.otp:
        c.create_trading_token(args.otp)
        print("✅ trading-token mới (hạn 8h, đã cache)")
    elif not c.has_trading_token():
        sys.exit("❌ chưa có trading-token — chạy --send-otp rồi --otp <mã> "
                 "(hoặc Smart OTP: --otp <mã trên app>).")
    else:
        print("ℹ dùng trading-token trong cache (còn hạn)")

    acc = c.accounts()["accounts"][0]["id"]
    b = DNSEBroker(account_id=acc, label="ordertest")
    b.client = c
    q = b.get_quote(args.symbol)
    if not (q and q.ok() and q.floor):
        sys.exit(f"❌ không lấy được giá sàn của {args.symbol}: {q}")
    floor = int(q.floor)
    print(f"\n{args.symbol}: last={q.last:,.0f} sàn={floor:,} trần={q.ceiling:,.0f} "
          f"→ đặt MUA {args.qty} @ {floor:,} (giá sàn, gần như không khớp)")

    # 1) ĐẶT
    try:
        oid = b.place_order(args.symbol, args.qty, "buy", price=floor)
    except (DNSEError, RuntimeError) as e:
        sys.exit(f"❌ PLACE FAIL: {e}\n   payload: {getattr(e, 'payload', None)}")
    print(f"✅ PLACE OK — orderId = {oid}")

    # 2) POLL trạng thái
    st = None
    for _ in range(5):
        time.sleep(2)
        ups = b.poll_orders()
        if oid in ups:
            st = ups[oid]
            print(f"   sổ lệnh: status='{st.status}' filled={st.filled_qty}")
            break
    if st is None:
        print("   ⚠ chưa thấy lệnh trong sổ — xem dnse_raw jsonl")

    if args.keep:
        print("ℹ --keep: giữ lệnh, tự hủy trên app/EntradeX nếu cần.")
        return 0

    # 3) HỦY
    try:
        r = b.cancel_order(oid)
        print(f"✅ CANCEL gửi OK — resp: {json.dumps(r, ensure_ascii=False)[:200]}")
    except (DNSEError, RuntimeError) as e:
        sys.exit(f"❌ CANCEL FAIL: {e} — HỦY TAY trên app/EntradeX ngay!")

    # 4) xác nhận đã hủy
    for _ in range(5):
        time.sleep(2)
        ups = b.poll_orders()
        if oid in ups and ups[oid].is_dead:
            print(f"✅ CONFIRMED — status cuối: '{ups[oid].status}'")
            print("\n🎉 TEST PASS: đặt + hủy lệnh DNSE hoạt động. "
                  "Sẵn sàng go-live bot (mirror V2.3, dọn 5 vị thế cũ).")
            return 0
    print("⚠ chưa xác nhận được trạng thái hủy — kiểm tra sổ lệnh trên app "
          "+ data/execution_logs/dnse_raw_*.jsonl")
    return 1


if __name__ == "__main__":
    sys.exit(main())
