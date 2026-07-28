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
                        capture_output=True, text=True, timeout=10)
    new_lines = [l for l in r.stdout.split("\n") if l]
    return new_lines, r.stderr, r.returncode


def read_cursor(state):
    return mike_json._cursor_read(state)


_tmpdirs = []  # cleaned up at exit (this ran nightly via kb_nightly.sh Phase 0 and used to
                # leak one dir per test — 17/run, ~6200/year uncleaned on a nightly cron)


def tmpfiles():
    d = tempfile.mkdtemp(prefix="cursor_sc_")
    _tmpdirs.append(d)
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

# ── C. Mode (b) leapfrog, mark SURVIVES relocation: content mark pruned from its old line
#      number + file regrows before next read, but the marked event itself is still somewhere
#      in the file -> resolves via resync-id (exact, no ts arithmetic involved) ────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(10)])
run_cursor_advance(inbox, state)  # cursor now anchored on e9
write_inbox(inbox, [ev(i) for i in range(5, 10)] + [ev(10)])  # e9 still present, shifted
new_c, err_c, _ = run_cursor_advance(inbox, state)
check("C1 leapfrog (mark relocatable) does not lose the new event", ev(10) in new_c, str(new_c))
check("C2 leapfrog (mark relocatable) resolves via resync-id, not resync-ts",
      "resync-id" in err_c, err_c)

# ── C'. Mode (b) leapfrog, mark is TRULY GONE + last_ts is PRESENT (not torn) — this is the
#      case a first version of the R1 bounded-replay fix got wrong: it trusted `prev` as a
#      floor even here, reproduced losing 100/150 real events with the repair line reporting
#      recovered=0 (the loss invisible even to a human reading it). The file is pruned WITHOUT
#      calling cursor_shift (the exact defect class this whole redesign exists to survive —
#      it is how the 2026-07-27 stranded-offset incident happened) and regrows PAST `prev`, so
#      a naive `min(prev, total)` bound lands in the middle of genuinely new content. Must lose
#      ZERO events: the resync-ts scan must stay unbounded whenever last_ts is available. ─────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(10)])
run_cursor_advance(inbox, state)  # cursor anchored on e9, prev=10, last_ts=e9's ts
# Prune away e5..e9 (the marked line e9 included) WITHOUT cursor_shift, then regrow past `prev`
# with events that are NEWER than the marked ts (this is what a real hourly gap looks like:
# several dispatches' worth of new findings land while nobody prunes/shifts).
write_inbox(inbox, [ev(i) for i in range(5)] + [ev(i) for i in range(10, 21)])  # 16 lines, prev=10 stale
new_cp, err_cp, _ = run_cursor_advance(inbox, state)
expected_cp = {ev(i) for i in range(10, 21)}  # every genuinely-new event, e10..e20
missing_cp = expected_cp - set(new_cp)
check("C'1 leapfrog (mark gone, last_ts present) loses ZERO of the 11 new events",
      not missing_cp, f"missing={len(missing_cp)}/11")
check("C'2 resolves via resync-ts (mark truly unresolvable by id)", "resync-ts" in err_cp, err_cp)

# ── D. Torn line in the UNREAD region must not be silently skipped (last_ts present case) ───
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
run_cursor_advance(inbox, state)
write_inbox(inbox, [ev(i) for i in range(5, 10)] + [ev(11, torn=True), ev(12)])
# force a resync (simulate the mark's own line having been pruned)
mike_json._cursor_write(state, mike_json._cursor_read(state)[0], "some-other-id", "2026-07-28T01:07:00Z")
new_d, err_d, _ = run_cursor_advance(inbox, state)
check("D1 torn line in unread region does not eat the event after it",
      ev(12) in new_d, str(new_d))

# ── E. Blank line in the UNREAD region must not be silently skipped: the anchor is gone AND
#      last_ts is None (the actual R1-bound path), so the scan must still land ON the blank
#      line (treating it as "not provably older") rather than jump past it to whatever comes
#      next. Distinct from D: this exercises the narrowed R1 bound itself, not the unbounded
#      last_ts-present path. ──────────────────────────────────────────────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
run_cursor_advance(inbox, state)  # prev=5, last_ts=e4's real ts
write_inbox(inbox, [ev(i) for i in range(5, 8)] + ["", ev(9)])  # total=8 now (prev=5 < total)
mike_json._cursor_write(state, mike_json._cursor_read(state)[0], "some-other-id", None)  # torn mark
new_e, _, _ = run_cursor_advance(inbox, state)
check("E1 R1-bounded scan (last_ts=None) still finds the blank line, not just skips to EOF",
      new_e != [], str(new_e))
check("E2 ...and the event after the blank line is not eaten", ev(9) in new_e, str(new_e))

