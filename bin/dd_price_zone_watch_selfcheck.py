#!/usr/bin/env python3
"""Selfcheck dd_price_zone_watch.py — logic thuần + run() với CSV giá giả, KHÔNG mạng/DNSE/BQ/Notifier.

Chạy dưới 3 TZ (env -u TZ · TZ=America/New_York · TZ=Asia/Ho_Chi_Minh) — logic ngày neo ICT tường minh.
Mutation: --mutants chạy lại toàn bộ ca trên bản đột biến của module; mỗi mutant phải bị ≥1 ca bắt.
"""
import argparse
import contextlib
import datetime as dt
import importlib.util
import io
import json
import os
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "dd_price_zone_watch.py")
LEDGER = os.path.join(os.path.dirname(HERE), "kb", "dd_price_zones.json")
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")
D = dt.date


def load(src_text, name="ddz_mod"):
    spec = importlib.util.spec_from_loader(name, loader=None)
    m = importlib.util.module_from_spec(spec)
    m.__file__ = SRC
    exec(compile(src_text, SRC, "exec"), m.__dict__)
    return m


def ent(t="AAA", dd="2026-10-30", c=20000, lo=18000, hi=24000, q="2026Q3", exp="2027-02-27"):
    return {"ticker": t, "dd_date": dd, "bctc_quarter": q, "zone_low": lo, "center": c, "zone_high": hi,
            "expires_on": exp}


