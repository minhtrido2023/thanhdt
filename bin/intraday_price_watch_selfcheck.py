#!/usr/bin/env python3
"""intraday_price_watch_selfcheck.py — selfcheck cổng giá trong phiên + cutloss SHADOW.

Ba phần:
  A. engine thuần (`intraday_cutloss_engine`): cổng kích hoạt, phán quyết→hành động, đọc trả lời,
     phiên theo sàn, loại lệnh, chọn/leo thang chế độ, bộ máy bán (kẹt sàn, nghỉ trưa, ATC, T+2,
     BOT_STOP, UPCOM rơi về LO, lô lẻ).
  B. driver (`intraday_price_watch.run_tick`) với phụ thuộc GIẢ: dòng thời gian T0 → phán quyết →
     báo cáo → trả lời/im lặng → bán; 1 lần/ngày; rút gọn khi sát sàn; dispatch at-most-once;
     carryover sang phiên sau (ATO); proxy chỉ-đọc DNSE.
  C. REPLAY dữ liệu PHÚT thật (DNSE ohlc resolution=1, fixture tải sẵn — chạy offline):
     PNJ 24/09→05/10, DGC 22-23/07, TV1 15-16/07. In bảng kết quả + kiểm kỳ vọng của plan.

Không gọi mạng, không gửi tin, không dispatch (Notifier dry, dispatch=False). Mọi state ghi vào
thư mục tạm. Chạy được dưới mọi TZ: giờ trong test là ICT naive truyền tường minh.
Chạy: $DNA_PYEXE bin/intraday_price_watch_selfcheck.py [-v]
"""
import datetime as dt
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude")

import intraday_cutloss_engine as E  # noqa: E402
import intraday_price_watch as W  # noqa: E402

FIXTURE = os.environ.get("IPW_FIXTURE") or os.path.join(
    os.path.dirname(HERE), "agents", "Taylor", "research", "intraday_watch_20261006", "fixtures",
    "replay_bars.json")
VERBOSE = "-v" in sys.argv
N_PASS, FAILS = 0, []


def check(name, cond, detail=""):
    global N_PASS
    if cond:
        N_PASS += 1
        if VERBOSE:
            print(f"  ok  {name}")
    else:
        FAILS.append(f"{name} {detail}")
        print(f"  FAIL {name} {detail}")


def T(hhmm, day="2026-10-06"):
    return dt.datetime.fromisoformat(f"{day}T{hhmm}")


# ================================================================ A. engine
def test_trigger():
    tr = E.trigger_check(95_000, 100_000, 93_000, 1000, 1000)
    check("trigger −5,0%/idio −4,0 biên ⇒ kích hoạt", tr["hit"])
    tr = E.trigger_check(95_100, 100_000, 93_000, 1000, 1000)
    check("trigger −4,9% ⇒ không", not tr["hit"])
    tr = E.trigger_check(94_000, 100_000, 93_000, 970, 1000)
    check("trigger −6% nhưng VNI −3% (idio −3) ⇒ không (cả thị trường)", not tr["hit"])
    tr = E.trigger_check(94_000, 100_000, 93_000, 990, 1000)
    check("trigger −6%, VNI −1% (idio −5) ⇒ kích hoạt", tr["hit"])
    tr = E.trigger_check(93_000, 100_000, 93_000, 940, 1000)
    check("chạm sàn ⇒ kích hoạt dù idio nhỏ", tr["hit"] and tr["at_floor"])
    tr = E.trigger_check(94_000, 100_000, 93_000, None, 1000)
    check("thiếu VNINDEX ⇒ idio=ret + cờ", tr["hit"] and tr["vni_missing"])
    check("thiếu last/ref ⇒ None (không phát biểu)", E.trigger_check(None, 100_000, 93_000, 1, 1) is None)


def test_default_action():
    exp = {E.BROKEN: E.SELL_ALL, E.UNCLEAR: E.SELL_HALF, E.NOISE: E.HOLD}
    for book in E.V24_BOOKS:
        for v, a in exp.items():
            check(f"mặc định {book}+{v} = {a}", E.default_action(v, book) == a)
    for book in (E.DISCRETIONARY, E.UNKNOWN):
        check(f"{book}+GÃY = bán hết", E.default_action(E.BROKEN, book) == E.SELL_ALL)
        check(f"{book}+CHƯA RÕ = giữ", E.default_action(E.UNCLEAR, book) == E.HOLD)
        check(f"{book}+NHIỄU = giữ", E.default_action(E.NOISE, book) == E.HOLD)
    check("target 50% của 1.500 = 750", E.target_qty(E.SELL_HALF, 1500) == 750)
    t0 = T("10:00")
    check("hạn phán quyết 20'", E.verdict_deadline(t0, False) == T("10:20"))
    check("hạn phán quyết rút gọn 10'", E.verdict_deadline(t0, True) == T("10:10"))
    check("hạn trả lời 30'", E.reply_deadline(t0, False) == T("10:30"))
    check("hạn trả lời rút gọn 15'", E.reply_deadline(t0, True) == T("10:15"))


def test_parse_reply():
    s = T("10:00")
    m = lambda c, hhmm="10:05", bot=False, i=1: {"id": i, "is_bot": bot, "content": c, "created_at": T(hhmm)}
    check("GIỮ PNJ", E.parse_reply([m("GIỮ PNJ")], "PNJ", s)[0] == E.HOLD)
    check("bán 50% pnj (thường, có dấu)", E.parse_reply([m("bán 50% pnj")], "PNJ", s)[0] == E.SELL_HALF)
    check("BÁN PNJ", E.parse_reply([m("BÁN PNJ")], "PNJ", s)[0] == E.SELL_ALL)
    check("BAN 50 % PNJ không dấu", E.parse_reply([m("BAN 50 % PNJ")], "PNJ", s)[0] == E.SELL_HALF)
    check("@mention + BÁN PNJ.", E.parse_reply([m("<@123> BÁN PNJ.")], "PNJ", s)[0] == E.SELL_ALL)
    check("sai mã (BÁN TV1) ⇒ bỏ", E.parse_reply([m("BÁN TV1")], "PNJ", s)[0] is None)
    check("mã dài hơn (BÁN PNJX) ⇒ bỏ", E.parse_reply([m("BÁN PNJX")], "PNJ", s)[0] is None)
    check("câu thường 'không bán PNJ' ⇒ KHÔNG phải lệnh",
          E.parse_reply([m("không bán PNJ nhé")], "PNJ", s)[0] is None)
    check("câu kết thúc bằng mã 'không bán PNJ' ⇒ KHÔNG phải lệnh",
          E.parse_reply([m("không bán PNJ")], "PNJ", s)[0] is None)
    check("'BÁN 50 PNJ' thiếu % ⇒ bỏ", E.parse_reply([m("BÁN 50 PNJ")], "PNJ", s)[0] is None)
    check("tin bot ⇒ bỏ", E.parse_reply([m("BÁN PNJ", bot=True)], "PNJ", s)[0] is None)
    check("tin trước mốc ⇒ bỏ", E.parse_reply([m("BÁN PNJ", "09:59")], "PNJ", s)[0] is None)
    msgs = [m("BÁN PNJ", "10:05", i=1), m("GIỮ PNJ", "10:09", i=2)]
    check("nhiều tin ⇒ tin MỚI NHẤT thắng", E.parse_reply(msgs, "PNJ", s)[0] == E.HOLD)
    check("nhiều dòng, mỗi dòng 1 mã", E.parse_reply([m("GIỮ TV1\nBÁN PNJ")], "PNJ", s)[0] == E.SELL_ALL)


