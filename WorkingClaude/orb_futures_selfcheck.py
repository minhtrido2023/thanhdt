# -*- coding: utf-8 -*-
"""Selfcheck trading_bot/orb_futures.py — FakeClient, KHÔNG chạm DNSE thật, KHÔNG ghi bus thật.

Chạy:  python3 orb_futures_selfcheck.py
       env -u TZ python3 orb_futures_selfcheck.py ; TZ=America/New_York python3 orb_futures_selfcheck.py
"""
import os
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b — TRƯỚC mọi import bot
import atexit
import datetime as dt
import json
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot import orb_futures as OF                  # noqa: E402

ICT = OF.ICT
DAY = dt.date(2026, 11, 17)
CT = "41I1GB000"
FAILS = []
ROOT = tempfile.mkdtemp(prefix="orbfut_")                  # N-e: MỌI thư mục test nằm dưới đây, dọn khi thoát
atexit.register(shutil.rmtree, ROOT, True)


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class Clock:
    def __init__(self, hh, mm, ss=0):
        self.t = dt.datetime(DAY.year, DAY.month, DAY.day, hh, mm, ss, tzinfo=ICT)

    hook = None                                            # gọi sau mỗi sleep (vd bật BOT_STOP giữa chừng)

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += dt.timedelta(seconds=s)
        if self.hook:
            self.hook(self.t)


class Fake:
    """Broker giả: OR theo `or_move`, giá sau 09:30 theo hàm `path(t)`; lệnh LO khớp ngay ở giá hiện tại
    nếu marketable (trừ khi `no_fill`)."""

    def __init__(self, clock, or_move=+5.0, path=None, no_fill=False, positions=None, orders=None,
                 qmax=5, fx_dev=0.0, feed_lag_s=0, exit_no_fill=False, cancel_status="Cancelled",
                 pc_fill_after=None, no_avg=False, exit_fill_hidden=False, drop_keys=(),
                 exit_nofill_n=None, entry_fill_hidden=False):
        self.clock, self.or_move, self.no_fill, self.qmax, self.fx_dev = clock, or_move, no_fill, qmax, fx_dev
        self.exit_no_fill, self.cancel_status, self.pc_fill_after = exit_no_fill, cancel_status, pc_fill_after
        self.no_avg, self.exit_fill_hidden, self.drop_keys = no_avg, exit_fill_hidden, set(drop_keys)
        self.exit_nofill_n, self.entry_fill_hidden = exit_nofill_n, entry_fill_hidden   # n lệnh đóng đầu không khớp
        self.fail_lt = 0                                   # số lần latest_trade sắp tới sẽ ném lỗi (lỗi thoáng qua)
        self.pc_reads = {}
        self.feed_lag = dt.timedelta(seconds=feed_lag_s)
        self.path = path or (lambda t: 1850.0 + or_move)
        self.pos = list(positions or [])
        self.book = list(orders or [])
        self.placed, self.cancelled, self.det = [], [], {}

    # market data
    def ohlc(self, sym, resolution, bar_type, **q):
        assert sym == "VN30F1M" and bar_type == "derivative"
        t, o, h, l, c = [], [], [], [], []
        start = dt.datetime.combine(DAY, dt.time(9, 0), ICT)
        now = self.clock() - self.feed_lag
        for i in range(0, 31):
            b = start + dt.timedelta(minutes=i)
            if b + dt.timedelta(minutes=1) > now:
                break
            px = 1850.0 + self.or_move * i / 30
            t.append(int(b.timestamp())); o.append(px); h.append(px); l.append(px); c.append(px)
        return {"t": t, "o": o, "h": h, "l": l, "c": c, "v": [1] * len(t)}

    def instruments(self, **q):
        return {"data": [{"symbol": CT, "marketId": "DVX", "securityGroupId": "FU", "symbolType": "VN30F1M"}]}

    def secdef(self, s, board_id=None):
        return [{"boardId": "G1", "symbol": s, "basicPrice": 1850, "ceilingPrice": 1979.5,
                 "floorPrice": 1720.5, "symbolTradingSanctionStatusCode": "NRM"}]

    def latest_trade(self, s, board_id=None):
        if self.fail_lt > 0:
            self.fail_lt -= 1
            raise ConnectionError("lỗi mạng giả")
        return {"trades": [{"boardId": "G1", "matchPrice": self.path(self.clock()) * (1 + self.fx_dev)}]}

    def loan_packages(self, acc, market_type="STOCK", symbol=None):
        return {"loanPackages": [{"id": 1306, "initialRate": 0.1848, "maintenanceRate": 0.1771,
                                  "tradingFee": {"progressTradingFee": [{"fee": 1000.0, "fromQuantity": 1,
                                                                         "toQuantity": 99}]}}]}

    def ppse(self, acc, sym, price, market_type="STOCK", loan_package_id=None):
        return {"qmaxBuy": self.qmax, "qmaxSell": self.qmax}

    def balances(self, acc):
        return {"derivative": {"remainSecure": 0, "usedSecure": 0, "pendingSecure": 0},
                "egg": {"totalValue": 752_313_273}}

    # account
    def positions(self, acc, market_type="STOCK"):
        assert market_type == "DERIVATIVE"
        return {} if "positions" in self.drop_keys else {"positions": list(self.pos)}

    def orders(self, acc, market_type="STOCK", order_category=None):
        return {} if "orders" in self.drop_keys else {"orders": list(self.book)}

    def _apply(self, sym, side):
        net = sum((1 if p["side"] == "NB" else -1) * p["openQuantity"] for p in self.pos)
        net += 1 if side == "buy" else -1
        self.pos = [] if net == 0 else [{"symbol": sym, "openQuantity": abs(net), "side": "NB" if net > 0 else "NS"}]

    def place_order(self, acc, sym, qty, side, order_type="LO", price=None, market_type="STOCK",
                    loan_package_id=None, order_category="NORMAL"):
        assert market_type == "DERIVATIVE" and qty == 1 and order_type == "LO" and loan_package_id == 1306
        oid = str(1000 + len(self.placed))
        self.placed.append({"oid": oid, "side": side, "price": price, "t": self.clock()})
        self.book.append({"id": oid, "symbol": sym})
        px = self.path(self.clock())
        marketable = (side == "buy" and price >= px) or (side == "sell" and price <= px)
        is_exit = len(self.placed) > 1
        self.meta = getattr(self, "meta", {}); self.meta[oid] = (sym, side, px)
        exit_nofill = is_exit and (self.exit_no_fill or (self.exit_nofill_n is not None
                                                          and len(self.placed) - 2 < self.exit_nofill_n))
        if (is_exit and self.exit_fill_hidden) or (not is_exit and self.entry_fill_hidden):
            self._apply(sym, side); self.det[oid] = (0, None, "New")   # broker ĐÃ khớp, order_detail báo cũ
        elif marketable and not self.no_fill and not exit_nofill:
            self.det[oid] = (1, px, "Filled"); self._apply(sym, side)
        else:
            self.det[oid] = (0, None, "New")
        return {"id": oid}

    def order_detail(self, acc, oid, market_type="STOCK"):
        q, px, st = self.det[oid]
        if st == "PendingCancel" and self.pc_fill_after is not None:
            self.pc_reads[oid] = self.pc_reads.get(oid, 0) + 1
            if self.pc_reads[oid] >= self.pc_fill_after:  # lệnh "đang huỷ" hoá ra KHỚP
                sym, side, px0 = self.meta[oid]
                self.det[oid] = (1, px0, "Filled"); self._apply(sym, side)
                q, px, st = self.det[oid]
        d = {"id": oid, "fillQuantity": q, "orderStatus": st}
        if not self.no_avg:
            d["averagePrice"] = px
        return d

    def cancel_order(self, acc, oid, market_type="STOCK", order_category="NORMAL"):
        self.cancelled.append(oid)
        q, px, st = self.det[oid]
        self.det[oid] = (q, px, self.cancel_status if q == 0 else st)
        return {}


