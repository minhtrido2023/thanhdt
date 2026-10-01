#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: `_atc_sweep` phải BỎ QUA mã UPCOM thay vì gửi order_type="ATC" vô điều kiện.

Sự cố thật (SCL/ZaloPay 2026-10-01, `data/execution_logs/exec_ZaloPay_2026-10-01_journal.csv`):
200/1000cp SCL (mã UPCOM) còn lại khi vào phase ATC. `_atc_sweep` gửi `order_type="ATC"` —
DNSE trả `HTTP 400: Invalid ordertype for the exchange` (UPCOM không có phiên khớp định kỳ
đóng cửa, chỉ HOSE/HNX có ATO/ATC). `_atc_sweep` chạy lại MỖI chu kỳ poll (~20s, xem
`run_session`/`step()`) và KHÔNG có cờ "đã thử, đừng thử lại" cho nhánh lỗi (`ps["atc_sent"]`
chỉ set True khi broker TRẢ VỀ oid thành công) ⇒ lặp vô hạn tới hết phase ATC: đúng **45 dòng**
ATC_FAIL từ **14:30:04 đến 14:44:53** trong log thật (đính chính 2026-10-01 vòng 2 — đếm trực
tiếp `grep ATC_FAIL ... | wc -l` trên file, con số 42/14:33:46 ở bản nháp đầu là SAI). 200cp
trôi sang phiên sau mà KHÔNG CÓ LỆNH NÀO thay thế (không hủy LO đang mở trước đó — nhưng tại
thời điểm này đã không còn LO sống, nên tổn thất là CƠ HỘI SWEEP cuối phiên, không phải một
lệnh LO đang sống bị hủy oan).

Fix (`trading_bot/executor.py::_atc_sweep`): tra sàn qua quote SỐNG có `exchange_known=True`
TRƯỚC (ưu tiên hơn `exchange_override` — cache đó chỉ ghi HOSE|HNX, không bao giờ ghi UPCOM, và
"HNX" ở đó mơ hồ với UPCOM), rồi mới rơi về `exchange_override`, TRƯỚC khi hủy lệnh LO đang mở.
UPCOM → journal `UPCOM_SKIP_ATC`, `continue` (không hủy LO, không gọi place_order). `get_quote`
lỗi/không hỗ trợ (paper/sim) hoặc quote không xác định được sàn (`exchange_known=False`) và
chưa có override học được → fail-open về "HOSE" (ATC vẫn được thử như hành vi cũ — không chặn
nhầm mã HOSE/HNX vì quote câm). Lưới an toàn phụ: nếu nhận diện sàn vẫn lọt, broker trả lỗi
"Invalid ordertype" (status 400) sẽ đặt `ps["atc_unsupported"]=True` ngay ở lần thử ĐẦU TIÊN,
đóng đường lặp vô hạn của chính sự cố gốc (xem `_is_invalid_ordertype` + check ở đầu vòng lặp).

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
    def __init__(self, exchange, exchange_known=True):
        self.exchange = exchange
        self.exchange_known = exchange_known


class _StubBroker:
    """Đếm lời gọi + trả exchange tuỳ cấu hình. `raise_on_quote=True` mô phỏng broker
    không hỗ trợ get_quote trong ngữ cảnh này (paper/sim); `quote_returns_none=True` mô phỏng
    đường lỗi THẬT của PHS/phs_flash (`brokers.py:354,:1385` trả `None`, không ném exception) —
    cả hai đường đều phải fail-open về HOSE. `exchange_known=False` mô phỏng feed câm/ambiguous
    (Quote thật không map được marketId) — cũng rơi về `exchange_override`/fail-open HOSE."""
    name = "stub"

    def __init__(self, exchange="HOSE", exchange_known=True, raise_on_quote=False,
                 quote_returns_none=False):
        self.exchange = exchange
        self.exchange_known = exchange_known
        self.raise_on_quote = raise_on_quote
        self.quote_returns_none = quote_returns_none
        self.quote_calls = []
        self.placed = []
        self.cancelled = []

    def get_quote(self, ticker):
        self.quote_calls.append(ticker)
        if self.raise_on_quote:
            raise RuntimeError("quote source không khả dụng (mô phỏng paper/sim)")
        if self.quote_returns_none:
            return None
        return _Quote(self.exchange, self.exchange_known)

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


