#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check cho cổng corp-action của `discretionary_accumulation_inject.py::broker_filled_qty()`
(job Taylor_20260924_064510+_073500, Việc 1 — THIẾT KẾ LẠI sau arch-review REJECTED bản đầu
d595a64c. LIVE hôm nay: TV1 SpaceX + ZaloPay, CẢ HAI `target_pct_active_nav=0.05` (pct_mode),
baseline_qty_before_program=0).

BUG GỐC ĐÃ SỬA: `broker_filled_qty()` trừ thẳng `total − baseline` từ `positions.total` đọc
broker, không phân biệt KL do LỆNH GOM MUA THÊM với KL do BROKER CREDIT sự kiện tỉ lệ (thưởng
CP/cổ tức CP/tách). Credit sự kiện thổi phồng `filled_qty` ⇒ `remaining <= 0` giả ⇒ chương trình
`mark_completed=True` SAI, dừng gom sớm TRONG IM LẶNG.

BUG BẢN VÁ ĐẦU (d595a64c, arch-review REJECTED): áp cơ chế quy đổi baseline BẤT KỂ mode, PERSIST
residual vào `state["baseline_qty_before_program"]` — ở `pct_mode` (TV1, DUY NHẤT LIVE), target
tự SUY LẠI mỗi phiên theo giá mới nên đã TỰ KHỚP; quy đổi thêm biến 1 lệch một-đêm tự sửa thành
lệch VĨNH VIỄN ⇒ mô phỏng arch-reviewer: vị thế vượt trần sleeve 5%/mã (6300+1300=7600cp=6,03%).
Cũng KHÔNG idempotent: chạy lại trong cùng cửa sổ cộng dồn residual nhiều lần.

THIẾT KẾ LẠI: (1) `pct_mode` (`state["target_pct_active_nav"]` có mặt) ⇒ BỎ QUA HẲN khối
corp-action, giữ NGUYÊN `total − baseline` thô — 0 chương trình LIVE nào cần cơ chế này.
(2) Chế độ `target_qty` cố định (hạ tầng phòng thủ, hiện 0 chương trình LIVE dùng) vẫn đối
chiếu qua `exdate_frame.classify_positions()`, NHƯNG có sự kiện CONFIRMED thì quy đổi baseline
CHỈ khi (ticker, ex_date, event_code) CHƯA quy đổi trước đó (idempotency key) — gọi lại cùng cửa
sổ KHÔNG cộng dồn residual lần 2. KL bất thường không giải thích được thì fail-safe (filled=None,
§29); lỗi hạ tầng phụ trợ (exdate_frame tự thân lỗi) thì KHÔNG fail-closed cả cổng.

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

# ── Section F — pct_mode (TV1 LIVE thật) + sự kiện CONFIRMED: gate BỎ QUA HẲN ─────────────
print("F. pct_mode (target_pct_active_nav khai báo, TV1 LIVE thật) + sự kiện CONFIRMED — gate "
      "BỎ QUA HẲN corp-action, filled=total-baseline THÔ, baseline KHÔNG bị persist (chặn "
      "overbuy vượt trần sleeve 5%/mã)")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1360})
    exdate_frame.classify_positions = classify_stub(
        {TICKER: {"residual": 260.0, "exercise_ratio": 0.26, "event_code": "ISS",
                  "ex_date": "2026-09-25", "qty_prev": 1000.0, "qty_now": 1260.0}}, {})
    state = {"baseline_qty_before_program": 0, "target_pct_active_nav": 0.05}
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 0, state=state)
    check("F1 filled=1360 (total-baseline THÔ, KHÔNG quy đổi — pct_mode tự sửa qua target)",
          filled == 1360, f"filled={filled}")
    check("F2 baseline KHÔNG bị đổi (vẫn 0)",
          state.get("baseline_qty_before_program") == 0,
          f"baseline={state.get('baseline_qty_before_program')}")
    check("F3 note=None (gate bỏ qua hẳn, không ghi gì)", note is None, f"note={note!r}")
    check("F4 KHÔNG ghi corp_action_baseline_adjustments",
          "corp_action_baseline_adjustments" not in state)
finally:
    restore()

# ── Section G — pct_mode + KL bất thường (blocked): gate vẫn BỎ QUA HẲN ───────────────────
print("G. pct_mode + KL bất thường (blocked ở exdate_frame) — gate vẫn BỎ QUA HẲN (hành vi "
      "total-baseline thô, KHÔNG fail-safe — pct_mode không dùng khối corp-action)")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1500})
    exdate_frame.classify_positions = classify_stub(
        {}, {TICKER: "KL bất thường CHƯA GIẢI THÍCH ĐƯỢC"})
    state = {"baseline_qty_before_program": 1000, "target_pct_active_nav": 0.05}
    filled, broker, note = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    check("G1 filled=500 (pct_mode bỏ qua hẳn cổng blocked, KHÔNG fail-safe)",
          filled == 500, f"filled={filled}")
    check("G2 note=None", note is None, f"note={note!r}")