def mk(fake, clock, live=True, d=None):
    d = d or tempfile.mkdtemp(dir=ROOT)
    ev = []
    bot = OF.OrbFutures(fake, "SpaceX", "0002023347", live, clock=clock, sleep=clock.sleep,
                        notify=lambda m, red=False: ev.append(("N", m, red)),
                        publish=lambda a, b, c: ev.append(("B", a, b)), data_dir=d)
    return bot, ev, d


def journal(d, live=True):
    p = os.path.join(d, "orb_futures", f"journal_SpaceX{'' if live else '_dry'}.csv")
    return open(p).read() if os.path.exists(p) else ""


print("1. LONG, giữ tới 14:29, thoát TIME")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0)
bot, ev, d = mk(f, ck)
r = bot.run()
check(r == "CLOSED", f"kết thúc CLOSED (={r})")
check(len(f.placed) == 2 and f.placed[0]["side"] == "buy" and f.placed[1]["side"] == "sell", "đúng 2 lệnh buy→sell")
check(f.placed[1]["t"].time() >= OF.EXIT_AT, f"lệnh thoát ≥14:29 ({f.placed[1]['t'].time()})")
check(f.placed[1]["price"] == 1720.5, "lệnh đóng long = LO giá sàn")
check(bot.state["exit_reason"] == "TIME" and f.pos == [], "reason TIME, broker phẳng")
check(journal(d).count(",FILL,") == 2, "journal 2 dòng FILL")
check(abs(f.placed[0]["price"] - OF.round_tick(1855 * 1.003)) < 1e-9, "lệnh vào LO trần +0,3%")

print("2. SHORT chạm stop 2,5%")
ck = Clock(9, 31, 5)
f = Fake(ck, or_move=-5.0, path=lambda t: 1845.0 if t.time() < dt.time(10, 30) else 1900.0)
bot, ev, d = mk(f, ck)
r = bot.run()
check(r == "CLOSED" and bot.state["exit_reason"] == "STOP", f"thoát STOP ({bot.state.get('exit_reason')})")
check(bot.state["stop_px"] == OF.round_tick(1845 * 1.025), f"stop = entry×1,025 ({bot.state['stop_px']})")
check(f.placed[1]["side"] == "buy" and f.placed[1]["price"] == 1979.5, "đóng short = LO giá trần")
check(dt.time(10, 30) <= f.placed[1]["t"].time() < dt.time(10, 31), "stop kích hoạt ngay phút chạm")
check(any(e[0] == "B" and e[1] == "finding" for e in ev), "STOP ⇒ bus finding")

print("3. OR = 0 ⇒ không lệnh")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=0.0)
bot, ev, d = mk(f, ck)
check(bot.run() == "FLAT" and not f.placed, "FLAT, 0 lệnh")

