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

PKG_MAP_G = {"HPG": [{"id": 1258, "type": "M"}, {"id": 1826, "type": "M"}]}
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
    # Stub THU THẬP, không no-op: F4 (đường suy biến phải để lại artifact) chỉ có ý nghĩa nếu
    # test đọc được bản ghi. Với stub no-op, revert sạch F4 vẫn xanh (arch-review R2).
    b.raw_log = []
    b._log_raw = lambda kind, payload: b.raw_log.append((kind, payload))
    return b


def resolve_records(b):
    return [pl for kind, pl in b.raw_log if kind == "sell_loan_package_resolve"]


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
print("=== V1-b COUNTER-PROOF: nạp brokers.py TRƯỚC KHI SỬA từ git, chạy lại fixture ===")
# Stub method mới trả None chỉ kiểm nhánh fail-safe (V1-e đã lo) — KHÔNG phải counter-proof.
# Nạp hẳn bản brokers.py ở commit cha rồi gọi CHÍNH place_order của nó (arch-review F-nit).
import importlib.util
import subprocess
import tempfile

FIX_COMMIT = "d51c735e"          # commit vá Việc 1 + Việc 2
try:
    old_src = subprocess.run(
        ["git", "show", f"{FIX_COMMIT}^:WorkingClaude/trading_bot/brokers.py"],
        cwd=WC_ROOT, capture_output=True, text=True, check=True).stdout
except Exception as exc:                                   # repo khác/commit bị rebase
    print(f"  SKIP  không nạp được brokers.py bản cũ từ git ({type(exc).__name__}: {exc})")
    old_src = None

if old_src:
    with tempfile.TemporaryDirectory() as td:
        # File nằm trong TMPDIR, KHÔNG ghi vào package trading_bot/ thật: bị kill giữa chừng
        # sẽ để lại một bản brokers.py TIỀN-VÁ, untracked, nằm ngay trong package production
        # (arch-review R2 nit). Import tương đối (`from . import config`) vẫn giải đúng vì
        # nó bám `__package__` của module, không bám vị trí file.
        mod_path = os.path.join(td, "_brokers_old_selfcheck.py")
        with open(mod_path, "w", encoding="utf-8") as fh:
            fh.write(old_src)
        spec = importlib.util.spec_from_file_location(
            "trading_bot._brokers_old_selfcheck", mod_path)
        old_mod = importlib.util.module_from_spec(spec)
        old_mod.__package__ = "trading_bot"
        sys.modules["trading_bot._brokers_old_selfcheck"] = old_mod
        try:
            spec.loader.exec_module(old_mod)
            OldBroker = old_mod.DNSEBroker
            check(not hasattr(OldBroker, "_resolve_sell_loan_package_id"),
                  "bản git cũ THỰC SỰ chưa có _resolve_sell_loan_package_id (đúng bản tiền-vá)")
            old_lps = []
            for sym in FAILED_6:
                cl = FakeClient(ZALOPAY_POSITIONS_20260929)
                b = OldBroker.__new__(OldBroker)
                b.account_id, b.label, b.client = "0001743768", "ZaloPay", cl
                b._loan_package_id = ZALOPAY_DEFAULT_LP
                b._loan_pkg_cache, b._lever_pkg_cache = {}, {}
                b._log_raw = lambda *a, **k: None
                b.place_order(sym, 100, "sell", price=20000)
                old_lps.append(cl.last_place["loan_package_id"])
            check(old_lps == [ZALOPAY_DEFAULT_LP] * 6,
                  f"CODE CŨ THẬT: cả 6 mã gửi {old_lps} = gói default ⇒ đúng ca DNSE trả "
                  f"'400 deal not found' ⇒ fix là load-bearing, không phải test vô nghĩa")
        finally:
            sys.modules.pop("trading_bot._brokers_old_selfcheck", None)

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

# (iii-bis) F3 — DỮ LIỆU THẬT 2026-09-29T14:45:04: MBB 1258 sellable=2, 1826 sellable=400.
# Bản vá đầu tiên áp tie-break "gói default" cả trong tập KHÔNG đủ hàng ⇒ chọn 1258 (2cp,
# không thể khớp) khi bán >400. arch-review F3 tái lập đúng ca này trên snapshot thật.
MBB_1445 = [_pos("MBB", 1826, 400, 400), _pos("MBB", 1258, 52, 2)]
for qty, want, why in [(400, 1826, "1826 đủ 400 → chọn 1826"),
                       (402, 1826, "KHÔNG gói nào đủ 402 → gói lớn nhất 1826, KHÔNG phải "
                                   "default 1258 (chỉ 2cp, không thể khớp)"),
                       (500, 1826, "bán quá tổng → vẫn gói lớn nhất 1826"),
                       (2, 1258, "2cp: default 1258 ĐỦ hàng → tie-break giữ 1258 (hành vi cũ)")]:
    cl = FakeClient(MBB_1445)
    b = make_broker(cl)
    b.place_order("MBB", qty, "sell", price=25000)
    got = cl.last_place["loan_package_id"]
    check(got == want, f"[F3 dữ liệu thật 14:45] MBB sell {qty} → {got} (kỳ vọng {want}: {why})")

