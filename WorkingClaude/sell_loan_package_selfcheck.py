#!/usr/bin/env python3
"""sell_loan_package_selfcheck.py — lệnh BÁN phải dùng gói vay của DEAL THẬT, và
PLACE_FAIL lỗi CẤU TRÚC phải có điểm dừng.

Sự cố gốc: kb/incidents/2026-09/2026-09-29-zalopay-sell-deal-not-found-loanpackage-1826.md
  • `DNSEBroker.place_order` nhánh SELL đặt `lp = None`, dòng ngay dưới ghi đè thành gói
    DEFAULT account (ZaloPay 1258) ⇒ 6 mã chỉ có deal ở gói 1826 (HPG MSB SHB TPB VIX VRE)
    bị DNSE trả HTTP 400 "deal not found".
  • Executor thử lại vô hạn: 2.628 PLACE_FAIL / 4h15, ~9,77tr VND không huy động được.

FIXTURE = snapshot positions THẬT của ZaloPay (0001743768) lúc 2026-09-29T04:55:03 trong
`data/execution_logs/dnse_raw_2026-09-29.jsonl` — tức trạng thái sổ ĐÚNG LÚC 15 lệnh bán
được đặt, không phải bản chụp cuối ngày (bản cuối ngày đã trừ phần vừa khớp, MBB 1258 còn
2cp ⇒ dùng nó sẽ cho kỳ vọng regression SAI).

Các ca:
  V1-a  6 mã sự cố       → resolve 1826 (KHÔNG còn gửi 1258)              [FIX]
  V1-b  counter-proof    → cùng fixture chạy trên CODE CŨ vẫn gửi 1258    [fix load-bearing]
  V1-c  9 mã bán trót    → vẫn resolve 1258 (không đổi hành vi)           [REGRESSION]
  V1-d  nhánh BUY        → không đụng positions, giữ nguyên đường cũ      [REGRESSION]
  V1-e  fail-safe        → positions rỗng/lỗi/mã lạ → gói default, không crash
  V1-f  nhiều gói        → ưu tiên gói đủ qty; không gói nào đủ → lớn nhất; KHÔNG cache
  V2    PLACE_FAIL       → 5 lượt cấu trúc liên tiếp thì dừng; lỗi tạm thời KHÔNG dừng

Chạy: python3 sell_loan_package_selfcheck.py   (không mạng — stub toàn bộ)
"""
import os
import sys

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")   # §5b — chặn _publish_bot_event ra bus THẬT

WC_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WC_ROOT)

from trading_bot.brokers import DNSEBroker
from trading_bot.executor import (PLACE_FAIL_STRUCTURAL_LIMIT, _place_fail_structural)

ZALOPAY_DEFAULT_LP = 1258
FAILS = []


def check(cond, msg):
    print(("  OK  " if cond else " FAIL ") + msg)
    if not cond:
        FAILS.append(msg)


# ───────────────────────── fixture: snapshot THẬT 2026-09-29T04:55:03 ─────────────────
def _pos(symbol, lp, open_q, trade_q, status="OPEN"):
    return {"symbol": symbol, "status": status, "loanPackageId": lp,
            "openQuantity": open_q, "tradeQuantity": trade_q, "accountNo": "0001743768"}


ZALOPAY_POSITIONS_20260929 = [
    _pos("ACB", 1826, 300, 300),
    _pos("BID", 1258, 320, 300),   _pos("BID", 1826, 107, 100),
    _pos("CSV", 1258, 1000, 1000), _pos("CTG", 1258, 450, 450),
    _pos("DGC", 1258, 10000, 10000), _pos("DRI", 1258, 1900, 1900),
    _pos("HDB", 1258, 359, 359),
    _pos("HPG", 1826, 500, 500),
    _pos("LPB", 1258, 252, 252),
    _pos("MBB", 1258, 252, 202),   _pos("MBB", 1826, 400, 400),
    _pos("MSB", 1826, 240, 200),
    _pos("NCT", 1258, 373, 373),   _pos("PVT", 1258, 2071, 2071),
    _pos("SAB", 1258, 744, 744),   _pos("SCL", 1258, 1000, 1000),
    _pos("SHB", 1826, 300, 300),
    _pos("SIP", 1258, 749, 749),   _pos("TCB", 1258, 356, 356),
    _pos("TPB", 1826, 100, 100),   _pos("TV1", 1258, 1400, 1400),
    _pos("VCB", 1258, 100, 100),   _pos("VCB", 1826, 200, 200),
    _pos("VHM", 1258, 300, 300),   _pos("VIB", 1826, 219, 200),
    _pos("VIX", 1826, 105, 105),   _pos("VNM", 1258, 601, 601),
    _pos("VPB", 1258, 1412, 1100), _pos("VPI", 1826, 400, 400),
    _pos("VRE", 1826, 100, 100),
]

