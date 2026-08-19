#!/usr/bin/env python3
"""Selfcheck for the ctxbloat auto-fix OKF-SPLIT path (bin/kb_nightly.sh `_ctxbloat_autofix_one`).

The gap it locks: before 2026-08-19 the auto-fix could only ever CHECK a single output file
(`<file>.proposed`) against the original. A file whose remaining bytes are facts/structure —
MIKE.md, kb/coding_guidelines.md — cannot be compressed under threshold without losing facts, so
every episode ended in "AUTO-FIX INSUFFICIENT" + a human escalation, and both files had to be
split by hand (2026-08-14, 2026-08-19). User mandate 2026-08-19 makes the split the DEFAULT
remedy, so the mechanical gate has to be able to validate one.

Design under test: the agent may also write `<file>_ext.md.proposed`; the fact-check runs on
core+ext CONCATENATED on both sides. That makes a MOVE a no-op to the gate (fact still present)
while a DELETE is still rejected — the property that matters, since the gate is the only thing
standing between a dispatched agent and the live file.

Harness: the real function body is sliced out of the shipped kb_nightly.sh by content markers
and never re-typed (same contract as bin/kb_nightly_backup_selfcheck.py — the cutter raises if a
marker moves). dispatch.sh is a stub that writes whatever the case wants; ctxbloat_fact_check.py
and git are REAL.

Case 6 is the RED control: the identical split case, run against the PRE-change function body
recovered from git, must be REJECTED — proving these tests would have caught the old behaviour
instead of being green on both.

Usage: bin/kb_nightly_ctxbloat_split_selfcheck.py    (exit 0 = all pass)
"""
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KBN = os.path.join(ROOT, "bin", "kb_nightly.sh")

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name)


def slice_fn(text):
    """The real `_ctxbloat_autofix_one` body, cut by content markers."""
    lines = text.splitlines(True)
    starts = [i for i, l in enumerate(lines) if l.startswith("_ctxbloat_autofix_one() {")]
    if len(starts) != 1:
        raise RuntimeError("marker `_ctxbloat_autofix_one() {` moved: %s" % (starts,))
    ends = [i for i, l in enumerate(lines) if i > starts[0] and l.rstrip("\n") == "}"]
    if not ends:
        raise RuntimeError("closing brace of _ctxbloat_autofix_one not found")
    return "".join(lines[starts[0]:ends[0] + 1])


def old_fn():
    """Pre-2026-08-19 body, from git (the version that could not validate a split).

    Walks commits that touched bin/kb_nightly.sh specifically (not a flat HEAD~N depth) —
    a fixed depth of 4 went stale within days as unrelated consolidate commits piled up on
    top of the split-introducing commit and pushed it past HEAD~4 (caught 2026-08-19,
    arch-reviewer coord-2026-08-19 follow-up: this selfcheck itself crashed instead of
    running, on a repo with 21 commits since ff35c6a5).
    """
    revs = subprocess.run(["git", "log", "--format=%H", "--", "bin/kb_nightly.sh"],
                          cwd=ROOT, capture_output=True, text=True).stdout.split()
    for rev in revs[:20]:
        blob = subprocess.run(["git", "show", "%s:bin/kb_nightly.sh" % rev],
                              cwd=ROOT, capture_output=True, text=True)
        if blob.returncode != 0:
            continue
        body = slice_fn(blob.stdout)
        if "_ext.md" not in body:
            return body
    raise RuntimeError("could not recover pre-split _ctxbloat_autofix_one from git history")


def buggy_order_fn():
    """The OKF-split body exactly as shipped in ff35c6a5: `mv "$proposed" "$file"` (core)
    BEFORE `mv "$ext_proposed" "$ext"` — the ordering arch-reviewer flagged coord-2026-08-19
    (race_idempotency fail: kill between the two mv calls leaves core already pointing at an
    ext file that was never written). Used only as a RED control for case 8 below."""
    blob = subprocess.run(["git", "show", "ff35c6a5:bin/kb_nightly.sh"],
                          cwd=ROOT, capture_output=True, text=True)
    if blob.returncode != 0:
        raise RuntimeError("could not recover ff35c6a5 kb_nightly.sh for RED control")
    return slice_fn(blob.stdout)