def test_phase_and_types():
    now = T("09:05")
    check("HNX không ATO ⇒ khớp liên tục", E.exchange_phase("ATO", now, "HNX") == "MORNING")
    check("HOSE ATO giữ", E.exchange_phase("ATO", now, "HOSE") == "ATO")
    check("UPCOM 14:35 ⇒ liên tục", E.exchange_phase("ATC", T("14:35"), "UPCOM") == "AFTERNOON")
    check("UPCOM 14:50 ⇒ liên tục", E.exchange_phase("CLOSED", T("14:50"), "UPCOM") == "AFTERNOON")
    check("UPCOM 15:01 ⇒ đóng", E.exchange_phase("CLOSED", T("15:01"), "UPCOM") == "CLOSED")
    check("HNX ATC giữ", E.exchange_phase("ATC", T("14:35"), "HNX") == "ATC")
    check("HOSE MP ⇒ MTL (chưa xác minh)", E.api_order_type("MP", "HOSE")[0] == "MTL"
          and "CHƯA" in E.api_order_type("MP", "HOSE")[1])
    check("UPCOM MP ⇒ rơi LO", E.api_order_type("MP", "UPCOM")[0] is None)
    check("UPCOM ATC ⇒ rơi LO", E.api_order_type("ATC", "UPCOM")[0] is None)
    check("HNX ATO ⇒ rơi LO", E.api_order_type("ATO", "HNX")[0] is None)
    check("HOSE ATC đã xác minh", E.api_order_type("ATC", "HOSE") == ("ATC", E.api_order_type("ATC", "HOSE")[1])
          and "đã xác minh" in E.api_order_type("ATC", "HOSE")[1])
    check("floor HOSE 35.300 ⇒ 32.850", E.floor_price(35_300, "HOSE") == 32_850)
    check("floor UPCOM 22.000 ⇒ 18.700", E.floor_price(22_000, "UPCOM") == 18_700)
    check("floor HNX 10.000 ⇒ 9.000", E.floor_price(10_000, "HNX") == 9_000)


def test_modes():
    check("mode 1 bình thường", E.select_mode(0.05, 0.0, 10_000, 1000, False) == 1)
    check("mode 2 speed ≤ −1%", E.select_mode(0.05, -0.01, 10_000, 1000, False) == 2)
    check("mode 2 room 3%", E.select_mode(0.03, 0.0, 10_000, 1000, False) == 2)
    check("mode 3 room 1,5%", E.select_mode(0.015, 0.0, 10_000, 1000, False) == 3)
    check("mode 3 depth2 < Q", E.select_mode(0.05, 0.0, 999, 1000, False) == 3)
    check("mode 4 sàn không bên mua", E.select_mode(0.0, 0.0, 0, 1000, True) == 4)
    check("chỉ leo thang 3→1 giữ 3", E.escalate(3, 1) == 3)
    check("leo 1→2", E.escalate(1, 2) == 2)
    check("depth2 lọc 2%", E.depth2_of([(100, 10), (98, 5), (97.9, 7)], 100) == 15)
    check("match_book chỉ khớp bên mua giá ≥ giá đặt", E.match_book(100_000, 500, [(100_000, 100), (99_000, 1_000)])
          == (100, 100_000))


def _snap(last=100_000, ref=105_000, floor=97_650, bids=None, px5=None, dvol=0, **kw):
    s = {"last": last, "ref": ref, "floor": floor, "bid": (bids or [(None, 0)])[0][0],
         "bids": bids if bids is not None else [(last, 100_000), (last - 100, 100_000)],
         "px_5m_ago": px5 or last, "dvol": dvol}
    s.update(kw)
    return s