FAILED_6 = ["HPG", "MSB", "SHB", "TPB", "VIX", "VRE"]          # 400 deal not found
OK_9 = ["BID", "CTG", "HDB", "LPB", "MBB", "TCB", "VCB", "VHM", "VPB"]   # PLACE OK


class FakeClient:
    """Stub DNSEClient. `positions()`/`loan_packages()` đếm số lần gọi (kiểm cache)."""

    def __init__(self, positions=None, raise_positions=False, pkg_map=None):
        self.loan_package_id = ZALOPAY_DEFAULT_LP
        self._positions = positions if positions is not None else []
        self._raise_positions = raise_positions
        self._pkg_map = pkg_map or {}
        self.n_positions = 0
        self.n_loan_packages = 0
        self.last_place = {}
        self.places = []

    def positions(self, account_id):
        self.n_positions += 1
        if self._raise_positions:
            raise RuntimeError("simulated positions timeout")
        return {"positions": list(self._positions)}

    def loan_packages(self, account_id, market_type="STOCK", symbol=None):
        self.n_loan_packages += 1
        return {"loanPackages": self._pkg_map.get(symbol, [])}

    def place_order(self, account_id, symbol, qty, side, order_type="LO",
                    price=None, loan_package_id=None):
        rec = {"symbol": symbol, "side": side, "qty": qty,
               "loan_package_id": loan_package_id}
        self.last_place = rec
        self.places.append(rec)
        return {"id": "OID_" + symbol}


def make_broker(client):
    b = DNSEBroker.__new__(DNSEBroker)
    b.account_id = "0001743768"
    b.label = "ZaloPay"
    b.client = client
    b._loan_package_id = ZALOPAY_DEFAULT_LP
    b._loan_pkg_cache = {}
    b._lever_pkg_cache = {}
    b._log_raw = lambda *a, **k: None
    return b


# ───────────────────── V1-a: 6 mã sự cố → 1826, không còn 1258 ───────────────────────
print("=== V1-a FIX: 6 mã chỉ có deal ở gói 1826 → lệnh bán mang 1826 ===")
for sym in FAILED_6:
    cl = FakeClient(ZALOPAY_POSITIONS_20260929)
    b = make_broker(cl)
    b.place_order(sym, 100, "sell", price=20000)
    got = cl.last_place["loan_package_id"]
    check(got == 1826,
          f"{sym} sell 100 → loanPackageId {got} (kỳ vọng 1826 = gói deal thật, "
          f"KHÔNG phải default {ZALOPAY_DEFAULT_LP})")

# ───────────────────── V1-b: counter-proof trên CODE CŨ ──────────────────────────────
print("=== V1-b COUNTER-PROOF: hành vi CŨ (lp=None) vẫn gửi 1258 cho cả 6 mã ===")
# Tái hiện nguyên văn nhánh else CŨ: `lp = None` rồi `lp_sent = lp or default`.
_old_resolve = DNSEBroker._resolve_sell_loan_package_id
try:
    DNSEBroker._resolve_sell_loan_package_id = lambda self, symbol, qty: None
    old_lps = []
    for sym in FAILED_6:
        cl = FakeClient(ZALOPAY_POSITIONS_20260929)
        b = make_broker(cl)
        b.place_order(sym, 100, "sell", price=20000)
        old_lps.append(cl.last_place["loan_package_id"])
    check(old_lps == [ZALOPAY_DEFAULT_LP] * 6,
          f"code cũ: cả 6 mã gửi {old_lps} = gói default ⇒ đúng ca DNSE trả "
          f"'400 deal not found' ⇒ fix là load-bearing, không phải test vô nghĩa")
