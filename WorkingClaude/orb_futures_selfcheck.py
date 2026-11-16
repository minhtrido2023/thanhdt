# -*- coding: utf-8 -*-
"""Selfcheck trading_bot/orb_futures.py — FakeClient, KHÔNG chạm DNSE thật, KHÔNG ghi bus thật.

Chạy:  python3 orb_futures_selfcheck.py
       env -u TZ python3 orb_futures_selfcheck.py ; TZ=America/New_York python3 orb_futures_selfcheck.py
"""
import os
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")          # §5b — TRƯỚC mọi import bot
import datetime as dt
import json
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from trading_bot import orb_futures as OF                  # noqa: E402

ICT = OF.ICT
DAY = dt.date(2026, 11, 17)
CT = "41I1GB000"
FAILS = []


def check(cond, msg):
    print(("  PASS " if cond else "  FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


class Clock:
    def __init__(self, hh, mm, ss=0):
        self.t = dt.datetime(DAY.year, DAY.month, DAY.day, hh, mm, ss, tzinfo=ICT)

    def __call__(self):
        return self.t

    def sleep(self, s):
        self.t += dt.timedelta(seconds=s)


class Fake:
    """Broker giả: OR theo `or_move`, giá sau 09:30 theo hàm `path(t)`; lệnh LO khớp ngay ở giá hiện tại
    nếu marketable (trừ khi `no_fill`)."""

    def __init__(self, clock, or_move=+5.0, path=None, no_fill=False, positions=None, orders=None,
                 qmax=5, fx_dev=0.0, feed_lag_s=0):
        self.clock, self.or_move, self.no_fill, self.qmax, self.fx_dev = clock, or_move, no_fill, qmax, fx_dev
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
        return {"positions": list(self.pos)}

    def orders(self, acc, market_type="STOCK", order_category=None):
        return {"orders": list(self.book)}

    def place_order(self, acc, sym, qty, side, order_type="LO", price=None, market_type="STOCK",
                    loan_package_id=None, order_category="NORMAL"):
        assert market_type == "DERIVATIVE" and qty == 1 and order_type == "LO" and loan_package_id == 1306
        oid = str(1000 + len(self.placed))
        self.placed.append({"oid": oid, "side": side, "price": price, "t": self.clock()})
        self.book.append({"id": oid, "symbol": sym})
        px = self.path(self.clock())
        marketable = (side == "buy" and price >= px) or (side == "sell" and price <= px)
        if marketable and not self.no_fill:
            self.det[oid] = (1, px, "Filled")
            net = sum((1 if p["side"] == "NB" else -1) * p["openQuantity"] for p in self.pos)
            net += 1 if side == "buy" else -1
            self.pos = [] if net == 0 else [{"symbol": sym, "openQuantity": abs(net),
                                             "side": "NB" if net > 0 else "NS"}]
        else:
            self.det[oid] = (0, None, "New")
        return {"id": oid}

    def order_detail(self, acc, oid, market_type="STOCK"):
        q, px, st = self.det[oid]
        return {"id": oid, "fillQuantity": q, "averagePrice": px, "orderStatus": st}

    def cancel_order(self, acc, oid, market_type="STOCK", order_category="NORMAL"):
        self.cancelled.append(oid)
        q, px, st = self.det[oid]
        self.det[oid] = (q, px, "Cancelled")
        return {}


def mk(fake, clock, live=True, d=None):
    d = d or tempfile.mkdtemp(prefix="orbfut_")
    ev = []
    bot = OF.OrbFutures(fake, "SpaceX", "0002023347", live, clock=clock, sleep=clock.sleep,
                        notify=lambda m: ev.append(("N", m)),
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
blk = OF.plan_block("SpaceX", f, "0002023347", False, fund=fs)
check("DRY-RUN" in blk and "100.0tr" in blk and "09:25" in blk and "Trứng vàng" in blk, "plan block đủ ý")

print("19. load_profile: thiếu khoá / giá trị không phải literal true ⇒ TẮT")
tmp = tempfile.mkdtemp()
pth = os.path.join(tmp, "a.json")
json.dump({"accounts": [{"label": "SpaceX", "orb_futures": {"enabled": "true"}},
                        {"label": "ZaloPay"}]}, open(pth, "w"))
check(OF.load_profile("SpaceX", pth)[1]["enabled"] is False, "'true' chuỗi ⇒ TẮT")
check(OF.load_profile("ZaloPay", pth)[1]["enabled"] is False, "không khoá ⇒ TẮT")

print("20. Feed trễ 90s: 09:31:05 chưa có bar 09:30 ⇒ CHỜ (không bỏ phiên), vào khi bar tới")
ck = Clock(9, 31, 5); f = Fake(ck, or_move=+5.0, feed_lag_s=90)
bot, ev, d = mk(f, ck); r = bot.run()
check(r == "CLOSED" and len(f.placed) == 2 and dt.time(9, 32, 30) <= f.placed[0]["t"].time() < dt.time(9, 33),
      f"vào lúc {f.placed[0]['t'].time() if f.placed else None}")

print(f"\n{'ALL PASS' if not FAILS else f'{len(FAILS)} FAIL'} (TZ={os.environ.get('TZ')})")
sys.exit(1 if FAILS else 0)