def test_execution():
    # mode 1: 3 đợt 50/25/25, sổ dày
    ex = E.new_execution(1000, T("10:00"))
    big = [(100_000, 1_000_000), (99_900, 1_000_000)]
    snap = _snap(last=100_000, ref=100_000, floor=93_000, bids=big)
    it, ev = E.step_execution(ex, snap, "MORNING", T("10:00"), "HOSE", 1000, False)
    check("mode1 đợt 1 = 50% (500cp LO giá mua tốt nhất)",
          ex["mode"] == 1 and it and it[0]["qty"] == 500 and it[0]["price"] == 100_000
          and it[0]["kind"] == "LO", str(it))
    check("mode1 mô phỏng khớp ngay 500", ex["sold"] == 500)
    it, _ = E.step_execution(ex, snap, "MORNING", T("10:05"), "HOSE", 1000, False)
    check("mode1 chưa tới đợt 2 ⇒ không lệnh", not it, str(it))
    it, _ = E.step_execution(ex, snap, "MORNING", T("10:10"), "HOSE", 1000, False)
    check("mode1 đợt 2 (+10') = thêm 250", it and it[0]["qty"] == 200 and ex["sold"] == 700,
          f"{it} sold={ex['sold']}")  # 250 làm tròn lô ⇒ 200
    it, _ = E.step_execution(ex, snap, "MORNING", T("10:20"), "HOSE", 1000, False)
    check("mode1 đợt 3 (+20') bán phần còn lại", ex["sold"] == 1000 and it, f"sold={ex['sold']}")
    E.step_execution(ex, snap, "MORNING", T("10:21"), "HOSE", 1000, False)
    check("bán đủ ⇒ DONE", ex["status"] == "DONE")

    # mode1 ≤30% depth2
    ex = E.new_execution(10_000, T("10:00"))
    thin = [(100_000, 3_000), (99_900, 3_000)]
    snap = _snap(last=100_000, ref=100_000, floor=93_000, bids=thin)
    it, _ = E.step_execution(ex, snap, "MORNING", T("10:00"), "HOSE", 10_000, False)
    check("depth2 6.000 < Q ⇒ mode 3 (LO sàn toàn bộ)", ex["mode"] == 3 and it[0]["price"] == 93_000
          and it[0]["qty"] == 10_000, str(it))
    check("LO sàn khớp theo giá bên mua (6.000cp @ ≥99.900)", ex["sold"] == 6000
          and abs(E.avg_price(ex) - 99_950) < 1, f"{ex['sold']} {E.avg_price(ex)}")
    ex2 = E.new_execution(1_000, T("10:00"))
    E.step_execution(ex2, _snap(last=100_000, ref=100_000, floor=93_000, bids=[(100_000, 1_500), (99_950, 2_000)]),
                     "MORNING", T("10:00"), "HOSE", 1_000, False)
    check("mode1 lệnh con ≤ 30% depth2 (3.500×0,3=1.050 ⇒ ≤500 đợt 1)", ex2["mode"] == 1 and ex2["sold"] == 500)

    ex4 = E.new_execution(10_000, T("10:00"))
    it, _ = E.step_execution(ex4, _snap(last=100_000, ref=100_000, floor=90_000,
                                        bids=[(100_000, 6_000), (99_950, 6_000)]),
                             "MORNING", T("10:00"), "HNX", 10_000, False)
    check("mode1: 30% depth2 (12.000×0,3=3.600) chặn trước đợt 50% (5.000)", ex4["mode"] == 1 and it
          and it[0]["qty"] == 3_600, str(it))
    ex5 = E.new_execution(1_000, T("10:00"))
    ex5["mode"] = 3
    ex5["open"] = [{"kind": "LO", "price": 93_000, "qty": 1_000, "placed_at": "2026-10-06T10:00:00", "auction": False}]
    E.step_execution(ex5, _snap(last=95_000, ref=100_000, floor=93_000, bids=[], dvol=1_000),
                     "MORNING", T("10:01"), "HOSE", 1_000, False)
    check("lệnh sàn đang chờ khớp theo GIÁ KHỚP (95.000), không phải giá sàn",
          ex5["sold"] == 300 and abs(E.avg_price(ex5) - 95_000) < 1, f"{ex5['sold']} {E.avg_price(ex5)}")

    # mode 2: speed ≤ −1%/5' ⇒ MP lệnh con ≤ KL 2 mức mua
    ex = E.new_execution(5_000, T("10:00"))
    snap = _snap(last=100_000, ref=100_000, floor=93_000, px5=101_100,
                 bids=[(100_000, 3_000), (99_900, 3_000), (99_800, 9_000)])
    it, _ = E.step_execution(ex, snap, "MORNING", T("10:00"), "HOSE", 5_000, False)
    check("speed −1,1% ⇒ mode 2, MP→MTL, qty ≤ 2 mức (5.000)",
          ex["mode"] == 2 and it[0]["kind"] == "MP" and it[0]["api_order_type"] == "MTL"
          and it[0]["qty"] == 5_000, str(it))
    ex = E.new_execution(5_000, T("10:00"))
    it, _ = E.step_execution(ex, dict(snap), "MORNING", T("10:00"), "UPCOM", 5_000, False)
    check("UPCOM mode 2 ⇒ rơi LO tại giá mua thứ 2", it[0]["kind_effective"] == "LO"
          and it[0]["price"] == 99_900, str(it))

    # kẹt sàn ⇒ mode 4, LO sàn, ATC 14:30, ngoài giờ chờ ATO
    ex = E.new_execution(2_000, T("10:00"))
    stuck = _snap(last=93_000, ref=100_000, floor=93_000, bids=[], dvol=5_000)
    it, ev = E.step_execution(ex, stuck, "MORNING", T("10:00"), "HOSE", 2_000, False)
    check("kẹt sàn ⇒ mode 4 + LO sàn toàn bộ", ex["mode"] == 4 and it[0]["price"] == 93_000
          and it[0]["qty"] == 2_000 and ex["sold"] == 0, str(it))
    it, _ = E.step_execution(ex, stuck, "MORNING", T("10:01"), "HOSE", 2_000, False)
    check("kẹt sàn giữ lệnh sàn (không huỷ/đặt lại), ăn hàng đợi 10% KL",
          not it and ex["sold"] == int(5_000 * E.FLOOR_QUEUE_SHARE) and len(ex["open"]) == 1,
          f"{it} sold={ex['sold']}")
    it, ev = E.step_execution(ex, _snap(last=93_000, ref=100_000, floor=93_000, bids=[]),
                              "LUNCH", T("12:00"), "HOSE", 2_000, False)
    check("nghỉ trưa ⇒ không lệnh", not it and any("LUNCH" in e for e in ev))
    it, _ = E.step_execution(ex, stuck, "ATC", T("14:31"), "HOSE", 2_000, False)
    check("14:30 ⇒ huỷ LO + ATC phần dư (2.000 − 1.000 đã ăn hàng đợi)",
          [i["kind"] for i in it] == ["CANCEL", "ATC"] and it[1]["qty"] == 1_000, str(it))
    it, _ = E.step_execution(ex, stuck, "ATC", T("14:35"), "HOSE", 2_000, False)
    check("ATC chỉ gửi 1 lần", not it)
    sold0 = ex["sold"]
    it, ev = E.step_execution(ex, dict(stuck, auctions={"ATO": (99_000, 1_000_000), "ATC": (93_000, 5_000)}),
                              "CLOSED", T("14:46"), "HOSE", 2_000, False)
    check("kết quả ATC (KHÔNG lấy nhầm ATO) ở sàn ⇒ ăn 10% KL ATC (500); dư chờ phiên sau",
          ex["sold"] == sold0 + 500 and abs(ex["value"] - (sold0 * 93_000 + 500 * 93_000)) < 1 and any("NGOÀI GIỜ" in e for e in ev) and ex["status"] == "EXECUTING",
          f"{ex['sold']} {ev}")
    ex3 = E.new_execution(1_000, T("09:05"))
    E.step_execution(ex3, dict(stuck), "ATO", T("09:05"), "HOSE", 1_000, False)
    it, ev = E.step_execution(ex3, dict(stuck), "MORNING", T("09:15"), "HOSE", 1_000, False)
    check("ATO chưa có kết quả ⇒ chờ, không đặt lệnh liên tục", not it and any("chờ kết quả" in e for e in ev))
    it, ev = E.step_execution(ex3, dict(stuck), "MORNING", T("09:26"), "HOSE", 1_000, False)
    check("ATO quá 20' không có KL ⇒ coi khớp 0, bán tiếp", it and it[0]["price"] == 93_000
          and any("coi khớp 0" in e for e in ev), f"{it} {ev}")

    # UPCOM sau 14:30 vẫn khớp liên tục ⇒ LO, không ATC
    ex = E.new_execution(1_000, T("14:31"))
    ph = E.exchange_phase("ATC", T("14:31"), "UPCOM")
    it, _ = E.step_execution(ex, _snap(last=20_000, ref=20_000, floor=17_000,
                                       bids=[(20_000, 100_000), (19_900, 100_000)]),
                             ph, T("14:31"), "UPCOM", 1_000, False)
    check("UPCOM 14:31 ⇒ LO (không ATC)", it and it[0]["kind"] == "LO", str(it))

    # T+2 chưa về
    ex = E.new_execution(1_000, T("10:00"))
    it, ev = E.step_execution(ex, _snap(last=100_000, ref=100_000, floor=93_000, bids=big),
                              "MORNING", T("10:00"), "HOSE", 300, False)
    check("T+2: chỉ bán phần bán được (≤300) + WAIT_T2",
          ex["sold"] <= 300 and all(i["qty"] <= 300 for i in it if i["kind"] != "CANCEL")
          and any("WAIT_T2" in e for e in ev), f"{it} {ev}")
    it, ev = E.step_execution(ex, _snap(last=100_000, ref=100_000, floor=93_000, bids=big),
                              "MORNING", T("10:01"), "HOSE", ex["sold"], False)
    check("T+2: bán được = đã bán ⇒ không lệnh mới", not [i for i in it if i["kind"] != "CANCEL"])

    # BOT_STOP
    ex = E.new_execution(1_000, T("10:00"))
    it, ev = E.step_execution(ex, _snap(), "MORNING", T("10:00"), "HOSE", 1_000, True)
    check("BOT_STOP ⇒ 0 lệnh", not it and ex["sold"] == 0 and any("BOT_STOP" in e for e in ev))

    # leo thang: mode 3 rồi thị trường hồi ⇒ vẫn 3
    ex = E.new_execution(2_000, T("10:00"))
    E.step_execution(ex, _snap(last=94_000, ref=100_000, floor=93_000, bids=[(94_000, 100)]),
                     "MORNING", T("10:00"), "HOSE", 2_000, False)
    E.step_execution(ex, _snap(last=99_000, ref=100_000, floor=93_000, bids=big),
                     "MORNING", T("10:01"), "HOSE", 2_000, False)
    check("chỉ leo thang trong ngày (3 không lùi về 1)", ex["mode"] == 3)

    # lô lẻ
    ex = E.new_execution(150, T("10:00"))
    it, _ = E.step_execution(ex, _snap(last=100_000, ref=100_000, floor=93_000, bids=[(100_000, 50)]),
                             "MORNING", T("10:00"), "HOSE", 150, False)
    check("lô lẻ tách riêng (100 chẵn + 50 lẻ)", sorted((i["board"], i["qty"]) for i in it) ==
          [("even", 100), ("odd", 50)], str(it))