# (iii-ter) nhánh thiếu trường (2 mutant arch-review báo chưa phủ)
cl = FakeClient([{"symbol": "HPG", "status": "OPEN", "loanPackageId": 1826,
                  "openQuantity": 300}])           # KHÔNG có tradeQuantity
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
check(cl.last_place["loan_package_id"] == 1826,
      "thiếu hẳn trường tradeQuantity → rơi về openQuantity (300) làm sellable, chọn 1826")

cl = FakeClient([{"symbol": "HPG", "status": "OPEN", "openQuantity": 300,
                  "tradeQuantity": 300},           # KHÔNG có loanPackageId
                 _pos("HPG", 1900, 100, 100)])
b = make_broker(cl)
b.place_order("HPG", 50, "sell", price=20000)
check(cl.last_place["loan_package_id"] == 1900,
      "dòng thiếu loanPackageId bị bỏ qua, không crash; gói 1900 còn lại được chọn")

# (iv) KHÔNG cache: gọi 2 lần phải đọc positions 2 lần (sellable đổi sau mỗi lần khớp)
cl = FakeClient(ZALOPAY_POSITIONS_20260929)
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
b.place_order("HPG", 100, "sell", price=20000)
check(cl.n_positions == 2,
      f"2 lệnh bán HPG → positions() gọi {cl.n_positions} lần (kỳ vọng 2 — KHÔNG cache, "
      f"sellable là số lượng có thật, đổi sau mỗi lần khớp)")

# ───────────────────── V1-g: F4 — MỌI đường resolve đều để lại ARTIFACT ─────────────
print("=== V1-h F-D: 2 mutant vòng 2 sống sót — id dạng CHUỖI, và tie-break sellable BẰNG NHAU ===")
# arch-review vòng 3 F-D: mọi fixture trước đây đều để loanPackageId là int ở CẢ HAI phía, nên
# mutant `v["id"] == default` (bỏ str()) xanh toàn bộ. DNSE trả JSON — một ngày nào đó nó trả
# chuỗi là tie-break "giữ gói default" TẮT LẶNG LẼ, đổi gói của BID/MBB/VCB so với hành vi cũ.
# Hình dạng phải là ca mà tie-break THỰC SỰ quyết: gói default có ÍT hàng hơn một gói đủ khác
# (VCB thật 2026-09-29: 1258:100 · 1826:200). Fixture kiểu BID (default 300 > 1826 100) KHÔNG
# giết được mutant — `max(sellable)` tình cờ cũng ra 1258 ⇒ test xanh vô nghĩa (đã đo).
STR_ID = [_pos("VCB", "1258", 100, 100), _pos("VCB", "1826", 200, 200)]
b = make_broker(FakeClient(STR_ID))
b.place_order("VCB", 100, "sell", price=20000)
check(str(b.client.last_place["loan_package_id"]) == "1258",
      f"loanPackageId dạng CHUỖI '1258' vs default int 1258 ⇒ vẫn nhận ra gói default, dù gói "
      f"1826 có NHIỀU hàng hơn (thực tế: {b.client.last_place['loan_package_id']!r}) — "
      f"giết mutant bỏ str()")

# Tie-break tất định: 2 gói sellable BẰNG NHAU, không gói nào là default ⇒ phải luôn ra CÙNG
# một gói bất kể thứ tự dòng positions. Mutant bỏ `str(v["id"])` khỏi key cũng xanh trước đây.
EQ = [_pos("FPT", 1900, 100, 100), _pos("FPT", 1901, 100, 100)]
picks = set()
for rows in (EQ, list(reversed(EQ))):
    b = make_broker(FakeClient(rows))
    b.place_order("FPT", 100, "sell", price=20000)
    picks.add(str(b.client.last_place["loan_package_id"]))
check(picks == {"1901"},
      f"2 gói sellable BẰNG NHAU (1900/1901, không gói nào default) ⇒ tie-break tất định theo "
      f"str(id), đảo thứ tự dòng vẫn ra 1901 (thực tế: {sorted(picks)})")

