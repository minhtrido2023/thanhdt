# -*- coding: utf-8 -*-
"""Regression self-check for the vol-scaled chase-cap patch (default-OFF).

Proves: (1) OFF => _buy_chase_pct returns the static cap exactly (byte-identical cap path);
(2) ON => clamp(k*rvol, static, ceil) exactly, per stored _gap_ref rvol_20d;
(3) fail-safe => ON but rvol missing/<=0 falls back to the static cap;
(4) monotone => ON cap is NEVER below the static cap for any rvol.
Drives the REAL Executor via load_config(), not a re-implementation."""
import os, sys, copy
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
os.chdir(WORKDIR)
from trading_bot.config import load_config
from trading_bot.executor import Executor


def _mk(cfg):
    ex = Executor.__new__(Executor)          # bypass __init__ (needs broker/plan); we only test _buy_chase_pct
    ex.cfg = cfg
    ex._gap_ref = {}
    return ex


def main():
    base = load_config()
    static = base["max_chase_pct_buy"]
    k = base.get("chase_cap_vol_k", 2.0)
    ceil = base.get("chase_cap_vol_ceil", 0.04)
    ok = True

    # 0) shipped default must be OFF
    off_default = (base.get("chase_cap_vol_scale_enabled", False) is False)
    print(f"0) shipped default OFF: {'PASS' if off_default else 'FAIL'}")
    ok &= off_default

    # 1) OFF => static exactly, regardless of any rvol present
    cfg_off = copy.deepcopy(base); cfg_off["chase_cap_vol_scale_enabled"] = False
    ex = _mk(cfg_off); ex._gap_ref = {"AAA": {"rvol_20d": 0.03}}   # even with high vol on record
    r = ex._buy_chase_pct("AAA")
    p1 = (r == static)
    print(f"1) OFF byte-identical to static ({static}): got {r} -> {'PASS' if p1 else 'FAIL'}")
    ok &= p1

    # 2) ON => clamp(k*rvol, static, ceil) exactly, across the 3 regimes
    cfg_on = copy.deepcopy(base); cfg_on["chase_cap_vol_scale_enabled"] = True
    ex = _mk(cfg_on)
    cases = {
        "low_vol_clamps_to_floor":  (0.005, min(max(k * 0.005, static), ceil)),   # 0.01<static -> static
        "mid_vol_scales":           (0.010, min(max(k * 0.010, static), ceil)),   # 0.02 in-band
        "high_vol_clamps_to_ceil":  (0.030, min(max(k * 0.030, static), ceil)),   # 0.06>ceil -> ceil
    }
    for name, (rvol, want) in cases.items():
        ex._gap_ref = {"T": {"rvol_20d": rvol}}
        got = ex._buy_chase_pct("T")
        p = abs(got - want) < 1e-12
        print(f"2) ON {name}: rvol={rvol} -> {got:.5f} (want {want:.5f}) {'PASS' if p else 'FAIL'}")
        ok &= p
        # monotone: never below static
        mono = got >= static - 1e-12
        ok &= mono

    # 3) fail-safe: ON but rvol missing / <=0 / no ref => static
    ex._gap_ref = {"T": {"rvol_20d": 0.0}}
    fs1 = ex._buy_chase_pct("T") == static           # rvol==0
    ex._gap_ref = {"T": {"rvol_20d": -0.01}}
    fs2 = ex._buy_chase_pct("T") == static           # rvol<0
    ex._gap_ref = {}
    fs3 = ex._buy_chase_pct("MISSING") == static      # no ref at all
    print(f"3) fail-safe (rvol=0 / <0 / absent) -> static: "
          f"{fs1}/{fs2}/{fs3} {'PASS' if (fs1 and fs2 and fs3) else 'FAIL'}")
    ok &= fs1 and fs2 and fs3

    # 4) monotone across a sweep of rvol values (ON): cap in [static, ceil], never < static
    ex2 = _mk(cfg_on)
    mono_all = True
    for rvol in [0.0, 0.001, 0.005, 0.0075, 0.01, 0.02, 0.03, 0.10]:
        ex2._gap_ref = {"T": {"rvol_20d": rvol}}
        c = ex2._buy_chase_pct("T")
        if not (static - 1e-12 <= c <= ceil + 1e-12):
            mono_all = False
    print(f"4) monotone + bounded [static,ceil] across rvol sweep: {'PASS' if mono_all else 'FAIL'}")
    ok &= mono_all

    print(f"\nSELF-CHECK: {'ALL PASS' if ok else 'FAIL'}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
