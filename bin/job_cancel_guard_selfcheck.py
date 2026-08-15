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
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MJ = os.path.join(ROOT, "bin", "mike_json.py")
JOBS_SH = os.path.join(ROOT, "bin", "jobs.sh")

PASS = 0
FAIL = 0
SPAWNED = []
# Sandboxes this run created, removed by cleanup() once the workers are dead (round 6, NICE 9).
TMPDIRS = []
# The job record left behind by the last real-dispatch.sh E2E, so a case can assert on what
# the REAL script wrote (the evidence pin) instead of on a hand-built fixture.
LAST_E2E_RECORD = {}


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
    # `nest` forks one extra real process per level (no `exec` — that would reuse the pid and
    # add no depth), so a case can ask how far inside the dispatcher tree the grant reaches.
    nestf = logfile + ".nest"
    with open(nestf, "w", encoding="utf-8") as f:
        f.write("#!/usr/bin/env bash\n"
                "d=\"$1\"; shift\n"
                "if [ \"$d\" -le 0 ]; then python3 %s job-set %s %s \"$@\"; exit $?; fi\n"
                "bash %s $((d - 1)) \"$@\"\n"
                % (shlex.quote(MJ), shlex.quote(jobs_dir), shlex.quote(job_id),
                   shlex.quote(nestf)))
    script = """
{ setsid sleep 300 2>%(err)s & echo $! > %(pidf)s; sleep 300; } | tee %(log)s >/dev/null &
while :; do
  if [ -s %(cmdf)s ]; then
    _claim="$(sed -n 1p %(cmdf)s)"; _args="$(sed -n 2p %(cmdf)s)"
    _nest="$(sed -n 3p %(cmdf)s)"; rm -f %(cmdf)s
    MIKE_JOB_OWNER="$_claim" bash %(nestf)s "$_nest" $_args >%(outf)s 2>&1
    echo $? > %(rcf)s
  fi
  sleep 0.1
done
""" % dict(err=shlex.quote(logfile + ".err"), pidf=shlex.quote(pidf),
           log=shlex.quote(logfile), cmdf=shlex.quote(cmdf), rcf=shlex.quote(rcf),
           outf=shlex.quote(outf), nestf=shlex.quote(nestf))
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


def sync_self_close(jobs_dir, job_id, logfile, status, claim=None, nest=0):
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
        f.write("%s\nstatus=%s\n%d\n" % (claim or job_id, status, nest))
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


def run_sync_kill_trap(tmp, break_verifier=False, break_cancel=False):
    """END-TO-END on the real bin/dispatch.sh: start a SYNC dispatch, let the worker come
    up, then SIGTERM dispatch.sh's whole process group — exactly what the caller's Bash tool
    does on its 2-minute timeout (incident 2026-07-09, DollarBill_20260709_125326).

    The worker is setsid'd, so it SURVIVES that group kill. _sync_killed_guard must stop it
    before writing the record: a `failed` stamp over a worker that is still editing the repo
    is the 2026-08-09 lie, just reached by a different door.

    `break_verifier` makes the legacy fallback `job-live-pids` fail; `break_cancel` makes the
    primary `job-cancel` primitive fail. The record is still created normally. This lets R5
    prove both sides of the post-fix contract: a broken fallback does not matter when the
    safe cancel primitive succeeds, while both paths broken must leave the record running.

    Returns (dispatcher_rc, worker_pid, final_status, dispatcher_stderr)."""
    mk, stub = build_sandbox(tmp)
    if break_verifier or break_cancel:
        shim = os.path.join(mk, "bin", "mike_json.py")
        os.remove(shim)                    # drop the symlink; NEVER write through it
        assert not os.path.exists(shim) and not os.path.islink(shim), shim
        with open(shim, "w", encoding="utf-8") as f:
            f.write("#!/usr/bin/env python3\n"
                    "import sys, runpy\n"
                    "REAL = %s\n"
                    "BREAK_VERIFIER = %r\n"
                    "BREAK_CANCEL = %r\n"
                    "if len(sys.argv) > 1 and ((sys.argv[1] == 'job-live-pids' and BREAK_VERIFIER)\n"
                    "                         or (sys.argv[1] == 'job-cancel' and BREAK_CANCEL)):\n"
                    "    sys.stderr.write('selfcheck: cancellation verifier deliberately broken\\n')\n"
                    "    sys.exit(4)\n"
                    "sys.argv[0] = REAL\n"
                    "runpy.run_path(REAL, run_name='__main__')\n"
                    % (repr(MJ), break_verifier, break_cancel))
        os.chmod(shim, 0o755)
        assert os.path.getsize(MJ) > 200, "SHIM LEAKED INTO %s — git checkout it NOW" % MJ
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
        return (p.poll(), None,
                "dispatch never reached the CLI: %s" % (p.stderr.read()[:400],), "")
    time.sleep(0.3)
    os.killpg(os.getpgid(p.pid), 15)           # the caller's process-group SIGTERM
    try:
        p.wait(timeout=40)
    except Exception:
        pass
    time.sleep(0.5)
    try:
        derr = p.stderr.read()
    except Exception:
        derr = ""
    try:
        with open(rec, encoding="utf-8") as f:
            final = json.load(f)
        status = final.get("status")
    except Exception:
        status, final = None, {}
    LAST_E2E_RECORD.clear()
    LAST_E2E_RECORD.update(final)
    return p.returncode, worker, status, derr


def fd_links_of(pid):
    """The raw /proc/<pid>/fd/{1,2} readlink strings — used to ASSERT that the kernel really
    did rewrite them ('(deleted)', or the new name after a rename). Without this the R-series
    would be testing a scenario that may not even be reproducible on this kernel."""
    out = []
    for fd in ("1", "2"):
        try:
            out.append(os.readlink("/proc/%d/fd/%s" % (int(pid), fd)))
        except Exception:
            continue
    return out


def run_sync_kill_trap_verifier_broken(tmp):
    """K3: both cancellation verification paths fail.
    Returns (dispatcher_rc, final_status, dispatcher_stderr)."""
    sub = os.path.join(tmp, "r5")
    os.makedirs(sub, exist_ok=True)
    rc, _worker, status, derr = run_sync_kill_trap(
        sub, break_verifier=True, break_cancel=True)
    return rc, status, derr


def _record_pin_of(obj):
    """The pin fields as the guard reads them — empty when the record carries no identity."""
    return {k: obj.get(k) for k in ("logfile_ino", "logfile_err_ino") if obj.get(k)}


def pin_pairs(logfile, create=True):
    """The (dev,ino) pins dispatch.sh stamps on every record it creates, as job-set pairs.

    Fixtures must carry them for the same reason `create_log=True` exists above: since round 6
    a record with NO pin cannot support a DEAD verdict at all (an unidentified file at the
    path may be a decoy), so a fixture without a pin silently tests the UNKNOWN path
    everywhere. Real records are pinned by dispatch.sh before any worker exists — `pin=False`
    is for the cases that test an UNPINNED record on purpose (legacy records, round 6 K1)."""
    out = []
    for path, field in ((logfile, "logfile_ino"), (logfile + ".err", "logfile_err_ino")):
        try:
            if create:
                open(path, "a").close()
            st = os.stat(path)
        except Exception:
            continue
        out.append("%s=%d:%d" % (field, st.st_dev, st.st_ino))
    return out


