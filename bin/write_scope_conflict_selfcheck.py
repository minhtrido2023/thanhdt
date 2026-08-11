#!/usr/bin/env python3
"""Selfcheck for `mike_json.py job-write-scope-conflict` + dispatch.sh's --write-scope gate
(2026-08-11). Replaces the worktree-pool write-isolation design (bin/job_workspace.py, bounced
twice by arch-reviewer for creating a NEW class of risk — reset --hard/clean -fd resolving into
the shared production repo). This mechanism is pure JSON comparison, touches no git state at all.

Targets the coord-2026-08-07 incident shape: two DIFFERENT agents with DIFFERENT prompts both
editing trading_bot/plan_funding_gate.py within a minute, one commit clobbering the other's
uncommitted work. job-find-dup (exact-prompt match, same agent) cannot see this collision —
write_scope is a caller-declared field precisely so the check does not need to guess.

Run: python3 bin/write_scope_conflict_selfcheck.py     (exit 0 = all pass)
No network, no BQ, no clock/TZ dependence — safe to run anywhere, any time.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJ = os.path.join(ROOT, "bin", "mike_json.py")
DISPATCH_SH = os.path.join(ROOT, "bin", "dispatch.sh")

PASS = 0
FAIL = 0
SPAWNED = []
TMPDIRS = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  ok   %s" % name)
    else:
        FAIL += 1
        print("  FAIL %s%s" % (name, ("  -- " + detail) if detail else ""))


def run(args, **kw):
    p = subprocess.run(args, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout, p.stderr


def mkjobs():
    d = tempfile.mkdtemp(prefix="wsc_selfcheck_")
    TMPDIRS.append(d)
    return d


def spawn_live_proc():
    """A real, long-lived pid — _job_live_pids resolves liveness via /proc, not a bare status
    string, so a fixture claiming status=running needs a genuinely alive pid to be believed."""
    p = subprocess.Popen(["sleep", "300"])
    SPAWNED.append(p)
    return p.pid


def write_record(jobs_dir, job_id, **fields):
    rec = {"job_id": job_id, "from": "Mike", "to": "Taylor", "logfile": "",
           "started_at": int(time.time()) - 30}
    rec.update(fields)
    with open(os.path.join(jobs_dir, job_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(rec, f)


def conflict(jobs_dir, scope_csv):
    return run([sys.executable, MJ, "job-write-scope-conflict", jobs_dir, scope_csv])


def cleanup():
    for p in SPAWNED:
        try:
            p.kill()
            p.wait(timeout=5)
        except Exception:
            pass
    SPAWNED.clear()
    for d in TMPDIRS:
        shutil.rmtree(d, ignore_errors=True)
    TMPDIRS.clear()


def main():
    # A: exact overlap on a live, running job -> conflict (exit 0), job_id printed.
    jd = mkjobs()
    pid = spawn_live_proc()
    write_record(jd, "A_running", status="running", pid=pid,
                 write_scope="trading_bot/plan_funding_gate.py,foo.py")
    rc, out, _ = conflict(jd, "trading_bot/plan_funding_gate.py")
    check("A: overlap + live pid -> conflict (exit 0)", rc == 0, "rc=%d out=%r" % (rc, out))
    check("A: conflicting job_id printed", "A_running" in out, out)

    # B: disjoint scope -> no conflict (exit 1), no output.
    rc, out, _ = conflict(jd, "some/other_file.py")
    check("B: disjoint scope -> no conflict (exit 1)", rc == 1, "rc=%d" % rc)
    check("B: no output on disjoint scope", out.strip() == "", repr(out))

    # C: overlap but status=done -> not live_enough -> no conflict, even with a live pid.
    write_record(jd, "C_done", status="done", pid=pid,
                 write_scope="trading_bot/plan_funding_gate.py")
    rc, out, _ = conflict(jd, "trading_bot/plan_funding_gate.py")
    # A_running still overlaps here too, so this only isolates C by checking A alone next.
    os.remove(os.path.join(jd, "A_running.json"))
    rc, out, _ = conflict(jd, "trading_bot/plan_funding_gate.py")
    check("C: status=done + overlap -> no conflict (exit 1)", rc == 1, "rc=%d out=%r" % (rc, out))
    os.remove(os.path.join(jd, "C_done.json"))

    # D: status=running but pid is dead -> _job_live_pids finds nothing -> no conflict.
    dead_pid = 99999999
    write_record(jd, "D_dead_pid", status="running", pid=dead_pid,
                 write_scope="trading_bot/plan_funding_gate.py")
    rc, out, _ = conflict(jd, "trading_bot/plan_funding_gate.py")
    check("D: running status + dead pid -> no conflict (exit 1)", rc == 1, "rc=%d out=%r" % (rc, out))
    os.remove(os.path.join(jd, "D_dead_pid.json"))

    # E: empty scope_csv -> exit 1 unconditionally (nothing declared, nothing to check).
    rc, out, _ = conflict(jd, "")
    check("E: empty scope -> exit 1", rc == 1, "rc=%d" % rc)

    # F: full dispatch.sh E2E — a real conflicting --write-scope must abort BEFORE the CLI
    # binary is invoked (exit 6) and must NOT create a job record for the blocked attempt
    # (same no-orphan-record contract as the circuit breaker's exit 4).
    # dispatch.sh always computes JOBS_DIR from ITS OWN $ROOT (bin/..), not a caller-supplied
    # dir, so this leg has to seed the repo's real bus/jobs/ — safe here because ROOT is this
    # worktree's own git root, never the shared fleet repo (a git worktree gets its own
    # untracked bus/ and state/ directories, confirmed empty before this selfcheck runs).
    fake_bus = os.path.join(ROOT, "bus", "jobs")
    live_pid = spawn_live_proc()
    seeded = "Taylor_wsc_selfcheck_seed"
    os.makedirs(fake_bus, exist_ok=True)
    pre_existing = set(os.listdir(fake_bus))
    write_record(fake_bus, seeded, status="running", pid=live_pid,
                 write_scope="trading_bot/plan_funding_gate.py")
    try:
        env = dict(os.environ)
        env["DISPATCH_CLAUDE_BIN"] = "/bin/echo"  # unreached if the gate works; harmless if not
        rc, out, err = run(
            ["bash", DISPATCH_SH, "Taylor", "write-scope selfcheck F — should never reach the CLI",
             "--write-scope", "trading_bot/plan_funding_gate.py", "--timeout", "5"],
            cwd=ROOT, env=env)
        check("F: real dispatch.sh aborts with exit 6 on declared conflict", rc == 6, "rc=%d err=%r" % (rc, err))
        check("F: error message names the colliding job", seeded in err, err)
        post = set(os.listdir(fake_bus)) - pre_existing - {seeded + ".json"}
        check("F: no orphan job record created for the blocked attempt", not post, post)
        for extra in post:
            os.remove(os.path.join(fake_bus, extra))
    finally:
        os.remove(os.path.join(fake_bus, seeded + ".json"))

    rc, _, err = run([sys.executable, "-m", "py_compile", MJ])
    check("py_compile bin/mike_json.py", rc == 0, err[:200])
    rc, _, err_bash = run(["bash", "-n", DISPATCH_SH])
    check("bash -n bin/dispatch.sh", rc == 0, err_bash[:200])

    cleanup()
    print("\n%d/%d PASS%s" % (PASS, PASS + FAIL, "" if not FAIL else "  — %d FAILED" % FAIL))
    return 1 if FAIL else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        cleanup()