finally:
    DNSEBroker._resolve_sell_loan_package_id = _old_resolve

# ───────────────────── V1-c: 9 mã bán trót → vẫn 1258 ────────────────────────────────
print("=== V1-c REGRESSION: 9 mã đã bán thành công 29/09 vẫn resolve 1258 ===")
for sym in OK_9:
    cl = FakeClient(ZALOPAY_POSITIONS_20260929)
    b = make_broker(cl)
    b.place_order(sym, 100, "sell", price=20000)
    got = cl.last_place["loan_package_id"]
    check(got == ZALOPAY_DEFAULT_LP,
          f"{sym} sell 100 → {got} (kỳ vọng {ZALOPAY_DEFAULT_LP}, hành vi KHÔNG đổi)")
print("    ↑ BID/MBB/VCB có deal ở CẢ HAI gói (1258 và 1826) — tie-break 'gói default "
      "nếu đủ hàng' giữ đúng gói mà lệnh thật hôm đó đã dùng.")

# ───────────────────── V1-d: nhánh BUY không đổi ─────────────────────────────────────
print("=== V1-d REGRESSION: nhánh BUY hoàn toàn không đổi ===")
PKG_MAP = {"HPG": [{"id": 1258, "type": "M"}, {"id": 1826, "type": "M"}]}
cl = FakeClient(ZALOPAY_POSITIONS_20260929, pkg_map=PKG_MAP)
b = make_broker(cl)
b.place_order("HPG", 100, "buy", price=20000)
check(cl.last_place["loan_package_id"] == ZALOPAY_DEFAULT_LP,
      f"HPG buy → {cl.last_place['loan_package_id']} (default hợp lệ ⇒ giữ nguyên, "
      f"đúng _resolve_loan_package_id cũ)")
check(cl.n_loan_packages == 1,
      "BUY vẫn query loan_packages đúng 1 lần (đường cũ nguyên vẹn)")
check(cl.n_positions == 0,
      "BUY KHÔNG gọi positions() — resolver mới chỉ chạy ở nhánh SELL")

cl = FakeClient(ZALOPAY_POSITIONS_20260929, pkg_map=PKG_MAP)
b = make_broker(cl)
b.place_order("HPG", 100, "buy", price=20000, loan_package_id=1826)
check(cl.n_positions == 0 and cl.last_place["loan_package_id"] == 1826,
      "BUY có gói CHỈ ĐỊNH (đòn bẩy CAPIT) vẫn đi đường _validate_lever_package, "
      "không đụng positions")

# ───────────────────── V1-e: fail-safe ───────────────────────────────────────────────
print("=== V1-e FAIL-SAFE: không resolve được → gói default (hành vi cũ), không crash ===")
cases = [
    ("positions rỗng", FakeClient([]), "HPG"),
    ("positions lỗi mạng", FakeClient(None, raise_positions=True), "HPG"),
    ("mã không có vị thế", FakeClient(ZALOPAY_POSITIONS_20260929), "FPT"),
    ("payload rác", FakeClient([{"foo": 1}, "not-a-dict"]), "HPG"),
]
for name, cl, sym in cases:
    b = make_broker(cl)
    try:
        b.place_order(sym, 100, "sell", price=20000)
        got = cl.last_place["loan_package_id"]
    except Exception as e:
        got = f"CRASH {type(e).__name__}: {e}"
    check(got == ZALOPAY_DEFAULT_LP, f"{name} → {got} (kỳ vọng {ZALOPAY_DEFAULT_LP})")

# sellable = 0 (T+2 chưa về) không được coi là gói hợp lệ
cl = FakeClient([_pos("HPG", 1826, 500, 0)])
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
check(cl.last_place["loan_package_id"] == ZALOPAY_DEFAULT_LP,
      "gói duy nhất có sellable=0 → không chọn, rơi về default (không ép gói không bán được)")

