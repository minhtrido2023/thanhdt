#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: `_atc_sweep` phải BỎ QUA mã UPCOM thay vì gửi order_type="ATC" vô điều kiện.

Sự cố thật (SCL/ZaloPay 2026-10-01, `data/execution_logs/exec_ZaloPay_2026-10-01_journal.csv`):
200/1000cp SCL (mã UPCOM) còn lại khi vào phase ATC. `_atc_sweep` gửi `order_type="ATC"` —
DNSE trả `HTTP 400: Invalid ordertype for the exchange` (UPCOM không có phiên khớp định kỳ
đóng cửa, chỉ HOSE/HNX có ATO/ATC). `_atc_sweep` chạy lại MỖI chu kỳ poll (~20s, xem
`run_session`/`step()`) và KHÔNG có cờ "đã thử, đừng thử lại" cho nhánh lỗi (`ps["atc_sent"]`
chỉ set True khi broker TRẢ VỀ oid thành công) ⇒ lặp vô hạn tới hết phase ATC: đúng 42 dòng
ATC_FAIL từ 14:30:04 đến 14:33:46 trong log thật. 200cp trôi sang phiên sau mà KHÔNG CÓ LỆNH
NÀO thay thế (không hủy LO đang mở trước đó — nhưng tại thời điểm này đã không còn LO sống,
nên tổn thất là CƠ HỘI SWEEP cuối phiên, không phải một lệnh LO đang sống bị hủy oan).

Fix (`trading_bot/executor.py::_atc_sweep`): tra sàn qua `exchange_override` (học được từ
`_retry_tick_mismatch`) rồi `get_quote().exchange`, TRƯỚC khi hủy lệnh LO đang mở. UPCOM →
journal `UPCOM_SKIP_ATC`, `continue` (không hủy LO, không gọi place_order). `get_quote` lỗi/
không hỗ trợ (paper/sim) → fail-open về "HOSE" (ATC vẫn được thử như hành vi cũ — không chặn
nhầm mã HOSE/HNX vì quote câm).

⚠️ KHÔNG đặt lệnh thật — toàn bộ dùng `Executor` thật với broker giả (`_StubBroker`), state/
journal nằm trong thư mục tạm. §5b: `MIKE_BOT_TEST_MODE=1` trước mọi import.

Chạy:  $DNA_PYEXE atc_upcom_ordertype_selfcheck.py
       python3 atc_upcom_ordertype_selfcheck.py
