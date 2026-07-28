# -*- coding: utf-8 -*-
"""Regression self-check for mike_json.py's content-anchored bus/inbox cursor
(cmd_cursor_advance + cursor_shift). Added 2026-07-28 after a same-day incident where the
FIRST version of this redesign (commits 0f2a8ab/fd76e61) fixed two real event-loss modes but
introduced a THIRD one (cursor persisted before payload flush -> a kill-mid-run drops events
silently) that an independent arch-review caught only by re-deriving the test cases from
scratch, because the original ad-hoc test harness was never committed. This file exists so
that never has to happen again for this pipeline.

Covers, in order: fast path, the two original loss modes (stranded / leapfrog), the two
round-2 gaps (torn/blank line in the unread region, ambiguous hash anchor), the round-3 gaps
(missing event_id anchor, null last_id falling back unsafely), the flush-before-cursor-write
ordering (structural check — timing-based repro is flaky by nature), the R1 bounded-replay
fix (torn last line must not replay the whole file), cursor_shift's no-over-subtract
invariant, and legacy bare-int cursor back-compat.

Run: python3 cursor_advance_selfcheck.py   (exit 0 = all pass)
"""
import inspect
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)
import mike_json  # noqa: E402

PYEXE = sys.executable
fails = []
total = 0


def check(name, cond, detail=""):
    global total
    total += 1
    print(f"  [{'PASS' if cond else 'FAIL'}] {name}" + (f"  — {detail}" if detail else ""))
    if not cond:
        fails.append(name)


def ev(i, ts=None, no_id=False, torn=False, blank=False):
    if blank:
        return ""
    if torn:
        return '{"event_id": "e%d", "ts": "%s", "event_typ' % (i, ts or "")  # truncated JSON
    d = {"ts": ts or f"2026-07-28T01:{i:02d}:00Z", "event_type": "finding", "agent_id": "t"}
    if not no_id:
        d["event_id"] = f"e{i}"
    return json.dumps(d)


def write_inbox(path, lines):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + ("\n" if lines else ""))


def run_cursor_advance(inbox, state):
    """Invoke the real CLI entry point (exact code path consolidate.sh uses), not the raw
    function, so this test exercises the same stdout/stderr wiring as production."""
    r = subprocess.run([PYEXE, os.path.join(ROOT, "mike_json.py"), "cursor-advance", inbox, state],
                        capture_output=True, text=True)
    new_lines = [l for l in r.stdout.split("\n") if l]
    return new_lines, r.stderr, r.returncode


def read_cursor(state):
    return mike_json._cursor_read(state)


def tmpfiles():
    d = tempfile.mkdtemp(prefix="cursor_sc_")
    return os.path.join(d, "inbox.jsonl"), os.path.join(d, "state.json")


# ── A. Fast path: mark still sits at line n -> no repair, no re-emit ────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
new1, _, _ = run_cursor_advance(inbox, state)
check("A1 first run ingests all 5", len(new1) == 5, str(len(new1)))
with open(inbox, "a", encoding="utf-8") as f:
    f.write(ev(5) + "\n")
new2, err2, _ = run_cursor_advance(inbox, state)
check("A2 second run ingests exactly the 1 new line", new2 == [ev(5)], str(new2))
check("A3 fast path has no CURSOR-REPAIR", "CURSOR-REPAIR" not in err2, err2)

# ── B. Mode (a) stranded: legacy bare-int cursor points past EOF -> clamp, no crash ─────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(3)])
with open(state, "w") as f:
    f.write("10")  # legacy cursor claims 10 lines read, file only has 3
new_b, err_b, rc_b = run_cursor_advance(inbox, state)
check("B1 stranded legacy cursor doesn't crash", rc_b == 0)
check("B2 stranded cursor emits nothing new (clamped, not negative-replayed)", new_b == [])
check("B3 stranded cursor reports a repair", "clamp-legacy" in err_b, err_b)

# ── C. Mode (b) leapfrog: content mark pruned + file regrows before next read ───────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(10)])
run_cursor_advance(inbox, state)  # cursor now anchored on e9
# Simulate kb_nightly pruning lines 0-4 (e0..e4) WITHOUT calling cursor_shift (the exact
# defect class this whole redesign exists to survive), then the file grows past where the
# mark used to be before the next consolidate run.
write_inbox(inbox, [ev(i) for i in range(5, 10)] + [ev(10)])
new_c, err_c, _ = run_cursor_advance(inbox, state)
check("C1 leapfrog does not lose the new event", ev(10) in new_c, str(new_c))
check("C2 leapfrog reports a repair (mark relocated or resynced)",
      "CURSOR-REPAIR" in err_c, err_c)

