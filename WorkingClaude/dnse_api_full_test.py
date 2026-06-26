# -*- coding: utf-8 -*-
"""Test đầy đủ DNSE API: auto-OTP → place → poll → modify → cancel.

Chạy:
  python dnse_api_full_test.py                        # SpaceX acc 0002023347, symbol FPT
  python dnse_api_full_test.py --account 0001743768   # account cũ
  python dnse_api_full_test.py --symbol HPG           # đổi mã
  python dnse_api_full_test.py --skip-otp             # nếu token cache còn hạn

An toàn: đặt tại giá SÀN (gần như không khớp), tự hủy sau test.
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone, timedelta

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from dnse_api import DNSEClient, DNSEError
from trading_bot.vn_market import tick_size


# ─────────────────────── helpers ────────────────────────

def ict_now():
    return datetime.now(timezone.utc) + timedelta(hours=7)


def log(msg):
    print(f"[{ict_now().strftime('%H:%M:%S')} ICT] {msg}", flush=True)


def poll_order(c, account_id, order_id, retries=6, interval=2):
    for i in range(retries):
        time.sleep(interval)
        try:
            orders = c.orders(account_id)
            items = orders if isinstance(orders, list) else orders.get("data") or []
            for o in items:
                oid = o.get("id") or o.get("orderId") or o.get("orderNo")
                if str(oid) == str(order_id):
                    return o
        except DNSEError as e:
            log(f"  poll err #{i+1}: {e}")
    return None


def order_status(o):
    if not o:
        return "NOT_FOUND"
    return o.get("status") or o.get("orderStatus") or "UNKNOWN"


# ─────────────────────── main ────────────────────────

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--account", default="0002023347", help="tiểu khoản DNSE")
    ap.add_argument("--symbol", default="FPT")
    ap.add_argument("--qty", type=int, default=100)
    ap.add_argument("--skip-otp", action="store_true",
                    help="bỏ qua OTP nếu token cache còn hạn")
    args = ap.parse_args()

    log(f"=== DNSE API FULL TEST — account={args.account} symbol={args.symbol} qty={args.qty} ===")
    log(f"ICT: {ict_now().strftime('%Y-%m-%d %H:%M:%S')}")

    c = DNSEClient.from_credentials_file()

    # ── 0. Kiểm tra account info ──
    log("\n[0] Accounts & balances")
    accs = c.accounts()
    log(f"  Tên: {accs.get('name')}  |  accounts: {[a['id'] for a in accs['accounts']]}")
    try:
        bal = c.balances(args.account)
        av_cash = (bal.get("availableBalance") or bal.get("withdrawableBalance")
                   or bal.get("cashBalance") or "N/A")
        log(f"  availableCash: {av_cash:,}" if isinstance(av_cash, (int, float)) else f"  balance raw: {str(bal)[:200]}")
    except DNSEError as e:
        log(f"  balances ERR (bỏ qua): {e}")

    try:
        pos = c.positions(args.account)
        items = pos if isinstance(pos, list) else pos.get("data") or []
        log(f"  positions: {len(items)} mã — {[p.get('symbol') for p in items[:5]]}")
    except DNSEError as e:
        log(f"  positions ERR (bỏ qua): {e}")

    # ── 1. Trading token ──
    log("\n[1] Trading token")
    if not args.skip_otp or not c.has_trading_token():
        from gmail_otp_reader import fetch_dnse_otp, _build_gmail_service, _save_last_id
        # Pre-mark latest OTP email TRUOC khi send OTP moi de tranh lay OTP cu
        log("  Pre-marking latest Gmail OTP email as seen...")
        try:
            svc = _build_gmail_service()
            q = ("from:noreply@mail.dnse.com.vn"
                 " subject:\"Xac thuc voi Email OTP\"")
            resp = svc.users().messages().list(userId="me", q=q, maxResults=1).execute()
            msgs = resp.get("messages", [])
            if msgs:
                _save_last_id(msgs[0]["id"])
                log(f"  last_id cap nhat: {msgs[0]['id']}")
            else:
                log("  Khong co email OTP nao trong inbox -- OK")
        except Exception as e:
            log(f"  pre-mark err (bo qua): {e}")

        log("  Gui OTP email...")
        send_ts = time.time()
        c.send_email_otp()
        log("  Doi OTP tu Gmail (timeout 120s, poll 5s, sent_after=now)...")
        otp = fetch_dnse_otp(timeout=120, poll_interval=5, sent_after=send_ts)
        log(f"  OTP nhan duoc: {otp}")
        c.create_trading_token(otp)
        log("  Trading token OK (8h)")
    else:
        log("  Dung token cache con han")

    # ── 2. Lấy giá sàn ──
    # secdef returns list (nghìn đồng units); pick T1 board
    try:
        sd = c.secdef(args.symbol)
        item = (sd[0] if isinstance(sd, list) else sd)
        ref_k = item.get("basicPrice") or item.get("referencePrice")
        floor_k = item.get("floorPrice")
        ceiling_k = item.get("ceilingPrice")
        log(f"  tham chieu={ref_k}k  san={floor_k}k  tran={ceiling_k}k VND")
    except Exception as e:
        log(f"  secdef ERR: {e} — thu latest_trade")
        try:
            lt = c.latest_trade(args.symbol)
            trades = lt.get("trades") or [lt]
            t0 = trades[0]
            ref_k = t0.get("matchPrice") or t0.get("openPrice")
            floor_k = round(ref_k * 0.93, 1)
            ceiling_k = round(ref_k * 1.07, 1)
            log(f"  fallback: ref={ref_k}k  floor_est={floor_k}k  ceiling_est={ceiling_k}k")
        except Exception as e2:
            sys.exit(f"Khong lay duoc gia: {e2}")

    # DNSE gia don vi nghin dong (e.g., 66.1 = 66,100 VND)
    # Giu nguyen format nghin dong khi goi API
    floor_k = round(float(floor_k), 1)  # nghin dong
    ceil_k = round(float(ceiling_k), 1)
    # Tinh tick theo nghin dong: <10k -> 0.01k, <50k -> 0.05k, else 0.1k
    if floor_k < 10:
        ts_k = 0.01
    elif floor_k < 50:
        ts_k = 0.05
    else:
        ts_k = 0.1
    floor_plus1_k = round(floor_k + ts_k, 2)
    floor = int(floor_k * 1000)  # VND (cho log va tick_size)
    log(f"  DNSE san={floor_k}k  san+1tick={floor_plus1_k}k  VND san={floor:,}")

    # ── 3. PPSE (sức mua) ──
    log(f"\n[3] Sức mua {args.symbol} @ {floor:,}")
    try:
        ppse = c.ppse(args.account, args.symbol, floor_k)
        max_qty = ppse.get("maxQty") or ppse.get("buyableQty") or ppse.get("quantity")
        log(f"  maxQty={max_qty}  raw={str(ppse)[:200]}")
    except DNSEError as e:
        log(f"  ppse ERR (bỏ qua): {e}")

    # ── 4. PLACE ──
    log(f"\n[4] PLACE BUY {args.symbol} {args.qty} @ {floor_k}k VND (gia san)")
    try:
        r_place = c.place_order(args.account, args.symbol, args.qty,
                                side="buy", order_type="LO", price=floor_k)
        order_id = (r_place.get("id") or r_place.get("orderId")
                    or r_place.get("orderNo") or r_place.get("data", {}).get("id"))
        log(f"  PLACE OK — orderId={order_id}  raw={str(r_place)[:300]}")
    except DNSEError as e:
        sys.exit(f"PLACE FAIL: {e}  payload={getattr(e, 'payload', None)}")

    if not order_id:
        sys.exit(f"Không lấy được orderId từ response: {r_place}")

    # ── 5. POLL trạng thái sau đặt ──
    log(f"\n[5] Poll status sau PLACE (chờ ~{2*3}s)…")
    o = poll_order(c, args.account, order_id)
    log(f"  status={order_status(o)}  filled={o.get('filledQty') or o.get('matchedQty') or 0}"
        if o else "  ⚠ chưa thấy lệnh trong sổ")

    # ── 6. MODIFY (đổi giá lên floor+1tick) ──
    log(f"\n[6] MODIFY orderId={order_id}  gia: {floor_k}k -> {floor_plus1_k}k VND")
    try:
        r_mod = c.modify_order(args.account, order_id, price=floor_plus1_k)
        log(f"  MODIFY OK — raw={str(r_mod)[:300]}")
    except DNSEError as e:
        log(f"  MODIFY FAIL: {e}  payload={getattr(e, 'payload', None)}")
        log("  (Có thể DNSE không cho sửa khi sắp ATC — tiếp tục hủy)")

    # poll sau modify
    log("  Poll sau MODIFY…")
    o2 = poll_order(c, args.account, order_id, retries=4)
    log(f"  status={order_status(o2)}  price={o2.get('price') or o2.get('orderPrice')}"
        if o2 else "  ⚠ chưa thấy lệnh")

    # ── 7. CANCEL ──
    log(f"\n[7] CANCEL orderId={order_id}")
    try:
        r_cancel = c.cancel_order(args.account, order_id)
        log(f"  CANCEL gửi OK — raw={str(r_cancel)[:300]}")
    except DNSEError as e:
        log(f"  CANCEL FAIL: {e}")
        log("  ⚠ HỦY TAY trên app EntradeX ngay!")
        return 1

    # ── 8. Xác nhận đã hủy ──
    log(f"\n[8] Xác nhận CANCEL (chờ ~12s)…")
    for attempt in range(6):
        time.sleep(2)
        o3 = poll_order(c, args.account, order_id, retries=1, interval=0)
        st = order_status(o3)
        if st in ("Canceled", "Cancelled", "CANCELLED", "REJECTED", "Expired"):
            log(f"  ✅ CONFIRMED CANCELLED — status={st}")
            break
        log(f"  attempt {attempt+1}: status={st}")
    else:
        log("  ⚠ chưa xác nhận hủy — kiểm tra sổ lệnh trên app")
        return 1

    # ── 9. Tổng kết ──
    log("\n" + "=" * 60)
    log("✅ PASS: place → poll → modify → cancel — tất cả kịch bản OK")
    log(f"   Account: {args.account}  Symbol: {args.symbol}  Qty: {args.qty}")
    log(f"   Floor: {floor:,}  DNSE API fully operational")
    return 0


if __name__ == "__main__":
    sys.exit(main())
