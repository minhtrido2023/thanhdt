#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `discretionary_margin_gate.py` — 0 side-effect thật (không ghi bus/Discord thật,
không đụng `data/discretionary_margin_arms.json` production).

Theo skill verify-before-done: chạy dưới TZ lạ (env -u TZ) để bắt lỗi neo múi giờ tường minh (§16).
KHÔNG chạm Executor (sleeve này không wire vào bot) nên không cần MIKE_BOT_TEST_MODE (§5b).

Bước 13-18 (job Taylor_20260924_064510, Việc 2) — cổng corp-action của `cmd_check_exits()`.
BUG ĐÃ SỬA: `drawdown = px / a["arm_price"] - 1.0` so `arm_price` (hệ giá TẠI THỜI ĐIỂM ARM) với
`px` hiện tại (đã tự nhiên đi qua mọi sự kiện tỉ lệ giữa lúc arm và bây giờ) mà KHÔNG quy đổi —
nhân chéo hai hệ quy chiếu giống bug đã vá ở `compute_active_nav.py` (`exdate_frame.py`). Sự kiện
tỉ lệ giữa hai mốc ⇒ cảnh báo de-lever GIẢ. Vá: `corp_action_frame_multiplier()` đối chiếu qua
`exdate_frame.classify_positions()` (tái dùng nguyên khối đã audit 5 vòng) — CONFIRMED thì quy đổi
arm_price theo hệ số tích luỹ; KL bất thường không giải thích được thì FAIL-CLOSED; lỗi hạ tầng
phụ trợ thì KHÔNG fail-closed cả cổng, giữ hành vi CŨ. Chỉ mock `current_price`, `_account_id_for`,
`trading_bot.brokers.DNSEBroker`, `exdate_frame.classify_positions` (KHÔNG chạm DNSE/BQ thật).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_margin_gate as gate  # noqa: E402
import exdate_frame  # noqa: E402
import trading_bot.brokers as tb_brokers  # noqa: E402

PASS = []
FAIL = []


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
    else:
        FAIL.append((name, detail))
        print(f"❌ FAIL: {name} — {detail}")


class _NoBus:
    """Chặn mọi side-effect thật ra bus/Discord trong selfcheck — trả True (giả lập thành công)
    để test logic gate, không phải test hạ tầng notify."""
    calls = []

    def bus(self, kind, topic, payload, trace_id=None):
        _NoBus.calls.append(("bus", kind, topic))
        return True

    def notify(self, msg):
        _NoBus.calls.append(("notify", msg))
        return True


def _patch_io(monkey_nav=None, monkey_adv=None, monkey_price=None):
    if monkey_nav is not None:
        gate.latest_nav = lambda account: monkey_nav
    if monkey_adv is not None:
        gate.adv_3m = lambda ticker: monkey_adv
    if monkey_price is not None:
        gate.current_price = lambda ticker: monkey_price


class _FakeBroker:
    def __init__(self, total_by_ticker):
        self._total = total_by_ticker

    def connect(self):
        pass

    def get_positions(self):
        return {tk: {"total": q} for tk, q in self._total.items()}


def _broker_factory(total_by_ticker):
    def _f(account_id=None, credentials_file=None, label=None):
        return _FakeBroker(total_by_ticker)
    return _f


def _classify_stub(credited, blocked):
    def _f(account_label, account_no, asof, positions):
        return dict(credited), dict(blocked)
    return _f


def _mk_arm(arm_price, ticker="VPB"):
    return {"ticker": ticker, "account": "SpaceX", "arm_price": arm_price, "shares": 1000,
            "exposure_vnd": arm_price * 1000, "f": 1.0, "exited": False, "exit_alerts": []}


