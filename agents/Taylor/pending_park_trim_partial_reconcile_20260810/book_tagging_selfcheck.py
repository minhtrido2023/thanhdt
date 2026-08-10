# -*- coding: utf-8 -*-
"""Self-check cho P0 book-tagging + sổ lô theo book + L1 park-trim.

Ba thứ được kiểm, mỗi ca là MỘT CÁCH LÀM SAI CÓ THẬT (không phải test cho có):

  A. `trading_bot.executor.Executor._journal()` — thay đổi production 2026-08-04: thêm 2 cột
     `book`/`play_type` TRƯỚC cột `note`. Kiểm cả tương thích ngược của các reader positional.
  B. `mike/bin/park_holdings.py` — dựng lại vị thế theo book (bootstrap → FIFO tiến).
  C. `mike/bin/compute_park_trim.py` — L1: các cổng an toàn phải CHẶN đúng chỗ.

Ca B2 (qty tích luỹ theo child_oid) và B4/B5 (không tag book / lệch broker) là 2 lỗi mà thiết
kế §F2/§F4 nói thẳng là dạng IM LẶNG — sai mà không ai thấy. Ca C1-C4 là các ranh giới tiền:
excluded_tickers, CAPIT, UNVERIFIED, reconcile lệch.

MÔI TRƯỜNG (§19 verify-before-done, §16 TZ): `_journal` gọi `now_ict()` và `park_holdings`
dùng `datetime.now(ZoneInfo(...))`. Selfcheck này KHÔNG được phụ thuộc TZ của người chạy —
chạy lại bằng cả 3 cách trước khi tin:
    python3 book_tagging_selfcheck.py
    env -u TZ python3 book_tagging_selfcheck.py
    TZ=America/New_York python3 book_tagging_selfcheck.py

Run: python3 book_tagging_selfcheck.py   (exit 0 = pass hết)
"""
import csv
import datetime as dt
import glob
import json
import os
import shutil
import sys
import tempfile

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)
sys.path.insert(0, os.path.join(WC_ROOT, "mike", "bin"))

from trading_bot.config import DEFAULTS, EXEC_DIR                      # noqa: E402
from trading_bot.plan import PlannedOrder, TradePlan                   # noqa: E402
from trading_bot.executor import Executor                              # noqa: E402
from park_holdings import park_holdings, norm_book, _fill_deltas       # noqa: E402
from compute_park_trim import compute_trim                             # noqa: E402

TAG = "booktag"   # tag riêng: Executor.__init__ nạp state.json theo đường dẫn MẶC ĐỊNH trước
                  # khi test kịp chuyển hướng ⇒ phải dọn file cũ ngay lúc load module (§7).
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*_journal.csv")):
    os.remove(_f)
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*_state.json")):
    os.remove(_f)

fails = []


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


class FakeBroker:
    name = "fake"

    def get_quote(self, sym):
        return None

    def get_cash(self):
        return 10_000_000_000

    def poll_orders(self):
        return {}


# ════════════════════════════════════════ A. Executor._journal (thay đổi production)
print("A. Executor._journal — 2 cột book/play_type")
orders = [PlannedOrder(id="BUY-VPB-01", ticker="VPB", side="buy", qty=1000, ref_price=25000,
                       book="custom30V_parking", play_type="NEUTRAL_park"),
          PlannedOrder(id="BUY-CSV-01", ticker="CSV", side="buy", qty=500, ref_price=19000,
                       book="LAG")]                       # play_type để TRỐNG có chủ ý
plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="tst",
                 strategy_version="0", state=3, state_name="NEUTRAL", nav_basis={},
                 orders=orders, account=TAG, created_at="2099-01-01T00:00:00")
cfg = dict(DEFAULTS); cfg.update({"mode": "paper", "fill_timing_enabled": False})
ex = Executor(plan, FakeBroker(), cfg)
ex._journal("FILL", orders[0], "OID1", 1000, 25000, note="ghi chú, có dấu phẩy, và \"ngoặc\"")
ex._journal("FILL", orders[1], "OID2", 500, 19000)
ex._journal("NO_QUOTE", None, note="event không gắn với order nào")

with open(ex.journal_file, newline="", encoding="utf-8") as f:
    rows = list(csv.reader(f))
hdr, body = rows[0], rows[1:]
check("A1 header 12 cột, book/play_type NGAY TRƯỚC note",
      hdr == ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
              "filled_total", "book", "play_type", "note"], str(hdr))
with open(ex.journal_file, newline="", encoding="utf-8") as f:
    drows = list(csv.DictReader(f))
