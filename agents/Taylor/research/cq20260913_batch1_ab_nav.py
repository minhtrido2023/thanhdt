"""A/B dry-run #2: V23Strategy.build_plan cờ nav_include_egg_offbook OFF vs ON — KHÔNG đặt lệnh,
KHÔNG ghi plan thật (JSON ra /tmp/cqb1/ab), KHÔNG ghi dnse_raw (_raw_log=None)."""
import json, os, sys
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
WC = "/home/trido/thanhdt/WorkingClaude"; sys.path.insert(0, WC); os.chdir(WC)
from trading_bot.config import load_config, load_accounts, pick_accounts
from trading_bot.brokers import make_broker
from trading_bot.strategies import get_strategy
base = load_config()
out = {}
for p in pick_accounts(load_accounts(base), ["SpaceX", "ZaloPay"]):
    res = {}
    for flag in (False, True):
        cfg = dict(p["cfg"]); cfg["nav_include_egg_offbook"] = flag
        b = make_broker(cfg, profile=p); b._raw_log = None; b.connect(); b._raw_log = None
        plan = get_strategy(cfg["strategy"]).build_plan(cfg, b)
        res["ON" if flag else "OFF"] = {
            "nav_basis": plan.nav_basis, "notes": [n for n in plan.notes if "NAV_BASIS" in n],
            "orders": {f"{o.side}:{o.ticker}": {"qty": o.qty, "value": round(o.value)} for o in plan.orders},
            "n_orders": len(plan.orders), "signal_date": plan.signal_date, "strategy": plan.strategy}
    out[p["label"]] = res
json.dump(out, open("/tmp/cqb1/ab/ab_nav.json", "w"), ensure_ascii=False, indent=1, default=str)
print("wrote /tmp/cqb1/ab/ab_nav.json")
