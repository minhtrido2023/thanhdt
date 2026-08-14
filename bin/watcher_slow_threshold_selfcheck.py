#!/usr/bin/env python3
"""watcher_slow_threshold_selfcheck.py — selfcheck cho bin/watcher_slow_threshold.py.

Chạy: python3 bin/watcher_slow_threshold_selfcheck.py   (exit 0 = PASS, 1 = FAIL)
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(ROOT, "watcher_slow_threshold.py")

FIXTURE = {
    "buckets": {
        "Wags|opus|high": {"n": 16, "median_s": 776, "p75_s": 1411},
        "Mafee|?|?": {"n": 8, "median_s": 93, "p75_s": 112},
        "Weird|tiny|median": {"n": 5, "median_s": 40, "p75_s": 45},
    },
    "global_fallback": {"n": 792, "median_s": 455, "p75_s": 706},
}

failures = []


def check(name, cond):
    status = "PASS" if cond else "FAIL"
    print("[%s] %s" % (status, name))
    if not cond:
        failures.append(name)


def run(bucket_key, profile_path):
    out = subprocess.run(
        [sys.executable, SCRIPT, bucket_key, profile_path],
        capture_output=True, text=True, timeout=10,
    )
    t1, t2 = (int(x) for x in out.stdout.strip().split())
    return t1, t2


with tempfile.TemporaryDirectory() as d:
    good_path = os.path.join(d, "wakeup_profile.json")
    with open(good_path, "w", encoding="utf-8") as f:
        json.dump(FIXTURE, f)

    # 1) Known bucket, median already > floor -> t1=median, t2=p75.
    t1, t2 = run("Wags|opus|high", good_path)
    check("known bucket: t1=median (776)", t1 == 776)
    check("known bucket: t2=p75 (1411)", t2 == 1411)

    # 2) Unknown bucket -> falls back to global_fallback, NOT the hard (180,420).
    t1, t2 = run("NoSuchAgent|weird|combo", good_path)
    check("unknown bucket falls back to global_fallback median (455)", t1 == 455)
    check("unknown bucket falls back to global_fallback p75 (706)", t2 == 706)

    # 3) Bucket with median below the 180s floor -> t1 clamped to floor, t2 still
    #    respects p75 if p75 > t1+60, else clamped to t1+60.
    t1, t2 = run("Weird|tiny|median", good_path)
    check("tiny-median bucket: t1 floored at 180 (not 40)", t1 == 180)
    check("tiny-median bucket: t2 = max(t1+60, p75) = max(240, 45) = 240", t2 == 240)

    # 4) Missing profile file -> hard fallback (180, 420), never raises.
    missing_path = os.path.join(d, "does_not_exist.json")
    t1, t2 = run("Wags|opus|high", missing_path)
    check("missing file -> hard fallback (180, 420)", (t1, t2) == (180, 420))

    # 5) Malformed JSON -> hard fallback, never raises/crashes (exit code 0).
    bad_path = os.path.join(d, "bad.json")
    with open(bad_path, "w", encoding="utf-8") as f:
        f.write("{not valid json")
    proc = subprocess.run(
        [sys.executable, SCRIPT, "Wags|opus|high", bad_path],
        capture_output=True, text=True, timeout=10,
    )
    check("malformed JSON: exit code 0 (never blocks the watcher)", proc.returncode == 0)
    t1, t2 = (int(x) for x in proc.stdout.strip().split())
    check("malformed JSON -> hard fallback (180, 420)", (t1, t2) == (180, 420))

    # 6) Profile with buckets but NO global_fallback key, unknown bucket -> still
    #    hard fallback (defensive: `.get('global_fallback') or {}` must not KeyError).
    no_fallback_path = os.path.join(d, "no_fallback.json")
    with open(no_fallback_path, "w", encoding="utf-8") as f:
        json.dump({"buckets": FIXTURE["buckets"]}, f)
    t1, t2 = run("NoSuchAgent|weird|combo", no_fallback_path)
    check("no global_fallback + unknown bucket -> hard fallback (180, 420)",
          (t1, t2) == (180, 420))

    # 7) t1 < t2 always holds (monotonic — the watcher fires t1 before t2).
    for key in ("Wags|opus|high", "Mafee|?|?", "Weird|tiny|median", "NoSuchAgent|x|y"):
        t1, t2 = run(key, good_path)
        check("t1 < t2 for bucket %r" % key, t1 < t2)

print()
if failures:
    print("=== watcher_slow_threshold_selfcheck: %d FAIL(s): %s ===" % (len(failures), failures))
    sys.exit(1)
print("=== watcher_slow_threshold_selfcheck: ALL PASS ===")
sys.exit(0)
