#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check cho cổng corp-action của `discretionary_accumulation_inject.py::broker_filled_qty()`
(job Taylor_20260924_064510, Việc 1 — ưu tiên cao nhất, LIVE hôm nay: TV1 SpaceX + ZaloPay,
baseline_qty_before_program=0).

BUG ĐÃ SỬA: `broker_filled_qty()` trừ thẳng `total − baseline` từ `positions.total` đọc broker,
không phân biệt KL do LỆNH GOM MUA THÊM với KL do BROKER CREDIT sự kiện tỉ lệ (thưởng CP/cổ tức
CP/tách). Credit sự kiện thổi phồng `filled_qty` ⇒ `remaining <= 0` giả ⇒ chương trình
`mark_completed=True` SAI, dừng gom sớm TRONG IM LẶNG (không cảnh báo — khác
`discretionary_margin_gate` nơi hậu quả là cảnh báo GIẢ).

Vá: đối chiếu qua `exdate_frame.classify_positions()` (TÁI DÙNG nguyên khối đã audit 5 vòng ở
`compute_active_nav.py`) trước khi trừ — có sự kiện CONFIRMED thì quy đổi baseline; KL bất
thường không giải thích được thì fail-safe (filled=None, không đoán, §29); lỗi hạ tầng phụ trợ
(exdate_frame tự thân lỗi) thì KHÔNG fail-closed cả cổng, giữ hành vi CŨ.

MỌI CA CHẠY QUA HÀM THẬT `broker_filled_qty()` + `compute_session_order()` thật (không mock nội
bộ), chỉ FakeBroker (KHÔNG chạm DNSE thật) và monkeypatch `exdate_frame.classify_positions`
(KHÔNG chạm BQ/journal/corp_action_daily thật). Section Z chạy MUTATION GUARD: mỗi assertion
then phải CHẾT (không PASS) khi patch bị revert từng phần — chứng minh test thật sự bắt được bug,
không phải PASS-vô-điều-kiện.

Không chạm bus/file production. Chạy: python3 mike/bin/discretionary_accumulation_inject_selfcheck.py
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import wc_paths  # noqa: E402
WC = wc_paths.find_wc_root(__file__)

fails = []
_case_id = [0]


def check(name, cond, detail=""):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)
    return cond


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


dai = load_module("_sc_discretionary_accumulation_inject",
                   os.path.join(HERE, "discretionary_accumulation_inject.py"))
import exdate_frame  # noqa: E402 — bin/ đã vào sys.path qua load_module(dai) ở trên
import trading_bot.brokers as tb_brokers  # noqa: E402
from trading_bot.discretionary_accumulation import compute_session_order  # noqa: E402

ORIG_DNSEBROKER = tb_brokers.DNSEBroker
ORIG_CLASSIFY = exdate_frame.classify_positions
TICKER = "TV1"


def restore():
    tb_brokers.DNSEBroker = ORIG_DNSEBROKER
    exdate_frame.classify_positions = ORIG_CLASSIFY


class FakeBroker:
    def __init__(self, total_by_ticker):
        self._total = total_by_ticker

    def connect(self):
        pass

    def get_positions(self):
        return {tk: {"total": q} for tk, q in self._total.items()}


def broker_factory(total_by_ticker):
    def _factory(account_id=None, credentials_file=None, label=None):
        return FakeBroker(total_by_ticker)
    return _factory


def classify_stub(credited, blocked):
    def _fake(account_label, account_no, asof, positions):
        return dict(credited), dict(blocked)
    return _fake


def classify_raiser(exc):
    def _fake(*a, **kw):
        raise exc
    return _fake


def target_state(target_qty):
    return {"ticker": TICKER, "status": "active", "target_qty": target_qty, "lot_size": 100,
            "per_session_cap_pct_adv": 0.1, "adv_ref_vnd": 500_000_000,
            "price_band": {"no_chase_ceiling": 30000, "resting_limit": 29000}}