check("A2 book/play_type ghi ĐÚNG giá trị của PlannedOrder",
      drows[0]["book"] == "custom30V_parking" and drows[0]["play_type"] == "NEUTRAL_park"
      and drows[1]["book"] == "LAG" and drows[1]["play_type"] == "",
      f"{drows[0]['book']}/{drows[0]['play_type']}, {drows[1]['book']}/{drows[1]['play_type']}")
check("A3 note vẫn là cột CUỐI và giữ nguyên dấu phẩy/ngoặc",
      drows[0]["note"] == 'ghi chú, có dấu phẩy, và "ngoặc"', drows[0]["note"])
check("A4 event=None-order không crash, book/play_type rỗng",
      drows[2]["event"] == "NO_QUOTE" and drows[2]["book"] == "" and drows[2]["play_type"] == "",
      str(drows[2]))
# Reader positional hiện có (churn_guard/tick_retry/extreme_regime dùng row[1]) KHÔNG được vỡ:
check("A5 reader positional cũ (row[1] == event) vẫn đúng — chỉ số 0-8 không đổi",
      [r[1] for r in body] == ["FILL", "FILL", "NO_QUOTE"], str([r[1] for r in body]))
check("A6 số cột mỗi dòng = 12 (không lệch header)",
      all(len(r) == 12 for r in body), str([len(r) for r in body]))

# A7: file 10 cột do code CŨ tạo, executor khởi động lại giữa phiên sau khi deploy → PHẢI giữ
# layout cũ, tuyệt đối không ghi 12 giá trị dưới header 10 cột (sẽ đọc `note` thành `book`).
legacy_path = os.path.join(EXEC_DIR, f"exec_{TAG}-legacy_2099-01-01_journal.csv")
with open(legacy_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
                "filled_total", "note"])
    w.writerow(["2099-01-01T09:00:00", "PLACE", "BUY-VPB-01", "VPB", "buy", "OID0", 1000,
                25000, 0, "ghi chú cũ"])
ex_legacy = Executor(plan, FakeBroker(), cfg)
ex_legacy.journal_file = legacy_path
ex_legacy._journal("FILL", orders[0], "OID9", 1000, 25000, note="dòng ghi bởi code MỚI")
with open(legacy_path, newline="", encoding="utf-8") as f:
    lrows = list(csv.reader(f))
check("A7 journal CŨ 10 cột + code mới → vẫn 10 cột, note vẫn ở cột cuối (không lệch cột)",
      all(len(r) == 10 for r in lrows) and lrows[-1][-1] == "dòng ghi bởi code MỚI",
      str([len(r) for r in lrows]))
with open(legacy_path, newline="", encoding="utf-8") as f:
    check("A7b DictReader trên file legacy vẫn đọc `note` đúng, `book` trống (không nuốt nhầm)",
          all(r.get("note") and not r.get("book") for r in csv.DictReader(f)))


# ════════════════════════════════════════ B. park_holdings — dựng lại sổ
print("\nB. park_holdings — bootstrap + FIFO tiến")

TMP = tempfile.mkdtemp(prefix="booktag_")
PLANS, EXECS = os.path.join(TMP, "plans"), os.path.join(TMP, "execs")
os.makedirs(PLANS); os.makedirs(EXECS)
DAY0, D1 = "2026-08-04", "2026-08-05"
SNAP_TS = "2026-08-03T19:10:00"


def write_bootstrap(label, positions, status="APPROVED by selfcheck", reconcile_ok=True):
    json.dump({"_schema": "bootstrap_book_snapshot/v1", "_status": status,
               "account_label": label, "day0_date": DAY0, "reconcile_ok": reconcile_ok,
               "broker_source": {"ts": SNAP_TS}, "positions": positions},
              open(os.path.join(PLANS, f"bootstrap_book_snapshot_{label}_20260804.json"),
                   "w", encoding="utf-8"), ensure_ascii=False)


def write_journal(label, date, rows, cols12=True):
    """rows = list dict. cols12=False → ghi journal CŨ 10 cột (không có book/play_type)."""
    hdr = ["ts", "event", "parent_id", "ticker", "side", "child_oid", "qty", "price",
           "filled_total"] + (["book", "play_type"] if cols12 else []) + ["note"]
    with open(os.path.join(EXECS, f"exec_{label}_{date}_journal.csv"), "w", newline="",
              encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=hdr, extrasaction="ignore")
        w.writeheader()
        for r in rows:
            w.writerow(r)


def fill(ts, tk, side, oid, qty, px, book="", play=""):
    return {"ts": ts, "event": "FILL", "parent_id": f"{side.upper()}-{tk}-01", "ticker": tk,
            "side": side, "child_oid": oid, "qty": qty, "price": px, "filled_total": qty,
            "book": book, "play_type": play, "note": ""}