print("4. Cờ TẮT ⇒ DRY: chạy đủ, KHÔNG gọi place_order")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0)
bot, ev, d = mk(f, ck, live=False)
r = bot.run()
check(r == "CLOSED" and not f.placed and not f.cancelled, f"DRY CLOSED, broker 0 lệnh ({r})")
check(",DRY_PLACE_ENTRY," in journal(d, live=False) and ",DRY," in journal(d, live=False), "journal DRY ghi lệnh dự kiến")
check(os.path.exists(os.path.join(d, "orb_futures", f"state_SpaceX_{DAY}_dry.json")), "state DRY tách file")

print("5. Vị thế lạ trên broker lúc khởi động ⇒ PAUSED, 0 lệnh")
ck = Clock(9, 31, 5); f = Fake(ck, positions=[{"symbol": CT, "openQuantity": 1, "side": "NB"}])
bot, ev, d = mk(f, ck)
check(bot.run() == "PAUSED" and not f.placed, "PAUSED, 0 lệnh")

print("6. Lệnh lạ trong sổ ⇒ PAUSED")
ck = Clock(9, 31, 5); f = Fake(ck, orders=[{"id": "777"}])
bot, ev, d = mk(f, ck)
check(bot.run() == "PAUSED" and not f.placed, "PAUSED, 0 lệnh")

print("7. Crash sau intent, trước oid (ENTRY_PENDING) ⇒ restart PAUSE, KHÔNG đặt lại")
ck = Clock(9, 32, 0); f = Fake(ck)
bot, ev, d = mk(f, ck)
bot.stage("ENTRY_PENDING", sig=1)
bot2, ev2, _ = mk(f, ck, d=d)
check(bot2.run() == "PAUSED" and not f.placed, "PAUSED, 0 lệnh")

print("8. Crash sau khi đặt (ENTRY_PLACED có oid) ⇒ restart chờ khớp oid cũ, không đặt lệnh vào mới")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0)
oid = f.place_order("x", CT, 1, "buy", price=1900.0, market_type="DERIVATIVE", loan_package_id=1306)["id"]
bot, ev, d = mk(f, ck)
bot.state.update(sig=1, contract=CT, ceiling=1979.5, floor=1720.5, loan_package_id=1306,
                 signal={"or_ret": 0.0027}, known_oids=[oid], entry_oid=oid)
bot.stage("ENTRY_PLACED")
bot2, _, _ = mk(f, ck, d=d)
r = bot2.run()
check(r == "CLOSED" and len(f.placed) == 2 and f.placed[1]["side"] == "sell", f"resume → CLOSED, chỉ thêm 1 lệnh thoát ({len(f.placed)})")

print("9. Crash khi OPEN ⇒ resume giám sát, không vào lại")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0)
bot, ev, d = mk(f, ck); bot.run(once=True)
check(bot.state["stage"] == "OPEN" and len(f.placed) == 1, "OPEN sau 1 chu kỳ")
ck.t = ck.t.replace(hour=13, minute=10)
bot2, _, _ = mk(f, ck, d=d)
check(bot2.run() == "CLOSED" and len(f.placed) == 2, "resume → CLOSED, tổng 2 lệnh")

print("10. Lỡ cửa sổ (khởi động 09:45) ⇒ SKIPPED")
ck = Clock(9, 45); f = Fake(ck)
bot, ev, d = mk(f, ck)
check(bot.run() == "SKIPPED" and not f.placed, "SKIPPED, 0 lệnh")

print("11. Giá HĐ lệch VN30F1M >0,5% ⇒ PAUSED (nghi roll)")
ck = Clock(9, 31, 5); f = Fake(ck, fx_dev=0.01)
bot, ev, d = mk(f, ck)
check(bot.run() == "PAUSED" and not f.placed, "PAUSED, 0 lệnh")

print("12. Thiếu ký quỹ (ppse qmax=0) ⇒ SKIPPED + cảnh báo funding")
ck = Clock(9, 31, 5); f = Fake(ck, qmax=0)
bot, ev, d = mk(f, ck)
check(bot.run() == "SKIPPED" and not f.placed, "SKIPPED, 0 lệnh")
check(any(e[0] == "B" and e[2] == "orb_futures_funding" for e in ev), "bus orb_futures_funding")

print("13. Lệnh vào không khớp 60s ⇒ huỷ, SKIPPED")
ck = Clock(9, 31, 5); f = Fake(ck, no_fill=True)
bot, ev, d = mk(f, ck)
check(bot.run() == "SKIPPED" and f.cancelled == [f.placed[0]["oid"]], "huỷ đúng lệnh, SKIPPED")

print("14. BOT_STOP ⇒ 0 lệnh")
ck = Clock(9, 31, 5); f = Fake(ck)
bot, ev, d = mk(f, ck)
open(os.path.join(d, "BOT_STOP"), "w").close()
check(bot.run() == "SKIPPED" and not f.placed, "SKIPPED, 0 lệnh")

print("15. Khoá flock: tiến trình 2 thoát LOCKED")
import fcntl                                               # noqa: E402
ck = Clock(9, 31, 5); f = Fake(ck)
bot, ev, d = mk(f, ck)
with open(bot.lock_file, "a+") as lf:
    fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
    check(bot.run() == "LOCKED" and not f.placed, "LOCKED, 0 lệnh")