def buggy_ext_gate_fn():
    """The @-import gate exactly as shipped in 38c64695: `[ -s "$ext_proposed" ] && grep ...`
    — arch-reviewer coord-2026-08-19 round 2 reproduced that this condition turns the gate OFF
    for a pure-compress proposal (no ext_proposed written) when `$ext` already exists from an
    earlier split, which is the live state of both monitored files. Used only as a RED control
    for case 13 below."""
    blob = subprocess.run(["git", "show", "38c64695:bin/kb_nightly.sh"],
                          cwd=ROOT, capture_output=True, text=True)
    if blob.returncode != 0:
        raise RuntimeError("could not recover 38c64695 kb_nightly.sh for RED control")
    return slice_fn(blob.stdout)


# --- fixtures -----------------------------------------------------------------------------
CORE_OLD = """# FIXTURE core

## Nguyên tắc
Quy tắc nền, phải nạp mỗi phiên. Ngưỡng cứng 40KB, chốt 2026-07-30.

## Quy trình hiếm dùng
Chỉ đọc khi thêm agent mới. Sự cố gốc 2026-08-14, commit d65167a9, mất 12% throughput.
Chi tiết dài dòng ở đây, tham chiếu bin/spawn_child.sh.
"""
# split: section 2 moved verbatim, pointer left behind
CORE_SPLIT = """# FIXTURE core

## Mục đã tách sang `fixture_ext.md` — đọc khi cần, KHÔNG auto-load
| Mục | Khi nào phải đọc |
|---|---|
| Quy trình hiếm dùng | Thêm agent mới |

## Nguyên tắc
Quy tắc nền, phải nạp mỗi phiên. Ngưỡng cứng 40KB, chốt 2026-07-30.

## Quy trình hiếm dùng
Chi tiết ở `fixture_ext.md`.
"""
EXT_SPLIT = """# fixture_ext

## Quy trình hiếm dùng
Chỉ đọc khi thêm agent mới. Sự cố gốc 2026-08-14, commit d65167a9, mất 12% throughput.
Chi tiết dài dòng ở đây, tham chiếu bin/spawn_child.sh.
"""
EXT_LOSSY = EXT_SPLIT.replace("Sự cố gốc 2026-08-14, commit d65167a9, mất 12% throughput.\n", "")
CORE_COMPRESSED = """# FIXTURE core

## Nguyên tắc
Ngưỡng cứng 40KB, chốt 2026-07-30.

## Quy trình hiếm dùng
Thêm agent mới. Sự cố gốc 2026-08-14, commit d65167a9, mất 12% throughput. bin/spawn_child.sh.
"""


