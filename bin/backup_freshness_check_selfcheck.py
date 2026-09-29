#!/usr/bin/env python3
"""backup_freshness_check_selfcheck.py — extract-and-test the check_repo() function of
bin/backup_freshness_check.sh against constructed git states with controlled commit
timestamps, in a throwaway sandbox (works under `env -u TZ`).

Why extract instead of duplicate: the function body is sed/awk-extracted from the REAL
file at run time, not retyped here — if someone edits check_repo() without keeping the
anchor lines in sync, this script breaks loudly instead of silently testing stale code.

Built coord-2026-09-10 (arch-review Wags_20260909_012007 required_change #5: 0 selfcheck
files despite bin/ already having 77). The case that actually matters here is (e): HEAD on
remote pushed recently by a MANUAL commit while the automated `auto-backup <ts>` pipeline
is dead behind it — invariant #1 (HEAD age) reports clean, invariant #3 (auto-backup commit
age, added coord-2026-09-10) must be the one that catches it. A negative control re-runs
the OLD check_repo() (pre invariant-3) on the exact same state and must show the problem
that fix is meant to close: it stays silent.
"""
import subprocess
import sys
import tempfile
import time
from pathlib import Path

REAL = Path("/home/trido/thanhdt/WorkingClaude/mike/bin/backup_freshness_check.sh")
PASS = 0
FAIL = 0


def extract_snippet():
    text = REAL.read_text()
    lines = text.splitlines()
    start = end = None
    for i, ln in enumerate(lines):
        if ln.startswith("MAX_AGE_H="):
            start = i
        if start is not None and ln.startswith('check_repo "workspace'):
            end = i
            break
    if start is None or end is None:
        print("FAIL: extraction anchors (MAX_AGE_H= / check_repo \"workspace) not found "
              "— backup_freshness_check.sh was restructured, this selfcheck is stale",
              file=sys.stderr)
        sys.exit(1)
    return "\n".join(lines[start:end])


def old_check_repo():
    """check_repo() as it existed BEFORE coord-2026-09-10 (no invariant #3) — the negative
    control target. Kept verbatim so the control demonstrably has the gap the fix closes."""
    return '''
MAX_AGE_H="${BACKUP_MAX_AGE_H:-30}"
NOW="$(date -u +%s)"
PROBLEMS=""
LINES=""
check_repo() {
  local label="$1" repo="$2" remote="$3" branch="$4"
  local rsha lsha age_h behind_h
  rsha="$(timeout 60 git -C "$repo" ls-remote "$remote" "$branch" 2>/dev/null | awk 'NR==1{print $1}')"
  if [ -z "$rsha" ]; then
    PROBLEMS="${PROBLEMS}- $label: KHONG doc duoc remote\\n"
    return
  fi
  if ! git -C "$repo" cat-file -e "$rsha^{commit}" 2>/dev/null; then
    timeout 120 git -C "$repo" fetch -q "$remote" "$branch" 2>/dev/null || true
  fi
  if git -C "$repo" cat-file -e "$rsha^{commit}" 2>/dev/null; then
    age_h=$(( (NOW - $(git -C "$repo" log -1 --format=%ct "$rsha")) / 3600 ))
    if [ "$age_h" -gt "$MAX_AGE_H" ]; then
      PROBLEMS="${PROBLEMS}- $label: ban tren GitHub da ${age_h}h tuoi\\n"
    fi
  fi
  lsha="$(git -C "$repo" rev-parse HEAD 2>/dev/null)" || return
  if [ "$lsha" != "$rsha" ]; then
    if git -C "$repo" merge-base --is-ancestor "$rsha" "$lsha" 2>/dev/null; then
      behind_h=$(( (NOW - $(git -C "$repo" log -1 --format=%ct "$lsha")) / 3600 ))
      if [ "$behind_h" -gt "$MAX_AGE_H" ]; then
        PROBLEMS="${PROBLEMS}- $label: commit local chua push, da ${behind_h}h\\n"
      fi
    else
      PROBLEMS="${PROBLEMS}- $label: PHAN NHANH\\n"
    fi
  fi
}
'''


def run_bash(snippet, call_line):
    script = snippet + "\n" + call_line + '\nprintf "%s" "$PROBLEMS"\n'
    out = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60)
    return out.stdout, out.stderr


def git(cwd, *args, env=None):
    subprocess.run(["git", "-C", str(cwd)] + list(args), check=True,
                    capture_output=True, text=True, env=env)


def commit_at(cwd, msg, hours_ago):
    ts = int(time.time()) - hours_ago * 3600
    date = f"{ts} +0000"
    import os
    env = dict(**os.environ, GIT_AUTHOR_DATE=date, GIT_COMMITTER_DATE=date)
    git(cwd, "add", "-A")
    subprocess.run(["git", "-C", str(cwd), "commit", "-q", "-m", msg], check=True,
                    capture_output=True, text=True, env=env)


