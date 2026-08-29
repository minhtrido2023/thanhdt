#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck cho `discretionary_margin_gate.py` — 0 side-effect thật (không ghi bus/Discord thật,
không đụng `data/discretionary_margin_arms.json` production).

Theo skill verify-before-done: chạy dưới TZ lạ (env -u TZ) để bắt lỗi neo múi giờ tường minh (§16).
KHÔNG chạm Executor (sleeve này không wire vào bot) nên không cần MIKE_BOT_TEST_MODE (§5b).
"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import discretionary_margin_gate as gate  # noqa: E402

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

    # ---- 3. sleeve cap block: case thu 2 lam tong > 5% NAV ----
    rc = gate.cmd_arm(mkargs(ticker="DGC", arm_price=5000, exposure_vnd=0.01 * NAV[0]))
    check("sleeve cap chan case thu 2 (tong 6% > 5% cap)", rc == 2, f"rc={rc}")
    check("sleeve cap block KHONG them record moi", len(gate.load_arms()) == 1)

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

    print(f"\n{'='*70}\nPASS={len(PASS)} FAIL={len(FAIL)}")
    if FAIL:
        for name, detail in FAIL:
            print(f"  - {name}: {detail}")
        return 1
    print("Tat ca selfcheck PASS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
