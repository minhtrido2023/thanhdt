"""READ-ONLY probe: tái đo check_plan_funding cho ZaloPay 2026-08-10 (không đặt lệnh)."""
import os, sys, json
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")
from trading_bot.config import load_config, load_accounts, pick_accounts
from trading_bot.brokers import make_broker
from trading_bot.plan import load_plan, filter_excluded_tickers
from trading_bot.plan_funding_gate import check_plan_funding

base = load_config()
p = pick_accounts(load_accounts(base), ["ZaloPay"])[0]
cfg = dict(p["cfg"])
plan = load_plan("2026-08-10", p["label"])
plan, _blk = filter_excluded_tickers(plan, p.get("excluded_tickers"))
br = make_broker(cfg, otp=None, profile=p).connect()
res = check_plan_funding(plan, br, cfg["mode"])
print(json.dumps(res, ensure_ascii=False, indent=2, default=str))