def run_case(name, fn_body, core_out, ext_out, limit_kb=40, pre_ext=None, kill_at_nth_mv=None):
    """Run the sliced function in a sandbox repo. Returns (rc, log_text, sandbox_dir).

    kill_at_nth_mv: if set, shadow `mv` with a shell function that passes the first N-1 calls
    through untouched and, on the Nth call, exits with 137 (simulated SIGKILL) INSTEAD of
    running it — probes what state a kill mid-function leaves on disk.
    """
    d = tempfile.mkdtemp(prefix="ctxbloat_sc_")
    subprocess.run(["git", "init", "-q", d], check=True)
    subprocess.run(["git", "-C", d, "config", "user.email", "sc@test"], check=True)
    subprocess.run(["git", "-C", d, "config", "user.name", "sc"], check=True)
    os.makedirs(os.path.join(d, "bin"))
    with open(os.path.join(d, "fixture.md"), "w", encoding="utf-8") as f:
        f.write(CORE_OLD)
    if pre_ext is not None:
        with open(os.path.join(d, "fixture_ext.md"), "w", encoding="utf-8") as f:
            f.write(pre_ext)
    # real fact-checker, stub dispatch
    os.symlink(os.path.join(ROOT, "bin", "ctxbloat_fact_check.py"),
               os.path.join(d, "bin", "ctxbloat_fact_check.py"))
    stub = os.path.join(d, "bin", "dispatch.sh")
    with open(stub, "w", encoding="utf-8") as f:
        f.write("#!/bin/bash\n")
        f.write("cat > %s/fixture.md.proposed <<'EOF_C'\n%sEOF_C\n" % (d, core_out))
        if ext_out is not None:
            f.write("cat > %s/fixture_ext.md.proposed <<'EOF_E'\n%sEOF_E\n" % (d, ext_out))
    os.chmod(stub, 0o755)
    subprocess.run(["git", "-C", d, "add", "-A"], check=True)
    subprocess.run(["git", "-C", d, "commit", "-qm", "seed"], check=True)

    kill_shim = ""
    if kill_at_nth_mv is not None:
        kill_shim = (
            "_mv_n=0\n"
            "mv() {\n"
            "  _mv_n=$((_mv_n+1))\n"
            "  if [ \"$_mv_n\" -eq %d ]; then\n"
            "    log \"SIMULATED-KILL before mv call #$_mv_n ($*)\"\n"
            "    exit 137\n"
            "  fi\n"
            "  command mv \"$@\"\n"
            "}\n" % kill_at_nth_mv
        )
    script = ("#!/bin/bash\nset -euo pipefail\nROOT=%s\nLOG=%s/log.txt\n"
              "log() { echo \"$*\" >> \"$LOG\"; }\n" % (d, d)) + kill_shim + fn_body + \
             '\n_ctxbloat_autofix_one "%s/fixture.md" %d "fixture.md" 42\n' % (d, limit_kb)
    sp = os.path.join(d, "run.sh")
    with open(sp, "w", encoding="utf-8") as f:
        f.write(script)
    os.chmod(sp, 0o755)
    r = subprocess.run(["bash", sp], capture_output=True, text=True)
    log = ""
    if os.path.exists(os.path.join(d, "log.txt")):
        log = open(os.path.join(d, "log.txt"), encoding="utf-8").read()
    print("--- %s (rc=%d)" % (name, r.returncode))
    return r.returncode, log, d


def read(d, rel):
    p = os.path.join(d, rel)
    return open(p, encoding="utf-8").read() if os.path.exists(p) else None


def committed_paths(d):
    r = subprocess.run(["git", "-C", d, "show", "--stat", "--name-only", "--format=", "HEAD"],
                       capture_output=True, text=True)
    return set(x for x in r.stdout.split() if x)


NEW = slice_fn(open(KBN, encoding="utf-8").read())
OLD = old_fn()

# 1 — compression only, no ext: unchanged legacy behaviour
rc, log, d = run_case("case1 compress-only", NEW, CORE_COMPRESSED, None)
check("1a compress-only applied (rc=0)", rc == 0)
check("1b core replaced", read(d, "fixture.md") == CORE_COMPRESSED)
check("1c no ext file created", read(d, "fixture_ext.md") is None)
check("1d committed core only", committed_paths(d) == {"fixture.md"})

# 2 — OKF split accepted
rc, log, d = run_case("case2 okf-split", NEW, CORE_SPLIT, EXT_SPLIT)
check("2a split applied (rc=0)", rc == 0)
check("2b core = pointer version", read(d, "fixture.md") == CORE_SPLIT)
check("2c ext written verbatim", read(d, "fixture_ext.md") == EXT_SPLIT)
check("2d both files committed", committed_paths(d) == {"fixture.md", "fixture_ext.md"})
check("2e log names the split", "OKF split" in log)
check("2f no .proposed left behind",
      read(d, "fixture.md.proposed") is None and read(d, "fixture_ext.md.proposed") is None)

# 3 — split that DROPS a fact must be rejected, live files untouched
rc, log, d = run_case("case3 lossy-split", NEW, CORE_SPLIT, EXT_LOSSY)
check("3a rejected (rc=1)", rc == 1)
check("3b core untouched", read(d, "fixture.md") == CORE_OLD)
check("3c ext not created", read(d, "fixture_ext.md") is None)
check("3d REJECTED logged", "AUTO-FIX REJECTED" in log)