# ================================================================ B. driver với phụ thuộc giả
class Clock:
    now = None


class FakeMarket:
    def __init__(self, clock, prices, ref=100_000, exch="HOSE", vni=(1000.0, 1000.0), pos=None,
                 bids_fn=None, open_buys=None):
        self.c, self.prices, self.ref, self.exch, self.vni_, self.pos = clock, prices, ref, exch, vni, pos or {}
        self.bids_fn = bids_fn or (lambda last: [(last, 1_000_000), (last - 100, 1_000_000)])
        self.open_buys_ = open_buys or []

    def _last(self):
        last = None
        for hhmm, px in sorted(self.prices.items()):
            if T(hhmm, self.c.now.date().isoformat()) <= self.c.now:
                last = px
        return last

    def quote(self, sym):
        last = self._last()
        fl = E.floor_price(self.ref, self.exch)
        return {"last": last, "ref": self.ref, "floor": fl, "bid": last,
                "bids": self.bids_fn(last) if last else [], "exchange": self.exch,
                "exchange_known": True, "day_volume": 0}

    def bars(self, sym, day, index=False):
        return [(T(h, day.isoformat()), p, 0) for h, p in sorted(self.prices.items())
                if T(h, day.isoformat()) <= self.c.now - dt.timedelta(minutes=1)]

    def vni(self, now):
        return self.vni_

    def positions(self, account_id):
        return self.pos

    def open_buys(self, account_id, sym):
        return self.open_buys_


def _deps(tmp, mkt, uni, msgs=None, dispatch=False, bot_stop=None):
    # chỉ tin ĐÃ đăng tới thời điểm hiện tại (không nhìn trước)
    return W.Deps(mkt, W.Notifier(dry=True), tmp, dispatch=dispatch,
                  messages=(lambda: [m for m in (msgs or []) if mkt.c.now is None or m["created_at"] <= mkt.c.now]),
                  accounts=[], universe=uni,
                  bot_stop_path=bot_stop or os.path.join(tmp, "BOT_STOP_absent"),
                  nav=lambda lab: (1_000_000_000, "2026-10-05T20:15"))


def _uni(book="BAL", qty=1000, sellable=None, buys=None, tk="XYZ"):
    return {tk: {"holdings": {"SpaceX": {"qty": qty, "sellable": qty if sellable is None else sellable,
                                         "cost": 110_000, "book": book, "account_id": "A1"}},
                 "buys": buys or [], "watch": False}}


def _drive(tmp, mkt, deps, start, end, day="2026-10-06", hook=None):
    t = T(start, day)
    while t <= T(end, day):
        mkt.c.now = t
        if hook:
            hook(t)
        W.run_tick(t, deps)
        t += dt.timedelta(minutes=1)
    return W._read_json(W.state_path(deps.state_dir, t.date()))


def _verdict(tmp, tk, label, day="2026-10-06"):
    W._atomic_json(W.verdict_path(tmp, dt.date.fromisoformat(day), tk),
                   {"ticker": tk, "label": label, "summary": "test", "at": "x"})


def scenario(name, book, verdict_at=None, label=None, msgs=None, prices=None, end="11:20", sellable=None,
             buys=None, dispatch=False, bot_stop=False, pre_state=None, exch="HNX"):
    # Mặc định HNX: trên HOSE (biên 7%) giảm −5% đã cách sàn ≤2% ⇒ LUÔN rút gọn + chế độ ≥2 —
    # muốn thử nhánh 20'/30' và chế độ 1 phải dùng sàn biên rộng.
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    prices = prices or {"09:15": 100_000, "09:59": 94_000}   # −6%, VNI phẳng
    sell = 1000 if sellable is None else sellable
    mkt = FakeMarket(clock, prices, exch=exch, pos={"XYZ": {"qty": 1000, "sellable": sell}})
    bs = os.path.join(tmp, "BOT_STOP")
    if bot_stop:
        open(bs, "w").close()
    deps = _deps(tmp, mkt, _uni(book, sellable=sellable, buys=buys), msgs=msgs, dispatch=dispatch,
                 bot_stop=bs)
    if pre_state:
        pre_state(tmp)
    hook = (lambda t: _verdict(tmp, "XYZ", label) if label and t == T(verdict_at) else None)
    st = _drive(tmp, mkt, deps, "09:15", end, hook=hook)
    return st, deps, tmp


def _log(tmp, day="2026-10-06"):
    p = os.path.join(tmp, f"shadow_{day}.jsonl")
    return [json.loads(x) for x in open(p)] if os.path.exists(p) else []