def cases(m):
    R = []

    def ok(name, cond):
        R.append((name, bool(cond)))

    e = ent()
    # 1. biên ngưỡng −15,0% vs −14,9% (tâm 20.000 ⇒ 17.000 / 17.020)
    ok("−15,0% (17.000) ⇒ BẬT", m.classify(17000, e, False)["alert"])
    ok("−14,9% (17.020) ⇒ KHÔNG bật", not m.classify(17020, e, False)["alert"])
    ok("tâm 9.950: 8.457 (−15,005%) bật, 8.458 (−14,995%) không",
       m.classify(8457, ent(c=9950), False)["alert"] and not m.classify(8458, ent(c=9950), False)["alert"])
    # 2. hysteresis
    ok("đang bật, −12% ⇒ GIỮ (hold_band)", m.classify(17600, e, True)["alert"] and m.classify(17600, e, True)["hold_band"])
    ok("đang bật, −10,0% ⇒ vẫn GIỮ", m.classify(18000, e, True)["alert"])
    ok("đang bật, −9,9% ⇒ TẮT", not m.classify(18020, e, True)["alert"])
    ok("đang tắt, −12% ⇒ vẫn TẮT", not m.classify(17600, e, False)["alert"])
    ok("new_alert chỉ khi vừa vào", m.classify(16000, e, False)["new_alert"] and not m.classify(16000, e, True)["new_alert"])
    # 3. trạng thái vùng
    ok("dưới đáy/trong/trên vùng", (m.classify(17900, e, False)["zone_status"], m.classify(18000, e, False)["zone_status"],
                                    m.classify(24001, e, False)["zone_status"]) == (m.ST_BELOW, m.ST_IN, m.ST_ABOVE))
    ok("center=null ⇒ không bao giờ bật", not m.classify(1, ent(c=None), False)["alert"])
    # 4. prev_state: phiên trước, cùng dd_date; DD mới ⇒ reset
    st = {"days": {"2026-10-29": {"AAA": {"dd_date": "2026-10-28", "alert": True}},
                   "2026-10-30": {"AAA": {"dd_date": "2026-10-30", "alert": True}}}}
    ok("prev = phiên trước asof", m.prev_state(st, "AAA", "2026-10-30", D(2026, 11, 2)) is True)
    ok("không lấy CHÍNH ngày asof làm prev (chạy lại cùng ngày idempotent)",
       m.prev_state(st, "AAA", "2026-10-28", D(2026, 10, 30)) is True and
       m.prev_state({"days": {"2026-10-30": st["days"]["2026-10-30"]}}, "AAA", "2026-10-30", D(2026, 10, 30)) is False)
    ok("DD mới (dd_date khác) ⇒ trạng thái trễ reset", m.prev_state(st, "AAA", "2026-11-01", D(2026, 11, 2)) is False)
    # 5. hết hạn
    nr = {"AAA": [("2026Q4", D(2027, 1, 20))]}
    ok("BCTC quý mới đã công bố ≤ asof ⇒ hết hạn", m.expiry_of(e, D(2027, 1, 20), nr)[0])
    ok("BCTC quý mới công bố SAU asof (PIT) ⇒ chưa hết hạn", not m.expiry_of(e, D(2027, 1, 19), nr)[0])
    ok("quý cũ/bằng quý DD không làm hết hạn", not m.expiry_of(e, D(2027, 1, 20), {"AAA": [("2026Q3", D(2026, 10, 29))]})[0])
    ok("quá expires_on ⇒ hết hạn (kể cả BQ lỗi=None)", m.expiry_of(e, D(2027, 2, 27), None)[0] and not m.expiry_of(e, D(2027, 2, 26), None)[0])
    led = {"entries": [ent("AAA"), ent("BBB", c=10000, lo=9000, hi=12000)]}
    rows, expired, day = m.evaluate(led, D(2027, 1, 21), {"AAA": {"close": 15000}, "BBB": {"close": 8000}}, {}, nr, {})
    ok("mã hết hạn KHÔNG nằm trong rows/không cảnh báo, nằm trong expired",
       [r["ticker"] for r in rows] == ["BBB"] and [x["ticker"] for x in expired] == ["AAA"] and "AAA" not in day)
    blk = m.render_block(rows, expired, D(2027, 1, 21), "test", "/tmp/x.md")
    ok("khối: hết hạn chỉ ở dòng 'Cần DD lại', BBB ở dòng cảnh báo",
       "Cần DD lại (BCTC mới hơn/quá hạn): AAA." in blk and "• AAA" not in blk and "• BBB" in blk)
    ok("khối có dòng nhắc 'không phải tín hiệu mua; không tự đưa vào plan'", m.NOTE in blk)
    # 6. giá đóng cửa đúng ngày
    bars = [(D(2026, 10, 28), 100.0, 10), (D(2026, 10, 29), 110.0, 10)]
    ok("bar cuối là phiên trước ⇒ KHÔNG dùng thay", m.bars_to_price(bars, D(2026, 10, 30))["close"] is None)
    ok("bar ngày asof ⇒ đúng giá đó", m.bars_to_price(bars + [(D(2026, 10, 30), 120.0, 10)], D(2026, 10, 30))["close"] == 120.0)
    ok("bar SAU asof bị bỏ (chạy --asof quá khứ)", m.bars_to_price(bars + [(D(2026, 10, 30), 120.0, 10)], D(2026, 10, 29))["close"] == 110.0)
    b25 = [(D(2026, 9, 1) + dt.timedelta(days=i), 10.0, 1 if i < 5 else 2) for i in range(25)]
    ok("ADV20 = TB 20 phiên cuối của close×vol", m.bars_to_price(b25, b25[-1][0])["adv20"] == 20.0)
    # 7. DD cũ bị thay bằng DD mới hơn (cả sổ thật: TV2 → 2026-11-01)
    led2 = {"entries": [ent("AAA", dd="2026-10-28", c=30000), ent("AAA", dd="2026-11-01", c=20000), ent("AAA", dd="2026-10-29", c=1)]}
    ok("bản dd_date mới nhất thắng (không theo thứ tự ghi)", m.latest_entries(led2)["AAA"]["center"] == 20000)
    real = json.load(open(LEDGER, encoding="utf-8"))
    ok("sổ thật: TV2 dùng DD 2026-11-01 (tâm 20.700)", m.latest_entries(real)["TV2"]["center"] == 20700)
    # 8. cờ: excluded / đang giữ / BANNED
    class FakeM:
        def positions(self, acc):
            return {"AAA": {"qty": 1250}} if acc == "1" else {}
    orig = None
    import intraday_price_watch as ipw
    orig = ipw.load_accounts
    ipw.load_accounts = lambda: [{"label": "SpaceX", "account_id": "1", "excluded": []},
                                 {"label": "ZaloPay", "account_id": "2", "excluded": ["BBB"]}]
    try:
        fl = m.account_flags(["AAA", "BBB"], FakeM(), {"AAA": [], "BBB": []})
    finally:
        ipw.load_accounts = orig
    ok("đang giữ gắn cờ đúng TK + số cp", fl["AAA"] == ["đang giữ SpaceX 1.250"])
    ok("excluded_tickers gắn cờ đúng TK", fl["BBB"] == ["excluded_tickers ZaloPay"])
    sf = m.static_flags(["HSG", "HHS", "FPT"], D(2026, 10, 30))
    ok("BANNED + forensic exclude gắn cờ, mã sạch không cờ",
       sf["HSG"][:1] == ["BANNED"] and any(x.startswith("forensic exclude") for x in sf["HHS"]) and sf["FPT"] == [])
    ok("forensic chỉ áp khi ngày cờ ≤ asof (PIT)", not any(x.startswith("forensic") for x in m.static_flags(["HHS"], D(2026, 6, 19))["HHS"]))
    # 9. run() 2 phiên liên tiếp qua CSV + state ⇒ 🆕 chỉ phiên đầu; trước giờ đóng cửa không lấy giá
    with tempfile.TemporaryDirectory() as td:
        lp = os.path.join(td, "l.json")
        json.dump({"entries": [ent("AAA", dd="2026-10-28")]}, open(lp, "w"))
        cp = os.path.join(td, "p.csv")
        open(cp, "w").write("ticker,date,close\nAAA,2026-10-29,16900\nAAA,2026-10-30,17500\nAAA,2026-11-02,18100\n")
        def go(asof, now=None, csvp=cp):
            a = argparse.Namespace(asof=asof, ledger=lp, state=os.path.join(td, "s.json"), out_dir=td, price_csv=csvp,
                                   report_block=True, no_bq=True, no_positions=True, no_state=False)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = m.run(a, now=now or dt.datetime(2026, 11, 2, 21, 0, tzinfo=_ICT))
            return rc, buf.getvalue()
        r1, o1 = go("2026-10-29")
        r2, o2 = go("2026-10-30")
        r2b, o2b = go("2026-10-30")
        r3, o3 = go("2026-11-02")
        ok("phiên 1 (−15,5%): 🆕 VỪA VÀO", r1 == 0 and "🆕 VỪA VÀO" in o1)
        ok("phiên 2 (−12,5%): vẫn liệt kê, không 🆕, giữ do trễ", "• AAA 17.500" in o2 and "🆕" not in o2 and "giữ do trễ" in o2)
        ok("chạy lại cùng ngày cho kết quả y hệt (idempotent)", o2 == o2b)
        ok("phiên 3 (−9,5%): tắt cảnh báo", "Không mã nào dưới tâm" in o3)
        r4, o4 = go("2026-11-02", now=dt.datetime(2026, 11, 2, 14, 0, tzinfo=_ICT), csvp=None)
        ok("asof=hôm nay trước 15:05 ICT ⇒ 'chưa đóng cửa', không gọi DNSE", r4 == 0 and "chưa đóng cửa" in o4)
    # 11. (điểm 1) rev đính chính + asof lọc DD tương lai + tâm FPT = kỳ vọng trọng số
    lrev = {"entries": [dict(ent("AAA", c=30000), rev=1), dict(ent("AAA", c=20000), rev=2), dict(ent("AAA", c=1), rev=1)]}
    ok("rev cao nhất của cùng (mã, dd_date) thắng, không theo thứ tự ghi", m.latest_entries(lrev)["AAA"]["center"] == 20000)
    lrev2 = {"entries": [dict(ent("AAA", dd="2026-10-30", c=1), rev=5), ent("AAA", dd="2026-11-01", c=2)]}
    ok("dd_date mới hơn thắng dù rev thấp hơn", m.latest_entries(lrev2)["AAA"]["center"] == 2)
    ok("asof lọc DD có dd_date > asof (không dùng DD tương lai)",
       m.latest_entries(lrev2, D(2026, 10, 31))["AAA"]["center"] == 1 and "AAA" not in m.latest_entries(lrev2, D(2026, 10, 29)))
    fpt = m.latest_entries(real, D(2026, 11, 2))["FPT"]
    ok("sổ thật: FPT tâm = 54.800 (kỳ vọng trọng số), center_alt 59.800 base_scenario, rev 2",
       (fpt["center"], fpt["center_kind"], fpt["center_alt"], fpt["center_alt_kind"], fpt["rev"]) == (54800, "expected_weighted", 59800, "base_scenario", 2))
    ok("sổ thật: asof 31/10 chưa có DD FPT (dd 01/11)", "FPT" not in m.latest_entries(real, D(2026, 10, 31)))
    # 12. (điểm 2) dnse_prices với payload DNSE thô: nghìn đồng, t=09:00 ICT, T7 không có bar
    days = [D(2026, 10, 26) + dt.timedelta(days=i) for i in range(5)]
    ts = [int(dt.datetime.combine(d, dt.time(9, 0), _ICT).timestamp()) for d in days]

    class FakeRO:
        def ohlc(self, t, resolution, **q):
            return {"t": ts, "c": [50.0, 51.0, 52.0, 52.5, 52.7], "v": [1000] * 5}

    class FakeMk:
        ro = FakeRO()
    pr = m.dnse_prices(["FPT"], D(2026, 10, 30), FakeMk())["FPT"]
    ok("dnse_prices: ×1000 (nghìn đồng → đồng), bar 09:00 ICT của chính ngày asof", pr["close"] == 52700.0 and pr["err"] is None)
    pr2 = m.dnse_prices(["FPT"], D(2026, 10, 31), FakeMk())["FPT"]
    ok("dnse_prices: T7 không có bar ⇒ close None + lý do, không lấy phiên T6 thay", pr2["close"] is None and "31/10" in (pr2["err"] or ""))
    ok("dnse_prices: ngày bar không lệch theo TZ host (T2 26/10 → 50.000)", m.dnse_prices(["FPT"], D(2026, 10, 26), FakeMk())["FPT"]["close"] == 50000.0)
    class BoomRO:
        def ohlc(self, *a, **k):
            raise TimeoutError("x")
    class BoomMk:
        ro = BoomRO()
    ok("dnse_prices: lỗi 1 mã ⇒ err, không ném", m.dnse_prices(["FPT"], D(2026, 10, 30), BoomMk())["FPT"]["err"] == "DNSE TimeoutError")
    eu = ent("AAA", c=20000); eu["price_ref"] = 18000
    rw, _, dy = m.evaluate({"entries": [eu]}, D(2026, 11, 2), {"AAA": {"close": 18.0}}, {}, None, {})
    ok("close lệch đơn vị (18 vs price_ref 18.000) ⇒ lỗi 'nghi sai đơn vị', không báo động, không vào state",
       rw[0]["err"] and "nghi sai đơn vị" in rw[0]["err"] and not rw[0].get("alert") and "AAA" not in dy)
    rw, _, _ = m.evaluate({"entries": [eu]}, D(2026, 11, 2), {"AAA": {"close": 55000.0}}, {}, None, {})
    ok("close ×3,06 so price_ref ⇒ nghi sai đơn vị; ×1,5 ⇒ bình thường",
       rw[0]["err"] and m.evaluate({"entries": [eu]}, D(2026, 11, 2), {"AAA": {"close": 27000.0}}, {}, None, {})[0][0]["err"] is None)
    # 13. (điểm 3) asof mặc định = phiên đã đóng gần nhất; khối không nói dối khi thiếu giá
    hol = lambda d: d == D(2026, 11, 2)
    I = lambda y, mo, d, h, mi: dt.datetime(y, mo, d, h, mi, tzinfo=_ICT)
    ok("CN 21:00 ⇒ thứ Sáu 30/10", m.default_asof(I(2026, 11, 1, 21, 0), hol)[0] == D(2026, 10, 30))
    ok("T7 ⇒ thứ Sáu 30/10", m.default_asof(I(2026, 10, 31, 10, 0), hol)[0] == D(2026, 10, 30))
    ok("T2 00:30 (plan sau nửa đêm, T2 chưa mở) ⇒ phiên trước = thứ Sáu 30/10", m.default_asof(I(2026, 11, 3, 0, 30), lambda d: False)[0] == D(2026, 11, 2))
    ok("ngày lễ T2 02/11 ⇒ thứ Sáu 30/10; T3 00:30 sau lễ ⇒ cũng T6 30/10", m.default_asof(I(2026, 11, 2, 20, 0), hol)[0] == D(2026, 10, 30)
       and m.default_asof(I(2026, 11, 3, 0, 30), hol)[0] == D(2026, 10, 30))
    ok("T4 16:00 (đã đóng) ⇒ hôm nay; T4 11:00 (đang phiên) ⇒ hôm nay (guard chưa đóng cửa ở run)",
       m.default_asof(I(2026, 11, 4, 16, 0), hol)[0] == D(2026, 11, 4) and m.default_asof(I(2026, 11, 4, 11, 0), hol)[0] == D(2026, 11, 4))
    with tempfile.TemporaryDirectory() as td:
        lp = os.path.join(td, "l.json")
        json.dump({"entries": [ent("AAA")]}, open(lp, "w"))
        cp = os.path.join(td, "p.csv")
        open(cp, "w").write("ticker,date,close\nAAA,2026-10-30,17000\n")
        def go2(now):
            a = argparse.Namespace(asof=None, ledger=lp, state=os.path.join(td, "s.json"), out_dir=td, price_csv=cp,
                                   report_block=True, no_bq=True, no_positions=True, no_state=True)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                m.run(a, now=now)
            return buf.getvalue()
        o_sun = go2(I(2026, 11, 1, 21, 0))
        o_mon = go2(I(2026, 11, 2, 0, 30) if not hol(D(2026, 11, 2)) else I(2026, 11, 2, 0, 30))
        ok("run() không --asof, CN 21:00 ⇒ khối đóng cửa 30/10 có giá, KHÔNG 'chưa đóng cửa'", "đóng cửa 30/10" in o_sun and "chưa đóng cửa" not in o_sun and "• AAA 17.000" in o_sun)
        ok("run() không --asof, T2 00:30 ⇒ vẫn đóng cửa 30/10 (không bị guard 15:05 của hôm nay)", "đóng cửa 30/10" in o_mon and "chưa đóng cửa" not in o_mon)
    eN = {"entries": [ent("AAA"), ent("BBB")]}
    rN, xN, _ = m.evaluate(eN, D(2026, 11, 2), {"AAA": {"close": None, "err": "x"}, "BBB": {"close": None, "err": "y"}}, {}, None, {})
    bN = m.render_block(rN, xN, D(2026, 11, 2), "t", "/tmp/x")
    ok("0/2 mã có giá ⇒ 'KHÔNG KIỂM ĐƯỢC', KHÔNG in 'Không mã nào dưới'", "KHÔNG KIỂM ĐƯỢC" in bN and "Không mã nào dưới" not in bN)
    rP, xP, _ = m.evaluate(eN, D(2026, 11, 2), {"AAA": {"close": 19000.0}, "BBB": {"close": None, "err": "y"}}, {}, None, {})
    bP = m.render_block(rP, xP, D(2026, 11, 2), "t", "/tmp/x")
    ok("1/2 mã có giá ⇒ 'KIỂM ĐƯỢC 1/2', không khẳng định toàn thể", "KIỂM ĐƯỢC 1/2" in bP and "Trong 1/2 mã" in bP and "Không mã nào dưới" not in bP)
    # 14. (điểm 4) hệ giá corp-action
    eF = ent("AAA", dd="2026-10-30", c=20000)
    iss = {"event_code": "ISS", "exright_date": "2026-11-02", "issue_method_name_vi": "Cổ phiếu thưởng"}
    div = {"event_code": "DIV", "exright_date": "2026-11-03", "value_per_share": "1000"}
    esop = {"event_code": "ISS", "exright_date": "2026-11-02", "issue_method_name_vi": "Phát hành cho CBCNV"}
    n1, b1 = m.frame_check(eF, [iss], D(2026, 11, 4))
    ok("cổ phiếu thưởng ex giữa DD và asof ⇒ block + ghi chú hệ giá", b1 and any("CHƯA điều chỉnh" in x for x in n1))
    n2, b2 = m.frame_check(eF, [div], D(2026, 11, 4))
    ok("cổ tức tiền ⇒ ghi chú (1.000đ), KHÔNG block", (not b2) and n2 and "1.000đ" in n2[0])
    ok("ISS không điều chỉnh giá (ESOP) ⇒ bỏ qua", m.frame_check(eF, [esop], D(2026, 11, 4)) == ([], False))
    ok("sự kiện trước/bằng dd_date hoặc sau asof ⇒ bỏ qua",
       m.frame_check(eF, [dict(iss, exright_date="2026-10-30"), dict(iss, exright_date="2026-11-05")], D(2026, 11, 4)) == ([], False))
    rF, _, dF = m.evaluate({"entries": [eF]}, D(2026, 11, 4), {"AAA": {"close": 12000.0}}, {}, None, {}, corp={"AAA": [iss]})
    ok("chia/thưởng sau DD, giá −40% so tâm ⇒ KHÔNG nhãn ngưỡng cảnh báo, nhãn 'cần DD/điều chỉnh tâm', state alert=False",
       rF[0]["alert"] is False and rF[0]["zone_status"] == m.ST_FRAME and dF["AAA"]["alert"] is False)
    bF = m.render_block(rF, [], D(2026, 11, 4), "t", "/tmp/x")
    ok("khối: mã bị frame nằm ở mục 'cần DD/điều chỉnh tâm', không ở 'Dưới tâm'", "cần DD/điều chỉnh tâm" in bF and "Dưới tâm ≥" not in bF)
    rD, _, _ = m.evaluate({"entries": [eF]}, D(2026, 11, 4), {"AAA": {"close": 12000.0}}, {}, None, {}, corp={"AAA": [div]})
    bD = m.render_block(rD, [], D(2026, 11, 4), "t", "/tmp/x")
    ok("cổ tức tiền: vẫn cảnh báo ngưỡng + ghi chú hệ giá", rD[0]["alert"] and "Ghi chú hệ giá" in bD or ("hệ giá sổ trước ex" in bD and rD[0]["alert"]))
    rN2, _, _ = m.evaluate({"entries": [eF]}, D(2026, 11, 4), {"AAA": {"close": 12000.0}}, {}, None, {}, corp=None)
    ok("corp=None (không kiểm được) ⇒ không block", rN2[0]["alert"] and not rN2[0]["frame_block"])
    # 15. (điểm 5) cơ sở ngưỡng center | zone_low
    eB = ent("AAA", c=20000, lo=18000, hi=24000)
    ok("cơ sở center: 16.000 (−20% tâm) ⇒ bật; cơ sở zone_low: −11,1% so đáy ⇒ không bật",
       m.classify(16000, eB, False, basis="center")["alert"] and not m.classify(16000, eB, False, basis="zone_low")["alert"])
    ok("cơ sở zone_low: 15.300 (đúng −15% đáy) ⇒ bật; 15.301 ⇒ không", m.classify(15300, eB, False, basis="zone_low")["alert"]
       and not m.classify(15301, eB, False, basis="zone_low")["alert"])
    ok("cơ sở zone_low mà sổ không có đáy ⇒ không bao giờ bật", not m.classify(1, ent(lo=None), False, basis="zone_low")["alert"])
    ok("state khác cơ sở ⇒ không kế thừa trạng thái trễ",
       m.prev_state({"days": {"2026-10-29": {"AAA": {"dd_date": "d", "alert": True, "basis": "center"}}}}, "AAA", "d", D(2026, 10, 30), "zone_low") is False
       and m.prev_state({"days": {"2026-10-29": {"AAA": {"dd_date": "d", "alert": True, "basis": "center"}}}}, "AAA", "d", D(2026, 10, 30), "center") is True)
    tb = m.render_table(rF, [], D(2026, 11, 4), "t")
    ok("bảng in cả % so tâm lẫn % so đáy + loại tâm", "% so tâm" in tb and "% so đáy" in tb)
    ok("hằng DD_ALERT_BASIS mặc định = center", m.DD_ALERT_BASIS == "center")
    # 16. retention
    with tempfile.TemporaryDirectory() as td:
        for nm in ("2026-08-01.md", "2026-09-10.md", "2026-11-01.md", "notes.md"):
            open(os.path.join(td, nm), "w").write("x")
        m.prune_md(td, D(2026, 11, 2), 60)
        ok("retention 60 ngày: bỏ file cũ, giữ file gần + file lạ", sorted(os.listdir(td)) == ["2026-09-10.md", "2026-11-01.md", "notes.md"])
    # 10. không đụng Notifier/Telegram/plan
    src = open(SRC, encoding="utf-8").read()
    ok("module không gọi notify/Notifier/ghi plan", not any(k in src for k in ("notify_telegram", "Notifier(", "trade_plans", "place_order(", "send_telegram")))
    return R


