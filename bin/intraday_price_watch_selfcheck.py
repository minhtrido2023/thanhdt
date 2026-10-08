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
    # (d) ngưỡng tương đối theo biên độ sàn — chỉ log
    r = E.trigger_check_rel(96_500, 100_000, 93_000, 1000, 1000, "HOSE")
    check("rel HOSE −3,5% ⇒ kích hoạt (ngưỡng hiện hành thì không)", r["hit"]
          and not E.trigger_check(96_500, 100_000, 93_000, 1000, 1000)["hit"])
    check("rel HNX −4% ⇒ không (ngưỡng −4,5%)", not E.trigger_check_rel(96_000, 100_000, 90_000, 1000, 1000, "HNX")["hit"])
    check("rel UPCOM −6,5% ⇒ không (−7%)", not E.trigger_check_rel(93_500, 100_000, 85_000, 1000, 1000, "UPCOM")["hit"])
    check("rel UPCOM −7% ⇒ kích hoạt", E.trigger_check_rel(93_000, 100_000, 85_000, 1000, 1000, "UPCOM")["hit"])
    check("rel idio −3: HOSE −3,5% nhưng VNI −1% (idio −2,5) ⇒ không",
          not E.trigger_check_rel(96_500, 100_000, 93_000, 990, 1000, "HOSE")["hit"])
    # cảnh báo gộp cả thị trường
    h = lambda **k: {"hit": True, "vni_missing": False, "at_floor": False, **k}
    check("1 mã ⇒ không gộp", E.market_wide_reason([h()]) is None)
    check("2 mã ⇒ không gộp", E.market_wide_reason([h(), h()]) is None)
    check("3 mã ⇒ gộp", "3 mã" in (E.market_wide_reason([h(), h(), h()]) or ""))
    check("2 mã chạm sàn ⇒ gộp", "sàn" in (E.market_wide_reason([h(at_floor=True), h(at_floor=True)]) or ""))
    check("thiếu VNINDEX (1 mã) ⇒ gộp", "VNINDEX" in (E.market_wide_reason([h(vni_missing=True)]) or ""))
    check("không có mã ⇒ None", E.market_wide_reason([]) is None)


def test_default_action():
    exp = {E.BROKEN: E.SELL_ALL, E.UNCLEAR: E.SELL_HALF, E.NOISE: E.HOLD}
    for book in E.V24_BOOKS:
        for v, a in exp.items():
            check(f"mặc định {book}+{v} = {a}", E.default_action(v, book) == a)
    for book in (E.DISCRETIONARY, E.UNKNOWN):
        check(f"{book}+GÃY = bán hết", E.default_action(E.BROKEN, book) == E.SELL_ALL)
        check(f"{book}+CHƯA RÕ = giữ", E.default_action(E.UNCLEAR, book) == E.HOLD)
        check(f"{book}+NHIỄU = giữ", E.default_action(E.NOISE, book) == E.HOLD)
    for book in E.V24_BOOKS:
        for src in ("timeout", "no_dispatch"):
            check(f"(a) {book} không phán quyết agent ({src}) ⇒ GIỮ (không bán 50%)",
                  E.default_action(E.UNCLEAR, book, src) == E.HOLD)
        check(f"(b) {book}+GÃY nhưng no_auto_sell ⇒ GIỮ", E.default_action(E.BROKEN, book, "agent", True) == E.HOLD)
    check("(a) hằng số NON_AGENT_DEFAULT = GIỮ", E.NON_AGENT_DEFAULT == E.HOLD)
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
    P = "SHADOW"
    check("SHADOW: 'SHADOW BÁN PNJ' ⇒ bán", E.parse_reply([m("SHADOW BÁN PNJ")], "PNJ", s, prefix=P)[0] == E.SELL_ALL)
    check("SHADOW: 'shadow giữ pnj' ⇒ giữ", E.parse_reply([m("shadow giữ pnj")], "PNJ", s, prefix=P)[0] == E.HOLD)
    check("SHADOW: '<@1> SHADOW BÁN 50% PNJ' ⇒ 50%",
          E.parse_reply([m("<@1> SHADOW BÁN 50% PNJ")], "PNJ", s, prefix=P)[0] == E.SELL_HALF)
    check("SHADOW: 'BÁN PNJ' trần (lệnh thật cho Mike) ⇒ KHÔNG hiểu", E.parse_reply([m("BÁN PNJ")], "PNJ", s,
                                                                                   prefix=P)[0] is None)
    check("SHADOW: 'GIỮ PNJ' trần ⇒ KHÔNG hiểu", E.parse_reply([m("GIỮ PNJ")], "PNJ", s, prefix=P)[0] is None)
    check("SHADOW: 'không SHADOW BÁN PNJ' ⇒ KHÔNG", E.parse_reply([m("không SHADOW BÁN PNJ")], "PNJ", s,
                                                                   prefix=P)[0] is None)


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
    ex["mode"] = 2
    ex["open"] = [{"kind": "LO", "price": 101_000, "qty": 700, "placed_at": "2026-10-06T10:00:00",
                   "auction": False}]
    it, _ = E.step_execution(ex, dict(snap), "MORNING", T("10:01"), "HOSE", 5_000, False)
    check("mode 2: HUỶ lệnh chờ cũ trước khi đặt lại (đặt lại mỗi 1')",
          any(i["kind"] == "CANCEL" and i["qty"] == 700 and i["price"] == 101_000 for i in it)
          and not any(o["price"] == 101_000 for o in ex["open"]), f"{it} open={ex['open']}")
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


