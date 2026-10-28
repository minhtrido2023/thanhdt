#!/usr/bin/env python3
"""Selfcheck `egg_transfer_alert.py` — chạy THẬT `check_plan_funding` trên broker stub (không mạng).

Bất biến chính: số tiền cảnh báo "cần chuyển" X thoả — sau khi cộng X vào hũ tiền mặt, gate KHÔNG còn
BLOCK; và trừ đi 1 bước làm tròn (0,1tr) thì vẫn BLOCK. Tức cảnh báo biến mất ĐÚNG khi user chuyển đủ.
Chạy: python3 bin/egg_transfer_alert_selfcheck.py   (độc lập TZ; thử `env -u TZ` và `TZ=America/New_York`)
"""
import os
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402

sys.path.insert(0, wc_paths.find_wc_root(__file__))
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")

import egg_transfer_alert as E                                      # noqa: E402
from trading_bot.plan_funding_gate import check_plan_funding       # noqa: E402

PASS = FAIL = 0


def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name} — {detail}")


def order(t, qty, px, side="buy", priority=5):
    o = types.SimpleNamespace(ticker=t, qty=qty, ref_price=px, side=side, id=f"{side}-{t}",
                              cash_only=True, loan_package_id=None, priority=priority)
    return o


class Broker:
    """Cash-only: pp0Buy = hũ tiền mặt (cash). Chuyển egg → cash ⇒ cộng thẳng vào hũ."""
    def __init__(self, pot):
        self.pot = pot
        self.client = types.SimpleNamespace(loan_package_id=None)
        self._resolve_loan_package_id = lambda t, *a, **k: 1841

    def get_buying_power(self, symbol, price, loan_package_id=None):
        return float(self.pot)

    def get_cash(self):
        return float(self.pot)


def fund(orders, pot):
    p = types.SimpleNamespace(orders=orders, account="SpaceX", plan_date="2026-10-26")
    return check_plan_funding(p, Broker(pot), "live")


print("A. thiếu tiền, egg đủ bù")
orders = [order("AAA", 10_000, 20_000)]                       # mua 200tr (+phí)
f = fund(orders, 50_000_000)
d = E.decide(f, 300_000_000)
ck("BLOCK → SHORT_EGG_COVERS", f["action"] == "BLOCK" and d["status"] == "SHORT_EGG_COVERS", (f["action"], d))
ck("X làm gate hết BLOCK", fund(orders, 50_000_000 + d["short"])["action"] == "OK", d)
ck("X − 0,1tr vẫn BLOCK (không báo thừa quá 1 bước làm tròn)",
   fund(orders, 50_000_000 + d["short"] - E.ROUND_UP_VND)["action"] == "BLOCK", d)
msg = E.render("SpaceX", "2026-10-26", "08:30", d, f, 300_000_000)
ck("tin nhắn nêu số tiền + hạn 09:05", "CHUYỂN" in msg and "09:05" in msg and f"{d['short']/1e6:,.1f}tr" in msg, msg)

print("B. egg không đủ bù → báo ĐỎ, nêu phần thiếu thêm")
d2 = E.decide(f, 40_000_000)
ck("SHORT_EGG_INSUFFICIENT", d2["status"] == "SHORT_EGG_INSUFFICIENT", d2)
ck("tin nhắn nêu 'THIẾU CẢ KHI CHUYỂN HẾT'", "THIẾU CẢ KHI CHUYỂN HẾT" in E.render("SpaceX", "x", "08:30", d2, f, 40_000_000))

print("C. đủ tiền → im lặng")
f3 = fund(orders, 500_000_000)
ck("OK → FUNDED, short=0", E.decide(f3, 300_000_000) == {"status": "FUNDED", "short": 0.0}, f3["action"])
ck("biên: sức mua đúng bằng Σ mua → FUNDED", E.decide(fund(orders, f["need_vnd"]), 0)["status"] == "FUNDED")

print("D. JIT-sell cùng plan trừ vào phần cần chuyển")
orders_j = orders + [order("BBB", 5_000, 20_000, side="sell", priority=1)]
fj = fund(orders_j, 50_000_000)
dj = E.decide(fj, 300_000_000)
ck("có JIT ⇒ cần chuyển ÍT hơn không JIT", dj["short"] < d["short"], (dj, d))
ck("X(JIT) làm gate hết BLOCK", fund(orders_j, 50_000_000 + dj["short"])["action"] == "OK", dj)

print("E. không áp dụng / không đo được → KHÔNG báo")
ck("plan chỉ có lệnh bán → NOT_APPLICABLE",
   E.decide(fund([order("CCC", 100, 10_000, side="sell")], 0), 1e9)["status"] == "NOT_APPLICABLE")
ck("UNVERIFIED → không báo (bot cũng không chặn)", E.decide({"action": "UNVERIFIED"}, 1e9)["status"] == "UNVERIFIED")


print("F. BẤT BIẾN: gate BLOCK ⇒ KHÔNG BAO GIỜ FUNDED (arch-review: nhánh cận ngoài khi có nhóm đo được)")