def bpos(**kw):
    return {tk: {"qty": q, "market_price": px, "sellable": q} for tk, (q, px) in kw.items()}


# — B1. journal CŨ 10 cột: đọc được, book rỗng, KHÔNG crash
write_bootstrap("SpaceX", [{"ticker": "ACB", "qty": 1000, "book": "custom30V_parking",
                            "entry_date": "2026-07-01", "cost_price_vnd": 22000}])
write_journal("SpaceX", D1, [fill("2026-08-05T09:30:00", "MBB", "buy", "O1", 500, 24000)],
              cols12=False)
h = park_holdings("SpaceX", D1, PLANS, EXECS,
                  broker=(bpos(ACB=(1000, 22550), MBB=(500, 24000)), 5e6, {"source": "fake"}))
check("B1 journal cũ 10 cột đọc được, không crash, mua không tag → sổ UNTAGGED (không tự đoán PARK)",
      h["reconcile"]["ok"] and h["by_book"].get("UNTAGGED", {}).get("qty") == 500
      and h["park_mv_vnd"] == 1000 * 22550, str({k: v["qty"] for k, v in h["by_book"].items()}))

# — B2. BẪY SỐ 1: cùng child_oid 3 dòng qty TĂNG DẦN → chỉ được cộng 1 lần
write_bootstrap("SpaceX", [])
write_journal("SpaceX", D1, [
    fill("2026-08-05T09:30:00", "ACB", "buy", "O1", 100, 22000, "custom30V_parking"),
    fill("2026-08-05T09:31:00", "ACB", "buy", "O1", 200, 22000, "custom30V_parking"),
    fill("2026-08-05T09:32:00", "ACB", "buy", "O1", 300, 22000, "custom30V_parking"),
])
h = park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(ACB=(300, 22000)), 0, {}))
tot = sum(l["qty"] for l in h["lots"])
check("B2 3 dòng FILL cùng child_oid (100→200→300) cộng đúng 300, KHÔNG phải 600",
      tot == 300 and h["reconcile"]["ok"], f"tổng={tot}")

# — B3. VPB nằm CẢ LAG lẫn PARK; bán lô LAG → PARK KHÔNG đổi (cốt lõi của §A7)
write_bootstrap("SpaceX", [])
write_journal("SpaceX", D1, [
    fill("2026-08-05T09:30:00", "VPB", "buy", "O1", 1000, 25000, "LAG"),
    fill("2026-08-05T09:31:00", "VPB", "buy", "O2", 2000, 25000, "custom30V_parking"),
    fill("2026-08-05T14:00:00", "VPB", "sell", "O3", 600, 25500, "LAG"),
])
h = park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(VPB=(2400, 25500)), 0, {}))
check("B3 bán 600cp book=LAG → PARK giữ nguyên 2000cp, LAG còn 400cp",
      h["by_book"]["PARK"]["qty"] == 2000 and h["by_book"]["LAG"]["qty"] == 400
      and h["reconcile"]["ok"] and not h["unverified_tickers"],
      str({k: v["qty"] for k, v in h["by_book"].items()}))

# — B3b. Cùng dữ liệu nhưng bán KHÔNG tag book → phải FIFO oldest-first + cờ UNVERIFIED
write_journal("SpaceX", D1, [
    fill("2026-08-05T09:30:00", "VPB", "buy", "O1", 1000, 25000, "LAG"),
    fill("2026-08-05T09:31:00", "VPB", "buy", "O2", 2000, 25000, "custom30V_parking"),
    fill("2026-08-05T14:00:00", "VPB", "sell", "O3", 600, 25500, ""),
])
h = park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(VPB=(2400, 25500)), 0, {}))
check("B4 bán KHÔNG có tag book → FIFO oldest-first + VPB gắn cờ UNVERIFIED",
      "VPB" in h["unverified_tickers"] and h["by_book"]["PARK"]["qty"] == 2000
      and h["by_book"]["LAG"]["qty"] == 400,
      f"unverified={h['unverified_tickers']}")
check("B4b park_mv_verified LOẠI phần UNVERIFIED (cấm dùng số chưa đối soát sinh lệnh)",
      h["park_mv_vnd"] > 0 and h["park_mv_verified_vnd"] == 0,
      f"{h['park_mv_vnd']} vs {h['park_mv_verified_vnd']}")

# — B5. Σ lô ≠ openQuantity → BÁO LỆCH, KHÔNG tự sửa lô cho khớp (§5)
write_bootstrap("SpaceX", [])
write_journal("SpaceX", D1, [fill("2026-08-05T09:30:00", "ACB", "buy", "O1", 300, 22000,
                                  "custom30V_parking")])