"""
import glob
import os
import sys
import tempfile

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from trading_bot.plan import PlannedOrder, TradePlan        # noqa: E402
from trading_bot.executor import Executor                    # noqa: E402
from trading_bot.config import load_config, EXEC_DIR         # noqa: E402

TAG = "selfcheck-atc-upcom"
for f in glob.glob(os.path.join(EXEC_DIR, f"exec_{TAG}_*")):
    os.remove(f)

_n = 0
fails = []


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        fails.append(msg)


class _Quote:
    def __init__(self, exchange):
        self.exchange = exchange


class _StubBroker:
    """Đếm lời gọi + trả exchange tuỳ cấu hình. `raise_on_quote=True` mô phỏng broker
    không hỗ trợ get_quote trong ngữ cảnh này (paper/sim) — phải fail-open về HOSE."""
    name = "stub"

    def __init__(self, exchange="HOSE", raise_on_quote=False):
        self.exchange = exchange
        self.raise_on_quote = raise_on_quote
        self.quote_calls = []
        self.placed = []
        self.cancelled = []

    def get_quote(self, ticker):
        self.quote_calls.append(ticker)
        if self.raise_on_quote:
            raise RuntimeError("quote source không khả dụng (mô phỏng paper/sim)")
        return _Quote(self.exchange)

    def place_order(self, ticker, qty, side, **k):
        self.placed.append((ticker, qty, side, k.get("order_type")))
        return f"OID-{len(self.placed)}"

    def cancel_order(self, oid):
        self.cancelled.append(oid)

    def get_cash(self):
        return 10**12

    def poll_orders(self):
        return {}

    def get_positions(self):
        return {}


def make_executor(tmpdir, ticker, broker, open_child=None, parent_filled=800, qty=1000,
                  exchange_override=None):
    o = PlannedOrder(id="SELL-01", ticker=ticker, side="sell", qty=qty, ref_price=28000)
    plan = TradePlan(plan_date="2099-01-01", signal_date="2099-01-01", strategy="selfcheck",
                     strategy_version="0", state=3, state_name="NEUTRAL",
                     nav_basis={"account_nav": 1e9, "scale": 1.0}, orders=[o],
                     account=TAG, created_at="2099-01-01T00:00:00")
    cfg = load_config()
    cfg["atc_remainder_sell"] = True
    cfg["mode"] = "paper"
    ex = Executor(plan, broker, cfg, shared={})
    ex.state_file = os.path.join(tmpdir, "state.json")
    ex.journal_file = os.path.join(tmpdir, "journal.csv")
    ps = ex.state["parents"]["SELL-01"]
    ps["filled"] = parent_filled
    if open_child:
        ps["children"].append(open_child)
    if exchange_override:
        ex.state.setdefault("exchange_override", {})[ticker] = exchange_override
    return ex, o


def _events(ex):
    import csv as _csv
    if not os.path.exists(ex.journal_file):
        return []
    with open(ex.journal_file, encoding="utf-8") as f:
        return [row[1] for row in _csv.reader(f) if len(row) > 1]


def t_upcom_skips_atc_no_place_order():
    """Mã UPCOM: KHÔNG gọi place_order(ATC), journal UPCOM_SKIP_ATC, atc_sent vẫn False."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM")
        ex, o = make_executor(tmp, "SCL", br)
        ex._atc_sweep()
        ok(br.placed == [], f"UPCOM: place_order KHÔNG được gọi, nhưng: {br.placed}")
        ok("UPCOM_SKIP_ATC" in _events(ex),
           f"UPCOM: phải journal UPCOM_SKIP_ATC, được: {_events(ex)}")
        ok(ex.state["parents"]["SELL-01"]["atc_sent"] is False,
           "UPCOM: atc_sent phải vẫn False (chưa thực sự gửi gì)")


def t_upcom_does_not_cancel_live_lo():
    """Mã UPCOM còn LO đang mở: KHÔNG hủy nó (UPCOM khớp liên tục tới hết phiên — hủy để
    nhường chỗ cho ATC rồi ATC luôn thất bại = mất đúng cơ hội khớp cuối cùng)."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM")
        child = {"oid": "OID-LIVE-LO", "qty": 200, "price": 28000, "filled": 0,
                 "status": "open", "ts": "2099-01-01T14:30:00"}
        ex, o = make_executor(tmp, "SCL", br, open_child=child, parent_filled=800)
        ex._atc_sweep()
        ok(br.cancelled == [], f"UPCOM: cancel_order KHÔNG được gọi, nhưng: {br.cancelled}")
        ok(child["status"] == "open", "UPCOM: LO đang mở phải GIỮ NGUYÊN status=open")


def t_hose_still_sweeps_atc_control():
    """CHỨNG MINH NGƯỢC: cùng fixture, chỉ đổi exchange→HOSE ⇒ ATC vẫn đi ra như cũ.
    Chặn nếu fix vô tình chặn luôn đường HOSE/HNX hợp lệ."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="HOSE")
        ex, o = make_executor(tmp, "AAA", br, parent_filled=800)
        ex._atc_sweep()
        ok(br.placed == [("AAA", 200, "sell", "ATC")],
           f"HOSE: ATC phải vẫn đi ra như cũ, được: {br.placed}")
        ok("ATC" in _events(ex) and "UPCOM_SKIP_ATC" not in _events(ex),
           f"HOSE: journal phải có ATC, KHÔNG có UPCOM_SKIP_ATC: {_events(ex)}")
        ok(ex.state["parents"]["SELL-01"]["atc_sent"] is True, "HOSE: atc_sent phải True")