print("=== V1-g F4: _log_raw('sell_loan_package_resolve') trên CẢ 3 đường ===")
# Đường suy biến (rơi về gói default) chính là đường tái lập bug gốc — nó mà im lặng thì
# không checker nào biết. 6 mã sự cố đều CHỈ có 1 gói, nên điều kiện log cũ ("chỉ log khi
# nhiều gói") loại đúng ca cần audit nhất.
cl = FakeClient(ZALOPAY_POSITIONS_20260929)
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
recs = resolve_records(b)
# G-2: payload mang NaN/Infinity (json.loads nhận thẳng 2 token đó). Trước bản vá, int(nan)
# ném ValueError NGOÀI `try` ⇒ ném ra khỏi place_order, và vì không có "HTTP <nnn>" nên bị xếp
# TẠM THỜI ⇒ retry vô hạn — đúng hình dạng bão vừa vá.
for _bad_name, _bad_rows in (
        ("tradeQuantity=NaN", [_pos("HPG", 1826, 500, float("nan"))]),
        ("openQuantity=Infinity", [dict(_pos("HPG", 1826, 0, None),
                                        openQuantity=float("inf"), tradeQuantity=None)]),
        ("NaN ở gói này, gói khác vẫn lành", [_pos("HPG", 1826, 500, float("nan")),
                                             _pos("HPG", 1900, 300, 300)])):
    b = make_broker(FakeClient(_bad_rows))
    try:
        b.place_order("HPG", 100, "sell", price=20000)
        got_lp, exc = b.client.last_place["loan_package_id"], None
    except Exception as _e:
        got_lp, exc = None, f"{type(_e).__name__}: {_e}"
    want = 1900 if "gói khác" in _bad_name else ZALOPAY_DEFAULT_LP
    check(exc is None and got_lp == want,
          f"{_bad_name} → KHÔNG ném, resolve {want} (thực tế: lp={got_lp!r} exc={exc})")

check(len(recs) == 1 and recs[0]["resolved"] == 1826,
      f"đường THÀNH CÔNG 1 gói (HPG): đúng 1 bản ghi, resolved=1826 (thực tế: {recs})")
check(recs[0].get("by_package") == {"1826": 500} and recs[0].get("rule"),
      f"bản ghi nêu sellable theo gói + luật đã áp (audit được): {recs[0]}")

cl = FakeClient(None, raise_positions=True)
b = make_broker(cl)
b.place_order("HPG", 100, "sell", price=20000)
recs = resolve_records(b)
check(len(recs) == 1 and recs[0]["resolved"] is None and "error" in recs[0],
      f"đường LỖI positions: có bản ghi kèm lỗi thật, không im lặng (thực tế: {recs})")

cl = FakeClient(ZALOPAY_POSITIONS_20260929)
b = make_broker(cl)
b.place_order("FPT", 100, "sell", price=20000)          # mã không có vị thế
recs = resolve_records(b)
check(len(recs) == 1 and recs[0]["resolved"] is None,
      f"đường KHÔNG gói nào có hàng: vẫn có bản ghi (thực tế: {recs})")

cl = FakeClient(ZALOPAY_POSITIONS_20260929, pkg_map=PKG_MAP_G)
b = make_broker(cl)
b.place_order("HPG", 100, "buy", price=20000)
check(resolve_records(b) == [],
      "nhánh BUY KHÔNG sinh bản ghi sell_loan_package_resolve (không nhiễu log)")

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
        self.dcf_check = None            # _load_state THẬT đọc trường này khi backfill parent


class FakePlan:
    plan_date = "2026-09-29"

    def __init__(self, orders=()):
        self.orders = list(orders)


def make_executor(orders=()):
    ex = Executor.__new__(Executor)
    ex.label = "ZaloPay"
    ex.plan = FakePlan(orders)
    ex.journal = []                      # (event, parent_id, note)
    ex._journal = lambda event, o=None, **kw: ex.journal.append(
        (event, getattr(o, "id", None), kw.get("note", "")))
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
check([e for e, _, _ in ex.journal] == ["PLACE_FAIL_STOPPED"],
      f"journal có đúng 1 dòng PLACE_FAIL_STOPPED (thực tế: {[e for e, _, _ in ex.journal]})")
for i in range(20):
    ex._count_place_fail(ps, o, NOTE, NOW)