h = park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(ACB=(500, 22000)), 0, {}))
check("B5 sổ 300 vs broker 500 → reconcile.ok=False, sổ GIỮ NGUYÊN 300 (không tự nống lên 500)",
      not h["reconcile"]["ok"] and sum(l["qty"] for l in h["lots"]) == 300
      and h["reconcile"]["mismatches"][0]["diff"] == -200,
      str(h["reconcile"]["mismatches"]))

# — B6. §12: hai account CÙNG ngày phải cho hai kết quả KHÁC nhau
write_bootstrap("SpaceX", [{"ticker": "ACB", "qty": 1000, "book": "custom30V_parking",
                            "entry_date": "2026-07-01", "cost_price_vnd": 22000}])
write_bootstrap("ZaloPay", [{"ticker": "BID", "qty": 200, "book": "custom30V_parking",
                             "entry_date": "2026-07-01", "cost_price_vnd": 38000},
                            {"ticker": "DGC", "qty": 10000, "book": "EXCLUDED",
                             "entry_date": "2026-06-26", "cost_price_vnd": 47775}])
write_journal("SpaceX", D1, [])
write_journal("ZaloPay", D1, [])
hA = park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(ACB=(1000, 22550)), 1e6, {}))
hB = park_holdings("ZaloPay", D1, PLANS, EXECS,
                   broker=(bpos(BID=(200, 38250), DGC=(10000, 39400)), 2e6, {}))
check("B6 2 account cùng ngày → 2 kết quả KHÁC nhau (giống hệt = quên lọc account, §12)",
      hA["park_mv_vnd"] != hB["park_mv_vnd"] and hA["account_no"] != hB["account_no"],
      f"{hA['park_mv_vnd']:,.0f} vs {hB['park_mv_vnd']:,.0f}")
check("B6b DGC (excluded) vào sổ EXCLUDED, KHÔNG vào PARK",
      hB["by_book"]["EXCLUDED"]["qty"] == 10000 and "DGC" not in
      {l["ticker"] for l in hB["park_lots"]}, str(sorted(hB["by_book"])))

# — B7. bootstrap CHƯA duyệt → phải TỪ CHỐI, không âm thầm dùng
write_bootstrap("SpaceX", [], status="DE XUAT — chua duyet")
try:
    park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(), 0, {}))
    check("B7 bootstrap chưa APPROVED → phải từ chối", False, "chạy lọt")
except SystemExit as e:
    check("B7 bootstrap chưa APPROVED → từ chối, không dùng làm ngày 0", "CHƯA được duyệt" in str(e))
write_bootstrap("SpaceX", [], reconcile_ok=False)
try:
    park_holdings("SpaceX", D1, PLANS, EXECS, broker=(bpos(), 0, {}))
    check("B7b bootstrap reconcile_ok=false → phải từ chối", False, "chạy lọt")
except SystemExit as e:
    check("B7b bootstrap reconcile_ok=false → từ chối", "reconcile_ok=false" in str(e))

check("B8 norm_book ánh xạ đúng tên book của plan",
      norm_book("custom30V_parking") == "PARK" and norm_book("LAG") == "LAG"
      and norm_book("") == "" and norm_book("CAPIT") == "CAPIT")


# ════════════════════════════════════════ C. compute_park_trim — cổng an toàn
print("\nC. compute_park_trim — L1, các cổng phải CHẶN đúng chỗ")

ADV_BIG = (5_000_000_000.0, "2026-08-05", None)     # ADV thừa sức, không bao giờ binding
DAYCAP = 500_000_000_000.0

# Rổ MỤC TIÊU + giá bơm TAY (2026-08-07, công thức đổi sang `order_i = mv_i − tgt_i`).
# Trước đây khối C không cần rổ; nay `compute_trim` suy target từ rổ custom30V ⇒ nếu không bơm,
# test sẽ phụ thuộc CSV rổ thật + quote LIVE (đúng bẫy `verify-before-done`: kết quả đổi theo
# ngày chạy và theo mạng). Rổ dưới đây cho ACB/BID target BẰNG NHAU ⇒ mọi khẳng định về đối
# xứng/không-dồn-phần-dư kiểm được bằng tay.
C_BASKET = {"ACB": 0.30, "BID": 0.30, "VCB": 0.40}
C_PX = {"ACB": 20_000, "BID": 40_000, "VCB": 60_000}


def c_price_fn(tk):
    return (C_PX.get(tk), None) if tk in C_PX else (None, "không có giá test")


def adv_ok(tk, asof):
    return ADV_BIG