# ── Section A — CÓ sự kiện CONFIRMED: quy đổi baseline đúng, KHÔNG mark_completed sai ──────
print("A. Có sự kiện corp-action CONFIRMED — quy đổi baseline, filled tính đúng, "
      "KHÔNG mark_completed sai")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1360})
    exdate_frame.classify_positions = classify_stub(
        {TICKER: {"residual": 260.0, "exercise_ratio": 0.26, "event_code": "ISS",
                  "ex_date": "2026-09-25", "qty_prev": 1000.0, "qty_now": 1260.0}}, {})
    state = {"baseline_qty_before_program": 1000}
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    check("A1 filled=100 (1360 broker − baseline quy đổi 1260, KHÔNG đếm 260cp credit là gom)",
          filled == 100, f"filled={filled}")
    check("A2 baseline state quy đổi 1000→1260 (PERSIST)",
          state.get("baseline_qty_before_program") == 1260,
          f"baseline={state.get('baseline_qty_before_program')}")
    check("A3 note không rỗng, nhắc 'credit'", bool(note) and "credit" in note.lower(), f"note={note!r}")
    adj = (state.get("corp_action_baseline_adjustments") or [{}])[0]
    check("A4 corp_action_baseline_adjustments ghi đúng residual=260.0",
          adj.get("residual") == 260.0, f"adj={adj}")

    order, decision = compute_session_order(
        target_state(200), filled, 100_000_000, 29500, "2026-09-25", "2026-09-24T20:30:00+07:00")
    check("A5 mark_completed KHÔNG bật SAI (remaining=100>0)",
          not decision.get("mark_completed"), f"decision={decision}")
    check("A6 decision.action='inject' (đúng — còn phải gom tiếp)",
          decision.get("action") == "inject", f"action={decision.get('action')}")
    check("A7 decision.filled_qty=100 (khớp filled đã quy đổi)",
          decision.get("filled_qty") == 100, f"filled_qty={decision.get('filled_qty')}")

    # Đối chứng: filled TÍNH SAI theo công thức CŨ (total-baseline THÔ, không quy đổi) ở CÙNG
    # dữ liệu này sẽ trigger mark_completed=True SAI ở target=150 — đúng bug dispatch mô tả.
    old_buggy_filled = 1360 - 1000  # = 360, KHÔNG dùng cổng mới
    _, decision_bug = compute_session_order(
        target_state(150), old_buggy_filled, 100_000_000, 29500,
        "2026-09-25", "2026-09-24T20:30:00+07:00")
    check("A8 [đối chứng] filled SAI (360, công thức cũ) trigger mark_completed=True ở "
          "target=150 — xác nhận đây đúng là lớp bug cổng mới đang chặn",
          decision_bug.get("mark_completed") is True, f"decision_bug={decision_bug}")
finally:
    restore()

# ── Section B — KHÔNG có sự kiện: hành vi CŨ giữ nguyên (không phá luồng gom thật) ─────────
print("B. KHÔNG có sự kiện — hành vi CŨ giữ nguyên (filled = total - baseline, không đổi)")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1150})
    exdate_frame.classify_positions = classify_stub({}, {})
    state = {"baseline_qty_before_program": 1000}
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    check("B1 filled=150 (lệnh gom thật, hành vi cũ nguyên vẹn)", filled == 150, f"filled={filled}")
    check("B2 note=None (không có gì bất thường)", note is None, f"note={note!r}")
    check("B3 baseline KHÔNG bị đổi", state.get("baseline_qty_before_program") == 1000)
    check("B4 không ghi corp_action_baseline_adjustments",
          "corp_action_baseline_adjustments" not in state)
finally:
    restore()

# ── Section C — KL bất thường KHÔNG giải thích được: fail-safe, KHÔNG mark_completed ──────
print("C. KL đổi bất thường KHÔNG giải thích được — fail-safe, KHÔNG mark_completed")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1500})
    exdate_frame.classify_positions = classify_stub(
        {}, {TICKER: "KL 1.000→1.500 (so với 2026-09-23), lệnh khớp thật +50 ⇒ phần dư +450 "
                     "CHƯA GIẢI THÍCH ĐƯỢC"})
    state = {"baseline_qty_before_program": 1000}
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    check("C1 filled=None (fail-safe, KHÔNG đoán theo tỉ lệ)", filled is None, f"filled={filled}")
    check("C2 broker vẫn trả về (đọc được, chỉ khối lượng nghi vấn)", broker is not None)
    check("C3 note cảnh báo rõ, nhắc 'CHƯA GIẢI THÍCH'",
          bool(note) and "CHƯA GIẢI THÍCH" in note, f"note={note!r}")
    check("C4 baseline KHÔNG bị đổi khi blocked", state.get("baseline_qty_before_program") == 1000)

    order, decision = compute_session_order(
        target_state(200), filled, 100_000_000, 29500, "2026-09-25", "2026-09-24T20:30:00+07:00")
    check("C5 order=None khi filled=None", order is None)
    check("C6 decision.action='failsafe'", decision.get("action") == "failsafe",
          f"action={decision.get('action')}")
    check("C7 mark_completed KHÔNG có mặt/False", not decision.get("mark_completed"))
finally:
    restore()

# ── Section D — exdate_frame tự thân lỗi (IO/BQ down): KHÔNG fail-closed cả cổng ──────────
print("D. exdate_frame.classify_positions tự thân lỗi — KHÔNG fail-closed cả cổng (giữ CŨ)")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1150})
    exdate_frame.classify_positions = classify_raiser(RuntimeError("BQ down"))
    state = {"baseline_qty_before_program": 1000}
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    check("D1 filled vẫn tính được = 150 (KHÔNG fail-closed vì lỗi phụ trợ)",
          filled == 150, f"filled={filled}")
    check("D2 note=None (lỗi hạ tầng không bị coi là sự kiện corp-action)", note is None)
