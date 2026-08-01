#!/usr/bin/env bash
# shellcheck_gate.sh <file.sh> [file2.sh ...]
#
# Pre-commit gate — runs ShellCheck (industry-standard bash static analyzer, installed via
# `pip install shellcheck-py`, no sudo needed) and HARD-BLOCKS the commit only on a curated
# list of SC codes that have caused REAL incidents in this repo. Everything else ShellCheck
# finds is printed as advisory, non-blocking.
#
# WHY curated, not "block on any finding": a raw `shellcheck bin/*.sh` run today returns 76
# pre-existing findings (0 error / 23 warning / 49 info / 4 style) across ~45 scripts that
# predate this gate — blocking on ALL of them on day one would stop every future commit dead
# until a full backlog cleanup, which is not what "add a check that prevents recurrence" means
# in practice (see kb/incidents/2026-08/2026-08-01-shellcheck-precommit-gate.md). Instead this
# gate hard-blocks a SMALL, PROVEN list of codes and lets the block-list grow the same way any
# lint rule grows: a NEW incident traces to a NEW SC code -> add it here in the same commit as
# the fix + the kb/incidents/ entry, exactly like a semgrep/CI rule written from a real bug
# (industry pattern: "a rule that fires twice with 100% accuracy beats one that fires 200 times
# with 50%" — write the rule FROM the incident, don't try to boil the ocean up front).
#
# Curated hard-block codes (each mapped to a REAL incident this exact code would have caught,
# verified empirically against the actual buggy historical commit before adding):
#   SC1078/SC1079 — unterminated/suspicious string (unescaped " inside a multi-line
#                   double-quoted bash string) -> kb_nightly.sh item 5b, 2026-07-17..2026-08-01
#                   (2 weeks silent Friday/Saturday dispatch failure).
#   SC2006        — legacy backtick `...` inside a string meant as literal prose, not real
#                   command substitution -> kb_nightly.sh item 7, same incident.
#   SC2261        — multiple redirections competing (classic symptom of a quote breaking mid-
#                   string and leftover text being reparsed as shell syntax) -> daily_retro.sh,
#                   2026-07-31/08-01 (2 nights silent crash).
#
# Tried and DROPPED: SC2154 (variable referenced but never assigned) — real signal for the
# daily_retro.sh break (draft_prompt never assigned), but produces false positives across
# hooks/*.sh where variables are legitimately set via `source` chains ShellCheck doesn't
# auto-follow (see SC1091 "Not following" on the same lines) — tested against this repo's real
# hooks/session_start.sh etc. before deciding, per the "verify against real files, don't guess"
# discipline. SC2261 alone already catches the daily_retro.sh incident class without it.
set -uo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="$HOME/.local/bin:$PATH"

HARD_BLOCK_CODES="1078 1079 2006 2261"

if [ "$#" -eq 0 ]; then
  echo "usage: shellcheck_gate.sh <file.sh> [...]" >&2
  exit 0
fi

if ! command -v shellcheck >/dev/null 2>&1; then
  echo "⚠️ shellcheck not found on PATH (expected ~/.local/bin from 'pip install shellcheck-py') — skipping gate, not blocking commit." >&2
  exit 0
fi

BLOCKED=0
for f in "$@"; do
  [ -f "$f" ] || continue
  json_file="$(mktemp)"
  shellcheck -f json "$f" > "$json_file" 2>/dev/null || true
  if [ ! -s "$json_file" ]; then
    rm -f "$json_file"
    continue
  fi
  result="$(python3 - "$f" "$HARD_BLOCK_CODES" "$json_file" <<'PYEOF'
import json, sys
f, hard_codes, json_file = sys.argv[1], set(int(c) for c in sys.argv[2].split()), sys.argv[3]
with open(json_file) as fh:
    findings = json.load(fh) or []
blocking, advisory = [], []
for it in findings:
    (blocking if it["code"] in hard_codes else advisory).append(it)
for it in advisory:
    print(f"  ℹ️  {f}:{it['line']}: SC{it['code']} ({it['level']}) {it['message']}")
for it in blocking:
    print(f"  🔴 {f}:{it['line']}: SC{it['code']} ({it['level']}) {it['message']} [HARD-BLOCK]")
print(f"__BLOCKED__={len(blocking)}")
PYEOF
  )"
  rm -f "$json_file"
  echo "$result" | grep -v '^__BLOCKED__='
  n="$(echo "$result" | grep '^__BLOCKED__=' | cut -d= -f2)"
  BLOCKED=$(( BLOCKED + ${n:-0} ))
done

if [ "$BLOCKED" -gt 0 ]; then
  echo "" >&2
  echo "🔴 shellcheck_gate: $BLOCKED hard-blocking finding(s) (🔴 above) — fix before commit." >&2
  echo "   Not one of these but genuinely a new incident-causing pattern? Add its SC code to" >&2
  echo "   HARD_BLOCK_CODES in bin/shellcheck_gate.sh (same commit as the fix + kb/incidents/ entry)." >&2
  echo "   Advisory (ℹ️) findings above are informational only — not blocking." >&2
  exit 1
fi
exit 0