def fake_holdings(park, cash, books=None, unver=(), excluded=(), ok=True, sellable=None):
    lots, positions = [], {}
    for tk, (q, px) in park.items():
        lots.append({"ticker": tk, "book": "PARK", "play_type": "NEUTRAL_park",
                     "entry_date": "2026-07-01", "qty": q, "price": px, "source": "bootstrap",
                     "market_price": px, "mv_vnd": q * px})
        positions[tk] = {"qty": q, "market_price": px,
                         "sellable": (sellable or {}).get(tk, q)}
    for tk, (q, px, bk) in (books or {}).items():
        positions[tk] = {"qty": q, "market_price": px, "sellable": q}
    return {"account_label": "SpaceX", "asof": "2026-08-05",
            "park_mv_vnd": sum(l["mv_vnd"] for l in lots),
            "park_mv_verified_vnd": sum(l["mv_vnd"] for l in lots),
            "cash_available_vnd": cash,
            # mẫu số pool L1 = totalCash (sửa 2026-08-09); ca ở file này không kiểm phần đó nên
            # để bằng cash — giữ nguyên ý nghĩa cũ của mọi ca. Kiểm riêng: T18* trong
            # mike/bin/compute_park_trim_selfcheck.py.
            "cash_total_vnd": cash, "cash_dividend_receiving_vnd": 0.0,
            "cash_debt_vnd": 0.0, "cash_basis": "total_cash",
            "park_lots": lots, "broker_positions": positions,
            "excluded_tickers": list(excluded), "unverified_tickers": list(unver),
            "reconcile": {"ok": ok, "mismatches": [] if ok else [{"ticker": "ACB", "diff": -200}]}}


def trim(h, target=0.80, **kw):
    kw.setdefault("share_override", 0.5)
    kw.setdefault("adv_fn", adv_ok)
    kw.setdefault("day_cap_override", DAYCAP)
    kw.setdefault("basket_override", C_BASKET)
    kw.setdefault("price_fn", c_price_fn)
    return compute_trim("SpaceX", "2026-08-05", target, holdings=h, **kw)

# C1. reconcile LỆCH — HAI HƯỚNG, HAI HÀNH VI (đổi 2026-08-10, xem
#     agents/Taylor/pending_park_trim_partial_reconcile_20260810/README.md).
#     Fixture gốc dùng diff=-200 (BROKER NHIỀU HƠN) và kỳ vọng chặn cả tài khoản; hành vi đó
#     chính là thứ làm mất phiên entry chuẩn 08-06. Giữ nguyên phép thử fail-closed cho hướng
#     NGUY HIỂM (diff>0), thêm phép thử mới cho hướng corp-action (diff<0).

# C1a. diff > 0 (SỔ NHIỀU HƠN broker — ghost order / fill sót journal) → vẫn chặn cả tài khoản.
h_over = fake_holdings({"ACB": (1000, 22000)}, 5_000_000, ok=False)
h_over["reconcile"]["mismatches"] = [{"ticker": "ACB", "ledger_qty": 1200,
                                      "broker_qty": 1000, "diff": 200}]
r = trim(h_over)
check("C1a sổ NHIỀU HƠN broker (diff>0) → BLOCKED_RECONCILE, 0 lệnh",
      r["decision"] == "BLOCKED_RECONCILE" and not r["orders"], r["decision"])

# C1b. diff < 0 (broker NHIỀU HƠN — chữ ký corp action) trên mã DUY NHẤT đang giữ → không còn
#      mã nào bán được, nhưng KHÔNG được chặn bằng BLOCKED_RECONCILE nữa.
r = trim(fake_holdings({"ACB": (1000, 22000)}, 5_000_000, ok=False))
check("C1b broker NHIỀU HƠN sổ (diff<0) → KHÔNG chặn cả tài khoản nữa",
      r["decision"] != "BLOCKED_RECONCILE" and r.get("reconcile_partial") is True,
      f"{r['decision']} partial={r.get('reconcile_partial')}")
check("C1b mã lệch bị CẤM bán dù caller KHÔNG khai unverified_tickers",
      all(o["ticker"] != "ACB" for o in r["orders"])
      and "ACB" in (r.get("unverified_tickers") or []),
      f"orders={[o['ticker'] for o in r['orders']]} unver={r.get('unverified_tickers')}")

# C1c. diff < 0 trên MỘT mã, còn mã khác khớp tuyệt đối → mã khớp VẪN sinh lệnh (chính là điều
#      đáng lẽ cứu được 115,68tr ngày 08-06), mã lệch thì không.
h_mix = fake_holdings({"ACB": (1000, 22000), "BID": (10000, 30000)}, 5_000_000, ok=False)
h_mix["reconcile"]["mismatches"] = [{"ticker": "ACB", "ledger_qty": 1000,
                                     "broker_qty": 2000, "diff": -1000}]
