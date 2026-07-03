#!/usr/bin/env bash
# verification_audit.sh <agent_id> [days]
#
# Audit REPORT (not a gate — nothing here blocks anything): every `finding` event from
# <agent_id> in the last N days (default 14), and whether a quant-skeptic `verification`
# event with the same trace_id exists anywhere on the bus.
#
# Grounding: MIKE.md already has a written rule ("finding R&D quan trọng ... phải qua
# reviewer trước khi wire", "REFUTED/INCONCLUSIVE = KHÔNG wire") but enforcement has been
# manual — whoever remembers to run verify_finding.sh. This makes coverage visible instead
# of requiring a manual grep across every agent's inbox. It deliberately does NOT try to
# guess which findings were "important enough" to need verification (a keyword classifier
# for that would be fragile and noisy) — that judgment stays with Mike/user. Read the table,
# decide for yourself which UNVERIFIED rows matter.
#
# Findings from before the 2026-07-03 trace_id fix show "trace=none" (can't be correlated
# retroactively, not the same as UNVERIFIED).
#
# Read-only. Depends only on python3 (via mike_json.py).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

agent="${1:?usage: verification_audit.sh <agent_id> [days]}"
days="${2:-14}"

python3 "$ROOT/bin/mike_json.py" verify-coverage "$ROOT/bus" "$agent" "$days"