# dòng CLOSED bị bỏ qua
cl = FakeClient([_pos("HPG", 1826, 500, 500, status="CLOSED"),
                 _pos("HPG", 1900, 200, 200)])
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
check(cl.last_place["loan_package_id"] == 1900, "dòng status=CLOSED bị loại khỏi ứng viên")

# ───────────────────── V1-f: nhiều gói + không cache ─────────────────────────────────
print("=== V1-f nhiều gói cùng có hàng / không cache ===")
# (i) Không gói nào đủ qty riêng lẻ → chọn gói sellable LỚN NHẤT (fail-safe, bán được nhiều nhất)
cl = FakeClient([_pos("HPG", 1900, 100, 100), _pos("HPG", 1901, 300, 300)])
b = make_broker(cl)
b.place_order("HPG", 1000, "sell", price=20000)
check(cl.last_place["loan_package_id"] == 1901,
      "không gói nào đủ 1000 → chọn gói sellable lớn nhất 1901 (300cp)")

# (ii) Gói default CÓ hàng nhưng KHÔNG đủ qty, gói khác đủ → chọn gói đủ (bán gọn 1 deal)
cl = FakeClient([_pos("HPG", ZALOPAY_DEFAULT_LP, 50, 50), _pos("HPG", 1826, 500, 500)])
b = make_broker(cl)
b.place_order("HPG", 300, "sell", price=20000)
check(cl.last_place["loan_package_id"] == 1826,
      "default chỉ 50cp < 300 cần bán, 1826 có 500 → chọn 1826 (ưu tiên gói đủ qty)")

# (iii) Nhiều DÒNG cùng một gói → cộng gộp sellable của gói đó
cl = FakeClient([_pos("HPG", 1900, 100, 100), _pos("HPG", 1900, 100, 100),
                 _pos("HPG", 1901, 150, 150)])
b = make_broker(cl)
b.place_order("HPG", 200, "sell", price=20000)
check(cl.last_place["loan_package_id"] == 1900,
      "2 dòng cùng gói 1900 (100+100=200) ≥ 200 → chọn 1900, không phải 1901 (150)")

# (iv) KHÔNG cache: gọi 2 lần phải đọc positions 2 lần (sellable đổi sau mỗi lần khớp)
cl = FakeClient(ZALOPAY_POSITIONS_20260929)
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
b.place_order("HPG", 100, "sell", price=20000)
check(cl.n_positions == 2,
      f"2 lệnh bán HPG → positions() gọi {cl.n_positions} lần (kỳ vọng 2 — KHÔNG cache, "
      f"sellable là số lượng có thật, đổi sau mỗi lần khớp)")

# ───────────────────── V2: dừng retry PLACE_FAIL cấu trúc ────────────────────────────
print("=== V2 phân loại lỗi: CẤU TRÚC vs TẠM THỜI (bằng chứng trong chuỗi lỗi) ===")
STRUCTURAL = ["HTTP 400: deal not found",
              "HTTP 400: loanPackageId is required",
              "HTTP 403: forbidden instrument",
              "HTTP 404: account not found",
              "HTTP 422: invalid price"]
TRANSIENT = ["HTTP 429: too many requests",
             "HTTP 408: request timeout",
             "HTTP 500: REMOTE_SERVER_ERROR",
             "HTTP 502: bad gateway",
             "HTTP 503: service unavailable",
             "HTTPSConnectionPool(host='api.dnse.com.vn'): Read timed out",
             "Connection aborted, reset by peer",
             "KeyError: 'id'"]
for n in STRUCTURAL:
    check(_place_fail_structural(n) is True, f"CẤU TRÚC: {n!r}")
for n in TRANSIENT:
    check(_place_fail_structural(n) is False, f"TẠM THỜI (vẫn retry như cũ): {n!r}")

print("=== V2 bộ đếm: dừng đúng ngưỡng, chỉ với lỗi cấu trúc lặp lại y hệt ===")
import datetime as dt

from trading_bot.executor import Executor


class FakeOrder:
    def __init__(self, tid="HPG", side="sell"):
        self.id, self.ticker, self.side = f"PARKMERGE-SELL-{tid}", tid, side