# 4 — ext already exists; proposal that forgets its old content must be rejected
PRE_EXT = EXT_SPLIT + "\n## Mục cũ\nQuyết định 2026-07-17, commit ab12cd34.\n"
rc, log, d = run_case("case4 ext-exists-dropped", NEW, CORE_SPLIT, EXT_SPLIT, pre_ext=PRE_EXT)
check("4a rejected (rc=1)", rc == 1)
check("4b existing ext untouched", read(d, "fixture_ext.md") == PRE_EXT)
check("4c core untouched", read(d, "fixture.md") == CORE_OLD)

# 5 — facts fine but core still over limit → INSUFFICIENT, nothing applied.
# Core is padded past 1KB and the limit set to 0 so the size gate (integer KB) really trips;
# the unpadded fixture rounds to 0KB and would pass the gate for the wrong reason.
CORE_STILL_BIG = CORE_SPLIT + "\n" + ("pad " * 400) + "\n"
rc, log, d = run_case("case5 still-over", NEW, CORE_STILL_BIG, EXT_SPLIT, limit_kb=0)
check("5a insufficient (rc=1)", rc == 1)
check("5b core untouched", read(d, "fixture.md") == CORE_OLD)
check("5c ext not created", read(d, "fixture_ext.md") is None)
check("5d INSUFFICIENT logged", "AUTO-FIX INSUFFICIENT" in log)
check("5e both .proposed cleaned up",
      read(d, "fixture.md.proposed") is None and read(d, "fixture_ext.md.proposed") is None)

# 6 — RED control: the same split against the OLD body must NOT apply
rc, log, d = run_case("case6 RED old-body-split", OLD, CORE_SPLIT, EXT_SPLIT)
check("6a old body refuses the split (rc!=0)", rc != 0)
check("6b old body leaves core unchanged", read(d, "fixture.md") == CORE_OLD)

# 7 — kill mid-function, between the two mv calls (fixed order: ext moves first). A crash
# here must NOT leave core pointing at an ext file that doesn't exist yet — worst case is
# duplicated content (ext updated, core still old/self-consistent), never a dangling ref.
rc, log, d = run_case("case7 kill-mid-mv (fixed order)", NEW, CORE_SPLIT, EXT_SPLIT,
                      kill_at_nth_mv=2)
check("7a killed before the 2nd mv (rc=137)", rc == 137)
check("7b ext already moved (1st mv, succeeded)", read(d, "fixture_ext.md") == EXT_SPLIT)
check("7c core NOT yet touched (2nd mv, interrupted) — no dangling pointer",
      read(d, "fixture.md") == CORE_OLD)

# 8 — RED control: the SAME kill-mid-mv probe against the ORIGINAL ff35c6a5 ordering (core
# moved first) must reproduce the actual bug — core already rewritten to point at
# `fixture_ext.md` while that file was never written, i.e. a dangling reference.
BUGGY_ORDER = buggy_order_fn()
rc, log, d = run_case("case8 RED kill-mid-mv (buggy pre-fix order)", BUGGY_ORDER,
                      CORE_SPLIT, EXT_SPLIT, kill_at_nth_mv=2)
check("8a killed before the 2nd mv (rc=137)", rc == 137)
check("8b core ALREADY swapped to pointer version (dangling risk)",
      read(d, "fixture.md") == CORE_SPLIT)
check("8c ext NOT moved yet — core points at a file that doesn't exist (the bug)",
      read(d, "fixture_ext.md") is None)

# 9 — @-import gate: a split whose core uses `@`-recursion as its pointer defeats the whole
# point of splitting (content re-loads verbatim every session) even though no fact is lost —
# must be mechanically REJECTED, not just discouraged in the dispatch prompt (arch-review
# coord-2026-08-19, fail_silent: fact-check + size gate both PASS this on their own).
CORE_ATIMPORT = """# FIXTURE core

@fixture_ext.md

## Nguyên tắc
Quy tắc nền, phải nạp mỗi phiên. Ngưỡng cứng 40KB, chốt 2026-07-30.

## Quy trình hiếm dùng
Chi tiết ở `fixture_ext.md`.
"""
rc, log, d = run_case("case9 at-import-pointer", NEW, CORE_ATIMPORT, EXT_SPLIT)
check("9a rejected (rc=1)", rc == 1)
check("9b core untouched", read(d, "fixture.md") == CORE_OLD)
check("9c ext not created", read(d, "fixture_ext.md") is None)
check("9d REJECTED logged", "AUTO-FIX REJECTED" in log)

