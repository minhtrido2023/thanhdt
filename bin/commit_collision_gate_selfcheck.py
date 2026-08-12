#!/usr/bin/env python3
"""Selfcheck for the repo-commit-collision gate (bin/repo_commit_gate.sh +
mike_json.py commit-collision-gate).

Every LIVE fixture job is backed by a REAL live process (a `sleep` this script spawns and
reaps), because the gate's liveness answer comes from /proc, not from the record's status
word — a fixture that only writes status=running would make the tests pass on a gate that
never looks at /proc at all. That is the same fixture trap that made the job-cancel guard
go green on broken code (round 9: started_at=1000 short-circuited the branch under test).

Case 12 replays the incident this gate was written for: the real job record
Wags_20260812_035748 (write_scope='') and the real file list of commit f827f6df, plus the
RED counterfactual proving the SHIPPED --write-scope gate is blind to it.

Usage: bin/commit_collision_gate_selfcheck.py     (exit 0 = all pass)
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
GATE = os.path.join(ROOT, "bin", "repo_commit_gate.sh")

PASS, FAIL = [], []
_procs = []


def sleeper():
    """A real live pid the gate's /proc check can see."""
    p = subprocess.Popen(["sleep", "600"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    _procs.append(p)
    return p.pid


def dead_pid():
    """A pid that is definitely gone (spawn + reap)."""
    p = subprocess.Popen(["true"])
    p.wait()
    return p.pid


def write_job(d, job_id, **kw):
    o = {"job_id": job_id, "from": "Mike", "to": "Taylor", "status": "running",
         "started_at": str(int(time.time()) - 60), "logfile": "", "write_scope": ""}
    o.update({k: str(v) for k, v in kw.items()})
    with open(os.path.join(d, job_id + ".json"), "w", encoding="utf-8") as f:
        json.dump(o, f)
    return o


def run_gate(jobs_dir, paths, self_pid=1, env=None):
    e = dict(os.environ)
    e.pop("JOB_ID", None)
    e.update(env or {})
    r = subprocess.run([sys.executable, MJ, "commit-collision-gate", jobs_dir,
                        "--self-pid", str(self_pid)] + list(paths),
                       capture_output=True, text=True, env=e)
    lines = [l for l in r.stdout.strip().splitlines() if l.strip()]
    return r.returncode, [l.split("|") for l in lines]


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name + (("  <- " + detail) if detail and not cond else ""))


def verdicts(rows):
    return sorted((r[0], r[1]) for r in rows)


def main():
    tmp = tempfile.mkdtemp(prefix="ccgate_")
    try:
        # ---------- A. tiering ----------
        d = os.path.join(tmp, "a")
        os.makedirs(d)
        write_job(d, "Taylor_live", pid=sleeper(), to="Taylor")
        rc, rows = run_gate(d, ["kb/notes.md"])
        check("1 live non-tooling job + unrelated path -> WARN only",
              rc == 0 and verdicts(rows) == [("WARN", "Taylor_live")], str(rows))

        rc, rows = run_gate(d, ["bin/dispatch.sh"])
        check("2 live NON-charter agent + shared path -> still only WARN (no over-blocking)",
              verdicts(rows) == [("WARN", "Taylor_live")], str(rows))

        d = os.path.join(tmp, "b")
        os.makedirs(d)
        write_job(d, "Wags_live", pid=sleeper(), to="Wags")
        rc, rows = run_gate(d, ["bin/dispatch.sh", "kb/notes.md"])
        check("3 live Wags job + shared tooling path -> BLOCK",
              verdicts(rows) == [("BLOCK", "Wags_live")], str(rows))
        check("3b BLOCK names only the shared path, not the innocent one",
              rows and rows[0][6] == "bin/dispatch.sh", str(rows))

        rc, rows = run_gate(d, ["kb/notes.md"])
        check("4 live Wags job but NO shared path staged -> WARN",
              verdicts(rows) == [("WARN", "Wags_live")], str(rows))

        d = os.path.join(tmp, "c")
        os.makedirs(d)
        write_job(d, "Mafee_live", pid=sleeper(), to="Mafee",
                  write_scope="trading_bot/plan_funding_gate.py")
        rc, rows = run_gate(d, ["trading_bot/plan_funding_gate.py"])
        check("5 declared write_scope overlap (non-tooling agent, non-shared path) -> BLOCK",
              verdicts(rows) == [("BLOCK", "Mafee_live")], str(rows))
        rc, rows = run_gate(d, ["trading_bot/executor.py"])
        check("6 declared write_scope, DIFFERENT file -> WARN",
              verdicts(rows) == [("WARN", "Mafee_live")], str(rows))

        # ---------- B. liveness must come from /proc ----------
        d = os.path.join(tmp, "d")
        os.makedirs(d)
        write_job(d, "Wags_zombie", pid=dead_pid(), to="Wags", status="running")
        rc, rows = run_gate(d, ["bin/dispatch.sh"])
        check("7 status=running but pid DEAD -> silent (status word is not evidence)",
              rows == [], str(rows))

        write_job(d, "Wags_done", pid=sleeper(), to="Wags", status="done")
        rc, rows = run_gate(d, ["bin/dispatch.sh"])
        check("8 terminal status -> silent even with a live pid",
              rows == [], str(rows))

        write_job(d, "Wags_unverified", pid=sleeper(), to="Wags", status="failed",
                  death_verified="0")
        rc, rows = run_gate(d, ["bin/dispatch.sh"])
        check("9 closed WITHOUT verified death + live pid -> BLOCK (same rule as job-find-dup K1)",
              verdicts(rows) == [("BLOCK", "Wags_unverified")], str(rows))

        # ---------- C. self-exclusion ----------
        d = os.path.join(tmp, "e")
        os.makedirs(d)
        write_job(d, "Wags_me", pid=os.getpid(), to="Wags")
        rc, rows = run_gate(d, ["bin/dispatch.sh"], self_pid=os.getpid())
        check("10 job whose pid is MY ancestor chain -> excluded (a job may commit its own work)",
              rows == [], str(rows))
        rc, rows = run_gate(d, ["bin/dispatch.sh"], self_pid=1)
        check("10b same record, foreign callsite -> BLOCK (proves case 10 is exclusion, not a dead gate)",
              verdicts(rows) == [("BLOCK", "Wags_me")], str(rows))

        d = os.path.join(tmp, "f")
        os.makedirs(d)
        write_job(d, "Wags_envself", pid=sleeper(), to="Wags")
        rc, rows = run_gate(d, ["bin/dispatch.sh"], self_pid=1,
                            env={"JOB_ID": "Wags_envself"})
        check("11 JOB_ID env fallback excludes self when ancestry is broken (setsid reparent)",
              rows == [], str(rows))
        rc, rows = run_gate(d, ["bin/dispatch.sh"], self_pid=1,
                            env={"JOB_ID": "Wags_someoneelse"})
        check("11b JOB_ID of a DIFFERENT job does not excuse this one",
              verdicts(rows) == [("BLOCK", "Wags_envself")], str(rows))

        # ---------- D. replay of the real 2026-08-12 collision ----------
        real = os.path.join(ROOT, "bus", "jobs", "Wags_20260812_035748.json")
        if os.path.exists(real):
            d = os.path.join(tmp, "g")
            os.makedirs(d)
            with open(real, encoding="utf-8") as f:
                rec = json.load(f)
            live = sleeper()
            rec.update({"status": "running", "pid": str(live), "logfile": "",
                        "started_at": str(int(time.time()) - 840)})   # commit landed 840s in
            rec.pop("ended_at", None)
            rec.pop("exit_code", None)
            rec.pop("logfile_ino", None)
            rec.pop("logfile_err_ino", None)
            with open(os.path.join(d, rec["job_id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(rec, f)
            staged = subprocess.run(["git", "show", "--pretty=", "--name-only", "f827f6df"],
                                    cwd=ROOT, capture_output=True, text=True).stdout.split()
            check("12a incident fixture intact (9 files, write_scope empty)",
                  len(staged) == 9 and rec.get("write_scope", "") == "",
                  "files=%d scope=%r" % (len(staged), rec.get("write_scope")))
            rc, rows = run_gate(d, staged)
            check("12b REPLAY 2026-08-12: Mike committing f827f6df during live "
                  "Wags_20260812_035748 -> BLOCK",
                  verdicts(rows) == [("BLOCK", "Wags_20260812_035748")], str(rows))
            check("12c BLOCK lists the 8 bin/ files, not kb/ops_runbook.md",
                  rows and rows[0][6].count(",") == 7 and "ops_runbook" not in rows[0][6],
                  str(rows))
            # RED counterfactual: the gate that WAS shipped (f58bd88a, --write-scope) is blind.
            r = subprocess.run([sys.executable, MJ, "job-write-scope-conflict", d,
                                ",".join(staged)], capture_output=True, text=True)
            check("12d RED: shipped --write-scope gate sees NOTHING here (both sides declared "
                  "no scope) -> this tier is new coverage, not a restatement",
                  r.returncode == 1 and not r.stdout.strip(), r.stdout)
            # And the same job, if it HAD declared a scope, is caught by tier 1 too.
            rec["write_scope"] = "bin/dispatch.sh"
            rec["to"] = "Taylor"      # strip the charter presumption, leave only the declaration
            with open(os.path.join(d, rec["job_id"] + ".json"), "w", encoding="utf-8") as f:
                json.dump(rec, f)
            rc, rows = run_gate(d, staged)
            check("12e same replay with a DECLARED scope and a non-charter agent -> BLOCK via tier 1",
                  verdicts(rows) == [("BLOCK", "Wags_20260812_035748")], str(rows))
        else:
            check("12 incident record present for replay", False, real + " missing")

        # ---------- E. wrapper policy (modes, fail-open, path matching) ----------
        d = os.path.join(tmp, "h")
        os.makedirs(d)
        write_job(d, "Wags_wrap", pid=sleeper(), to="Wags")
        check("13 pre-commit config wires the gate with always_run + pass_filenames:false",
              _config_wired(), "gate not registered in .pre-commit-config.yaml")

        r = subprocess.run(["bash", "-n", GATE], capture_output=True, text=True)
        check("14 wrapper parses", r.returncode == 0, r.stderr)

        modes = _wrapper_modes()
        check("15 wrapper honours MIKE_COMMIT_GATE=off / warn / block",
              modes == {"off": 0, "warn": 0, "block": 1}, str(modes))

        # path-overlap semantics, via the module directly
        sys.path.insert(0, os.path.join(ROOT, "bin"))
        import importlib
        mj = importlib.import_module("mike_json")
        ov = mj._path_overlaps
        check("16 overlap is segment-aware (bin/jobs.sh vs bin/jobs.sh.bak must NOT overlap)",
              ov("bin/jobs.sh", "bin/jobs.sh") and ov("bin/jobs.sh", "bin/")
              and ov("bin/", "bin/jobs.sh") and not ov("bin/jobs.sh", "bin/jobs.sh.bak")
              and not ov("bin/jobs.sh", "") and not ov("binx/jobs.sh", "bin"))
        check("17 SHARED_TOOLING_PATHS covers every path family this gate claims to protect",
              set(mj.SHARED_TOOLING_PATHS) >= {"bin/", "hooks/", ".pre-commit-config.yaml"}
              and mj.SHARED_TOOLING_AGENTS == ("Wags",),
              "%r %r" % (mj.SHARED_TOOLING_PATHS, mj.SHARED_TOOLING_AGENTS))
        check("18 empty staged list is a no-op, not a crash",
              run_gate(d, [])[0] == 0)

        # ---------- F. end-to-end: does `git commit` ACTUALLY refuse? ----------
        # Cases 19-21 exist because the classifier and the wrapper both passed while the
        # real thing did not: installed as a copied .git/hooks/pre-commit, ROOT resolved to
        # `.git`, mike_json.py was not there, and the fail-open branch made the gate a
        # SILENT no-op — the commit sailed through with no output at all.
        e2e = _e2e()
        check("19 E2E: git commit of a shared-tooling file during a live foreign Wags job "
              "is REFUSED (hook installed as .git/hooks/pre-commit)",
              e2e.get("blocked") is True, str(e2e))
        check("20 E2E: the same commit succeeds under MIKE_COMMIT_GATE=warn",
              e2e.get("override_ok") is True, str(e2e))
        check("21 E2E: a gate that cannot find its helper SAYS SO instead of passing silently",
              e2e.get("orphan_warns") is True, str(e2e))

        # ---------- G. the AUTOMATIC CALLERS: is the refusal reported or swallowed? ----------
        # Cases 19-21 drive `git commit` directly and stop at the gate's own exit code. They
        # cannot see what the callers DO with a refusal — and all three automatic ones swallowed
        # it (`2>/dev/null || true`) and printed their success line anyway (arch-review round 2,
        # 2026-08-12). consolidate.sh is the one that matters: ~50 runs/day vs a handful of hand
        # commits, and `git add kb/` with kb/coding_guidelines.md dirty is a shared-tooling path.
        cons = _consolidate_caller()
        check("22 CALLER: consolidate.sh does NOT print its success line when the gate refuses",
              cons.get("blocked_no_false_success") is True, str(cons))
        check("23 CALLER: consolidate.sh reports WHY it could not commit (reason + gate output)",
              cons.get("blocked_says_why") is True and cons.get("blocked_notified") is True,
              str(cons))
        check("24 CALLER: refused run really produced no commit (kb/ left dirty, not lost)",
              cons.get("blocked_no_commit") is True, str(cons))
        # Control — without it, a consolidate.sh that never reports success would pass 22-24.
        check("25 CALLER: with no live foreign job, consolidate.sh DOES commit and DOES say so",
              cons.get("clear_commits") is True and cons.get("clear_says_success") is True,
              str(cons))

        # Cases 22-25 cover consolidate.sh's own log line. kb_nightly.sh Phase 4.6 needed the
        # SAME question asked one level up (arch-review round 3, 2026-08-12): round 2 fixed the
        # log line INSIDE _ctxbloat_autofix_one but left it returning 0 on both branches, so the
        # CALLER still Discord-announced "đã tự nén xong ... đã commit — không cần người can
        # thiệp" on a refused commit and deleted the episode stamp. A log line nobody reads was
        # right while the human-facing channel kept the false success.
        kbn = _kb_nightly_caller()
        check("26 CALLER: kb_nightly Phase 4.6 does NOT tell a human \"đã commit\" when refused",
              kbn.get("blocked_no_false_success") is True, str(kbn))
        check("27 CALLER: refused run says the compression is on disk but NOT committed",
              kbn.get("blocked_says_uncommitted") is True, str(kbn))
        check("28 CALLER: refused run really produced no commit, and the file IS compressed",
              kbn.get("blocked_no_commit") is True and kbn.get("blocked_file_shrunk") is True,
              str(kbn))
        check("29 CALLER: refused run keeps the episode stamp (episode is NOT closed)",
              kbn.get("blocked_stamp_kept") is True, str(kbn))
        # Control — without it, a Phase 4.6 that never reports success would pass 26-29.
        check("30 CALLER: with no live foreign job, Phase 4.6 DOES commit, says ✅ đã commit, "
              "and clears the stamp",
              kbn.get("clear_commits") is True and kbn.get("clear_says_success") is True
              and kbn.get("clear_stamp_removed") is True, str(kbn))
    finally:
        for p in _procs:
            try:
                p.kill()
                p.wait(timeout=5)
            except Exception:
                pass
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n%d/%d PASS" % (len(PASS), len(PASS) + len(FAIL)))
    if FAIL:
        print("FAILED: " + "; ".join(FAIL))
    return 1 if FAIL else 0


def _config_wired():
    p = os.path.join(ROOT, ".pre-commit-config.yaml")
    try:
        with open(p, encoding="utf-8") as f:
            txt = f.read()
    except Exception:
        return False
    if "repo_commit_gate.sh" not in txt:
        return False
    blk = txt[txt.index("repo_commit_gate.sh"):]
    blk = blk[:blk.index("\n  - ") if "\n  - " in blk else len(blk)]
    return "always_run: true" in blk and "pass_filenames: false" in blk


def _wrapper_modes():
    """Drive the real wrapper against a throwaway git repo with a live Wags job, once per
    mode. Exercises the exit-code policy, not just the classifier."""
    out = {}
    tmp = tempfile.mkdtemp(prefix="ccgate_wrap_")
    try:
        repo = os.path.join(tmp, "mike")
        os.makedirs(os.path.join(repo, "bin"))
        os.makedirs(os.path.join(repo, "bus", "jobs"))
        shutil.copy(GATE, os.path.join(repo, "bin", "repo_commit_gate.sh"))
        shutil.copy(MJ, os.path.join(repo, "bin", "mike_json.py"))
        env0 = dict(os.environ)
        env0.pop("JOB_ID", None)
        for c in (["git", "init", "-q"], ["git", "config", "user.email", "t@t"],
                  ["git", "config", "user.name", "t"]):
            subprocess.run(c, cwd=repo, capture_output=True, env=env0)
        with open(os.path.join(repo, "bin", "dispatch.sh"), "w") as f:
            f.write("#!/bin/bash\n")
        subprocess.run(["git", "add", "bin/dispatch.sh"], cwd=repo, capture_output=True, env=env0)
        write_job(os.path.join(repo, "bus", "jobs"), "Wags_wrapfix", pid=sleeper(), to="Wags")
        for mode in ("off", "warn", "block"):
            e = dict(env0)
            e["MIKE_COMMIT_GATE"] = mode
            r = subprocess.run(["bash", os.path.join(repo, "bin", "repo_commit_gate.sh")],
                               cwd=repo, capture_output=True, text=True, env=e)
            out[mode] = r.returncode
            if mode == "warn" and "downgraded" not in r.stderr:
                out[mode] = "warn-mode did not announce the downgrade"
            if mode == "off" and r.stderr.strip():
                out[mode] = "off-mode printed something"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return out


def _e2e():
    """Drive a real `git commit` through the gate installed as .git/hooks/pre-commit."""
    res = {}
    tmp = tempfile.mkdtemp(prefix="ccgate_e2e_")
    try:
        repo = os.path.join(tmp, "mike")
        os.makedirs(os.path.join(repo, "bin"))
        os.makedirs(os.path.join(repo, "bus", "jobs"))
        shutil.copy(MJ, os.path.join(repo, "bin", "mike_json.py"))
        env = dict(os.environ)
        env.pop("JOB_ID", None)
        for c in (["git", "init", "-q", "."], ["git", "config", "user.email", "t@t"],
                  ["git", "config", "user.name", "t"]):
            subprocess.run(c, cwd=repo, capture_output=True, env=env)
        hook = os.path.join(repo, ".git", "hooks", "pre-commit")
        shutil.copy(GATE, hook)
        os.chmod(hook, 0o755)
        write_job(os.path.join(repo, "bus", "jobs"), "Wags_e2e", pid=sleeper(), to="Wags")

        def commit(msg, extra_env=None):
            e = dict(env)
            e.update(extra_env or {})
            return subprocess.run(["git", "commit", "-q", "-m", msg], cwd=repo,
                                  capture_output=True, text=True, env=e)

        def head_count():
            r = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo,
                               capture_output=True, text=True, env=env)
            return int(r.stdout.strip() or 0)

        with open(os.path.join(repo, "bin", "dispatch.sh"), "w") as f:
            f.write("#!/bin/bash\n")
        subprocess.run(["git", "add", "bin/dispatch.sh"], cwd=repo, capture_output=True, env=env)
        r = commit("fix(dispatch): e2e")
        res["blocked"] = r.returncode != 0 and head_count() == 0
        res["blocked_stderr"] = r.stderr.strip()[:120]

        r = commit("fix(dispatch): e2e override", {"MIKE_COMMIT_GATE": "warn"})
        res["override_ok"] = r.returncode == 0 and head_count() == 1

        # gate copied somewhere with no bin/mike_json.py next to it -> must complain, not
        # pass in silence (the bug case 19 caught).
        bare = os.path.join(tmp, "bare")
        os.makedirs(bare)
        shutil.copy(GATE, os.path.join(bare, "repo_commit_gate.sh"))
        subprocess.run(["git", "init", "-q", "."], cwd=bare, capture_output=True, env=env)
        r = subprocess.run(["bash", os.path.join(bare, "repo_commit_gate.sh")], cwd=bare,
                           capture_output=True, text=True, env=env)
        res["orphan_warns"] = r.returncode == 0 and "INACTIVE" in r.stderr
    except Exception as exc:
        res["error"] = repr(exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res


def _consolidate_caller():
    """Run the REAL bin/consolidate.sh in a throwaway repo, in the exact shape it runs in
    production: `git add kb/` while kb/coding_guidelines.md (a SHARED_TOOLING_PATH) is dirty,
    with a foreign live Wags job outside. Asserts the refusal is REPORTED, then — the control
    that keeps this from being tautological — that the same script really does commit and say
    so once the foreign job is gone. Every outbound notifier is stubbed: a selfcheck must never
    reach Discord."""
    res = {}
    tmp = tempfile.mkdtemp(prefix="ccgate_cons_")
    try:
        repo = os.path.join(tmp, "mike")
        shutil.copytree(os.path.join(ROOT, "bin"), os.path.join(repo, "bin"))
        for d in ("kb", "bus/inbox", "bus/jobs", "state/offsets", "locks", "logs"):
            os.makedirs(os.path.join(repo, *d.split("/")), exist_ok=True)
        for s in ("notify.sh", "notify_discord.sh", "notify_telegram.sh", "notify_thread.sh"):
            p = os.path.join(repo, "bin", s)
            with open(p, "w", encoding="utf-8") as f:
                f.write('#!/usr/bin/env bash\nprintf "%s\\n" "$*" '
                        '>> "$(dirname "$0")/../logs/notify_stub.log"\nexit 0\n')
            os.chmod(p, 0o755)
        with open(os.path.join(repo, "kb", "version.txt"), "w", encoding="utf-8") as f:
            f.write("2000\n")
        with open(os.path.join(repo, "kb", "coding_guidelines.md"), "w", encoding="utf-8") as f:
            f.write("# guidelines\n")

        def add_event(n):
            with open(os.path.join(repo, "bus", "inbox", "Taylor.jsonl"), "a",
                      encoding="utf-8") as f:
                f.write(json.dumps({"event_id": "e%d" % n, "ts": "2026-08-12T05:0%d:00Z" % n,
                                    "agent_id": "Taylor", "event_type": "finding",
                                    "topic": "t%d" % n, "payload": "p"}) + "\n")

        env = dict(os.environ)
        env.pop("JOB_ID", None)
        for c in (["git", "init", "-q", "."], ["git", "config", "user.email", "t@t"],
                  ["git", "config", "user.name", "t"], ["git", "add", "-A"],
                  ["git", "commit", "-q", "-m", "init"]):
            subprocess.run(c, cwd=repo, capture_output=True, env=env)
        hook = os.path.join(repo, ".git", "hooks", "pre-commit")
        shutil.copy(GATE, hook)
        os.chmod(hook, 0o755)

        def consolidate():
            return subprocess.run(["bash", os.path.join(repo, "bin", "consolidate.sh")],
                                  cwd=repo, capture_output=True, text=True, env=env)

        def head_count():
            r = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo,
                               capture_output=True, text=True, env=env)
            return int(r.stdout.strip() or 0)

        SUCCESS = "consolidated new events"
        with open(os.path.join(repo, "kb", "coding_guidelines.md"), "a", encoding="utf-8") as f:
            f.write("edited by another session, uncommitted\n")
        write_job(os.path.join(repo, "bus", "jobs"), "Wags_cons", pid=sleeper(), to="Wags")
        add_event(1)
        n0 = head_count()
        r = consolidate()
        out = r.stdout + r.stderr
        res["blocked_no_false_success"] = SUCCESS not in r.stdout
        res["blocked_no_commit"] = head_count() == n0
        res["blocked_says_why"] = "KHÔNG ĐƯỢC COMMIT" in out and "commit-collision" in out
        try:
            with open(os.path.join(repo, "logs", "notify_stub.log"), encoding="utf-8") as f:
                res["blocked_notified"] = "consolidate.sh" in f.read()
        except OSError:
            res["blocked_notified"] = False
        res["blocked_stdout"] = r.stdout.strip()[:160]

        os.remove(os.path.join(repo, "bus", "jobs", "Wags_cons.json"))
        add_event(2)
        n1 = head_count()
        r2 = consolidate()
        res["clear_commits"] = head_count() == n1 + 1
        res["clear_says_success"] = SUCCESS in r2.stdout
    except Exception as exc:
        res["error"] = repr(exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res


def _ctxbloat_block():
    """The REAL Phase 4.6 body of bin/kb_nightly.sh, sliced out by content markers (not by line
    number, and never re-typed): a test against a hand-copied paraphrase proves nothing about
    the script cron runs. Raises if either marker moves — a fixture that silently tests an empty
    string would be worse than no fixture."""
    with open(os.path.join(ROOT, "bin", "kb_nightly.sh"), encoding="utf-8") as f:
        lines = f.read().splitlines(True)
    starts = [i for i, l in enumerate(lines) if l.startswith("_ctx_kb_or_missing() {")]
    ends = [i for i, l in enumerate(lines)
            if l.strip() == 'log "Context-bloat episode cleared."']
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise RuntimeError("kb_nightly.sh Phase 4.6 markers moved: starts=%s ends=%s"
                           % (starts, ends))
    return "".join(lines[starts[0]:ends[0] + 2])   # +2 = the log line and its closing `fi`


def _kb_nightly_caller():
    """Run the REAL kb_nightly.sh Phase 4.6 block in a throwaway repo with the real gate
    installed as .git/hooks/pre-commit and a real live foreign Wags job that declared
    --write-scope over the very file being compressed. Only the outward calls are stubbed —
    dispatch.sh (stands in for the compressing agent) and every notifier, because a selfcheck
    must never reach Discord. The fact-check, the mv, the git add/commit, the return-code
    routing and the caller's message/stamp handling are all the shipped code.

    Asserts the refused commit is reported AS refused on the human channel, then — the control
    that keeps this from being tautological — that the same block really does commit, say
    "đã commit", and close the episode once the foreign job is gone."""
    res = {}
    tmp = tempfile.mkdtemp(prefix="ccgate_kbn_")
    try:
        repo = os.path.join(tmp, "mike")
        shutil.copytree(os.path.join(ROOT, "bin"), os.path.join(repo, "bin"))
        for d in ("kb", "bus/inbox", "bus/jobs", "state", "logs"):
            os.makedirs(os.path.join(repo, *d.split("/")), exist_ok=True)
        notify_log = os.path.join(repo, "logs", "notify_stub.log")
        for s in ("notify.sh", "notify_thread.sh", "notify_discord.sh", "notify_telegram.sh",
                  "append_event.sh"):
            p = os.path.join(repo, "bin", s)
            with open(p, "w", encoding="utf-8") as f:
                f.write('#!/usr/bin/env bash\nprintf "%s\\n" "$*" '
                        '>> "$(dirname "$0")/../logs/notify_stub.log"\nexit 0\n')
            os.chmod(p, 0o755)

        # Facts the mechanical fact-check must find intact on both sides; filler is the only
        # thing the stub "agent" drops (no date/%/KB/sha/job-id/filename tokens in it).
        FACTS = ("# context pack\nFACT 2026-08-12: nguong 45KB, giam 12,5% — commit 0ffda43e,"
                 " job Wags_20260812_052131, file bin/kb_nightly.sh.\n")
        FILLER = "cau van dien giai lap lai, khong mang du lieu moi.\n"
        big = FACTS + FILLER * 1200          # > 45KB
        small = FACTS + FILLER * 200         # < 45KB, every fact kept
        cp = os.path.join(repo, "kb", "context_pack.md")

        def reset_file():
            with open(cp, "w", encoding="utf-8") as f:
                f.write(big)
        reset_file()
        for name, body in (("MIKE.md", "# mike\n"),
                           (os.path.join("kb", "coding_guidelines.md"), "# guidelines\n")):
            with open(os.path.join(repo, name), "w", encoding="utf-8") as f:
                f.write(body)

        # dispatch.sh stub = the compressing agent: writes the .proposed sibling and stops,
        # exactly what the real prompt demands. The caller still runs ctxbloat_fact_check.py
        # on it for real.
        with open(os.path.join(repo, "bin", "dispatch.sh"), "w", encoding="utf-8") as f:
            f.write('#!/usr/bin/env bash\ncat > "$(dirname "$0")/../kb/context_pack.md.proposed"'
                    " <<'EOF'\n" + small + "EOF\nexit 0\n")
        os.chmod(os.path.join(repo, "bin", "dispatch.sh"), 0o755)

        env = dict(os.environ)
        env.pop("JOB_ID", None)
        for c in (["git", "init", "-q", "."], ["git", "config", "user.email", "t@t"],
                  ["git", "config", "user.name", "t"], ["git", "add", "-A"],
                  ["git", "commit", "-q", "-m", "init"]):
            subprocess.run(c, cwd=repo, capture_output=True, env=env)
        hook = os.path.join(repo, ".git", "hooks", "pre-commit")
        shutil.copy(GATE, hook)
        os.chmod(hook, 0o755)

        runner = os.path.join(repo, "run_phase46.sh")
        with open(runner, "w", encoding="utf-8") as f:
            f.write('#!/usr/bin/env bash\nset -euo pipefail\n'
                    'ROOT="%s"\ncd "$ROOT"\nLOG="$ROOT/logs/kb_nightly.log"\n'
                    'log() { echo "[selfcheck] $*" | tee -a "$LOG"; }\n\n' % repo
                    + _ctxbloat_block())
        stamp = os.path.join(repo, "state", "ctxbloat_episode.txt")

        def run_phase():
            for p in (stamp, os.path.join(repo, "state", "ctxbloat_autofix_attempted.txt")):
                if os.path.exists(p):
                    os.remove(p)
            open(notify_log, "w").close()
            return subprocess.run(["bash", runner], cwd=repo, capture_output=True, text=True,
                                  env=env)

        def head_count():
            r = subprocess.run(["git", "rev-list", "--count", "HEAD"], cwd=repo,
                               capture_output=True, text=True, env=env)
            return int(r.stdout.strip() or 0)

        def notified():
            with open(notify_log, encoding="utf-8") as f:
                return f.read()

        # --- BLOCKED: a live Wags job declared it is writing the very file we compress ---
        write_job(os.path.join(repo, "bus", "jobs"), "Wags_ctx", pid=sleeper(), to="Wags",
                  write_scope="kb/context_pack.md")
        n0 = head_count()
        r = run_phase()
        msg = notified()
        res["blocked_rc"] = r.returncode
        res["blocked_no_false_success"] = "đã commit" not in msg and "✅" not in msg
        res["blocked_says_uncommitted"] = "CHƯA COMMIT" in msg and "COMMIT TAY" in msg
        res["blocked_no_commit"] = head_count() == n0
        res["blocked_file_shrunk"] = os.path.getsize(cp) == len(small.encode("utf-8"))
        res["blocked_stamp_kept"] = os.path.exists(stamp)
        res["blocked_notify"] = msg.strip()[:200]

        # --- CONTROL: same block, same breach, no foreign job → must really commit ---
        os.remove(os.path.join(repo, "bus", "jobs", "Wags_ctx.json"))
        reset_file()
        subprocess.run(["git", "reset", "-q", "HEAD", "--", "."], cwd=repo,
                       capture_output=True, env=env)
        n1 = head_count()
        r2 = run_phase()
        msg2 = notified()
        res["clear_rc"] = r2.returncode
        res["clear_commits"] = head_count() == n1 + 1
        res["clear_says_success"] = "✅" in msg2 and "đã commit" in msg2
        res["clear_stamp_removed"] = not os.path.exists(stamp)
    except Exception as exc:
        res["error"] = repr(exc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return res


if __name__ == "__main__":
    sys.exit(main())