class MultiBroker:
    """2 nhóm gói vay theo mã; bp theo gói. Gói None = KHÔNG đo được."""
    def __init__(self, bp, resolve, cash=0.0):
        self.bp, self.resolve, self.cash = bp, resolve, cash
        self.client = types.SimpleNamespace(loan_package_id=None)
        self._resolve_loan_package_id = lambda t, *a, **k: self.resolve[t]

    def get_buying_power(self, symbol, price, loan_package_id=None):
        v = self.bp.get(loan_package_id)
        if v is None:
            raise RuntimeError("không đo được")
        return float(v)

    def get_cash(self):
        return float(self.cash)


def fund2(orders, broker):
    p = types.SimpleNamespace(orders=orders, account="SpaceX", plan_date="2026-10-26")
    return check_plan_funding(p, broker, "live")


mixed = [order("AAA", 500, 20_000), order("BBB", 25_000, 20_000)]      # 10tr (đo được, ≤ pp0) + 500tr (không đo được)
fm = fund2(mixed, MultiBroker({1: 20_000_000, 2: None}, {"AAA": 1, "BBB": 2}, cash=50_000_000))
dm = E.decide(fm, 2e9)
ck("nhóm đo được + nhóm không đo được, vượt cận ngoài ⇒ BLOCK", fm["action"] == "BLOCK" and fm.get("fallback_bound_vnd") is not None, fm["action"])
ck("…và decide() KHÔNG ra FUNDED (ca killer của arch-review)", dm["status"] != "FUNDED" and dm["short"] > 0, dm)
ck("…short ≥ Σ mua − cận ngoài (không đòi thiếu)", dm["short"] >= fm["need_vnd"] - fm["fallback_bound_vnd"], (dm, fm["need_vnd"], fm["fallback_bound_vnd"]))
ck("…chuyển X ⇒ nhóm đo được tăng, gate hết BLOCK (hũ nhóm 1 + X, nhóm 2 đo được từ giờ)",
   fund2(mixed, MultiBroker({1: 20_000_000 + dm["short"], 2: 50_000_000 + dm["short"]}, {"AAA": 1, "BBB": 2}, cash=50_000_000 + dm["short"]))["action"] == "OK", dm)
ck("action lạ ⇒ không đoán là đủ", E.decide({"action": "???"}, 1e9)["status"] == "UNVERIFIED")

two = [order("AAA", 10_000, 20_000), order("BBB", 10_000, 20_000)]         # 400tr, nhóm 1 (λ=1) + nhóm 2 (pp0=2×)
for pot in (50_000_000, 150_000_000, 300_000_000):
    fo = fund2(two, MultiBroker({1: pot, 2: 2 * pot}, {"AAA": 1, "BBB": 2}))
    if fo["action"] != "BLOCK":
        continue
    dd = E.decide(fo, 1e10)
    ck(f"nhiều nhóm pot={pot/1e6:.0f}tr: chuyển X (tỉ lệ) ⇒ gate hết BLOCK",
       fund2(two, MultiBroker({1: pot + dd["short"], 2: 2 * (pot + dd["short"])}, {"AAA": 1, "BBB": 2}))["action"] == "OK", dd)
    ck(f"nhiều nhóm pot={pot/1e6:.0f}tr: chuyển X (cộng thêm cố định) ⇒ gate hết BLOCK",
       fund2(two, MultiBroker({1: pot + dd["short"], 2: 2 * pot + dd["short"]}, {"AAA": 1, "BBB": 2}))["action"] == "OK", dd)

print("F2. cash 0 + lệnh BÁN cùng plan (fallback_bound = (cash+bán)×3 không được làm đòi thiếu)")
sell_plan = [order("SSS", 1_000, 10_000, side="sell", priority=1), order("AAA", 2_500, 20_000)]   # bán 10tr, mua 50tr
fs = fund2(sell_plan, MultiBroker({1: None}, {"AAA": 1}, cash=0))
ds = E.decide(fs, 1e10)
ck("cash 0 + bán ⇒ BLOCK và X làm gate hết BLOCK", fs["action"] == "BLOCK"
   and fund2(sell_plan, MultiBroker({1: ds["short"]}, {"AAA": 1}, cash=ds["short"]))["action"] != "BLOCK", (fs["action"], ds))

print("G. egg không đọc được ⇒ không báo ĐỎ giả")
dn = E.decide(f, None)
ck("egg=None ⇒ SHORT_EGG_UNKNOWN (không phải INSUFFICIENT)", dn["status"] == "SHORT_EGG_UNKNOWN", dn)
ck("tin nhắn nói rõ không đọc được", "KHÔNG đọc được" in E.render("SpaceX", "x", "08:30", dn, f, None))
ck("tin nhắn có số lệnh BÁN bị kéo theo + cờ chưa duyệt",
   "3 lệnh BÁN" in E.render("SpaceX", "x", "08:30", d, f, 3e8, n_sell=3, approved=False)
   and "CHƯA duyệt" in E.render("SpaceX", "x", "08:30", d, f, 3e8, n_sell=3, approved=False))