h_mix["broker_positions"]["ACB"]["qty"] = 2000
r = trim(h_mix)
_tks = [o["ticker"] for o in r["orders"]]
check("C1c 1 mã lệch KHÔNG chặn mã khớp — BID vẫn bán được, ACB thì không",
      r["decision"] == "TRIM" and "BID" in _tks and "ACB" not in _tks, f"{r['decision']} {_tks}")

# C1d. mẫu số pool phải được hiệu chỉnh theo SỐ LƯỢNG BROKER — nếu không, tgt_i thiếu ⇒ OVER-TRIM.
#      Chứng minh NGƯỢC: pool ở chế độ PARTIAL phải bằng pool khi sổ đã đúng hoàn toàn.
h_fixed = fake_holdings({"ACB": (2000, 22000), "BID": (10000, 30000)}, 5_000_000)
r_fixed = trim(h_fixed)
check("C1d pool PARTIAL == pool khi sổ đã đúng (không còn lệch ⇒ không over-trim)",
      abs(r.get("pool_vnd", 0) - r_fixed.get("pool_vnd", -1)) < 1.0,
      f"partial={r.get('pool_vnd')} fixed={r_fixed.get('pool_vnd')} "
      f"adj={r.get('reconcile_partial_mv_adj_vnd')}")

# C1e. lệch mà KHÔNG định giá được phần chênh (thiếu marketPrice broker) ⇒ quay về fail-closed.
h_nopx = fake_holdings({"ACB": (1000, 22000), "BID": (10000, 30000)}, 5_000_000, ok=False)
h_nopx["reconcile"]["mismatches"] = [{"ticker": "ACB", "ledger_qty": 1000,
                                      "broker_qty": 2000, "diff": -1000}]
h_nopx["broker_positions"]["ACB"]["market_price"] = 0
r = trim(h_nopx)
check("C1e lệch nhưng KHÔNG có marketPrice để hiệu chỉnh mẫu số → BLOCKED_RECONCILE",
      r["decision"] == "BLOCKED_RECONCILE" and not r["orders"], r["decision"])

# C2. Trong band → KHÔNG trim (ngưỡng 0,005 × pool)
r = trim(fake_holdings({"ACB": (10000, 20000)}, 50_000_000))   # park 200tr, pool 250tr, 80%
check("C2 PARK = đúng target → NO_TRIM (không sinh lệnh vô cớ)",
      r["decision"] == "NO_TRIM" and not r["orders"],
      f"{r['decision']} park={r['park_mv_vnd']:,.0f} target={r.get('target_park_vnd', 0):,.0f}")

# C3. Vượt trần → trim pro-rata; excluded/CAPIT/UNVERIFIED không bao giờ bị đụng
h = fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000,
                  books={"SAB": (1000, 50000, "CAPIT"), "DGC": (10000, 39400, "EXCLUDED")})
r = trim(h)
sold = {o["ticker"] for o in r["orders"]}
check("C3 vượt trần → TRIM trên ĐÚNG mã PARK; CAPIT/EXCLUDED không có trong lệnh",
      r["decision"] == "TRIM" and sold == {"ACB", "BID"}, f"{r['decision']} {sorted(sold)}")
tot = sum(o["value_vnd"] for o in r["orders"])
# 2026-08-07: công thức đổi sang `mv_i − tgt_i`. Bất biến MỚI (thay cho "Σ ≤ mức vượt trần" và
# "tỷ lệ theo trọng số SỐNG" — hai khẳng định đó mô tả công thức pro-rata ĐÃ BỊ THAY):
#   · mỗi lệnh ≤ khoảng cách tới target của CHÍNH mã đó (không mã nào gánh phần của mã khác);
#   · ACB/BID có trọng số mục tiêu BẰNG NHAU (0,30) ⇒ want bằng nhau ⇒ đối xứng;
#   · Σ ≤ tổng lệch cấu trúc, và LỚN HƠN mức vượt trần 72tr — đúng thiết kế P1 sell-only
#     (phần chênh là trọng số của VCB, mã trong rổ mà ta CHƯA MUA).
w_acb = next(o for o in r["orders"] if o["ticker"] == "ACB")
w_bid = next(o for o in r["orders"] if o["ticker"] == "BID")
check("C3b mỗi lệnh ≤ (mv − tgt) của chính mã đó; ACB/BID cùng w' ⇒ want bằng nhau",
      all(o["value_vnd"] <= o["mv_vnd"] - o["target_vnd"] + 1 for o in r["orders"])
      and abs(w_acb["want_vnd"] - w_bid["want_vnd"]) < 1
      and abs(w_acb["weight_target"] - 0.30) < 1e-12,
      f"want ACB={w_acb['want_vnd']:,.0f} BID={w_bid['want_vnd']:,.0f}")
