# -*- coding: utf-8 -*-
"""
dcf_refresh_gate_selfcheck.py — selfcheck for dcf_refresh_gate.py (Việc 2, job Taylor_20260717_063638).

Covers the decision logic across the 1pp band + the boundary, first-run init, persistence, idempotency,
and the fail-safe. Uses a tmp state/log path so it never touches the real data/dcf_refresh_state.json.
Run: $DNA_PYEXE dcf_refresh_gate_selfcheck.py   → prints PASS/FAIL per case, exits non-zero on any FAIL.
"""
import os, sys, json, tempfile
WORKDIR = "/home/trido/thanhdt/WorkingClaude"
sys.path.insert(0, WORKDIR)
import dcf_refresh_gate as GATE

fails = []


def check(name, cond):
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
    if not cond:
        fails.append(name)


# ---- pure decision logic (no I/O) --------------------------------------------------------------
print("decide() — band + boundary:")
check("delta 1.5pp > 1 → refresh",        GATE.decide(6.5, {"last_used_rate": 5.0})[0] is True)
check("delta 0.5pp < 1 → skip",           GATE.decide(5.5, {"last_used_rate": 5.0})[0] is False)
check("delta 0.99pp < 1 → skip",          GATE.decide(5.99, {"last_used_rate": 5.0})[0] is False)
check("delta exactly 1.0pp → refresh (inclusive)", GATE.decide(6.0, {"last_used_rate": 5.0})[0] is True)
check("delta 1.01pp → refresh",           GATE.decide(6.01, {"last_used_rate": 5.0})[0] is True)
check("float 6.8-5.8=1.0pp → refresh (no float-eq miss)", GATE.decide(6.8, {"last_used_rate": 5.8})[0] is True)
check("downward move -1.2pp → refresh (abs)", GATE.decide(4.8, {"last_used_rate": 6.0})[0] is True)
check("no state → refresh (first run)",   GATE.decide(6.0, None)[0] is True)
check("empty state dict → refresh",       GATE.decide(6.0, {})[0] is True)

# strict '>' variant honored if flag flipped
GATE.THRESHOLD_INCLUSIVE = False
check("strict mode: exactly 1.0pp → skip", GATE.decide(6.0, {"last_used_rate": 5.0})[0] is False)
check("strict mode: 1.01pp → refresh",     GATE.decide(6.01, {"last_used_rate": 5.0})[0] is True)
GATE.THRESHOLD_INCLUSIVE = True

# ---- run_gate() persistence + idempotency ------------------------------------------------------
print("\nrun_gate() — persistence + idempotency (tmp paths, forced asof):")
d = tempfile.mkdtemp()
sp, lp = os.path.join(d, "state.json"), os.path.join(d, "gate.log")

# first run: no state → refresh, writes last_used_rate = the as-of deposit rate
r1 = GATE.run_gate(asof="2026-06-15", state_path=sp, log_path=lp)
st1 = GATE.load_state(sp)
check("first run → refresh", r1["refresh"] is True)
check("state persisted last_used_rate", st1 is not None and "last_used_rate" in st1)
check("state has last_used_date", st1.get("last_used_date") == "2026-06-15")

# second run same as-of: rate unchanged → skip, last_used_rate stays put (idempotent)
r2 = GATE.run_gate(asof="2026-06-15", state_path=sp, log_path=lp)
st2 = GATE.load_state(sp)
check("second run same date → skip", r2["refresh"] is False)
check("last_used_rate unchanged on skip", st2["last_used_rate"] == st1["last_used_rate"])
check("last_check_date advanced", "last_check_date" in st2)

# log appended one line per run
nlog = sum(1 for _ in open(lp))
check("log has 2 append lines", nlog == 2)
check("log lines are valid json", all(json.loads(l) for l in open(lp)))

# ---- fail-safe: broken deposit source → refresh=True -------------------------------------------
print("\nfail-safe:")
_orig = GATE._dep.current_deposit_rate
GATE._dep.current_deposit_rate = lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom"))
rf = GATE.run_gate(asof="2026-06-15", state_path=sp, log_path=lp, dry=True)
check("gate error → refresh=True (fail-safe)", rf["refresh"] is True)
check("gate error → reason flagged", "failsafe" in rf["reason"])
GATE._dep.current_deposit_rate = _orig

# ---- dry run writes nothing --------------------------------------------------------------------
print("\ndry-run isolation:")
d2 = tempfile.mkdtemp(); sp2 = os.path.join(d2, "s.json")
GATE.run_gate(asof="2026-06-15", state_path=sp2, log_path=os.path.join(d2, "l.log"), dry=True)
check("dry run writes no state file", not os.path.exists(sp2))

print(f"\n{'ALL PASS' if not fails else 'FAILURES: ' + ', '.join(fails)}")
sys.exit(1 if fails else 0)