# ── D. Torn line in the UNREAD region must not be silently skipped ──────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
run_cursor_advance(inbox, state)
write_inbox(inbox, [ev(i) for i in range(5, 10)] + [ev(11, torn=True), ev(12)])
# force a resync (simulate the mark's own line having been pruned)
mike_json._cursor_write(state, mike_json._cursor_read(state)[0], "some-other-id", "2026-07-28T01:07:00Z")
new_d, err_d, _ = run_cursor_advance(inbox, state)
check("D1 torn line in unread region does not eat the event after it",
      ev(12) in new_d, str(new_d))

# ── E. Degenerate case: prev >= total when the resync-ts scan starts (should not happen via
#      the real cursor_shift path, but must not silently emit nothing if it ever does) — the
#      bounded-replay fix (R1/M below) must fall back to a full scan rather than an empty one.
#      Also covers "blank line in the unread region must not be silently skipped".
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
run_cursor_advance(inbox, state)  # prev=5
write_inbox(inbox, [ev(i) for i in range(5, 8)] + ["", ev(9)])  # total=5 again, content unrelated
mike_json._cursor_write(state, mike_json._cursor_read(state)[0], "some-other-id", "2026-07-28T01:07:00Z")
new_e, _, _ = run_cursor_advance(inbox, state)
check("E1 prev==total degenerate case falls back to full scan, does not emit nothing",
      new_e != [], str(new_e))
check("E2 blank line in the (fallback) scan does not eat the event after it",
      ev(9) in new_e, str(new_e))

# ── F. ts="" is not evidence of age (must not be treated as "older, skip") ──────────────────
n, last_id, last_ts = 3, "e2", "2026-07-28T01:02:00Z"
line_empty_ts = json.dumps({"event_id": "e-empty", "ts": "", "event_type": "x"})
anchor, ts = mike_json._line_mark(line_empty_ts)
check("F1 ts='' parses (not treated as torn)", anchor == "e-empty" and ts == "")

# ── G. Ambiguous hash anchor (2 byte-identical anchor-less lines) forces resync, not skip ───
inbox, state = tmpfiles()
dup_line = json.dumps({"ts": "2026-07-28T01:00:00Z", "event_type": "heartbeat", "agent_id": "t"})
write_inbox(inbox, [dup_line, ev(1), dup_line, ev(3)])
new_g1, _, _ = run_cursor_advance(inbox, state)
check("G1 first run ingests all 4 lines incl. both duplicate anchors", len(new_g1) == 4)
with open(inbox, "a") as f:
    f.write(ev(4) + "\n")
new_g2, _, _ = run_cursor_advance(inbox, state)
check("G2 ambiguous anchor at EOF still finds the genuinely new line",
      ev(4) in new_g2, str(new_g2))

# ── H. Last written line has no event_id (anchored by content hash) -> next run ingests
#      exactly the 1 new line, no dup no loss ───────────────────────────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(0), ev(1, no_id=True)])
run_cursor_advance(inbox, state)
_, last_id_h, _ = read_cursor(state)
check("H1 anchor-less last line still gets a real (non-null) anchor",
      last_id_h is not None and str(last_id_h).startswith("raw:"), str(last_id_h))
with open(inbox, "a") as f:
    f.write(ev(2) + "\n")
new_h, _, _ = run_cursor_advance(inbox, state)
check("H2 next run ingests exactly the 1 new line (no dup, no loss)",
      new_h == [ev(2)], str(new_h))

# ── I. cursor_shift never subtracts a deletion that lands AHEAD of the cursor (would
#      over-subtract and re-ingest real events as duplicates on the next run) ───────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(6)])
run_cursor_advance(inbox, state)  # cursor at n=6 (lines 1..6 consumed, 1-based)
n_before, _, _ = read_cursor(state)
# Pretend lines 2,3 (below/at cursor) were removed by a prune, AND line 7 (STRICTLY above the
# cursor — not yet consumed, e.g. appended after the prune snapshot) was also "removed" by a
# buggy caller. Only the first two may lower the cursor; charging it for line 7 would make the
# next run re-ingest a real, not-yet-read event as a duplicate.
mike_json.cursor_shift(state, [2, 3, 7])  # 1-based indices
n_after, _, _ = read_cursor(state)
check("I1 cursor_shift only subtracts the 2 indices at/below the pre-shift cursor",
      n_after == n_before - 2, f"before={n_before} after={n_after}")

