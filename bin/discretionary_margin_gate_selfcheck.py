#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `discretionary_margin_gate.py` — 0 side-effect thật (không ghi bus/Discord thật,
không đụng `data/discretionary_margin_arms.json` production).

Theo skill verify-before-done: chạy dưới TZ lạ (env -u TZ) để bắt lỗi neo múi giờ tường minh (§16).
KHÔNG chạm Executor (sleeve này không wire vào bot) nên không cần MIKE_BOT_TEST_MODE (§5b).

Bước 13-16 (job Taylor_20260924_064510+_073500, Việc 2 — THIẾT KẾ LẠI sau arch-review
NEEDS_CHANGES bản đầu e75788f8) — cổng corp-action của `cmd_check_exits()`.
BUG GỐC ĐÃ SỬA: `drawdown = px / a["arm_price"] - 1.0` so `arm_price` (hệ giá TẠI THỜI ĐIỂM ARM)
với `px` hiện tại (đã tự nhiên đi qua mọi sự kiện tỉ lệ giữa lúc arm và bây giờ) mà KHÔNG quy
đổi — nhân chéo hai hệ quy chiếu, sinh cảnh báo de-lever GIẢ.

BUG BẢN VÁ ĐẦU (e75788f8, arch-review NEEDS_CHANGES): dùng `exdate_frame.classify_positions()`
— cơ chế đối chiếu THEO NGÀY, chỉ khớp khi cron chạy ĐÚNG cửa sổ credit (~19:07-19:10 ICT); cron
thật (`check-exits`) chạy 15:20 ICT ⇒ KHÔNG BAO GIỜ khớp (no-op cấu trúc). Cũng KHÔNG idempotent
(nhân dồn `corp_action_multiplier` mỗi lần gọi lại).

THIẾT KẾ LẠI: `corp_action_frame_multiplier(ticker, arm_date)` gọi thẳng
`daily_nav_snapshot.confirmed_qty_multiplier_after()` — đọc registry PERSISTENT
`data/corp_actions.json` (do `corp_action_auto_confirm.py` ghi 19:25 ICT, TRƯỚC cửa sổ credit
phiên mai), tích luỹ TẤT CẢ sự kiện CONFIRMED có `ex_date > arm_date` — không phụ thuộc thời
điểm gọi trong ngày, và tự động idempotent (đọc lại từ nguồn mỗi lần, không cộng dồn state).
Chỉ mock `current_price` + `daily_nav_snapshot.confirmed_qty_multiplier_after` (KHÔNG chạm
DNSE/BQ/corp_actions.json thật).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_margin_gate as gate  # noqa: E402
import daily_nav_snapshot  # noqa: E402

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


def _mult_after_stub(mult_by_ticker, calls_out=None):
    """Mock `daily_nav_snapshot.confirmed_qty_multiplier_after(ticker, asof_date)` — trả hệ số
    theo ticker (test wiring, KHÔNG test bản thân hàm gốc — hàm đó đã có test riêng trong
    `daily_nav_snapshot`). Nếu `calls_out` (list) được truyền, GHI LẠI (ticker, asof_date) mỗi
    lần gọi để test kiểm tra đúng arm_date THẬT được truyền vào (bắt mutation truyền nhầm ngày
    hôm nay thay vì ngày arm — trước đây stub bỏ qua hẳn `asof_date` nên không bắt được)."""
    def _f(ticker, asof_date):
        if calls_out is not None:
            calls_out.append((ticker, asof_date))
        return mult_by_ticker.get(ticker, 1.0)
    return _f


def _mult_after_stub_raising(bad_tickers, mult_by_ticker=None):
    """Mock ném exception cho ticker trong `bad_tickers` (giả lập registry `corp_actions.json`
    hỏng/lookup lỗi) — dùng để test R3: 1 arm lỗi registry KHÔNG được làm mất breach thật của
    arm KHÁC trong cùng vòng lặp (fail-silent)."""
    mult_by_ticker = mult_by_ticker or {}

    def _f(ticker, asof_date):
        if ticker in bad_tickers:
            raise RuntimeError("gia lap corp_actions.json hong: Expecting value: line 1 column 1")
        return mult_by_ticker.get(ticker, 1.0)
    return _f