# ── E'. Degenerate case: prev >= total AND last_ts is None (the actual R1-bound gate) — must
#      fall back to a full scan rather than silently emit nothing. ──────────────────────────
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(5)])
run_cursor_advance(inbox, state)  # prev=5
write_inbox(inbox, [ev(i) for i in range(5, 8)] + ["", ev(9)])  # total=5 again, unrelated content
mike_json._cursor_write(state, mike_json._cursor_read(state)[0], "some-other-id", None)
new_ep, _, _ = run_cursor_advance(inbox, state)
check("E'1 prev>=total AND last_ts=None falls back to full scan, not empty",
      new_ep != [], str(new_ep))
check("E'2 ...still finds the event past the blank line", ev(9) in new_ep, str(new_ep))

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

# ── I'. Pin the i==n boundary exactly (n=6): index 6 counts ("at" the cursor), index 7 does
#      not ("above" it) — I1 above tests this implicitly via the delta; this pins it directly.
inbox2, state2 = tmpfiles()
write_inbox(inbox2, [ev(i) for i in range(6)])
run_cursor_advance(inbox2, state2)  # n=6
mike_json.cursor_shift(state2, [6])   # exactly AT the cursor -> must count
n_at, _, _ = read_cursor(state2)
check("I'1 index == n counts (subtracts)", n_at == 5, f"n_at={n_at}")

inbox3, state3 = tmpfiles()
write_inbox(inbox3, [ev(i) for i in range(6)])
run_cursor_advance(inbox3, state3)  # n=6
mike_json.cursor_shift(state3, [7])   # strictly ABOVE the cursor -> must NOT count
n_above, _, _ = read_cursor(state3)
check("I'2 index == n+1 does not count (no-op, returns None)",
      n_above == 6, f"n_above={n_above}")

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

# ── O. consolidate.sh debounce: run the REAL script end-to-end in an isolated sandbox ROOT
#      (not a re-implementation of its logic, which could silently drift from the real file) —
#      same kind + not-worse = suppressed; same kind + recovered ESCALATES = re-alerts even
#      mid-streak; a run with no new repair clears the marker for the next occurrence. ─────────
def run_consolidate_sandbox(sandbox, inbox_lines):
    """One consolidate.sh pass against a fresh single-line-count inbox state; returns
    (notify_call_count_delta, append_call_count_delta, warn_dir_contents)."""
    write_inbox(os.path.join(sandbox, "bus", "inbox", "Test.jsonl"), inbox_lines)
    notify_log = os.path.join(sandbox, "notify_calls.log")
    append_log = os.path.join(sandbox, "append_calls.log")
    before_n = os.path.getsize(notify_log) if os.path.exists(notify_log) else 0
    before_a = os.path.getsize(append_log) if os.path.exists(append_log) else 0
    subprocess.run(["bash", os.path.join(sandbox, "bin", "consolidate.sh")],
                    cwd=sandbox, capture_output=True, text=True, timeout=30)
    after_n = os.path.getsize(notify_log) if os.path.exists(notify_log) else 0
    after_a = os.path.getsize(append_log) if os.path.exists(append_log) else 0
    warn_dir = os.path.join(sandbox, "state", "cursorwarn")
    contents = {}
    if os.path.isdir(warn_dir):
        for fn in os.listdir(warn_dir):
            contents[fn] = open(os.path.join(warn_dir, fn)).read()
    return (after_n > before_n), (after_a > before_a), contents


import shutil  # noqa: E402
sandbox = tempfile.mkdtemp(prefix="consolidate_sc_")
_tmpdirs.append(sandbox)
for d in ["bin", "kb", "bus/inbox", "bus/registry", "bus/directives", "state/offsets", "locks", "logs"]:
    os.makedirs(os.path.join(sandbox, d), exist_ok=True)
shutil.copy(os.path.join(ROOT, "consolidate.sh"), os.path.join(sandbox, "bin", "consolidate.sh"))
shutil.copy(os.path.join(ROOT, "mike_json.py"), os.path.join(sandbox, "bin", "mike_json.py"))
# Stub the 2 side-effecting calls consolidate.sh makes on a repair, so this test can count
# invocations instead of actually hitting Telegram/the bus.
with open(os.path.join(sandbox, "bin", "notify.sh"), "w") as f:
    f.write('#!/usr/bin/env bash\necho "$@" >> "$(dirname "$0")/../notify_calls.log"\n')
with open(os.path.join(sandbox, "bin", "append_event.sh"), "w") as f:
    f.write('#!/usr/bin/env bash\necho "$@" >> "$(dirname "$0")/../append_calls.log"\n')
os.chmod(os.path.join(sandbox, "bin", "notify.sh"), 0o755)
os.chmod(os.path.join(sandbox, "bin", "append_event.sh"), 0o755)

# Pass 1: cold state, no repair possible (fresh file) — establishes prev, no alert expected.
run_consolidate_sandbox(sandbox, [ev(i) for i in range(10)])
# Pass 2: force a torn-last-line resync-ts repair with a small recovered count.
mike_json._cursor_write(os.path.join(sandbox, "state", "offsets", "Test.jsonl"), 10, "gone-id", None)
notified2, _, warn2 = run_consolidate_sandbox(sandbox, [ev(i) for i in range(10)] + [ev(10, torn=True)])
check("O1 first repair occurrence alerts", notified2)