def _deps(tmp, mkt, uni, msgs=None, dispatch=False, bot_stop=None, notifier=None, job_status=None,
          accounts=None):
    # chỉ tin ĐÃ đăng tới thời điểm hiện tại (không nhìn trước)
    return W.Deps(mkt, notifier or W.Notifier(dry=True), tmp, dispatch=dispatch,
                  messages=(lambda: [m for m in (msgs or []) if mkt.c.now is None or m["created_at"] <= mkt.c.now]),
                  accounts=accounts or [], universe=uni,
                  bot_stop_path=bot_stop or os.path.join(tmp, "BOT_STOP_absent"),
                  nav=lambda lab: (1_000_000_000, "2026-10-05T20:15"),
                  job_status=job_status or (lambda job: None), budget_s=1e9)


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
    # 1) BAL im lặng, điều tra hết giờ KHÔNG phán quyết ⇒ (a) GIỮ + cảnh báo lớn (không bán 50%)
    st, deps, tmp = scenario("bal_timeout", "BAL")
    c = st["cases"]["XYZ"]
    check("HNX −6% ⇒ room 4% ⇒ KHÔNG rút gọn", not c["compressed"])
    check("T0 = lần quét 10:00 (15'/lần)", c["t0"].endswith("10:00:00"), c["t0"])
    check("quá 20' ⇒ nguồn 'timeout' (≠ CHƯA RÕ của agent)", c["verdict"]["source"] == "timeout"
          and c["report_at"].endswith("10:20:00"), str(c.get("verdict")))
    check("hạn trả lời = báo cáo + 30'", c["reply_deadline"].endswith("10:50:00"))
    check("(a) im lặng BAL + timeout ⇒ GIỮ, không lệnh bán", c["decision"]["source"] == "default"
          and c["actions_default"]["SpaceX"] == E.HOLD and not c["execution"] and c["status"] == "HOLD",
          str(c.get("actions_default")))
    check("(a) báo cáo có cảnh báo lớn 'KHÔNG CÓ PHÁN QUYẾT'",
          any("KHÔNG CÓ PHÁN QUYẾT" in m["msg"] for m in deps.notifier.sent))
    lg = _log(tmp)
    check("VERDICT log + ca ghi nguồn + độ trễ", any(r["kind"] == "VERDICT" and r["verdict"]["source"] == "timeout"
                                                     and r["latency_min"] == 20.0 for r in lg)
          and c["verdict"]["latency_min"] == 20.0 and st["stats"]["verdicts"][0]["latency_min"] == 20.0)
    check("T0 báo Discord+Telegram+email, @owner", any(s["channel"] == "email" for s in deps.notifier.sent)
          and any("CỔNG GIÁ" in s["msg"] for s in deps.notifier.sent)
          and any(m["mention"] for m in st["outbox"] if "CỔNG GIÁ" in m["msg"]))
    check("mọi tin có nhãn [SHADOW]", all(s["msg"].startswith("[SHADOW]") for s in deps.notifier.sent))
    check("hộp thư đi: mọi tin đã gửi hết kênh", all(not m["left"] for m in st["outbox"]))
    n_trig = sum(1 for r in lg if r["kind"] == "TRIGGER")
    check("mỗi mã tối đa 1 lần/ngày (quét 10:15/10:30/... không mở lại)", n_trig == 1, str(n_trig))
    check("1 điều tra hết giờ ⇒ dừng dispatch tới hết ngày", "hết giờ" in (st.get("dispatch_halted") or ""))
    shutil.rmtree(tmp)

    # 1b) BAL + CHƯA RÕ DO AGENT ⇒ vẫn bán 50% sau hạn (chính sách user duyệt)
    st, deps, tmp = scenario("bal_unclear_agent", "BAL", "10:19", E.UNCLEAR)
    c = st["cases"]["XYZ"]
    check("agent CHƯA RÕ 10:19 ⇒ im lặng ⇒ bán 50% (target 500)", c["verdict"]["source"] == "agent"
          and c["decision"]["source"] == "default" and c["execution"]["SpaceX"]["target"] == 500,
          str(c.get("execution")))
    lg = _log(tmp)
    first_int = [r for r in lg if r["kind"] == "CUTLOSS_TICK" and r.get("intents")]
    check("không lệnh dự định nào trước hạn chót 10:49", first_int and first_int[0]["ts"] >= "2026-10-06T10:49",
          first_int[0]["ts"] if first_int else "none")
    check("(6) báo cáo hướng dẫn lệnh có tiền tố SHADOW + 'không có lệnh thật'",
          any("SHADOW BÁN 50% XYZ" in m["msg"] and "KHÔNG CÓ LỆNH THẬT" in m["msg"] for m in deps.notifier.sent))
    shutil.rmtree(tmp)

    # 2) BAL + GÃY (agent 10:05) + user GIỮ trước hạn ⇒ giữ; rồi BÁN ⇒ bán
    msgs = [{"id": 1, "is_bot": False, "content": "SHADOW GIỮ XYZ", "created_at": T("10:10")}]
    st, deps, tmp = scenario("bal_broken_hold", "BAL", "10:05", E.BROKEN, msgs=msgs, end="10:45")
    c = st["cases"]["XYZ"]
    check("phán quyết agent GÃY lúc 10:05", c["verdict"]["label"] == E.BROKEN and c["verdict"]["source"] == "agent"
          and c["report_at"].endswith("10:05:00"))
    check("mặc định GÃY = bán hết", c["actions_default"]["SpaceX"] == E.SELL_ALL)
    check("user GIỮ trước hạn ⇒ HOLD, không bán", c["decision"]["source"] == "user"
          and c["status"] == "HOLD" and not c["execution"], str(c.get("status")))
    shutil.rmtree(tmp)
    msgs2 = msgs + [{"id": 2, "is_bot": False, "content": "SHADOW BÁN XYZ", "created_at": T("10:40")}]
    st, deps, tmp = scenario("bal_hold_then_sell", "BAL", "10:05", E.BROKEN, msgs=msgs2, end="10:45")
    c = st["cases"]["XYZ"]
    check("ca HOLD vẫn nhận lệnh BÁN sau đó ⇒ bán hết", c["execution"].get("SpaceX", {}).get("target") == 1000
          and c["status"] in ("EXECUTING", "DONE"), str(c.get("execution")))
    shutil.rmtree(tmp)

    # 2b) user BÁN trước phán quyết ⇒ bán ngay; phán quyết đến sau KHÔNG đè trạng thái
    msgs3 = [{"id": 3, "is_bot": False, "content": "SHADOW BÁN XYZ", "created_at": T("10:02")}]
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
    msgs4 = [{"id": 4, "is_bot": False, "content": "SHADOW GIỮ XYZ", "created_at": T("10:40")}]
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
    W.dispatch_investigation = lambda case, cmd, dry=False, **kw: (calls.append(1), (None, "rc=2: boom"))[1]
    try:
        st, deps, tmp = scenario("dispatch_fail", "BAL", dispatch=True, end="10:25")
    finally:
        W.dispatch_investigation = orig
    c = st["cases"]["XYZ"]
    check("dispatch lỗi ⇒ gọi đúng 1 lần", len(calls) == 1, str(len(calls)))
    t0m = [m["msg"] for m in deps.notifier.sent if "CỔNG GIÁ" in m["msg"]]
    check("(2) dispatch lỗi ⇒ tin T0 nói KHÔNG CÓ ĐIỀU TRA + lỗi thật, KHÔNG nói 'đang điều tra'",
          t0m and "KHÔNG CÓ ĐIỀU TRA" in t0m[0] and "rc=2: boom" in t0m[0] and "đang điều tra" not in t0m[0],
          t0m[0] if t0m else "none")
    check("(2)+(a) dispatch lỗi ⇒ nguồn 'no_dispatch', mặc định GIỮ", c["verdict"]["source"] == "no_dispatch"
          and c["actions_default"]["SpaceX"] == E.HOLD)
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
    hook = (lambda t: _verdict(tmp, "XYZ", E.BROKEN) if t == T("09:20") else None)
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


# ================================================================ B2. r2 — 7 mục chặn + 4 mặc định an toàn
class MultiMarket(FakeMarket):
    """Giá riêng từng mã (FakeMarket dùng chung 1 đường giá)."""

    def __init__(self, clock, by, exch="HNX", vni=(1000.0, 1000.0), quote_err=(), ref=100_000):
        super().__init__(clock, {}, ref=ref, exch=exch, vni=vni)
        self.by, self.quote_err = by, set(quote_err)

    def quote(self, sym):
        if sym in self.quote_err:
            return {"error": "HTTPError 502"}
        self.prices = self.by.get(sym, {"09:15": self.ref})
        return super().quote(sym)

    def bars(self, sym, day, index=False):
        self.prices = self.by.get(sym, {"09:15": self.ref})
        return super().bars(sym, day, index)