def test_driver():
    # 1) BAL im lặng: timeout ⇒ CHƯA RÕ ⇒ bán 50%
    st, deps, tmp = scenario("bal_timeout", "BAL")
    c = st["cases"]["XYZ"]
    check("HNX −6% ⇒ room 4% ⇒ KHÔNG rút gọn", not c["compressed"])
    check("T0 = lần quét 10:00 (15'/lần)", c["t0"].endswith("10:00:00"), c["t0"])
    check("quá 20' ⇒ CHƯA RÕ (timeout)", c["verdict"]["label"] == E.UNCLEAR and c["verdict"]["source"] == "timeout"
          and c["report_at"].endswith("10:20:00"), str(c.get("verdict")))
    check("hạn trả lời = báo cáo + 30'", c["reply_deadline"].endswith("10:50:00"))
    check("im lặng BAL+CHƯA RÕ ⇒ bán 50% (target 500)", c["decision"]["source"] == "default"
          and c["execution"]["SpaceX"]["target"] == 500, str(c.get("execution")))
    lg = _log(tmp)
    first_int = [r for r in lg if r["kind"] == "CUTLOSS_TICK" and r.get("intents")]
    check("không lệnh dự định nào trước hạn chót 10:50", first_int and first_int[0]["ts"] >= "2026-10-06T10:50",
          first_int[0]["ts"] if first_int else "none")
    check("T0 báo Discord+Telegram+email, @owner", any(s["channel"] == "email" for s in deps.notifier.sent)
          and any("CỔNG GIÁ" in s["msg"] for s in deps.notifier.sent))
    check("mọi tin có nhãn [SHADOW]", all(s["msg"].startswith("[SHADOW]") for s in deps.notifier.sent))
    n_trig = sum(1 for r in lg if r["kind"] == "TRIGGER")
    check("mỗi mã tối đa 1 lần/ngày (quét 10:15/10:30/... không mở lại)", n_trig == 1, str(n_trig))
    shutil.rmtree(tmp)

    # 2) BAL + GÃY (agent 10:05) + user GIỮ trước hạn ⇒ giữ; rồi BÁN ⇒ bán
    msgs = [{"id": 1, "is_bot": False, "content": "GIỮ XYZ", "created_at": T("10:10")}]
    st, deps, tmp = scenario("bal_broken_hold", "BAL", "10:05", E.BROKEN, msgs=msgs, end="10:45")
    c = st["cases"]["XYZ"]
    check("phán quyết agent GÃY lúc 10:05", c["verdict"]["label"] == E.BROKEN and c["verdict"]["source"] == "agent"
          and c["report_at"].endswith("10:05:00"))
    check("mặc định GÃY = bán hết", c["actions_default"]["SpaceX"] == E.SELL_ALL)
    check("user GIỮ trước hạn ⇒ HOLD, không bán", c["decision"]["source"] == "user"
          and c["status"] == "HOLD" and not c["execution"], str(c.get("status")))
    shutil.rmtree(tmp)
    msgs2 = msgs + [{"id": 2, "is_bot": False, "content": "BÁN XYZ", "created_at": T("10:40")}]
    st, deps, tmp = scenario("bal_hold_then_sell", "BAL", "10:05", E.BROKEN, msgs=msgs2, end="10:45")
    c = st["cases"]["XYZ"]
    check("ca HOLD vẫn nhận lệnh BÁN sau đó ⇒ bán hết", c["execution"].get("SpaceX", {}).get("target") == 1000
          and c["status"] in ("EXECUTING", "DONE"), str(c.get("execution")))
    shutil.rmtree(tmp)

    # 2b) user BÁN trước phán quyết ⇒ bán ngay; phán quyết đến sau KHÔNG đè trạng thái
    msgs3 = [{"id": 3, "is_bot": False, "content": "BÁN XYZ", "created_at": T("10:02")}]
    st, deps, tmp = scenario("early_sell", "BAL", "10:15", E.NOISE, msgs=msgs3, end="10:40")
    c = st["cases"]["XYZ"]
    check("user BÁN 10:02 (trước phán quyết) ⇒ bán, phán quyết NHIỄU sau đó không dừng",
          c["decision"]["source"] == "user" and c["execution"]["SpaceX"]["target"] == 1000
          and c["status"] in ("EXECUTING", "DONE") and c.get("verdict", {}).get("label") == E.NOISE
          and any(r["kind"] == "VERDICT_LATE" for r in _log(tmp)), str(c.get("status")))
    check("tin user chỉ được đọc SAU khi đăng (USER_REPLY ≥ 10:02)",
          [r["ts"] for r in _log(tmp) if r["kind"] == "USER_REPLY"][0] >= "2026-10-06T10:02")
    check("bán xong ⇒ DONE + sổ cấm mua lại 10 phiên (06/10 ⇒ 20/10)", c["status"] == "DONE" and
          (W._read_json(os.path.join(tmp, "no_rebuy_shadow.json")) or {}).get("XYZ|SpaceX", {}).get("until")
          == "2026-10-20", str(W._read_json(os.path.join(tmp, "no_rebuy_shadow.json"))))
    shutil.rmtree(tmp)

    # 3) im lặng theo từng phán quyết × book
    for book, label, exp in [("BAL", E.NOISE, 0), ("LAG", E.BROKEN, 1000), ("CUSTOM30V", E.UNCLEAR, 500),
                             ("CAPIT", E.UNCLEAR, 500), (E.DISCRETIONARY, E.NOISE, 0),
                             (E.DISCRETIONARY, E.UNCLEAR, 0), (E.DISCRETIONARY, E.BROKEN, 1000),
                             (E.UNKNOWN, E.UNCLEAR, 0)]:
        st, deps, tmp = scenario(f"silence_{book}_{label}", book, "10:05", label, end="10:40")
        c = st["cases"]["XYZ"]
        tgt = c["execution"].get("SpaceX", {}).get("target", 0)
        check(f"im lặng {book}+{E.VERDICT_VN[label]} ⇒ target {exp}", tgt == exp and
              c["decision"]["source"] == "default", f"tgt={tgt} status={c['status']}")
        if exp == 0:
            check(f"{book}+{E.VERDICT_VN[label]} giữ ⇒ status HOLD", c["status"] == "HOLD")
        shutil.rmtree(tmp)

    # 3b) rơi sát sàn SAU T0, trước phán quyết ⇒ rút gọn từ lúc đó (hạn tính từ T0)
    st, deps, tmp = scenario("compress_later", "BAL", prices={"09:15": 100_000, "09:59": 94_000, "10:04": 92_500},
                             end="10:40")
    c = st["cases"]["XYZ"]
    check("HNX 92.500 (room 2,5%) lúc 10:05 ⇒ rút gọn, hết hạn phán quyết T0+10' = 10:10",
          c["compressed"] and c["report_at"].endswith("10:10:00"), str(c.get("report_at")))
    shutil.rmtree(tmp)

    # 3c) user GIỮ giữa lúc đang bán ⇒ dừng phần còn lại
    msgs4 = [{"id": 4, "is_bot": False, "content": "GIỮ XYZ", "created_at": T("10:40")}]
    st, deps, tmp = scenario("hold_mid", "BAL", "10:05", E.BROKEN, msgs=msgs4, end="11:00")
    c = st["cases"]["XYZ"]
    ex = c["execution"]["SpaceX"]
    check("GIỮ lúc 10:40 (đang bán từ 10:35) ⇒ STOPPED_BY_USER, bán dở 500/1000, ca HOLD",
          ex["status"] == "STOPPED_BY_USER" and ex["sold"] == 500 and c["status"] == "HOLD",
          f"{ex['status']} {ex['sold']} {c['status']}")
    shutil.rmtree(tmp)

    # 3d) carryover: chế độ đặt lại (chỉ leo thang TRONG ngày), lệnh chờ hết hiệu lực
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    W._atomic_json(W.state_path(tmp, dt.date(2026, 10, 6)), {"date": "2026-10-06", "cases": {
        "XYZ": {"ticker": "XYZ", "status": "EXECUTING", "execution": {"SpaceX": {
            "mode": 4, "open": [{"kind": "LO"}], "ato_sent": True, "atc_sent": True}}},
        "HLD": {"ticker": "HLD", "status": "HOLD", "execution": {}}}})
    st = W.load_state(tmp, dt.date(2026, 10, 7))
    ex = st["cases"]["XYZ"]["execution"]["SpaceX"]
    check("carryover: mode→0, open rỗng, cờ ATO/ATC đặt lại; ca HOLD không carry",
          ex["mode"] == 0 and ex["open"] == [] and not ex["atc_sent"] and "HLD" not in st["cases"])
    shutil.rmtree(tmp)

    # 4) rút gọn: sát sàn lúc kích hoạt (room ≤ 3%) ⇒ 10' + 15'
    st, deps, tmp = scenario("compressed", "BAL", prices={"09:15": 100_000, "09:59": 95_000}, end="10:40",
                             exch="HOSE")
    c = st["cases"]["XYZ"]
    check("HOSE −5% ⇒ room 2% (95.000 vs sàn 93.000) ⇒ rút gọn ngay từ T0", c["compressed"])
    check("rút gọn: phán quyết hết hạn 10' (10:10)", c["report_at"].endswith("10:10:00"), c.get("report_at"))
    check("rút gọn: hạn trả lời 15' (10:25)", c["reply_deadline"].endswith("10:25:00"))
    check("báo cáo ghi 'RÚT GỌN'", any("RÚT GỌN" in s["msg"] for s in deps.notifier.sent))
    shutil.rmtree(tmp)

    # 5) lệnh MUA trong plan ⇒ ghi hoãn (shadow)
    buys = [{"ticker": "XYZ", "qty": 300, "book": "LAG", "id": "B1", "account": "SpaceX", "account_id": "A1"}]
    st, deps, tmp = scenario("defer", "BAL", buys=buys, end="10:01")
    c = st["cases"]["XYZ"]
    check("lệnh MUA trong plan ⇒ deferred_buys 'GỠ khỏi plan' (chưa ra sàn)",
          c["deferred_buys"] and c["deferred_buys"][0]["would"].startswith("GỠ"))
    check("báo T0 nêu hoãn mua", any("lệnh MUA" in s["msg"] for s in deps.notifier.sent))
    shutil.rmtree(tmp)

    # 6) hạn chót rơi vào nghỉ trưa ⇒ thực hiện lúc 13:00
    st, deps, tmp = scenario("lunch", "BAL", "11:15", E.BROKEN, prices={"09:15": 100_000, "11:14": 94_000},
                             end="13:02")
    lg = _log(tmp)
    ints = [r for r in lg if r["kind"] == "CUTLOSS_TICK" and r.get("intents")]
    check("hạn 11:45 trong nghỉ trưa ⇒ lệnh đầu tiên lúc 13:00",
          ints and ints[0]["ts"] == "2026-10-06T13:00:00", ints[0]["ts"] if ints else "none")
    shutil.rmtree(tmp)

    # 7) BOT_STOP ⇒ không lệnh dự định
    st, deps, tmp = scenario("botstop", "BAL", "10:05", E.BROKEN, end="10:45", bot_stop=True)
    lg = _log(tmp)
    check("BOT_STOP ⇒ 0 intent", not any(r.get("intents") for r in lg if r["kind"] == "CUTLOSS_TICK")
          and any("BOT_STOP" in " ".join(r.get("events", [])) for r in lg))
    shutil.rmtree(tmp)

    # 8) T+2 chưa về: sellable 0 ⇒ chờ
    st, deps, tmp = scenario("t2", "BAL", "10:05", E.BROKEN, end="10:45", sellable=0)
    lg = _log(tmp)
    check("T+2 chưa về ⇒ không lệnh + WAIT_T2", not any(r.get("intents") for r in lg if r["kind"] == "CUTLOSS_TICK")
          and any("WAIT_T2" in " ".join(r.get("events", [])) for r in lg))
    shutil.rmtree(tmp)

    # 9) dispatch at-most-once: đã thử mà không có job ⇒ không dispatch lại, cờ
    calls = []
    orig = W.dispatch_investigation
    W.dispatch_investigation = lambda case, cmd, dry=False: (calls.append(1), (None, "boom"))[1]
    try:
        st, deps, tmp = scenario("dispatch_fail", "BAL", dispatch=True, end="10:25")
    finally:
        W.dispatch_investigation = orig
    c = st["cases"]["XYZ"]
    check("dispatch lỗi ⇒ gọi đúng 1 lần", len(calls) == 1, str(len(calls)))
    check("dispatch lỗi ⇒ cờ DISPATCH_UNCERTAIN + hết hạn CHƯA RÕ",
          any(r["kind"] == "DISPATCH_UNCERTAIN" for r in _log(tmp)) and c["verdict"]["label"] == E.UNCLEAR)
    shutil.rmtree(tmp)
    st, deps, tmp = scenario("dispatch_dry", "BAL", dispatch=False, end="10:01")
    inv = st["cases"]["XYZ"]["investigation"]
    check("dispatch dry ⇒ prompt có lệnh verdict + legal-vn", inv["job"] == "DRY")
    lg = [r for r in _log(tmp) if r["kind"] == "DISPATCH"]
    check("prompt nêu legal-vn + nhãn + lệnh verdict", lg and "legal-vn" in lg[0]["info"]
          and "verdict --date 2026-10-06 --ticker XYZ" in lg[0]["info"])
    shutil.rmtree(tmp)

    # 10) ngày nghỉ / cuối tuần / ngoài giờ ⇒ bỏ qua
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    deps = _deps(tmp, FakeMarket(Clock(), {}), {})
    check("thứ Bảy ⇒ bỏ qua", "skipped" in W.run_tick(T("10:00", "2026-10-10"), deps))
    check("Quốc khánh 02/09 ⇒ bỏ qua", "skipped" in W.run_tick(T("10:00", "2026-09-02"), deps))
    check("15:00 ⇒ bỏ qua", "skipped" in W.run_tick(T("15:00"), deps))
    shutil.rmtree(tmp)

    # 11) carryover: kẹt sàn tới hết phiên ⇒ phiên sau ATO (HOSE)
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 93_000}, bids_fn=lambda last: [], exch="HOSE")
    mkt.pos = {"XYZ": {"qty": 1000, "sellable": 1000}}
    deps = _deps(tmp, mkt, _uni("BAL"))
    hook = (lambda t: _verdict(tmp, "XYZ", E.BROKEN) if t == T("09:31") else None)
    st = _drive(tmp, mkt, deps, "09:15", "14:59", hook=hook)
    c = st["cases"]["XYZ"]
    ex = c["execution"]["SpaceX"]
    check("kẹt sàn cả phiên ⇒ mode 4", ex["mode"] == 4, str(ex["mode"]))
    check("14:30 ATC đã gửi", ex["atc_sent"])
    mkt.prices = {"09:15": 86_500}
    mkt.ref = 93_000
    st2 = _drive(tmp, mkt, deps, "09:00", "09:16", day="2026-10-07")
    c2 = st2["cases"]["XYZ"]
    lg = _log(tmp, "2026-10-07")
    ato = [i for r in lg if r["kind"] == "CUTLOSS_TICK" for i in r.get("intents", []) if i["kind"] == "ATO"]
    check("carryover sang 07/10 (không kích hoạt lại)", c2.get("carryover_from") == "2026-10-06"
          and sum(1 for r in lg if r["kind"] == "TRIGGER") == 0)
    check("phiên sau ⇒ ATO trước 09:15 cho phần dư", ato and ato[0]["at"] < "2026-10-07T09:15",
          str(ato[:1]))
    shutil.rmtree(tmp)

    # 11b) mã chỉ-watchlist ⇒ báo, không dispatch
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, {"XYZ": {"holdings": {}, "buys": [], "watch": True}}, dispatch=False)
    st = _drive(tmp, mkt, deps, "09:15", "10:02")
    c = st["cases"]["XYZ"]
    check("watchlist-only ⇒ báo + NO_POSITION, không dispatch", c["status"] == "NO_POSITION"
          and "investigation" not in c and any("chỉ watchlist" in m["msg"] for m in deps.notifier.sent))
    shutil.rmtree(tmp)

    # 12) proxy chỉ-đọc
    class _C:
        def place_order(self, *a, **k):
            return "PLACED"

        def positions(self, *a):
            return {"ok": 1}
    ro = W.ReadOnlyDNSE(_C())
    for bad in ("place_order", "cancel_order", "modify_order", "create_trading_token", "send_email_otp"):
        try:
            getattr(ro, bad)
            check(f"ReadOnlyDNSE chặn {bad}", False)
        except PermissionError:
            check(f"ReadOnlyDNSE chặn {bad}", True)
    check("ReadOnlyDNSE cho positions", ro.positions() == {"ok": 1})
    src = open(os.path.join(HERE, "intraday_price_watch.py")).read() + \
        open(os.path.join(HERE, "intraday_cutloss_engine.py")).read()
    check("mã nguồn không gọi .place_order(/.cancel_order(/.modify_order(",
          not any(f".{f}(" in src for f in ("place_order", "cancel_order", "modify_order")))
    check("không truy cập ._c ngoài proxy", src.count("_c\")") <= 1 and "ro._c" not in src)


