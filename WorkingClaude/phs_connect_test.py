# -*- coding: utf-8 -*-
"""Kiểm tra kết nối tài khoản PHS thật — CHỈ các API đọc, không đặt/sửa/hủy lệnh.

Cách dùng:
  1. Điền username/password vào data/phs_credentials.json
  2. python phs_connect_test.py            # REST: login + số dư + danh mục
  3. python phs_connect_test.py --stream   # thêm stream room account ~15s
"""

import argparse
import json
import os
import sys
import time

from phs_flex_api import FlexClient, FlexError, FlexStream

WORKDIR = os.path.dirname(os.path.abspath(__file__))
CRED_FILE = os.path.join(WORKDIR, "secrets", "phs_credentials.json")


def load_credentials():
    user = os.environ.get("PHS_USERNAME")
    pw = os.environ.get("PHS_PASSWORD")
    if user and pw:
        return user, pw
    if os.path.exists(CRED_FILE):
        with open(CRED_FILE, encoding="utf-8") as f:
            d = json.load(f)
        user, pw = d.get("username", ""), d.get("password", "")
        if user and "DIEN_" not in user and pw and "DIEN_" not in pw:
            return user, pw
    sys.exit(f"Chưa có credentials — điền vào {CRED_FILE} "
             "hoặc set env PHS_USERNAME/PHS_PASSWORD.")


def fmt(x, width=80):
    return json.dumps(x, ensure_ascii=False)[:width]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stream", action="store_true",
                    help="stream room account sau khi check REST")
    args = ap.parse_args()

    user, pw = load_credentials()
    c = FlexClient()

    print(f"== Đăng nhập tài khoản {user[:4]}*** ==")
    c.login(user, pw)
    print("   OK — token hết hạn sau",
          int(c.token_expiry - time.time()) // 3600, "giờ,",
          "otp_token:", "có" if c.otp_token else "KHÔNG")

    print("\n== 2.4 Tiểu khoản ==")
    accounts = c.sub_accounts()
    for a in accounts:
        print(f"   {a.get('id')}  {a.get('typename', '')}  "
              f"({a.get('name', '')}, {a.get('afstatus', '')})")
    acc = accounts[0]["id"]
    print(f"   → dùng tiểu khoản đầu tiên: {acc}")

    print("\n== 2.1 Số dư tiền ==")
    bal = c.cash_balance(acc)
    row = bal[0] if isinstance(bal, list) and bal else bal
    for k in ("balance", "pp", "baldefovd", "avladvance", "totalloan"):
        if isinstance(row, dict) and k in row:
            print(f"   {k:14s} = {row[k]:,}")

    print("\n== 2.2 Tổng hợp tài khoản ==")
    summ = c.account_summary(acc)
    row = summ[0] if isinstance(summ, list) and summ else summ
    for k in ("navaccount", "totalassamt", "totalsevalue", "tongtien"):
        if isinstance(row, dict) and k in row:
            print(f"   {k:14s} = {row[k]:,}")

    print("\n== 1.7 Chứng khoán hiện có ==")
    port = c.portfolio(acc)
    if port:
        for p in port:
            print(f"   {p.get('symbol'):8s} total={p.get('total'):>10,} "
                  f"giá vốn={p.get('costPrice'):>10,} pnl={p.get('pnlAmt'):>12,}")
    else:
        print("   (danh mục trống)")

    print("\n== 1.8 Sức mua (thử với HPG) ==")
    print("  ", fmt(c.buying_power(acc, "HPG"), 200))

    print("\n== 1.6 Sổ lệnh trong ngày ==")
    orders = c.daily_orders(acc)
    if orders:
        for o in orders[:10]:
            print(f"   {o.get('orderid')} {o.get('symbol')} {o.get('exectype')} "
                  f"{o.get('orderqtty')}@{o.get('quoteprice')} → {o.get('status')}")
    else:
        print("   (chưa có lệnh nào hôm nay)")

    print("\n✅ REST OK — kết nối tài khoản thật thành công.")

    if args.stream:
        print(f"\n== Streaming room account:{acc} (15s) ==")
        s = FlexStream(access_token=c.access_token)
        s.on_account(lambda m: print("   account msg:", fmt(m, 300)))
        s.connect()
        s.subscribe_account([acc])
        time.sleep(15)
        s.disconnect()
        print("✅ Stream OK (message chỉ phát khi có biến động lệnh/tài khoản).")


if __name__ == "__main__":
    try:
        main()
    except FlexError as e:
        sys.exit(f"❌ FlexError: {e} (HTTP {e.status})")