def _mk_arm(arm_price, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00"):
    return {"ticker": ticker, "account": "SpaceX", "arm_price": arm_price, "shares": 1000,
            "exposure_vnd": arm_price * 1000, "f": 1.0, "exited": False, "exit_alerts": [],
            "armed_at": armed_at}


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

    # ════════════════════ CORP-ACTION GATE (cmd_check_exits) — Việc 2 (thiết kế lại) ═════════
    ORIG_MULT_AFTER = daily_nav_snapshot.confirmed_qty_multiplier_after

    def _restore_corp_action_mocks():
        daily_nav_snapshot.confirmed_qty_multiplier_after = ORIG_MULT_AFTER

    # ---- 13. co su kien CONFIRMED (registry) -> arm_price quy doi dung he, drawdown that (-5%),
    #          KHONG breach gia; + 13b idempotency (goi lai LAN 2 KHONG binh phuong multiplier)
    try:
        gate.save_arms([_mk_arm(26000.0)])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.30})
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

        n_adj_before = len(a0.get("corp_action_adjustments") or [])
        rc2 = gate.cmd_check_exits(_argparse.Namespace())
        a1 = (gate.load_arms() or [{}])[0]
        check("idempotent: goi lai LAN 2 (cung du lieu) multiplier VAN 1.30 (khong binh phuong 1.69)",
              abs(a1.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a1.get('corp_action_multiplier')}")
        check("idempotent: corp_action_adjustments KHONG them entry moi",
              len(a1.get("corp_action_adjustments") or []) == n_adj_before,
              f"before={n_adj_before} after={len(a1.get('corp_action_adjustments') or [])}")
        check("idempotent: drawdown lan 2 van dung -5% (khong lech do cong don)",
              abs(a1.get("last_drawdown", 0) - (-0.05)) < 1e-6, f"{a1.get('last_drawdown')}")
        check("idempotent: rc2=0", rc2 == 0, f"rc2={rc2}")
    finally:
        _restore_corp_action_mocks()

    # ---- 13c. R1+R2 (khong qua mutation-harness, di THANG qua code that): su kien MOI duoc
    #           CONFIRMED GIUA 2 lan goi (gia tri KHAC, khong lap lai) -> multiplier phai CAP
    #           NHAT dung gia tri MOI, KHONG nhan don voi gia tri CU (R1: bat mutation
    #           `a["corp_action_multiplier"] = prior_factor * factor`). Dong thoi bat arm_date
    #           THAT duoc truyen vao registry o CA 2 lan (R2: bat mutation truyen ngay HOM NAY
    #           thay vi ngay ARM that).
    try:
        gate.save_arms([_mk_arm(26000.0, armed_at="2026-09-01T09:00:00+07:00")])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        calls = []
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.30}, calls_out=calls)
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("13c buoc 1: multiplier = 1.30",
              abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a0.get('corp_action_multiplier')}")

        # su kien MOI duoc CONFIRMED giua 2 phien -> stub tra gia tri KHAC (1.43, khong phai lap
        # lai 1.30) - mo phong dung kich ban "1 su kien moi xuat hien" thay vi "goi lai y het".
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.43}, calls_out=calls)
        gate.cmd_check_exits(_argparse.Namespace())
        a1 = (gate.load_arms() or [{}])[0]
        check("13c buoc 2 (R1): multiplier CAP NHAT = 1.43 (KHONG phai 1.30*1.43=1.859 nhan don)",
              abs(a1.get("corp_action_multiplier", 0) - 1.43) < 1e-9, f"{a1.get('corp_action_multiplier')}")
        expected_drawdown = 19000.0 / (26000.0 / 1.43) - 1.0
        check("13c buoc 2: drawdown dung theo he quy doi MOI (1.43, khong phai 1.30 cu)",
              abs(a1.get("last_drawdown", 0) - expected_drawdown) < 1e-6, f"{a1.get('last_drawdown')}")

        check("13c (R2): arm_date THAT truyen vao registry o CA 2 lan goi = ngay ARM (2026-09-01), "
              "KHONG phai ngay hom nay/rong",
              len(calls) == 2 and all(c[1] == "2026-09-01" for c in calls), f"{calls}")
    finally:
        _restore_corp_action_mocks()

    # ---- 14. KHONG co su kien -> hanh vi CU giu nguyen (drawdown nhe, khong breach)
    try:
        gate.save_arms([_mk_arm(20000.0)])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({})
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
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("khong su kien, drawdown that -25%: gia tri dung",
              abs(a0.get("last_drawdown", 0) - (-0.25)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("khong su kien, drawdown that -25%: breach THAT van kich hoat",
              any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls), str(_NoBus.calls))
    finally:
        _restore_corp_action_mocks()

    # ---- 16. thieu armed_at (record cu/hong) -> fail-safe factor=1.0, KHONG doan, KHONG crash
    try:
        a_no_armed_at = _mk_arm(20000.0)
        a_no_armed_at.pop("armed_at", None)
        gate.save_arms([a_no_armed_at])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.30})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("thieu armed_at: fail-safe factor=1.0 (khong goi registry, khong doan)",
              "corp_action_multiplier" not in a0, f"{a0}")
        check("thieu armed_at: drawdown dung cong thuc cu -15%",
              abs(a0.get("last_drawdown", 0) - (-0.15)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("thieu armed_at: rc=0", rc == 0, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()

    # ---- 17. MUTATION GUARD cho corp_action_frame_multiplier — moi assertion tren phai chet dung
    #          mutation cua no
    ORIG_FRAME_MULT = gate.corp_action_frame_multiplier

    def _oracle_A():
        gate.save_arms([_mk_arm(26000.0)])
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        return (abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9
                and abs(a0.get("last_drawdown", 0) - (-0.05)) < 1e-6)

    def _oracle_idempotent():
        gate.save_arms([_mk_arm(26000.0)])
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        gate.cmd_check_exits(_argparse.Namespace())
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        return abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9

    def _mutate(name, patched, oracle_fn):
        try:
            gate.corp_action_frame_multiplier = patched
            killed = not oracle_fn()
            check(f"mutation {name}: mutant bi giet (assertion dao verdict)", killed)
        finally:
            gate.corp_action_frame_multiplier = ORIG_FRAME_MULT

    # Mutant 1: bo qua quy doi hoan toan — luon tra factor=1.0. Kich ban A se KHONG quy doi =>
    # multiplier khong dat 1.30, drawdown giu nguyen -26,9% (!= -5%) => assertion goc bat duoc.
    _mutate("factor-not-applied", lambda ticker, arm_date: 1.0, _oracle_A)

    # Mutant 2: gia lap bug CU (nhan don moi lan goi thay vi doc lai TU NGUON) — moi lan goi
    # binh phuong luy thua thay vi tra CO DINH 1.30 => oracle idempotency phai bat duoc lech.
    _acc_state = {"n": 0}

    def _accumulating_mult(ticker, arm_date):
        _acc_state["n"] += 1
        return 1.30 ** _acc_state["n"]
    _mutate("idempotency-missing-simulated", _accumulating_mult, _oracle_idempotent)

    # ---- 18. R3 (§29 fail-silent): registry loi (vd corp_actions.json hong JSON) o MOT arm
    #          KHONG duoc lam crash vong lap / mat breach THAT cua arm KHAC.
    try:
        gate.save_arms([
            _mk_arm(20000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00"),
            _mk_arm(20000.0, ticker="TV1", armed_at="2026-09-01T09:00:00+07:00"),
        ])
        _NoBus.calls.clear()
        _prices = {
            "VPB": (17000.0, "dnse_g1_fake", None),   # -15%: fail-open factor=1.0 -> khong breach
            "TV1": (15000.0, "dnse_g1_fake", None),   # -25%: breach THAT, khong lien quan VPB
        }
        gate.current_price = lambda ticker: _prices[ticker]
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub_raising({"VPB"})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        arms_after = {a["ticker"]: a for a in gate.load_arms()}
        check("R3: registry loi o VPB KHONG lam crash vong lap (TV1 van duoc xu ly)",
              "TV1" in arms_after and arms_after["TV1"].get("last_checked"), f"{arms_after}")
        check("R3: breach THAT cua TV1 (-25%) VAN duoc gui bus du VPB registry loi",
              any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls), str(_NoBus.calls))
        check("R3: VPB fail-open factor=1.0 (drawdown -15% KHONG quy doi, KHONG crash)",
              abs(arms_after.get("VPB", {}).get("last_drawdown", 0) - (-0.15)) < 1e-6,
              f"{arms_after.get('VPB', {}).get('last_drawdown')}")
        check("R3: VPB fail-open KHONG ghi corp_action_multiplier gia (factor=1.0 == default)",
              "corp_action_multiplier" not in arms_after.get("VPB", {}), f"{arms_after.get('VPB')}")
        check("R3: rc=1 (co errors) de nguoi truc biet co van de can kiem",
              rc == 1, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()
        _patch_io(monkey_price=(0.0, "reset", None))

    print(f"\n{'='*70}\nPASS={len(PASS)} FAIL={len(FAIL)}")
    if FAIL:
        for name, detail in FAIL:
            print(f"  - {name}: {detail}")
        return 1
    print("Tat ca selfcheck PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