# ================================================================ C. REPLAY dữ liệu phút thật
class ReplayMarket:
    """Thị trường dựng từ bar 1 phút DNSE. Sổ lệnh KHÔNG có lịch sử ⇒ sổ GIẢ: 2 mức mua =
    giá đóng bar & 1 bước dưới, mỗi mức = KL bar đó; bar khoá ở sàn (h=l=sàn) ⇒ không bên mua.
    Bar chỉ "thấy" được sau khi phút đó đóng (không nhìn trước)."""

    def __init__(self, fx, tk, clock, qty):
        self.c, self.tk, self.qty = clock, tk, qty
        self.case = fx["cases"][tk]
        self.exch = self.case["exchange"]

    def _day(self):
        return self.c.now.date().isoformat()

    def _ref(self, day):
        prev = [v for d, v in sorted(self.case["daily_close"].items()) if d < day]
        return prev[-1] * 1000

    def _bars(self, key="bars"):
        d = self.case["days"].get(self._day())
        if not d:
            return []
        out = []
        for hhmm, o, h, l_, c, v in d[key]:
            t = T(hhmm, self._day())
            if t + dt.timedelta(minutes=1) <= self.c.now:
                out.append((t, o, h, l_, c, v))
        return out

    def quote(self, sym):
        day = self._day()
        ref = self._ref(day)
        fl = E.floor_price(ref, self.exch)
        b = self._bars()
        if not b:
            return {"last": None, "ref": ref, "floor": fl, "bids": [], "exchange": self.exch,
                    "exchange_known": True, "day_volume": 0}
        t, o, h, l_, c, v = b[-1]
        last = c * 1000
        locked = h == l_ and last <= fl + 1
        tick = E.tick_of(last, self.exch)
        fresh = t + dt.timedelta(minutes=2) > self.c.now   # khớp định kỳ: chỉ có bên mua lúc có bar
        bids = [] if (locked or not fresh) else [(last, v), (last - tick, v)]
        return {"last": last, "ref": ref, "floor": fl, "bid": bids[0][0] if bids else None, "bids": bids,
                "exchange": self.exch, "exchange_known": True, "day_volume": sum(x[5] for x in b)}

    def bars(self, sym, day, index=False):
        return [(t, c * 1000, v) for t, o, h, l_, c, v in self._bars()]

    def vni(self, now):
        b = self._bars("vni_bars")
        prev = [v for d, v in sorted(self.case["vni_daily_close"].items()) if d < self._day()]
        return (b[-1][4] if b else None), (prev[-1] if prev else None)

    def positions(self, account_id):
        return {self.tk: {"qty": self.qty, "sellable": self.qty}}

    def open_buys(self, account_id, sym):
        return []