MUTANTS = [
    # (tên, gốc, thay, TZ ép khi chạy mutant — None = giữ TZ hiện tại)
    ("M1 bỏ ×1000 đơn vị DNSE", 'r["c"][i] * 1000', 'r["c"][i]'),
    ("M2 fromtimestamp naive (TZ host)", "dt.datetime.fromtimestamp(x, _ICT).date()", "dt.datetime.fromtimestamp(x).date()", "America/New_York"),
    ("điểm1: rev bị bỏ qua", 'k = (e["dd_date"], int(e.get("rev", 1)))', 'k = (e["dd_date"], 0)'),
    ("điểm1: latest_entries bỏ lọc asof", 'if lim is not None and e["dd_date"] > lim:', 'if False:'),
    ("điểm2: bỏ chặn sai đơn vị", "if not (PRICE_RATIO_OK[0] <= r <= PRICE_RATIO_OK[1]):", "if False:"),
    ("điểm3: bỏ phân biệt trước 09:00", "and now.time() < dt.time(9, 0)", "and False"),
    ("điểm3: bỏ kiểm ngày lễ", "d.weekday() < 5 and not is_holiday(d)", "d.weekday() < 5"),
    ("điểm3: khối khẳng định 'không mã nào' khi thiếu giá", "elif n == m and m:", "elif True:"),
    ("điểm3: asof mặc định = hôm nay thô", "        asof, asof_note = default_asof(now)", "        asof, asof_note = now.date(), ''"),
    ("điểm4: không block khi ISS điều chỉnh giá", "            block = True", "            block = False"),
    ("điểm4: cửa sổ sự kiện gồm cả trước DD", 'if not (entry["dd_date"] < xd <= asof.isoformat()):', 'if not (xd <= asof.isoformat()):'),
    ("điểm4: bỏ ghi chú cổ tức tiền", 'if ev.get("event_code") == "DIV":', 'if False:'),
    ("điểm5: cơ sở luôn center", "b = alert_base(entry, basis)", 'b = entry.get("center")'),
    ("điểm5: state bỏ phân biệt cơ sở", 'rec.get("basis", "center") == (basis or DD_ALERT_BASIS)', 'True'),
    ("retention: không xoá", "os.remove(os.path.join(out_dir, f))", "pass"),
    ("ngưỡng ≤ → <", "alert = p * 100 <= b * (100 - thr)", "alert = p * 100 < b * (100 - thr)"),
    ("hysteresis tắt theo thr", "alert = p * 100 <= b * (100 - rel)", "alert = p * 100 <= b * (100 - thr)"),
    ("bỏ hysteresis (prev_alert bị bỏ qua)", "        if prev_alert:\n", "        if False:\n"),
    ("hết hạn bỏ kiểm PIT rd ≤ asof", "and rd is not None and rd <= asof", "and rd is not None"),
    ("hết hạn bỏ qua expires_on", "    if asof >= exp:\n", "    if False:\n"),
    ("giá: nhận bar phiên khác", "if not bars or bars[-1][0] != asof:", "if not bars:"),
    ("DD cũ thắng", 'if t not in out or k >= (out[t]["dd_date"], int(out[t].get("rev", 1))):', 'if t not in out or k <= (out[t]["dd_date"], int(out[t].get("rev", 1))):'),
    ("prev lấy cả ngày asof", "if d < asof.isoformat()", "if d <= asof.isoformat()"),
    ("DD mới không reset trễ", 'same = rec.get("dd_date") == dd_date and', 'same = True or'),
    ("bỏ cờ excluded", "if t in a[\"excluded\"]:", "if False:"),
    ("forensic bỏ PIT", "if t in fl and d.date() <= asof:", "if t in fl:"),
    ("không cảnh báo khi chưa đóng cửa", "elif asof == now.date() and now.time() < CLOSE_READY:", "elif False:"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mutants", action="store_true")
    a = ap.parse_args()
    base = open(SRC, encoding="utf-8").read()
    R = cases(load(base))
    for n, r in R:
        print(("PASS " if r else "FAIL ") + n)
    allok = all(r for _, r in R)
    print(f"-- {sum(r for _, r in R)}/{len(R)} PASS (TZ={os.environ.get('TZ', '<unset>')})")
    if a.mutants:
        killed = 0
        import time
        for name, old, new, *tz in MUTANTS:
            if old not in base:
                print(f"MUTANT-SKIP? '{name}': chuỗi gốc không còn trong module")
                allok = False
                continue
            tz0 = os.environ.get("TZ")
            if tz:                                   # mutant phụ thuộc TZ host: ép TZ ngoại để kết quả tất định
                os.environ["TZ"] = tz[0]
                time.tzset()
            try:
                rr = cases(load(base.replace(old, new, 1), "ddz_mut"))
                dead = not all(r for _, r in rr)
            except Exception:  # noqa: BLE001 — mutant làm vỡ module cũng tính là bị bắt
                dead = True
            finally:
                if tz:
                    os.environ.pop("TZ", None) if tz0 is None else os.environ.__setitem__("TZ", tz0)
                    time.tzset()
            killed += dead
            print(("KILLED " if dead else "SURVIVED ") + name)
        print(f"-- mutants killed {killed}/{len(MUTANTS)}")
        allok = allok and killed == len(MUTANTS)
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
