#!/usr/bin/env python3
"""Selfcheck for the job-board liveness guard + `jobs.sh cancel` (2026-08-10, Wags).

Covers the mechanism behind incident 2026-08-09 (Taylor_20260809_123917 — the 3rd
duplicate-dispatch collision, the one that touched executor.py). Reconstructed from the
primary evidence, NOT from the retro's hypothesis:

    12:39:17Z  Mike dispatches Taylor_20260809_123917 (--bg, timeout 600s)
    12:39:34Z  Mike decides 600s is too short and improvises a cancel:
                   kill 2135469            <- the _bg_wrapper pid, NOT the worker
                   ps -p 2135469           <- prints only a header => "it's dead"
                   mike_json.py job-set bus/jobs Taylor_20260809_123917 status=failed
    12:40:16Z  Mike re-dispatches the same prompt as Taylor_20260809_124016
    12:40:06Z .. 13:11:32Z  the "failed" job keeps writing bus heartbeats and keeps
               editing executor.py + plan.py, finishing successfully 33 min later.

Both halves of that improvisation were wrong, and each has its own case below:
  * `kill <pid>` reaches only the wrapper. The worker is spawned under `setsid` (own
    session), so it survives and is reparented to init — invisible to a PPid walk. (F, H)
  * `job-set status=<terminal>` had zero liveness validation, so the board asserted a
    failure that had not happened. That assertion is what triggered the re-dispatch. (A)

The guard must NOT break the legitimate writers, so the regression cases matter as much as
the new ones: dispatch.sh's own _bg_wrapper finalises its record from inside the recorded
pid (E), the retry path writes non-terminal statuses on a live job (D), and job-reap writes
status=orphaned once the pid is dead (C).

Run: python3 bin/job_cancel_guard_selfcheck.py     (exit 0 = all pass)
No network, no BQ, no clock/TZ dependence — safe to run anywhere, any time.
"""
import json
import os
import shlex
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJ = os.path.join(ROOT, "bin", "mike_json.py")
JOBS_SH = os.path.join(ROOT, "bin", "jobs.sh")

PASS = 0
FAIL = 0
SPAWNED = []


def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  ok   %s" % name)
    else:
        FAIL += 1
        print("  FAIL %s%s" % (name, ("  -- " + detail) if detail else ""))


def run(args, **kw):
    """Run mike_json.py (or any argv) and return (rc, stdout, stderr)."""
    p = subprocess.run(args, capture_output=True, text=True, **kw)
    return p.returncode, p.stdout, p.stderr


def jset(jobs_dir, job_id, *pairs):
    return run([sys.executable, MJ, "job-set", jobs_dir, job_id] + list(pairs))


def read_job(jobs_dir, job_id):
    with open(os.path.join(jobs_dir, job_id + ".json"), encoding="utf-8") as f:
        return json.load(f)


def alive(pid):
    """Same definition mike_json._pid_alive uses: a zombie is DEAD. The wrapper processes
    here are children of this selfcheck, so a killed one lingers as a zombie until reaped —
    `kill -0` would call that alive and every death assertion below would be wrong."""
    try:
        os.kill(int(pid), 0)
    except Exception:
        return False
    try:
        with open("/proc/%d/status" % int(pid), encoding="utf-8") as f:
            for line in f:
                if line.startswith("State:"):
                    return line.split()[1] != "Z"
    except Exception:
        return False
    return True