print("16. Bar 09:30 chưa có lúc 09:31:05 ⇒ chờ (strict), không dùng bar 09:29")
sig, info = OF.compute_signal([(f"09:{m:02d}", 0, 0, 0, 1850 + m) for m in range(0, 30)], strict=True)
check(sig is None and "09:30" in info, f"strict chặn ({info})")
sig, info = OF.compute_signal([(f"09:{m:02d}", 0, 0, 0, 1850 + m) for m in range(0, 30)], strict=False)
check(sig == 1, "sau 09:33 nới về bar cuối ≤09:30")

print("17. Epoch ↔ giờ ICT không phụ thuộc TZ process (§16)")
ck = Clock(9, 31, 5); f = Fake(ck)
b = OF.bars_today(f, DAY)
check(b[0][0] == "09:00" and b[-1][0] == "09:30", f"bar đầu/cuối 09:00/09:30 dưới TZ={os.environ.get('TZ')}")

print("18. funding_status + plan_block: TK phái sinh 0đ ⇒ SHORT, số tiền cụ thể, không có lệnh")
ck = Clock(20, 0); f = Fake(ck, qmax=0)
fs = OF.funding_status(f, "0002023347")
check(fs["status"] == "SHORT" and fs["short_vnd"] == 100_000_000, f"thiếu 100tr ({fs['short_vnd']})")
check(abs(fs["im_vnd"] - 1850 * 100_000 * 0.1848) < 1, "ký quỹ ban đầu theo gói 1306")
check(fs["min_required_vnd"] >= 55_000_000, f"ký quỹ tối thiểu ≥55tr ({fs['min_required_vnd']:,.0f})")
blk = OF.plan_block("SpaceX", f, "0002023347", False, fund=fs)
check("TẮT/DRY" in blk and "CẦN NỘP" not in blk and len(blk.splitlines()) == 1, f"cờ TẮT ⇒ 1 dòng trạng thái, KHÔNG 'CẦN NỘP' ({blk[:60]})")
blk = OF.plan_block("SpaceX", f, "0002023347", True, fund=fs)
check("LIVE" in blk and "CẦN NỘP" in blk and "100.0tr" in blk and "09:25" in blk and "Trứng vàng" in blk, "cờ BẬT ⇒ khối đủ ý + CẦN NỘP")

print("19. load_profile: thiếu khoá / giá trị không phải literal true ⇒ TẮT")
tmp = tempfile.mkdtemp(dir=ROOT)
pth = os.path.join(tmp, "a.json")
json.dump({"accounts": [{"label": "SpaceX", "orb_futures": {"enabled": "true"}},
                        {"label": "ZaloPay"}]}, open(pth, "w"))
check(OF.load_profile("SpaceX", pth)[1]["enabled"] is False, "'true' chuỗi ⇒ TẮT")
check(OF.load_profile("ZaloPay", pth)[1]["enabled"] is False, "không khoá ⇒ TẮT")
json.dump({"accounts": [{"label": "SpaceX", "enabled": False, "orb_futures": {"enabled": True}},
                        {"label": "ZaloPay", "enabled": True, "orb_futures": {"enabled": True}}]}, open(pth, "w"))
check(OF.load_profile("SpaceX", pth)[1]["enabled"] is False, "m2: account enabled=false ⇒ ORB TẮT dù sleeve true")
check(OF.load_profile("ZaloPay", pth)[1]["enabled"] is True, "account true + sleeve true ⇒ BẬT")

print("20. Feed trễ 90s: 09:31:05 chưa có bar 09:30 ⇒ CHỜ (không bỏ phiên), vào khi bar tới")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0, feed_lag_s=90)
bot, ev, d = mk(f, ck); r = bot.run()
check(r == "CLOSED" and len(f.placed) == 2 and dt.time(9, 32, 30) <= f.placed[0]["t"].time() < dt.time(9, 33),
      f"vào lúc {f.placed[0]['t'].time() if f.placed else None}")

def reds(ev, sub=""):
    return [e for e in ev if e[0] == "N" and e[2] and sub in e[1]]


def open_bot(path=None, **kw):
    """Bot LIVE đã OPEN long sau 1 chu kỳ lúc 09:31:05."""
    ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0, path=path, **kw)
    bot, ev, d = mk(f, ck); bot.run(once=True)
    assert bot.state["stage"] == "OPEN", bot.state
    return ck, f, bot, ev, d


print("20b. user chốt 17/11: mặc định ORB_CLOSE_ALLOWED_UNDER_BOT_STOP=True (đóng được, KHÔNG vào được dưới BOT_STOP)")
check(OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP is True, "hằng số mặc định = True")
print("21. B1 BOT_STOP khi OPEN, hằng số=False: nhiều vòng, chạm stop ⇒ 0 lệnh đóng, KHÔNG SKIPPED, báo ĐỎ lặp")
OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = False
ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 30) else 1800.0)
open(os.path.join(d, "BOT_STOP"), "w").close()
ck.t = ck.t.replace(hour=10, minute=0)
r = bot.run()
n_red = len(reds(ev, "CẦN USER ĐÓNG TAY"))
check(r == "OPEN" and len(f.placed) == 1, f"kết thúc phiên vẫn OPEN, chỉ 1 lệnh (vào) ({r}, {len(f.placed)})")
check(n_red >= 10, f"báo ĐỎ lặp nhiều chu kỳ ({n_red})")
check(any("CHẠM STOP" in e[1] for e in reds(ev)), "có báo 'CHẠM STOP' khi giá qua stop")
check(any(e[0] == "N" and e[2] and "14:45" in e[1] for e in ev), "14:45 báo ĐỎ đóng tay")
check(bot.state["stage"] != "SKIPPED", "KHÔNG bị ghi đè SKIPPED")
lo = reds(ev, "đã qua 14:29")
check(lo and all("KHÔNG đặt lệnh nào" in e[1] for e in lo) and not any("đang đặt lại" in e[1] for e in lo),
      f"N-c late_open dưới BOT_STOP+False: 'KHÔNG đặt lệnh nào', không 'đang đặt lại' ({len(lo)})")
