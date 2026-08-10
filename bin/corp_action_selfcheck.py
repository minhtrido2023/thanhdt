#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `mike/bin/corp_actions.py` + `LotBook.corp_action_split` trong park_holdings.py.

Chạy:  python3 mike/bin/corp_action_selfcheck.py
Phải PASS y hệt khi KHÔNG có biến TZ và khi chạy từ thư mục khác (§16 + skill
`verify-before-done` bước 3):
       cd /tmp && env -u TZ python3 <repo>/mike/bin/corp_action_selfcheck.py

RÀNG BUỘC MÔI TRƯỜNG đã rà (skill `verify-before-done` bước 2), và cách selfcheck này cắt bỏ:
  · MẠNG/BROKER — `park_holdings` gọi DNSE LIVE khi `asof == hôm nay`. Mọi ca dưới đây truyền
    `asof` QUÁ KHỨ CỐ ĐỊNH + `broker=` dựng sẵn ⇒ không chạm mạng, không phụ thuộc ngày chạy.
    (Đây cũng là lý do không dùng `asof=today`: selfcheck sẽ đổi hành vi theo ngày người chạy.)
  · TZ — `today_ict()` đã neo `ZoneInfo` tường minh; ca 8 kiểm nó ra đúng ngày ICT ngay cả khi
    `TZ` bị gỡ, để chống hồi quy về `datetime.now()` trần.
  · CWD — `WC_ROOT` suy từ `__file__`; ca 9 khẳng định đường dẫn registry không phụ thuộc cwd.
  · SỔ THẬT `data/corp_actions.json` — mọi ca logic đều BƠM record qua tham số `corp_actions=`
    thay vì đọc sổ thật, nên selfcheck không đổi kết quả khi ai đó thêm/bớt record thật. RIÊNG
    ca 10 CỐ Ý đọc sổ thật (đó là phần cần khoá lại: record VHM đang chạy production).
