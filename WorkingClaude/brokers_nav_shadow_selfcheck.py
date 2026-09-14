#!/usr/bin/env python3
"""Selfcheck — code-quality-weekly 2026-09-13, batch 1 (job Taylor_20260913_050827):

#3 make_broker() nhánh live truyền `loan_package_id=` cho mọi BROKER_CLASSES ⇒ PHSBroker phải
   nhận tham số (trước đây TypeError). RED control: bản brokers.py ở base (git) PHẢI ném.

Phần #2 (DNSEBroker.get_nav() shadow NAV_BASIS + cờ `nav_include_egg_offbook`) đã GỠ 2026-09-13
cùng get_nav()/V23Strategy (cq-20260913-remove-v23, user duyệt "gỡ hẳn") — caller duy nhất là
V23Strategy.build_plan, 0/148 plan 2026 dùng. Tên file giữ nguyên để không lệch production_manifest.

Base so sánh = `b53d26b4` (repo ngoài, trước bản vá #3). Không kết nối PHS thật.
Chạy: source wc_env.sh && env -u TZ MIKE_BOT_TEST_MODE=1 $DNA_PYEXE brokers_nav_shadow_selfcheck.py
"""
import importlib.util
import os
import subprocess
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
WC = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC)

import trading_bot.brokers as B                        # noqa: E402

FAILS = []
N = 0


def check(name, cond, detail=""):
    global N
    N += 1
    print(f"  {'PASS' if cond else 'FAIL'}  {name}{(' — ' + str(detail)) if detail else ''}")
    if not cond:
        FAILS.append(name)


def load_base_brokers():
    """brokers.py trước bản vá (commit gốc của repo ngoài chứa WorkingClaude/)."""
    top = subprocess.run(["git", "-C", WC, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    rel = os.path.relpath(os.path.join(WC, "trading_bot", "brokers.py"), top)
    ref = os.environ.get("BROKERS_SELFCHECK_BASE_REF", "b53d26b4")  # repo ngoài, trước bản vá
    src = subprocess.run(["git", "-C", top, "show", f"{ref}:{rel}"],
                         capture_output=True, text=True, check=True).stdout
    with tempfile.TemporaryDirectory(prefix="brokers_base_") as d:
        path = os.path.join(d, "brokers_base.py")
        open(path, "w", encoding="utf-8").write(src)
        spec = importlib.util.spec_from_file_location("trading_bot._brokers_base", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    return mod, ref


def main():
    base, ref = load_base_brokers()
    print(f"[base = {ref}:trading_bot/brokers.py]")

    q = B.Quote({"symbol": "AAA", "lastPrice": 23456.0})
    check("Quote giả dựng được, last đúng đơn vị VND", q.ok() and q.last == 23456.0, q)

    print("\n#3 make_broker phs mode=live")
    cfg = {"mode": "live", "paper_init_cash": 1, "paper_fee_rate": 0}
    prof = {"label": "phs_live_test", "broker": "phs", "credentials_file": None,
            "account_id": "X", "loan_package_id": None}
    try:
        b = B.make_broker(cfg, profile=prof)
        check("không TypeError, trả PHSBroker chưa connect", isinstance(b, B.PHSBroker)
              and b.client is None)
    except TypeError as e:
        check("không TypeError", False, e)
    try:
        base.make_broker(cfg, profile=prof)
        check("RED control: bản base PHẢI TypeError", False, "không ném")
    except TypeError as e:
        check("RED control: bản base TypeError", "loan_package_id" in str(e), e)

    print(f"\n{N - len(FAILS)}/{N} PASS")
    if FAILS:
        print("FAIL:", FAILS)
        return 1
    print("ALL PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