def replay(fx, tk, qty, book, label_by_day, reply=None):
    """Chạy run_tick mỗi phút qua mọi ngày fixture. label_by_day: {ngày: (giờ trả phán quyết, nhãn)}."""
    tmp = tempfile.mkdtemp(prefix=f"ipw_rp_{tk}_")
    clock = Clock()
    mkt = ReplayMarket(fx, tk, clock, qty)
    uni = {tk: {"holdings": {"ACC": {"qty": qty, "sellable": qty, "cost": None, "book": book,
                                     "account_id": "A"}}, "buys": [], "watch": False}}
    msgs = []
    deps = _deps(tmp, mkt, uni, msgs=msgs)
    held = qty
    deps.messages = lambda: [m for m in msgs if m["created_at"] <= clock.now]
    if reply:
        msgs.append(reply)
    rows = []
    for day in sorted(fx["cases"][tk]["days"]):
        t = T("09:00", day)
        while t <= T("14:59", day):
            clock.now = t
            st = W._read_json(W.state_path(tmp, t.date())) or {}
            c = (st.get("cases") or {}).get(tk)
            if c and day in label_by_day and not c.get("verdict"):
                at, lab = label_by_day[day]
                if t >= _p_t0_plus(c["t0"], at):
                    _verdict(tmp, tk, lab, c["t0"][:10])
            W.run_tick(t, deps)
            t += dt.timedelta(minutes=1)
        st = W._read_json(W.state_path(tmp, dt.date.fromisoformat(day))) or {}
        c = (st.get("cases") or {}).get(tk)
        ex = (c or {}).get("execution", {}).get("ACC") if c else None
        # Ca xong (DONE) ⇒ phiên sau broker trả KL còn lại. Ca đang carryover GIỮ nguyên KL broker
        # (đúng như shadow live: broker không đổi, engine tự trừ phần đã "bán").
        if c and c.get("status") == "DONE" and ex:
            held = max(0, held - ex["sold"])
        mkt.qty = held
        if held:
            uni[tk]["holdings"]["ACC"].update(qty=held, sellable=held)
        else:
            uni[tk]["holdings"] = {}
        close = fx["cases"][tk]["daily_close"][day] * 1000
        rows.append({"day": day, "case": bool(c), "t0": c["t0"][11:16] if c else None,
                     "trigger": c["trigger"]["reason"] if c else None,
                     "verdict": (c.get("verdict") or {}).get("label") if c else None,
                     "status": c["status"] if c else None, "mode": ex["mode"] if ex else None,
                     "sold": ex["sold"] if ex else 0, "target": ex["target"] if ex else 0,
                     "avg": E.avg_price(ex) if ex else None, "close": close})
    log = []
    for f in sorted(os.listdir(tmp)):
        if f.startswith("shadow_"):
            log += [json.loads(x) for x in open(os.path.join(tmp, f))]
    shutil.rmtree(tmp)
    return rows, log


def _p_t0_plus(t0, minutes):
    return dt.datetime.fromisoformat(t0) + dt.timedelta(minutes=minutes)


def _print_replay(title, rows, final_close):
    print(f"\n  REPLAY {title}")
    for r in rows:
        if not (r["case"] or r["sold"]):
            print(f"    {r['day']}: không kích hoạt (đóng cửa {r['close']:,.0f})")
            continue
        print(f"    {r['day']}: T0 {r['t0']} [{r['trigger']}] phán quyết={r['verdict']} status={r['status']}"
              f" mode={r['mode']} đã bán(mô phỏng) {r['sold']:,}/{r['target']:,}"
              + (f" giá TB {r['avg']:,.0f}" if r["avg"] else "") + f" | đóng cửa {r['close']:,.0f}")
    last = rows[-1]
    if last["sold"]:
        print(f"    ⇒ giá TB bán {last['avg']:,.0f} vs đóng cửa cuối {final_close:,.0f} "
              f"({(last['avg'] / final_close - 1) * 100:+.1f}%)")


