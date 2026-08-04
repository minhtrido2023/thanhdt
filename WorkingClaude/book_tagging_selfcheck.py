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
            "cash_available_vnd": cash, "park_lots": lots, "broker_positions": positions,
            "excluded_tickers": list(excluded), "unverified_tickers": list(unver),
            "reconcile": {"ok": ok, "mismatches": [] if ok else [{"ticker": "ACB", "diff": -200}]}}


def trim(h, target=0.80):
    return compute_trim("SpaceX", "2026-08-05", target, holdings=h, share_override=0.5,
                        adv_fn=adv_ok, day_cap_override=DAYCAP)

# C1. reconcile LỆCH → không đề xuất gì (fail-closed)
r = trim(fake_holdings({"ACB": (1000, 22000)}, 5_000_000, ok=False))
check("C1 sổ lệch broker → BLOCKED_RECONCILE, 0 lệnh",
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
check("C3 vượt trần → TRIM pro-rata trên ĐÚNG mã PARK; CAPIT/EXCLUDED không có trong lệnh",
      r["decision"] == "TRIM" and sold == {"ACB", "BID"}, f"{r['decision']} {sorted(sold)}")
tot = sum(o["value_vnd"] for o in r["orders"])
check("C3b Σ trim ≤ mức vượt trần và tỷ lệ giữa 2 mã ≈ trọng số hiện tại",
      tot <= -r["delta_vnd"] + 1 and abs(
          next(o["weight_in_park"] for o in r["orders"] if o["ticker"] == "BID") - 0.5) < 1e-9,
      f"Σ={tot:,.0f} vs vượt {-r['delta_vnd']:,.0f}")

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
    r = compute_trim("SpaceX", "2026-08-05", 0.80,
                     holdings=fake_holdings({"ACB": (10000, 20000)}, 10_000_000),
                     share_override=0.5, adv_fn=lambda t, a, _r=advret: _r,
                     day_cap_override=DAYCAP)
    check(f"C5 ADV {label} → fail-closed, không trim mã đó",
          not r["orders"] and r["blocked"], f"{r['decision']} {r['blocked']}")

# C6. trần per-name (= gate LAG live) phải CẮT khi ADV mỏng, phần dư KHÔNG dồn sang mã khác
h = fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000)
r = trim(h)                     # chân đối chứng: cùng holdings, ADV thừa sức cho CẢ HAI mã
r_thin = compute_trim("SpaceX", "2026-08-05", 0.80, holdings=h, share_override=0.5,
                      adv_fn=lambda t, a: ((10_000_000.0 if t == "ACB" else 5e9),
                                           "2026-08-05", None),
                      day_cap_override=DAYCAP)
acb = [o for o in r_thin["orders"] if o["ticker"] == "ACB"]
bid_thin = [o for o in r_thin["orders"] if o["ticker"] == "BID"]
bid_full = [o for o in r["orders"] if o["ticker"] == "BID"]
check("C6 ADV mỏng → ACB bị trần per-name cắt (hoặc chặn hẳn), BID KHÔNG được nhận thêm phần dư",
      (not acb or acb[0]["adv_capped"]) and bid_thin and bid_full
      and bid_thin[0]["qty"] == bid_full[0]["qty"],
      f"ACB={acb} BID {bid_thin[0]['qty'] if bid_thin else None} vs {bid_full[0]['qty'] if bid_full else None}")

# C7. CP chưa về T+2 → không đề xuất bán quá phần sellable
h = fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)}, 10_000_000,
                  sellable={"ACB": 200})
r = trim(h)
acb = [o for o in r["orders"] if o["ticker"] == "ACB"]
check("C7 không bán quá số CP đã về (sellable) — ràng buộc T+2",
      (not acb) or acb[0]["qty"] <= 200, str(acb))

# C8. trần TỔNG/phiên (engine _etf_day_cap) chặn khi mức vượt lớn hơn trần
r = compute_trim("SpaceX", "2026-08-05", 0.80,
                 holdings=fake_holdings({"ACB": (10000, 20000), "BID": (5000, 40000)},
                                        10_000_000),
                 share_override=0.5, adv_fn=adv_ok, day_cap_override=1_000_000.0)
check("C8 trần TỔNG/phiên binding → trim_total bị kẹp về trần",
      r["trim_total_vnd"] == 1_000_000.0 and r.get("day_cap_binding"),
      f"trim_total={r['trim_total_vnd']:,.0f}")
r = compute_trim("SpaceX", "2026-08-05", 0.80,
                 holdings=fake_holdings({"ACB": (10000, 20000)}, 10_000_000),
                 share_override=0.5, adv_fn=adv_ok, day_cap_override=0.0)
check("C8b không đo được trần TỔNG (=0) → BLOCKED_DAYCAP, không trim",
      r["decision"] == "BLOCKED_DAYCAP" and not r["orders"], r["decision"])

# C9. không dựng được danh sách account live → fail-closed
r = compute_trim("SpaceX", "2026-08-05", 0.80,
                 holdings=fake_holdings({"ACB": (10000, 20000)}, 10_000_000),
                 share_override=None, adv_fn=adv_ok, day_cap_override=DAYCAP)
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
