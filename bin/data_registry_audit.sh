#!/usr/bin/env bash
# data_registry_audit.sh — periodic correctness + freshness audit for kb/data_registry.md
#
# Built 2026-07-11 (user directive, after SIGNAL_V11 base-leak incident): a written registry
# with a Status column is not self-enforcing — nothing had ever re-checked that the exact
# files bitten by that incident hadn't regressed, or that a deprecated/trap source wasn't
# quietly gaining new readers. This script is the mechanical half of that check; judgment
# calls (should we deprecate X, is this drift acceptable) stay with Winston/Mike/user.
#
# Report-only — never edits code or the registry. Wired into kb_nightly.sh's Friday
# editorial-review dispatch (Phase 5); can also be run ad-hoc.
#
# Exit codes: 0 = all clean, 1 = at least one FAIL (regression/dead writer), 2 = WARN only.

set -uo pipefail
ROOT="/home/trido/thanhdt/WorkingClaude"
PROJECT="lithe-record-440915-m9"
export PATH="/home/trido/google-cloud-sdk/bin:$PATH"
cd "$ROOT"

FAIL=0
WARN=0
REPORT=""

log()  { REPORT+="$1"$'\n'; echo "$1"; }
ok()   { log "OK   $1"; }
warn() { log "WARN $1"; WARN=$((WARN+1)); }
fail() { log "FAIL $1"; FAIL=$((FAIL+1)); }

log "=== data_registry_audit — $(date -u +%FT%TZ) ==="

# ── A. Regression guard — files bitten by the 2026-07-11 vnindex_5state base-leak ──────────
log "--- A. Regression guard (vnindex_5state base-leak class) ---"

# A1: signal_v11_sql.py's substitution anchor must exist verbatim — pt_v4/pt_v22/pt_v23_audit
# do `.replace("tav2_bq.vnindex_5state AS s", STATE_TABLE + " AS s")` on this exact string at
# runtime. If the anchor text ever changes (reformatting, edit), the replace() silently no-ops
# and those consumers fall back to reading the TRAP table with zero error.
if grep -qF 'tav2_bq.vnindex_5state AS s' "$ROOT/signal_v11_sql.py" 2>/dev/null; then
  ok "signal_v11_sql.py: substitution anchor 'tav2_bq.vnindex_5state AS s' present"
else
  fail "signal_v11_sql.py: substitution anchor MISSING/CHANGED — pt_v4/pt_v22/pt_v23_audit .replace() will silently no-op, falling back to the vnindex_5state TRAP table"
fi

for f in pt_v4_dt5g.py pt_v22_dt5g.py pt_v23_audit_2014.py; do
  path="$ROOT/$f"
  [ -f "$path" ] || { warn "$f: not found, skipped"; continue; }
  if grep -qE 'STATE_TABLE[[:space:]]*=[[:space:]]*"tav2_bq\.vnindex_5state_dt5g_live"' "$path"; then
    ok "$f: STATE_TABLE = vnindex_5state_dt5g_live"
  else
    fail "$f: STATE_TABLE does not point to vnindex_5state_dt5g_live — check for regression"
  fi
  bare=$(grep -n 'tav2_bq\.vnindex_5state\b' "$path" | grep -v 'vnindex_5state_dt5g_live' | grep -v '\.replace(')
  if [ -n "$bare" ]; then
    fail "$f: bare vnindex_5state reference outside .replace() call -> $bare"
  fi
done

if grep -qE 'tav2_bq\.vnindex_5state\b' "$ROOT/golive_recommend_v23.py" 2>/dev/null; then
  if grep -E 'tav2_bq\.vnindex_5state\b' "$ROOT/golive_recommend_v23.py" | grep -qv 'vnindex_5state_dt5g_live'; then
    fail "golive_recommend_v23.py: references bare vnindex_5state (the TRAP table)"
  else
    ok "golive_recommend_v23.py: clean (only dt5g_live references)"
  fi
else
  ok "golive_recommend_v23.py: no vnindex_5state reference at all"
fi

# A2: custom30 mislabel-class regression (2026-07-11 golive_recommend incident) — production
# consumers must go through custom30.TABLE_V, never hardcode the legacy blend table name.
if grep -n 'custom30_8l' "$ROOT/golive_recommend_v23.py" 2>/dev/null | grep -qv 'custom30v_8l\|TABLE_V'; then
  fail "golive_recommend_v23.py: hardcodes custom30_8l literal instead of custom30.TABLE_V"
else
  ok "golive_recommend_v23.py: no hardcoded custom30_8l literal"
fi

# ── B. Freshness re-check — risk-critical CANONICAL/DERIVED sources, real bq show ──────────
log "--- B. Freshness re-check (risk-critical sources) ---"

