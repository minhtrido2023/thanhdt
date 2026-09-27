# -*- coding: utf-8 -*-
"""failc_sweep8_selfcheck.py — selfcheck for the FAIL-C as-of sweep (job Taylor_20260927_103332).

Guards the 8 remaining edge-health call-sites that were re-labelled `entry` -> `known_date`.
The check is SEMANTIC, not a grep: for each file it lifts the real patched block out of the
source, execs it against a synthetic lag_edge_health.csv whose `entry` and `known_date` straddle
a probe date, and asserts the resulting series carries the value that was OBSERVABLE on that
date (known_date labelling) — not the look-ahead one (`entry` labelling).

Mutation mode (--mutations) reverts each patch in-memory and asserts the matching assertion DIES.
An assertion that survives its own mutation is not testing anything.

Usage:
  python3 failc_sweep8_selfcheck.py              # assertions only
  python3 failc_sweep8_selfcheck.py --mutations  # + mutation kill-test
  python3 failc_sweep8_selfcheck.py --all-tz     # re-exec self under 4 TZ regimes (incl. unset)
"""
import io, os, re, subprocess, sys, textwrap, tempfile

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
import numpy as np
import pandas as pd

WC = os.path.dirname(os.path.abspath(__file__))

# file -> name of the variable the block assigns the daily-reindexed series to
TARGETS = {
    "pt_v22_dt5g.py":                               "_m12",
    "pt_v23_audit_ddpark.py":                       "_edge_m12",
    "pt_v23_lagcap_research.py":                    "_edge_m12",
    "pt_v23_lagqual_research.py":                   "_edge_m12",
    "lag_dnpr_harness.py":                          "_edge_m12",
    "converge_fullharness_test.py":                 "_edge_m12",
    "data/research_edge_alloc_walkforward.py":      "mean12",
    "data/research_edge_conditional_allocator.py":  "mean12",
}

START = '_eh_path = os.environ.get("EDGE_HEALTH_CSV"'
PROBE = pd.Timestamp("2020-03-10")          # after `entry`, before `known_date` of the trap row
COMMON = pd.bdate_range("2020-01-01", "2020-06-30")

_fails, _checks = [], 0


def check(cond, label):
    global _checks
    _checks += 1
    if not cond:
        _fails.append(label)
    return bool(cond)


def synth_csv(with_known_date=True):
    """Row 2's value is OBSERVABLE only from known_date 2020-04-01, though it is keyed entry 2020-02-03.
    A probe on 2020-03-10 must therefore still read row 1's value (1.0), not row 2's (99.0)."""
    rows = [
        ("2019-11-01", "2019-12-06", 1.0),
        ("2020-02-03", "2020-04-01", 99.0),
        ("2020-05-04", "2020-06-08", 7.0),
    ]
    df = pd.DataFrame(rows, columns=["entry", "known_date", "mean12"])
    if not with_known_date:
        df = df.drop(columns=["known_date"])
    fd, path = tempfile.mkstemp(suffix=".csv", prefix="failc8_synth_")
    os.close(fd)
    df.to_csv(path, index=False)
    return path


def lift_block(path, mutate=None):
    """Return the patched edge-series block from `path`, dedented, optionally mutated."""
    src = open(os.path.join(WC, path), encoding="utf-8").read().splitlines()
    i = next(n for n, l in enumerate(src) if START in l)
    j = next(n for n, l in enumerate(src[i:], i) if 'reindex(common, method="ffill")' in l)
    block = textwrap.dedent("\n".join(src[i:j + 1]))
    if mutate == "revert_key":                       # M1: undo the fix -> back to `entry`
        block = re.sub(r'_eh_key = .*', '_eh_key = "entry"', block, count=1)
    elif mutate == "drop_warning":                   # M2: silence the missing-column warning
        block = re.sub(r'if _eh_key != "known_date":\n(    .*\n)+', '', block)
    return block