bot2, ev2, _ = mk(f, Clock(14, 50), d=d); bot2.run()
check(len(f.placed) == 1 and reds(ev2), "watchdog 14:50: vẫn báo ĐỎ, vẫn 0 lệnh mới")

print("22. B1 BOT_STOP khi OPEN, hằng số=True: chạm stop ⇒ ĐÓNG; INIT dưới BOT_STOP vẫn SKIPPED (không vào)")
OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = True
ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 30) else 1800.0)
open(os.path.join(d, "BOT_STOP"), "w").close()
r = bot.run()
check(r == "CLOSED" and bot.state["exit_reason"] == "STOP" and len(f.placed) == 2 and f.pos == [],
      f"đóng STOP dưới BOT_STOP ({r}, {len(f.placed)})")
ck = Clock(9, 31, 5); f = Fake(ck); bot, ev, d = mk(f, ck)
open(os.path.join(d, "BOT_STOP"), "w").close()
check(bot.run() == "SKIPPED" and not f.placed, "INIT + BOT_STOP ⇒ SKIPPED, 0 lệnh (kể cả hằng số=True)")
OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = False
ck = Clock(9, 31, 5); f = Fake(ck); bot, ev, d = mk(f, ck)
open(os.path.join(d, "BOT_STOP"), "w").close()
try:
    bot._place("buy", 1860.0, "ENTRY"); refused = False
except OF.OrderRefused:
    refused = True
check(refused and not f.placed, "_place: lớp chặn cuối từ chối khi BOT_STOP")

print("23. B4 lỗi thoáng qua trong vòng giám sát: không crash, thử lại, ≥3 lỗi liên tiếp ⇒ báo ĐỎ")
ck, f, bot, ev, d = open_bot()
f.fail_lt = 2
r1 = bot.run(once=True); r2 = bot.run(once=True)
check(r1 == r2 == "OPEN" and bot.err_n == 2 and not reds(ev, "LIÊN TIẾP"), "2 lỗi: vẫn OPEN, chưa báo")
f.fail_lt = 1
bot.run(once=True)
check(len(reds(ev, "LIÊN TIẾP")) == 1, "lỗi thứ 3 liên tiếp ⇒ 1 báo ĐỎ")
r = bot.run()
check(r == "CLOSED" and bot.err_n == 0 and len(f.placed) == 2, f"hồi phục ⇒ CLOSED ({r})")

print("24. B3 order_detail thiếu averagePrice ⇒ KHÔNG crash, giá ƯỚC + cờ + báo ĐỎ")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0, no_avg=True)
bot, ev, d = mk(f, ck)
r = bot.run()
check(r == "CLOSED" and bot.state.get("fill_px_estimated") is True and bot.state.get("exit_px_estimated") is True,
      f"CLOSED, cờ fill_px_estimated + exit_px_estimated ({r})")
check(bot.state["entry_px"] == 1855.0 and len(reds(ev, "giá ƯỚC")) == 2, "giá ước = LTP, 2 báo ĐỎ")

print("25. Sau phiên: khởi động 15:00 (INIT) ⇒ 0 lệnh; M1 _exit ≥14:45 chỉ báo, 0 lệnh")
ck = Clock(15, 0); f = Fake(ck); bot, ev, d = mk(f, ck)
check(bot.run() == "SKIPPED" and not f.placed, "INIT 15:00 ⇒ SKIPPED, 0 lệnh")
ck, f, bot, ev, d = open_bot()
ck.t = ck.t.replace(hour=14, minute=46)
bot._exit("TIME", ck.t)
check(len(f.placed) == 1 and reds(ev, "14:45"), "_exit 14:46: 0 lệnh đóng, báo ĐỎ")
bot2, ev2, _ = mk(f, ck, d=d)
check(bot2.run() == "OPEN" and len(f.placed) == 1 and reds(ev2, "14:45"), "watchdog 14:46 ở OPEN: chỉ báo")

print("26. B2 trạng thái kết thúc mà broker còn vị thế ⇒ báo ĐỎ MỖI lần chạy, 0 lệnh")
ck = Clock(10, 0); f = Fake(ck, positions=[{"symbol": CT, "openQuantity": 1, "side": "NB"}])
bot, ev, d = mk(f, ck); bot.stage("SKIPPED", skip_reason="x")
for i in range(2):
    b, e, _ = mk(f, ck, d=d)
    check(b.run() == "SKIPPED" and not f.placed and reds(e, "CÒN +1 HĐ"), f"lần {i + 1}: SKIPPED + báo ĐỎ")
f.pos = []
b, e, _ = mk(f, ck, d=d); b.run()
check(not reds(e), "broker phẳng ⇒ im lặng")