check(len([e for e, _, _ in ex.journal if e == "PLACE_FAIL_STOPPED"]) == 1,
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
import re
srcs = inspect.getsource(Executor._place_slices)
check('ps.get("place_blocked")' in srcs,
      "_place_slices bỏ qua parent có place_blocked (chặn trước cả bước đo quote)")
check("self._count_place_fail(ps, o, str(e), now)" in srcs,
      "_count_place_fail được gọi ngay sau dòng journal PLACE_FAIL")
check(srcs.index('ps.get("place_blocked")') < srcs.index("self._count_place_fail"),
      "cờ được KIỂM ở đầu vòng, trước khi đặt lệnh (không phải chỉ đếm rồi vẫn gửi)")

print("=== V2-F1 cờ chặn có phạm vi TIẾN TRÌNH: khởi động lại là gỡ ===")
# arch-review F1 replay journal THẬT: chặn vĩnh viễn sẽ giữ chết 20 lệnh đã khớp thật sau mốc
# chặn (11 lệnh bán 2026-07-06 khớp 13:00 sau khi T+2 về; 8 lệnh bán ZaloPay 2026-08-10 — cùng
# lỗi 'deal not found' — khớp 10:35 sau hot-fix + restart; 1 lệnh mua 2026-07-28 khớp 14:13).
BLOCKED_ORDERS = [FakeOrder("HPG"), FakeOrder("CTG")]
ex = make_executor(BLOCKED_ORDERS)
PID_HPG, PID_CTG = BLOCKED_ORDERS[0].id, BLOCKED_ORDERS[1].id
st = {"parents": {
    PID_HPG: {"place_blocked": True, "place_blocked_ts": "2026-09-29T09:16:28",
              "place_fail_streak": 5, "place_fail_note": NOTE, "done": False},
    PID_CTG: {"place_fail_streak": 0, "place_fail_note": "", "done": False},
}}
ex._clear_place_blocks(st)
check(not st["parents"][PID_HPG].get("place_blocked"),
      "resume tiến trình mới → place_blocked bị XOÁ (kịch bản hot-fix + restart 2026-08-10)")
check(st["parents"][PID_HPG]["place_fail_streak"] == 0
      and st["parents"][PID_HPG]["place_fail_note"] == "",
      "streak + note cũng reset (không chặn lại ngay lượt fail đầu tiên sau restart)")
check("place_blocked_ts" not in st["parents"][PID_HPG], "dọn cả place_blocked_ts, không để rác")
check([(e, pid) for e, pid, _ in ex.journal] == [("PLACE_BLOCK_CLEARED", PID_HPG)],
      f"1 dòng PLACE_BLOCK_CLEARED cho ĐÚNG parent bị chặn, parent_id máy đọc được "
      f"(thực tế: {[(e, pid) for e, pid, _ in ex.journal]})")
check("FAIL" not in "PLACE_BLOCK_CLEARED",
      "tên sự kiện KHÔNG chứa 'FAIL' — execution_quality_review.py đếm FAIL|ERROR|REJECT "
      "là lỗi, một lần PHỤC HỒI không phải lỗi")
check(NOTE in ex.journal[0][2],
      "note giữ nguyên văn lỗi CŨ để người đọc biết vì sao nó từng bị chặn")

# 2 parent cùng bị chặn → 2 dòng riêng, không gộp vào 1 dòng văn xuôi
ex2 = make_executor(BLOCKED_ORDERS)
ex2._clear_place_blocks({"parents": {
    PID_HPG: {"place_blocked": True, "place_fail_note": NOTE},
    PID_CTG: {"place_blocked": True, "place_fail_note": NOTE}}})
check(sorted(pid for _, pid, _ in ex2.journal) == sorted([PID_HPG, PID_CTG]),
      "2 parent bị chặn → 2 dòng journal riêng (§28: không nhồi id vào note văn xuôi)")

ex3 = make_executor(BLOCKED_ORDERS)
ex3._clear_place_blocks({"parents": {PID_CTG: {"done": False}}})
check(ex3.journal == [], "không có lệnh nào bị chặn → KHÔNG ghi journal (im lặng đúng chỗ)")

print("=== V2-F1c ĐƯỜNG THẬT: _load_state() + _journal() THẬT, KHÔNG stub (vòng 3 F-A) ===")
# Vòng 2 chỉ kiểm CHUỖI NGUỒN ("self._clear_place_blocks(st)" có mặt trong _load_state) — đúng
# về chữ, sai về hành vi: _journal đọc `self.state["parents"]`, mà `self.state` chỉ được gán
# SAU khi _load_state trả về ⇒ mọi lần resume có cờ chặn làm __init__ ném AttributeError, chết
# cả phiên chiều của account. Stub `ex._journal = lambda` của make_executor che đúng lỗi đó.
# Nay đi ĐƯỜNG THẬT: _load_state() thật trên state file thật + _journal() thật ra CSV tmpdir.
import ast
import csv
import json
import textwrap


class RealPathPlan(FakePlan):
    created_at = "2026-09-29T09:00:00"


with tempfile.TemporaryDirectory() as td:
    R_ORDERS = [FakeOrder("HPG"), FakeOrder("CTG")]
    RP_H, RP_C = R_ORDERS[0].id, R_ORDERS[1].id
    ORPHAN = "PARKMERGE-SELL-GONE"        # trong state, KHÔNG còn trong plan (F-C)
    st_file = os.path.join(td, "state_ZaloPay.json")
    with open(st_file, "w", encoding="utf-8") as fh:
        json.dump({"plan_date": "2026-09-29", "plan_created_at": RealPathPlan.created_at,
                   "parents": {
                       RP_H: {"filled": 0, "done": False, "place_blocked": True,
                              "place_blocked_ts": "2026-09-29T09:16:28",
                              "place_fail_streak": 5, "place_fail_note": NOTE},
                       ORPHAN: {"filled": 0, "done": False, "place_blocked": True,
                                "place_fail_streak": 5, "place_fail_note": NOTE},
                       RP_C: {"filled": 0, "done": False}}}, fh)

    ex = Executor.__new__(Executor)       # CỐ Ý không gán ex.state — như __init__ thật
    ex.label = "ZaloPay"
    ex.plan = RealPathPlan(R_ORDERS)
    ex.state_file = st_file
    ex.journal_file = os.path.join(td, "exec_ZaloPay_2026-09-29_journal.csv")
    check(not hasattr(ex, "state"),
          "tiền đề của test: `state` CHƯA là thuộc tính khi _load_state() chạy (như __init__)")
    try:
        st, load_err = ex._load_state(), None
    except Exception as exc:
        st, load_err = None, f"{type(exc).__name__}: {exc}"
    check(load_err is None,
          f"_load_state() KHÔNG ném khi self.state chưa tồn tại (thực tế: {load_err}) — bản "
          f"82732a05 journal TỪ TRONG _load_state ⇒ AttributeError ở MỌI lần resume có cờ chặn")
    check(st is not None and st["parents"][RP_H].get("place_blocked") is True,
          "…và _load_state KHÔNG tự gỡ cờ (việc gỡ thuộc __init__, sau khi state đã gán)")

    ex.state = st                          # ĐÚNG thứ tự __init__ thật
    if st is None:                         # _load_state đã ném ⇒ đã FAIL ở trên; đừng để
        st = {"parents": {}}               # harness chết giữa đường, còn kiểm tiếp phần sau
    ex._clear_place_blocks(st)             # _journal THẬT, ghi ra CSV thật
    check(not st["parents"][RP_H].get("place_blocked"),
          "đường thật: place_blocked bị XOÁ (kịch bản hot-fix + restart 2026-08-10)")
    with open(ex.journal_file, newline="", encoding="utf-8") as fh:
        jrows = list(csv.DictReader(fh))
    got = sorted((r["event"], r["parent_id"], r["ticker"]) for r in jrows)
    check(got == sorted([("PLACE_BLOCK_CLEARED", RP_H, "HPG"),
                         ("PLACE_BLOCK_CLEARED", ORPHAN, "")]),
          f"CSV thật có 2 dòng, parent_id KHÔNG rỗng cả ở parent đã rời plan (F-C) "
          f"(thực tế: {got})")
    check(all(NOTE in r["note"] for r in jrows),
          "mỗi dòng giữ nguyên văn lỗi cũ trong note")

# Cấu trúc: lệnh gọi phải nằm trong __init__ và SAU phép gán self.state — kiểm bằng AST chứ
# không so chuỗi, và kiểm cả chiều NGƯỢC (không được quay về nằm trong _load_state).
_init_src = textwrap.dedent(inspect.getsource(Executor.__init__))
_i_state = next((i for i, l in enumerate(_init_src.splitlines())
                 if "self.state = self._load_state()" in l), -1)
_i_clear = next((i for i, l in enumerate(_init_src.splitlines())
                 if "self._clear_place_blocks(" in l), -1)
check(_i_state < _i_clear,
      f"__init__ gỡ chặn SAU khi gán self.state (dòng state={_i_state}, clear={_i_clear})")
# Thứ tự dòng KHÔNG đủ: mutant `self._clear_place_blocks({})` giữ nguyên thứ tự, giữ nguyên
# 102/102 PASS, mà hành vi là KHÔNG parent nào được gỡ cờ — im lặng tuyệt đối, `place_blocked`
# quay lại thành bản án cả ngày, đúng bug F1 sinh ra để diệt (arch-review vòng 4 G-1).
_clear_call = next((n for n in ast.walk(ast.parse(_init_src))
                    if isinstance(n, ast.Call)
                    and ast.unparse(n.func) == "self._clear_place_blocks"), None)
check(_clear_call is not None
      and [ast.unparse(a) for a in _clear_call.args] == ["self.state"],
      f"…và gỡ chặn trên CHÍNH `self.state`, không phải dict khác "
      f"(thực tế: {None if _clear_call is None else [ast.unparse(a) for a in _clear_call.args]})")
check("_clear_place_blocks" not in inspect.getsource(Executor._load_state),
      "_load_state KHÔNG còn gọi _clear_place_blocks (nơi self.state chưa tồn tại)")

print("=== V2-F1b ngưỡng dừng bị RÀNG BUỘC (không được lặng lẽ nâng lên vô nghĩa) ===")
# Nhịp thử lại đo thật: PLACE_FAIL không cập nhật last_slice_ts và không sinh child ⇒ throttle
# không kích hoạt ⇒ ~20 giây/lượt. Ngưỡng phải nằm trong vùng "cắt được bão retry nhưng không
# chặn oan một trục trặc thoáng qua": 2..10 lượt ⇔ ~40 giây..3,5 phút.
check(2 <= PLACE_FAIL_STRUCTURAL_LIMIT <= 10,
      f"PLACE_FAIL_STRUCTURAL_LIMIT = {PLACE_FAIL_STRUCTURAL_LIMIT} ∈ [2,10] "
      f"(~{PLACE_FAIL_STRUCTURAL_LIMIT * 20}s ở nhịp retry ~20s/lượt)")

print("=== V2-F5 ATC là lưới cuối: KHÔNG bị cờ chặn, nhưng phải để lại dấu vết ===")
atc_src = inspect.getsource(Executor._atc_sweep)
check('ATC_AFTER_BLOCK' in atc_src,
      "_atc_sweep journal ATC_AFTER_BLOCK khi đi qua cờ chặn (không đi ra im lặng)")
import ast
import textwrap


def _guard_bodies(func, marker):
    """Thân của mọi `if …<marker>…:` trong `func` — so bằng AST, không bằng chuỗi."""
    tree = ast.parse(textwrap.dedent(inspect.getsource(func)))
    return [n.body for n in ast.walk(tree)
            if isinstance(n, ast.If) and marker in ast.unparse(n.test)]


atc_guards = _guard_bodies(Executor._atc_sweep, "place_blocked")
check(len(atc_guards) == 1
      and not any(isinstance(x, ast.Continue) for b in atc_guards for x in b),
      "_atc_sweep CỐ Ý không `continue` ở cờ chặn — lệnh BÁN vẫn còn 1 lần thử ATC")

# Vị trí là NỘI DUNG, không phải hình thức: bản đầu ghi ATC_AFTER_BLOCK TRƯỚC khi đọc
# `atc_remainder_buy` (=False) ⇒ mỗi lệnh MUA bị chặn phun 45 dòng khẳng định "vẫn thử" rồi
# `continue` ngay dòng sau — đúng lỗi §29 (arch-review R2 killer objection).
_atc_lines = inspect.getsource(Executor._atc_sweep).splitlines()
_i_flag = next((i for i, l in enumerate(_atc_lines) if "atc_remainder_buy" in l), -1)
_i_journal = next((i for i, l in enumerate(_atc_lines)
                   if 'self._journal("ATC_AFTER_BLOCK"' in l), -1)
_i_place = next((i for i, l in enumerate(_atc_lines) if "order_type=\"ATC\"" in l), -1)
check(_i_flag < _i_journal < _i_place,
      f"ATC_AFTER_BLOCK ghi SAU cổng atc_remainder_* và NGAY TRƯỚC place_order ATC "
      f"(dòng flag={_i_flag}, journal={_i_journal}, place={_i_place}) — không khẳng định "
      f"'vẫn thử' cho lệnh MUA vốn bị `continue` ngay sau đó")
for _skip in ("HARD_CEILING_SKIP_ATC", "ODD_LOT_SKIP_ATC", "WAIT_T2_SETTLEMENT"):
    _i = next(i for i, l in enumerate(_atc_lines) if _skip in l)
    check(_i < _i_journal,
          f"ATC_AFTER_BLOCK cũng nằm sau nhánh bỏ qua {_skip} (chỉ ghi khi ATC thật sự đi ra)")
slice_guards = _guard_bodies(Executor._place_slices, "place_blocked")
check(len(slice_guards) == 1
      and any(isinstance(x, ast.Continue) for b in slice_guards for x in b),
      "_place_slices thì NGƯỢC LẠI: `continue` thật sự (vòng retry mới là thứ phải cắt)")
check("BẤT ĐỐI XỨNG" in inspect.getdoc(Executor._count_place_fail),
      "bất đối xứng ATC (bán có lưới / mua không) được ghi rõ trong docstring, không ngầm hiểu")
check("place_blocked" in inspect.getdoc(Executor._count_place_fail)
      and "state_" in inspect.getdoc(Executor._count_place_fail),
      "docstring nêu cách GỠ chặn thủ công (khoá nào, file nào)")

print("=== V2-F2 PLACE_FAIL_STOPPED phải được ops_health_check.sh nhìn thấy ===")
# Gate mới cắt PLACE_FAIL xuống ≤5/lệnh — dưới hẳn ngưỡng >20 vốn là cái chuông DUY NHẤT đã bắt
# được sự cố 29/09. Nếu không wire sự kiện mới vào, ta đổi ồn ào lấy im lặng (arch-review F2).
# So chuỗi nguồn KHÔNG đủ: mutant dời `continue` xuống DƯỚI khối hạ cấp vẫn giữ nguyên cả hai
# chuỗi mà hành vi quay về đúng sự im lặng F2 nói tới (arch-review R2). Nên trích KHỐI PYTHON
# check #3 ra chạy thật trên journal fixture — kiểm HÀNH VI, không kiểm chữ.
OPS_SH = os.path.join(WC_ROOT, "mike", "bin", "ops_health_check.sh")
_ops_lines = open(OPS_SH, encoding="utf-8").read().splitlines()
_i0 = next(i for i, l in enumerate(_ops_lines) if l.startswith('REPORT="$(python3 - '))
_i1 = next(i for i, l in enumerate(_ops_lines) if "# 4. Circuit breaker per-agent" in l)
OPS_BLOCK = "\n".join(_ops_lines[_i0 + 1:_i1]) + '\nprint("WARN=%d" % warn)\nprint("\\n".join(lines))\n'

HDR = ("ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n")


def run_ops_check(rows):
    """Chạy THẬT khối check #3 của ops_health_check.sh trên 1 journal dựng sẵn → (warn, text)."""
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "data", "execution_logs"))
        jp = os.path.join(td, "data", "execution_logs", "exec_T_2026-09-29_journal.csv")
        with open(jp, "w", encoding="utf-8") as fh:
            fh.write(HDR + "".join(rows))
        blk = os.path.join(td, "blk.py")
        with open(blk, "w", encoding="utf-8") as fh:
            fh.write(OPS_BLOCK)
        r = subprocess.run([sys.executable, blk, td, "2026-09-29", "T"],
                           capture_output=True, text=True)
        out = r.stdout
        return int(re.search(r"WARN=(\d+)", out).group(1)), out