def main():
    tmpdir = tempfile.mkdtemp(prefix="dmg_selfcheck_")
    gate.ARMS_PATH = os.path.join(tmpdir, "arms.json")
    no_bus = _NoBus()
    gate._bus = no_bus.bus
    gate._notify = no_bus.notify

    NAV = (1_000_000_000.0, "2026-08-28")   # NAV 1 ty VND
    ADV_OK = (1_000_000_000.0, "2026-08-28", None)   # ADV 1 ty/ngay -> 10% = 100tr

    base_args = dict(account="SpaceX", shares=0, exposure_vnd=None, f=1.3,
                      marginability_confirmed_by="Mafee — loan_packages verified job Mafee_x",
                      fundamental_skeptic_confirmed=True, rating_8l=2,
                      approved_by="user (John) — test", decided_by="user", dry_run=False)

    def mkargs(**overrides):
        d = dict(base_args)
        d.update(overrides)
        return argparse_ns(d)

    import argparse as _argparse

    def argparse_ns(d):
        return _argparse.Namespace(**d)

    # ---- 1. per-name cap block: exposure 6% NAV > 5% cap ----
    _patch_io(monkey_nav=NAV, monkey_adv=ADV_OK)
    gate.save_arms([])
    rc = gate.cmd_arm(mkargs(ticker="AAA", arm_price=10000, exposure_vnd=0.06 * NAV[0]))
    check("per-name cap chan exposure 6% NAV (cap 5%)", rc == 2, f"rc={rc}")
    check("per-name cap block KHONG ghi arm", len(gate.load_arms()) == 0)

    # ---- 2. successful arm tai dung 5% NAV (bien) ----
    gate.save_arms([])
    rc = gate.cmd_arm(mkargs(ticker="TV1", arm_price=20000, exposure_vnd=0.05 * NAV[0]))
    check("arm thanh cong tai dung tran 5% NAV per-name", rc == 0, f"rc={rc}")
    arms = gate.load_arms()
    check("arm ghi 1 record", len(arms) == 1, f"len={len(arms)}")
    if arms:
        check("record co f=1.3", arms[0]["f"] == 1.3)
        check("record co pct_nav_exposure ~0.05", abs(arms[0]["pct_nav_exposure"] - 0.05) < 1e-6)

    # ---- 3. sleeve cap: case thu 2 tai dung tran per-name (5%) -> tong 10% == sleeve cap, PASS ----
    rc = gate.cmd_arm(mkargs(ticker="DGC", arm_price=5000, exposure_vnd=0.05 * NAV[0]))
    check("case thu 2 tai 5% NAV thanh cong (tong 10% == sleeve cap, khong vuot)", rc == 0, f"rc={rc}")
    check("sleeve tai tran co 2 record", len(gate.load_arms()) == 2)

    # ---- 3b. sleeve cap block: case thu 3 lam tong > 10% NAV ----
    rc = gate.cmd_arm(mkargs(ticker="DRI", arm_price=8000, exposure_vnd=0.01 * NAV[0]))
    check("sleeve cap chan case thu 3 (tong 11% > 10% cap)", rc == 2, f"rc={rc}")
    check("sleeve cap block KHONG them record moi", len(gate.load_arms()) == 2)

    # ---- 4. f > 1.3 hard-cap block ----
    gate.save_arms([])
    rc = gate.cmd_arm(mkargs(ticker="BBB", arm_price=10000, exposure_vnd=0.01 * NAV[0], f=2.0))
    check("f=2.0 > hard-cap 1.3 bi chan", rc == 2, f"rc={rc}")

    # ---- 5. %ADV cap block (exposure vuot 10% ADV du duoi tran %NAV) ----
    gate.save_arms([])
    adv_thin = (100_000_000.0, "2026-08-28", None)  # ADV mong: 100tr/ngay -> 10%=10tr
    _patch_io(monkey_nav=NAV, monkey_adv=adv_thin)
    rc = gate.cmd_arm(mkargs(ticker="CCC", arm_price=10000, exposure_vnd=0.02 * NAV[0]))
    check("exposure 2% NAV nhung vuot 10% ADV mong bi chan", rc == 2, f"rc={rc}")

    # ---- 6. marginability placeholder bi tu choi ----
    _patch_io(monkey_nav=NAV, monkey_adv=ADV_OK)
    gate.save_arms([])
    rc = gate.cmd_arm(mkargs(ticker="DDD", arm_price=10000, exposure_vnd=0.01 * NAV[0],
                              marginability_confirmed_by="mafee"))
    check("marginability placeholder ('mafee') bi tu choi", rc == 2, f"rc={rc}")

    # ---- 7. FAIL-SAFE: thieu NAV -> chan arm, khong doan ----
    gate.save_arms([])
    _patch_io(monkey_nav=(None, "khong doc duoc NAV"), monkey_adv=ADV_OK)
    rc = gate.cmd_arm(mkargs(ticker="EEE", arm_price=10000, exposure_vnd=1_000_000))
    check("fail-safe: thieu NAV chan arm (rc=3)", rc == 3, f"rc={rc}")

    # ---- 8. FAIL-SAFE: thieu ADV -> chan arm ----
    _patch_io(monkey_nav=NAV, monkey_adv=(None, None, "khong co du lieu ADV"))
    rc = gate.cmd_arm(mkargs(ticker="FFF", arm_price=10000, exposure_vnd=1_000_000))
    check("fail-safe: thieu ADV chan arm (rc=3)", rc == 3, f"rc={rc}")

    # ---- 9. check-exits: drawdown -20% -> alert ----
    _patch_io(monkey_nav=NAV, monkey_adv=ADV_OK)
    gate.save_arms([])
    gate.cmd_arm(mkargs(ticker="TV1", arm_price=20000, exposure_vnd=0.03 * NAV[0]))
    _NoBus.calls.clear()
    _patch_io(monkey_price=(16000.0, "dnse_g1_today", None))  # -20% dung nguong
    rc = gate.cmd_check_exits(_argparse.Namespace())
    arms = gate.load_arms()
    check("check-exits ghi last_drawdown ~-0.20", arms and abs(arms[0]["last_drawdown"] - (-0.20)) < 1e-6,
          f"{arms[0].get('last_drawdown') if arms else None}")
    check("check-exits ghi exit_alerts khi cham -20%", arms and len(arms[0]["exit_alerts"]) == 1)
    check("check-exits ban error len bus khi breach",
          any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls), str(_NoBus.calls))

    # ---- 10. check-exits: gia on dinh -> KHONG alert ----
    gate.save_arms([])
    gate.cmd_arm(mkargs(ticker="TV1", arm_price=20000, exposure_vnd=0.03 * NAV[0]))
    _NoBus.calls.clear()
    _patch_io(monkey_price=(19500.0, "dnse_g1_today", None))  # -2.5%, khong cham
    gate.cmd_check_exits(_argparse.Namespace())
    arms = gate.load_arms()
    check("gia on dinh KHONG sinh exit_alerts", arms and len(arms[0]["exit_alerts"]) == 0)
    check("gia on dinh KHONG ban 'error' len bus",
          not any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls))

    # ---- 11. exit dong case ----
    rc = gate.cmd_exit(_argparse.Namespace(ticker="TV1", reason="test chot"))
    check("exit dong case thanh cong", rc == 0, f"rc={rc}")
    check("case sau exit KHONG con active", len(gate.active_arms(gate.load_arms())) == 0)

    # ---- 12. account != SpaceX bi chan cung ----
    gate.save_arms([])
    rc = gate.cmd_arm(mkargs(ticker="TV1", arm_price=20000, exposure_vnd=1_000_000,
                              account="ZaloPay"))
    check("account ZaloPay (cash-only) bi chan cung", rc == 2, f"rc={rc}")

    # ════════════════════ CORP-ACTION GATE (cmd_check_exits) — Việc 2 ═══════════════════════
    ORIG_DNSEBROKER = tb_brokers.DNSEBroker
    ORIG_CLASSIFY = exdate_frame.classify_positions
    ORIG_ACCOUNT_ID_FOR = gate._account_id_for
    gate._account_id_for = lambda label: "0002023347"

    def _restore_corp_action_mocks():
        tb_brokers.DNSEBroker = ORIG_DNSEBROKER
        exdate_frame.classify_positions = ORIG_CLASSIFY

    # ---- 13. co su kien CONFIRMED -> arm_price quy doi dung he, drawdown that (-5%), KHONG breach gia
    try:
        gate.save_arms([_mk_arm(26000.0)])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1260})
        exdate_frame.classify_positions = _classify_stub(
            {"VPB": {"residual": 260.0, "exercise_ratio": 0.30, "event_code": "ISS",
                     "ex_date": "2026-09-25"}}, {})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("corp-action CONFIRMED: multiplier tich luy = 1.30",
              abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a0.get('corp_action_multiplier')}")
        check("corp-action CONFIRMED: arm_price_frame_adjusted = 20.000 (26.000/1,30)",
              abs(a0.get("arm_price_frame_adjusted", 0) - 20000.0) < 0.5, f"{a0.get('arm_price_frame_adjusted')}")
        check("corp-action CONFIRMED: drawdown that = -5% (KHONG phai -26,9% neu khong quy doi)",
              abs(a0.get("last_drawdown", 0) - (-0.05)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("corp-action CONFIRMED: KHONG breach gia",
              not any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls), str(_NoBus.calls))
        check("corp-action CONFIRMED: rc=0", rc == 0, f"rc={rc}")
        old_buggy = 19000.0 / 26000.0 - 1.0
        check("[doi chung] cong thuc CU (khong quy doi) se breach GIA (-26,9% <= -20%)",
              old_buggy <= -0.20, f"old_buggy_drawdown={old_buggy:.4f}")
    finally:
        _restore_corp_action_mocks()

    # ---- 14. KHONG co su kien -> hanh vi CU giu nguyen (drawdown nhe, khong breach)
    try:
        gate.save_arms([_mk_arm(20000.0)])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1000})
        exdate_frame.classify_positions = _classify_stub({}, {})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("khong su kien: KHONG co corp_action_multiplier", "corp_action_multiplier" not in a0)
        check("khong su kien: drawdown = -15% dung cong thuc cu",
              abs(a0.get("last_drawdown", 0) - (-0.15)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("khong su kien: KHONG breach (>-20%)",
              rc == 0 and not any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls))
    finally:
        _restore_corp_action_mocks()

    # ---- 15. KHONG co su kien, drawdown that vuot nguong -25% -> VAN breach dung (tin hieu that
    #          khong bi cong moi che mat)
    try:
        gate.save_arms([_mk_arm(20000.0)])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(15000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1000})
        exdate_frame.classify_positions = _classify_stub({}, {})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("khong su kien, drawdown that -25%: gia tri dung",
              abs(a0.get("last_drawdown", 0) - (-0.25)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("khong su kien, drawdown that -25%: breach THAT van kich hoat",
              any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls), str(_NoBus.calls))
    finally:
        _restore_corp_action_mocks()

    # ---- 16. KL bat thuong KHONG giai thich duoc -> fail-closed (khong tinh drawdown)
    try:
        gate.save_arms([_mk_arm(20000.0)])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(15000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1500})
        exdate_frame.classify_positions = _classify_stub(
            {}, {"VPB": "KL 1.000->1.500, lenh khop that +50 => phan du +450 CHUA GIAI THICH DUOC"})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("KL bat thuong: last_drawdown KHONG duoc set (fail-closed)", "last_drawdown" not in a0, f"{a0}")
        check("KL bat thuong: last_checked KHONG duoc set", "last_checked" not in a0)
        check("KL bat thuong: canh bao len bus (kind=error, topic corpaction-blocked)",
              any(c[0] == "bus" and c[1] == "error" and "corpaction-blocked" in c[2] for c in _NoBus.calls),
              str(_NoBus.calls))
        check("KL bat thuong: canh bao day Discord (notify)",
              any(c[0] == "notify" and "CẦN NGƯỜI xử lý tay" in c[1] for c in _NoBus.calls), str(_NoBus.calls))
        check("KL bat thuong: rc=1", rc == 1, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()

    # ---- 17. exdate_frame tu than loi (ha tang) -> KHONG fail-closed toan cong, giu hanh vi CU
    try:
        gate.save_arms([_mk_arm(20000.0)])
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1000})

        def _raise(*a, **kw):
            raise RuntimeError("BQ down")
        exdate_frame.classify_positions = _raise
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("loi ha tang: drawdown van tinh -15% (KHONG fail-closed vi loi phu tro)",
              abs(a0.get("last_drawdown", 0) - (-0.15)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("loi ha tang: KHONG co corp_action_multiplier", "corp_action_multiplier" not in a0)
    finally:
        _restore_corp_action_mocks()

    # ---- 18. MUTATION GUARD cho corp_action_frame_multiplier — moi assertion tren phai chet dung
    #          mutation cua no
    ORIG_FRAME_MULT = gate.corp_action_frame_multiplier

    def _oracle_A():
        gate.save_arms([_mk_arm(26000.0)])
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1260})
        exdate_frame.classify_positions = _classify_stub(
            {"VPB": {"residual": 260.0, "exercise_ratio": 0.30, "event_code": "ISS",
                     "ex_date": "2026-09-25"}}, {})
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        return (abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9
                and abs(a0.get("last_drawdown", 0) - (-0.05)) < 1e-6)

    def _oracle_C():
        gate.save_arms([_mk_arm(20000.0)])
        _patch_io(monkey_price=(15000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1500})
        exdate_frame.classify_positions = _classify_stub({}, {"VPB": "phan du CHUA GIAI THICH DUOC"})
        gate.cmd_check_exits(_argparse.Namespace())
        return "last_drawdown" not in (gate.load_arms() or [{}])[0]

    def _oracle_D():
        gate.save_arms([_mk_arm(20000.0)])
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        tb_brokers.DNSEBroker = _broker_factory({"VPB": 1000})
        exdate_frame.classify_positions = lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("BQ down"))
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        return abs(a0.get("last_drawdown", 999) - (-0.15)) < 1e-6

    def _mutate(name, patched, oracle_fn):
        try:
            gate.corp_action_frame_multiplier = patched
            killed = not oracle_fn()
            check(f"mutation {name}: mutant bi giet (assertion dao verdict)", killed)
        finally:
            gate.corp_action_frame_multiplier = ORIG_FRAME_MULT
            _restore_corp_action_mocks()

    # Mutant 1: bo qua quy doi khi co credited — luon tra factor=1.0. Kich ban A se KHONG quy
    # doi => multiplier khong dat 1.30, drawdown giu nguyen -26,9% (!= -5%) => assertion goc bat duoc.
    _mutate("baseline-not-converted",
            lambda ticker, account_label, account_id, asof: (1.0, None, None), _oracle_A)
    # Mutant 2: bo qua nhanh blocked — luon tra (1.0, None, None) du co blocked_reason that.
    # Kich ban C se TINH drawdown thay vi fail-closed => last_drawdown SE duoc set.
    _mutate("blocked-not-failclosed",
            lambda ticker, account_label, account_id, asof: (1.0, None, None), _oracle_C)
    # Mutant 3: fail-closed TOAN BO cong khi co loi ha tang (thay vi fail-open giu hanh vi cu).
    _mutate("infra-error-wrongly-fail-closed",
            lambda ticker, account_label, account_id, asof: (1.0, None, "gia lap fail-closed sai"),
            _oracle_D)

    gate._account_id_for = ORIG_ACCOUNT_ID_FOR

    print(f"\n{'='*70}\nPASS={len(PASS)} FAIL={len(FAIL)}")
    if FAIL:
        for name, detail in FAIL:
            print(f"  - {name}: {detail}")
        return 1
    print("Tat ca selfcheck PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