def make_job(jobs_dir, job_id, pid, logfile, prompt="do the thing", to="Taylor",
             dispatcher_pid="", create_log=True, pin=True):
    # A real dispatch's logfile EXISTS while the job runs, so the fixture must create it:
    # since round 4 an absent logfile means "liveness evidence gone -> UNKNOWN -> guard ON"
    # (_logfile_evidence_missing), and a fixture that skipped it would be testing the blind
    # path everywhere by accident. `create_log=False` is for the cases that test blindness
    # ON PURPOSE.
    if create_log and logfile:
        try:
            open(logfile, "a").close()
        except Exception:
            pass
    rc, _, err = jset(jobs_dir, job_id, "job_id=" + job_id, "from=Mike", "to=" + to,
                      "status=running", "attempt=1", "max_attempts=2",
                      "started_at=1000", "deadline=1600", "logfile=" + logfile,
                      "prompt_summary=" + prompt, "pid=%s" % pid,
                      "dispatcher_pid=%s" % dispatcher_pid,
                      *(pin_pairs(logfile, create=create_log) if pin and logfile else []))
    assert rc == 0, err
    return job_id


def hb_sandbox(tmp):
    """A throwaway ROOT whose `bus/inbox` the guard will actually read.

    _hb_age derives the inbox from mike_json.py's own location, so pointing it at a sandbox
    is done by INVOKING it through a symlink inside one (abspath does not resolve symlinks).
    Deliberately not an env override: a var that redirects where the heartbeat is looked for
    would be K2 with a nicer name — anyone could turn a fresh heartbeat into 'never seen'.

    Returns (root, mike_json_path, jobs_dir)."""
    r = os.path.join(tmp, "hbroot")
    for d in ("bin", "bus/inbox", "bus/jobs"):
        os.makedirs(os.path.join(r, d), exist_ok=True)
    link = os.path.join(r, "bin", "mike_json.py")
    if not os.path.exists(link):
        os.symlink(MJ, link)
    return r, link, os.path.join(r, "bus", "jobs")


def write_hb(root, agent, job_id, age_s):
    """Append one AGENT-written heartbeat for `job_id`, `age_s` seconds old. The payload shape
    matters: _hb_age(agent_only=True) skips the watcher's own still_running pings."""
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() - age_s))
    with open(os.path.join(root, "bus", "inbox", agent + ".jsonl"), "a",
              encoding="utf-8") as f:
        f.write(json.dumps({"ts": ts, "agent_id": agent, "event_type": "heartbeat",
                            "topic": job_id, "trace_id": job_id,
                            "payload": {"status": "in_progress", "note": "selfcheck"}}) + "\n")