def new_repo(root):
    bare = root / "remote.git"
    work = root / "work"
    git(root, "init", "-q", "--bare", "-b", "main", str(bare))
    subprocess.run(["git", "init", "-q", "-b", "main", str(work)], check=True, capture_output=True)
    git(work, "config", "user.email", "x@test")
    git(work, "config", "user.name", "x")
    git(work, "remote", "add", "origin", str(bare))
    return bare, work


def push(work):
    git(work, "push", "-q", "origin", "main")


def check(name, condition, extra=""):
    global PASS, FAIL
    if condition:
        print(f"PASS: {name}")
        PASS += 1
    else:
        print(f"FAIL: {name} {extra}")
        FAIL += 1


CALL = 'check_repo "test" "{work}" origin main "{grep}"'


def case_clean():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare, work = new_repo(root)
        (work / "f").write_text("v0")
        commit_at(work, "auto-backup 2026-09-10T00:00:00Z", hours_ago=2)
        push(work)
        snippet = extract_snippet()
        out, err = run_bash(snippet, CALL.format(work=work, grep="^auto-backup "))
        check("clean-state-no-problems", out.strip() == "", extra=f"PROBLEMS={out!r} err={err[-300:]}")


def case_stale_head():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare, work = new_repo(root)
        (work / "f").write_text("v0")
        commit_at(work, "auto-backup old", hours_ago=40)
        push(work)
        snippet = extract_snippet()
        out, _ = run_bash(snippet, CALL.format(work=work, grep="^auto-backup "))
        check("stale-head-caught-by-invariant-1", "40h tuoi" in out or "40h tuổi" in out, extra=out)


def case_unpushed_local():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare, work = new_repo(root)
        (work / "f").write_text("v0")
        commit_at(work, "auto-backup base", hours_ago=50)
        push(work)
        (work / "f").write_text("v1")
        commit_at(work, "auto-backup unpushed", hours_ago=40)
        snippet = extract_snippet()
        out, _ = run_bash(snippet, CALL.format(work=work, grep="^auto-backup "))
        check("unpushed-local-caught-by-invariant-2", "chưa push" in out or "chua push" in out, extra=out)


def case_diverged():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare, work = new_repo(root)
        (work / "f").write_text("v0")
        commit_at(work, "auto-backup base", hours_ago=5)
        push(work)
        other = root / "other"
        subprocess.run(["git", "clone", "-q", str(bare), str(other)], check=True, capture_output=True)
        git(other, "checkout", "-q", "-B", "main", "origin/main")
        git(other, "config", "user.email", "y@test")
        git(other, "config", "user.name", "y")
        (other / "f").write_text("remote_side")
        commit_at(other, "auto-backup remote-side", hours_ago=1)
        push(other)
        (work / "f").write_text("local_side")
        commit_at(work, "auto-backup local-side", hours_ago=1)
        snippet = extract_snippet()
        out, _ = run_bash(snippet, CALL.format(work=work, grep="^auto-backup "))
        check("diverged-caught", "PHÂN NHÁNH" in out or "PHAN NHANH" in out, extra=out)


def case_manual_push_masks_dead_pipeline():
    """THE case invariant #3 exists for: HEAD on remote is fresh (a human pushed by hand),
    but the last *automated* commit underneath it is stale — pipeline has been dead for
    days and invariant #1 alone reports clean."""
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        bare, work = new_repo(root)
        (work / "f").write_text("v0")
        commit_at(work, "auto-backup last-automated-run", hours_ago=48)
        push(work)
        (work / "f").write_text("v1 (nguoi sua tay)")
        commit_at(work, "manual fix, not from pipeline", hours_ago=1)
        push(work)
        snippet = extract_snippet()
        new_out, _ = run_bash(snippet, CALL.format(work=work, grep="^auto-backup "))
        check("new-invariant3-catches-dead-pipeline-under-fresh-head",
              "48h tuổi" in new_out or "48h tuoi" in new_out, extra=new_out)

        old_out, _ = run_bash(old_check_repo(), CALL.format(work=work, grep="^auto-backup "))
        check("negative-control-old-check-repo-stays-silent-on-same-state",
              old_out.strip() == "", extra=f"old code should be blind here but printed: {old_out!r}")


if __name__ == "__main__":
    case_clean()
    case_stale_head()
    case_unpushed_local()
    case_diverged()
    case_manual_push_masks_dead_pipeline()
    print(f"\nbackup_freshness_check_selfcheck: {PASS} PASS, {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)