class FakePlan:
    plan_date = "2026-09-29"


def make_executor():
    ex = Executor.__new__(Executor)
    ex.label = "ZaloPay"
    ex.plan = FakePlan()
    ex.journal = []
    ex._journal = lambda event, o=None, **kw: ex.journal.append((event, kw.get("note", "")))
    return ex


NOW = dt.datetime(2026, 9, 29, 9, 15, 8)
NOTE = "HTTP 400: deal not found"

ex, o, ps = make_executor(), FakeOrder(), {}
for i in range(PLACE_FAIL_STRUCTURAL_LIMIT - 1):
    ex._count_place_fail(ps, o, NOTE, NOW)
check(not ps.get("place_blocked"),
      f"{PLACE_FAIL_STRUCTURAL_LIMIT - 1} lượt → CHƯA dừng (streak={ps['place_fail_streak']})")
ex._count_place_fail(ps, o, NOTE, NOW)
check(ps.get("place_blocked") is True,
      f"lượt thứ {PLACE_FAIL_STRUCTURAL_LIMIT} → DỪNG (place_blocked=True)")
check([e for e, _ in ex.journal] == ["PLACE_FAIL_STOPPED"],
      f"journal có đúng 1 dòng PLACE_FAIL_STOPPED (thực tế: {[e for e, _ in ex.journal]})")
for i in range(20):
    ex._count_place_fail(ps, o, NOTE, NOW)
check(len([e for e, _ in ex.journal if e == "PLACE_FAIL_STOPPED"]) == 1,
      "20 lượt nữa → vẫn chỉ 1 dòng PLACE_FAIL_STOPPED (không spam journal/bus)")

ex, o, ps = make_executor(), FakeOrder(), {}
for i in range(50):
    ex._count_place_fail(ps, o, "HTTPSConnectionPool: Read timed out", NOW)
check(not ps.get("place_blocked") and ex.journal == [],
      "50 lượt lỗi TẠM THỜI → KHÔNG dừng, không journal (retry giữ nguyên hành vi cũ)")

ex, o, ps = make_executor(), FakeOrder(), {}
for n in ["HTTP 400: deal not found", "HTTP 400: deal not found",
          "HTTP 400: price out of band", "HTTP 400: deal not found",
          "HTTP 400: deal not found", "HTTP 400: deal not found"]:
    ex._count_place_fail(ps, o, n, NOW)
check(not ps.get("place_blocked"),
      f"lỗi cấu trúc ĐỔI chuỗi ở giữa → bộ đếm reset, chưa dừng (streak={ps['place_fail_streak']})")

ex, o, ps = make_executor(), FakeOrder(), {}
for i in range(PLACE_FAIL_STRUCTURAL_LIMIT - 1):
    ex._count_place_fail(ps, o, NOTE, NOW)
ex._count_place_fail(ps, o, "Read timed out", NOW)          # tạm thời xen giữa → reset
for i in range(PLACE_FAIL_STRUCTURAL_LIMIT - 1):
    ex._count_place_fail(ps, o, NOTE, NOW)
check(not ps.get("place_blocked"),
      "lỗi tạm thời xen giữa cũng reset chuỗi cấu trúc → chưa dừng")

print("=== V2 plumbing: _place_slices đọc cờ place_blocked và _count_place_fail được gọi ===")
import inspect
srcs = inspect.getsource(Executor._place_slices)
check('ps.get("place_blocked")' in srcs,
      "_place_slices bỏ qua parent có place_blocked (chặn trước cả bước đo quote)")
check("self._count_place_fail(ps, o, str(e), now)" in srcs,
      "_count_place_fail được gọi ngay sau dòng journal PLACE_FAIL")
check(srcs.index('ps.get("place_blocked")') < srcs.index("self._count_place_fail"),
      "cờ được KIỂM ở đầu vòng, trước khi đặt lệnh (không phải chỉ đếm rồi vẫn gửi)")

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAIL:")
    for m in FAILS:
        print("   - " + m)
    sys.exit(1)
print("✅ TẤT CẢ PASS")