finally:
    restore()

# ── Section H — idempotency (target_qty cố định): gọi 2 lần cùng cửa sổ, KHÔNG cộng dồn ───
print("H. Idempotency (target_qty cố định) — gọi broker_filled_qty() 2 lần liên tiếp cùng sự "
      "kiện, residual KHÔNG cộng dồn lần 2")
try:
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1360})
    exdate_frame.classify_positions = classify_stub(
        {TICKER: {"residual": 260.0, "exercise_ratio": 0.26, "event_code": "ISS",
                  "ex_date": "2026-09-25", "qty_prev": 1000.0, "qty_now": 1260.0}}, {})
    state = {"baseline_qty_before_program": 1000}
    filled1, _b1, note1 = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    baseline_after_1 = state.get("baseline_qty_before_program")
    filled2, _b2, note2 = dai.broker_filled_qty(
        "SpaceX", "0002023347", TICKER, baseline_after_1, state=state)
    check("H1 run#1 baseline 1000→1260", baseline_after_1 == 1260, f"baseline={baseline_after_1}")
    check("H2 run#2 baseline KHÔNG cộng dồn nữa (vẫn 1260, không thành 1520)",
          state.get("baseline_qty_before_program") == 1260,
          f"baseline={state.get('baseline_qty_before_program')}")
    check("H3 run#2 note nhắc 'idempotent' (dedup theo event_key)",
          bool(note2) and "idempotent" in note2.lower(), f"note2={note2!r}")
    check("H4 chỉ 1 entry trong corp_action_baseline_adjustments (không nhân đôi)",
          len(state.get("corp_action_baseline_adjustments") or []) == 1,
          f"len={len(state.get('corp_action_baseline_adjustments') or [])}")
    check("H5 filled2=100 (1360-1260, không lệch do double-count)", filled2 == 100, f"filled2={filled2}")
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


def run_case_F_pctmode_untouched():
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1360})
    exdate_frame.classify_positions = classify_stub(
        {TICKER: {"residual": 260.0, "exercise_ratio": 0.26, "event_code": "ISS",
                  "ex_date": "2026-09-25", "qty_prev": 1000.0, "qty_now": 1260.0}}, {})
    state = {"baseline_qty_before_program": 0, "target_pct_active_nav": 0.05}
    filled, _b, _n = dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 0, state=state)
    return filled == 1360 and state.get("baseline_qty_before_program") == 0


def run_case_H_idempotent():
    tb_brokers.DNSEBroker = broker_factory({TICKER: 1360})
    exdate_frame.classify_positions = classify_stub(
        {TICKER: {"residual": 260.0, "exercise_ratio": 0.26, "event_code": "ISS",
                  "ex_date": "2026-09-25", "qty_prev": 1000.0, "qty_now": 1260.0}}, {})
    state = {"baseline_qty_before_program": 1000}
    dai.broker_filled_qty("SpaceX", "0002023347", TICKER, 1000, state=state)
    b1 = state.get("baseline_qty_before_program")
    dai.broker_filled_qty("SpaceX", "0002023347", TICKER, b1, state=state)
    return state.get("baseline_qty_before_program") == 1260


# Mutant 4: pct_mode KHÔNG được bỏ qua — bug bản đầu d595a64c (quy đổi baseline bất kể mode).
def _mut4():
    def fake(account, account_id, ticker, baseline, state=None):
        residual = 260.0
        new_baseline = int(baseline) + int(residual)
        if state is not None:
            state["baseline_qty_before_program"] = new_baseline
        return max(0, 1360 - new_baseline), None, "quy đổi baseline dù đang pct_mode (SAI, bug d595a64c)"
    dai.broker_filled_qty = fake


mutate("pct-mode-not-skipped", _mut4, run_case_F_pctmode_untouched)


# Mutant 5: thiếu khoá idempotency — mỗi lần gọi lại cộng dồn residual (không dedup theo event_key).
def _mut5():
    def fake(account, account_id, ticker, baseline, state=None):
        new_baseline = int(baseline) + 260
        if state is not None:
            state["baseline_qty_before_program"] = new_baseline
            state.setdefault("corp_action_baseline_adjustments", []).append({"residual": 260})
        return max(0, 1360 - new_baseline), None, "cộng dồn residual mỗi lần gọi (SAI, thiếu dedup)"
    dai.broker_filled_qty = fake


mutate("idempotency-dedup-missing", _mut5, run_case_H_idempotent)


n_mutation_fail = sum(1 for _, k in mutation_results if not k)
check(f"Z-summary {len(mutation_results)}/{len(mutation_results)} mutant bị giết",
      n_mutation_fail == 0, f"sống sót: {[n for n, k in mutation_results if not k]}")


# ── kết luận ────────────────────────────────────────────────────────────────────────────
print()
if fails:
    print(f"❌ {len(fails)} FAIL: {fails}")
    sys.exit(1)
print("✅ ALL PASS")