print("27. B2 lệnh vào PendingCancel sau huỷ ⇒ PAUSED (KHÔNG SKIPPED)")
ck = Clock(9, 31, 5); f = Fake(ck, no_fill=True, cancel_status="PendingCancel")
bot, ev, d = mk(f, ck)
check(bot.run() == "PAUSED" and "CÒN SỐNG" in bot.state["pause_reason"], f"PAUSED ({bot.state['stage']})")
check(OF.order_state(0, "PendingCancel") == "ALIVE" and OF.order_state(0, "Cancelled") == "DEAD"
      and OF.order_state(0, "") == "ALIVE" and OF.order_state(0, "Filled") == "ALIVE", "order_state: chỉ chết khi CHẮC")

print("28. B2 lệnh đóng PendingCancel rồi KHỚP ⇒ chỉ 1 lệnh đóng, không đảo vị thế")
ck = Clock(9, 31, 5)
f = Fake(ck, or_move=+5.0, exit_no_fill=True, cancel_status="PendingCancel", pc_fill_after=6)
bot, ev, d = mk(f, ck)
r = bot.run()
check(r == "CLOSED" and len(f.placed) == 2 and f.pos == [], f"CLOSED, 2 lệnh tổng, broker phẳng ({r}, {len(f.placed)}, {f.pos})")
ck = Clock(9, 31, 5)
f = Fake(ck, or_move=+5.0, exit_no_fill=True, cancel_status="PendingCancel")   # không bao giờ chết
bot, ev, d = mk(f, ck)
bot.run()
check(len(f.placed) == 2 and reds(ev, "chưa CHẮC chết") and reds(ev, "14:45"),
      f"PendingCancel mãi: KHÔNG đặt lệnh đóng thứ 2, báo ĐỎ ({len(f.placed)})")

print("29. B2 view cũ: order_detail nói lệnh đóng Cancelled/0 nhưng broker đã phẳng ⇒ PAUSED, không đóng lần 2")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0, exit_fill_hidden=True)
bot, ev, d = mk(f, ck)
r = bot.run()
check(r == "PAUSED" and len(f.placed) == 2 and f.pos == [], f"PAUSED, 0 lệnh đóng thứ 2 ({r}, {len(f.placed)})")

print("30. M2 thiếu khoá positions/orders ⇒ PAUSED (không coi là rỗng); kết thúc + thiếu khoá ⇒ báo ĐỎ")
for k in ("positions", "orders"):
    ck = Clock(9, 31, 5); f = Fake(ck, drop_keys=[k]); bot, ev, d = mk(f, ck)
    check(bot.run() == "PAUSED" and not f.placed and "thiếu khoá" in bot.state["pause_reason"], f"thiếu '{k}' ⇒ PAUSED")
ck = Clock(10, 0); f = Fake(ck, drop_keys=["positions"]); bot, ev, d = mk(f, ck); bot.stage("CLOSED")
b, e, _ = mk(f, ck, d=d); b.run()
check(reds(e, "KHÔNG đọc được positions"), "CLOSED + positions thiếu khoá ⇒ báo ĐỎ")

print("31. m1 đọc lại state SAU khi có khoá")
ck = Clock(9, 31, 5); f = Fake(ck); bot, ev, d = mk(f, ck)
other, _, _ = mk(f, ck, d=d); other.stage("SKIPPED", skip_reason="tiến trình khác")
check(bot.state["stage"] == "INIT" and bot.run() == "SKIPPED" and not f.placed, "state cũ trong RAM bị bỏ, 0 lệnh")

print("32. M3 default_notify: kênh rc≠0 ⇒ trả False, in stderr (không DEVNULL)")
import io, contextlib as _cl                                # noqa: E401,E402
tmpb = tempfile.mkdtemp(dir=ROOT)
for nm, rc in (("notify_thread.sh", 1), ("notify_telegram.sh", 3)):
    pth2 = os.path.join(tmpb, nm); open(pth2, "w").write(f"#!/bin/sh\necho loi-{nm} >&2\nexit {rc}\n"); os.chmod(pth2, 0o755)
saved = (OF.MIKE_BIN, os.environ.pop("MIKE_BOT_TEST_MODE"))
OF.MIKE_BIN = tmpb
buf = io.StringIO()
with _cl.redirect_stderr(buf):
    ok = OF.default_notify("x", red=True)
OF.MIKE_BIN = saved[0]; os.environ["MIKE_BOT_TEST_MODE"] = saved[1]
check(ok is False and "rc=1" in buf.getvalue() and "rc=3" in buf.getvalue() and "loi-notify_telegram" in buf.getvalue(),
      "2 kênh rc≠0 ⇒ False + stderr có rc và lỗi thật")
open(os.path.join(tmpb, "notify_telegram.sh"), "w").write("#!/bin/sh\nexit 0\n")
os.environ.pop("MIKE_BOT_TEST_MODE"); OF.MIKE_BIN = tmpb
with _cl.redirect_stderr(io.StringIO()):
    ok2 = OF.default_notify("x", red=True)
OF.MIKE_BIN = saved[0]; os.environ["MIKE_BOT_TEST_MODE"] = saved[1]
check(ok2 is True, "Telegram rc=0 ⇒ True dù Discord hỏng")