def jrow(ts, ev, pid="P-HPG", tic="HPG", note=""):
    return f"2026-09-29T{ts},{ev},{pid},{tic},sell,,,,0,PARK,PARK_TRIM,{note}\n"


# Fixture phải GIỐNG THẬT: 5 PLACE_FAIL rồi mới tới PLACE_FAIL_STOPPED. Thiếu dòng PLACE_FAIL
# thì `last_ts["PLACE_FAIL"]` rỗng và mutant "dời continue xuống dưới khối hạ cấp" SỐNG SÓT —
# chính là ca arch-review R2 dựng ra (đã tái lập: bỏ 5 dòng này ⇒ mutant không bị bắt).
STOPPED_ROW = ("".join(jrow(f"09:15:{8 + i * 20 % 60:02d}", "PLACE_FAIL",
                            note="HTTP 400: deal not found") for i in range(5))
               + jrow("09:16:28", "PLACE_FAIL_STOPPED", note="5 luot lien tiep"))
LATER_FILL = jrow("10:30:00", "PLACE", "P-CTG", "CTG") + jrow("10:31:00", "FILL", "P-CTG", "CTG")

w, out = run_ops_check([STOPPED_ROW] + [LATER_FILL])
check(w == 1 and "PLACE_FAIL_STOPPED" in out and "ĐÃ DỨT" not in out,
      f"1 PLACE_FAIL_STOPPED + 1 mã KHÁC khớp sau đó ⇒ vẫn ⚠️ (warn={w}) — không bị "
      f"last_success_ts của mã khác dìm xuống ℹ️")