def _uni_multi(qtys, **extra):
    return {tk: {"holdings": {"SpaceX": {"qty": q, "sellable": q, "cost": 110_000, "book": "BAL",
                                         "account_id": "A1", **extra}}, "buys": [], "watch": False}
            for tk, q in qtys.items()}


def _write_stub(d):
    rec = os.path.join(d, "rec")
    stub = os.path.join(d, "dispatch.sh")
    with open(stub, "w") as f:
        f.write(f"""#!/bin/bash
# stub: mô phỏng parser cờ + 2 chặn định tuyến của mike/bin/dispatch.sh thật
printf '%s\\0' "$@" > "{rec}.argv"; printf '%s' "${{DISPATCH_FROM:-Mike}}" > "{rec}.from"
id="$1"; shift 2
from="${{DISPATCH_FROM:-Mike}}"
while [ $# -gt 0 ]; do
  case "$1" in
    --bg) ;;
    --thread|--timeout|--retries|--model|--effort) [ -n "$2" ] || exit 1; shift ;;
    *) echo "ERROR: unknown argument '$1'" >&2; exit 1 ;;
  esac
  shift
done
if [ "$from" = "$id" ]; then echo "ERROR: self-dispatch blocked ($from -> $id)." >&2; exit 2; fi
if [ "$id" = "Mike" ] && [ "$from" != "user" ]; then exit 2; fi
[ -n "$STUB_SLEEP" ] && sleep "$STUB_SLEEP"
echo "DISPATCHED $id (job=${{id}}_20261006_100000 pid=1) → log: x"
""")
    os.chmod(stub, 0o755)
    return stub, rec


def _drive_multi(tmp, mkt, deps, start, end, day="2026-10-06", hook=None):
    return _drive(tmp, mkt, deps, start, end, day=day, hook=hook)


