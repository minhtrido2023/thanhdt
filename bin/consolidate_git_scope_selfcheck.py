# -*- coding: utf-8 -*-
"""Regression self-check for consolidate.sh's git-commit SCOPE (added 2026-07-28, user directive
after `git -C "$ROOT" add -A` — repo-wide — silently swept an unrelated in-progress code edit
into an auto-generated "consolidate KB vNNNN" commit message TWICE during the same session,
replacing a carefully-written rationale with a one-liner. consolidate.sh only ever writes inside
kb/ (context_pack.md, events_buffer.md, version.txt, recent_delta.jsonl, fleet_status.md) — the
fix scopes the add to `kb/`, matching kb_nightly.sh's existing `git add kb/` convention.

Runs the REAL consolidate.sh end-to-end in an isolated sandbox (own .git, own bus/inbox), not a
re-implementation of its git logic — same reasoning as cursor_advance_selfcheck.py's sandbox O
section: a re-implementation can silently drift from the file it's supposed to be testing.

Run: python3 consolidate_git_scope_selfcheck.py   (exit 0 = all pass)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
fails = []
total = 0


def check(name, cond, detail=""):
    global total
    total += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def sh(cmd, cwd, check_rc=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=30)
    if check_rc and r.returncode != 0:
        raise RuntimeError(f"{cmd} failed rc={r.returncode}\nSTDOUT:{r.stdout}\nSTDERR:{r.stderr}")
    return r.stdout.strip()


def build_sandbox():
    d = tempfile.mkdtemp(prefix="consolidate_gitscope_")
    for sub in ["bin", "kb", "bus/inbox", "bus/registry", "bus/directives",
                "state/offsets", "locks", "logs"]:
        os.makedirs(os.path.join(d, sub), exist_ok=True)
    shutil.copy(os.path.join(ROOT, "consolidate.sh"), os.path.join(d, "bin", "consolidate.sh"))
    shutil.copy(os.path.join(ROOT, "mike_json.py"), os.path.join(d, "bin", "mike_json.py"))
    shutil.copy(os.path.join(ROOT, "publish_context.sh"), os.path.join(d, "bin", "publish_context.sh"))
    for name in ["notify.sh", "notify_discord.sh"]:
        p = os.path.join(d, "bin", name)
        with open(p, "w") as f:
            f.write("#!/usr/bin/env bash\nexit 0\n")
        os.chmod(p, 0o755)
    sh(["git", "init", "-q"], cwd=d)
    sh(["git", "config", "user.email", "selfcheck@test"], cwd=d)
    sh(["git", "config", "user.name", "selfcheck"], cwd=d)
    with open(os.path.join(d, "kb", "context_pack.md"), "w") as f:
        f.write("seed\n")
    sh(["git", "add", "-A"], cwd=d)
    sh(["git", "commit", "-q", "-m", "seed"], cwd=d)
    return d


def write_event(sandbox, agent, event_id, topic="test"):
    line = json.dumps({"event_id": event_id, "ts": "2026-07-28T01:00:00Z",
                        "event_type": "finding", "agent_id": agent, "topic": topic})
    with open(os.path.join(sandbox, "bus", "inbox", f"{agent}.jsonl"), "a") as f:
        f.write(line + "\n")


sandbox = tempfile.mkdtemp(prefix="_placeholder_")  # replaced below; keeps lints quiet
shutil.rmtree(sandbox, ignore_errors=True)
sandbox = build_sandbox()

# ── A. A real new bus event exists (forces the commit code path) AND an unrelated file
#      outside kb/ is sitting dirty in the working tree (simulating an in-progress code edit,
#      exactly the 2026-07-28 scenario) — the resulting commit must NOT include it. ───────────
write_event(sandbox, "Test", "e1")
with open(os.path.join(sandbox, "bin", "unrelated_wip_script.sh"), "w") as f:
    f.write("# work in progress, not meant to be committed by consolidate.sh\n")
with open(os.path.join(sandbox, "unrelated_root_file.md"), "w") as f:
    f.write("also in progress\n")

r = subprocess.run(["bash", os.path.join(sandbox, "bin", "consolidate.sh")],
                    cwd=sandbox, capture_output=True, text=True, timeout=30)
check("A1 consolidate.sh runs without error", r.returncode == 0, f"stderr={r.stderr[:300]}")

log_line = sh(["git", "log", "--oneline", "-1"], cwd=sandbox)
check("A2 a new commit was actually made (event path exercised, not the no-op branch)",
      "seed" not in log_line, log_line)

committed_files = sh(["git", "show", "--stat", "--format=", "HEAD"], cwd=sandbox)
check("A3 the unrelated bin/ script was NOT swept into the commit",
      "unrelated_wip_script.sh" not in committed_files, committed_files)
check("A4 the unrelated root file was NOT swept into the commit",
      "unrelated_root_file.md" not in committed_files, committed_files)
check("A5 the real kb/ change WAS committed (fix didn't just stop committing anything)",
      "kb/" in committed_files, committed_files)

status_after = sh(["git", "status", "--porcelain"], cwd=sandbox)
check("A6 the unrelated files are still present, uncommitted, untouched (not deleted/reverted)",
      "unrelated_wip_script.sh" in status_after and "unrelated_root_file.md" in status_after,
      status_after)

# ── C. The residual round-2 review found: `git add kb/` only controls what gets STAGED —
#      `git commit` with no pathspec commits the WHOLE INDEX. A file some OTHER in-flight
#      session already `git add`-ed (staged, not yet committed) a moment before consolidate.sh
#      runs must NOT ride along into "consolidate KB vNNNN" just because it's sitting in the
#      index. This is the scenario `add kb/` alone does not close. ─────────────────────────────
sandbox2 = build_sandbox()
write_event(sandbox2, "Test", "e1")
with open(os.path.join(sandbox2, "bin", "preexisting.sh"), "w") as f:
    f.write("# a change someone else already `git add`-ed but hasn't committed yet\n")
sh(["git", "add", "bin/preexisting.sh"], cwd=sandbox2)  # STAGED, not committed — the real trigger

r_c = subprocess.run(["bash", os.path.join(sandbox2, "bin", "consolidate.sh")],
                      cwd=sandbox2, capture_output=True, text=True, timeout=30)
check("C1 consolidate.sh runs without error", r_c.returncode == 0, f"stderr={r_c.stderr[:300]}")
committed_c = sh(["git", "show", "--stat", "--format=", "HEAD"], cwd=sandbox2)
check("C2 a pre-STAGED file outside kb/ is NOT swept into the commit",
      "preexisting.sh" not in committed_c, committed_c)
check("C3 the real kb/ change still gets committed", "kb/" in committed_c, committed_c)
status_c = sh(["git", "status", "--porcelain"], cwd=sandbox2)
check("C4 the pre-staged file is still staged afterward (not committed, not unstaged/lost)",
      "A  bin/preexisting.sh" in status_c, status_c)
shutil.rmtree(sandbox2, ignore_errors=True)

# ── B. Steady state (no new events): must not create an empty/spurious commit, and must not
#      touch the unrelated dirty files either. ──────────────────────────────────────────────
before_log = sh(["git", "log", "--oneline", "-1"], cwd=sandbox)
r2 = subprocess.run(["bash", os.path.join(sandbox, "bin", "consolidate.sh")],
                     cwd=sandbox, capture_output=True, text=True, timeout=30)
after_log = sh(["git", "log", "--oneline", "-1"], cwd=sandbox)
check("B1 no new events -> no new commit", before_log == after_log,
      f"before={before_log} after={after_log}")
status_after2 = sh(["git", "status", "--porcelain"], cwd=sandbox)
check("B2 unrelated files still untouched after a no-op run",
      "unrelated_wip_script.sh" in status_after2, status_after2)

print()
shutil.rmtree(sandbox, ignore_errors=True)
if fails:
    print(f"FAIL: {len(fails)}/{total} — {fails}")
    sys.exit(1)
print(f"ALL PASS: {total}/{total}")
sys.exit(0)