print("H. run() end-to-end với stub (plan chưa duyệt / lever / exec-state lệch / notify rc)")
import tempfile, json                                            # noqa: E402

import trading_bot.brokers as TB, trading_bot.config as TC, trading_bot.plan as TP, trading_bot.vn_market as TV  # noqa: E402


def run_case(orders, pot, egg_val, approved=True, exec_state=None, notify_ok=True, loan_pkg_broker=None, hm=(8, 30)):
    tmp = tempfile.mkdtemp()
    os.makedirs(os.path.join(tmp, "data", "execution_logs"))
    if exec_state is not None:
        json.dump(exec_state, open(os.path.join(tmp, "data", "execution_logs", "exec_SpaceX_2026-10-26_state.json"), "w"))
    sent = []
    plan = types.SimpleNamespace(orders=orders, account="SpaceX", plan_date="2026-10-26",
                                 requires_user_approval=True, approved_by=("user" if approved else None))
    bal = {"egg": {"totalValue": egg_val}} if egg_val is not None else {}
    br = loan_pkg_broker or Broker(pot)
    br.account_id = "x"
    br.client = types.SimpleNamespace(loan_package_id=None, balances=lambda a: bal)
    br.connect = lambda: br
    saved = (TB.make_broker, TC.load_config, TC.load_accounts, TP.load_plan, TP.filter_excluded_tickers, TV.now_ict,
             E._notify, E.WC_ROOT)
    import datetime as dt
    TB.make_broker = lambda *a, **k: br
    TC.load_config = lambda *a, **k: {}
    TC.load_accounts = lambda cfg: [{"label": "SpaceX", "cfg": {"mode": "live"}, "excluded_tickers": None}]
    TP.load_plan = lambda d, account=None: plan
    TP.filter_excluded_tickers = lambda p, ex: (p, [])
    TV.now_ict = lambda: dt.datetime(2026, 10, 26, hm[0], hm[1], tzinfo=dt.timezone(dt.timedelta(hours=7)))
    E._notify = lambda m: (sent.append(m), notify_ok)[1]
    E.WC_ROOT = tmp
    try:
        rc = E.run("SpaceX", "2026-10-26", False)
    finally:
        (TB.make_broker, TC.load_config, TC.load_accounts, TP.load_plan, TP.filter_excluded_tickers, TV.now_ict,
         E._notify, E.WC_ROOT) = saved
    st = E._read_state(os.path.join(tmp, "data", "execution_logs", "egg_alert_state_SpaceX_2026-10-26.json")) \
        if False else json.load(open(os.path.join(tmp, "data", "execution_logs", "egg_alert_state_SpaceX_2026-10-26.json"))) \
        if os.path.exists(os.path.join(tmp, "data", "execution_logs", "egg_alert_state_SpaceX_2026-10-26.json")) else {}
    return rc, sent, st


buy = lambda: [order("AAA", 10_000, 20_000)]                                 # noqa: E731
rc, sent, st = run_case(buy() + [order("ZZZ", 100, 10_000, side="sell")], 50_000_000, 300_000_000, approved=False)
ck("plan CHƯA duyệt VẪN nhắc, có tiền tố + đếm lệnh bán", len(sent) == 1 and "CHƯA duyệt" in sent[0] and "1 lệnh BÁN" in sent[0], sent)
ck("state ghi alerted khi gửi thành công", st.get("alerted") is True, st)

rc, sent, st = run_case(buy(), 50_000_000, 300_000_000, notify_ok=False)
ck("notify rc≠0 ⇒ KHÔNG latch alerted (lần sau còn nhắc lại)", st.get("alerted") is None, st)

rc, sent, st = run_case(buy(), 50_000_000, None)
ck("thiếu field egg ⇒ báo 'không đọc được', không ĐỎ giả", len(sent) == 1 and "KHÔNG đọc được" in sent[0], sent)

lev = buy(); lev[0].loan_package_id = 1840
bm = MultiBroker({1840: 400_000_000, None: 50_000_000}, {"AAA": None})
bm._validate_lever_package = lambda t, lp: (lp, True, "ok")                  # nếu KHÔNG gỡ cờ: đo bằng gói 1840 ⇒ "đủ" (sai)
rc, sent, st = run_case(lev, 0, 300_000_000, loan_pkg_broker=bm)
ck("plan mang loan_package_id đòn bẩy bị gỡ như bot ⇒ vẫn nhắc (không báo đủ nhờ gói không có thật)", len(sent) == 1, sent)

mism = {"plan_date": "2026-10-26", "parents": {"NET-AAA-BUY": {"filled": 0}}}   # cascade đổi id ⇒ state không khớp
rc, sent, st = run_case(buy(), 50_000_000, 300_000_000, exec_state=mism)
ck("exec state lệch id ⇒ KHÔNG gửi số tiền sai, chỉ 1 thông báo", len(sent) == 1 and "không đối chiếu" in sent[0], sent)
ck("…và state ghi state_mismatch_notified", st.get("state_mismatch_notified") is True, st)

print(f"\n{PASS} PASS / {FAIL} FAIL")
sys.exit(1 if FAIL else 0)
