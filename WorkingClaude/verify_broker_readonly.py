# -*- coding: utf-8 -*-
"""Mafee step-2 verify: kết nối broker READ-ONLY (KHÔNG trading-token, KHÔNG đặt lệnh).

DNSE: accounts / balances / positions / ppse / market-data.
PHS : login (read scope) / sub_accounts / cash_balance / portfolio / buying_power.
Mọi call chỉ truy vấn — không tạo/sửa/hủy lệnh nào.
"""
import json
import sys
import traceback

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TARGET_ACCT = "0001743768"   # tiểu khoản DNSE theo directive
SYMBOL = "HPG"


def short(x, n=400):
    try:
        return json.dumps(x, ensure_ascii=False)[:n]
    except Exception:
        return str(x)[:n]


def verify_dnse():
    print("\n===== DNSE (READ-ONLY) =====")
    try:
        from dnse_api import DNSEClient
        c = DNSEClient.from_credentials_file()
    except Exception as e:
        print(f"[FAIL] khởi tạo client: {e}")
        return False
    ok = True

    try:
        accs = c.accounts()
        ids = [a.get("id") for a in accs.get("accounts", [])]
        print(f"[OK]  accounts: {ids}")
        if TARGET_ACCT not in ids:
            print(f"[WARN] tiểu khoản đích {TARGET_ACCT} KHÔNG có trong danh sách")
    except Exception as e:
        print(f"[FAIL] accounts: {e}")
        return False

    acc = TARGET_ACCT if TARGET_ACCT in ids else (ids[0] if ids else None)
    if not acc:
        print("[FAIL] không có tiểu khoản để query")
        return False
    print(f"      -> dùng tiểu khoản: {acc}")

    for name, fn in (
        ("balances", lambda: c.balances(acc)),
        ("positions", lambda: c.positions(acc)),
        ("latest_quote", lambda: c.latest_quote(SYMBOL)),
    ):
        try:
            print(f"[OK]  {name}: {short(fn())}")
        except Exception as e:
            ok = False
            print(f"[FAIL] {name}: {e}")

    # ppse cần 1 giá nguyên hợp lệ — lấy best-bid từ latest_quote
    try:
        q = c.latest_quote(SYMBOL)["quotes"][0]
        px = int(round(float(q["bid"][0]["price"]) * 1000))   # 23.6 -> 23600
        print(f"[OK]  ppse({SYMBOL}@{px}): {short(c.ppse(acc, SYMBOL, px))}")
    except Exception as e:
        ok = False
        print(f"[FAIL] ppse: {e}")
    return ok


def verify_phs():
    print("\n===== PHS (READ-ONLY; live order BLOCKED -700003) =====")
    try:
        from phs_flex_api import FlexClient
        c = FlexClient.from_credentials_file(auto_login=True)
    except Exception as e:
        print(f"[FAIL] khởi tạo/login PHS: {e}")
        return False
    ok = True
    acc = None
    try:
        subs = c.sub_accounts()
        print(f"[OK]  sub_accounts: {short(subs)}")
        if isinstance(subs, list) and subs:
            first = subs[0]
            acc = first.get("account_id") or first.get("id") or first.get("accountNo") \
                if isinstance(first, dict) else first
    except Exception as e:
        ok = False
        print(f"[FAIL] sub_accounts: {e}")

    if acc:
        for name, fn in (
            ("cash_balance", lambda: c.cash_balance(acc)),
            ("portfolio", lambda: c.portfolio(acc)),
        ):
            try:
                print(f"[OK]  {name}: {short(fn())}")
            except Exception as e:
                ok = False
                print(f"[FAIL] {name}: {e}")
    else:
        print("[WARN] không lấy được account_id PHS -> bỏ qua cash/portfolio")
    return ok


if __name__ == "__main__":
    results = {}
    for label, fn in (("DNSE", verify_dnse), ("PHS", verify_phs)):
        try:
            results[label] = fn()
        except Exception:
            results[label] = False
            print(f"[FAIL] {label} ngoại lệ:\n{traceback.format_exc()}")
    print("\n===== TÓM TẮT =====")
    for k, v in results.items():
        print(f"  {k}: {'PASS' if v else 'FAIL/PARTIAL'}")