print("33. R1 lệnh ĐÓNG treo (EXIT_PLACED), BOT_STOP bật GIỮA CHỪNG, hằng số=False ⇒ không lệnh mới, không huỷ, ĐỎ lặp")
OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = False
ck, f, bot, ev, d = open_bot(exit_nofill_n=99)
ck.t = ck.t.replace(hour=14, minute=28, second=50)
bs = os.path.join(d, "BOT_STOP")
ck.hook = lambda t: t.time() >= dt.time(14, 29, 10) and not os.path.exists(bs) and open(bs, "w").close()
r = bot.run()
n_bs = len(reds(ev, "BOT_STOP đang bật"))
check(len(f.placed) == 2, f"placed giữ nguyên 2 (vào + 1 đóng) ({len(f.placed)})")
check(f.cancelled == [], f"KHÔNG huỷ lệnh đóng đang sống dưới BOT_STOP ({f.cancelled})")
check(n_bs >= 10, f"báo ĐỎ BOT_STOP lặp ({n_bs})")
check(r == "EXIT_PLACED" and bot.state["exit_oid"] == f.placed[1]["oid"], f"kết thúc EXIT_PLACED, giữ oid đóng ({r})")

print("34. R1 cùng kịch bản, hằng số=True ⇒ huỷ lệnh đóng treo, đặt lại, ĐÓNG xong")
OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = True
ck, f, bot, ev, d = open_bot(exit_nofill_n=1)
ck.t = ck.t.replace(hour=14, minute=28, second=50)
bs = os.path.join(d, "BOT_STOP")
ck.hook = lambda t: t.time() >= dt.time(14, 29, 10) and not os.path.exists(bs) and open(bs, "w").close()
r = bot.run()
check(r == "CLOSED" and len(f.placed) == 3 and f.cancelled == [f.placed[1]["oid"]] and f.pos == [],
      f"CLOSED, huỷ đúng lệnh đóng 1, tổng 3 lệnh, phẳng ({r}, {len(f.placed)}, {f.cancelled})")
check(reds(ev, "cho phép ĐÓNG"), "báo chế độ cho phép ĐÓNG")
OF.ORB_CLOSE_ALLOWED_UNDER_BOT_STOP = False

print("35. R2 lệnh vào báo Cancelled/khớp 0 nhưng broker CÓ vị thế ⇒ SKIPPED + báo ĐỎ NGAY trong cùng tiến trình")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0, entry_fill_hidden=True)
bot, ev, d = mk(f, ck)
r = bot.run()
check(r == "SKIPPED" and len(f.placed) == 1 and f.pos, f"SKIPPED, 1 lệnh, broker còn vị thế ({r})")
check(reds(ev, "CÒN +1 HĐ"), "báo ĐỎ 'BROKER CÒN +1 HĐ' ngay, không chờ watchdog")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0); bot, ev, d = mk(f, ck)
check(bot.run() == "CLOSED" and not reds(ev, "BROKER CÒN"), "CLOSED + broker phẳng ⇒ không báo thừa")

print("36. N-a DRY: trạng thái kết thúc + broker có vị thế (user giữ tay) ⇒ chỉ log, KHÔNG Telegram/Discord/ĐỎ")
ck = Clock(10, 0); f = Fake(ck, positions=[{"symbol": CT, "openQuantity": 1, "side": "NB"}])
bot, ev, d = mk(f, ck, live=False); bot.stage("SKIPPED", skip_reason="x")
evs = []
for _ in range(3):
    b, e, _ = mk(f, ck, live=False, d=d); b.run(); evs += e
rawp = os.path.join(d, "orb_futures", f"orb_futures_raw_{DAY}.jsonl")
check(not [e for e in evs if e[0] == "N"] and not [e for e in evs if e[0] == "B"], f"DRY: 0 notify/bus ({len(evs)})")
check(open(rawp).read().count("watch_dry_position") == 3, "DRY: ghi raw log mỗi lần")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0); bot, ev, d = mk(f, ck, live=False)
check(bot.run() == "CLOSED" and not f.placed, "DRY chạy đủ vẫn CLOSED, 0 lệnh broker")

print("37. N-b lỗi vòng giám sát kéo dài 150s ⇒ báo ĐỎ ≤1 tin/phút (không mỗi 3 lỗi)")
ck, f, bot, ev, d = open_bot()
f.fail_lt = 30
r = bot.run()
n_le = len(reds(ev, "LIÊN TIẾP"))
check(r == "CLOSED" and 1 <= n_le <= 3, f"30 lỗi × 5s ⇒ {n_le} báo ĐỎ (cũ: 10), hồi phục CLOSED ({r})")
check("loop_err" not in bot._last_alert, "minor vòng 4: hồi phục ⇒ xoá _last_alert['loop_err']")

print("38. N-e lớp chặn cuối _place ≥14:45 (không BOT_STOP) ⇒ OrderRefused, 0 lệnh")
ck, f, bot, ev, d = open_bot()
ck.t = ck.t.replace(hour=14, minute=45, second=0)
try:
    bot._place("sell", 1720.5, "EXIT"); refused = False
except OF.OrderRefused:
    refused = True
check(refused and len(f.placed) == 1, f"14:45:00 ⇒ từ chối, placed giữ 1 ({len(f.placed)})")

print("39. R2 vòng 4: positions TRỄ 1 lần đọc sau khớp lệnh đóng ⇒ KHÔNG báo 'BROKER CÒN' (đọc lại thấy phẳng)")


