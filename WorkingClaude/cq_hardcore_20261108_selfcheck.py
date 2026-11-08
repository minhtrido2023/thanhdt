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

# r2 #2: leg SELL có floor KHÔNG gộp chung leg SELL không floor
lag = PlannedOrder(id="L1", ticker="AAA", side="sell", qty=1000, ref_price=10000, book="LAG")
disc = PlannedOrder(id="D1", ticker="AAA", side="sell", qty=200, ref_price=10000,
                    book="DISCRETIONARY_SPECIAL", hard_sell_floor_vnd=12000)
bb = PlannedOrder(id="B9", ticker="AAA", side="buy", qty=100, ref_price=10000, book="CAPIT",
                  hard_no_chase_ceiling_vnd=10400, cash_only=True)
pl, _ = net_offsetting_orders(mk_plan([lag, disc, bb]))
nets = [o for o in pl.orders if o.id.startswith("NET-")]
check("LAG+DISC+BUY: NET SELL 900 (LAG - BUY) KHÔNG mang floor của DISC",
      len(nets) == 1 and nets[0].side == "sell" and nets[0].qty == 900
      and nets[0].hard_sell_floor_vnd is None, [(o.id, o.qty, o.hard_sell_floor_vnd) for o in pl.orders])
check("DISC SELL 200 floor 12000 đi qua nguyên vẹn",
      any(o is disc and o.qty == 200 and o.hard_sell_floor_vnd == 12000 for o in pl.orders))
check("NET SELL không nhận trần/cash_only của leg BUY ngược chiều",
      nets and nets[0].hard_no_chase_ceiling_vnd is None and nets[0].cash_only is False)
pl, adj = net_offsetting_orders(mk_plan([disc, bb]))
check("chỉ SELL có floor + BUY ⇒ không netting (giữ nguyên 2 lệnh)",
      [o.id for o in pl.orders] == ["D1", "B9"] and not adj, [o.id for o in pl.orders])

# r2 #1: giá trị thô chuỗi/rác không được raise
bs = PlannedOrder(id="BS", ticker="CCC", side="buy", qty=500, ref_price=10000, book="LAG",
                  hard_no_chase_ceiling_vnd="abc", cash_only="false")
sf = PlannedOrder(id="SF", ticker="CCC", side="sell", qty=100, ref_price=10000, book="BAL",
                  hard_sell_floor_vnd="9800")
sg = PlannedOrder(id="SG", ticker="CCC", side="sell", qty=100, ref_price=10000, book="BAL",
                  hard_sell_floor_vnd="abc")
try:
    pl, _ = net_offsetting_orders(mk_plan([bs, sf, sg]))
    exc = None
except Exception as e:                                         # noqa: BLE001
    pl, exc = None, e
check("ceiling='abc' + floor='9800' (chuỗi) KHÔNG raise", exc is None, repr(exc))
if pl:
    nets = [o for o in pl.orders if o.id.startswith("NET-")]
    check("floor='9800' (chuỗi hợp lệ) ⇒ leg có floor đi riêng; floor='abc' ⇒ coi như không floor, net",
          len(nets) == 1 and nets[0].side == "buy" and nets[0].qty == 400
          and any(o is sf for o in pl.orders), [(o.id, o.qty) for o in pl.orders])
    check("ceiling='abc' ⇒ không ceiling (None), cash_only='false' ⇒ False",
          nets and nets[0].hard_no_chase_ceiling_vnd is None and nets[0].cash_only is False)

# r2 #3: cash_only boolean chặt
sb = lambda i, v: PlannedOrder(id=i, ticker="DDD", side="buy", qty=100, ref_price=1, cash_only=v)  # noqa: E731
sd = PlannedOrder(id="SD", ticker="DDD", side="sell", qty=10, ref_price=1)
for v, want in (("false", False), ("0", False), ("no", False), ("junk", False),
                ("true", True), ("TRUE", True), ("yes", True), ("1", True), (1, True), (True, True)):
    pl, _ = net_offsetting_orders(mk_plan([sb("X", v), sd]))
    check(f"cash_only={v!r} ⇒ {want}", pl.orders[0].cash_only is want, pl.orders[0].cash_only)

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
sent = []
be.get_dnse_client = lambda *a, **k: sent.append(a)             # nếu chạm tới ⇒ đã đi qua khối OTP
for flag in ("--send-otp", "--auto-otp"):
    sys.argv = ["bot_execute.py", "--accept-gdkhq-shadow", "2026-11-06",
                "--accept-gdkhq-by", "auto", flag, "SpaceX"]
    rc = None
    try:
        be.main()
    except SystemExit as e:
        rc = e.code
    except Exception as e:                                     # noqa: BLE001
        rc = repr(e)
    check(f"{flag} + by=placeholder ⇒ exit 2 TRƯỚC khối OTP (không gửi OTP)",
          rc == 2 and not sent, (rc, sent))
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

os.makedirs(tdir, exist_ok=True)
pd.DataFrame({"time": pd.to_datetime(["2025-01-02"]).date, "ticker": ["OLD"],
              "Price": [3000.0], "Close": [3000.0]}).to_parquet(os.path.join(tdir, "2025.parquet"))
p, d = D.latest_price_session("OLD", "2025-12-31")
check("giá 363 ngày tuổi (≤400) ⇒ vẫn trả", (p, d) == (3000.0, "2025-01-02"), (p, d))
p, d = D.latest_price_session("OLD", "2026-03-01")
check("giá >400 ngày tuổi ⇒ (None, None)", (p, d) == (None, None), (p, d))

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