w, _ = run_ops_check([LATER_FILL])
check(w == 0, f"journal sạch ⇒ không báo động (warn={w}) — không sinh cảnh báo giả")

w, _ = run_ops_check([jrow("09:15:08", "PLACE_FAIL",
                           note="HTTP 400: Trade quantity not enough") * 1] * 25)
check(w == 0, f"25 lượt PLACE_FAIL mẫu T+2 vẫn được loại trừ như cũ (warn={w})")

w, _ = run_ops_check([jrow("14:40:00", "ATC_AFTER_BLOCK", note="luoi ATC")] * 40)
check(w == 0, f"40 dòng ATC_AFTER_BLOCK KHÔNG sinh báo động (warn={w}) — sự kiện mới không "
              f"làm checker ồn lên")

w, _ = run_ops_check([jrow("09:00:00", "PLACE_BLOCK_CLEARED", note="restart")] * 10)
check(w == 0, f"PLACE_BLOCK_CLEARED (phục hồi) KHÔNG bị tính là lỗi (warn={w})")

print("=== V2-F-E PLACE_FAIL_STOPPED phải hiện trong heartbeat 5' (bịt khoảng sau 12:45) ===")
# ops_health_check.sh chỉ chạy 08:20 + 12:45 và chỉ đọc journal của HÔM NAY ⇒ một lần chặn lúc
# 13:05-14:45 KHÔNG lượt cron nào quét tới. bot_heartbeat.sh chạy 5 phút/lần cả phiên, nên nó
# là kênh bịt đúng khoảng trống đó (arch-review vòng 3 F-E). Kiểm HÀNH VI: trích nguyên khối
# python của `_orderbook_digest` ra chạy thật trên journal fixture, không so chuỗi nguồn.
HB_SH = os.path.join(WC_ROOT, "mike", "bin", "bot_heartbeat.sh")
_hb = open(HB_SH, encoding="utf-8").read().splitlines()
_j0 = next(i for i, l in enumerate(_hb) if "<< 'PYEOF'" in l)
_j1 = next(i for i, l in enumerate(_hb) if l.strip() == "PYEOF" and i > _j0)
HB_BLOCK = "\n".join(_hb[_j0 + 1:_j1])