# 10 — RED control: the SAME @-import proposal against the pre-gate (ff35c6a5) body must be
# WRONGLY applied — proving case 9 exercises new behaviour, not a pre-existing check.
rc, log, d = run_case("case10 RED at-import (pre-gate body)", BUGGY_ORDER, CORE_ATIMPORT, EXT_SPLIT)
check("10a pre-gate body wrongly applies the @-import split (rc=0)", rc == 0)
check("10b core ends up holding the recursive @ pointer (the bug case 9 blocks)",
      "@fixture_ext.md" in (read(d, "fixture.md") or ""))

# 11 — regression guard: an UNRELATED pre-existing @-import (e.g. MIKE.md's own real
# `@context_pack.md` at line 3, which a legitimate compression must preserve verbatim) must
# NOT trip the case-9 gate just because it also starts a line with `@`. A first draft of the
# gate matched bare `^@` and would have permanently blocked every future MIKE.md compression —
# caught before commit by checking real files, not just synthetic fixtures.
CORE_UNRELATED_IMPORT = """# FIXTURE core

@fixture_other.md

## Mục đã tách sang `fixture_ext.md` — đọc khi cần, KHÔNG auto-load
| Mục | Khi nào phải đọc |
|---|---|
| Quy trình hiếm dùng | Thêm agent mới |

## Nguyên tắc
Quy tắc nền, phải nạp mỗi phiên. Ngưỡng cứng 40KB, chốt 2026-07-30.

## Quy trình hiếm dùng
Chi tiết ở `fixture_ext.md`.
"""
rc, log, d = run_case("case11 unrelated-at-import-not-blocked", NEW, CORE_UNRELATED_IMPORT, EXT_SPLIT)
check("11a applied despite unrelated @-import (rc=0)", rc == 0)
check("11b core keeps the unrelated import + becomes the pointer version",
      read(d, "fixture.md") == CORE_UNRELATED_IMPORT)
check("11c ext written", read(d, "fixture_ext.md") == EXT_SPLIT)

# 12 — @-import gate must ALSO fire on a PURE-COMPRESS proposal (no ext_proposed written) when
# `$ext` already exists from an earlier split — this is the live state of both monitored files
# (MIKE_ext.md, kb/coding_guidelines_ext.md) today, so every future breach hits this path, not
# the fresh-split path case 9 covers (arch-review coord-2026-08-19 round 2, reproduced live).
rc, log, d = run_case("case12 at-import-pure-compress-existing-ext", NEW, CORE_ATIMPORT, None,
                      pre_ext=EXT_SPLIT)
check("12a rejected (rc=1)", rc == 1)
check("12b core untouched", read(d, "fixture.md") == CORE_OLD)
check("12c pre-existing ext untouched", read(d, "fixture_ext.md") == EXT_SPLIT)
check("12d REJECTED logged", "AUTO-FIX REJECTED" in log)

# 13 — RED control: the SAME pure-compress @-import proposal against the 38c64695 gate (which
# only checked `[ -s "$ext_proposed" ]`) must be WRONGLY applied — proving case 12 exercises the
# round-2 fix, not a pre-existing check.
BUGGY_EXT_GATE = buggy_ext_gate_fn()
rc, log, d = run_case("case13 RED at-import-pure-compress (38c64695 gate)", BUGGY_EXT_GATE,
                      CORE_ATIMPORT, None, pre_ext=EXT_SPLIT)
check("13a 38c64695 gate wrongly applies it (rc=0)", rc == 0)
check("13b core ends up holding the recursive @ pointer (the bug case 12 blocks)",
      "@fixture_ext.md" in (read(d, "fixture.md") or ""))

print("\n%d PASS, %d FAIL" % (len(PASS), len(FAIL)))
sys.exit(1 if FAIL else 0)
