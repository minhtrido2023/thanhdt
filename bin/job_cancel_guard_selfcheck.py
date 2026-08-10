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


def holders_of(path):
    """Pids whose fd1 or fd2 IS `path` — the same question mike_json._pids_holding asks,
    reimplemented here so the assertions do not inherit the bug they are checking for."""
    out = []
    for entry in os.listdir("/proc"):
        if not entry.isdigit():
            continue
        for fd in ("1", "2"):
            try:
                if os.readlink("/proc/%s/fd/%s" % (entry, fd)) == path:
                    out.append(int(entry))
                    break
            except Exception:
                continue
    return out


def owner_env(claim_job_id):
    """The environment dispatch.sh's JSET sets — forged here by a process that is NOT in the
    dispatcher's tree, which is the whole point of these cases."""
    e = dict(os.environ)
    e["MIKE_JOB_OWNER"] = str(claim_job_id)
    return e


def spawn_sync_worker(logfile, jobs_dir, job_id):
    """Reproduce dispatch.sh's SYNCHRONOUS process shape, which is the fleet's default and
    has none of the handles the --bg shape has:

        _hb_aware_timeout "${CLI_ARGV[@]}" 2>"$logfile.err" | tee "$logfile"

    bash runs the left side of a pipeline in a SUBSHELL, so the worker's parent is that
    subshell (not the script), its stdout is a PIPE into tee, and only its stderr is a real
    file. Nothing is written to the record's `pid` field at all. Returns (dispatcher_pid,
    worker_pid) where dispatcher_pid is `$$` — what dispatch.sh stores as dispatcher_pid.

    The dispatcher then sits in a command loop so that a later case can make it close its
    own record from INSIDE its own process tree (see sync_self_close)."""
    pidf, cmdf, rcf, outf = (logfile + s for s in (".workerpid", ".cmd", ".setrc", ".setout"))
    script = """
{ setsid sleep 300 2>%(err)s & echo $! > %(pidf)s; sleep 300; } | tee %(log)s >/dev/null &
while :; do
  if [ -s %(cmdf)s ]; then
    _claim="$(head -1 %(cmdf)s)"; _args="$(tail -1 %(cmdf)s)"; rm -f %(cmdf)s
    MIKE_JOB_OWNER="$_claim" python3 %(mj)s job-set %(jobs)s %(job)s $_args >%(outf)s 2>&1
    echo $? > %(rcf)s
  fi
  sleep 0.1
done
""" % dict(err=shlex.quote(logfile + ".err"), pidf=shlex.quote(pidf),
           log=shlex.quote(logfile), cmdf=shlex.quote(cmdf), rcf=shlex.quote(rcf),
           outf=shlex.quote(outf), mj=shlex.quote(MJ), jobs=shlex.quote(jobs_dir),
           job=shlex.quote(job_id))
    p = subprocess.Popen(["bash", "-c", script],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    SPAWNED.append(p.pid)
    worker = None
    for _ in range(60):
        try:
            with open(pidf, encoding="utf-8") as f:
                worker = int(f.read().strip())
            break
        except Exception:
            time.sleep(0.1)
    if worker:
        SPAWNED.append(worker)
    time.sleep(0.3)
    return p.pid, worker


def sync_self_close(jobs_dir, job_id, logfile, status, claim=None):
    """Ask the dispatcher spawned by spawn_sync_worker to close its own record — the write
    then really does come from inside that dispatch.sh's process tree, which is the only
    thing that makes it legitimate. `claim` forges MIKE_JOB_OWNER when it is not job_id."""
    rcf, outf = logfile + ".setrc", logfile + ".setout"
    for f in (rcf, outf):
        try:
            os.remove(f)
        except Exception:
            pass
    with open(logfile + ".cmd", "w", encoding="utf-8") as f:
        f.write("%s\nstatus=%s\n" % (claim or job_id, status))
    for _ in range(80):
        try:
            with open(rcf, encoding="utf-8") as f:
                rc = int(f.read().strip())
            with open(outf, encoding="utf-8") as f:
                return rc, "", f.read()
        except Exception:
            time.sleep(0.1)
    return None, "", "dispatcher never answered"


SANDBOX_STUBS = ("notify.sh", "notify_thread.sh", "append_event.sh", "consolidate.sh")


def build_sandbox(tmp):
    """A throwaway ROOT that runs the REAL bin/dispatch.sh against a stub CLI.

    Same recipe as bin/dispatch_discord_topic_selfcheck.sh, including its hard-won rule:
    the stubs must `rm -f` the symlink FIRST. Writing through a symlink into bin/ truncated
    four live fleet scripts on 2026-08-02."""
    mk = os.path.join(tmp, "mk")
    for d in ("bin", "kb", "bus/jobs", "logs", "state/circuit", "agents/Taylor", "agents/Mike"):
        os.makedirs(os.path.join(mk, d), exist_ok=True)
    for name in os.listdir(os.path.join(ROOT, "bin")):
        src = os.path.join(ROOT, "bin", name)
        if os.path.isfile(src):
            os.symlink(src, os.path.join(mk, "bin", name))
    with open(os.path.join(ROOT, "kb", "cli_providers.json"), encoding="utf-8") as f:
        reg = f.read()
    with open(os.path.join(mk, "kb", "cli_providers.json"), "w", encoding="utf-8") as f:
        f.write(reg)
    for name in SANDBOX_STUBS:
        p = os.path.join(mk, "bin", name)
        os.remove(p)                       # drop the symlink; NEVER write through it
        assert not os.path.exists(p) and not os.path.islink(p), p
        with open(p, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(p, 0o755)
    # Last fence: the real scripts must be untouched (this is the 08-02 failure mode).
    for name in SANDBOX_STUBS:
        real = os.path.join(ROOT, "bin", name)
        assert os.path.getsize(real) > 200, "STUB LEAKED INTO %s — git checkout it NOW" % real
    stub = os.path.join(tmp, "claude_stub.sh")
    with open(stub, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\necho '[claude-stub] working'\nexec sleep 300\n")
    os.chmod(stub, 0o755)
    return mk, stub


def run_sync_kill_trap(tmp):
    """END-TO-END on the real bin/dispatch.sh: start a SYNC dispatch, let the worker come
    up, then SIGTERM dispatch.sh's whole process group — exactly what the caller's Bash tool
    does on its 2-minute timeout (incident 2026-07-09, DollarBill_20260709_125326).

    The worker is setsid'd, so it SURVIVES that group kill. _sync_killed_guard must stop it
    before writing the record: a `failed` stamp over a worker that is still editing the repo
    is the 2026-08-09 lie, just reached by a different door.

    Returns (dispatcher_rc, worker_pid, final_status)."""
    mk, stub = build_sandbox(tmp)
    env = dict(os.environ)
    env.update({"DISPATCH_CLAUDE_BIN": stub, "DISPATCH_KILL_GRACE_S": "3",
                "DISPATCH_FROM": "Mike", "MIKE_ROOT": mk})
    p = subprocess.Popen(["bash", os.path.join(mk, "bin", "dispatch.sh"), "Taylor", "hello"],
                         cwd=mk, env=env, stdout=subprocess.DEVNULL,
                         stderr=subprocess.PIPE, text=True, start_new_session=True)
    SPAWNED.append(p.pid)
    jobs_dir = os.path.join(mk, "bus", "jobs")
    worker, rec = None, None
    for _ in range(400):                       # up to 40s for the CLI to be spawned
        recs = [f for f in os.listdir(jobs_dir) if f.endswith(".json")]
        if recs:
            rec = os.path.join(jobs_dir, recs[0])
            try:
                with open(rec, encoding="utf-8") as f:
                    lf = json.load(f).get("logfile", "")
                with open(lf + ".workerpid", encoding="utf-8") as f:
                    worker = int(f.read().strip())
                SPAWNED.append(worker)
                break
            except Exception:
                pass
        if p.poll() is not None:
            break
        time.sleep(0.1)
    if worker is None:
        return p.poll(), None, "dispatch never reached the CLI: %s" % (p.stderr.read()[:400],)
    time.sleep(0.3)
    os.killpg(os.getpgid(p.pid), 15)           # the caller's process-group SIGTERM
    try:
        p.wait(timeout=40)
    except Exception:
        pass
    time.sleep(0.5)
    try:
        with open(rec, encoding="utf-8") as f:
            status = json.load(f).get("status")
    except Exception:
        status = None
    return p.returncode, worker, status


def make_job(jobs_dir, job_id, pid, logfile, prompt="do the thing", to="Taylor",
             dispatcher_pid=""):
    rc, _, err = jset(jobs_dir, job_id, "job_id=" + job_id, "from=Mike", "to=" + to,
                      "status=running", "attempt=1", "max_attempts=2",
                      "started_at=1000", "deadline=1600", "logfile=" + logfile,
                      "prompt_summary=" + prompt, "pid=%s" % pid,
                      "dispatcher_pid=%s" % dispatcher_pid)
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
    wpid_r, worker_r = spawn_wrapper(log_r)
    make_job(jobs, "J_R", wpid_r, log_r)
    jset(jobs, "J_R", "deadline=1")                     # long past deadline, but ALIVE
    rc, out, _ = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap leaves a live past-deadline job alone", "J_R" not in out, out[:160])
    check("still running", read_job(jobs, "J_R")["status"] == "running")
    # The wrapper dies but the worker keeps going: 'orphaned' would be the board lying in
    # the OTHER direction — the job is not abandoned, it is running unattended. Before the
    # round-2 fix reap read the recorded pid only and closed the record here.
    os.kill(wpid_r, 9)
    time.sleep(0.8)
    check("setup: wrapper dead, worker alive", not alive(wpid_r) and alive(worker_r))
    rc, out, _ = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap does NOT orphan a job whose worker still lives",
          read_job(jobs, "J_R")["status"] == "running", read_job(jobs, "J_R")["status"])
    os.kill(worker_r, 9)
    time.sleep(0.8)
    rc, out, _ = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap closes it once the whole job is dead",
          read_job(jobs, "J_R")["status"] == "orphaned", read_job(jobs, "J_R")["status"])
    # The reap loop must survive a guarded record: a second job that IS alive must not stop
    # reap from examining and closing a dead one later in the same pass (internal=True).
    log_r2 = os.path.join(tmp, "r2.log")
    wpid_r2, _ = spawn_wrapper(log_r2)
    make_job(jobs, "J_R_LIVE", wpid_r2, log_r2)
    jset(jobs, "J_R_LIVE", "deadline=1")
    make_job(jobs, "J_R_DEAD", 999999, os.path.join(tmp, "r3.log"))
    jset(jobs, "J_R_DEAD", "deadline=1")
    rc, out, _ = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("a live record does not abort the reap pass",
          read_job(jobs, "J_R_DEAD")["status"] == "orphaned",
          read_job(jobs, "J_R_DEAD")["status"])
    check("...and the live one is still untouched",
          read_job(jobs, "J_R_LIVE")["status"] == "running")

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
    # The wrapper dies but the setsid'd worker keeps the logfile — the 08-09 state. The
    # collision is at its MOST dangerous here (a live writer nobody is pointing at), so this
    # is exactly when the warning must still fire. Keying on the recorded pid alone made it
    # go silent (arch-reviewer round 2, finding K1b).
    os.kill(wpid_j, 9)
    time.sleep(0.6)
    worker_j = int(open(log_j + ".workerpid").read().strip())
    check("setup: wrapper dead, worker still holding the logfile",
          not alive(wpid_j) and alive(worker_j))
    rc, out, _ = run([sys.executable, MJ, "job-find-dup", jobs, "Taylor",
                      "build the ceiling mechanism"])
    check("wrapper killed but worker ALIVE -> still exit 0 and names the job",
          rc == 0 and "J_J" in out, "rc=%d out=%s" % (rc, out[:120]))
    os.kill(worker_j, 9)
    time.sleep(0.6)
    rc, _, _ = run([sys.executable, MJ, "job-find-dup", jobs, "Taylor",
                    "build the ceiling mechanism"])
    check("whole job dead -> exit 1 (a finished job is not a collision)", rc == 1, "rc=%d" % rc)

    # ------------------------------------------------------ L: the incident, COMPOSED
    # Cases A and F each passed while the bug was still live, because they were never
    # composed: A stamps while the wrapper is alive, F proves the worker survives the kill.
    # The incident IS the composition — Mike killed first, THEN stamped — and replaying it
    # against the round-1 fix still succeeded (arch-reviewer round 2, killer objection K1).
    print("\nL. COMPOSED REPLAY — the literal 2026-08-09 order: kill wrapper, THEN stamp")
    log_l = os.path.join(tmp, "l.log")
    wpid_l, worker_l = spawn_wrapper(log_l)
    make_job(jobs, "J_L", wpid_l, log_l, prompt="fix executor.py")
    os.kill(wpid_l, 15)                        # step 1: `kill <pid>` (hits only the wrapper)
    time.sleep(1.0)
    check("setup: recorded pid dead, worker ALIVE and still editing",
          not alive(wpid_l) and alive(worker_l))
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_L", "status=failed"])
    check("step 2: job-set status=failed -> REFUSED (exit 3)", rc == 3,
          "rc=%d — the board would be lying again; %s" % (rc, (out + err)[:200]))
    check("record still says running", read_job(jobs, "J_L")["status"] == "running",
          read_job(jobs, "J_L")["status"])
    check("refusal names the live worker, not the dead recorded pid",
          str(worker_l) in err, err[:250])
    for word in ("aborted", "superseded", "killed", "done"):
        rc, _, _ = run([sys.executable, MJ, "job-set", jobs, "J_L", "status=" + word])
        check("improvised status=%s also refused in this state" % word, rc == 3, "rc=%d" % rc)
    # S3: the two-command bypass — "the guard says the pid is alive, so I'll fix the pid".
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_L", "pid=999999"])
    check("rewriting pid= on a live job -> REFUSED", rc == 3, "rc=%d %s" % (rc, (out + err)[:180]))
    check("pid unchanged", str(read_job(jobs, "J_L")["pid"]) == str(wpid_l))
    # cancel is the supported way out of this state, and it must still work.
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_L", "5"])
    check("jobs.sh cancel still closes it properly (exit 0)", rc == 0, (out + err)[:200])
    time.sleep(0.3)
    check("orphaned worker killed", not alive(worker_l))
    check("status=cancelled", read_job(jobs, "J_L")["status"] == "cancelled")

    # S4: the guard's precondition was `status == "running"`, so a record sitting in one of
    # the OTHER live statuses the fix itself blesses was unprotected.
    print("\nL2. the guard covers every LIVE status, not just 'running'")
    log_l2 = os.path.join(tmp, "l2.log")
    wpid_l2, _ = spawn_wrapper(log_l2)
    make_job(jobs, "J_L2", wpid_l2, log_l2)
    rc, _, _ = jset(jobs, "J_L2", "status=retrying")
    check("a live job may move to retrying (allowlist)", rc == 0, "rc=%d" % rc)
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_L2", "status=failed"])
    check("outsider cannot then stamp failed over 'retrying'", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:180]))
    check("record still retrying", read_job(jobs, "J_L2")["status"] == "retrying",
          read_job(jobs, "J_L2")["status"])

    # S2: pid recycling. cancel signalled whatever now owns the recorded pid, with no check
    # that it is this job's process (arch-reviewer measured an unrelated canary SIGKILLed).
    print("\nL3. cancel proves the recorded pid BELONGS to the job before signalling it")
    canary2 = subprocess.Popen(["sleep", "300"], stdout=subprocess.DEVNULL)
    SPAWNED.append(canary2.pid)
    time.sleep(0.3)
    log_l3 = os.path.join(tmp, "l3.log")          # canary holds no job logfile, no job kinship
    make_job(jobs, "J_L3", canary2.pid, log_l3)
    jset(jobs, "J_L3", "started_at=%d" % (int(time.time()) - 86400))   # stale record, day old
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_L3", "5"])
    check("recycled pid -> REFUSED (exit 3), nothing signalled", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("the unrelated process is ALIVE", alive(canary2.pid),
          "canary %s was killed by a cancel that could not prove ownership" % canary2.pid)
    check("record left running (cancel never stamps what it cannot back up)",
          read_job(jobs, "J_L3")["status"] == "running")
    check("refusal points at the --force escape", "--force" in err, err[:250])

    # ------------------------------------------------- M: the SYNC dispatch shape (K1/N2)
    # Everything above models `dispatch.sh --bg`: a record with a pid, a worker whose stdout
    # IS the logfile. The fleet's DEFAULT is the sync path, which has NEITHER:
    #     _hb_aware_timeout "${CLI_ARGV[@]}" 2>"$logfile.err" | tee "$logfile"
    # fd1 of the worker is a PIPE (tee owns the logfile), only fd2 is a real file — and the
    # record carries no pid at all, because `JSET pid=$BASHPID` lives in _bg_wrapper only.
    # So on a sync job the guard had nothing whatsoever to hold on to: no recorded pid to
    # test ancestry against, and _pids_holding(logfile) finding nobody.
    print("\nM. sync dispatch: a job with NO recorded pid is still seen to be alive")
    log_m = os.path.join(tmp, "m.log")
    disp_m, work_m = spawn_sync_worker(log_m, jobs, "J_M")
    make_job(jobs, "J_M", "", log_m, dispatcher_pid=disp_m)   # sync record: pid EMPTY
    check("worker is alive", alive(work_m), "worker=%s" % work_m)
    check("its stdout is a PIPE — nobody's fd1/fd2 is the logfile itself",
          work_m not in holders_of(log_m), "holders=%s" % holders_of(log_m))
    check("but its stderr IS logfile.err — the only handle the guard has",
          work_m in holders_of(log_m + ".err"), "holders=%s" % holders_of(log_m + ".err"))
    rc, out, err = jset(jobs, "J_M", "status=failed")
    check("outsider stamping failed on a live SYNC job -> REFUSED (exit 3)", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("record left running", read_job(jobs, "J_M")["status"] == "running")

    # N2: the dispatcher of a sync job must still close its OWN record. It has no pid on the
    # record, and the worker is its SIBLING (dispatch.sh spawns both), so neither
    # _is_self_or_ancestor nor _writer_belongs_to_job (which only walks UP) sees the kinship.
    # dispatcher_pid + MIKE_JOB_OWNER is that missing evidence — and it is evidence, not a
    # password: every case below forges the env var and still gets refused.
    print("\nN. dispatcher_pid is proof; MIKE_JOB_OWNER only narrows it (never a password)")
    rc, out, err = sync_self_close(jobs, "J_M", log_m, "timeout")
    check("the real dispatcher CAN close its own record from inside its tree", rc == 0,
          "rc=%s %s" % (rc, (out + err)[:250]))
    check("record closed as timeout", read_job(jobs, "J_M")["status"] == "timeout")

    # ADVERSARIAL 1 — a stranger forges MIKE_JOB_OWNER for a job it does not own. The env
    # var is satisfied; /proc is not: the stranger is not inside that dispatch.sh's tree.
    # This is the 2026-08-09 improvisation, typed in a separate Bash tool call.
    log_n = os.path.join(tmp, "n.log")
    disp_n, work_n = spawn_sync_worker(log_n, jobs, "J_N")
    make_job(jobs, "J_N", "", log_n, dispatcher_pid=disp_n)
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_N", "status=failed"],
                       env=owner_env("J_N"))
    check("forged MIKE_JOB_OWNER from outside the dispatcher tree -> REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:250]))
    check("record still running after the forgery", read_job(jobs, "J_N")["status"] == "running")
    check("the worker it lied about is still alive", alive(work_n), "worker=%s" % work_n)

    # ADVERSARIAL 2 — the 2-command bypass: point dispatcher_pid at your own shell first,
    # then stamp. Rewriting it on a live job is refused for the same reason `pid` is.
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_N",
                        "dispatcher_pid=%d" % os.getpid()], env=owner_env("J_N"))
    check("rewriting dispatcher_pid on a live job -> REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:250]))
    check("dispatcher_pid unchanged", str(read_job(jobs, "J_N")["dispatcher_pid"]) == str(disp_n),
          read_job(jobs, "J_N").get("dispatcher_pid"))
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_N", "status=failed"],
                       env=owner_env("J_N"))
    check("...so the follow-up stamp is still REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:250]))

    # ADVERSARIAL 3 — right tree, WRONG job id: a dispatcher may close only the record it
    # was given, not any live record its tree happens to be an ancestor of.
    rc, out, err = sync_self_close(jobs, "J_N", log_n, "failed", claim="J_SOMETHING_ELSE")
    check("owner env naming a DIFFERENT job -> REFUSED", rc == 3,
          "rc=%s %s" % (rc, (out + err)[:250]))
    check("record still running", read_job(jobs, "J_N")["status"] == "running")

    # ADVERSARIAL 4 — the LEGACY-RECORD bypass, and the reason dispatcher_pid is guarded
    # more strictly than pid. Every job record already on the board predates this field, so
    # if a FIRST write of dispatcher_pid were allowed on a live record, the guard would ship
    # with a 2-command hole on exactly the records it exists to protect: claim the record as
    # yours, then stamp. (This case was written expecting a refusal and FAILED — rc=0 — on
    # the first run; the strict rule is its fix, not a rationalisation of it.)
    log_n2 = os.path.join(tmp, "n2.log")
    wrap_n2, work_n2 = spawn_wrapper(log_n2)
    time.sleep(0.4)
    make_job(jobs, "J_N2", wrap_n2, log_n2)               # legacy shape: NO dispatcher_pid
    check("legacy record really has no dispatcher_pid",
          not read_job(jobs, "J_N2").get("dispatcher_pid"),
          read_job(jobs, "J_N2").get("dispatcher_pid"))
    os.kill(wrap_n2, 9)                                   # exactly Mike's `kill <pid>`
    time.sleep(0.5)
    check("orphaned worker survived the kill", alive(work_n2), "worker=%s" % work_n2)
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_N2",
                        "dispatcher_pid=%d" % os.getpid()], env=owner_env("J_N2"))
    check("claiming an unowned live record as your own -> REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:250]))
    check("no dispatcher_pid was written", not read_job(jobs, "J_N2").get("dispatcher_pid"),
          read_job(jobs, "J_N2").get("dispatcher_pid"))
    rc, out, err = run([sys.executable, MJ, "job-set", jobs, "J_N2", "status=failed"],
                       env=owner_env("J_N2"))
    check("08-09 replay on a legacy record, forged env -> still REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:250]))
    check("record still running", read_job(jobs, "J_N2")["status"] == "running")

    # Regression: the env var must not disturb ordinary, unguarded writes.
    rc, _, err = run([sys.executable, MJ, "job-set", jobs, "J_N", "note=progress"],
                     env=owner_env("J_N"))
    check("non-closing field update on a live job still allowed", rc == 0, err[:200])
    check("and it actually landed", read_job(jobs, "J_N").get("note") == "progress")

    # ------------------------------------------------- O: the sync KILL trap (E2E, real script)
    # dispatch.sh's sync path traps TERM so a killed dispatcher does not leave the record at
    # running forever (incident 2026-07-09). But the worker is setsid'd: it SURVIVES the
    # caller's process-group kill. Stamping failed while it keeps editing the repo is exactly
    # the record that made the board lie on 08-09 — so the trap must STOP it, then stamp.
    print("\nO. dispatch.sh sync trap kills the worker BEFORE it closes the record")
    rc_o, worker_o, status_o = run_sync_kill_trap(tmp)
    check("trap fired and closed the record", status_o in ("failed", None) and status_o == "failed",
          "status=%s" % status_o)
    check("the setsid'd worker is DEAD, not orphaned into the repo", worker_o is not None
          and not alive(worker_o), "worker=%s" % worker_o)

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