def test_r2():
    import fcntl
    import re
    case0 = {"ticker": "XYZ", "trigger": {"reason": "r", "ret": -0.06, "vni_ret": 0.0},
             "t0": "2026-10-06T10:00:00", "holdings": {}, "compressed": False}

    # ---- (1) argv THẬT vào stub dispatch.sh + đối chiếu dispatch.sh thật
    sd = tempfile.mkdtemp(prefix="ipw_stub_")
    stub, rec = _write_stub(sd)
    job, prompt = W.dispatch_investigation(case0, "CMD", dispatch_bin=stub)
    check("(1) dispatch qua stub (argv thật) ⇒ rc 0, nhận job", job == "Taylor_20261006_100000", f"{job} {prompt[:200]}")
    argv = open(rec + ".argv").read().split("\0")[:-1]
    check("(1) argv stub nhận = dispatch_argv() thật", argv == W.dispatch_argv(prompt, False, stub)[1:])
    check("(1) prompt điều tra CẤM đặt/huỷ lệnh + sửa plan (ghim, arch-review r2 F6)",
          "KHÔNG đặt/huỷ lệnh" in prompt and "KHÔNG sửa plan" in prompt)
    check("(1) dispatch gửi về đúng topic Trading Daily (--thread trading_daily)",
          "--thread" in argv and argv[argv.index("--thread") + 1] == "trading_daily", str(argv))
    check("(1) DISPATCH_FROM = intraday_watch (≠ Taylor ⇒ không bị chặn self-dispatch)",
          open(rec + ".from").read() == "intraday_watch")
    real = open(W.DISPATCH).read()
    flags = [a for a in argv if a.startswith("--")]
    check("(1) mọi cờ trong argv đều có trong parser của dispatch.sh THẬT",
          all(re.search(rf"^\s*{re.escape(f)}\)", real, re.M) for f in flags), str(flags))
    check("(1) dispatch.sh thật vẫn có chặn self-dispatch (stub mô phỏng đúng thứ đang tồn tại)",
          'if [ "$from" = "$id" ]' in real)
    check("(1) DISPATCH_FROM_ID không phải agent (không auto-callback) và không phải Mike/user/Taylor",
          not os.path.isdir(os.path.join(W.MIKE, "agents", W.DISPATCH_FROM_ID))
          and W.DISPATCH_FROM_ID not in ("Mike", "user", "Taylor"))
    a = W.dispatch_argv("p", False)
    check("(4) --retries 0 + --timeout = hạn điều tra + 5' (25' thường / 15' rút gọn)",
          a[a.index("--retries") + 1] == "0" and a[a.index("--timeout") + 1] == "1500"
          and W.dispatch_argv("p", True)[W.dispatch_argv("p", True).index("--timeout") + 1] == "900")
    old = W.DISPATCH_FROM_ID
    W.DISPATCH_FROM_ID = "Taylor"
    try:
        job, info = W.dispatch_investigation(case0, "CMD", dispatch_bin=stub)
    finally:
        W.DISPATCH_FROM_ID = old
    check("(1) đối chứng: DISPATCH_FROM=Taylor ⇒ stub chặn rc=2 ⇒ None + lỗi thật",
          job is None and "rc=2" in info and "self-dispatch" in info, f"{job} {info}")
    os.environ["STUB_SLEEP"] = "3"
    old_t = W.DISPATCH_SUBPROC_TIMEOUT
    W.DISPATCH_SUBPROC_TIMEOUT = 1
    try:
        job, info = W.dispatch_investigation(case0, "CMD", dispatch_bin=stub)
    finally:
        W.DISPATCH_SUBPROC_TIMEOUT = old_t
        del os.environ["STUB_SLEEP"]
    check("(2) TimeoutExpired được bắt ⇒ None + lý do", job is None and "TimeoutExpired" in info, str(info))
    job, info = W.dispatch_investigation(case0, "CMD", dispatch_bin=os.path.join(sd, "missing.sh"))
    check("(2) OSError (không có file) được bắt ⇒ None", job is None and "không chạy được" in info, str(info))

    # end-to-end: scenario dispatch thật qua stub ⇒ T0 nói đang điều tra + job
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, _uni("BAL"), dispatch=True)
    deps.dispatch_bin = stub
    st = _drive(tmp, mkt, deps, "09:15", "10:01")
    t0m = [m["msg"] for m in deps.notifier.sent if "CỔNG GIÁ" in m["msg"]]
    check("(1) e2e: T0 nói 'đang điều tra' kèm job từ dispatch", t0m and "job Taylor_20261006_100000" in t0m[0])
    shutil.rmtree(tmp)

    # job điều tra chết sớm ⇒ báo ngay + dừng dispatch
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, _uni("BAL"), dispatch=True, job_status=lambda j: "failed")
    deps.dispatch_bin = stub
    st = _drive(tmp, mkt, deps, "09:15", "10:25")
    c = st["cases"]["XYZ"]
    check("(2) job 'failed' trước hạn ⇒ cảnh báo ngay (10:01) + dừng dispatch hôm nay",
          any(r["kind"] == "JOB_DEAD" and r["ts"] == "2026-10-06T10:01:00" for r in _log(tmp))
          and any("kết thúc 'failed'" in m["msg"] for m in deps.notifier.sent) and st.get("dispatch_halted"))
    check("(a) job chết ⇒ hết hạn nguồn 'timeout' ⇒ GIỮ", c["verdict"]["source"] == "timeout"
          and c["actions_default"]["SpaceX"] == E.HOLD)
    shutil.rmtree(tmp)
    shutil.rmtree(sd)

    # ---- (3) kill giữa lúc gửi tin T0 ⇒ lượt sau gửi nốt; dispatch không lặp
    class KillOnce(W.Notifier):
        def __init__(self):
            super().__init__(dry=True)
            self.killed = False

        def send(self, msg, *a, **k):
            if not self.killed and "CỔNG GIÁ" in msg:
                self.killed = True
                raise KeyboardInterrupt("kill giả giữa lúc gửi")
            return super().send(msg, *a, **k)
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    kn = KillOnce()
    deps = _deps(tmp, mkt, _uni("BAL"), notifier=kn)
    _drive(tmp, mkt, deps, "09:15", "09:59")
    clock.now = T("10:00")
    try:
        W.run_tick(T("10:00"), deps)
        killed = False
    except KeyboardInterrupt:
        killed = True
    clock.now = T("10:01")
    W.run_tick(T("10:01"), deps)
    st = W._read_json(W.state_path(tmp, dt.date(2026, 10, 6)))
    check("(3) kill giữa gửi T0 ⇒ lượt sau GỬI tin T0 (không mất)", killed and
          sum(1 for m in kn.sent if "CỔNG GIÁ" in m["msg"]) == 3, str([m["channel"] for m in kn.sent]))
    check("(3) dispatch không lặp sau kill", sum(1 for r in _log(tmp) if r["kind"] == "DISPATCH") == 1)
    shutil.rmtree(tmp)

    # kill giữa lúc gửi báo cáo PHÁN QUYẾT (trạng thái AWAITING_REPLY đã lên đĩa) ⇒ lượt sau gửi nốt
    class KillVerdict(KillOnce):
        def send(self, msg, *a, **k):
            if not self.killed and "PHÁN QUYẾT" in msg:
                self.killed = True
                raise KeyboardInterrupt("kill giả giữa lúc gửi phán quyết")
            return W.Notifier.send(self, msg, *a, **k)
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    kv = KillVerdict()
    deps = _deps(tmp, mkt, _uni("BAL"), notifier=kv)
    killed = False
    t = T("09:15")
    while t <= T("10:12"):
        clock.now = t
        if t == T("10:05"):
            _verdict(tmp, "XYZ", E.BROKEN)
        try:
            W.run_tick(t, deps)
        except KeyboardInterrupt:
            killed = True
        t += dt.timedelta(minutes=1)
    check("(3) kill giữa gửi PHÁN QUYẾT ⇒ lượt sau GỬI nốt (outbox bền)", killed and
          sum(1 for m in kv.sent if "PHÁN QUYẾT" in m["msg"]) == 3, str(len(kv.sent)))
    shutil.rmtree(tmp)

    # kill giữa lúc dispatch ⇒ không dispatch lại, T0 nói không xác nhận được
    calls = []

    def _kill_dispatch(case, cmd, dry=False, **kw):
        calls.append(1)
        raise KeyboardInterrupt("kill giả giữa dispatch")
    orig = W.dispatch_investigation
    W.dispatch_investigation = _kill_dispatch
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    try:
        clock = Clock()
        mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
        deps = _deps(tmp, mkt, _uni("BAL"), dispatch=True)
        _drive(tmp, mkt, deps, "09:15", "09:59")
        clock.now = T("10:00")
        try:
            W.run_tick(T("10:00"), deps)
        except KeyboardInterrupt:
            pass
        st = _drive(tmp, mkt, deps, "10:01", "10:21")
    finally:
        W.dispatch_investigation = orig
    c = st["cases"]["XYZ"]
    t0m = [m["msg"] for m in deps.notifier.sent if "CỔNG GIÁ" in m["msg"]]
    check("(3) kill giữa dispatch ⇒ KHÔNG dispatch lại (at-most-once)", len(calls) == 1, str(len(calls)))
    check("(3) …và tin T0 vẫn đi, nói 'không xác nhận được job'", t0m and "không xác nhận được job" in t0m[0])
    check("(3) …hết hạn ⇒ nguồn no_dispatch ⇒ GIỮ", c["verdict"]["source"] == "no_dispatch"
          and c["actions_default"]["SpaceX"] == E.HOLD)
    shutil.rmtree(tmp)

    # hết ngân sách thời gian ⇒ để lượt sau
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, _uni("BAL"))
    _drive(tmp, mkt, deps, "09:15", "09:59")
    deps.budget_s = -1
    clock.now = T("10:00")
    W.run_tick(T("10:00"), deps)
    st = W._read_json(W.state_path(tmp, dt.date(2026, 10, 6)))
    b_ok = st["cases"]["XYZ"].get("need_dispatch") and not deps.notifier.sent
    deps.budget_s = 1e9
    clock.now = T("10:01")
    W.run_tick(T("10:01"), deps)
    check("ngân sách hết ⇒ không tác động ngoài; lượt sau làm nốt (dispatch + T0)",
          b_ok and any("CỔNG GIÁ" in m["msg"] for m in deps.notifier.sent))
    shutil.rmtree(tmp)

    # ---- (4) cảnh báo gộp cả thị trường + trần
    def multi(by, qtys, end="10:02", exch="HNX", vni=(1000.0, 1000.0), quote_err=(), dispatch=False, ref=100_000):
        tmp = tempfile.mkdtemp(prefix="ipw_sc_")
        clock = Clock()
        mkt = MultiMarket(clock, by, exch=exch, vni=vni, quote_err=quote_err, ref=ref)
        deps = _deps(tmp, mkt, _uni_multi(qtys), dispatch=dispatch)
        st = _drive(tmp, mkt, deps, "09:15", end)
        return st, deps, tmp, mkt
    down = {"09:15": 100_000, "09:59": 94_000}
    st, deps, tmp, mkt = multi({"AAA": down, "BBB": down, "CCC": down}, {"AAA": 1000, "BBB": 1000, "CCC": 1000},
                               end="10:31")
    check("(4) biến động chung kéo dài 3 lượt quét ⇒ vẫn chỉ 1 cảnh báo gộp",
          sum(1 for m in st["outbox"] if "CẢ THỊ TRƯỜNG" in m["msg"]) == 1
          and sum(1 for r in _log(tmp) if r["kind"] == "MARKET_WIDE") == 3)
    shutil.rmtree(tmp)
    st, deps, tmp, mkt = multi({"AAA": down, "BBB": down, "CCC": down}, {"AAA": 1000, "BBB": 1000, "CCC": 1000})
    lg = _log(tmp)
    check("(4) 3 mã cùng kích hoạt ⇒ KHÔNG mở ca, KHÔNG dispatch", not st["cases"]
          and not any(r["kind"] == "DISPATCH" for r in lg))
    check("(4) …MỘT cảnh báo gộp 'CẢ THỊ TRƯỜNG' có @mention", sum(1 for m in st["outbox"] if "CẢ THỊ TRƯỜNG" in m["msg"]
                                                                and m["mention"]) == 1)
    deps.universe = _uni_multi({"AAA": 1000, "BBB": 1000, "CCC": 1000})
    mkt.by = {"AAA": down, "BBB": {"09:15": 100_000}, "CCC": {"09:15": 100_000}}
    st = _drive(tmp, mkt, deps, "10:03", "10:16")
    check("(4) lượt sau chỉ còn AAA (không còn chung) ⇒ mở ca riêng AAA", list(st["cases"]) == ["AAA"]
          and st["cases"]["AAA"]["t0"].endswith("10:15:00"), str(list(st["cases"])))
    check("(4) không lặp cảnh báo gộp", sum(1 for m in st["outbox"] if "CẢ THỊ TRƯỜNG" in m["msg"]) == 1)
    shutil.rmtree(tmp)

    st, deps, tmp, _ = multi({"AAA": down}, {"AAA": 1000}, vni=(None, 1000.0))
    check("(4) thiếu VNINDEX + 1 mã ⇒ gộp (không dispatch) + cảnh báo sức khoẻ vnindex", not st["cases"]
          and any("VNINDEX" in m["msg"] and "CẢ THỊ TRƯỜNG" in m["msg"] for m in st["outbox"])
          and any("SỨC KHOẺ" in m["msg"] and "vnindex" in m["msg"] for m in st["outbox"]))
    shutil.rmtree(tmp)
    # 08/10: quét 09:15:01 chưa có bar VNINDEX nào (DNSE phát bar sau khi phút đóng) ⇒ KHÔNG cảnh báo sức khoẻ
    for pend, vni, alert, label in ((True, (None, 1000.0), False, "đầu phiên chờ bar"),
                                    (True, (None, None), True, "đầu phiên nhưng thiếu cả ref"),
                                    (False, (None, 1000.0), True, "ngoài đầu phiên")):
        tmp = tempfile.mkdtemp(prefix="ipw_sc_")
        mkt = MultiMarket(Clock(), {"AAA": {"09:15": 100_000}}, exch="HNX", vni=vni, quote_err=(), ref=100_000)
        mkt.vni_pending_open = pend
        deps = _deps(tmp, mkt, _uni_multi({"AAA": 1000}), dispatch=False)
        st = _drive(tmp, mkt, deps, "09:15", "09:15")
        got = any("SỨC KHOẺ" in m["msg"] and "vnindex" in m["msg"] for m in st["outbox"])
        check(f"VNINDEX {label} ⇒ {'CÓ' if alert else 'KHÔNG'} cảnh báo sức khoẻ", got == alert,
              str([m["msg"][:80] for m in st["outbox"]]))
        if not alert:
            check(f"VNINDEX {label} ⇒ ghi log VNI_PENDING_OPEN",
                  any(r["kind"] == "VNI_PENDING_OPEN" for r in _log(tmp)))
        shutil.rmtree(tmp)
    flo = {"09:15": 100_000, "09:59": 93_000}
    st, deps, tmp, _ = multi({"AAA": flo, "BBB": flo}, {"AAA": 1000, "BBB": 1000}, exch="HOSE", vni=(940.0, 1000.0))
    check("(4) 2 mã chạm sàn ⇒ gộp", not st["cases"] and any("chạm sàn" in m["msg"] for m in st["outbox"]))
    shutil.rmtree(tmp)

    old = W.MAX_DISPATCH_PER_SCAN
    W.MAX_DISPATCH_PER_SCAN = 1
    try:
        st, deps, tmp, _ = multi({"AAA": down, "BBB": down}, {"AAA": 1000, "BBB": 5000})
    finally:
        W.MAX_DISPATCH_PER_SCAN = old
    inv = {k: c["investigation"] for k, c in st["cases"].items()}
    check("(4) trần/lượt quét ⇒ ưu tiên vị thế lớn (BBB), AAA bị chặn + T0 nói rõ",
          inv["BBB"].get("job") == "DRY" and "lượt quét" in (inv["AAA"].get("skipped") or "")
          and any("AAA" in m["msg"] and "KHÔNG CÓ ĐIỀU TRA" in m["msg"] for m in deps.notifier.sent), str(inv))
    shutil.rmtree(tmp)
    old = (W.MAX_DISPATCH_PER_DAY, W.STOP_DISPATCH_AFTER_TIMEOUT)
    W.MAX_DISPATCH_PER_DAY, W.STOP_DISPATCH_AFTER_TIMEOUT = 1, False
    try:
        st, deps, tmp, _ = multi({"AAA": down, "BBB": {"09:15": 100_000, "10:14": 94_000}},
                                 {"AAA": 1000, "BBB": 1000}, end="10:16")
    finally:
        W.MAX_DISPATCH_PER_DAY, W.STOP_DISPATCH_AFTER_TIMEOUT = old
    check("(4) trần/ngày ⇒ mã thứ 2 không dispatch", st["cases"]["AAA"]["investigation"].get("job") == "DRY"
          and "ngày" in (st["cases"]["BBB"]["investigation"].get("skipped") or ""))
    shutil.rmtree(tmp)
    st, deps, tmp, _ = multi({"AAA": down, "BBB": {"09:15": 100_000, "10:29": 94_000}},
                             {"AAA": 1000, "BBB": 1000}, end="10:31")
    check("(4) điều tra AAA hết giờ 10:20 ⇒ BBB (10:30) không dispatch — 'DỪNG'",
          "DỪNG" in (st["cases"]["BBB"]["investigation"].get("skipped") or ""), str(st["cases"]["BBB"].get("investigation")))
    shutil.rmtree(tmp)

    # ---- (5) sức khoẻ
    st, deps, tmp, _ = multi({"AAA": down}, {"AAA": 1000, "BBB": 1, "CCC": 1, "DDD": 1},
                             quote_err=("BBB", "CCC", "DDD"))
    check("(5) lỗi giá 3/4 > 50% ⇒ cảnh báo sức khoẻ 'quote'",
          any("SỨC KHOẺ" in m["msg"] and "3/4" in m["msg"] for m in st["outbox"]))
    shutil.rmtree(tmp)

    def boom():
        raise OSError("ccdb connection refused")
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, _uni("BAL"))
    deps.messages = boom
    st = _drive(tmp, mkt, deps, "09:15", "10:40")
    n_cc = sum(1 for m in st["outbox"] if "SỨC KHOẺ" in m["msg"] and "ccdb" in m["msg"])
    check("(5) ccdb không đọc được ⇒ cảnh báo (tối đa 1 lần/60')", n_cc == 1 and
          st["stats"]["reply_read_errors"] >= 40, f"n={n_cc} err={st['stats']['reply_read_errors']}")
    shutil.rmtree(tmp)

    class DiscordDown(W.Notifier):
        def send(self, msg, channels=("discord", "telegram"), subject=None, mention=False):
            res = super().send(msg, channels, subject, mention)
            if "discord" in res:
                res["discord"] = (False, "HTTP 500")
                self.sent[-len(channels) + list(channels).index("discord")]["ok"] = False
            return res
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, _uni("BAL"), notifier=DiscordDown(dry=True))
    st = _drive(tmp, mkt, deps, "09:15", "10:06")
    t0 = [m for m in st["outbox"] if "CỔNG GIÁ" in m["msg"]][0]
    check("(5) kết quả Notifier được KIỂM: kênh lỗi giữ lại, thử lại tối đa N lượt",
          t0["left"] == ["discord"] and t0["attempts"] == W.NOTIFY_MAX_ATTEMPTS, str(t0))
    check("(5) bỏ cuộc kênh discord ⇒ cảnh báo qua telegram", any(
        m["channel"] == "telegram" and "kênh discord lỗi" in m["msg"] for m in deps.notifier.sent))
    check("(5) đếm lỗi gửi tin", st["stats"]["notify_fail"] >= W.NOTIFY_MAX_ATTEMPTS)
    shutil.rmtree(tmp)

    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    n = W.Notifier(dry=True)

    def bad_factory():
        raise RuntimeError("DNSE token hỏng")
    rcs = []
    for _ in range(2):
        try:
            W.main(["run", "--state-dir", tmp], market_factory=bad_factory, notifier=n)
        except SystemExit as e:
            rcs.append(e.code)
    check("(5) LiveMarket khởi tạo lỗi ⇒ exit 1 + cảnh báo 1 lần/ngày (2 lần chạy ⇒ 1 cảnh báo)",
          rcs == [1, 1] and len(n.sent) == 2 and "DNSE token hỏng" in n.sent[0]["msg"]
          and "(init)" in n.sent[0]["msg"], f"{rcs} {[m['msg'][:80] for m in n.sent]}")
    orig_rt = W.run_tick

    def bad_tick(now, deps):
        raise ValueError("bug giả")
    W.run_tick = bad_tick
    n2 = W.Notifier(dry=True)
    raised = 0
    try:
        for _ in range(2):
            try:
                W.main(["run", "--state-dir", tmp], market_factory=lambda: FakeMarket(Clock(), {}), notifier=n2)
            except ValueError:
                raised += 1
    finally:
        W.run_tick = orig_rt
    check("(5) crash cấp cao nhất ⇒ re-raise + cảnh báo 1 lần/ngày", raised == 2 and len(n2.sent) == 2
          and "(crash)" in n2.sent[0]["msg"] and "bug giả" in n2.sent[0]["msg"])
    shutil.rmtree(tmp)

    # positions lỗi trong build_universe ⇒ cảnh báo; (b) excluded/restricted ⇒ no_auto_sell; book map
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    pd_, dd_ = os.path.join(tmp, "plans"), os.path.join(tmp, "disc")
    os.makedirs(pd_)
    os.makedirs(dd_)
    W._atomic_json(os.path.join(pd_, "bootstrap_book_snapshot_SpaceX_20260804.json"),
                   {"positions": [{"ticker": "ACB", "book": "PARK"}]})
    W._atomic_json(os.path.join(pd_, "plan_SpaceX_2026-10-01.json"), {"orders": [
        {"ticker": "BID", "side": "buy", "book": "custom30V_parking"},
        {"ticker": "FPT", "side": "buy", "book": "BAL"},
        {"ticker": "OLD", "side": "sell", "book": "legacy_orphan"}]})
    W._atomic_json(os.path.join(pd_, "park_add_SpaceX_2026-10-02.json"),
                   {"orders": [{"ticker": "MBB", "side": "buy", "book": "PARK"}]})
    W._atomic_json(os.path.join(pd_, "jit_unpark_SpaceX_2026-10-03.json"),
                   {"orders": [{"ticker": "VCB", "side": "sell", "book": "PARK"},
                               {"ticker": "FPT", "side": "sell", "book": "PARK"}]})
    bk = W.classify_books("SpaceX", dt.date(2026, 10, 6), ["DGC"], [], plans_dir=pd_)
    check("book: custom30V_parking / PARK (plan, park_add, jit_unpark, bootstrap) ⇒ CUSTOM30V",
          all(bk.get(t) == "CUSTOM30V" for t in ("ACB", "BID", "MBB", "VCB")), str(bk))
    check("book: lệnh MUA thắng lệnh bán (FPT=BAL); legacy_orphan ⇒ không gán; excluded ⇒ DISCRETIONARY",
          bk.get("FPT") == "BAL" and "OLD" not in bk and bk.get("DGC") == E.DISCRETIONARY, str(bk))
    W._atomic_json(os.path.join(tmp, "restricted.json"), {"tickers": ["AAA"]})

    class PosMkt(FakeMarket):
        def positions(self, account_id):
            if account_id == "BAD":
                raise RuntimeError("401 token")
            return {"DGC": {"qty": 100, "sellable": 100}, "AAA": {"qty": 100, "sellable": 100},
                    "BID": {"qty": 100, "sellable": 100}}
    old = (W.PLANS_DIR, W.DISC_DIR)
    W.PLANS_DIR, W.DISC_DIR = pd_, dd_
    try:
        errs = []
        uni = W.build_universe(dt.date(2026, 10, 6), PosMkt(Clock(), {}),
                               [{"label": "ZaloPay", "account_id": "Z1", "excluded": ["DGC"]},
                                {"label": "SpaceX", "account_id": "BAD", "excluded": []}], tmp, errors=errs)
    finally:
        W.PLANS_DIR, W.DISC_DIR = old
    h = {t: u["holdings"].get("ZaloPay", {}) for t, u in uni.items()}
    check("(b) excluded_tickers ⇒ no_auto_sell; restricted.json ⇒ no_auto_sell; mã thường ⇒ None",
          "excluded" in (h["DGC"].get("no_auto_sell") or "") and "restricted" in (h["AAA"].get("no_auto_sell") or "")
          and h["BID"].get("no_auto_sell") is None, str(h))
    check("(5) vị thế 1 TK lỗi ⇒ errors nhận mô tả (driver cảnh báo)", errs and "SpaceX" in errs[0], str(errs))
    shutil.rmtree(tmp)

    # (b) no_auto_sell: agent GÃY + user SHADOW BÁN ⇒ vẫn KHÔNG có lệnh
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 94_000}, exch="HNX")
    uni = _uni("BAL")
    uni["XYZ"]["holdings"]["SpaceX"]["no_auto_sell"] = "excluded_tickers SpaceX"
    msgs = [{"id": 7, "is_bot": False, "content": "SHADOW BÁN XYZ", "created_at": T("10:10")}]
    deps = _deps(tmp, mkt, uni, msgs=msgs)
    st = _drive(tmp, mkt, deps, "09:15", "10:40",
                hook=lambda t: _verdict(tmp, "XYZ", E.BROKEN) if t == T("10:05") else None)
    c = st["cases"]["XYZ"]
    check("(b) excluded + GÃY ⇒ mặc định GIỮ; user BÁN ⇒ KHÔNG lệnh, ghi NO_AUTO_SELL",
          c["actions_default"]["SpaceX"] == E.HOLD and not c["execution"]
          and any(r["kind"] == "NO_AUTO_SELL" for r in _log(tmp))
          and any("KHÔNG đặt lệnh" in m["msg"] for m in deps.notifier.sent), str(c.get("execution")))
    check("(b) dispatch điều tra VẪN chạy cho mã excluded", c["investigation"].get("job") == "DRY")
    shutil.rmtree(tmp)

    # ---- (c) kích hoạt sau 14:00 ⇒ quyết định phiên sau; 08:30 nhắc; mặc định từ 09:15
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "14:04": 94_000}, exch="HNX")
    deps = _deps(tmp, mkt, _uni("BAL"))
    st = _drive(tmp, mkt, deps, "09:15", "14:59",
                hook=lambda t: _verdict(tmp, "XYZ", E.UNCLEAR) if t == T("14:10") else None)
    c = st["cases"]["XYZ"]
    check("(c) T0 14:15 (≥14:00) ⇒ ca 'late', hạn = 09:15 phiên sau, không lệnh trong ngày",
          c["late"] and c["reply_deferred"] and c["reply_deadline"] == "2026-10-07T09:15:00"
          and not c["execution"], f"{c.get('t0')} {c.get('reply_deadline')}")
    check("(c) T0 báo 'chỉ báo + điều tra … 09:15 phiên sau'",
          any("kích hoạt sau 14:00" in m["msg"] for m in deps.notifier.sent))
    sent0 = len(deps.notifier.sent)
    st2 = _drive(tmp, mkt, deps, "08:20", "09:20", day="2026-10-07")
    rem = [m for m in deps.notifier.sent[sent0:] if "NHẮC 08:30" in m["msg"]]
    lg = _log(tmp, "2026-10-07")
    dap = [r for r in lg if r["kind"] == "DEFAULT_APPLIED"]
    check("(c) 08:30 phiên sau nhắc đúng 1 lần (3 kênh mặc định 2)", len(rem) == 2
          and rem[0]["msg"].count("SHADOW") >= 3, str(len(rem)))
    check("(c) mặc định áp đúng 09:15 phiên sau (không sớm hơn)", dap and dap[0]["ts"] == "2026-10-07T09:15:00",
          str([r["ts"] for r in dap]))
    check("(c) …rồi bán 50% (agent CHƯA RÕ, BAL)", st2["cases"]["XYZ"]["execution"]["SpaceX"]["target"] == 500)
    shutil.rmtree(tmp)
    old = W.NO_EOD_DEFAULT_AFTER
    W.NO_EOD_DEFAULT_AFTER = dt.time(14, 40)
    try:
        rd_l, df_l = W._reply_deadline({"late": True, "compressed": True, "t0": "2026-10-06T14:00:00"}, T("14:01"))
        rd_n, df_n = W._reply_deadline({"late": False, "compressed": True, "t0": "2026-10-06T13:45:00"}, T("14:01"))
    finally:
        W.NO_EOD_DEFAULT_AFTER = old
    check("(c) cờ 'late' tự hoãn (độc lập với luật 14:15): late ⇒ 09:15 phiên sau, không late ⇒ +15'",
          df_l and rd_l == T("09:15", "2026-10-07") and not df_n and rd_n == T("14:16"), f"{rd_l} {rd_n}")
    st, deps, tmp = scenario("deadline_after_1415", "BAL", "13:50", E.BROKEN,
                             prices={"09:15": 100_000, "13:44": 94_000}, end="14:59")
    c = st["cases"]["XYZ"]
    check("(c) T0 13:45, báo cáo 13:50 ⇒ hạn 14:20 > 14:15 ⇒ hoãn 09:15 phiên sau, không bán trong ngày",
          c["reply_deferred"] and c["reply_deadline"] == "2026-10-07T09:15:00" and not c["execution"],
          f"{c.get('reply_deadline')} {c.get('execution')}")
    shutil.rmtree(tmp)

    # (6) lệnh trần "BÁN XYZ" (không tiền tố SHADOW) KHÔNG được hiểu trong shadow
    st, deps, tmp = scenario("plain_reply", "BAL", "10:05", E.BROKEN, end="10:40",
                             msgs=[{"id": 5, "is_bot": False, "content": "GIỮ XYZ", "created_at": T("10:08")}])
    c = st["cases"]["XYZ"]
    check("(6) 'GIỮ XYZ' trần bị bỏ qua ⇒ mặc định GÃY bán hết vẫn áp", c["decision"]["source"] == "default"
          and c["execution"]["SpaceX"]["target"] == 1000, str(c.get("decision")))
    shutil.rmtree(tmp)

    # ---- (d) ngưỡng tương đối: log song song, không hành động
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    clock = Clock()
    mkt = FakeMarket(clock, {"09:15": 100_000, "09:59": 96_500}, exch="HOSE")
    deps = _deps(tmp, mkt, _uni("BAL"))
    st = _drive(tmp, mkt, deps, "09:15", "10:01")
    alt = [r for r in _log(tmp) if r["kind"] == "ALT_THRESHOLD"]
    check("(d) HOSE −3,5%: log ALT (rel kích hoạt, hiện hành không), KHÔNG mở ca",
          alt and alt[-1]["rows"][0]["hit_rel"] and not alt[-1]["rows"][0]["hit_cur"] and not st["cases"]
          and st["stats"]["alt_rel"] == ["XYZ"] and st["stats"]["alt_cur"] == [])
    shutil.rmtree(tmp)

    # ---- tóm tắt cuối ngày (5) + carry outbox
    st, deps, tmp = scenario("eod", "BAL", "10:05", E.BROKEN, end="14:55")
    summ = [m for m in deps.notifier.sent if "Tóm tắt SHADOW" in m["msg"]]
    check("(5) tóm tắt cuối ngày 1 dòng, đúng 1 lần, có số kích hoạt/điều tra/phán quyết",
          len(summ) == 1 and "1 kích hoạt" in summ[0]["msg"] and "phán quyết agent 1" in summ[0]["msg"],
          summ[0]["msg"] if summ else "none")
    shutil.rmtree(tmp)
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    W._atomic_json(W.state_path(tmp, dt.date(2026, 10, 6)), {"date": "2026-10-06", "cases": {}, "outbox": [
        {"id": 1, "msg": "x", "left": ["discord"], "attempts": 1, "mention": False},
        {"id": 2, "msg": "y", "left": [], "attempts": 1, "mention": False}]})
    st = W.load_state(tmp, dt.date(2026, 10, 7))
    check("tin chưa gửi xong phiên trước được mang sang (không mất qua đêm)", [m["id"] for m in st["outbox"]] == [1])
    shutil.rmtree(tmp)

    # ---- đột biến reviewer thấy SỐNG ở r1
    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    deps = _deps(tmp, FakeMarket(Clock(), {}), {})
    os.makedirs(tmp, exist_ok=True)
    with open(os.path.join(tmp, ".lock"), "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX | fcntl.LOCK_NB)
        r = W.run_tick(T("10:00"), deps)
    check("flock: lượt khác đang giữ khoá ⇒ bỏ qua", r.get("skipped") == "lượt trước còn chạy", str(r))
    shutil.rmtree(tmp)

    class RC:
        def positions(self, acc):
            return {"positions": [
                {"accountNo": "A1", "symbol": "XYZ", "openQuantity": 1000, "tradeQuantity": 1000, "costPrice": 100_000},
                {"accountNo": "A2", "symbol": "XYZ", "openQuantity": 500, "tradeQuantity": 500, "costPrice": 90_000},
                {"accountNo": "A2", "symbol": "QQQ", "openQuantity": 300, "tradeQuantity": 300, "costPrice": 9_000}]}
    lm = W.LiveMarket.__new__(W.LiveMarket)
    lm._q, lm._bars, lm._pos = {}, {}, {}
    lm.ro = W.ReadOnlyDNSE(RC())
    pos = lm.positions("A1")
    check("§12: LiveMarket.positions lọc accountNo trước mọi phép tính",
          set(pos) == {"XYZ"} and pos["XYZ"]["qty"] == 1000 and pos["XYZ"]["cost"] == 100_000, str(pos))

    # 07/10: DNSE cache /price/ohlc theo URL ⇒ `to` phải đổi theo phút; bar VNINDEX cũ ⇒ None
    class OC:
        def __init__(self, last_hm):
            self.last_hm, self.tos = last_hm, []

        def ohlc(self, symbol, resolution="1D", bar_type="stock", **q):
            self.tos.append(q["to"])
            d = dt.datetime.fromtimestamp(q["from"], W._ICT).date()
            if resolution == "1D":
                t = dt.datetime.combine(d - dt.timedelta(days=1), dt.time(15)).replace(tzinfo=W._ICT)
                return {"t": [int(t.timestamp())], "c": [1759.08], "v": [0]}
            t = dt.datetime.combine(d, dt.time(*(self.last_hm or (0, 0)))).replace(tzinfo=W._ICT)
            if self.last_hm is None:
                return {"t": [], "c": [], "v": []}
            return {"t": [int(t.timestamp())], "c": [1750.0], "v": [0]}

    old_now = W._now
    try:
        for now_hm, last_hm, ok, label in (((11, 15, 1), (11, 14), True, "bar tươi"),
                                           ((11, 15, 1), (9, 29), False, "bar 09:29 lúc 11:15 (ca thật)"),
                                           ((12, 0, 1), (11, 29), True, "nghỉ trưa, bar 11:29"),
                                           ((14, 40, 1), (14, 29), True, "ATC, bar 14:29"),
                                           ((13, 0, 1), (11, 29), True, "13:00:01 chưa có bar chiều (ca thật 07/10)"),
                                           ((13, 3, 0), (11, 29), False, "13:03 vẫn kẹt bar 11:29"),
                                           ((9, 16, 30), (9, 15), True, "09:16:30 đã có bar 09:15"),
                                           ((9, 15, 1), None, None, "09:15:01 chưa có bar (ca thật 08/10)"),
                                           ((9, 30, 1), None, None, "09:30 vẫn rỗng")):
            now = dt.datetime(2026, 10, 7, *now_hm)
            W._now = lambda now=now: now
            oc = OC(last_hm)
            lm = W.LiveMarket.__new__(W.LiveMarket)
            lm._q, lm._bars, lm._pos = {}, {}, {}
            lm.ro = W.ReadOnlyDNSE(oc)
            vl, vr = lm.vni(now)
            to = dt.datetime.fromtimestamp(oc.tos[0], W._ICT).replace(tzinfo=None)
            if ok is None:
                pend = now_hm[:2] == (9, 15)
                check(f"VNINDEX {label}: None, vni_pending_open={pend}",
                      vl is None and lm.vni_pending_open is pend, f"{vl} {lm.vni_pending_open}")
            else:
                check(f"VNINDEX {label}: {'đọc được' if ok else 'None + lý do'}",
                      (vl == 1750.0 and lm.vni_note is None) if ok else
                      (vl is None and "quá cũ" in (lm.vni_note or "")), f"{vl} {lm.vni_note}")
                check(f"VNINDEX {label}: có bar ⇒ vni_pending_open=False", lm.vni_pending_open is False)
            check(f"VNINDEX {label}: `to` = phút hiện tại +1 (chống cache URL)",
                  to == now.replace(second=0) + dt.timedelta(minutes=1) and vr == 1759.08, f"{to} {vr}")
    finally:
        W._now = old_now

    tmp = tempfile.mkdtemp(prefix="ipw_sc_")
    W._atomic_json(os.path.join(tmp, "ch.json"), {"users": {"owner": {"id": "4242"}}})
    old = W.CHANNELS
    W.CHANNELS = os.path.join(tmp, "ch.json")
    try:
        nt = W.Notifier(dry=False)
        cmds = []
        nt._run = lambda cmd: (cmds.append(cmd), (True, ""))[1]
        nt.send("A", ("discord",), mention=True)
        nt.send("B", ("discord",), mention=False)
    finally:
        W.CHANNELS = old
    check("@mention: mention=True ⇒ discord bắt đầu '<@owner>'; False ⇒ không",
          cmds[0][1].startswith("<@4242> ") and not cmds[1][1].startswith("<@"), str(cmds))
    shutil.rmtree(tmp)


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
    check("PNJ 24/09 T0 14:15 ≥ 14:00 ⇒ (c) hoãn: chờ tới 09:15 25/09, 0 bán trong 24/09",
          r["2026-09-24"]["t0"] == "14:15" and r["2026-09-24"]["status"] == "AWAITING_REPLY"
          and r["2026-09-24"]["sold"] == 0, str(r["2026-09-24"]))
    check("PNJ 25/09 discretionary+NHIỄU ⇒ giữ, 0 bán", r["2026-09-25"]["status"] == "HOLD"
          and r["2026-09-25"]["sold"] == 0)
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
    check("PNJ-BAL 24/09 (T0 14:15) ⇒ không bán trong 24/09 (c)", rb["2026-09-24"]["sold"] == 0,
          str(rb["2026-09-24"]))
    check("PNJ-BAL CHƯA RÕ (agent) ⇒ bán 50% (700cp) từ 09:15 25/09", rb["2026-09-25"]["sold"] == 700,
          str(rb["2026-09-25"]))

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
    check("TV1 discretionary+NHIỄU ⇒ 0 bán; hạn trả lời > 14:15 ⇒ hoãn 09:15 phiên sau (c)",
          r["2026-07-16"]["status"] in ("AWAITING_REPLY", "HOLD") and r["2026-07-16"]["sold"] == 0,
          str(r["2026-07-16"]))
    rows, log = replay(fx, "TV1", 2300, E.DISCRETIONARY, {"2026-07-16": (8, E.BROKEN)},
                       reply={"id": 9, "is_bot": False, "content": "SHADOW BÁN TV1",
                              "created_at": T("13:55", "2026-07-16")})
    _print_replay("TV1 kịch bản GÃY + user 'SHADOW BÁN TV1' 13:55 (UPCOM ⇒ chỉ LO)", rows,
                  fx["cases"]["TV1"]["daily_close"]["2026-07-16"] * 1000)
    kinds = {i["api_order_type"] for x in log if x["kind"] == "CUTLOSS_TICK" for i in x.get("intents", [])
             if i["kind"] != "CANCEL"}
    check("TV1 UPCOM: mọi lệnh dự định đều LO", kinds == {"LO"}, str(kinds))


def main():
    print("intraday_price_watch_selfcheck")
    # fsync mỗi nhịp là độ bền ĐĨA (production 1 lần/phút); replay ~3.000 nhịp ⇒ tắt trong tiến
    # trình test để chạy đột biến được. Không phép thử nào ở đây kiểm độ bền đĩa.
    os.fsync = lambda fd: None
    for fn in (test_trigger, test_default_action, test_parse_reply, test_phase_and_types, test_modes,
               test_execution, test_driver, test_r2, test_replay):
        fn()
    total = N_PASS + len(FAILS)
    print(f"\n{N_PASS}/{total} PASS" + (f" — {len(FAILS)} FAIL" if FAILS else ""))
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