"""
import datetime as dt
import json
import os
import sys
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
WC_ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, WC_ROOT)

import corp_actions as CA               # noqa: E402
import park_holdings as PH              # noqa: E402

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def raises(fn, name):
    try:
        fn()
    except CA.CorpActionError:
        check(name, True)
    except Exception as e:
        check(name, False, f"ném {type(e).__name__} thay vì CorpActionError: {e}")
    else:
        check(name, False, "KHÔNG ném lỗi — record sai đã lọt qua")


def book_with(lots):
    b = PH.LotBook()
    for tk, book, qty, px, d in lots:
        b.buy(tk, book, qty, px, d, "test")
    return b


ACT_VHM = {"id": "T-VHM", "ticker": "VHM", "event_type": "STOCK_DIVIDEND", "qty_multiplier": 2.0,
           "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05T12:00:00",
           "_status": "CONFIRMED test"}

# ── 1. Bất biến cốt lõi: nhân qty, chia giá, TỔNG GIÁ VỐN KHÔNG ĐỔI ──────────────────────────
print("\n[1] corp_action_split ×2 — tổng giá vốn bất biến")
b = book_with([("VHM", "PARK", 500, 149800.0, "2026-07-01")])
cost_before = sum(l["qty"] * l["price"] for l in b.lots)
n = b.corp_action_split("VHM", 2.0, "2026-08-06", "2026-08-05T12:00:00", "test", "T-VHM")
cost_after = sum(l["qty"] * l["price"] for l in b.lots)
check("1 lô được điều chỉnh", n == 1, n)
check("qty 500 → 1000", b.lots[0]["qty"] == 1000, b.lots[0]["qty"])
check("giá 149.800 → 74.900", b.lots[0]["price"] == 74900.0, b.lots[0]["price"])
check("tổng giá vốn bất biến", abs(cost_before - cost_after) < 1e-6,
      f"{cost_before} → {cost_after}")
check("qty là int (không phải float)", isinstance(b.lots[0]["qty"], int), type(b.lots[0]["qty"]))
check("có dấu vết corp_actions trên lô", b.lots[0].get("corp_actions") == ["T-VHM"],
      b.lots[0].get("corp_actions"))

# ── 2. Quyền theo ex_date, KHÔNG theo ngày broker credit ────────────────────────────────────
print("\n[2] entitlement — chỉ lô có entry_date < ex_date")
b = book_with([("VHM", "PARK", 100, 150000.0, "2026-08-05"),    # trước ex → hưởng
               ("VHM", "PARK", 100, 75000.0, "2026-08-06"),     # ĐÚNG ex → KHÔNG hưởng
               ("VHM", "PARK", 100, 75000.0, "2026-08-07")])    # sau ex  → KHÔNG hưởng
b.corp_action_split("VHM", 2.0, "2026-08-06", "2026-08-05T12:00:00", "test", "T-VHM")
check("lô mua 08-05 (trước ex) ×2", b.lots[0]["qty"] == 200, b.lots[0]["qty"])
check("lô mua ĐÚNG ngày ex 08-06 KHÔNG nhân", b.lots[1]["qty"] == 100, b.lots[1]["qty"])
check("lô mua sau ex 08-07 KHÔNG nhân", b.lots[2]["qty"] == 100, b.lots[2]["qty"])

# ── 3. Tỉ lệ KHÔNG chia hết ⇒ làm tròn Ở MỨC VỊ THẾ (đúng chỗ broker làm tròn) ──────────────
# Đổi hành vi 2026-08-11 (job Taylor_20260810_183618): bản cũ fail-closed mọi lô lẻ. Ca THẬT
# MBB cổ tức CP 15% cho thấy fail-closed ở đây là SAI CHỖ — broker không làm tròn từng lô, nó
# làm tròn XUỐNG một lần trên tổng vị thế. Cái fail-closed thật sự bảo vệ ta là cổng
# `_status: CONFIRMED` + cổng đối soát Σ lô == openQuantity, không phải phép chia.
print("\n[3] tỉ lệ không chia hết ⇒ làm tròn XUỐNG ở MỨC VỊ THẾ + Hamilton chia phần dôi")
b = book_with([("MBB", "PARK", 100, 24700.0, "2026-07-10"),
               ("MBB", "PARK", 102, 23597.06, "2026-07-20")])
cost_before = sum(l["qty"] * l["price"] for l in b.lots)
n = b.corp_action_split("MBB", 1.15, "2026-08-11", "2026-08-10T19:32:49", "test", "T-MBB")
qtys = [l["qty"] for l in b.lots]
check("ca THẬT ZaloPay 100+102 ×1,15: cả 2 lô được điều chỉnh", n == 2, n)
check("tổng 202 → 232 = floor(232,3) — KHỚP openQuantity broker thật",
      sum(qtys) == 232, f"{qtys} = {sum(qtys)}")
check("chia lô: 100→115 (quyền 15,0 chẵn), 102→117 (quyền 15,3 làm tròn xuống)",
      qtys == [115, 117], qtys)
check("tổng giá vốn bất biến dù hệ số hiệu dụng 232/202 ≠ 1,15",
      abs(cost_before - sum(l["qty"] * l["price"] for l in b.lots)) < 1e-6,
      f"{cost_before} → {sum(l['qty'] * l['price'] for l in b.lots)}")
check("KHÔNG gắn UNVERIFIED (làm tròn đúng chỗ ≠ nghi vấn)", not b.unverified, b.unverified)
check("mọi qty vẫn là int", all(isinstance(l["qty"], int) for l in b.lots), qtys)

# Ca SpaceX cùng sự kiện, chia hết — phải ra đúng số broker 1.265 và không đụng Hamilton.
b = book_with([("MBB", "PARK", 1100, 25850.0, "2026-07-02")])
b.corp_action_split("MBB", 1.15, "2026-08-11", "2026-08-10T19:32:49", "test", "T-MBB")
check("ca THẬT SpaceX 1.100 ×1,15 → 1.265 (float 1265,0000000000002 KHÔNG được floor thành 1264)",
      b.lots[0]["qty"] == 1265, b.lots[0]["qty"])

# Hamilton phải chia phần dôi, không phải bỏ rơi: 3 lô 101cp ×1,5 ⇒ tổng 303→454 (floor 454,5),
# quyền chính xác mỗi lô 50,5 ⇒ mỗi lô +50, còn dôi 1cp về lô đầu tiên (tie → thứ tự sổ).
b = book_with([("ABC", "PARK", 101, 10000.0, "2026-01-01"),
               ("ABC", "PARK", 101, 10000.0, "2026-01-02"),
               ("ABC", "PARK", 101, 10000.0, "2026-01-03")])
b.corp_action_split("ABC", 1.5, "2026-08-06", "2026-08-05T12:00:00", "test", "T-ABC")
qtys = [l["qty"] for l in b.lots]
check("Hamilton: tổng 303 → 454 = floor(454,5)", sum(qtys) == 454, f"{qtys} = {sum(qtys)}")
check("Hamilton: phần dôi 1cp về lô ĐẦU (tie-break tất định theo thứ tự sổ)",
      qtys == [152, 151, 151], qtys)

# Quyền làm tròn xuống còn 0 ⇒ no-op có cảnh báo, KHÔNG phải UNVERIFIED (vị thế quá nhỏ là
# chuyện bình thường, không phải dấu hiệu kế toán sai).
b = book_with([("ABC", "PARK", 3, 10000.0, "2026-01-01")])
n = b.corp_action_split("ABC", 1.15, "2026-08-06", "2026-08-05T12:00:00", "test", "T-ABC")
check("vị thế 3cp ×1,15 → quyền 0,45 làm tròn xuống 0 ⇒ no-op",
      n == 0 and b.lots[0]["qty"] == 3, (n, b.lots[0]["qty"]))
check("  …có cảnh báo, KHÔNG gắn UNVERIFIED",
      len(b.warnings) == 1 and not b.unverified, (b.warnings, b.unverified))

# ── 4. Không giữ mã / không lô nào hưởng quyền ──────────────────────────────────────────────
print("\n[4] no-op an toàn")
b = book_with([("XYZ", "PARK", 100, 10000.0, "2026-01-01")])
check("không giữ mã ⇒ 0, không cảnh báo",
      b.corp_action_split("VHM", 2.0, "2026-08-06", "2026-08-05T12:00:00", "t") == 0
      and not b.warnings, b.warnings)
b = book_with([("VHM", "PARK", 100, 10000.0, "2026-08-10")])
check("giữ mã nhưng không lô nào hưởng quyền ⇒ 0 + có cảnh báo",
      b.corp_action_split("VHM", 2.0, "2026-08-06", "2026-08-05T12:00:00", "t") == 0
      and len(b.warnings) == 1, b.warnings)
check("  …và KHÔNG gắn UNVERIFIED (không hưởng quyền là bình thường, không phải nghi vấn)",
      not b.unverified, b.unverified)

# ── 5. validate(): record hỏng phải NÉM, không được im lặng bỏ qua ──────────────────────────
print("\n[5] validate — fail-loud")
raises(lambda: CA.validate({"ticker": "VHM", "event_type": "CASH_DIVIDEND", "qty_multiplier": 2.0,
                            "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05"}),
       "cổ tức TIỀN MẶT bị từ chối (thuộc §21, không thuộc sổ này)")
raises(lambda: CA.validate({"ticker": "VHM", "event_type": "SPLIT", "qty_multiplier": 1.0,
                            "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05"}),
       "qty_multiplier = 1 bị từ chối")
raises(lambda: CA.validate({"ticker": "VHM", "event_type": "SPLIT", "qty_multiplier": 0.5,
                            "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05"}),
       "reverse split (<1) bị từ chối — chưa thiết kế, sinh lô lẻ")
raises(lambda: CA.validate({"ticker": "VHM", "event_type": "SPLIT", "qty_multiplier": 2.0,
                            "ex_date": "06/08/2026", "broker_effective_ts": "2026-08-05"}),
       "ex_date sai định dạng bị từ chối")
raises(lambda: CA.validate({"ticker": "VHM", "event_type": "SPLIT", "qty_multiplier": 2.0,
                            "ex_date": "2026-08-06"}),
       "thiếu broker_effective_ts bị từ chối")
v = CA.validate({"ticker": " vhm ", "event_type": "stock_dividend", "qty_multiplier": "2",
                 "ex_date": "2026-08-06", "broker_effective_ts": "2026-08-05T12:00:00"})
check("chuẩn hoá ticker/type/số", v["ticker"] == "VHM" and v["event_type"] == "STOCK_DIVIDEND"
      and v["qty_multiplier"] == 2.0, v)
check("id tự sinh khi thiếu", v["id"] == "VHM-2026-08-06-STOCK_DIVIDEND", v["id"])

# ── 6. Cổng CONFIRMED — record chưa ký KHÔNG được áp (fail-closed) ──────────────────────────
print("\n[6] chỉ record CONFIRMED mới vào đường live")
tmp = os.path.join(WC_ROOT, "data", f".corp_actions_selfcheck_{os.getpid()}.json")
json.dump({"actions": [
    dict(ACT_VHM, id="A-confirmed", _status="CONFIRMED by user"),
    dict(ACT_VHM, id="B-proposed", _status="PROPOSED chờ duyệt"),
    dict(ACT_VHM, id="C-nostatus", _status=""),
    dict(ACT_VHM, id="D-revoked", _status="REVOKED sai ngày"),
]}, open(tmp, "w", encoding="utf-8"))
try:
    live = [a["id"] for a in CA.load_corp_actions(tmp)]
    check("chỉ 'A-confirmed' được áp", live == ["A-confirmed"], live)
    check("load_all vẫn thấy đủ 4 (để người soát)", len(CA.load_all(tmp)) == 4)
finally:
    os.remove(tmp)
check("sổ VẮNG MẶT ⇒ [] chứ không nổ (phiên thường không có corp action nào)",
      CA.load_corp_actions(os.path.join(WC_ROOT, "data", "__khong_ton_tai__.json")) == [])

# ── 7. Tích hợp park_holdings trên DỮ LIỆU THẬT (bootstrap thật + broker thật 2026-08-05) ───
print("\n[7] park_holdings — ca VHM thật, 2 account")


def broker_from_raw(asof, acct):
    pos, ts = {}, None
    path = os.path.join(WC_ROOT, "data", "execution_logs", f"dnse_raw_{asof}.jsonl")
    for line in open(path, encoding="utf-8"):
        try:
            rec = json.loads(line)
        except Exception:
            continue
        if str(rec.get("account_no")) != str(acct) or rec.get("kind") != "positions":
            continue                                        # §12: lọc account TRƯỚC mọi phép tính
        cur = {}
        for p in (rec.get("payload") or {}).get("positions") or []:
            q = int(p.get("openQuantity") or 0)
            if q > 0 and p.get("symbol"):
                cur[p["symbol"]] = {"qty": q, "market_price": float(p.get("marketPrice") or 0),
                                    "sellable": int(p.get("tradeQuantity") or 0)}
        if cur and (ts is None or rec.get("ts", "") >= ts):
            pos, ts = cur, rec.get("ts", "")
    return pos, 0.0, {"source": "selfcheck", "asof": asof, "ts": ts}


for label, acct, want in [("SpaceX", "0002023347", 1000), ("ZaloPay", "0001743768", 600)]:
    bk = broker_from_raw("2026-08-05", acct)
    # (a) KHÔNG có corp action → phải LỆCH (chứng minh ca thật vốn hỏng, không phải test rỗng)
    r0 = PH.park_holdings(label, asof="2026-08-05", broker=bk, corp_actions=[])
    m0 = [m for m in r0["reconcile"]["mismatches"] if m["ticker"] == "VHM"]
    check(f"{label}: KHÔNG corp action ⇒ VHM lệch {want // 2} vs {want}",
          bool(m0) and m0[0]["broker_qty"] == want and m0[0]["ledger_qty"] == want // 2, m0)
    # (b) CÓ corp action → khớp tuyệt đối
    r1 = PH.park_holdings(label, asof="2026-08-05", broker=bk, corp_actions=[ACT_VHM])
    vhm = [l for l in r1["lots"] if l["ticker"] == "VHM"]
    check(f"{label}: CÓ corp action ⇒ reconcile.ok=True, 0 lệch",
          r1["reconcile"]["ok"] and not r1["reconcile"]["mismatches"],
          r1["reconcile"]["mismatches"])
    check(f"{label}: Σ lô VHM == openQuantity broker ({want})",
          sum(l["qty"] for l in vhm) == want, sum(l["qty"] for l in vhm))
    check(f"{label}: tổng giá vốn VHM bất biến",
          abs(sum(l["qty"] * l["price"] for l in vhm)
              - sum(l0["qty"] * l0["price"] for l0 in r0["lots"] if l0["ticker"] == "VHM")) < 1e-6)
    check(f"{label}: không ticker nào UNVERIFIED", not r1["unverified_tickers"],
          r1["unverified_tickers"])
    check(f"{label}: KHÔNG mã nào KHÁC bị đụng vào",
          {l["ticker"] for l in r0["lots"]} == {l["ticker"] for l in r1["lots"]}
          and all(a["qty"] == c["qty"] for a, c in
                  zip([l for l in r0["lots"] if l["ticker"] != "VHM"],
                      [l for l in r1["lots"] if l["ticker"] != "VHM"])))

# ── 7b. Cửa sổ thời gian: chưa tới ngày broker credit thì CHƯA áp ───────────────────────────
print("\n[7b] corp action ở TƯƠNG LAI so với asof ⇒ chưa áp")
bk = broker_from_raw("2026-08-05", "0002023347")
r = PH.park_holdings("SpaceX", asof="2026-08-05", broker=bk,
                     corp_actions=[dict(ACT_VHM, broker_effective_ts="2026-08-20T12:00:00")])
check("record hiệu lực 08-20 không áp ở asof 08-05", not r["corp_actions_applied"],
      r["corp_actions_applied"])
check("  …và sổ vẫn lệch (cổng reconcile tiếp tục chặn, đúng ý)",
      not r["reconcile"]["ok"])

# ── 7c. Cửa sổ xám: MUA sau lúc broker credit nhưng TRƯỚC ex_date ⇒ phải gắn UNVERIFIED ─────
# Nhánh này không kích hoạt trong ca VHM thật (không có lệnh VHM nào phiên 08-05), nên phải
# dựng journal tổng hợp — nếu bỏ qua, một nhánh quyết định đi vào production mà chưa từng chạy.
print("\n[7c] cửa sổ xám — mua giữa lúc credit và ex_date")
import csv                                                   # noqa: E402
import shutil                                                # noqa: E402
import tempfile                                              # noqa: E402

tmpdir = tempfile.mkdtemp(prefix="corp_action_selfcheck_")
try:
    def write_journal(rows):
        p = os.path.join(tmpdir, "exec_SpaceX_2026-08-05_journal.csv")
        with open(p, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty",
                        "price", "filled_total", "note", "book", "play_type"])
            w.writerows(rows)

    bk = broker_from_raw("2026-08-05", "0002023347")
    # mua VHM 14:00 ngày 08-05: SAU credit (12:00), TRƯỚC ex (08-06) ⇒ vẫn hưởng quyền nhưng
    # broker credit phần thưởng của nó ở nhịp khác ta không quan sát được.
    write_journal([["2026-08-05T14:00:00", "FILL", "BUY-VHM-99", "VHM", "buy", "99001", "100",
                    "153000", "100", "", "custom30V_parking", "NEUTRAL_park"]])
    r = PH.park_holdings("SpaceX", asof="2026-08-05", broker=bk, exec_dir=tmpdir,
                         corp_actions=[ACT_VHM])
    check("mua trong cửa sổ xám ⇒ VHM gắn UNVERIFIED", "VHM" in r["unverified_tickers"],
          r["unverified_tickers"])
    check("  …có cảnh báo nêu đúng lý do",
          any("cửa sổ" in w or "credit" in w for w in r["warnings"]), r["warnings"][-1:])
    check("  …park_mv_verified LOẠI phần VHM chưa chắc (fail-closed)",
          r["park_mv_verified_vnd"] < r["park_mv_vnd"],
          f"{r['park_mv_verified_vnd']} vs {r['park_mv_vnd']}")

    # đối chứng: mua 08-06 (từ ex_date trở đi) ⇒ KHÔNG hưởng quyền, KHÔNG phải cửa sổ xám
    os.remove(os.path.join(tmpdir, "exec_SpaceX_2026-08-05_journal.csv"))
    p6 = os.path.join(tmpdir, "exec_SpaceX_2026-08-06_journal.csv")
    with open(p6, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
                    "filled_total", "note", "book", "play_type"])
        w.writerow(["2026-08-06T10:00:00", "FILL", "BUY-VHM-98", "VHM", "buy", "98001", "100",
                    "76500", "100", "", "custom30V_parking", "NEUTRAL_park"])
    bk6 = (dict(bk[0], VHM={"qty": 1100, "market_price": 76500.0, "sellable": 500}), 0.0,
           {"source": "selfcheck", "asof": "2026-08-06"})
    r6 = PH.park_holdings("SpaceX", asof="2026-08-06", broker=bk6, exec_dir=tmpdir,
                          corp_actions=[ACT_VHM])
    check("mua ĐÚNG ngày ex ⇒ 1000 (cũ ×2) + 100 (mới, không nhân) = 1100 khớp broker",
          r6["reconcile"]["ok"] and sum(l["qty"] for l in r6["lots"] if l["ticker"] == "VHM") == 1100,
          r6["reconcile"]["mismatches"])
    check("  …KHÔNG bị gắn cửa sổ xám (mua từ ex_date trở đi là bình thường)",
          "VHM" not in r6["unverified_tickers"], r6["unverified_tickers"])
finally:
    shutil.rmtree(tmpdir, ignore_errors=True)

# ── 7d. Record đã nằm TRONG bootstrap (hiệu lực <= snap_ts) ⇒ KHÔNG áp lần hai ───────────────
print("\n[7d] chống áp trùng phần đã có trong bootstrap")
bk = broker_from_raw("2026-08-05", "0002023347")
r = PH.park_holdings("SpaceX", asof="2026-08-05", broker=bk,
                     corp_actions=[dict(ACT_VHM, broker_effective_ts="2026-07-15T12:00:00")])
check("record hiệu lực TRƯỚC snapshot ngày 0 bị bỏ qua (bootstrap đã phản ánh rồi)",
      not r["corp_actions_applied"], r["corp_actions_applied"])
check("  …sổ giữ 500 (không nhân đôi lần hai)",
      sum(l["qty"] for l in r["lots"] if l["ticker"] == "VHM") == 500,
      sum(l["qty"] for l in r["lots"] if l["ticker"] == "VHM"))

# ── 8. TZ: today_ict() phải đúng kể cả khi biến TZ bị gỡ ────────────────────────────────────
print("\n[8] neo TZ tường minh (§16)")
saved = os.environ.pop("TZ", None)
try:
    expect = dt.datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    check("today_ict() == ngày ICT khi KHÔNG có biến TZ", PH.today_ict() == expect,
          f"{PH.today_ict()} != {expect}")
finally:
    if saved is not None:
        os.environ["TZ"] = saved

# ── 9. Đường dẫn không phụ thuộc thư mục chạy ───────────────────────────────────────────────
print("\n[9] độc lập cwd")
cwd = os.getcwd()
try:
    os.chdir("/tmp")
    check("REGISTRY là đường dẫn tuyệt đối, không đổi theo cwd",
          os.path.isabs(CA.REGISTRY) and CA.REGISTRY.endswith("data/corp_actions.json"), CA.REGISTRY)
    check("load_all() chạy được từ /tmp", isinstance(CA.load_all(), list))
finally:
    os.chdir(cwd)

# ── 10. Sổ THẬT đang chạy production ────────────────────────────────────────────────────────
print("\n[10] data/corp_actions.json thật")
real = CA.load_all()


def _raw_by_id():
    """Record THÔ theo id — `validate()` không giữ `decided_by` nên phải đọc lại file gốc.
    Tra theo ID chứ không theo chỉ số mảng: thêm record mới ở đầu file sẽ làm lệch chỉ số."""
    blob = json.load(open(CA.REGISTRY, encoding="utf-8"))
    return {r.get("id"): r for r in (blob.get("actions") or [])}


check("mọi record thật hợp lệ (validate không ném)", True)
vhm = [a for a in real if a["ticker"] == "VHM" and a["ex_date"] == "2026-08-06"]
check("có đúng 1 record VHM ex 2026-08-06", len(vhm) == 1, len(vhm))
if vhm:
    a = vhm[0]
    check("  hệ số = 2,0", a["qty_multiplier"] == 2.0, a["qty_multiplier"])
    check("  broker_effective_ts (08-05) TRƯỚC ex_date (08-06) — thứ tự phản trực giác của ca này",
          a["broker_effective_ts"][:10] < a["ex_date"], a["broker_effective_ts"])
    check("  đã CONFIRMED ⇒ đang áp vào sổ live", a["_status"].upper().startswith("CONFIRMED"))
    check("  có ≥2 nguồn bằng chứng độc lập", len(a["evidence"]) >= 2, len(a["evidence"]))
    check("  ghi rõ decided_by (§20 — user đã ký duyệt chính thức 2026-08-05, xem _status)",
          _raw_by_id().get("VHM-2026-08-06-STOCK-DIVIDEND", {}).get("decided_by") == "user")

# Bất biến áp cho MỌI record đang ÁP VÀO SỔ LIVE — viết theo bất biến chứ không theo danh sách
# mã cụ thể (§23 hệ luận 1: assert lên giá trị sống thì test tự mốc). Thêm record mới mà thiếu
# bằng chứng/ghi công là fail ngay tại đây, không cần ai nhớ sửa test.
for a in CA.load_corp_actions():
    raw = _raw_by_id().get(a["id"], {})
    check(f"  [{a['id']}] có ≥2 nguồn bằng chứng độc lập", len(a["evidence"]) >= 2,
          len(a["evidence"]))
    check(f"  [{a['id']}] khai decided_by (§20: 'user' chỉ khi user THẬT ký, không thì 'agent')",
          raw.get("decided_by") in ("user", "agent"), raw.get("decided_by"))
    check(f"  [{a['id']}] hệ số > 1 và ≤ 10 (chặn lỗi gõ nhầm thang, vd 15 thay vì 1,15)",
          1.0 < a["qty_multiplier"] <= 10.0, a["qty_multiplier"])

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
sys.exit(1 if FAIL else 0)