def t_quote_known_wins_over_stale_exchange_override():
    """Quote SỐNG biết chắc mã là UPCOM (exchange_known=True) PHẢI thắng `exchange_override`
    cũ/sai (ở đây cố tình đặt "HOSE") — override chỉ ghi được HOSE|HNX (`_retry_tick_mismatch`
    KHÔNG BAO GIỜ ghi UPCOM), nên tin nó hơn quote sống sẽ bỏ lọt đúng ca sự cố gốc (arch-review
    R2 §3: thứ tự cũ `override trước, quote sau` đọc nhầm mã UPCOM có override="HNX" thành HNX
    thật). override=UPCOM không test riêng vì KHÔNG THỂ xảy ra trong production."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM", exchange_known=True)
        ex, o = make_executor(tmp, "SCL", br, parent_filled=800,
                              exchange_override="HOSE")
        ex._atc_sweep()
        ok(br.quote_calls == ["SCL"], f"phải LUÔN thử quote trước override: {br.quote_calls}")
        ok(br.placed == [], f"quote biết UPCOM phải thắng override HOSE cũ: {br.placed}")
        ok("UPCOM_SKIP_ATC" in _events(ex), f"phải journal UPCOM_SKIP_ATC: {_events(ex)}")


def t_override_fallback_when_quote_unknown():
    """Quote sống KHÔNG xác định được sàn (exchange_known=False — feed câm/ambiguous) ⇒ rơi về
    `exchange_override` đã học (HOSE) ⇒ vẫn sweep ATC bình thường, không chặn nhầm."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="HOSE", exchange_known=False)
        ex, o = make_executor(tmp, "SHS", br, parent_filled=800,
                              exchange_override="HOSE")
        ex._atc_sweep()
        ok(br.quote_calls == ["SHS"], f"vẫn phải thử quote trước: {br.quote_calls}")
        ok(br.placed == [("SHS", 200, "sell", "ATC")],
           f"quote không biết sàn ⇒ rơi về override HOSE ⇒ ATC đi ra: {br.placed}")