def lag_positions(f, bot, n):
    """n lần đọc positions ĐẦU TIÊN sau khi state = CLOSED trả vị thế cũ (+1 NB) dù broker đã phẳng."""
    orig, left = f.positions, [n]

    def lagged(acc, market_type="STOCK"):
        if bot.state["stage"] == "CLOSED" and left[0] > 0:
            left[0] -= 1
            return {"positions": [{"symbol": CT, "openQuantity": 1, "side": "NB"}]}
        return orig(acc, market_type)
    f.positions = lagged
    return left


ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 0) else 1800.0)
left = lag_positions(f, bot, 1)
r = bot.run()
check(r == "CLOSED" and f.pos == [] and left[0] == 0, f"CLOSED do bot khớp lệnh đóng, đã đọc trễ 1 lần ({r}, {left})")
check(not reds(ev, "BROKER CÒN"), f"positions trễ 1 lần ⇒ KHÔNG báo ĐỎ giả ({len(reds(ev, 'BROKER CÒN'))})")

print("40. R2 vòng 4: positions còn vị thế qua MỌI lần đọc (trễ > số lần) ⇒ VẪN báo ĐỎ, đúng 3 lần đọc")
ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 0) else 1800.0)
left = lag_positions(f, bot, 99)
r = bot.run()
check(r == "CLOSED" and 99 - left[0] == OF.TERMINAL_CONFIRM_TRIES, f"đọc đúng {OF.TERMINAL_CONFIRM_TRIES} lần ({99 - left[0]})")
check(len(reds(ev, "BROKER CÒN +1 HĐ")) == 1, "hết số lần mà vẫn còn ⇒ báo ĐỎ 1 lần")

print("41. R2 vòng 4: positions LỖI đọc ngay sau khi kết thúc ⇒ báo ĐỎ NGAY (không chờ đọc lại)")
ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 0) else 1800.0)
orig = f.positions
n_err = [0]


def boom(acc, market_type="STOCK"):
    if bot.state["stage"] == "CLOSED":
        n_err[0] += 1
        raise ConnectionError("positions lỗi giả")
    return orig(acc, market_type)


f.positions = boom
r = bot.run()
check(r == "CLOSED" and reds(ev, "KHÔNG đọc được positions") and n_err[0] == 1,
      f"lỗi đọc ⇒ ĐỎ ngay, 1 lần đọc ({r}, n_err={n_err[0]})")
check(not reds(ev, "BROKER CÒN"), "lỗi đọc ≠ 'BROKER CÒN'")

print("42. R2 vòng 4: đọc lại lần 2 LỖI (open→err→phẳng) ⇒ ĐỎ 'KHÔNG đọc được' đúng 1 lần, dừng ở lần 2, KHÔNG 'BROKER CÒN'")


def seq_positions(f, bot, seq):
    """Sau khi state = CLOSED, các lần đọc positions lần lượt trả: 'open' (+1 NB) | 'none' (dòng thiếu số lượng)
    | 'err' (ném lỗi) | 'flat'. Trả list ghi lại các lần đọc đã xảy ra."""
    orig, reads = f.positions, []

    def scripted(acc, market_type="STOCK"):
        if bot.state["stage"] != "CLOSED":
            return orig(acc, market_type)
        k = len(reads)
        step = seq[min(k, len(seq) - 1)]
        reads.append(step)
        if step == "err":
            raise ConnectionError("positions lỗi giả lần đọc lại")
        if step == "open":
            return {"positions": [{"symbol": CT, "openQuantity": 1, "side": "NB"}]}
        if step == "none":
            return {"positions": [{"symbol": CT}]}
        return {"positions": []}
    f.positions = scripted
    return reads


ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 0) else 1800.0)
reads = seq_positions(f, bot, ["open", "err", "flat"])
r = bot.run()
check(r == "CLOSED" and reads == ["open", "err"], f"dừng ở lần đọc 2, không chạy lần 3 ({r}, {reads})")
check(len(reds(ev, "KHÔNG đọc được positions")) == 1, f"đúng 1 ĐỎ 'KHÔNG đọc được' ({len(reds(ev, 'KHÔNG đọc được positions'))})")
check(not reds(ev, "BROKER CÒN"), "lỗi đọc ở lần ≥2 ≠ 'BROKER CÒN'")

print("43. R2 vòng 4: dòng vị thế thiếu số lượng (None) ⇒ ĐỎ 'không đọc được số lượng'; open,open,None ⇒ cũng ĐỎ")
ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 0) else 1800.0)
reads = seq_positions(f, bot, ["none", "none", "none"])
r = bot.run()
check(r == "CLOSED" and len(reads) == OF.TERMINAL_CONFIRM_TRIES, f"None ×{OF.TERMINAL_CONFIRM_TRIES} đọc đủ số lần ({r}, {reads})")
check(len(reds(ev, "không đọc được số lượng")) == 1, f"đúng 1 ĐỎ 'không đọc được số lượng' ({len(reds(ev, 'không đọc được số lượng'))})")
ck, f, bot, ev, d = open_bot(path=lambda t: 1855.0 if t.time() < dt.time(10, 0) else 1800.0)
reads = seq_positions(f, bot, ["open", "open", "none"])
r = bot.run()
check(r == "CLOSED" and reads == ["open", "open", "none"], f"open,open,None đọc đủ 3 lần ({r}, {reads})")
check(len(reds(ev, "không đọc được số lượng")) + len(reds(ev, "BROKER CÒN")) >= 1, "open,open,None ⇒ có ĐỎ (không im lặng)")
check(len(reds(ev, "BROKER CÒN +1 HĐ")) == 0, "lần đọc cuối None ⇒ KHÔNG nói còn +1 (số cuối không rõ)")

print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'} (TZ={os.environ.get('TZ')})")
sys.exit(1 if FAILS else 0)