def put_record(jobs_dir, job_id, **fields):
    """Write a job record DIRECTLY, bypassing job-set. Needed because the round-5 fixtures set
    `deadline` and `started_at` to specific ages, and those are guarded fields now — the guard
    would (correctly) refuse the setup itself."""
    obj = {"job_id": job_id, "from": "Mike", "to": "Taylor", "status": "running",
           "attempt": "1", "max_attempts": "2", "prompt_summary": "do the thing"}
    pin = fields.pop("pin", True)
    obj.update({k: str(v) for k, v in fields.items()})
    # Same faithfulness rule as make_job: a real record carries dispatch.sh's pin. Pin only
    # what is already on disk — these fixtures create (or deliberately omit) their own files.
    if pin and obj.get("logfile"):
        obj.update(dict(p.split("=", 1) for p in pin_pairs(obj["logfile"], create=False)))
    with open(os.path.join(jobs_dir, job_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(obj, f)
    return job_id


def cleanup():
    for pid in SPAWNED:
        for sig in (15, 9):
            try:
                os.kill(pid, sig)
            except Exception:
                pass
    # And the sandbox itself. Killing the workers but leaving the tmpdir behind had quietly
    # accumulated 110 `/tmp/jobguard_*` dirs / 57MB by round 6 — every run of a check that
    # exists to keep the fleet honest leaking a little more disk (round 6, NICE 9). Removed
    # only AFTER the workers are dead, so nothing is still writing into it.
    for d in TMPDIRS:
        shutil.rmtree(d, ignore_errors=True)


def main():
    tmp = tempfile.mkdtemp(prefix="jobguard_")
    TMPDIRS.append(tmp)
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
    # A pid-less SYNC record with nothing of it alive USED to be refused here ("cannot prove
    # it killed anything"), and that refusal was itself the bug: reap skipped the record as
    # live and job-set refused to close it, so nothing could ever close it except the --force
    # write this guard exists to prevent (round 3, O3). The new contract is narrower and
    # honest — "no pid" is not the question, "is anything of this job alive" is. Nothing
    # alive: close it and SAY that is why. Something alive: kill, verify, then close (P4).
    # And "nothing alive" itself has a precondition (round 4, K2): the logfile must still BE
    # there, because with it gone the query returns empty regardless. So this case creates the
    # logfile — a sync record whose log is missing is the R-series case below, and it refuses.
    log_i = os.path.join(tmp, "i.log")
    open(log_i, "w").close()
    make_job(jobs, "J_I", "", log_i)          # sync dispatch — no pid recorded
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_I"])
    check("no pid + logfile present + nothing alive -> closes the record (exit 0)", rc == 0,
          "rc=%d %s" % (rc, (out + err)[:220]))
    check("no pid -> status=cancelled", read_job(jobs, "J_I")["status"] == "cancelled",
          read_job(jobs, "J_I")["status"])
    check("no pid -> the summary says it closed a DEAD job, not a killed one",
          "no process is holding it" in (read_job(jobs, "J_I").get("result_summary") or ""),
          read_job(jobs, "J_I").get("result_summary"))
    # ...and it must NOT claim that on a record whose worker is still alive: same shape, one
    # live process, and the close has to go through kill+verify instead (asserted in P4).
    log_i0 = os.path.join(tmp, "i0.log")
    _, work_i0 = spawn_wrapper(log_i0)
    time.sleep(0.4)
    make_job(jobs, "J_I0", "", log_i0)        # sync-shaped: no pid, but a live logfile holder
    check("live sync worker is running", alive(work_i0), "worker=%s" % work_i0)
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_I0", "5"])
    check("no pid + something ALIVE -> killed and verified, not silently closed", rc == 0,
          "rc=%d %s" % (rc, (out + err)[:220]))
    check("that worker is dead", not alive(work_i0), "worker=%s" % work_i0)
    check("and the summary says it KILLED something",
          "killed and verified dead" in (read_job(jobs, "J_I0").get("result_summary") or ""),
          read_job(jobs, "J_I0").get("result_summary"))

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

    # ---------------------------------------- P: the EVIDENCE is guarded, not just `status`
    # Round 3's audit walked past the round-2 fix twice, both times in two commands, both
    # times rc=0 with the worker alive. Neither needed --force, and neither touched a field
    # anyone thought of as protected. The guard reads pid/dispatcher_pid/logfile to decide
    # whether a job is alive; whoever can edit those can decide the answer.
    print("\nP. editing the liveness EVIDENCE needs the same proof as closing the record")

    # P1 (round 3, O1) — logfile= is the only evidence left once the wrapper is dead, and it
    # was writable. Point it somewhere empty and the job looks finished.
    log_p1 = os.path.join(tmp, "p1.log")
    wrap_p1, work_p1 = spawn_wrapper(log_p1)
    time.sleep(0.4)
    make_job(jobs, "J_P1", wrap_p1, log_p1)
    os.kill(wrap_p1, 9)                                   # the 08-09 `kill <pid>`
    time.sleep(0.5)
    check("orphan alive, so a plain stamp is refused", alive(work_p1)
          and jset(jobs, "J_P1", "status=failed")[0] == 3, "worker=%s" % work_p1)
    rc, out, err = jset(jobs, "J_P1", "logfile=" + os.path.join(tmp, "nowhere.log"))
    check("repointing logfile= at an empty path -> REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:220]))
    check("logfile unchanged", read_job(jobs, "J_P1")["logfile"] == log_p1)
    rc, _, _ = jset(jobs, "J_P1", "status=failed")
    check("...so the follow-up stamp is still REFUSED", rc == 3, "rc=%d" % rc)
    check("record still running", read_job(jobs, "J_P1")["status"] == "running")

    # P2 (round 3, O2) — the same hole on the DEFAULT dispatch mode, and worse: a sync record
    # has no pid to rewrite, so a plain FIRST write of pid= handed the attacker the guard's
    # own `_is_self_or_ancestor` short-circuit. This is the live-worker twin of case E, whose
    # absence was the reason nobody noticed (E runs on a job with no live process at all, so
    # the guard never engages there).
    log_p2 = os.path.join(tmp, "p2.log")
    disp_p2, work_p2 = spawn_sync_worker(log_p2, jobs, "J_P2")
    make_job(jobs, "J_P2", "", log_p2, dispatcher_pid=disp_p2)
    check("sync record really has no pid", not read_job(jobs, "J_P2").get("pid"),
          read_job(jobs, "J_P2").get("pid"))
    rc, out, err = jset(jobs, "J_P2", "pid=%d" % os.getpid())
    check("writing your OWN pid onto a live sync record -> REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:220]))
    check("no pid was written", not read_job(jobs, "J_P2").get("pid"),
          read_job(jobs, "J_P2").get("pid"))
    rc, _, _ = jset(jobs, "J_P2", "status=failed")
    check("...so the follow-up stamp is still REFUSED", rc == 3, "rc=%d" % rc)
    check("the refusal no longer invites you to supply a pid",
          "_bg_wrapper" not in jset(jobs, "J_P2", "status=failed")[2], "")

    # P3 — the legitimate late pid= write must survive all of the above: _bg_wrapper stamps
    # its own pid onto a record that has none, BEFORE it spawns anything. Nothing is alive
    # yet, so nothing is being asserted over a running worker.
    log_p3 = os.path.join(tmp, "p3.log")
    make_job(jobs, "J_P3", "", log_p3, dispatcher_pid=os.getpid())
    rc, _, err = jset(jobs, "J_P3", "pid=%d" % os.getpid())
    check("wrapper's late pid= on a record with NO live process still allowed", rc == 0,
          err[:200])
    check("and it landed", str(read_job(jobs, "J_P3")["pid"]) == str(os.getpid()))

    # P4 (round 3, O3) — K1 taught job-set to see the sync worker; cancel had to learn it
    # too, or such a record becomes unclosable by ANY command (cancel refused "no pid", reap
    # skipped it as live, job-set refused) and the only exit left was the --force write this
    # guard exists to prevent.
    print("\nP4. a SYNC job still has a supported kill+verify+close path")
    rc, out, err = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap leaves the live sync job alone",
          read_job(jobs, "J_P2")["status"] == "running", read_job(jobs, "J_P2")["status"])
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_P2", "5"])
    check("jobs.sh cancel closes a sync job (exit 0)", rc == 0,
          "rc=%d %s" % (rc, (out + err)[:220]))
    check("its worker is dead", not alive(work_p2), "worker=%s" % work_p2)
    check("record cancelled", read_job(jobs, "J_P2")["status"] == "cancelled")

    # P5 (round 3, O5) — the dispatcher grant must not leak DOWNWARD through nested
    # dispatches. Peer dispatch is routine, so agent B runs inside agent A's dispatcher tree;
    # B must not be able to close A's live job just by being deep in that tree.
    rc, out, err = sync_self_close(jobs, "J_N", log_n, "failed", nest=3)
    check("a process buried deeper in the dispatcher tree -> REFUSED", rc == 3,
          "rc=%s %s" % (rc, (out + err)[:220]))
    check("record still running", read_job(jobs, "J_N")["status"] == "running")

    # ------------------------------------- R (round 4): the premises that are NOT record fields
    # Rounds 2-4 kept hardening FIELDS, and the audit kept finding the answer somewhere else.
    # `_job_live_pids` rests on two things no field allowlist can reach: the logfile's presence
    # on disk, and the record file's parseability. Each was a one-command bypass, and neither
    # command is a job-set — so the guard never even saw it happen.
    print("\nR. liveness evidence that lives OUTSIDE the record (round 4 killers)")

    # R1 (K1) — rm the logfile. /proc/<pid>/fd/2 then reads "<path> (deleted)", the old exact
    # string compare missed it, live==[] and the next stamp landed rc=0 over a live worker.
    log_r1 = os.path.join(tmp, "r1.log")
    disp_r1, work_r1 = spawn_sync_worker(log_r1, jobs, "J_R1")
    make_job(jobs, "J_R1", "", log_r1, dispatcher_pid=disp_r1)
    check("sync worker alive and holding its .err", alive(work_r1)
          and work_r1 in holders_of(log_r1 + ".err"), "worker=%s" % work_r1)
    check("baseline: stamp refused while the log exists", jset(jobs, "J_R1", "status=failed")[0] == 3)
    for f in (log_r1 + ".err", log_r1):                   # not a job-set: guard never sees it
        if os.path.exists(f):
            os.remove(f)
    check("the fd now reads '(deleted)', i.e. the exact-string match is defeated",
          any(l.startswith(log_r1 + ".err") and l.endswith("(deleted)")
              for l in fd_links_of(work_r1)),
          "worker=%s links=%s" % (work_r1, fd_links_of(work_r1)))
    check("worker still alive after the unlink", alive(work_r1), "worker=%s" % work_r1)
    rc, out, err = jset(jobs, "J_R1", "status=failed")
    check("unlinked logfile -> stamp STILL REFUSED (inode match survives rm)", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:260]))
    check("record still running", read_job(jobs, "J_R1")["status"] == "running")
    # ...and cancel, which FINDS the worker here (the inode match survives rm), must do both
    # halves of its job. This case used to assert rc=3 + 'still running' — enshrining round 7's
    # K2: cancel killed the tree and was then refused the status write, leaving the board
    # claiming `running` about a process it had just killed. Killing is not the hard part;
    # telling the truth about it afterwards is.
    rc_r1, out_r1, err_r1 = run([sys.executable, MJ, "job-cancel", jobs, "J_R1", "2"])
    time.sleep(0.4)
    check("cancel FINDS the worker through the deleted logfile and closes properly",
          rc_r1 == 0, "rc=%d %s" % (rc_r1, (out_r1 + err_r1)[:200]))
    check("the worker it reported killing really is dead", not alive(work_r1),
          "worker=%s" % work_r1)
    check("and the record says cancelled — never 'dead process, board says running'",
          read_job(jobs, "J_R1")["status"] == "cancelled",
          read_job(jobs, "J_R1")["status"])

    # R2 (K1, the half rm does not cover) — RENAME. The old name is gone, so there is no inode
    # left to compare against: _pids_holding genuinely cannot answer. That is the case the
    # "logfile absent -> UNKNOWN, not dead" term exists for.
    log_r2 = os.path.join(tmp, "r2.log")
    disp_r2, work_r2 = spawn_sync_worker(log_r2, jobs, "J_R2")
    make_job(jobs, "J_R2", "", log_r2, dispatcher_pid=disp_r2)
    check("second sync worker alive", alive(work_r2), "worker=%s" % work_r2)
    os.rename(log_r2 + ".err", os.path.join(tmp, "moved_away.err"))
    if os.path.exists(log_r2):
        os.rename(log_r2, os.path.join(tmp, "moved_away.log"))
    # State the premise the way _pids_holding asks it, not by pinning one pid's fd order: after
    # the rename NOTHING resolves the recorded name any more — no inode to compare (the name is
    # gone) and no string to match (the fd reads the new name). That is what makes this the
    # half `rm` does not cover, and it is why the UNKNOWN term has to exist at all.
    check("after the rename, nothing resolves the RECORDED logfile name any more",
          not holders_of(log_r2 + ".err") and not holders_of(log_r2),
          "worker=%s links=%s holders=%s" % (work_r2, fd_links_of(work_r2),
                                             holders_of(log_r2 + ".err")))
    # On a PINNED record — which is now every record dispatch.sh creates — the rename does not
    # blind anything: the worker's fd still holds the pinned inode, so the answer is a definite
    # ALIVE instead of round 4's UNKNOWN. Strictly better, and it must be asserted as such.
    check("renamed logfile -> a PINNED record still LISTS the worker (found by inode)",
          str(work_r2) in run([sys.executable, MJ, "job-live-pids", jobs, "J_R2"])[1].split(),
          run([sys.executable, MJ, "job-live-pids", jobs, "J_R2"])[1])
    rc, out, err = jset(jobs, "J_R2", "status=failed")
    check("...and the stamp is REFUSED", rc == 3, "rc=%d %s" % (rc, (out + err)[:260]))
    check("the refusal names the live processes it actually found",
          "are ALIVE right now" in err, err[:260])
    check("record still running", read_job(jobs, "J_R2")["status"] == "running")
    check("worker was never touched", alive(work_r2), "worker=%s" % work_r2)
    rc, out, err = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("reap does NOT close it either — it is alive, not blind",
          read_job(jobs, "J_R2")["status"] == "running", read_job(jobs, "J_R2")["status"])

    # R2b — the SAME rename on an UNPINNED (legacy, pre-round-5) record: nothing resolves the
    # recorded name any more, so the guard genuinely cannot answer. This is the case the
    # "absent evidence -> UNKNOWN, not dead" term exists for, and the board must not leak:
    # reap still closes it, saying on the record that the closure was not verified.
    log_r2b = os.path.join(tmp, "r2b.log")
    disp_r2b, work_r2b = spawn_sync_worker(log_r2b, jobs, "J_R2B")
    make_job(jobs, "J_R2B", "", log_r2b, dispatcher_pid=disp_r2b, pin=False)
    check("R2b legacy worker alive", alive(work_r2b), "worker=%s" % work_r2b)
    os.rename(log_r2b + ".err", os.path.join(tmp, "moved_away_b.err"))
    if os.path.exists(log_r2b):
        os.rename(log_r2b, os.path.join(tmp, "moved_away_b.log"))
    check("R2b unpinned + renamed -> job-live-pids reports nothing",
          run([sys.executable, MJ, "job-live-pids", jobs, "J_R2B"])[1].strip() == "",
          run([sys.executable, MJ, "job-live-pids", jobs, "J_R2B"])[1])
    rc, out, err = jset(jobs, "J_R2B", "status=failed")
    check("R2b ...yet the stamp is REFUSED, because empty-because-blind is not dead", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:260]))
    check("R2b the refusal says it CANNOT DETERMINE, it does not claim the job is alive",
          "CANNOT BE DETERMINED" in err, err[:260])
    check("R2b worker was never touched", alive(work_r2b), "worker=%s" % work_r2b)
    rc, out, err = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("R2b reap CAN still close a blind record (no permanent board leak)",
          read_job(jobs, "J_R2B")["status"] == "orphaned",
          read_job(jobs, "J_R2B")["status"])
    check("R2b and it records WHY it was allowed to",
          "GONE" in (read_job(jobs, "J_R2B").get("result_summary") or ""),
          read_job(jobs, "J_R2B").get("result_summary"))

    # R3 (N1) — corrupt the record itself. `except Exception: obj = {}` made the guard read a
    # blank record: no status meant the live-status precondition failed, no fields meant nothing
    # looked like an evidence rewrite. One `printf` disabled the entire guard.
    log_r3 = os.path.join(tmp, "r3.log")
    wrap_r3, work_r3 = spawn_wrapper(log_r3)
    time.sleep(0.4)
    make_job(jobs, "J_R3", wrap_r3, log_r3)
    with open(os.path.join(jobs, "J_R3.json"), "w", encoding="utf-8") as f:
        f.write("x")                                      # partial write / truncated record
    rc, out, err = jset(jobs, "J_R3", "status=failed")
    check("unparseable record -> REFUSED (was rc=0, guard fully off)", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:260]))
    check("the corrupt bytes were NOT overwritten with a fake terminal record",
          open(os.path.join(jobs, "J_R3.json"), encoding="utf-8").read() == "x")
    check("worker still alive", alive(work_r3), "worker=%s" % work_r3)
    check("--force still lets a human proceed deliberately",
          jset(jobs, "J_R3", "status=failed", "--force")[0] == 0)
    # A record file that simply does not exist is the normal create path and must stay open.
    rc, _, err = jset(jobs, "J_R4_new", "status=running", "to=Wags")
    check("a MISSING record is still created normally (missing != corrupt)", rc == 0, err[:200])

    # R5 (K3) — the trap now delegates to the same safe cancel primitive as operators. A
    # broken legacy fallback must not defeat a successful cancel; if BOTH verification
    # paths fail, the record must remain live rather than claim an unproved death.
    print("\nR5. sync trap centralises cancellation and still fails CLOSED")
    sub_r5a = os.path.join(tmp, "r5a")
    os.makedirs(sub_r5a, exist_ok=True)
    _rc, worker_r5a, status_r5a, _err = run_sync_kill_trap(
        sub_r5a, break_verifier=True)
    check("legacy verifier broken -> safe cancel still closes as cancelled",
          status_r5a == "cancelled", "status=%s" % status_r5a)
    check("...and the worker is genuinely dead", worker_r5a is not None
          and not alive(worker_r5a), "worker=%s" % worker_r5a)
    rc_r5, status_r5, err_r5 = run_sync_kill_trap_verifier_broken(tmp)
    check("both verifiers broken -> record deliberately LEFT at running", status_r5 == "running",
          "status=%s" % status_r5)
    check("...and it says why instead of silently stamping",
          "KHÔNG kiểm tra được" in err_r5, err_r5[-300:])

    # ------------------------- S (round 5): the premises round 4 CREATED and left unguarded
    # Round 4 answered "the logfile can be destroyed" by promoting two new things to evidence:
    # the startup grace window (`started_at`) and the agent's bus heartbeat (`to` + `job_id`
    # locate it). Neither was added to EVIDENCE_FIELDS, so each was a one-command bypass of
    # the guard that had just been built on it — the same shape as rounds 2/3/4, one level up.
    print("\nS. round 5 — the evidence round 4 introduced is now evidence too")
    hbroot, MJ_HB, jobs_hb = hb_sandbox(tmp)
    now = int(time.time())

    def mj(*args):
        return run([sys.executable, MJ_HB] + list(args))

    # S1 (K1) — `started_at` gates EVIDENCE_GRACE_S, so rewriting it to 'now' says "this job is
    # too young to have a logfile yet" about a job that has been running for an hour. That
    # turned the blind term OFF and the 2026-08-09 write went through: mv, started_at, failed.
    log_s1 = os.path.join(tmp, "s1.log")
    disp_s1, work_s1 = spawn_sync_worker(log_s1, jobs, "J_S1")
    make_job(jobs, "J_S1", "", log_s1, dispatcher_pid=disp_s1)
    for f in (log_s1 + ".err", log_s1):
        if os.path.exists(f):
            os.rename(f, f + ".moved")
    check("S1 baseline: with the logfile moved away, the stamp is refused",
          jset(jobs, "J_S1", "status=failed")[0] == 3)
    rc, out, err = jset(jobs, "J_S1", "started_at=%d" % now)
    check("S1 rewriting started_at is REFUSED (it is the grace window's own input)", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S1 the recorded started_at was not moved",
          read_job(jobs, "J_S1").get("started_at") == "1000",
          read_job(jobs, "J_S1").get("started_at"))
    rc2, _, _ = jset(jobs, "J_S1", "status=failed")
    check("S1 ...so the follow-up stamp stays refused too", rc2 == 3, "rc=%d" % rc2)
    check("S1 record still running", read_job(jobs, "J_S1")["status"] == "running")
    check("S1 worker never touched", alive(work_s1), "worker=%s" % work_s1)

    # S2 (K2) — `to` is what points _hb_age at bus/inbox/<agent>.jsonl. Rewriting it makes
    # every heartbeat unobservable, and round 4 spent "no heartbeat" as proof of death.
    log_s2 = os.path.join(tmp, "s2.log")
    disp_s2, work_s2 = spawn_sync_worker(log_s2, jobs, "J_S2")
    make_job(jobs, "J_S2", "", log_s2, dispatcher_pid=disp_s2)
    rc, out, err = jset(jobs, "J_S2", "to=Nobody")
    check("S2 rewriting `to` is REFUSED (it addresses the heartbeat evidence)", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S2 the recorded `to` is unchanged", read_job(jobs, "J_S2").get("to") == "Taylor")
    check("S2 worker still alive", alive(work_s2), "worker=%s" % work_s2)

    # S2b — and the heartbeat, once it cannot be redirected, must still VETO a blind cancel.
    log_s2b = os.path.join(tmp, "s2b.log")
    open(log_s2b, "a").close()
    put_record(jobs_hb, "J_S2B", to="HBAgent", logfile=log_s2b,
               started_at=now - 9000, deadline=now - 7200)
    write_hb(hbroot, "HBAgent", "J_S2B", 5)
    rc, out, err = mj("job-cancel", jobs_hb, "J_S2B", "2")
    check("S2b cancel REFUSES while the agent is still writing heartbeats", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S2b and it says the heartbeat is FRESH, not that the job is dead",
          "FRESH" in err, err[:200])

    # S2c (K3, cancel's half) — a job that NEVER heartbeated may still be cancelled (its
    # logfile is the evidence), but the record must not claim a coldness nobody observed.
    log_s2c = os.path.join(tmp, "s2c.log")
    open(log_s2c, "a").close()
    put_record(jobs_hb, "J_S2C", to="SilentAgent", logfile=log_s2c,
               started_at=now - 9000, deadline=now - 7200)
    rc, out, err = mj("job-cancel", jobs_hb, "J_S2C", "2")
    summ = read_job(jobs_hb, "J_S2C").get("result_summary", "")
    check("S2c a never-heartbeating job is still closable (no board leak)", rc == 0,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S2c the record does NOT claim the heartbeat 'has gone cold'",
          "gone cold" not in summ and "never wrote a heartbeat" in summ, summ[:240])

    # S3 (K3, reap's half) — reap ran from watchdog.sh every hour and closed records it had no
    # evidence about at ALL: logfile gone AND not one heartbeat ever written. 'orphaned' reads
    # as exit 1 = failed to every poller, i.e. the 2026-08-09 re-dispatch trigger, generated by
    # the fleet's own cron. Closing them eventually is still required — late and marked.
    put_record(jobs_hb, "J_S3_SOON", to="SilentAgent",
               logfile=os.path.join(tmp, "s3_never_existed.log"),
               started_at=now - 9000, deadline=now - 7200)
    mj("job-reap", jobs_hb, "3600")
    check("S3 no evidence either way -> reap does NOT close it 2h past deadline",
          read_job(jobs_hb, "J_S3_SOON")["status"] == "running",
          read_job(jobs_hb, "J_S3_SOON")["status"])
    put_record(jobs_hb, "J_S3_OLD", to="SilentAgent",
               logfile=os.path.join(tmp, "s3_never_existed2.log"),
               started_at=now - 200000, deadline=now - 100000)
    mj("job-reap", jobs_hb, "3600")
    rec_s3 = read_job(jobs_hb, "J_S3_OLD")
    check("S3 ...but a day later it IS closed (no permanent board leak)",
          rec_s3["status"] == "orphaned", rec_s3["status"])
    check("S3 and the record says the closure was UNVERIFIED",
          "UNVERIFIED" in (rec_s3.get("result_summary") or ""),
          (rec_s3.get("result_summary") or "")[:240])

    # S4 (N4) — reap used the caller's `grace` as the heartbeat threshold, so the documented
    # `jobs.sh reap 0` set it to zero and reaped a job whose agent had heartbeated that second.
    log_s4 = os.path.join(tmp, "s4.log")
    open(log_s4, "a").close()
    put_record(jobs_hb, "J_S4", to="HBAgent", logfile=log_s4,
               started_at=now - 9000, deadline=now - 7200)
    write_hb(hbroot, "HBAgent", "J_S4", 5)
    mj("job-reap", jobs_hb, "0")
    check("S4 `reap 0` does NOT close a job whose agent heartbeated 5s ago",
          read_job(jobs_hb, "J_S4")["status"] == "running",
          read_job(jobs_hb, "J_S4")["status"])
    log_s4b = os.path.join(tmp, "s4b.log")
    open(log_s4b, "a").close()
    put_record(jobs_hb, "J_S4B", to="HBAgent", logfile=log_s4b,
               started_at=now - 9000, deadline=now - 7200)
    write_hb(hbroot, "HBAgent", "J_S4B", 5000)
    mj("job-reap", jobs_hb, "3600")
    check("S4 a genuinely cold job is still reaped (the floor did not break reap)",
          read_job(jobs_hb, "J_S4B")["status"] == "orphaned",
          read_job(jobs_hb, "J_S4B")["status"])

    # S4c — `deadline` is guarded by DIRECTION: shrinking it is how a record is made instantly
    # reap-eligible; growing it is dispatch.sh's own heartbeat-aware extension on a job that is
    # by definition alive. Guarding both would refuse the fleet's most routine write.
    log_s4c = os.path.join(tmp, "s4c.log")
    disp_s4c, work_s4c = spawn_sync_worker(log_s4c, jobs, "J_S4C")
    make_job(jobs, "J_S4C", "", log_s4c, dispatcher_pid=disp_s4c)
    check("S4c shrinking the deadline on a live job is REFUSED",
          jset(jobs, "J_S4C", "deadline=1")[0] == 3)
    check("S4c EXTENDING it (hb-aware extension) is still allowed",
          jset(jobs, "J_S4C", "deadline=99999", "hb_extensions=1")[0] == 0)
    check("S4c worker untouched", alive(work_s4c), "worker=%s" % work_s4c)

    # S5 (N5) — a file that merely occupies the path is not the job's logfile. `mv log x;
    # : > log` restored "evidence present" while nothing on disk related to the job any more,
    # and "present but nobody holding it" is read as PROVEN DEAD. With the inode pinned at
    # dispatch time the move does not even blind the guard: the holder is found by identity.
    # The pin is CREATED only by the owning dispatcher, and only while the record is younger
    # than EVIDENCE_GRACE_S — the window in which no worker exists yet and the path therefore
    # still means what the record says (round 6, K3). This is dispatch.sh's own call shape.
    log_s5 = os.path.join(tmp, "s5.log")
    put_record(jobs, "J_S5", to="Taylor", logfile=log_s5, pin=False,
               started_at=int(time.time()), deadline=int(time.time()) + 600,
               dispatcher_pid=os.getpid())
    rc, _, err = run([sys.executable, MJ, "job-pin-log", jobs, "J_S5"],
                     env=owner_env("J_S5"))
    pinned = read_job(jobs, "J_S5")
    check("S5 job-pin-log records the logfile identity", bool(pinned.get("logfile_ino")),
          str(pinned)[:200])
    disp_s5, work_s5 = spawn_sync_worker(log_s5, jobs, "J_S5")
    jset(jobs, "J_S5", "dispatcher_pid=%s" % disp_s5)
    for f in (log_s5 + ".err", log_s5):
        if os.path.exists(f):
            os.rename(f, f + ".hidden")
            open(f, "a").close()                      # the decoy, at the very same path
    live_out = mj("job-live-pids", jobs, "J_S5")[1]
    check("S5 the decoy does not hide the worker (found by pinned inode)",
          str(work_s5) in live_out.split(), "worker=%s out=%r" % (work_s5, live_out))
    rc, out, err = jset(jobs, "J_S5", "status=failed")
    check("S5 ...so the stamp is REFUSED over the decoy", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S5 record still running", read_job(jobs, "J_S5")["status"] == "running")
    check("S5 re-pinning onto the decoy is refused (idempotent pin)",
          read_job(jobs, "J_S5").get("logfile_ino") == pinned.get("logfile_ino")
          and mj("job-pin-log", jobs, "J_S5")[0] == 0
          and read_job(jobs, "J_S5").get("logfile_ino") == pinned.get("logfile_ino"))

    # S6 — DISCRIMINATING test for the round-4 K1 mechanism. R1 asserts only that the stamp is
    # refused, which the blind term satisfies on its own: deleting the '(deleted)' fallback
    # left the suite fully green while job-live-pids went empty on a live worker. Assert the
    # mechanism itself — after the unlink the holder must still be LISTED, not merely doubted.
    log_s6 = os.path.join(tmp, "s6.log")
    disp_s6, work_s6 = spawn_sync_worker(log_s6, jobs, "J_S6")
    make_job(jobs, "J_S6", "", log_s6, dispatcher_pid=disp_s6)   # unpinned: legacy record
    for f in (log_s6 + ".err", log_s6):
        if os.path.exists(f):
            os.remove(f)
    out_s6 = mj("job-live-pids", jobs, "J_S6")[1]
    check("S6 after rm, job-live-pids still LISTS the worker (not just 'refuses')",
          str(work_s6) in out_s6.split(), "worker=%s out=%r" % (work_s6, out_s6))

    # S5b (round 6, K1) — the SAME decoy on a record with NO pin. Round 5 pinned the inode and
    # called N5 closed; every one of the 751 records on the live board was in fact unpinned, so
    # the decoy still walked straight through the ordinary close path. Unpinned + a file at the
    # path must be UNKNOWN, never DEAD: nothing ties that file to this job.
    log_s5b = os.path.join(tmp, "s5b.log")
    disp_s5b, work_s5b = spawn_sync_worker(log_s5b, jobs, "J_S5B")
    make_job(jobs, "J_S5B", "", log_s5b, dispatcher_pid=disp_s5b, pin=False)
    check("S5b legacy worker alive", alive(work_s5b), "worker=%s" % work_s5b)
    for f in (log_s5b + ".err", log_s5b):
        if os.path.exists(f):
            os.rename(f, f + ".hidden")
            open(f, "a").close()                      # the decoy, at the very same path
    rc, out, err = jset(jobs, "J_S5B", "status=failed")
    check("S5b decoy on an UNPINNED record -> the stamp is REFUSED", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:220]))
    check("S5b the refusal says WHY: no pinned identity, so the file proves nothing",
          "NO pinned logfile identity" in err, err[:260])
    check("S5b record still running", read_job(jobs, "J_S5B")["status"] == "running")
    check("S5b worker untouched", alive(work_s5b), "worker=%s" % work_s5b)
    # ...and reap must not paper over it either. Moved to just-past-deadline (a GROWTH, the one
    # direction that stays unguarded) so the case being asserted is the REAP_UNVERIFIED_S wait
    # rather than this fixture's epoch-1970 deadline, which is already a day past everything.
    jset(jobs, "J_S5B", "deadline=%d" % (int(time.time()) - 60))
    rc, out, err = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("S5b reap does not close it early either (the unverified wait applies)",
          read_job(jobs, "J_S5B")["status"] == "running",
          read_job(jobs, "J_S5B")["status"])

    # S8 (round 6, K3) — job-pin-log is itself a writer of the evidence, so it must not be
    # usable as the attack it was added to prevent. On an already-running record it may pin
    # ONLY what a live process of the job is really holding; hiding the log and asking it to
    # pin must not create files and call them evidence, which turned UNKNOWN into DEAD in one
    # official command.
    log_s8 = os.path.join(tmp, "s8.log")
    disp_s8, work_s8 = spawn_sync_worker(log_s8, jobs, "J_S8")
    make_job(jobs, "J_S8", "", log_s8, dispatcher_pid=disp_s8, pin=False)
    for f in (log_s8 + ".err", log_s8):
        if os.path.exists(f):
            os.rename(f, os.path.join(tmp, os.path.basename(f) + ".gone"))
    rc, _, _ = run([sys.executable, MJ, "job-pin-log", jobs, "J_S8"], env=owner_env("J_S8"))
    check("S8 job-pin-log does not pin a file it made up on a running record",
          not _record_pin_of(read_job(jobs, "J_S8")),
          str(read_job(jobs, "J_S8"))[:200])
    check("S8 and it did not create the files either",
          not os.path.exists(log_s8) and not os.path.exists(log_s8 + ".err"))
    check("S8 ...so the close stays REFUSED", jset(jobs, "J_S8", "status=failed")[0] == 3)
    check("S8 the failure is recorded on the record, not swallowed",
          str(read_job(jobs, "J_S8").get("pin_failed")) == "1",
          str(read_job(jobs, "J_S8").get("pin_failed")))
    check("S8 worker untouched", alive(work_s8), "worker=%s" % work_s8)

    # S8b (round 7, K1) — the variant S8 misses: the decoy is not just planted, it is HELD OPEN
    # by a live process. The first backfill asked _job_live_pids for its candidates, and on an
    # unpinned record that matches processes by stat()ing the PATH — so the decoy's holder WAS
    # "the job", and its inode became the record's permanent identity. One unprivileged
    # job-pin-log then made job-set/reap/cancel all close a provably live worker with rc=0,
    # citing the pin. Candidates must come from the recorded pid's tree, never from the path.
    log_s8b = os.path.join(tmp, "s8b.log")
    disp_s8b, work_s8b = spawn_sync_worker(log_s8b, jobs, "J_S8B")
    make_job(jobs, "J_S8B", "", log_s8b, dispatcher_pid=disp_s8b, pin=False)
    real_ino = os.stat(log_s8b + ".err").st_ino
    for f in (log_s8b + ".err", log_s8b):
        if os.path.exists(f):
            os.rename(f, f + ".hidden")
    squatter = subprocess.Popen(["sh", "-c", "exec sleep 60"],
                                stdout=open(log_s8b, "a"), stderr=open(log_s8b + ".err", "a"))
    SPAWNED.append(squatter.pid)
    time.sleep(0.3)
    run([sys.executable, MJ, "job-pin-log", jobs, "J_S8B"])
    rec_s8b = read_job(jobs, "J_S8B")
    check("S8b a HELD decoy is not laundered into the record as the job's identity",
          not _record_pin_of(rec_s8b), str(_record_pin_of(rec_s8b)))
    check("S8b ...and certainly not the squatter's inode",
          str(os.stat(log_s8b).st_ino) not in str(_record_pin_of(rec_s8b))
          and str(real_ino) not in str(_record_pin_of(rec_s8b)))
    check("S8b so job-set still REFUSES", jset(jobs, "J_S8B", "status=failed")[0] == 3)
    rc, out, err = run([sys.executable, MJ, "job-reap", jobs, "0"])
    check("S8b and reap does not close it either",
          read_job(jobs, "J_S8B")["status"] == "running",
          read_job(jobs, "J_S8B")["status"])
    check("S8b worker untouched", alive(work_s8b), "worker=%s" % work_s8b)
    for sig in (15, 9):
        try:
            os.kill(squatter.pid, sig)
        except Exception:
            pass

    # S8c (round 7, K2) — cancel must not do the destructive half and then refuse the
    # bookkeeping. On an UNPINNED record the verdict is UNKNOWN, so the status write was
    # refused AFTER the kill: processes dead, board still 'running', record drifting to
    # 'orphaned' hours later — which every poller reads as a failure worth re-dispatching.
    log_s8c = os.path.join(tmp, "s8c.log")
    disp_s8c, work_s8c = spawn_sync_worker(log_s8c, jobs, "J_S8C")
    make_job(jobs, "J_S8C", "", log_s8c, dispatcher_pid=disp_s8c, pin=False)
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_S8C", "5"])
    time.sleep(0.4)
    check("S8c cancel REFUSES an unpinned record BEFORE killing anything", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S8c nothing was killed — the destructive half never ran", alive(work_s8c),
          "worker=%s" % work_s8c)
    check("S8c the refusal says so out loud", "NOTHING has been killed" in err, err[:200])
    check("S8c record untouched", read_job(jobs, "J_S8C")["status"] == "running",
          read_job(jobs, "J_S8C")["status"])
    check("S8c stdout did not announce a kill it did not do", "killing" not in out, out[:120])

    # S8d (round 8, K1) — the exploit the round-7 exemption opened. `_kill_tree` returning "no
    # survivors" proves only that the pids it enumerated are dead, and on an unpinned record
    # those come from stat()ing the path. Hide the real logfile, park a squatter on the path,
    # and cancel would kill the squatter, report "1 process killed and verified dead", and stamp
    # `cancelled` while the real worker ran on — the 2026-08-09 lie rebuilt out of sanctioned
    # commands. A path match must never buy the right to close a record.
    log_s8d = os.path.join(tmp, "s8d.log")
    disp_s8d, work_s8d = spawn_sync_worker(log_s8d, jobs, "J_S8D")
    make_job(jobs, "J_S8D", "", log_s8d, dispatcher_pid=disp_s8d, pin=False)
    for f in (log_s8d + ".err", log_s8d):
        if os.path.exists(f):
            os.rename(f, f + ".hidden")
    squat_d = subprocess.Popen(["sh", "-c", "exec sleep 60"],
                               stdout=open(log_s8d, "a"), stderr=open(log_s8d + ".err", "a"))
    SPAWNED.append(squat_d.pid)
    time.sleep(0.3)
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_S8D", "5"])
    time.sleep(0.4)
    check("S8d a squatter on the path does not buy a cancel", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S8d the REAL worker is untouched", alive(work_s8d), "worker=%s" % work_s8d)
    check("S8d the board never says 'cancelled' about a job still running",
          read_job(jobs, "J_S8D")["status"] == "running",
          read_job(jobs, "J_S8D")["status"])
    for sig in (15, 9):
        try:
            os.kill(squat_d.pid, sig)
        except Exception:
            pass

    # S8e (round 8, K2) — the branch S8c could not reach. S8c's fixture has no bus/inbox at all,
    # so its heartbeat reads 'never' and it only ever exercised the UNKNOWN path. With a FRESH
    # heartbeat the verdict is ALIVE, which no exemption may override: the agent is still
    # writing events, so there is nothing to claim and nothing to kill on the strength of.
    log_s8e = os.path.join(tmp, "s8e.log")
    disp_s8e, work_s8e = spawn_sync_worker(log_s8e, jobs_hb, "J_S8E")
    make_job(jobs_hb, "J_S8E", "", log_s8e, to="HBAgent", dispatcher_pid=disp_s8e)
    write_hb(hbroot, "HBAgent", "J_S8E", 30)
    for f in (log_s8e + ".err", log_s8e):        # evidence gone, but the agent is alive
        if os.path.exists(f):
            os.remove(f)
    rc, out, err = run([sys.executable, MJ_HB, "job-cancel", jobs_hb, "J_S8E", "5"])
    time.sleep(0.4)
    check("S8e a FRESH heartbeat stops cancel before the kill", rc == 3,
          "rc=%d %s" % (rc, (out + err)[:200]))
    check("S8e the worker is untouched", alive(work_s8e), "worker=%s" % work_s8e)
    check("S8e record still running", read_job(jobs_hb, "J_S8E")["status"] == "running",
          read_job(jobs_hb, "J_S8E")["status"])

    # S9a (round 9, K1) — the exemption was granted in the very state where the guard had just
    # declared itself blind. "targets ⊆ the recorded pid's tree" was accepted as identity, but
    # _descendants cannot see an orphan, and orphans are the entire reason _pids_holding exists;
    # meanwhile the exemption is only reachable with the verdict at UNKNOWN, i.e. right after
    # the OTHER lookup came back empty. Real --bg shape: recorded pid = wrapper, the true worker
    # setsid'd out of that tree onto the SAME logfile, then the logfile renamed away (the same
    # in-scope attacker/housekeeping action rounds 4-8 accept). Killing the tree is legitimate —
    # those really are the job's processes. Writing "verified dead" afterwards is not.
    log_s9a = os.path.join(tmp, "s9a.log")
    open(log_s9a, "a").close()
    wrap_a = subprocess.Popen(["bash", "-c", "exec sleep 900"],
                              stdout=open(log_s9a, "a"), stderr=subprocess.STDOUT)
    work_a = subprocess.Popen(["setsid", "bash", "-c", "exec sleep 900"],
                              stdout=open(log_s9a, "a"), stderr=subprocess.STDOUT)
    SPAWNED.extend([wrap_a.pid, work_a.pid])
    time.sleep(0.4)
    # started_at must be a REAL age, not the round-5 fixtures' epoch 1000: past EVIDENCE_GRACE_S
    # (120) so a vanished logfile counts as evidence gone, yet inside PID_OWNERSHIP_SLACK (300)
    # of the wrapper's own start so the ownership check does not reject the fixture before the
    # branch under test is reached. With started_at=1000 this test passed against the BROKEN
    # code for the wrong reason — the same vacuous-fixture trap that hid round 7's K2.
    _t0 = int(time.time()) - 200
    put_record(jobs, "J_S9A", to="Taylor", status="running", pin=False,
               prompt_summary="round nine kay one", logfile=log_s9a, pid=str(wrap_a.pid),
               started_at=str(_t0), deadline=str(_t0 + 3600), dispatcher_pid="")
    os.rename(log_s9a, log_s9a + ".hidden")
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_S9A", "3"])
    time.sleep(0.5)
    rec_a = read_job(jobs, "J_S9A")
    sum_a = rec_a.get("result_summary") or ""
    check("S9a the job's real worker, outside the recorded pid tree, is still alive",
          alive(work_a.pid), "worker=%d" % work_a.pid)
    check("S9a the record NEVER claims verified death while that worker runs",
          "verified dead" not in sum_a, sum_a[:200])
    check("S9a an unverified close is MARKED for machines, not just worded for humans",
          rec_a.get("status") != "cancelled" or str(rec_a.get("death_verified")) == "0",
          "status=%s death_verified=%r" % (rec_a.get("status"), rec_a.get("death_verified")))
    check("S9a and it says which lookup went blind, so the operator can check by hand",
          rec_a.get("status") != "cancelled" or "NOT VERIFIED" in sum_a, sum_a[:200])
    for p in (wrap_a.pid, work_a.pid):
        try:
            os.kill(p, 9)
        except Exception:
            pass

    # S9b (round 9, K2) — the pre-flight bounded the DECISION but not the KILL SET. _kill_tree
    # re-collects _job_live_pids on every pass, which on an unpinned record is a PATH match, so
    # a process that opened the logfile after the verdict was signalled anyway: an innocent
    # bystander SIGKILLed, and then counted in "N process(es) killed". On this host that
    # collateral could have been run_bot.sh or the Discord bridge.
    log_s9b = os.path.join(tmp, "s9b.log")
    open(log_s9b, "a").close()
    wrap_b = subprocess.Popen(["bash", "-c", 'trap "" TERM; while :; do sleep 1; done'],
                              stdout=open(log_s9b, "a"), stderr=subprocess.STDOUT)
    SPAWNED.append(wrap_b.pid)
    time.sleep(0.3)
    make_job(jobs, "J_S9B", wrap_b.pid, log_s9b, prompt="round nine kay two", pin=False)
    late = {}

    def _late_squatter():
        time.sleep(2.0)                      # after the verdict, inside _kill_tree's grace
        p = subprocess.Popen(["bash", "-c", "exec sleep 900"],
                             stdout=open(log_s9b, "a"), stderr=subprocess.STDOUT)
        late["p"] = p
        SPAWNED.append(p.pid)

    th = threading.Thread(target=_late_squatter)
    th.start()
    rc, out, err = run([sys.executable, MJ, "job-cancel", jobs, "J_S9B", "6"])
    th.join()
    time.sleep(0.5)
    byst = late.get("p")
    check("S9b a bystander that touched the path AFTER the verdict is not killed",
          byst is not None and alive(byst.pid),
          "bystander=%s rc=%d %s" % (byst and byst.pid, rc, (out + err)[:200]))
    check("S9b and with it still holding the path, cancel refuses to stamp anything",
          rc == 5 and read_job(jobs, "J_S9B")["status"] == "running",
          "rc=%d status=%s" % (rc, read_job(jobs, "J_S9B")["status"]))
    for p in (wrap_b.pid, byst.pid if byst else 0):
        try:
            os.kill(p, 9)
        except Exception:
            pass

    # S9c (round 9, K1 second half) — a record closed WITHOUT verified death must not become
    # invisible to the duplicate-dispatch check. Terminal status is permission to stop waiting,
    # not evidence that nothing is running, and the collision it would otherwise produce is
    # exactly the 2026-08-09 one: board reads terminal, someone re-dispatches, new run meets the
    # old one that never stopped.
    log_s9c = os.path.join(tmp, "s9c.log")
    disp_s9c, work_s9c = spawn_sync_worker(log_s9c, jobs, "J_S9C")
    put_record(jobs, "J_S9C", to="Taylor", status="cancelled",
               prompt_summary="round nine dup scan", logfile=log_s9c, pid=str(work_s9c),
               death_verified="0", started_at="1000", deadline="1600")
    rc, out, err = run([sys.executable, MJ, "job-find-dup", jobs, "Taylor",
                        "round nine dup scan"])
    check("S9c an unverified close still shows up as a duplicate-dispatch collision",
          rc == 0 and "J_S9C" in out, "rc=%d out=%s" % (rc, out[:160]))

    # S9d (round 9, contract) — NICE5 of round 8 shipped with no test at all: deleting
    # pin_source from EVIDENCE_FIELDS left the suite fully green. It is an ATTESTATION about
    # where the guard's evidence came from, so forging it is forging the guard's own testimony.
    log_s9d = os.path.join(tmp, "s9d.log")
    disp_s9d, work_s9d = spawn_sync_worker(log_s9d, jobs, "J_S9D")
    make_job(jobs, "J_S9D", "", log_s9d, dispatcher_pid=disp_s9d)
    rc, _o, err = jset(jobs, "J_S9D", "pin_source=backfill")
    check("S9d pin_source cannot be hand-written onto a live record", rc != 0,
          "rc=%d %s" % (rc, err[:160]))
    check("S9d and the record's own attestation is unchanged",
          read_job(jobs, "J_S9D").get("pin_source") != "backfill",
          repr(read_job(jobs, "J_S9D").get("pin_source")))


    # S7 — EVIDENCE_GRACE_S had no discriminating coverage at all: setting it to 1e11 and
    # deleting the blind term produced identical results. It is the window killer S1 walked
    # through, and it has to be tested in BOTH directions — too small hangs every new job at
    # running (a fleet outage), too large is the bypass.
    # Both fixtures are PINNED and then have their files removed — that is what isolates the
    # grace: the identity is on the record either way, so the only thing left that can differ
    # between the two is how old the record is (round 6 made a pin a precondition of DEAD, so
    # an unpinned fixture would read UNKNOWN in both directions and test nothing).
    s7_young = os.path.join(tmp, "s7_not_open_yet.log")
    s7_old = os.path.join(tmp, "s7_gone.log")
    for p in (s7_young, s7_old):
        open(p, "a").close()
        open(p + ".err", "a").close()
    put_record(jobs_hb, "J_S7_YOUNG", to="SilentAgent", logfile=s7_young,
               started_at=now, deadline=now + 600)
    for p in (s7_young, s7_young + ".err"):
        os.remove(p)
    check("S7 a job younger than the grace may be closed (no logfile yet is NORMAL)",
          run([sys.executable, MJ_HB, "job-set", jobs_hb, "J_S7_YOUNG",
               "status=failed"])[0] == 0)
    put_record(jobs_hb, "J_S7_OLD", to="SilentAgent", logfile=s7_old,
               started_at=now - 3600, deadline=now + 600)
    for p in (s7_old, s7_old + ".err"):
        os.remove(p)
    check("S7 past the grace the same shape is REFUSED (absent logfile = UNKNOWN)",
          run([sys.executable, MJ_HB, "job-set", jobs_hb, "J_S7_OLD",
               "status=failed"])[0] == 3)

    # ------------------------------------------------- O: the sync KILL trap (E2E, real script)
    # dispatch.sh's sync path traps TERM so a killed dispatcher does not leave the record at
    # running forever (incident 2026-07-09). But the worker is setsid'd: it SURVIVES the
    # caller's process-group kill. Stamping failed while it keeps editing the repo is exactly
    # the record that made the board lie on 08-09 — so the trap must STOP it, then stamp.
    print("\nO. dispatch.sh sync trap kills the worker BEFORE it closes the record")
    rc_o, worker_o, status_o, _err_o = run_sync_kill_trap(tmp)
    check("trap delegates to safe cancel and closes the record", status_o == "cancelled",
          "status=%s" % status_o)
    check("the setsid'd worker is DEAD, not orphaned into the repo", worker_o is not None
          and not alive(worker_o), "worker=%s" % worker_o)
    # ...and the REAL script pinned the evidence. Asserted on the record dispatch.sh itself
    # wrote, not on a fixture: the pin is only worth anything if the production path sets it,
    # and it must be the same encoding mike_json.py compares against (dev:ino, not %i alone).
    _pin = LAST_E2E_RECORD.get("logfile_ino")
    _lf = LAST_E2E_RECORD.get("logfile") or ""
    try:
        _st = os.stat(_lf)
        _want = "%d:%d" % (_st.st_dev, _st.st_ino)
    except Exception:
        _want = None
    check("a real dispatch pins its logfile identity onto the record",
          bool(_pin) and _pin == _want, "pin=%s want=%s logfile=%s" % (_pin, _want, _lf))

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
