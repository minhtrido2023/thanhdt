#!/usr/bin/env bash
# repo_commit_gate.sh — pre-commit gate: refuse to commit shared fleet tooling while ANOTHER
# agent's job is live in this same working copy.
#
# WHY (three occurrences of one shape, none of them caught by anything shipped):
#   2026-07-31, 2026-08-02, 2026-08-12 — a commit made from OUTSIDE a running job swept that
#   job's staged-but-uncommitted files into itself. No data was lost any of the three times;
#   what breaks is provenance (wrong author, wrong message, one fix's files buried inside
#   another's commit) and, worse, the running job then commits an EMPTY or partial change set
#   and reports success. The 2026-08-12 instance: Mike committed f827f6df ("dispatch.sh fix")
#   while job Wags_20260812_035748 was live in the same repo; six of Wags' files rode along.
#
# WHY THIS AND NOT THE TWO THINGS ALREADY TRIED:
#   - bin/job_workspace.py (worktree pool) was bounced twice by arch-reviewer and dropped by
#     user decision (a) on 2026-08-11: `reset --hard`/`clean -fd` had a path that resolved
#     into the production repo, isolation was 0% for the `claude` provider, and the merge-back
#     gate could hang forever on a stable-but-continuously-written file. Do not re-propose it.
#   - dispatch.sh --write-scope (f58bd88a) is OPT-IN and fires at DISPATCH time. It cannot see
#     a bare `git commit`, and on 2026-08-12 NEITHER side had declared a scope. This gate asks
#     the question at the one moment every writer passes through, and needs nobody to remember.
#
# WHY IT DOES NOT BLOCK ON "any job is live": measured over 14 days of real history, 56% of
# hand-authored commits in this repo happen while at least one job is live. A gate that fires
# on that is the permanent-block failure mode that killed the worktree pool. So: BLOCK only on
# evidence pointed at THESE paths (a declared --write-scope overlap, or shared fleet tooling
# with a live job of the agent whose charter that tooling is), WARN on everything else.
#
# Modes (env MIKE_COMMIT_GATE):
#   block (default) — BLOCK lines are fatal, WARN lines print and pass.
#   warn            — everything prints, nothing is fatal. The documented escape when the
#                     other job genuinely is not touching your files and you must ship now.
#   off             — gate does not run.
# `git commit --no-verify` also bypasses, as with every other hook here.
#
# FAILS OPEN on every internal error. A gate that can brick the repo when its own helper has a
# syntax error is a worse outage than the collision it prevents.

set -uo pipefail

[ "${MIKE_COMMIT_GATE:-block}" = "off" ] && exit 0

# ROOT from git, NOT from BASH_SOURCE. Caught by the end-to-end test: invoked as a copied
# .git/hooks/pre-commit (a normal way to install a hook without pre-commit), dirname/.. lands
# on `.git`, bin/mike_json.py is not there, and the fail-open path made the gate a no-op that
# printed nothing at all. A dead gate that announces nothing is worse than no gate — you stop
# looking. BASH_SOURCE stays as the fallback for the pre-commit invocation.
ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
[ -n "$ROOT" ] && [ -f "$ROOT/bin/mike_json.py" ] || \
  ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." 2>/dev/null && pwd)"
cd "$ROOT" 2>/dev/null || exit 0
if [ ! -f "$ROOT/bin/mike_json.py" ]; then
  printf '⚠️  commit-collision gate INACTIVE: bin/mike_json.py not found under %s\n' "$ROOT" >&2
  exit 0
fi

mapfile -t staged < <(git diff --cached --name-only --diff-filter=ACMRD 2>/dev/null)
[ "${#staged[@]}" -eq 0 ] && exit 0

# --self-pid: this script is a descendant of `git commit`, which is a descendant of whatever
# shell the committer is using — so a job that is committing its OWN work at the end of its
# run finds itself in this pid's ancestor chain and is excluded. Without this, the gate would
# fire on nearly every Wags fix commit (Wags commits from inside its own live job by design).
if ! out="$(python3 "$ROOT/bin/mike_json.py" commit-collision-gate "$ROOT/bus/jobs" \
             --self-pid "$$" "${staged[@]}" 2>&1)"; then
  # Still fail-open, but never silently: see the ROOT comment above.
  printf '⚠️  commit-collision gate ERRORED (commit allowed): %s\n' "${out:-no output}" >&2
  exit 0
fi
[ -z "$out" ] && exit 0

blocked=0
while IFS='|' read -r verdict jid to from age why hits; do
  [ -z "${verdict:-}" ] && continue
  if [ "$verdict" = "BLOCK" ] && [ "${MIKE_COMMIT_GATE:-block}" = "block" ]; then
    blocked=1
    printf '⛔ commit-collision: job %s (%s->%s, live %ss) — %s\n' "$jid" "$from" "$to" "$age" "$why" >&2
    printf '   paths: %s\n' "$hits" >&2
  elif [ "$verdict" = "BLOCK" ]; then
    printf '⚠️  commit-collision (downgraded by MIKE_COMMIT_GATE=warn): job %s (%s->%s, live %ss) — %s\n' \
      "$jid" "$from" "$to" "$age" "$why" >&2
    printf '   paths: %s\n' "$hits" >&2
  else
    printf '⚠️  commit-collision: job %s (%s->%s, live %ss) — %s\n' "$jid" "$from" "$to" "$age" "$why" >&2
  fi
done <<< "$out"

if [ "$blocked" = "1" ]; then
  cat >&2 <<'EOF'

   Another agent's job is live in THIS working copy and the shared git index is not yours
   alone: `git add` by that job stages into the same index your `git commit` writes out.
   Choose one:
     1. wait for it        — bin/jobs.sh list   (then commit normally)
     2. let it finish first, or cancel it       — bin/jobs.sh status <job_id>
     3. ship anyway, on purpose:  MIKE_COMMIT_GATE=warn git commit ...
   If you take (3), check `git show --stat HEAD` afterwards for files you did not write.
EOF
  exit 1
fi
exit 0