def t_quote_returns_none_fails_open_to_hose():
    """`get_quote` trả `None` (không ném) — đường lỗi THẬT của PHS/phs_flash
    (`trading_bot/brokers.py:354,:1385`; DNSE không rơi vào ca này, nó mặc định HOSE qua
    `MARKET_ID_TO_EXCHANGE` câm) — phải cùng đường fail-open HOSE như khi get_quote ném lỗi."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM", quote_returns_none=True)
        ex, o = make_executor(tmp, "CCC", br, parent_filled=800)
        ex._atc_sweep()
        ok(br.quote_calls == ["CCC"], f"phải có thử gọi get_quote: {br.quote_calls}")
        ok(br.placed == [("CCC", 200, "sell", "ATC")],
           f"get_quote trả None ⇒ fail-open HOSE ⇒ ATC vẫn đi ra, được: {br.placed}")


def t_real_quote_missing_market_id_is_ambiguous_fails_open_hose():
    """Dùng `brokers.Quote` THẬT (không phải `_Quote` giả tự set `.exchange` tay) — payload
    thiếu `marketId`/`exchange`/`market`/`floorcode` ⇒ `exchange_known=False` đúng như đo thật
    2026-08-15 (xem comment `MARKET_ID_TO_EXCHANGE`) ⇒ không override ⇒ fail-open HOSE."""
    from trading_bot.brokers import Quote

    class _RealQuoteBroker(_StubBroker):
        def get_quote(self, ticker):
            self.quote_calls.append(ticker)
            return Quote({"symbol": ticker, "lastprice": 28000, "refprice": 28000})

    with tempfile.TemporaryDirectory() as tmp:
        br = _RealQuoteBroker()
        q = br.get_quote("DDD-PROBE")
        ok(q.exchange_known is False, f"Quote thiếu marketId phải exchange_known=False: {vars(q)}")
        br.quote_calls.clear()
        ex, o = make_executor(tmp, "DDD", br, parent_filled=800)
        ex._atc_sweep()
        ok(br.placed == [("DDD", 200, "sell", "ATC")],
           f"exchange_known=False, không override ⇒ fail-open HOSE ⇒ ATC đi ra: {br.placed}")


def t_real_quote_market_id_upx_skips_atc():
    """`brokers.Quote` THẬT với `marketId="UPX"` (mã sàn UPCOM thô DNSE,
    `MARKET_ID_TO_EXCHANGE`) ⇒ `exchange="UPCOM"`, `exchange_known=True` ⇒ UPCOM_SKIP_ATC.
    Đi qua đường map marketId thật — `_Quote` giả (chỉ set `.exchange` tay) không chạm được
    nhánh này, nên không giết được một mutation làm hỏng `MARKET_ID_TO_EXCHANGE`/`exchange_known`
    bên trong `brokers.Quote` chính nó."""
    from trading_bot.brokers import Quote

    class _RealQuoteBroker(_StubBroker):
        def get_quote(self, ticker):
            self.quote_calls.append(ticker)
            return Quote({"symbol": ticker, "marketid": "UPX",
                         "lastprice": 28000, "refprice": 28000})

    with tempfile.TemporaryDirectory() as tmp:
        br = _RealQuoteBroker()
        ex, o = make_executor(tmp, "SCL", br, parent_filled=800)
        ex._atc_sweep()
        ok(br.placed == [], f"marketId=UPX ⇒ UPCOM thật ⇒ KHÔNG đặt ATC: {br.placed}")
        ok("UPCOM_SKIP_ATC" in _events(ex), f"phải journal UPCOM_SKIP_ATC: {_events(ex)}")


def t_real_incident_repro_45_cycles_no_place_order():
    """Tái hiện đúng hình dạng sự cố thật (đính chính 2026-10-01 vòng 2: journal thật
    `exec_ZaloPay_2026-10-01_journal.csv` có 45 dòng ATC_FAIL, 14:30:04→14:44:53, không phải
    42/14:33:46 như bản nháp đầu): 45 chu kỳ poll liên tiếp trên SCL (UPCOM), KHÔNG CÓ lần nào
    gọi place_order — khác hẳn log thật nơi DNSE bị gọi 45 lần và trả HTTP 400 mỗi lần."""
    with tempfile.TemporaryDirectory() as tmp:
        br = _StubBroker(exchange="UPCOM")
        ex, o = make_executor(tmp, "SCL", br, parent_filled=800, qty=1000)
        for _ in range(45):
            ex._atc_sweep()
        ok(br.placed == [], f"45 chu kỳ UPCOM: place_order phải KHÔNG BAO GIỜ được gọi: {br.placed}")
        n_skip = _events(ex).count("UPCOM_SKIP_ATC")
        ok(n_skip == 45, f"phải có đúng 45 dòng UPCOM_SKIP_ATC (1/chu kỳ), được {n_skip}")


def t_invalid_ordertype_error_sets_unsupported_flag_stops_retry():
    """Lưới an toàn PHỤ (item 2, arch-review R2): dù nhận diện sàn ở trên lọt (vd quote câm
    + chưa học override + fail-open HOSE SAI cho một mã thật ra UPCOM), broker trả lỗi
    'Invalid ordertype' (HTTP 400) phải đặt `ps['atc_unsupported']=True` ngay LẦN ĐẦU TIÊN,
    đóng đường lặp vô hạn của chính sự cố gốc — 45 chu kỳ chỉ 1 lần gọi place_order thật."""
    class _RejectOrdertypeBroker(_StubBroker):
        def place_order(self, ticker, qty, side, **k):
            self.placed.append((ticker, qty, side, k.get("order_type")))
            from dnse_api import DNSEError
            raise DNSEError("HTTP 400: Invalid ordertype for the exchange", status=400)

    with tempfile.TemporaryDirectory() as tmp:
        br = _RejectOrdertypeBroker(exchange="HOSE")  # sàn nhận diện SAI (fail-safe lọt)
        ex, o = make_executor(tmp, "EEE", br, parent_filled=800, qty=1000)
        for _ in range(45):
            ex._atc_sweep()
        ok(len(br.placed) == 1,
           f"phải chỉ gọi place_order ĐÚNG 1 LẦN rồi ngừng, được {len(br.placed)}: {br.placed}")
        ok(ex.state["parents"]["SELL-01"]["atc_unsupported"] is True,
           "atc_unsupported phải được đặt True sau lần lỗi đầu tiên")
        n_fail = _events(ex).count("ATC_FAIL")
        ok(n_fail == 1, f"phải chỉ có đúng 1 dòng ATC_FAIL (không lặp 45 lần), được {n_fail}")


TESTS = [t_upcom_skips_atc_no_place_order, t_upcom_does_not_cancel_live_lo,
         t_hose_still_sweeps_atc_control, t_quote_error_fails_open_to_hose,
         t_quote_known_wins_over_stale_exchange_override,
         t_override_fallback_when_quote_unknown,
         t_quote_returns_none_fails_open_to_hose,
         t_real_quote_missing_market_id_is_ambiguous_fails_open_hose,
         t_real_quote_market_id_upx_skips_atc,
         t_real_incident_repro_45_cycles_no_place_order,
         t_invalid_ordertype_error_sets_unsupported_flag_stops_retry]

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
