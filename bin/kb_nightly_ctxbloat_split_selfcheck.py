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
    """Pre-2026-08-19 body, from git (the version that could not validate a split)."""
    for rev in ("HEAD", "HEAD~1", "HEAD~2", "HEAD~3", "HEAD~4"):
        blob = subprocess.run(["git", "show", "%s:bin/kb_nightly.sh" % rev],
                              cwd=ROOT, capture_output=True, text=True)
        if blob.returncode != 0:
            continue
        body = slice_fn(blob.stdout)
        if "_ext.md" not in body:
            return body
    raise RuntimeError("could not recover pre-split _ctxbloat_autofix_one from git history")


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


def run_case(name, fn_body, core_out, ext_out, limit_kb=40, pre_ext=None):
    """Run the sliced function in a sandbox repo. Returns (rc, log_text, sandbox_dir)."""
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

    script = ("#!/bin/bash\nset -euo pipefail\nROOT=%s\nLOG=%s/log.txt\n"
              "log() { echo \"$*\" >> \"$LOG\"; }\n" % (d, d)) + fn_body + \
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

print("\n%d PASS, %d FAIL" % (len(PASS), len(FAIL)))
sys.exit(1 if FAIL else 0)