check("C3b2 Σ lệnh ≤ lệch cấu trúc, và > mức vượt trần (P1 sell-only ⇒ cảnh báo DƯỚI target)",
      tot <= r["structural_excess_vnd"] + 1 and tot > -r["delta_vnd"]
      and r["underpark_after_vnd"] > 0
      and any("DƯỚI target" in n for n in r["notes"]),
      f"Σ={tot:,.0f} lệch cấu trúc={r['structural_excess_vnd']:,.0f} "
      f"vượt trần={-r['delta_vnd']:,.0f}")

# C3c. excluded_tickers LỌT vào sổ PARK (sai bất biến) → mã đó vẫn KHÔNG được trim
h = fake_holdings({"ACB": (10000, 20000), "DGC": (5000, 40000)}, 10_000_000, excluded=("DGC",))
r = trim(h)
check("C3c DGC lỡ nằm trong sổ PARK vẫn KHÔNG bị trim (excluded_tickers là ranh giới cứng)",
      "DGC" not in {o["ticker"] for o in r["orders"]}
      and any(b["ticker"] == "DGC" for b in r["blocked"]), str(r["blocked"]))

# C4. UNVERIFIED → cấm sinh lệnh cho mã đó (§21)
h = fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000, unver=("BID",))
r = trim(h)
check("C4 mã UNVERIFIED bị loại khỏi lệnh trim",
      "BID" not in {o["ticker"] for o in r["orders"]}
      and any(b["ticker"] == "BID" for b in r["blocked"]), str(r["blocked"]))

# C5. ADV fail-closed — không đo được / cũ / ≤0 đều phải CHẶN mã đó
for label, advret in [("lỗi đọc", (0.0, None, "cache lỗi")),
                      ("ADV=0", (0.0, "2026-08-05", None)),
                      ("ADV cũ 60 ngày", (5e9, "2026-06-06", None))]:
    r = trim(fake_holdings({"ACB": (10000, 20000)}, 10_000_000),
             adv_fn=lambda t, a, _r=advret: _r)
    check(f"C5 ADV {label} → fail-closed, không trim mã đó",
          not r["orders"] and r["blocked"], f"{r['decision']} {r['blocked']}")

# C6. trần per-name (= gate LAG live) phải CẮT khi ADV mỏng, phần dư KHÔNG dồn sang mã khác
h = fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000)
r = trim(h)                     # chân đối chứng: cùng holdings, ADV thừa sức cho CẢ HAI mã
r_thin = trim(h, adv_fn=lambda t, a: ((10_000_000.0 if t == "ACB" else 5e9),
                                      "2026-08-05", None))
acb = [o for o in r_thin["orders"] if o["ticker"] == "ACB"]
bid_thin = [o for o in r_thin["orders"] if o["ticker"] == "BID"]
bid_full = [o for o in r["orders"] if o["ticker"] == "BID"]
check("C6 ADV mỏng → ACB bị trần per-name cắt (hoặc chặn hẳn), BID KHÔNG được nhận thêm phần dư",
      (not acb or acb[0]["adv_capped"]) and bid_thin and bid_full
      and bid_thin[0]["qty"] == bid_full[0]["qty"],
      f"ACB={acb} BID {bid_thin[0]['qty'] if bid_thin else None} vs {bid_full[0]['qty'] if bid_full else None}")

# C6b-C6d. Rổ MỤC TIÊU: mã rớt rổ bán sạch, BANNED bị loại, chuẩn hoá theo tập khả thi.
#   (Bộ đầy đủ 39 ca ở `mike/bin/compute_park_trim_selfcheck.py`; 3 ca dưới giữ ở đây để khối C
#   vẫn tự đứng được như một cổng hồi quy của chính file này.)
h_out = fake_holdings({"ACB": (10000, 20000), "SHS": (200, 15700)}, 10_000_000)
r_out = trim(h_out, price_fn=lambda tk: ((15_700, None) if tk == "SHS" else c_price_fn(tk)))
o_shs = [o for o in r_out["orders"] if o["ticker"] == "SHS"]
check("C6b mã RỚT RỔ (SHS, ngoài rổ mục tiêu) → target 0 → bán SẠCH 200cp",
      o_shs and o_shs[0]["qty"] == 200 and o_shs[0]["target_vnd"] == 0
      and o_shs[0]["in_basket"] is False, str(o_shs))
r_ban = trim(fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000),
             basket_override={"ACB": 0.30, "BID": 0.30, "PC1": 0.40},
             price_fn=lambda tk: ((30_000, None) if tk == "PC1" else c_price_fn(tk)))
