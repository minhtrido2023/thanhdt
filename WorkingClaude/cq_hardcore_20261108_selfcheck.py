# -*- coding: utf-8 -*-
"""cq_hardcore_20261108_selfcheck.py — selfcheck cho 6 finding hard-boundary/tiền thật của
`mike/reports/code_quality/code_quality_2026-11-08.md` (job Taylor_20261108_045937).

  #1 net_offsetting_orders giữ hard_no_chase_ceiling_vnd/ceiling_*/hard_sell_floor_vnd/cash_only
  #2 approval_block_reason: approved_by placeholder (auto/pending/...) = CHƯA duyệt
  #3 bot_execute --accept-gdkhq-by: không default 'user', từ chối thiếu/placeholder
  #4 dcf_valuation.terminal_growth: cpi end = đầu tháng của asof (không hardcode 2026-12-01)
  #5 dcf_valuation.latest_price_session: đọc cả {yr-1} và {yr}
  #6 TradePlan.save created_at neo ICT (không phụ thuộc TZ host)

Chạy:  $DNA_PYEXE cq_hardcore_20261108_selfcheck.py
       env -u TZ ... / TZ=America/New_York ...   (phải cho kết quả như nhau, §16)
       CQ_CODE_ROOT=<dir>  — import code từ bản sao (mutation runner).
Offline, không chạm broker/BQ/bus, không ghi file ngoài tmpdir.
"""
import os
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")             # §5b — bot_execute import Executor

HERE = os.path.dirname(os.path.abspath(__file__))
CODE_ROOT = os.environ.get("CQ_CODE_ROOT") or HERE
sys.path.insert(0, CODE_ROOT)

import pandas as pd                                            # noqa: E402

from trading_bot import plan as plan_mod                       # noqa: E402
from trading_bot.plan import (PlannedOrder, TradePlan, approval_block_reason,  # noqa: E402
                              net_offsetting_orders)

PASS = FAIL = 0


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  PASS  {name}")
    else:
        FAIL += 1
        print(f"  FAIL  {name}  {detail}")


def mk_plan(orders, **kw):
    return TradePlan(plan_date="2026-11-09", signal_date="2026-11-06", strategy="selfcheck",
                     strategy_version="x", state=2, state_name="NEUTRAL", nav_basis={},
                     orders=orders, account="SELFCHECK", **kw)


print("=== #1 net_offsetting_orders giữ cổng cứng ===")
b = PlannedOrder(id="B1", ticker="TV1", side="buy", qty=1000, ref_price=20000,
                 book="DISCRETIONARY_SPECIAL", cash_only=True, hard_no_chase_ceiling_vnd=20800,
                 ceiling_rule="A", ceiling_anchor_price=20000, ceiling_anchor_date="2026-11-06",
                 ceiling_tau=0.04)
s = PlannedOrder(id="S1", ticker="TV1", side="sell", qty=300, ref_price=20000, book="BAL")
pl, adj = net_offsetting_orders(mk_plan([b, s]))
n = pl.orders[0] if len(pl.orders) == 1 else None
check("NET BUY 700 sinh ra", n is not None and n.side == "buy" and n.qty == 700,
      [(o.side, o.qty) for o in pl.orders])
check("NET BUY giữ hard_no_chase_ceiling_vnd", n and n.hard_no_chase_ceiling_vnd == 20800,
      n and n.hard_no_chase_ceiling_vnd)
check("NET BUY giữ provenance trần (rule/anchor/date/tau)",
      n and (n.ceiling_rule, n.ceiling_anchor_price, n.ceiling_anchor_date, n.ceiling_tau)
      == ("A", 20000, "2026-11-06", 0.04))
check("NET BUY giữ cash_only", n and n.cash_only is True)

b2 = PlannedOrder(id="B2", ticker="TV1", side="buy", qty=200, ref_price=20000, book="LAG",
                  hard_no_chase_ceiling_vnd=20500)
pl, _ = net_offsetting_orders(mk_plan([b, b2, s]))
n = pl.orders[0]
check("2 leg BUY ⇒ trần = min (chặt hơn)", n.hard_no_chase_ceiling_vnd == 20500,
      n.hard_no_chase_ceiling_vnd)
check("provenance đi theo leg cho trần đã chọn", n.ceiling_rule is None)

s1 = PlannedOrder(id="S1", ticker="AAA", side="sell", qty=1000, ref_price=10000, book="BAL",
                  hard_sell_floor_vnd=9500)
s2 = PlannedOrder(id="S2", ticker="AAA", side="sell", qty=500, ref_price=10000, book="LAG",
                  hard_sell_floor_vnd=9800)
bb = PlannedOrder(id="B9", ticker="AAA", side="buy", qty=200, ref_price=10000, book="CAPIT",
                  hard_no_chase_ceiling_vnd=10400, cash_only=True)
pl, _ = net_offsetting_orders(mk_plan([s1, s2, bb]))
n = pl.orders[0]
check("NET SELL 1300", n.side == "sell" and n.qty == 1300, (n.side, n.qty))
check("NET SELL sàn = max (chặt hơn)", n.hard_sell_floor_vnd == 9800, n.hard_sell_floor_vnd)
check("NET SELL KHÔNG nhận trần/cash_only của leg BUY ngược chiều",
      n.hard_no_chase_ceiling_vnd is None and n.cash_only is False)