def spawn_wrapper(logfile):
    """Reproduce dispatch.sh's process shape: a wrapper bash whose worker child is put in
    its OWN session by `setsid` (exactly what _hb_aware_timeout does), with the worker's
    stdout redirected to the job's logfile (what _bg_wrapper does). Returns (wrapper_pid,
    worker_pid)."""
    script = ("setsid sleep 120 >>%s 2>&1 & echo $! > %s; sleep 120"
              % (shlex.quote(logfile), shlex.quote(logfile + ".workerpid")))
    p = subprocess.Popen(["bash", "-c", script],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SPAWNED.append(p.pid)
    worker = None
    for _ in range(50):
        try:
            with open(logfile + ".workerpid", encoding="utf-8") as f:
                worker = int(f.read().strip())
            break
        except Exception:
            time.sleep(0.1)
    if worker:
        SPAWNED.append(worker)
    return p.pid, worker


def make_job(jobs_dir, job_id, pid, logfile, prompt="do the thing", to="Taylor"):
    rc, _, err = jset(jobs_dir, job_id, "job_id=" + job_id, "from=Mike", "to=" + to,
                      "status=running", "attempt=1", "max_attempts=2",
                      "started_at=1000", "deadline=1600", "logfile=" + logfile,
                      "prompt_summary=" + prompt, "pid=%s" % pid)
    assert rc == 0, err
    return job_id


def cleanup():
    for pid in SPAWNED:
        for sig in (15, 9):
            try:
                os.kill(pid, sig)
            except Exception:
                pass


def main():
    tmp = tempfile.mkdtemp(prefix="jobguard_")
    jobs = os.path.join(tmp, "jobs")
    os.makedirs(jobs, exist_ok=True)

    # ---------------------------------------------------------------- A: the incident
    print("\nA. job-set REFUSES a terminal status while the job's pid is alive "
          "(the 2026-08-09 write)")
    log_a = os.path.join(tmp, "a.log")
    wpid_a, worker_a = spawn_wrapper(log_a)
    make_job(jobs, "J_A", wpid_a, log_a)
    rc, out, err = jset(jobs, "J_A", "status=failed")
    check("exit code 3 (refused)", rc == 3, "rc=%d" % rc)
    check("explains why + points at jobs.sh cancel",
          "REFUSED" in err and "jobs.sh cancel" in err, err[:200])
    check("record UNCHANGED — still running", read_job(jobs, "J_A")["status"] == "running",
          read_job(jobs, "J_A")["status"])
    check("no ended_at written", "ended_at" not in read_job(jobs, "J_A"))
    # Every known death word...
    for st in ("done", "timeout", "orphaned", "cancelled"):
        rc, _, _ = jset(jobs, "J_A", "status=" + st)
        check("also refuses status=%s" % st, rc == 3, "rc=%d" % rc)
    # ...AND every word nobody thought of. The first version of this guard was a denylist of
    # the 5 known death words; arch-reviewer broke it in one try with status=aborted, which
    # cmd_job_get maps to exit 1 ("failed") for every poller — the same signal that caused
    # the 08-09 re-dispatch. The board already holds 6 hand-stamped records using 'aborted'
    # (×3), 'superseded' and 'cancelled', three of them MORE RECENT than that incident. So
    # the invariant under test is the allowlist, not a list of forbidden words.
    for st in ("aborted", "superseded", "killed", "stopped", "zzz_made_up", ""):
        rc, _, _ = jset(jobs, "J_A", "status=" + st)
        check("refuses invented status=%r (allowlist, not denylist)" % st, rc == 3,
              "rc=%d — record is now %s" % (rc, read_job(jobs, "J_A")["status"]))
    check("record still running after every attempt",
          read_job(jobs, "J_A")["status"] == "running", read_job(jobs, "J_A")["status"])

    # ---------------------------------------------------------------- B: escape hatch
    print("\nB. --force is available but must carry its evidence")
    rc, _, err = jset(jobs, "J_A", "status=failed", "--force")
    check("--force alone is REFUSED (would recreate the no-ended_at shape)", rc == 3,
          "rc=%d" % rc)
    check("says what is missing", "ended_at" in err and "result_summary" in err, err[:200])
    check("record untouched", read_job(jobs, "J_A")["status"] == "running")
    rc, _, err = jset(jobs, "J_A", "status=failed", "ended_at=1786000000",
                      "result_summary=pid recycled, record stale", "--force")
    check("--force WITH ended_at + reason succeeds", rc == 0, err[:200])
    check("status written", read_job(jobs, "J_A")["status"] == "failed")
    check("forced close carries ended_at", read_job(jobs, "J_A").get("ended_at") == "1786000000")
    check("--force is not stored as a field", "--force" not in read_job(jobs, "J_A"))

    # ---------------------------------------------------- C: regression — dead pid path
    print("\nC. REGRESSION — a dead pid is still freely closable (job-reap / stale records)")
    log_c = os.path.join(tmp, "c.log")
    wpid_c, worker_c = spawn_wrapper(log_c)
    make_job(jobs, "J_C", wpid_c, log_c)
    cleanup()
    del SPAWNED[:]
    time.sleep(0.5)
    check("precondition: pid really dead", not alive(wpid_c))
    rc, _, err = jset(jobs, "J_C", "status=orphaned", "ended_at=1")
    check("exit 0", rc == 0, err[:200])
    check("status=orphaned written", read_job(jobs, "J_C")["status"] == "orphaned")

    # ------------------------------------------- D: regression — non-terminal statuses
    print("\nD. REGRESSION — non-terminal statuses stay writable on a LIVE job "
          "(dispatch.sh retry path)")
    log_d = os.path.join(tmp, "d.log")
    wpid_d, _ = spawn_wrapper(log_d)
    make_job(jobs, "J_D", wpid_d, log_d)
    for st in ("retrying", "usage_limited", "maxturns_pending", "running"):
        rc, _, err = jset(jobs, "J_D", "status=" + st)
        check("allows status=%s on a live job" % st, rc == 0, err[:160])
    rc, _, _ = jset(jobs, "J_D", "deadline=9999", "hb_extensions=1")
    check("allows plain field updates (hb-aware deadline extension)", rc == 0)

    # ------------------------------------------- E: regression — the owner finalises itself
    print("\nE. REGRESSION — the job's OWN wrapper may finalise its record "
          "(dispatch.sh _bg_wrapper)")
    log_e = os.path.join(tmp, "e.log")
    make_job(jobs, "J_E", 999999, log_e)
    # A bash that records ITS OWN pid on the job, then stamps a terminal status from a
    # child process — precisely the shape of _bg_wrapper's `JSET pid=$BASHPID` followed by
    # `JSET status=done`. The guard must see itself in the ancestor chain and allow it.
    script = ("%s %s job-set %s J_E pid=$$ && %s %s job-set %s J_E status=done ended_at=2"
              % (shlex.quote(sys.executable), shlex.quote(MJ), shlex.quote(jobs),
                 shlex.quote(sys.executable), shlex.quote(MJ), shlex.quote(jobs)))
    rc, out, err = run(["bash", "-c", script])
    check("owner's terminal write allowed (exit 0)", rc == 0, err[:250])
    check("status=done landed", read_job(jobs, "J_E")["status"] == "done")

    # ...and under the THREE spawn modes dispatch.sh actually uses. Production takes the
    # systemd-run --scope path (LIFETIME DETACH, dispatch.sh ~1130); if a scope re-parented
    # the wrapper out of mike_json's ancestor chain, EVERY --bg job would be refused its own
    # finalize and hang at status=running forever. That is the highest-risk failure mode of
    # this guard, so it is tested against the real spawner, not just plain `bash -c`.
    scope_ok = run(["systemd-run", "--user", "--scope", "--quiet", "--collect",
                    "/bin/true"])[0] == 0
    modes = [("plain &", []), ("setsid", ["setsid"])]
    if scope_ok:
        modes.append(("systemd-run --user --scope",
                      ["systemd-run", "--user", "--scope", "--quiet", "--collect"]))
    for label, prefix in modes:
        jid = "J_E_" + label.split()[0].strip("-")
        make_job(jobs, jid, 999999, log_e)
        owner = ("%s %s job-set %s %s pid=$$ && %s %s job-set %s %s status=done ended_at=3"
                 % (shlex.quote(sys.executable), shlex.quote(MJ), shlex.quote(jobs), jid,
                    shlex.quote(sys.executable), shlex.quote(MJ), shlex.quote(jobs), jid))
        rc, _, err = run(prefix + ["bash", "-c", owner])
        check("owner finalize works under %s" % label,
              read_job(jobs, jid)["status"] == "done",
              "status=%s rc=%d %s" % (read_job(jobs, jid)["status"], rc, err[:150]))
    check("systemd-run scope path was actually exercised", scope_ok,
          "systemd-run --user --scope unavailable here — production path UNTESTED on this host")

    # ----------------------------------------------------- F: prove the ORIGINAL bug real
    print("\nF. PROVE-THE-BUG — `kill <recorded pid>` does NOT stop the worker "
          "(Mike's improvisation)")
    log_f = os.path.join(tmp, "f.log")
    wpid_f, worker_f = spawn_wrapper(log_f)
    check("setup: wrapper and setsid'd worker both alive",
          worker_f and alive(wpid_f) and alive(worker_f))
    os.kill(wpid_f, 15)
    time.sleep(1.0)
    check("wrapper is dead (so `ps -p <pid>` shows nothing — looks handled)",
          not alive(wpid_f))
    check("but the WORKER SURVIVED — this is the 33-minute orphan of 2026-08-09",
          alive(worker_f), "worker %s died; the reproduction is wrong" % worker_f)
    check("orphan is invisible to a PPid walk (reparented to init)",
          _descendants_of(wpid_f) == [])

    # ------------------------------------------------- G: cancel kills the whole shape
    print("\nG. `jobs.sh cancel` kills wrapper + setsid'd worker, then stamps cancelled")
    log_g = os.path.join(tmp, "g.log")
    wpid_g, worker_g = spawn_wrapper(log_g)
    make_job(jobs, "J_G", wpid_g, log_g)
    check("setup: both alive", alive(wpid_g) and alive(worker_g))
    # jobs.sh pins JOBS_DIR to the real board, so the temp board is driven through the same
    # python entry point jobs.sh calls; the shell front door itself is checked just below.
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_G", "5"])
    check("exit 0", rc == 0, (out + err)[:250])
    time.sleep(0.3)
    check("wrapper dead", not alive(wpid_g))
    check("setsid'd worker dead too (what `kill <pid>` could not do)", not alive(worker_g))
    j = read_job(jobs, "J_G")
    check("status=cancelled (not 'failed' — nothing failed)", j["status"] == "cancelled",
          j["status"])
    check("ended_at recorded", "ended_at" in j)
    check("result_summary says who stopped it",
          "cancelled by operator" in j.get("result_summary", ""), j.get("result_summary", ""))
    # The shell front door is wired to the same command (read-only probe on the real board:
    # a job id that cannot exist, so nothing is ever killed or written).
    rc, out, err = run(["bash", JOBS_SH, "cancel", "__no_such_job__"])
    check("jobs.sh cancel is wired through (exit 4 on unknown id)", rc == 4,
          "rc=%d %s" % (rc, (out + err)[:160]))
    rc, out, err = run(["bash", JOBS_SH, "bogus_subcommand"])
    check("jobs.sh usage line advertises cancel", "cancel <job_id>" in err, err[:200])

    # ------------------------------------------------- H: cancel finds an ALREADY orphan
    print("\nH. cancel still reaches a worker whose wrapper is already gone "
          "(the /proc fd path)")
    log_h = os.path.join(tmp, "h.log")
    wpid_h, worker_h = spawn_wrapper(log_h)
    make_job(jobs, "J_H", wpid_h, log_h)
    os.kill(wpid_h, 9)          # exactly the state Mike left behind on 08-09
    time.sleep(0.8)
    check("setup: wrapper dead, worker orphaned but alive",
          not alive(wpid_h) and alive(worker_h))
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_H", "5"])
    check("exit 0", rc == 0, (out + err)[:250])
    time.sleep(0.3)
    check("orphan found via its logfile fd and killed", not alive(worker_h),
          "orphan %s survived cancel" % worker_h)
    check("status=cancelled", read_job(jobs, "J_H")["status"] == "cancelled")

    # ------------------------------------------------- I: cancel never overstates itself
    print("\nI. cancel refuses to stamp anything it cannot back up")
    log_i = os.path.join(tmp, "i.log")
    make_job(jobs, "J_I", "", log_i)          # sync dispatch — no pid recorded
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_I"])
    check("no pid -> exit 3", rc == 3, "rc=%d" % rc)
    check("no pid -> record untouched", read_job(jobs, "J_I")["status"] == "running")
    check("no pid -> says why", "cannot prove" in err, err[:200])

    make_job(jobs, "J_I2", os.getpid(), log_i)
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_I2"])
    check("refuses to cancel the job it is running inside", rc == 3, "rc=%d" % rc)
    check("self-cancel -> record untouched", read_job(jobs, "J_I2")["status"] == "running")

    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_G"])
    check("already-terminal job -> exit 0, idempotent", rc == 0, (out + err)[:200])
    check("idempotent cancel does not rewrite the status",
          read_job(jobs, "J_G")["status"] == "cancelled")

    rc, _, _ = run([sys.executable, MJ, "job-cancel", jobs, "does_not_exist"])
    check("unknown job -> exit 4 (distinct from 'survived the kill' = 5)", rc == 4, "rc=%d" % rc)

    # BLAST RADIUS. os.kill(0, sig) signals THIS PROCESS GROUP and os.kill(-1, sig) signals
    # every process the user may signal — so a record carrying pid 0 or -1 would have turned
    # `jobs.sh cancel` into a machine-wide SIGKILL (arch-reviewer measured _job_pids("0") =
    # 146 pids including init). Nothing in dispatch.sh writes such a pid, but job-set takes
    # pid= from any caller and this command exists for stressed operators improvising.
    print("\nI2. cancel refuses nonsensical pids instead of mass-signalling")
    canary = subprocess.Popen(["sleep", "60"], stdout=subprocess.DEVNULL)
    SPAWNED.append(canary.pid)
    for bad in ("0", "-1", "1", "abc"):
        make_job(jobs, "J_BAD", bad, os.path.join(tmp, "bad.log"))
        rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_BAD"])
        check("pid=%r -> refused (exit 3), no kill attempted" % bad, rc == 3,
              "rc=%d out=%s" % (rc, (out + err)[:140]))
        check("pid=%r -> record untouched" % bad,
              read_job(jobs, "J_BAD")["status"] == "running")
    check("innocent bystander process survived every bad-pid cancel", alive(canary.pid),
          "canary %s was killed — cancel mass-signalled" % canary.pid)
    check("this selfcheck itself survived", True)

    # job-reap must still be able to close a genuinely dead job THROUGH the new guard, and
    # must still refuse to touch a live one — reap calls cmd_job_set internally.
    print("\nI3. job-reap end-to-end through the guard")
    log_r = os.path.join(tmp, "r.log")
    wpid_r, _ = spawn_wrapper(log_r)
    make_job(jobs, "J_R", wpid_r, log_r)
    jset(jobs, "J_R", "deadline=1")                     # long past deadline, but ALIVE
    rc, out, _ = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap leaves a live past-deadline job alone", "J_R" not in out, out[:160])
    check("still running", read_job(jobs, "J_R")["status"] == "running")
    os.kill(wpid_r, 9)
    time.sleep(0.8)
    rc, out, _ = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap closes it once the pid is dead", read_job(jobs, "J_R")["status"] == "orphaned",
          read_job(jobs, "J_R")["status"])

    print("\nI4. terminal-statuses is the fleet's single definition")
    rc, out, _ = run([sys.executable, MJ, "terminal-statuses"])
    terms = out.split()
    check("exit 0 and non-empty", rc == 0 and terms, out[:80])
    for st in ("done", "failed", "timeout", "orphaned", "cancelled"):
        check("includes %s" % st, st in terms, out[:80])
    check("includes the words the fleet actually improvised (aborted/superseded)",
          "aborted" in terms and "superseded" in terms, out[:80])

    # ------------------------------------------------- J: duplicate-dispatch warning
    print("\nJ. job-find-dup — the observable signature of a duplicate dispatch")
    log_j = os.path.join(tmp, "j.log")
    wpid_j, _ = spawn_wrapper(log_j)
    make_job(jobs, "J_J", wpid_j, log_j, prompt="build the ceiling mechanism", to="Taylor")
    rc, out, _ = run([sys.executable, MJ, "job-find-dup", jobs, "Taylor",
                      "build the ceiling mechanism"])
    check("identical prompt + live pid -> exit 0 and names the job", rc == 0 and "J_J" in out,
          "rc=%d out=%s" % (rc, out[:120]))
    rc, _, _ = run([sys.executable, MJ, "job-find-dup", jobs, "Taylor", "a different task"])
    check("different prompt -> exit 1 (no crying wolf)", rc == 1, "rc=%d" % rc)
    rc, _, _ = run([sys.executable, MJ, "job-find-dup", jobs, "Winston",
                    "build the ceiling mechanism"])
    check("different agent -> exit 1", rc == 1, "rc=%d" % rc)
    os.kill(wpid_j, 9)
    time.sleep(0.6)
    rc, _, _ = run([sys.executable, MJ, "job-find-dup", jobs, "Taylor",
                    "build the ceiling mechanism"])
    check("dead pid -> exit 1 (a finished job is not a collision)", rc == 1, "rc=%d" % rc)

    # ------------------------------------------------- K: real dispatch.sh syntax intact
    print("\nK. touched scripts still parse")
    for f in ("bin/dispatch.sh", "bin/jobs.sh", "bin/watchdog.sh", "hooks/session_start.sh",
              "bin/kb_nightly.sh", "bin/fleet_housekeeping.sh"):
        rc, _, err = run(["bash", "-n", os.path.join(ROOT, f)])
        check("bash -n %s" % f, rc == 0, err[:200])
    rc, _, err = run([sys.executable, "-c",
                      "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)",
                      MJ])
    check("py_compile bin/mike_json.py", rc == 0, err[:200])

    cleanup()
    print("\n%d/%d PASS%s" % (PASS, PASS + FAIL, "" if not FAIL else "  — %d FAILED" % FAIL))
    return 1 if FAIL else 0


def _descendants_of(pid):
    """Local PPid walk, used only to assert that an orphan is genuinely invisible to one."""
    out = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        try:
            with open("/proc/%s/status" % entry, encoding="utf-8") as f:
                for line in f:
                    if line.startswith("PPid:") and int(line.split()[1]) == int(pid):
                        out.append(int(entry))
                    if line.startswith("PPid:"):
                        break
        except Exception:
            continue
    return out


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        cleanup()