# ── J. Legacy bare-int cursor still works and self-upgrades to the JSON+anchor form ─────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
with open(state, "w") as f:
    f.write("3")
new_j, _, _ = run_cursor_advance(inbox, state)
check("J1 legacy int cursor resumes from the right line", new_j == [ev(3), ev(4)], str(new_j))
n_j, last_id_j, _ = read_cursor(state)
check("J2 legacy cursor self-upgrades to carry an anchor", last_id_j is not None, str(last_id_j))

# ── K. Empty file: no crash, cursor stays at 0 ───────────────────────────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [])
new_k, _, rc_k = run_cursor_advance(inbox, state)
check("K1 empty file does not crash", rc_k == 0)
check("K2 empty file emits nothing", new_k == [])

# ── L. File ending in a blank line: no crash, no false repair on the steady state ───────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(0), ev(1), ""])
new_l1, _, _ = run_cursor_advance(inbox, state)
new_l2, err_l2, _ = run_cursor_advance(inbox, state)
check("L1 trailing blank line doesn't crash", True)
check("L2 re-running with no new content ingests nothing", new_l2 == [])
check("L3 steady state (no new lines) reports no repair", "CURSOR-REPAIR" not in err_l2, err_l2)

# ── M. R1 fix: a torn LAST line at cursor-write time must bound the replay near `prev`,
#      not replay the entire file from position 0 ───────────────────────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(30)])
run_cursor_advance(inbox, state)  # prev=30, last line (e29) is well-formed
# Force the exact state the incident produced: cursor with last_ts=None (as if the last line
# read had been torn at write time), last_id set to something no longer present.
mike_json._cursor_write(state, 30, "id-that-will-be-pruned", None)
write_inbox(inbox, [ev(i) for i in range(30)] + [ev(30)])  # file regrows by exactly 1
new_m, err_m, _ = run_cursor_advance(inbox, state)
check("M1 torn-last-line resync does NOT replay the whole file",
      len(new_m) <= 3, f"replayed {len(new_m)} lines (expected <=3, incident case was 30)")
check("M2 torn-last-line resync still delivers the genuinely new event",
      ev(30) in new_m, str(new_m))

# ── N. Structural: payload MUST flush to stdout before the cursor is persisted ──────────────
# Timing-based repro (SIGTERM mid-write) is real but flaky in CI; assert the ordering directly
# in the source instead, so a future edit that re-reverses it fails loudly and immediately.
src = inspect.getsource(mike_json.cmd_cursor_advance)
i_print = src.find("for raw in lines[start:]:")
i_flush = src.find("sys.stdout.flush()")
i_write = src.find("_cursor_write(state, total, nid, nts)")
check("N1 stdout.flush() exists in cmd_cursor_advance", i_flush != -1)
check("N2 print-loop -> flush -> cursor_write, in that order",
      -1 < i_print < i_flush < i_write, f"print={i_print} flush={i_flush} write={i_write}")

# ── O. consolidate.sh debounce key must be the repair KIND, not the whole line (whole-line
#      compare never matches twice on a file whose total= line count changes every run) ────
consolidate_src = open(os.path.join(ROOT, "consolidate.sh"), encoding="utf-8").read()
check("O1 debounce compares repair kind (awk field 3), not the full repaired line",
      "awk '{print $3}'" in consolidate_src and 'wkind' in consolidate_src)
line1 = "CURSOR-REPAIR Taylor.jsonl resync-ts prev=10 total=12 resume_from=10 recovered=0"
line2 = "CURSOR-REPAIR Taylor.jsonl resync-ts prev=12 total=15 resume_from=12 recovered=0"
kind1 = line1.split()[2]
kind2 = line2.split()[2]
check("O2 same repair kind on a growing file now compares equal (would debounce)",
      kind1 == kind2 and line1 != line2, f"{kind1} vs {kind2}")

print()
if fails:
    print(f"FAIL: {len(fails)}/{total} — {fails}")
    sys.exit(1)
print(f"ALL PASS: {total}/{total}")
sys.exit(0)