print("=== #2 approval_block_reason: placeholder = chưa duyệt ===")
o = PlannedOrder(id="B1", ticker="FPT", side="buy", qty=100, ref_price=100000)
for who in ("auto", "pending", "Agent", " mike ", "DollarBill", "false", "None", ""):
    r = approval_block_reason(mk_plan([o], requires_user_approval=True, approved_by=who))
    check(f"approved_by={who!r} ⇒ bị chặn", r is not None)
for who in ("user", "user (John) - Discord 08/11 22:00 ICT"):
    r = approval_block_reason(mk_plan([o], requires_user_approval=True, approved_by=who))
    check(f"approved_by={who!r} ⇒ qua", r is None, r)
check("requires_user_approval=false + auto ⇒ qua (không đổi hành vi cũ)",
      approval_block_reason(mk_plan([o], requires_user_approval=False, approved_by="auto")) is None)

print("=== #3 --accept-gdkhq-by ===")
import bot_execute as be                                       # noqa: E402

called = []
be.accept_gdkhq_shadow = lambda *a, **k: called.append(a) or {}   # chặn mọi ghi state thật
check("thiếu --accept-gdkhq-by ⇒ lỗi", be.gdkhq_accepted_by_error(None) is not None)
for who in ("", "  ", "auto", "agent", "Mike", "taylor", "pending"):
    check(f"by={who!r} ⇒ lỗi", be.gdkhq_accepted_by_error(who) is not None)
check("by='user' tường minh ⇒ hợp lệ", be.gdkhq_accepted_by_error("user") is None)
check("by='John Dinh' ⇒ hợp lệ", be.gdkhq_accepted_by_error("John Dinh") is None)
old_argv = sys.argv
for extra in ([], ["--accept-gdkhq-by", "auto"]):
    sys.argv = ["bot_execute.py", "--accept-gdkhq-shadow", "2026-11-06"] + extra
    rc = None
    try:
        be.main()
    except SystemExit as e:
        rc = e.code
    check(f"main() {extra or '(không by)'} ⇒ exit 2, KHÔNG ghi nghiệm thu",
          rc == 2 and not called, (rc, called))
sys.argv = old_argv

print("=== #4 terminal_growth: cpi end theo asof ===")
import dcf_valuation as D                                      # noqa: E402

ends = []
real = D._cpi.cpi_monthly_df


def spy(end="2026-06-01"):
    ends.append(end)
    return real(end=end)


D._cpi.cpi_monthly_df = spy
D._CPI_DF = None
D._TG_CACHE.clear()
D.terminal_growth("2027-04-15")
check("asof 2027-04-15 ⇒ end=2027-04-01", ends == ["2027-04-01"], ends)
cpi = D._CPI_DF.get("2027-04-01")
a = pd.Timestamp("2027-04-15")
w = cpi[(cpi.time <= a) & (cpi.time > a - pd.Timedelta(days=365 * D.CPI_TERMINAL_YEARS))]
check("cửa sổ 5y chứa 2027-01..04", pd.Timestamp("2027-04-01") in set(w.time)
      and pd.Timestamp("2027-01-01") in set(w.time))
v_new = D.terminal_growth("2026-08-20")
D._TG_CACHE.clear()
D._CPI_DF = {"2026-08-01": real(end="2026-12-01")}             # ép df của đường cũ (hardcode)
v_old = D.terminal_growth("2026-08-20")
check("asof ≤ 2026-12: giá trị KHÔNG đổi so với end cũ", abs(v_new - v_old) < 1e-12, (v_new, v_old))
D._cpi.cpi_monthly_df = real

print("=== #5 latest_price_session đọc cả năm trước ===")
tmp = tempfile.mkdtemp(prefix="cq_hc_")
tdir = os.path.join(tmp, "data", "bq_cache", "ticker")
os.makedirs(tdir)
pd.DataFrame({"time": pd.to_datetime(["2026-12-30", "2026-12-31"]).date, "ticker": ["XYZ", "XYZ"],
              "Price": [10000.0, 10100.0], "Close": [10000.0, 10100.0]}
             ).to_parquet(os.path.join(tdir, "2026.parquet"))
pd.DataFrame({"time": pd.to_datetime(["2027-01-05"]).date, "ticker": ["OTH"],
              "Price": [5000.0], "Close": [5000.0]}).to_parquet(os.path.join(tdir, "2027.parquet"))
D.WORKDIR = tmp
p, d = D.latest_price_session("XYZ", "2027-01-02")
check("asof 2027-01-02, file 2027 không có XYZ ⇒ lấy giá 31/12/2026", (p, d) == (10100.0, "2026-12-31"),
      (p, d))
p, d = D.latest_price_session("OTH", "2027-01-06")
check("năm hiện tại vẫn đọc đúng", (p, d) == (5000.0, "2027-01-05"), (p, d))
os.remove(os.path.join(tdir, "2026.parquet"))
p, d = D.latest_price_session("OTH", "2027-01-06")
check("thiếu file năm trước ⇒ fallback chỉ {yr}", (p, d) == (5000.0, "2027-01-05"), (p, d))

print("=== #6 TradePlan.save created_at neo ICT ===")
plan_mod.PLAN_DIR = tmp
os.environ["TZ"] = "America/New_York"
import time as _t                                              # noqa: E402
_t.tzset()
pth = mk_plan([o]).save()
import json                                                    # noqa: E402
ca = json.load(open(pth))["created_at"]
check("created_at có offset +07:00 dù TZ host = New York", ca.endswith("+07:00"), ca)

print(f"\n{PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
