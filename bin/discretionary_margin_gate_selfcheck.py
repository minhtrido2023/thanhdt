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
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_margin_gate as gate  # noqa: E402
import daily_nav_snapshot  # noqa: E402

# Bẫy 2026-09-24 (vòng 6 blocker 1 debug): `gate.py` từng chèn `MIKE_ROOT/bin` CANONICAL vào
# sys.path phía TRƯỚC thư mục của chính nó, khiến `import daily_nav_snapshot` (và mọi sibling
# module) nạp bản ĐÃ LANDED thay vì bản đang sửa dở trong worktree — test 22a-22d "hàm thật"
# từng PASS giả vì thực ra chạy code cũ. Chốt cứng: module vừa import PHẢI nằm CÙNG thư mục
# với chính file selfcheck này (không phải canonical mike/bin nếu đang chạy từ worktree khác).
_HERE = os.path.dirname(os.path.abspath(__file__))
assert os.path.dirname(os.path.abspath(daily_nav_snapshot.__file__)) == _HERE, (
    f"daily_nav_snapshot nạp từ {daily_nav_snapshot.__file__}, KHÔNG phải {_HERE} — "
    f"sys.path đang shadow bản worktree bằng bản canonical, xem gate.py MIKE_ROOT comment")

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
        _NoBus.calls.append(("bus", kind, topic, payload))
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

    # ---- 16. [vong 6, blocker 2] thieu armed_at (record cu/hong) -> nhanh UNVERIFIED (KHONG
    #          phai success voi factor=1.0 ngu y da doc registry) - fail-safe factor=1.0 (mac
    #          dinh khi thieu key), KHONG goi registry (stub KHONG duoc goi), rc=1 (co errors).
    try:
        a_no_armed_at = _mk_arm(20000.0)
        a_no_armed_at.pop("armed_at", None)
        gate.save_arms([a_no_armed_at])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        calls = []
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.30}, calls_out=calls)
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("thieu armed_at: fail-safe factor=1.0 (khong goi registry, khong doan)",
              "corp_action_multiplier" not in a0, f"{a0}")
        check("thieu armed_at: KHONG goi corp_action_frame_multiplier/registry",
              len(calls) == 0, f"{calls}")
        check("thieu armed_at: drawdown dung cong thuc cu -15%",
              abs(a0.get("last_drawdown", 0) - (-0.15)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("thieu armed_at (vong 6): rc=1 (UNVERIFIED, KHONG phai success gia)",
              rc == 1, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()

    # ---- 16b. [vong 6, blocker 2] armed_at = chuoi khong hop le ("unknown-date") -> cung nhanh
    #           UNVERIFIED nhu rong, KHONG bi cat [:10] roi so chuoi tho lam sai lech ngay.
    try:
        a_bad = _mk_arm(20000.0, armed_at="unknown-date")
        gate.save_arms([a_bad])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(17000.0, "dnse_g1_fake", None))
        calls = []
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.30}, calls_out=calls)
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("16b armed_at='unknown-date': fail-safe factor=1.0, KHONG doan",
              "corp_action_multiplier" not in a0, f"{a0}")
        check("16b: KHONG goi registry", len(calls) == 0, f"{calls}")
        check("16b: rc=1 (UNVERIFIED)", rc == 1, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()

    # ---- 17. [GO 2026-09-24, vong 4, arch-review R4] MUTATION GUARD cu cho
    #          corp_action_frame_multiplier bi VO HIEU: _restore_corp_action_mocks() da thao stub
    #          truoc khi chay toi day, nen "khong mutation" (ORIG_FRAME_MULT) cung goi thang
    #          daily_nav_snapshot.confirmed_qty_multiplier_after THAT (doc corp_actions.json that
    #          tren may, khong phai stub 1.30) => oracle_fn() LUON False bat ke co mutation hay
    #          khong => "mutant bi giet" la HU CAU (vacuous anchor, cung lop voi
    #          report_return_gate.py:723/727/737). Khong dung lai bang cach them
    #          `assert oracle_fn() is True` truoc _mutate: gia tri do phu thuoc corp_actions.json
    #          THAT tren may chay selfcheck (khong on dinh giua cac moi truong/CI). Cac invariant
    #          ma Section 17 dinh bat (quy doi dung, idempotent khong nhan don) da duoc phu bang
    #          KICH BAN THAT (khong can gia lap ham) o test 13/13b/13c ben tren — xoa Section 17
    #          thay vi dung lai, tranh nuoi mot test hu cau song song voi test that.

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
        try:
            rc = gate.cmd_check_exits(_argparse.Namespace())
        except Exception as exc:
            # R5: neu mutation go try/except quanh corp_action_frame_multiplier() lam loi
            # registry CRASH thang ra ngoai, bat lai o day de chet bang assertion CO TEN thay vi
            # traceback lam sap ca selfcheck (dung quy uoc R3/13-18 hom nay).
            check("R3: cmd_check_exits KHONG duoc de loi registry lam crash ra ngoai "
                  "(try/except quanh corp_action_frame_multiplier bi thao?)", False,
                  f"{type(exc).__name__}: {exc}")
            rc = None
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

    # ---- 18b. [vong 4, arch-review R1+R2] registry loi NHUNG arm DA CO corp_action_multiplier=
    #           1.30 tu lan doc THANH CONG truoc do -> gia tri do PHAI duoc GIU NGUYEN (khong bi
    #           de ve 1.0), KHONG sinh them corp_action_adjustments, va tin notify KHONG duoc
    #           ngu y da doc duoc registry luot nay (khong in "x1.000000"). Day chinh la ca that
    #           arch-reviewer do duoc: arm factor dung 1.30, drawdown that -5%, nhung ban va vong
    #           3 in "he so x1.000000" trong tin breach khi registry loi.
    try:
        arm = _mk_arm(26000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00")
        arm["corp_action_multiplier"] = 1.30
        arm["corp_action_adjustments"] = [
            {"at": "2026-09-10T09:00:00+07:00", "factor_before": 1.0, "factor_after": 1.30,
             "note": "seed: da doc thanh cong lan truoc"}]
        gate.save_arms([arm])
        _NoBus.calls.clear()
        n_adj_before = len(arm["corp_action_adjustments"])
        # arm_price_frame = 26000/1.30 = 20000; px=15000 -> drawdown = -25% (breach, de test noi
        # dung tin notify khi breach xay ra dung luc registry loi).
        _patch_io(monkey_price=(15000.0, "dnse_g1_fake", None))
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub_raising({"VPB"})
        try:
            rc = gate.cmd_check_exits(_argparse.Namespace())
        except Exception as exc:
            check("18b: cmd_check_exits KHONG duoc crash khi registry loi + da co multiplier cu",
                  False, f"{type(exc).__name__}: {exc}")
            rc = None
        a0 = (gate.load_arms() or [{}])[0]
        check("18b (R1a): registry loi NHUNG multiplier CU (1.30) duoc GIU NGUYEN, khong bi de ve 1.0",
              abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a0.get('corp_action_multiplier')}")
        check("18b (R1b): KHONG sinh them corp_action_adjustments moi khi registry loi",
              len(a0.get("corp_action_adjustments") or []) == n_adj_before,
              f"before={n_adj_before} after={len(a0.get('corp_action_adjustments') or [])}")
        check("18b (R1c): drawdown van tinh theo he so CU da biet (20.000 frame => -25%, khong "
              "bi reset ve khong quy doi / -42,3%)",
              abs(a0.get("last_drawdown", 0) - (-0.25)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("18b: rc=1 (co errors)", rc == 1, f"rc={rc}")

        notify_msgs = [c[1] for c in _NoBus.calls if c[0] == "notify"]
        check("18b: co it nhat 1 tin notify duoc gui khi breach xay ra du registry loi",
              len(notify_msgs) >= 1, str(_NoBus.calls))
        joined = " ".join(notify_msgs)
        check("18b (R1d): tin notify KHONG chua 'x1.000000' (khong ngu y da doc duoc registry)",
              "×1.000000" not in joined and "x1.000000" not in joined, joined)
        check("18b (R1e): tin notify CO dau hieu 'khong xac dinh duoc' cho nguoi doc biet ro "
              "day la canh bao chua xac nhan, khong phai da quy doi that",
              "không xác định được" in joined.lower(), joined)
    finally:
        _restore_corp_action_mocks()
        _patch_io(monkey_price=(0.0, "reset", None))

    # ---- 18c. [vong 4, arch-review R3] he so GIAM (su kien bi REVOKE / row bi xoa khoi registry)
    #           -> corp_action_multiplier PHAI CAP NHAT xuong gia tri moi, khong chi cap nhat khi
    #           TANG. arch-reviewer ban mutation `factor != prior_factor` -> `factor > prior_factor`
    #           (dong ~402) va no SONG vi chua co test cho chieu giam — mutation nay PHAI chet
    #           sau khi them ca duoi day (factor > prior_factor se False khi factor=1.0 <
    #           prior_factor=1.30 => khong cap nhat => assertion 18c-a bat duoc ngay).
    try:
        gate.save_arms([_mk_arm(26000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00")])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.30})
        gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("18c-setup: multiplier ban dau = 1.30",
              abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a0.get('corp_action_multiplier')}")

        # su kien bi REVOKE giua 2 lan goi -> registry (da doc THANH CONG, khong loi) tra ve 1.0
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({"VPB": 1.0})
        gate.cmd_check_exits(_argparse.Namespace())
        a1 = (gate.load_arms() or [{}])[0]
        check("18c-a (R3): he so GIAM tu 1.30 xuong 1.0 PHAI duoc cap nhat (bat mutation "
              "'factor != prior_factor' -> 'factor > prior_factor')",
              abs(a1.get("corp_action_multiplier", 0) - 1.0) < 1e-9, f"{a1.get('corp_action_multiplier')}")
        expected_dd = round(19000.0 / (26000.0 / 1.0) - 1.0, 4)   # last_drawdown duoc round(4)
        check("18c-b: drawdown tinh lai dung theo he so MOI (1.0) sau khi giam, khong con dung "
              "frame 1.30 cu", abs(a1.get("last_drawdown", 0) - expected_dd) < 1e-6,
              f"{a1.get('last_drawdown')} vs expected {expected_dd}")
        n_adj_after_decrease = len(a1.get("corp_action_adjustments") or [])
        check("18c-c: co ghi corp_action_adjustments cho lan giam (khong bi coi la 'khong doi')",
              n_adj_after_decrease >= 1, f"{n_adj_after_decrease}")
    finally:
        _restore_corp_action_mocks()

    # ════════════════ Vòng 5 — R1/R2/R3: HÀM THẬT (không stub), cửa "file vắng" ═══════════════
    # Bug vòng 3+4: `confirmed_qty_multiplier_after()` trả 1.0 IM LẶNG khi CORP_ACTIONS_FILE
    # KHÔNG TỒN TẠI (khác lớp lỗi "JSON hỏng" đã vá vòng 4) — mọi test 13-18c ở trên đều STUB
    # `daily_nav_snapshot.confirmed_qty_multiplier_after`, KHÔNG một ca nào chạm
    # `corp_action_frame_multiplier()` THẬT lẫn `confirmed_qty_multiplier_after()` THẬT cùng lúc,
    # nên hợp đồng "ném exception khi registry vắng" chưa từng được kiểm. R2 bắt buộc: dùng HÀM
    # THẬT, trỏ CORP_ACTIONS_FILE vào tmpdir tự tạo.
    ORIG_CORP_ACTIONS_FILE = daily_nav_snapshot.CORP_ACTIONS_FILE

    def _restore_corp_actions_file():
        daily_nav_snapshot.CORP_ACTIONS_FILE = ORIG_CORP_ACTIONS_FILE

    # ---- 19. R2a [HÀM THẬT]: CORP_ACTIONS_FILE trỏ tmpdir, file KHÔNG TỒN TẠI, arm ĐÃ có
    #          corp_action_multiplier=1.30 từ lần đọc thành công trước đó -> phải đi đúng nhánh
    #          except (giữ nguyên 1.30, KHÔNG entry adjustments mới, notify "không xác định
    #          được" và KHÔNG "×1.000000", rc=1). Bắt mutation bỏ nhánh exists()-check mới thêm
    #          ở corp_action_frame_multiplier() (không check -> confirmed_qty_multiplier_after
    #          THẬT trả 1.0 im lặng -> multiplier bị đè về 1.0, đúng bug vòng 3 tái hiện).
    try:
        daily_nav_snapshot.CORP_ACTIONS_FILE = os.path.join(tmpdir, "corp_actions_R2a_absent.json")
        check("R2a-setup: file registry THẬT SỰ không tồn tại (tiền đề của ca này)",
              not os.path.exists(daily_nav_snapshot.CORP_ACTIONS_FILE))
        arm = _mk_arm(26000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00")
        arm["corp_action_multiplier"] = 1.30
        arm["corp_action_adjustments"] = [
            {"at": "2026-09-10T09:00:00+07:00", "factor_before": 1.0, "factor_after": 1.30,
             "note": "seed: da doc thanh cong lan truoc"}]
        gate.save_arms([arm])
        _NoBus.calls.clear()
        n_adj_before = len(arm["corp_action_adjustments"])
        # arm_price_frame = 26000/1.30 = 20000; px=15000 -> drawdown = -25% (breach)
        _patch_io(monkey_price=(15000.0, "dnse_g1_fake", None))
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("R2a: CORP_ACTIONS_FILE vắng -> corp_action_frame_multiplier() THẬT phải NÉM lỗi "
              "(không trả 1.0 im lặng) -> multiplier CŨ (1.30) được GIỮ NGUYÊN, không bị đè về 1.0",
              abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a0.get('corp_action_multiplier')}")
        check("R2a: KHÔNG sinh thêm corp_action_adjustments khi registry vắng",
              len(a0.get("corp_action_adjustments") or []) == n_adj_before,
              f"before={n_adj_before} after={len(a0.get('corp_action_adjustments') or [])}")
        check("R2a: drawdown vẫn tính theo hệ số CŨ đã biết (frame 20.000 => -25%, không reset "
              "về không quy đổi)", abs(a0.get("last_drawdown", 0) - (-0.25)) < 1e-6,
              f"{a0.get('last_drawdown')}")
        check("R2a: rc=1 (có errors)", rc == 1, f"rc={rc}")
        notify_msgs = [c[1] for c in _NoBus.calls if c[0] == "notify"]
        joined = " ".join(notify_msgs)
        check("R2a: notify CÓ ít nhất 1 tin khi breach", len(notify_msgs) >= 1, str(_NoBus.calls))
        check("R2a: notify KHÔNG chứa 'x1.000000' (không ngụ ý đã đọc được registry vắng)",
              "×1.000000" not in joined and "x1.000000" not in joined, joined)
        check("R2a: notify CÓ dấu hiệu 'không xác định được'",
              "không xác định được" in joined.lower(), joined)
        bus_payloads = [c[3] for c in _NoBus.calls if c[0] == "bus" and c[1] == "error"]
        check("R2a (R4): bus payload đánh dấu frame_unverified=True khi registry vắng",
              bus_payloads and bus_payloads[0].get("frame_unverified") is True, str(bus_payloads))
    finally:
        _restore_corp_actions_file()
        _patch_io(monkey_price=(0.0, "reset", None))

    # ---- 20. R2b [HÀM THẬT]: CORP_ACTIONS_FILE trỏ tmpdir, file CÓ 1 sự kiện CONFIRMED hợp lệ
    #          -> hàm thật vẫn quy đổi ĐÚNG khi có dữ liệu tốt (chứng minh exists()-check mới
    #          không chặn nhầm đường THÀNH CÔNG, chỉ chặn đường FILE VẮNG).
    try:
        corp_file = os.path.join(tmpdir, "corp_actions_R2b_present.json")
        with open(corp_file, "w", encoding="utf-8") as f:
            json.dump({"actions": [
                {"ticker": "VPB", "_status": "CONFIRMED", "ex_date": "2026-09-15",
                 "qty_multiplier": 1.30, "event_type": "BONUS_ISSUE",
                 "broker_effective_ts": "2026-09-14T19:00:00+07:00"},
            ]}, f)
        daily_nav_snapshot.CORP_ACTIONS_FILE = corp_file
        gate.save_arms([_mk_arm(26000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00")])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(19000.0, "dnse_g1_fake", None))
        rc = gate.cmd_check_exits(_argparse.Namespace())
        a0 = (gate.load_arms() or [{}])[0]
        check("R2b: HÀM THẬT (không stub) đọc registry CÓ file -> multiplier tích luỹ = 1.30",
              abs(a0.get("corp_action_multiplier", 0) - 1.30) < 1e-9, f"{a0.get('corp_action_multiplier')}")
        check("R2b: HÀM THẬT -> drawdown quy đổi đúng -5% (20.000 frame), không breach",
              abs(a0.get("last_drawdown", 0) - (-0.05)) < 1e-6, f"{a0.get('last_drawdown')}")
        check("R2b: HÀM THẬT -> KHÔNG breach, rc=0",
              rc == 0 and not any(c[0] == "bus" and c[1] == "error" for c in _NoBus.calls),
              f"rc={rc} {_NoBus.calls}")
    finally:
        _restore_corp_actions_file()
        _patch_io(monkey_price=(0.0, "reset", None))

    # ---- 21. R3: factor_lookup_failed PHẢI khởi tạo 1 LẦN TRƯỚC vòng lặp, không phải bên trong.
    #          2 arm CÙNG breach, arm LỖI đứng TRƯỚC arm LÀNH (đảo thứ tự so với test 18, nơi arm
    #          lỗi VPB đứng trước nhưng KHÔNG breach nên không bắt được mutation). Mutation
    #          "factor_lookup_failed = {} khởi tạo TRONG vòng lặp" sẽ reset dict khi xử lý TV1
    #          (lành, sau VPB) -> mất entry lỗi của VPB -> tin breach VPB SAI thành "đã quy đổi
    #          ×1.000000" thay vì "không xác định được" (đúng bug vòng 3 tái hiện qua thứ tự).
    try:
        gate.save_arms([
            _mk_arm(20000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00"),  # LỖI, đứng TRƯỚC
            _mk_arm(20000.0, ticker="TV1", armed_at="2026-09-01T09:00:00+07:00"),  # LÀNH, đứng SAU
        ])
        _NoBus.calls.clear()
        _prices = {
            "VPB": (15000.0, "dnse_g1_fake", None),   # -25%: breach, nhưng registry lỗi
            "TV1": (15000.0, "dnse_g1_fake", None),   # -25%: breach, registry lành (mult=1.0)
        }
        gate.current_price = lambda ticker: _prices[ticker]
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub_raising({"VPB"})
        try:
            rc = gate.cmd_check_exits(_argparse.Namespace())
        except Exception as exc:
            check("R3-21: cmd_check_exits KHÔNG được crash (thứ tự arm lỗi-trước-lành)",
                  False, f"{type(exc).__name__}: {exc}")
            rc = None
        bus_errors = {c[2].rsplit("-", 1)[-1]: c[3] for c in _NoBus.calls
                      if c[0] == "bus" and c[1] == "error"}
        check("R3-21: CẢ HAI arm (VPB lỗi + TV1 lành) đều được báo breach qua bus",
              set(bus_errors) == {"VPB", "TV1"}, str(bus_errors))
        vpb_payload = bus_errors.get("VPB", {})
        tv1_payload = bus_errors.get("TV1", {})
        check("R3-21: arm LỖI (VPB, đứng TRƯỚC) VẪN giữ frame_unverified=True dù xử lý sau đó "
              "có arm lành khác (bắt mutation factor_lookup_failed khởi tạo trong vòng lặp)",
              vpb_payload.get("frame_unverified") is True, str(vpb_payload))
        check("R3-21: arm LÀNH (TV1, đứng SAU) frame_unverified=False (không bị lây lỗi của VPB)",
              tv1_payload.get("frame_unverified") is False, str(tv1_payload))
        notify_msgs = [c[1] for c in _NoBus.calls if c[0] == "notify"]
        vpb_msgs = [m for m in notify_msgs if "VPB" in m]
        check("R3-21: tin notify của VPB CÓ 'không xác định được', KHÔNG có '×1.000000' giả",
              bool(vpb_msgs) and all("không xác định được" in m.lower() for m in vpb_msgs)
              and all("×1.000000" not in m and "x1.000000" not in m for m in vpb_msgs),
              str(vpb_msgs))
        check("R3-21: rc=1 (có errors)", rc == 1, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()
        _patch_io(monkey_price=(0.0, "reset", None))

    # ---- 21b. [§29 vòng 6 blocker 3] 2 arm CÙNG ticker (re-arm ở giá khác) cùng breach — bản
    #           cũ tra lại theo `by_ticker = {a["ticker"]: a for a in live}` (dict, key=ticker)
    #           COLLAPSE 2 arm thành 1 entry ⇒ alert của arm A in nhầm arm_price/frame của arm
    #           B. Đo thật: 2 arm VPB (26.000 và 39.000) cùng breach, alert của arm dd -25% (arm
    #           26.000) lại in "arm_price 39.000" (thuộc arm kia). Sửa: mang thẳng OBJECT `a`
    #           trong breaches, KHÔNG tra lại qua ticker string.
    try:
        arm_a = _mk_arm(26000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00")  # dd -25%
        arm_b = _mk_arm(39000.0, ticker="VPB", armed_at="2026-09-05T09:00:00+07:00")  # dd -50%
        gate.save_arms([arm_a, arm_b])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(19500.0, "dnse_g1_fake", None))
        daily_nav_snapshot.confirmed_qty_multiplier_after = _mult_after_stub({})
        rc = gate.cmd_check_exits(_argparse.Namespace())
        breach_payloads = [c[3] for c in _NoBus.calls if c[0] == "bus" and c[1] == "error"]
        check("21b: CẢ HAI arm VPB (2 giá arm khác nhau) đều báo breach riêng (không bị collapse)",
              len(breach_payloads) == 2, str(breach_payloads))
        dds = sorted(round(p["drawdown"], 4) for p in breach_payloads)
        # arm 26.000: 19500/26000-1=-25%; arm 39.000: 19500/39000-1=-50%
        check("21b: drawdown của TỪNG arm đúng theo arm_price CỦA CHÍNH NÓ (không lẫn giữa 2 arm)",
              dds == [-0.5, -0.25], f"dds={dds}")
        notify_msgs = [c[1] for c in _NoBus.calls if c[0] == "notify"]
        msg_25 = [m for m in notify_msgs if "-25.0%" in m or "-25,0%" in m]
        msg_50 = [m for m in notify_msgs if "-50.0%" in m or "-50,0%" in m]
        check("21b: tin −25% CÓ nhắc arm_price 26.000, KHÔNG lẫn arm_price 39.000",
              bool(msg_25) and all("26,000" in m and "39,000" not in m for m in msg_25),
              str(msg_25))
        check("21b: tin −50% CÓ nhắc arm_price 39.000, KHÔNG lẫn arm_price 26.000",
              bool(msg_50) and all("39,000" in m and "26,000" not in m for m in msg_50),
              str(msg_50))
        check("21b: rc=0 (không lỗi registry, chỉ mock ticker khác)", rc == 0, f"rc={rc}")
    finally:
        _restore_corp_action_mocks()
        _patch_io(monkey_price=(0.0, "reset", None))

    # ---- 21c. [B1 vòng 7] factor_lookup_failed key theo id(a), KHÔNG theo ticker string — 2
    #           arm CÙNG TICKER (VPB), một arm registry LỖI, một arm registry LÀNH. Bản sai
    #           (`factor_lookup_failed[a["ticker"]] = ...`) sẽ COLLAPSE 2 arm thành 1 key "VPB":
    #           arm lành xử lý SAU sẽ bị lây `frame_unverified=True`/lý do lỗi của arm lỗi
    #           (hoặc ngược lại, tuỳ thứ tự) — mất khả năng phân biệt "quy đổi tin được" khỏi
    #           "không xác định được" ngay trên CHÍNH 1 mã. Phân biệt 2 arm cùng ticker bằng
    #           `armed_at` KHÁC nhau (arm_date khác nhau) — stub raise theo asof_date, không
    #           theo ticker, vì ticker trùng nhau ở cả 2 arm nên không thể dùng để phân biệt.
    try:
        arm_bad = _mk_arm(20000.0, ticker="VPB", armed_at="2026-09-01T09:00:00+07:00")
        arm_good = _mk_arm(20000.0, ticker="VPB", armed_at="2026-09-05T09:00:00+07:00")
        gate.save_arms([arm_bad, arm_good])
        _NoBus.calls.clear()
        _patch_io(monkey_price=(15000.0, "dnse_g1_fake", None))   # -25%: breach cho cả hai

        def _raise_by_arm_date(ticker, asof_date):
            if asof_date == "2026-09-01":
                raise RuntimeError("gia lap corp_actions.json hong cho arm_date 2026-09-01")
            return 1.0

        daily_nav_snapshot.confirmed_qty_multiplier_after = _raise_by_arm_date
        rc = gate.cmd_check_exits(_argparse.Namespace())
        breach_payloads = [c[3] for c in _NoBus.calls if c[0] == "bus" and c[1] == "error"]
        check("21c: cả 2 arm VPB (cùng ticker, khác armed_at) đều được báo breach",
              len(breach_payloads) == 2, str(breach_payloads))
        by_frame = sorted(p.get("frame_unverified") for p in breach_payloads)
        check("21c: ĐÚNG 1 arm frame_unverified=True (lỗi) và 1 arm frame_unverified=False "
              "(lành) — KHÔNG bị lây chéo do key trùng ticker (bắt mutation keying theo ticker)",
              by_frame == [False, True], str(breach_payloads))
    finally:
        _restore_corp_action_mocks()
        _patch_io(monkey_price=(0.0, "reset", None))

    # ══════ Vòng 6 blocker 1 — daily_nav_snapshot.confirmed_qty_multiplier_after() HÀM THẬT,
    # KHÔNG stub: record hỏng trong corp_actions.json phải NÉM CorpActionError, không nuốt im
    # lặng. Test THẲNG hàm này (không qua discretionary_margin_gate) để cô lập blocker 1 khỏi
    # blocker 2/3 (arm_date/by_ticker) — 2 lớp lỗi độc lập, không nên chung 1 assertion.
    import corp_actions as _corp_actions

    def _write_registry(actions):
        path = os.path.join(tmpdir, f"corp_actions_v6_{len(actions)}_{id(actions)}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"actions": actions}, f)
        return path

    _valid_vpb = {"ticker": "VPB", "event_type": "BONUS_ISSUE", "qty_multiplier": 1.30,
                  "ex_date": "2026-09-15", "broker_effective_ts": "2026-09-14T19:00:00+07:00",
                  "_status": "CONFIRMED — test"}

    # ---- 22a. qty_multiplier kiểu số Việt "1,30" (JSON hợp lệ, số SAI định dạng) -> phải NÉM
    #           CorpActionError, KHÔNG được nuốt rồi trả 1.0/coi như không có sự kiện.
    try:
        bad = dict(_valid_vpb)
        bad["qty_multiplier"] = "1,30"
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([bad])
        try:
            daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-01")
            check("22a: qty_multiplier='1,30' (số kiểu Việt) PHẢI ném CorpActionError", False,
                  "không ném lỗi nào — record hỏng bị nuốt im lặng")
        except _corp_actions.CorpActionError:
            check("22a: qty_multiplier='1,30' (số kiểu Việt) PHẢI ném CorpActionError", True)
    finally:
        _restore_corp_actions_file()

    # ---- 22b. ex_date null/thiếu -> phải NÉM CorpActionError.
    try:
        bad = dict(_valid_vpb)
        bad["ex_date"] = None
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([bad])
        try:
            daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-01")
            check("22b: ex_date=None PHẢI ném CorpActionError", False,
                  "không ném lỗi nào — record hỏng bị nuốt im lặng")
        except _corp_actions.CorpActionError:
            check("22b: ex_date=None PHẢI ném CorpActionError", True)
    finally:
        _restore_corp_actions_file()

    # ---- 22c. 2 record, 1 hỏng (ticker KHÁC) -> KHÔNG được âm thầm trả tích số của phần còn
    #           lại (load_all() validate TOÀN BỘ file, chủ đích — xem docstring
    #           confirmed_qty_multiplier_after). Hỏi về VPB (record LÀNH) vẫn phải ném lỗi vì
    #           record TV1 (KHÔNG liên quan) hỏng.
    try:
        bad_other = dict(_valid_vpb)
        bad_other.update(ticker="TV1", qty_multiplier="1,10")
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([dict(_valid_vpb), bad_other])
        try:
            mult = daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-01")
            check("22c: 1 record TV1 hỏng KHÔNG được để lọt qua tích số của VPB (phải ném lỗi)",
                  False, f"trả về mult={mult} thay vì ném lỗi")
        except _corp_actions.CorpActionError:
            check("22c: 1 record TV1 hỏng KHÔNG được để lọt qua tích số của VPB (phải ném lỗi)",
                  True)
    finally:
        _restore_corp_actions_file()

    # ---- 22d. [QUAN TRỌNG NHẤT] ex_date="2026-9-05" (không zero-pad) với asof_date="2026-10-01"
    #           -> bản CŨ so CHUỖI THÔ: "2026-9-05" > "2026-10-01" = True (so ký tự, ký tự '9' >
    #           '1') -> sự kiện NẰM TRƯỚC ngày arm/asof vẫn bị coi là "SAU" -> ÁP NHẦM, che một
    #           breach thật (ca đã đo: drawdown thật -21,15% bị báo +2,5%). Bản MỚI: ex_date
    #           không zero-pad bị `dt.date.fromisoformat` từ chối ngay ở validate() -> PHẢI ném
    #           CorpActionError (KHÔNG được lặng lẽ áp dụng multiplier).
    try:
        bad = dict(_valid_vpb)
        bad["ex_date"] = "2026-9-05"
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([bad])
        try:
            mult = daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-10-01")
            check("22d [missed-breach]: ex_date='2026-9-05' KHÔNG zero-pad, asof='2026-10-01' — "
                  "PHẢI ném lỗi, KHÔNG được so chuỗi thô rồi áp nhầm multiplier (che breach thật)",
                  False, f"trả về mult={mult} thay vì ném lỗi — so chuỗi thô đã tái hiện")
        except _corp_actions.CorpActionError:
            check("22d [missed-breach]: ex_date='2026-9-05' KHÔNG zero-pad, asof='2026-10-01' — "
                  "PHẢI ném lỗi, KHÔNG được so chuỗi thô rồi áp nhầm multiplier (che breach thật)",
                  True)
    finally:
        _restore_corp_actions_file()

    # ---- 22e. đối chứng KHÔNG-ĐƯỢC-CHẾT: registry LÀNH hoàn toàn vẫn quy đổi ĐÚNG (chứng minh
    #           validate() không chặn nhầm đường thành công).
    try:
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([dict(_valid_vpb)])
        mult = daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-01")
        check("22e: registry LÀNH -> mult=1.30 đúng (ex_date 2026-09-15 > asof 2026-09-01)",
              abs(mult - 1.30) < 1e-9, f"mult={mult}")
        mult2 = daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-20")
        check("22e: registry LÀNH, asof SAU ex_date -> mult=1.0 (sự kiện đã qua)",
              abs(mult2 - 1.0) < 1e-9, f"mult={mult2}")
    finally:
        _restore_corp_actions_file()

    # ---- 22f. [B2 vòng 7] cổng `_status` CONFIRMED — mutation `load_corp_actions(...) ->
    #           load_all(...)` (bỏ lọc `_status`) hiện SỐNG qua toàn bộ 93 test cũ vì chưa có
    #           test nào đặt record KHÔNG-CONFIRMED cạnh 1 record CONFIRMED cùng ticker. Registry
    #           có 1 record PROPOSED (chưa ký) + 1 record REVOKED (đã thu hồi) — CẢ HAI đều
    #           KHÔNG được tính vào tích số dù ex_date hợp lệ và SAU asof_date.
    try:
        proposed = dict(_valid_vpb)
        proposed.update(qty_multiplier=1.50, ex_date="2026-09-16", _status="PROPOSED — chưa ký")
        revoked = dict(_valid_vpb)
        revoked.update(qty_multiplier=1.20, ex_date="2026-09-17",
                       _status="REVOKED — thu hồi ngày 2026-09-18")
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([proposed, revoked])
        mult = daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-01")
        check("22f [B2]: record PROPOSED + REVOKED (ex_date hợp lệ, SAU asof) -> mult=1.0 "
              "(cổng _status CONFIRMED phải lọc CẢ HAI, không tính vào tích số — bắt mutation "
              "load_corp_actions -> load_all bỏ lọc _status)",
              abs(mult - 1.0) < 1e-9, f"mult={mult}")
    finally:
        _restore_corp_actions_file()

    # ---- 22g. [B2 vòng 7] tích luỹ THẬT (mult *=), không phải chỉ giữ hệ số sự kiện CUỐI —
    #           mutation `mult *= a["qty_multiplier"]` -> `mult = a["qty_multiplier"]` hiện SỐNG
    #           qua toàn bộ test cũ vì 22e chỉ có ĐÚNG 1 sự kiện CONFIRMED mỗi lần gọi. 2 sự
    #           kiện CONFIRMED cùng ticker, cả 2 ex_date đều SAU asof -> kết quả PHẢI là TÍCH của
    #           cả 2 hệ số (1,30 × 1,10 = 1,43), không phải chỉ hệ số của record xử lý SAU CÙNG.
    try:
        ev1 = dict(_valid_vpb)
        ev1.update(qty_multiplier=1.30, ex_date="2026-09-15",
                   broker_effective_ts="2026-09-14T19:00:00+07:00")
        ev2 = dict(_valid_vpb)
        ev2.update(qty_multiplier=1.10, ex_date="2026-09-20",
                   broker_effective_ts="2026-09-19T19:00:00+07:00")
        daily_nav_snapshot.CORP_ACTIONS_FILE = _write_registry([ev1, ev2])
        mult = daily_nav_snapshot.confirmed_qty_multiplier_after("VPB", "2026-09-01")
        check("22g [B2]: 2 sự kiện CONFIRMED cùng ticker, cả 2 ex_date SAU asof -> mult = "
              "TÍCH của cả 2 hệ số (1,30 × 1,10 = 1,43), KHÔNG chỉ hệ số cuối (bắt mutation "
              "mult *= -> mult =)",
              abs(mult - 1.43) < 1e-9, f"mult={mult}")
    finally:
        _restore_corp_actions_file()

    print(f"\n{'='*70}\nPASS={len(PASS)} FAIL={len(FAIL)}")
    if FAIL:
        for name, detail in FAIL:
            print(f"  - {name}: {detail}")
        return 1
    print("Tat ca selfcheck PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