def run_block(path, csv_path, mutate=None):
    """Exec the lifted block with a captured stdout; return (series, printed_text)."""
    ns = {"os": os, "pd": pd, "np": np, "common": COMMON,
          "WORKDIR": WC, "W": WC, "__name__": "__failc8_selfcheck__"}
    old_env, old_out = os.environ.get("EDGE_HEALTH_CSV"), sys.stdout
    os.environ["EDGE_HEALTH_CSV"] = csv_path
    cap = io.StringIO()
    sys.stdout = cap
    try:
        exec(compile(lift_block(path, mutate), f"<{path}:edge-block>", "exec"), ns)
    finally:
        sys.stdout = old_out
        if old_env is None:
            os.environ.pop("EDGE_HEALTH_CSV", None)
        else:
            os.environ["EDGE_HEALTH_CSV"] = old_env
    return ns[TARGETS[path]], cap.getvalue()


def assertions(path, mutate=None):
    """The real assertions. Returns True iff ALL pass (used by both normal and mutation mode)."""
    ok = True
    csv_ok = synth_csv(True)
    csv_no = synth_csv(False)
    try:
        s, out = run_block(path, csv_ok, mutate)
        # A1 — causal labelling: the probe date must NOT see the value that only became
        #      observable 3 weeks later. This is the FAIL-C bug, stated as a number.
        ok &= check(float(s.loc[PROBE]) == 1.0,
                    f"{path} A1 causal: mean12@{PROBE.date()} == 1.0 (got {float(s.loc[PROBE])})")
        # A2 — the look-ahead value must be absent before its known_date and present after.
        ok &= check(float(s.loc[pd.Timestamp("2020-04-01")]) == 99.0,
                    f"{path} A2 value lands on its known_date")
        # A3 — the block must announce which label column it used (no silent as-of choice).
        ok &= check("label_col=known_date" in out,
                    f"{path} A3 prints label_col=known_date")
        # A4 — missing column must be LOUD, not silent (dispatch requirement).
        _, out_no = run_block(path, csv_no, mutate)
        ok &= check("WARNING" in out_no and "known_date" in out_no,
                    f"{path} A4 warns loudly when known_date column is absent")
        # A5 — and in that degraded mode it must fall back to `entry` (not crash).
        s_no, _ = run_block(path, csv_no, mutate)
        ok &= check(float(s_no.loc[PROBE]) == 99.0,
                    f"{path} A5 documented fallback to `entry` when column missing")
    finally:
        for p in (csv_ok, csv_no):
            try:
                os.unlink(p)
            except OSError:
                pass
    return ok


def main():
    if "--all-tz" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--all-tz"]
        rc = 0
        for label, env in [("TZ=Asia/Ho_Chi_Minh", {"TZ": "Asia/Ho_Chi_Minh"}),
                           ("TZ=UTC", {"TZ": "UTC"}),
                           ("TZ=America/Los_Angeles", {"TZ": "America/Los_Angeles"}),
                           ("TZ UNSET", None)]:
            e = dict(os.environ)
            e.pop("TZ", None)
            if env:
                e.update(env)
            print(f"\n=========== {label} ===========")
            r = subprocess.run([sys.executable, os.path.abspath(__file__)] + args, env=e)
            rc |= r.returncode
        print(f"\n[all-tz] overall {'PASS' if rc == 0 else 'FAIL'} across 4 TZ regimes")
        return rc

    print(f"failc_sweep8_selfcheck — {len(TARGETS)} call-sites, WC={WC}")
    for path in TARGETS:
        print(f"  {'PASS' if assertions(path) else 'FAIL'}  {path}")
    print(f"\n{_checks} assertions, {len(_fails)} failed")
    for f in _fails:
        print(f"  FAILED: {f}")
    rc = 1 if _fails else 0

    if "--mutations" in sys.argv:
        print("\n--- mutation kill-test (each revert MUST make its assertion die) ---")
        killed = survived = 0
        for path in TARGETS:
            for m, why in [("revert_key", "revert entry->known_date fix"),
                           ("drop_warning", "delete missing-column warning")]:
                base_fails = len(_fails)
                assertions(path, mutate=m)
                died = len(_fails) > base_fails
                del _fails[base_fails:]          # mutation failures are EXPECTED, not real failures
                print(f"  {'KILLED ' if died else 'SURVIVED'} {path} :: {why}")
                killed += died
                survived += not died
        print(f"\n{killed} mutations killed, {survived} survived "
              f"({killed}/{killed + survived})")
        if survived:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