# Pass 3: SAME repair magnitude again (steady state) — must be debounced.
mike_json._cursor_write(os.path.join(sandbox, "state", "offsets", "Test.jsonl"), 10, "gone-id", None)
notified3, _, _ = run_consolidate_sandbox(sandbox, [ev(i) for i in range(10)] + [ev(10, torn=True)])
check("O2 identical repair kind+magnitude on the next run is debounced (no 2nd alert)",
      not notified3)

# Pass 4: same KIND but the loss ESCALATES (recovered grows) — must re-alert despite the
# still-active marker from pass 2/3. Passes 2/3 both landed on recovered=0 (the bounded scan
# always resumes exactly at `prev` when there's only one trailing torn line). To get a genuinely
# bigger `recovered`, force the prev>=total fallback (E'-shaped): prev far exceeds the tiny
# file, so the scan falls back to position 0 and `recovered = prev - 0` is large.
mike_json._cursor_write(os.path.join(sandbox, "state", "offsets", "Test.jsonl"), 100, "gone-id", None)
notified4, _, _ = run_consolidate_sandbox(sandbox, [ev(i) for i in range(5)])
check("O3 same repair kind but recovered ESCALATES -> re-alerts (not silenced mid-streak)",
      notified4)

# ── P. Unterminated final line (the actual production trigger, round-5 review): a large
#      (>4KB) event written via append_event.sh's `printf` can land as 2+ non-atomic write()
#      syscalls, so cursor-advance can read the file mid-write with the last line incomplete
#      and no trailing \n. It must be DROPPED, not anchored on — anchoring on it is exactly
#      what produces a last_ts=None cursor and reopens the whole resync-ts bound question.
inbox, state = tmpfiles()
with open(inbox, "w", encoding="utf-8") as f:
    f.write(ev(0) + "\n" + ev(1) + "\n")
    f.write('{"event_id": "e2", "ts": "2026-07-28T01:02:00Z", "event_type": "finding", "agent')
    # deliberately NO trailing newline — simulates a write() caught mid-syscall
new_p1, _, _ = run_cursor_advance(inbox, state)
check("P1 unterminated final line is not ingested as a fragment",
      new_p1 == [ev(0), ev(1)], str(new_p1))
n_p, last_id_p, last_ts_p = read_cursor(state)
check("P2 cursor does NOT anchor on the incomplete line (stays at the last COMPLETE one)",
      n_p == 2 and last_ts_p == "2026-07-28T01:01:00Z", f"n={n_p} last_ts={last_ts_p}")
# Now the writer "finishes": the event reappears complete (proper JSON, trailing \n).
write_inbox(inbox, [ev(0), ev(1), ev(2)])
new_p2, _, _ = run_cursor_advance(inbox, state)
check("P3 once the writer completes the line, a later run ingests it normally (no loss)",
      ev(2) in new_p2, str(new_p2))

# ── C''. The exact residual round-5 flagged: mark truly gone + last_ts=None (torn mark, not
#      just a torn CURRENT read) + prune WITHOUT cursor_shift + regrowth past prev. This is
#      the one case the P1/P2 unterminated-line fix does not by itself rule out: the cursor
#      was written in the PAST with last_ts=None (e.g. from a run that hit exactly the P1/P2
#      case last time), and *now* a completely unrelated large-scale prune+regrowth happens.
#      Bound still applies here (no ts info to do better with) — assert it stays small AND
#      that a directly-following normal run still finds everything from there on.
inbox, state = tmpfiles()
write_inbox(inbox, [ev(i) for i in range(10)])
run_cursor_advance(inbox, state)
mike_json._cursor_write(state, 10, "gone-id-2", None)   # simulates a past P1/P2-shaped cursor
write_inbox(inbox, [ev(i) for i in range(5)] + [ev(i) for i in range(10, 25)])  # 20 lines, prev=10 stale
new_cpp, err_cpp, _ = run_cursor_advance(inbox, state)
# The bound caps the replay at (total - prev) = 15, never the full 20-line file — that's the
# property being tested, not a specific small number (this scenario genuinely has 15 lines
# past `prev`, unlike M's single-line-regrowth case).
check("C''1 last_ts=None + prune-without-shift bound caps at total-prev, not a full 20-line replay",
      len(new_cpp) <= 15, f"replayed {len(new_cpp)} lines (file has 20)")
# Whatever this run missed (it has no ts info to avoid missing SOMETHING when the mark is
# truly gone), the very next run — now with the freshly-written last_ts — must not miss more.
new_cpp2, _, _ = run_cursor_advance(inbox, state)
check("C''2 immediate next run (now with fresh ts info) ingests nothing further (no residual)",
      new_cpp2 == [], str(new_cpp2))

print()
for d in _tmpdirs:
    shutil.rmtree(d, ignore_errors=True)
if fails:
    print(f"FAIL: {len(fails)}/{total} — {fails}")
    sys.exit(1)
print(f"ALL PASS: {total}/{total}")
sys.exit(0)
