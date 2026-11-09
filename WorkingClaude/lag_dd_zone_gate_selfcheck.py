# -*- coding: utf-8 -*-
"""lag_dd_zone_gate_selfcheck.py — self-check cho trading_bot.plan.filter_lag_dd_zone_orders
(luật user 2026-11-09: mua LAG cần DD + giá ≤ tâm). Offline: sổ DD giả qua monkeypatch _lag_dd_zone_deps.
Chạy: python3 lag_dd_zone_gate_selfcheck.py [--live]   (--live: replay trên sổ THẬT + plan 10/11 nếu có)
Không phụ thuộc TZ (asof tường minh, §16); chạy lại dưới `env -u TZ`.
"""
import datetime as dt
import os
import sys

CODE_ROOT = os.environ.get("LAGZONE_CODE_ROOT") or os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, CODE_ROOT)
from trading_bot import plan as pm                                  # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan                # noqa: E402

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    PASS, FAIL = (PASS + 1, FAIL) if cond else (PASS, FAIL + 1)
    print(("  PASS  " if cond else "  FAIL  ") + name + ("" if cond else "  " + str(detail)))


def mk(specs, asof="2026-11-10"):
    os_ = [PlannedOrder(id=f"{s[2].upper()}-{s[0]}-{i}", ticker=s[0], side=s[2], qty=1000,
                        ref_price=s[3], book=s[1]) for i, s in enumerate(specs)]
    return TradePlan(plan_date=asof, signal_date=asof, strategy="t", strategy_version="0", state=3,
                     state_name="N", nav_basis={}, orders=os_, account="SELFCHECK")


def E(t, center, d="2026-11-09", rev=1, lo=1, hi=None):
    return {"ticker": t, "dd_date": d, "rev": rev, "center": center, "zone_low": lo,
            "zone_high": hi or center * 1.3}


LEDGER = {"entries": [E("AAA", 10000), E("BBB", 10000, d="2026-11-20"), E("CCC", 10000),
                      E("CCC", 12000, rev=2), E("LCK", 10000)]}


def fake_deps(lock_bad=()):
    def latest(ledger, asof=None):
        out = {}
        for e in ledger["entries"]:
            if asof is not None and e["dd_date"] > asof.isoformat():
                continue
            k = (e["dd_date"], e.get("rev", 1))
            t = e["ticker"]
            if t not in out or k >= (out[t]["dd_date"], out[t].get("rev", 1)):
                out[t] = e
        return out
    return lambda: (latest, (lambda e: "md5 lệch" if e["ticker"] in lock_bad else None), LEDGER)


def run(specs, lock_bad=(), deps=None):
    pm._lag_dd_zone_deps = deps or fake_deps(lock_bad)
    return pm.filter_lag_dd_zone_orders(mk(specs))


print("== unit ==")
p, b = run([("AAA", "LAG", "buy", 9000)]);               check("giá < tâm ⇒ GIỮ", len(p.orders) == 1 and not b)
p, b = run([("AAA", "LAG", "buy", 10000)]);              check("giá == tâm ⇒ GIỮ", len(p.orders) == 1 and not b)
p, b = run([("AAA", "LAG", "buy", 10001)]);              check("giá > tâm 1đ ⇒ LOẠI", len(p.orders) == 0 and len(b) == 1)
p, b = run([("ZZZ", "LAG", "buy", 5000)]);               check("không có DD ⇒ LOẠI", len(p.orders) == 0 and "chưa có DD" in b[0]["reason"])
p, b = run([("BBB", "LAG", "buy", 5000)]);               check("DD tương lai (dd_date > asof) ⇒ coi như chưa có ⇒ LOẠI", len(p.orders) == 0)
p, b = run([("CCC", "LAG", "buy", 11000)]);              check("rev mới nhất thắng (tâm 12000) ⇒ GIỮ", len(p.orders) == 1)
p, b = run([("LCK", "LAG", "buy", 5000)], lock_bad=("LCK",)); check("khoá md5 lệch ⇒ LOẠI", len(p.orders) == 0 and "md5" in b[0]["reason"])
p, b = run([("AAA", "LAG", "sell", 99999)]);             check("SELL LAG không bao giờ bị chặn", len(p.orders) == 1 and not b)
p, b = run([("AAA", "BAL", "buy", 99999)]);              check("book khác (BAL) không bị cổng này", len(p.orders) == 1 and not b)
p, b = run([("AAA", "lag", "buy", 99999)]);              check("book 'lag' thường vẫn là LAG (upper)", len(p.orders) == 0)
p, b = run([("AAA", "LAG_X", "buy", 99999)]);            check("khớp TUYỆT ĐỐI: 'LAG_X' không phải LAG", len(p.orders) == 1)
p, b = run([("AAA", "LAG", "buy", 9000), ("AAA", "LAG", "buy", 20000), ("BAL1", "BAL", "buy", 1)])
check("hỗn hợp: giữ lệnh đạt, loại lệnh không đạt, không đụng book khác", [o.ref_price for o in p.orders] == [9000, 1] and len(b) == 1)