def run_heartbeat(rows):
    """Chạy THẬT khối _orderbook_digest của bot_heartbeat.sh trên 1 journal dựng sẵn → stdout."""
    with tempfile.TemporaryDirectory() as td:
        jp = os.path.join(td, "exec_T_2026-09-29_journal.csv")
        with open(jp, "w", encoding="utf-8") as fh:
            fh.write(HDR + "".join(rows))
        blk = os.path.join(td, "hb.py")
        with open(blk, "w", encoding="utf-8") as fh:
            fh.write(HB_BLOCK)
        r = subprocess.run([sys.executable, blk, jp, "ZaloPay", "13:05", "2"],
                           capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr


rc_hb, out_hb = run_heartbeat([jrow("13:05:00", "PLACE_FAIL_STOPPED", note="HTTP 400: deal not found")])
check(rc_hb == 0, f"khối heartbeat chạy được trên fixture (rc={rc_hb}) — {out_hb[:200]}")
check("HPG" in out_hb and "DỪNG" in out_hb.upper().replace("DUNG", "DỪNG"),
      f"PLACE_FAIL_STOPPED lúc 13:05 HIỆN trong digest kèm lý do 'ĐÃ DỪNG' (thực tế: {out_hb!r})")
check("deal not found" in out_hb,
      f"…và giữ nguyên văn lỗi thật để người trực biết vì sao (thực tế: {out_hb!r})")

rc_hb2, out_hb2 = run_heartbeat([jrow("13:05:00", "PLACE_FAIL_STOPPED", note="HTTP 400: deal not found"),
                                 jrow("13:30:00", "DONE", note="khớp đủ")])
check("DỪNG" not in out_hb2.upper().replace("DUNG", "DỪNG"),
      f"parent sau đó DONE ⇒ không còn báo đang-chờ (không cảnh báo giả) (thực tế: {out_hb2!r})")

print()
if FAILS:
    print(f"❌ {len(FAILS)} FAIL:")
    for m in FAILS:
        print("   - " + m)
    sys.exit(1)
print("✅ TẤT CẢ PASS")