def t_quote_error_fails_open_to_hose():
    """get_quote lỗi (paper/sim không hỗ trợ) ⇒ fail-open về HOSE ⇒ ATC vẫn được thử —
    KHÔNG được vì một ngoại lệ đọc quote mà chặn nhầm mã HOSE/HNX thật."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM", raise_on_quote=True)
        ex, o = make_executor(tmp, "BBB", br, parent_filled=800)
        ex._atc_sweep()
        ok(br.quote_calls == ["BBB"], f"phải có thử gọi get_quote: {br.quote_calls}")
        ok(br.placed == [("BBB", 200, "sell", "ATC")],
           f"get_quote lỗi ⇒ fail-open HOSE ⇒ ATC vẫn đi ra, được: {br.placed}")


def t_exchange_override_upcom_skips_without_quote_call():
    """`exchange_override` (học từ `_retry_tick_mismatch`) ghi UPCOM cho mã ⇒ skip NGAY,
    không cần gọi get_quote lại (ưu tiên cache đã học, tiết kiệm 1 call/chu kỳ)."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="HOSE")   # cố tình đặt khác override để chứng minh override thắng
        ex, o = make_executor(tmp, "TV1", br, parent_filled=800,
                              exchange_override="UPCOM")
        ex._atc_sweep()
        ok(br.quote_calls == [], f"override có sẵn ⇒ KHÔNG được gọi get_quote: {br.quote_calls}")
        ok(br.placed == [], f"override=UPCOM ⇒ KHÔNG đặt ATC: {br.placed}")
        ok("UPCOM_SKIP_ATC" in _events(ex), f"phải journal UPCOM_SKIP_ATC: {_events(ex)}")


def t_exchange_override_hose_sweeps_atc():
    """CHỨNG MINH NGƯỢC cho trên: override=HOSE ⇒ ATC vẫn đi ra, không bị khoá nhầm."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM")  # cố tình đặt khác override
        ex, o = make_executor(tmp, "SHS", br, parent_filled=800,
                              exchange_override="HOSE")
        ex._atc_sweep()
        ok(br.quote_calls == [], f"override có sẵn ⇒ KHÔNG được gọi get_quote: {br.quote_calls}")
        ok(br.placed == [("SHS", 200, "sell", "ATC")],
           f"override=HOSE ⇒ ATC đi ra: {br.placed}")


def t_real_incident_repro_42_cycles_no_place_order():
    """Tái hiện đúng hình dạng sự cố thật: 42 chu kỳ poll liên tiếp (14:30:04→14:33:46,
    bước ~20s) trên SCL (UPCOM), KHÔNG CÓ lần nào gọi place_order — khác hẳn log thật nơi
    DNSE bị gọi 42 lần và trả HTTP 400 mỗi lần."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM")
        ex, o = make_executor(tmp, "SCL", br, parent_filled=800, qty=1000)
        for _ in range(42):
            ex._atc_sweep()
        ok(br.placed == [], f"42 chu kỳ UPCOM: place_order phải KHÔNG BAO GIỜ được gọi: {br.placed}")
        n_skip = _events(ex).count("UPCOM_SKIP_ATC")
        ok(n_skip == 42, f"phải có đúng 42 dòng UPCOM_SKIP_ATC (1/chu kỳ), được {n_skip}")


TESTS = [t_upcom_skips_atc_no_place_order, t_upcom_does_not_cancel_live_lo,
         t_hose_still_sweeps_atc_control, t_quote_error_fails_open_to_hose,
         t_exchange_override_upcom_skips_without_quote_call,
         t_exchange_override_hose_sweeps_atc,
         t_real_incident_repro_42_cycles_no_place_order]

if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}")
    for t in TESTS:
        before = len(fails)
        try:
            t()
        except Exception as e:
            fails.append(f"{t.__name__}: lỗi khi chạy — {type(e).__name__}: {e}")
        status = "PASS" if len(fails) == before else "FAIL"
        print(f"  [{status}] {t.__name__}")
    print()
    if fails:
        print(f"FAIL ({_n} assertion, {len(fails)} fail)")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"PASS ({_n} assertion)")
    sys.exit(0)