def boom():
    raise OSError("sổ hỏng")
p, b = run([("AAA", "LAG", "buy", 1), ("AAA", "BAL", "buy", 1)], deps=boom)
check("sổ lỗi ⇒ FAIL-CLOSED: loại LAG buy, giữ book khác", len(p.orders) == 1 and p.orders[0].book == "BAL" and "fail-closed" in b[0]["reason"])
pm._lag_dd_zone_deps = fake_deps()
pl = mk([("AAA", "LAG", "buy", 11000)])
pl.orders[0].hard_no_chase_ceiling_vnd = 9500.0
p, b = pm.filter_lag_dd_zone_orders(pl);                check("giá = min(ref, trần) ⇒ trần 9500 ≤ tâm ⇒ GIỮ", len(p.orders) == 1)
pm.LAG_DD_ZONE_GATE_ENABLED = False
p, b = pm.filter_lag_dd_zone_orders(mk([("ZZZ", "LAG", "buy", 1)])); check("công tắc OFF ⇒ no-op", len(p.orders) == 1 and not b)
pm.LAG_DD_ZONE_GATE_ENABLED = True

print("== wiring (cấu trúc bot_execute) ==")
src = open(os.path.join(CODE_ROOT, "bot_execute.py"), encoding="utf-8").read()
i_dd, i_lz, i_net = (src.find("plan, dd_blocked = filter_dd_flag_orders(plan)"),
                     src.find("plan, lagzone_blocked = filter_lag_dd_zone_orders(plan)"),
                     src.find("plan, net_adj = net_offsetting_orders(plan)"))
check("cổng LAG-zone được gọi trong bot_execute", i_lz > 0)
check("thứ tự: dd_flag < lag_zone < netting", 0 < i_dd < i_lz < i_net, (i_dd, i_lz, i_net))

if "--live" in sys.argv:
    print("== live replay (sổ thật) ==")
    import importlib
    importlib.reload(pm)
    for acct in ("SpaceX", "ZaloPay"):
        f = os.path.join("/home/trido/thanhdt/WorkingClaude/data/trade_plans", f"plan_{acct}_2026-11-10.json")
        if not os.path.exists(f):
            print("  (bỏ qua, không có", f, ")")
            continue
        import json
        raw = json.load(open(f, encoding="utf-8"))
        orders = [PlannedOrder(**{k: v for k, v in o.items() if k in PlannedOrder.__dataclass_fields__})
                  for o in raw["orders"]]
        plan = TradePlan(plan_date="2026-11-10", signal_date="2026-11-09", strategy="x", strategy_version="x",
                         state=3, state_name="N", nav_basis={}, orders=orders, account=acct)
        nlag = sum(1 for o in orders if o.book.upper() == "LAG" and o.side == "buy")
        p, b = pm.filter_lag_dd_zone_orders(plan)
        for a in b:
            print("   ", acct, a["ticker"], a["price"], "tâm", a["center"], "|", a["reason"][:90])
        check(f"{acct}: mọi LAG buy plan 10/11 ({nlag}) đã đối chiếu sổ thật", nlag == len(b) + sum(
            1 for o in p.orders if o.book.upper() == "LAG"))

print(f"\n{PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
