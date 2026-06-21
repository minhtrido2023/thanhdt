# -*- coding: utf-8 -*-
"""Bước 2 — Thực thi trading plan trong phiên (chạy sáng trước 09:15, để chạy cả ngày).

  python bot_execute.py                       # MỌI account có plan hôm nay, 1 process
  python bot_execute.py --account main        # chỉ 1 account (lặp lại được)
  python bot_execute.py --otp main=123456 --otp acc2=654321   # Smart OTP theo account
  python bot_execute.py --otp 123456          # 1 OTP áp cho mọi account live cùng login
  python bot_execute.py --date 2026-06-13     # ép ngày plan
  python bot_execute.py --once                # 1 vòng rồi thoát (debug)
  python bot_execute.py --force-phase MORNING # test ngoài giờ (paper)
  python bot_execute.py --probe HPG [--broker dnse]  # dump quote thô rồi thoát
  python bot_execute.py --send-otp acc_dnse   # gửi email OTP (DNSE email_otp) rồi thoát

Tất cả account chạy trong MỘT vòng lặp, dùng chung quota participation
(các tài khoản không tự cạnh tranh nhau trên cùng một mã).
Dừng khẩn cấp: tạo file data/BOT_STOP (hủy lệnh treo MỌI account rồi thoát).
Giết process giữa chừng vô hại — chạy lại là resume từ state đã lưu.
"""

import argparse
import datetime as dt
import json
import sys

if hasattr(sys.stdout, "reconfigure"):  # console Windows cp1252 → utf-8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from trading_bot.config import load_config, load_accounts, pick_accounts
from trading_bot.brokers import make_broker, get_quote_source, get_dnse_client
from trading_bot.plan import load_plan
from trading_bot.executor import Executor, run_session


def parse_otp(items):
    """["main=123456","acc2=654321"] hoặc ["123456"] → (dict label→otp, otp chung)."""
    per, common = {}, None
    for it in items or []:
        if "=" in it:
            k, v = it.split("=", 1)
            per[k.strip()] = v.strip()
        else:
            common = it.strip()
    return per, common


def main():
    ap = argparse.ArgumentParser(description="Thực thi trading plan (đa tài khoản)")
    ap.add_argument("--account", action="append", default=None,
                    help="label account (lặp lại được); mặc định mọi account enabled")
    ap.add_argument("--date", default=None, help="plan date YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--mode", default=None, choices=["paper", "live"],
                    help="override mode cho MỌI account được chọn")
    ap.add_argument("--otp", action="append", default=None,
                    help="Smart OTP: 'label=123456' (lặp lại) hoặc '123456' chung")
    ap.add_argument("--once", action="store_true", help="chạy 1 vòng rồi thoát")
    ap.add_argument("--max-cycles", type=int, default=None)
    ap.add_argument("--force-phase", default=None,
                    choices=["MORNING", "AFTERNOON", "ATC"], help="test ngoài giờ")
    ap.add_argument("--probe", default=None, metavar="SYMBOL",
                    help="in payload quote thô của 1 mã rồi thoát")
    ap.add_argument("--broker", default="phs", choices=["phs", "dnse"],
                    help="broker cho --probe")
    ap.add_argument("--send-otp", default=None, metavar="LABEL",
                    help="gửi email OTP cho account DNSE (email_otp) rồi thoát")
    args = ap.parse_args()

    if args.probe:
        b = get_quote_source(args.broker).connect()
        q = b.get_quote(args.probe)
        print(json.dumps(q.raw if q else None, indent=2, ensure_ascii=False, default=str))
        print("\nparsed:", q)
        return 0

    base = load_config()

    if args.send_otp:
        profiles = pick_accounts(load_accounts(base), [args.send_otp])
        c = get_dnse_client(profiles[0].get("credentials_file"))
        c.send_email_otp()
        print(f"✅ đã gửi OTP vào email (hạn 2 phút) — chạy lại với "
              f"--otp {args.send_otp}=<mã>")
        return 0
    profiles = pick_accounts(load_accounts(base), args.account)
    otp_by_label, otp_common = parse_otp(args.otp)
    plan_date = args.date or dt.date.today().strftime("%Y-%m-%d")

    shared_fills = {}                            # sổ participation chung của fleet

    executors = []
    for p in profiles:
        cfg = dict(p["cfg"])
        if args.mode:
            cfg["mode"] = args.mode
        plan = load_plan(plan_date, account=p["label"])
        if plan is None:
            print(f"[{p['label']}] không có plan cho {plan_date} — bỏ qua "
                  f"(chạy bot_prepare_plan.py trước)")
            continue
        if not plan.orders:
            print(f"[{p['label']}] plan {plan_date} không có lệnh — bỏ qua")
            continue
        otp = otp_by_label.get(p["label"], otp_common)
        if cfg["mode"] == "live" and otp is None:
            print(f"⚠ [{p['label']}] mode live chưa có --otp: nếu otp_token cache "
                  f"còn hạn vẫn chạy được, hết hạn lệnh sẽ bị từ chối.")
        broker = make_broker(cfg, otp=otp, profile=p).connect()
        if cfg["mode"] == "paper" and hasattr(broker, "set_fallback_refs"):
            broker.set_fallback_refs({o.ticker: o.ref_price for o in plan.orders})
        executors.append(Executor(plan, broker, cfg, shared=shared_fills))

    if not executors:
        sys.exit(f"❌ không có account nào có plan thực thi cho {plan_date}.")

    run_session(executors, once=args.once, max_cycles=args.max_cycles,
                force_phase=args.force_phase)
    return 0


if __name__ == "__main__":
    sys.exit(main())
