# -*- coding: utf-8 -*-
"""Bước 1 — Chuẩn bị trading plan từ V2.3 (chạy EOD sau golive_recommend_v23 + pt_v22_dt5g).

  python bot_prepare_plan.py                    # MỌI account enabled trong
                                                # data/trading_bot_accounts.json
  python bot_prepare_plan.py --account main     # chỉ 1 account (lặp lại được)
  python bot_prepare_plan.py --date 2026-06-12  # ép signal date
  python bot_prepare_plan.py --dry              # chỉ in, không ghi file plan

Output: data/trade_plans/plan_<account>_<T+1>.json — đầu vào của bot_execute.py.
Mỗi account tự scale theo NAV của chính nó (plan độc lập hoàn toàn).
"""

import argparse
import sys

if hasattr(sys.stdout, "reconfigure"):  # console Windows cp1252 → utf-8
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from trading_bot.config import load_config, load_accounts, pick_accounts
from trading_bot.brokers import make_broker
from trading_bot.strategies import get_strategy


def main():
    ap = argparse.ArgumentParser(description="Chuẩn bị trading plan (đa tài khoản)")
    ap.add_argument("--account", action="append", default=None,
                    help="label account (lặp lại được); mặc định mọi account enabled")
    ap.add_argument("--date", default=None, help="signal date YYYY-MM-DD")
    ap.add_argument("--strategy", default=None, help="override config strategy")
    ap.add_argument("--mode", default=None, choices=["paper", "live"],
                    help="override mode cho MỌI account được chọn")
    ap.add_argument("--dry", action="store_true", help="chỉ in plan, không ghi file")
    args = ap.parse_args()

    base = load_config()
    profiles = pick_accounts(load_accounts(base), args.account)
    if not profiles:
        sys.exit("không có account nào enabled — sửa data/trading_bot_accounts.json")

    written = []
    for p in profiles:
        cfg = dict(p["cfg"])
        if args.mode:
            cfg["mode"] = args.mode
        strat = get_strategy(args.strategy or cfg["strategy"])
        # nguồn quote paper được pool theo (broker, credentials) trong make_broker
        broker = make_broker(cfg, profile=p).connect()
        plan = strat.build_plan(cfg, broker, signal_date=args.date)
        plan.account = p["label"]
        print()
        print(plan.summary())
        if not args.dry:
            written.append(plan.save())

    if args.dry:
        print("\n(dry — không ghi file)")
        return
    print(f"\n✅ đã ghi {len(written)} plan:")
    for w in written:
        print(f"   {w}")
    print("   thực thi trong phiên kế tiếp:  python bot_execute.py")


if __name__ == "__main__":
    sys.exit(main())