check("C6c PC1 (BANNED) trong rổ mục tiêu → bị loại, trọng số chuẩn hoá sang ACB/BID (0,5/0,5)",
      "PC1" not in r_ban["target_weights"]
      and abs(r_ban["target_weights"]["ACB"] - 0.5) < 1e-12
      and any(d["ticker"] == "PC1" and "BANNED" in d["reason"]
              for d in r_ban["basket_dropped"]), str(r_ban["target_weights"]))
r_lot = trim(fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000),
             basket_override={"ACB": 0.30, "BID": 0.30, "TIN": 0.40},
             price_fn=lambda tk: ((5_000_000, None) if tk == "TIN" else c_price_fn(tk)))
check("C6d mã có target < 1 lô bị loại + trọng số chuẩn hoá lại (no silent cap: có ghi lý do)",
      "TIN" not in r_lot["target_weights"]
      and abs(r_lot["target_weights"]["BID"] - 0.5) < 1e-12
      and any(d["ticker"] == "TIN" and "1 lô" in d["reason"] for d in r_lot["basket_dropped"]),
      str(r_lot["basket_dropped"]))

# C7. CP chưa về T+2 → không đề xuất bán quá phần sellable
h = fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000,
                  sellable={"ACB": 200})
r = trim(h)
acb = [o for o in r["orders"] if o["ticker"] == "ACB"]
check("C7 không bán quá số CP đã về (sellable) — ràng buộc T+2",
      (not acb) or acb[0]["qty"] <= 200, str(acb))

# C8. trần TỔNG/phiên (engine _etf_day_cap) chặn khi mức vượt lớn hơn trần
r = trim(fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000),
         day_cap_override=1_000_000.0)
check("C8 trần TỔNG/phiên binding → trim_total bị kẹp về trần",
      r["trim_total_vnd"] == 1_000_000.0 and r.get("day_cap_binding"),
      f"trim_total={r['trim_total_vnd']:,.0f}")
r = trim(fake_holdings({"ACB": (10000, 20000)}, 10_000_000), day_cap_override=0.0)
check("C8b không đo được trần TỔNG (=0) → BLOCKED_DAYCAP, không trim",
      r["decision"] == "BLOCKED_DAYCAP" and not r["orders"], r["decision"])

# C9. không dựng được danh sách account live → fail-closed
r = trim(fake_holdings({"ACB": (10000, 20000)}, 10_000_000), share_override=None)
check("C9 share tính được từ config thật (hoặc fail-closed nếu không) — không bao giờ mặc định 1.0",
      (r["decision"] != "TRIM") or (0 < r["adv_share"] <= 1.0),
      f"{r['decision']} share={r.get('adv_share')}")

# C10. FIFO trong mã: lô CŨ NHẤT bị tiêu thụ trước
h = fake_holdings({"ACB": (10000, 20000)}, 10_000_000)
h["park_lots"] = [dict(h["park_lots"][0], qty=4000, entry_date="2026-07-20",
                       mv_vnd=4000 * 20000),
                  dict(h["park_lots"][0], qty=6000, entry_date="2026-07-01",
                       mv_vnd=6000 * 20000)]
r = trim(h)
if r["orders"]:
    check("C10 FIFO trong mã — lô entry_date cũ nhất (07-01) bị tiêu thụ trước",
          r["orders"][0]["fifo_lots"][0]["entry_date"] == "2026-07-01",
          str(r["orders"][0]["fifo_lots"]))
else:
    check("C10 FIFO trong mã", False, "không có lệnh để kiểm")


# ════════════════════════════════════════ D. TZ (§16) — không được phụ thuộc TZ người chạy
print("\nD. Phụ thuộc môi trường")
check("D1 park_holdings neo TZ tường minh (ZoneInfo), không dùng datetime.now() trần",
      "ZoneInfo(\"Asia/Ho_Chi_Minh\")" in open(
          os.path.join(WC_ROOT, "mike", "bin", "park_holdings.py"), encoding="utf-8").read())
_seen = {}
for _tz in (None, "America/New_York", "UTC"):
    env_backup = os.environ.get("TZ")
    if _tz is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = _tz
    import importlib
    import park_holdings as _ph
    importlib.reload(_ph)
    _seen[_tz] = _ph.today_ict()
    if env_backup is None:
        os.environ.pop("TZ", None)
    else:
        os.environ["TZ"] = env_backup
check("D2 today_ict() giống nhau dưới TZ rỗng / New_York / UTC", len(set(_seen.values())) == 1,
      str(_seen))

shutil.rmtree(TMP, ignore_errors=True)
for _f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}*")):
    os.remove(_f)

print("\n" + ("✅ TẤT CẢ PASS" if not fails else f"❌ {len(fails)} FAIL: {fails}"))
sys.exit(1 if fails else 0)