finally:
    restore()

# ── Section E — broker không đọc được (hồi quy hành vi CŨ) ────────────────────────────────
print("E. Broker không đọc được (hồi quy) — fail-safe (None, None, None)")
try:
    def _raise_factory(**kw):
        raise ConnectionError("DNSE down")
    tb_brokers.DNSEBroker = _raise_factory
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000)
    check("E1 filled=None", filled is None)
    check("E2 broker=None", broker is None)
    check("E3 note=None", note is None)
finally:
    restore()


# ═══════════════════════════════════════ MUTATION GUARD ═══════════════════════════════════
# Không sửa file nguồn — patch object trong module ĐÃ LOAD (dai) để giả lập từng mutation, rồi
# chạy lại đúng kịch bản tương ứng và xác nhận assertion CHẾT (đảo verdict PASS→FAIL). Mutant
# nào không giết được ⇒ bản thân MUTATION GUARD này FAIL (bắt bằng biến `killed`).
print("Z. MUTATION GUARD — mỗi assertion trên phải chết đúng mutation của nó")
mutation_results = []


def run_case_A_filled_and_baseline():
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1360})
    exdate_frame.classify_positions = classify_stub(
        {TICKER: {"residual": 260.0, "exercise_ratio": 0.26, "event_code": "ISS",
                  "ex_date": "2026-09-25", "qty_prev": 1000.0, "qty_now": 1260.0}}, {})
    state = {"baseline_qty_before_program": 1000}
    filled, _b, _n = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    return filled == 100 and state.get("baseline_qty_before_program") == 1260


def run_case_C_blocked_failsafe():
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1500})
    exdate_frame.classify_positions = classify_stub(
        {}, {TICKER: "phần dư CHƯA GIẢI THÍCH ĐƯỢC"})
    state = {"baseline_qty_before_program": 1000}
    filled, _b, _n = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    return filled is None


def run_case_D_infra_error_not_closed():
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1150})
    exdate_frame.classify_positions = classify_raiser(RuntimeError("BQ down"))
    state = {"baseline_qty_before_program": 1000}
    filled, _b, _n = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    return filled == 150


def mutate(name, patch_fn, oracle_fn):
    """`patch_fn` monkeypatches `dai.broker_filled_qty` để mô phỏng mutation; `oracle_fn` là
    ĐÚNG kịch bản test-case ở trên còn nguyên. PASS của mutation-guard = oracle_fn() trả FALSE
    (nghĩa là assertion gốc SẼ bắt được mutation này nếu nó thật sự lọt vào code)."""
    orig_fn = dai.broker_filled_qty
    try:
        patch_fn()
        killed = not oracle_fn()
        check(f"Z-{name} mutant bị giết (assertion đảo verdict)", killed)
        mutation_results.append((name, killed))
    finally:
        dai.broker_filled_qty = orig_fn
        restore()


# Mutant 1: bỏ qua bước quy đổi baseline khi credited (như thể block "if ticker in credited"
# không tồn tại) — filled sẽ tính THẲNG total-baseline gốc (360 thay vì 100).
def _mut1():
    def fake(account, account_id, ticker, baseline, state=None):
        return max(0, 1360 - 1000), None, None   # bỏ hẳn cổng — mô phỏng code CŨ trước vá
    dai.broker_filled_qty = fake


mutate("baseline-not-converted", _mut1, run_case_A_filled_and_baseline)


# Mutant 2: bỏ qua nhánh `blocked` (coi mọi KL bất thường như bình thường, trừ thẳng).
def _mut2():
    def fake(account, account_id, ticker, baseline, state=None):
        return max(0, 1500 - 1000), None, None   # không fail-safe khi blocked
    dai.broker_filled_qty = fake


mutate("blocked-not-failsafe", _mut2, run_case_C_blocked_failsafe)


# Mutant 3: fail-closed TOÀN BỘ cổng khi exdate_frame tự lỗi (thay vì giữ hành vi cũ).
def _mut3():
    def fake(account, account_id, ticker, baseline, state=None):
        return None, None, "fail-closed vì lỗi hạ tầng"   # SAI theo docstring — phải fail-open
    dai.broker_filled_qty = fake


mutate("infra-error-wrongly-fail-closed", _mut3, run_case_D_infra_error_not_closed)


n_mutation_fail = sum(1 for _, k in mutation_results if not k)
check(f"Z-summary {len(mutation_results)}/{len(mutation_results)} mutant bị giết",
      n_mutation_fail == 0, f"sống sót: {[n for n, k in mutation_results if not k]}")


# ── kết luận ────────────────────────────────────────────────────────────────────────────
print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ ALL PASS")
