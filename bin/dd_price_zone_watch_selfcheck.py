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
        json.dump({"entries": [ent("AAA")]}, open(lp, "w"))
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
    # 10. không đụng Notifier/Telegram/plan
    src = open(SRC, encoding="utf-8").read()
    ok("module không gọi notify/Notifier/ghi plan", not any(k in src for k in ("notify_telegram", "Notifier(", "trade_plans", "place_order(", "send_telegram")))
    return R


MUTANTS = [
    ("ngưỡng ≤ → <", "alert = p * 100 <= c * (100 - thr)", "alert = p * 100 < c * (100 - thr)"),
    ("hysteresis tắt theo thr", "alert = p * 100 <= c * (100 - rel)", "alert = p * 100 <= c * (100 - thr)"),
    ("bỏ hysteresis (prev_alert bị bỏ qua)", "        if prev_alert:\n", "        if False:\n"),
    ("hết hạn bỏ kiểm PIT rd ≤ asof", "and rd is not None and rd <= asof", "and rd is not None"),
    ("hết hạn bỏ qua expires_on", "    if asof >= exp:\n", "    if False:\n"),
    ("giá: nhận bar phiên khác", "if not bars or bars[-1][0] != asof:", "if not bars:"),
    ("DD cũ thắng", 'e["dd_date"] >= out[t]["dd_date"]', 'e["dd_date"] <= out[t]["dd_date"]'),
    ("prev lấy cả ngày asof", "if d < asof.isoformat()", "if d <= asof.isoformat()"),
    ("DD mới không reset trễ", 'if rec.get("dd_date") == dd_date else False', ''),
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
        for name, old, new in MUTANTS:
            if old not in base:
                print(f"MUTANT-SKIP? '{name}': chuỗi gốc không còn trong module")
                allok = False
                continue
            try:
                rr = cases(load(base.replace(old, new, 1), "ddz_mut"))
                dead = not all(r for _, r in rr)
            except Exception:  # noqa: BLE001 — mutant làm vỡ module cũng tính là bị bắt
                dead = True
            killed += dead
            print(("KILLED " if dead else "SURVIVED ") + name)
        print(f"-- mutants killed {killed}/{len(MUTANTS)}")
        allok = allok and killed == len(MUTANTS)
    sys.exit(0 if allok else 1)


if __name__ == "__main__":
    main()