def test_replay():
    if not os.path.exists(FIXTURE):
        check("fixture replay tồn tại", False, FIXTURE)
        return
    fx = json.load(open(FIXTURE))
    pnj_close = fx["cases"]["PNJ"]["daily_close"]["2026-10-05"] * 1000

    # PNJ 1.400cp (≈5% NAV sleeve) — book DISCRETIONARY (PNJ thật là excluded/discretionary)
    rows, log = replay(fx, "PNJ", 1400, E.DISCRETIONARY,
                       {"2026-09-24": (8, E.NOISE), "2026-09-28": (8, E.BROKEN)})
    _print_replay("PNJ discretionary (24/09 NHIỄU ⇒ giữ; 28/09 GÃY ⇒ bán hết)", rows, pnj_close)
    r = {x["day"]: x for x in rows}
    check("PNJ 24/09: cổng −5/−4 bắt được TRONG phiên (plan: 'bắt cả 3 ca')", r["2026-09-24"]["case"],
          str(r["2026-09-24"]))
    check("PNJ 24/09 discretionary+NHIỄU ⇒ giữ, 0 bán", r["2026-09-24"]["status"] == "HOLD"
          and r["2026-09-24"]["sold"] == 0)
    check("PNJ 28/09 chạm sàn ⇒ kích hoạt lại (ca 24/09 HOLD không carry)", r["2026-09-28"]["case"]
          and "SÀN" in (r["2026-09-28"]["trigger"] or ""))
    check("PNJ 28/09 sát sàn ⇒ chế độ rút gọn", any(x["kind"] == "TRIGGER" and x["ts"].startswith("2026-09-28")
                                                for x in log) and any(
        x["kind"] == "VERDICT" and x["ts"].startswith("2026-09-28") for x in log))
    check("PNJ 28/09 kẹt sàn ⇒ mode 4", r["2026-09-28"]["mode"] == 4, str(r["2026-09-28"]["mode"]))
    # Độ nhạy vị trí hàng đợi ở sàn: KHÔNG biết thật ⇒ chạy cận BI QUAN (ăn 0% KL khớp tại sàn)
    old = E.FLOOR_QUEUE_SHARE
    E.FLOOR_QUEUE_SHARE = 0.0
    try:
        rows_w, log_w = replay(fx, "PNJ", 1400, E.DISCRETIONARY,
                               {"2026-09-24": (8, E.NOISE), "2026-09-28": (8, E.BROKEN)})
    finally:
        E.FLOOR_QUEUE_SHARE = old
    _print_replay("PNJ discretionary — CẬN BI QUAN hàng đợi sàn = 0%", rows_w, pnj_close)
    atos = [i for x in log_w if x["kind"] == "CUTLOSS_TICK" for i in x.get("intents", []) if i["kind"] == "ATO"]
    atcs = [i for x in log_w if x["kind"] == "CUTLOSS_TICK" for i in x.get("intents", []) if i["kind"] == "ATC"]
    check("PNJ bi quan: kẹt sàn ⇒ ATC mỗi phiên + ATO phiên sau", len(atos) >= 4 and len(atcs) >= 4,
          f"ATO={len(atos)} ATC={len(atcs)}")
    rw = {x["day"]: x for x in rows_w}
    check("PNJ bi quan: 28/09 GÃY carry tới khi bán (không kích hoạt lại)",
          all(not rw[d]["case"] or rw[d]["t0"] == rw["2026-09-28"]["t0"] for d in
              ("2026-09-29", "2026-09-30", "2026-10-01", "2026-10-02")))
    check("PNJ bi quan: 0 khớp khi còn khoá sàn 28/09→01/10", all(rw[d]["sold"] == 0 for d in
                                                                ("2026-09-28", "2026-09-29", "2026-09-30", "2026-10-01")))
    check("PNJ bi quan: 02/10 sàn mở (KL lớn) ⇒ bán xong, giá TB ≥ sàn 02/10",
          rw["2026-10-02"]["sold"] == 1400 and rw["2026-10-02"]["avg"] >= 23_050, str(rw["2026-10-02"]))
    check("PNJ: mã đã bán hết (chỉ còn watchlist) ⇒ KHÔNG dispatch điều tra lại",
          not any(x["kind"] == "DISPATCH" and x["ts"] >= "2026-10-05" for x in log_w))
    rows_b, _ = replay(fx, "PNJ", 1400, "BAL", {"2026-09-24": (8, E.UNCLEAR), "2026-09-28": (8, E.BROKEN)})
    _print_replay("PNJ GIẢ ĐỊNH book V2.4 BAL (24/09 CHƯA RÕ ⇒ bán 50%)", rows_b, pnj_close)
    rb = {x["day"]: x for x in rows_b}
    check("PNJ-BAL 24/09 CHƯA RÕ ⇒ bán 50% (700cp) trong ngày", rb["2026-09-24"]["sold"] == 700,
          str(rb["2026-09-24"]))

    # DGC: 22/07 cả thị trường giảm ⇒ không; 23/07 kích hoạt. ZaloPay giữ 10.000cp, discretionary.
    rows, log = replay(fx, "DGC", 10_000, E.DISCRETIONARY, {"2026-07-23": (8, E.BROKEN)})
    _print_replay("DGC ZaloPay 10.000cp discretionary (23/07 GÃY ⇒ bán hết; khớp ĐỊNH KỲ)", rows,
                  fx["cases"]["DGC"]["daily_close"]["2026-07-23"] * 1000)
    r = {x["day"]: x for x in rows}
    # Plan nói DGC 22/07 KHÔNG bắt (idio −2,2 theo giá ĐÓNG CỬA). Trong phiên khác: kiểm engine
    # khớp công thức tính ĐỘC LẬP từ bar ở đúng lần quét T0, rồi báo phát hiện (không tune ngưỡng).
    c22 = fx["cases"]["DGC"]
    t0 = r["2026-07-22"]["t0"]
    if t0:
        bars = [b for b in c22["days"]["2026-07-22"]["bars"] if b[0] < t0]
        vbars = [b for b in c22["days"]["2026-07-22"]["vni_bars"] if b[0] < t0]
        ret = bars[-1][4] / c22["daily_close"]["2026-07-21"] - 1
        vret = vbars[-1][4] / c22["vni_daily_close"]["2026-07-21"] - 1
        check("DGC 22/07 kích hoạt TRONG phiên khớp công thức độc lập (ret≤−5 ∧ idio≤−4)",
              ret <= -0.05 and ret - vret <= -0.04, f"t0={t0} ret={ret:.4f} idio={ret - vret:.4f}")
        print(f"    ⚠️ PHÁT HIỆN: DGC 22/07 plan dự kiến KHÔNG bắt (theo đóng cửa idio −2,2) nhưng lúc {t0} "
              f"ret {ret*100:+.1f}% / idio {(ret - vret)*100:+.1f}% ⇒ cổng trong phiên BẮT.")
    else:
        check("DGC 22/07 không kích hoạt (đúng plan)", True)
    check("DGC 23/07 ⇒ kích hoạt", r["2026-07-23"]["case"], str(r["2026-07-23"]))

    # TV1 UPCOM: 16/07 kích hoạt; discretionary + NHIỄU ⇒ giữ; kịch bản GÃY ⇒ chỉ LO
    rows, log = replay(fx, "TV1", 2300, E.DISCRETIONARY, {"2026-07-16": (8, E.NOISE)})
    _print_replay("TV1 SpaceX 2.300cp discretionary (16/07 NHIỄU ⇒ giữ)", rows,
                  fx["cases"]["TV1"]["daily_close"]["2026-07-16"] * 1000)
    r = {x["day"]: x for x in rows}
    check("TV1 16/07 ⇒ kích hoạt", r["2026-07-16"]["case"], str(r["2026-07-16"]))
    check("TV1 discretionary+NHIỄU ⇒ giữ", r["2026-07-16"]["status"] == "HOLD" and r["2026-07-16"]["sold"] == 0)
    rows, log = replay(fx, "TV1", 2300, E.DISCRETIONARY, {"2026-07-16": (8, E.BROKEN)})
    _print_replay("TV1 kịch bản GÃY (UPCOM ⇒ chỉ LO)", rows, fx["cases"]["TV1"]["daily_close"]["2026-07-16"] * 1000)
    kinds = {i["api_order_type"] for x in log if x["kind"] == "CUTLOSS_TICK" for i in x.get("intents", [])
             if i["kind"] != "CANCEL"}
    check("TV1 UPCOM: mọi lệnh dự định đều LO", kinds == {"LO"}, str(kinds))


def main():
    print("intraday_price_watch_selfcheck")
    # fsync mỗi nhịp là độ bền ĐĨA (production 1 lần/phút); replay ~3.000 nhịp ⇒ tắt trong tiến
    # trình test để chạy đột biến được. Không phép thử nào ở đây kiểm độ bền đĩa.
    os.fsync = lambda fd: None
    for fn in (test_trigger, test_default_action, test_parse_reply, test_phase_and_types, test_modes,
               test_execution, test_driver, test_replay):
        fn()
    total = N_PASS + len(FAILS)
    print(f"\n{N_PASS}/{total} PASS" + (f" — {len(FAILS)} FAIL" if FAILS else ""))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