check_bq_fresh() {
  local table="$1" max_age_days="$2" label="$3"
  local lm_ms
  lm_ms=$(bq show --format=prettyjson "${PROJECT}:tav2_bq.$table" 2>/dev/null \
          | python3 -c "import json,sys; print(json.load(sys.stdin).get('lastModifiedTime',''))" 2>/dev/null)
  if [ -z "$lm_ms" ]; then
    warn "$label ($table): could not read lastModifiedTime (bq call failed or table missing)"
    return
  fi
  local age_days=$(( ( $(date +%s) - lm_ms/1000 ) / 86400 ))
  if [ "$age_days" -gt "$max_age_days" ]; then
    warn "$label ($table): lastModified ${age_days}d ago (>${max_age_days}d expected) -- possible dead writer"
  else
    ok "$label ($table): fresh (${age_days}d old, threshold ${max_age_days}d)"
  fi
}

check_bq_fresh "vnindex_5state_dt5g_live" 3  "DT5G production regime state"
check_bq_fresh "custom30v_8l"             5  "custom30V parking basket (production money-path)"
check_bq_fresh "fa_ratings_8l"            9  "8L fundamentals as-of (cron weekly Sat 08:30 ICT since 2026-07-11, expect <7d gaps)"
check_bq_fresh "fa_ratings"               9  "legacy tier A-E, SIGNAL_V11 fa_tier input (append-only refresh cron weekly Sat 09:15 ICT proposed 2026-07-11 — WARNs until first successful run; table static since 05-10)"

# ── C. Reference-count drift on known DEPRECATED/DEAD sources ──────────────────────────────
# Not a pass/fail gate (some counts are expected to stay >0 forever, e.g. archived research
# scripts) — just surfaces the current count so a jump vs. the documented baseline in
# kb/data_registry.md is easy to eyeball during the Friday review.
log "--- C. Reference-count snapshot (deprecated/dead/trap sources) ---"
count_refs() {
  grep -rlE "$1" "$ROOT" --include='*.py' --include='*.sql' 2>/dev/null \
    | grep -vE '/\.git/|/archive/' | wc -l
}
log "INFO vnindex_5state (bare) referenced in $(count_refs 'tav2_bq\.vnindex_5state\b') files -- registry baseline: 0 production, ~few archived/research"
log "INFO vnindex_5state_dt_4gate (BQ, dead since 06-02) referenced in $(count_refs 'tav2_bq\.vnindex_5state_dt_4gate') files -- registry baseline: ~20 research scripts"
log "INFO fa_ratings (bare, static since 05-10) referenced in $(count_refs "tav2_bq\.fa_ratings[^_]") files -- registry baseline: ~50 scripts (still CANONICAL until migration decided)"

# ── D. Stale-duplicate scan — un-archived variants of a confirmed-canonical file ───────────
# WARN-only (coding_guidelines.md §10): flags repo-root files that are known superseded variants
# of an already-canonical script and haven't been git-mv'd into archive/. Curated list, extend
# whenever a new canonical/variant pair is confirmed -- deliberately NOT fuzzy-name-matching,
# that invites false positives on unrelated files that just happen to share a word.
log "--- D. Stale-duplicate scan (superseded variants not yet archived) ---"
check_variant_archived() {
  local canonical="$1"; shift
  for variant in "$@"; do
    if [ -f "$ROOT/$variant" ]; then
      warn "$variant: superseded variant of canonical '$canonical' still at repo root (not archived) -- see coding_guidelines.md Section 10"
    else
      ok "$variant: not at repo root (archived or removed)"
    fi
  done
}
check_variant_archived "fundamental_rating.py" \
  "build_fa_ratings_v9.py" "build_fa_ratings_pre2014.py" \
  "fundamental_rating_v5.py" "fundamental_rating_v8c.py"

log "=== SUMMARY: FAIL=$FAIL WARN=$WARN ==="

if [ "${1:-}" = "--bus" ]; then
  status_word="clean"
  [ "$WARN" -gt 0 ] && status_word="warn"
  [ "$FAIL" -gt 0 ] && status_word="fail"
  report_tmp="$(mktemp)"
  printf '%s' "$REPORT" > "$report_tmp"
  payload=$(FAIL="$FAIL" WARN="$WARN" STATUS="$status_word" REPORT_FILE="$report_tmp" python3 -c "
import json, os
with open(os.environ['REPORT_FILE']) as f:
    report = f.read()
print(json.dumps({'fail': int(os.environ['FAIL']), 'warn': int(os.environ['WARN']), 'status': os.environ['STATUS'], 'report': report}))
")
  rm -f "$report_tmp"
  "$ROOT/mike/bin/append_event.sh" Mike status "data-registry-audit" "$payload" 2>/dev/null || true
fi

[ "$FAIL" -gt 0 ] && exit 1
[ "$WARN" -gt 0 ] && exit 2
exit 0
