#!/usr/bin/env python3
"""Selfcheck for the kb_nightly backup-failure path (bin/kb_nightly.sh, Backup + Phase 4).

The bug: `backup.sh ... || true` swallowed backup.sh's real exit code, so a backup that died
on a full disk / rejected git push / broken credential still ended the night with an
unconditional "🌙 KB nightly done" on Discord + the architecture topic. Same false-success
family as the commit-collision-gate chain, different shape: an independent side-car script
failing for its own operational reasons, not a commit refused by a gate.

Design under test (deliberate, see the comment block in kb_nightly.sh): a failed backup does
NOT suppress the "done" line — KB compaction genuinely succeeded and suppressing it would also
swallow the OVERSIZE/PRUNE warnings and make silence indistinguishable from a dead cron. It
attaches a warning that says so out loud.

Why a NEW file rather than a case in bin/commit_collision_gate_selfcheck.py: that harness is
built around a real git repo + the pre-commit gate installed as a hook + live /proc-backed
fixture jobs. None of that is involved here — this needs no repo at all, only a stub
backup.sh and stub notifiers. Bolting it on would drag every case behind irrelevant setup.
What IS reused is the marker-slice contract: the shell under test is cut out of the shipped
file by content markers and never re-typed, and the cutter raises if a marker moves.

Case 5 is the RED control: the same harness run against the OLD `|| true` line must FAIL the
failure-path assertions. A green test that is also green on the broken code proves nothing.

Usage: bin/kb_nightly_backup_selfcheck.py     (exit 0 = all pass)
"""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KBN = os.path.join(ROOT, "bin", "kb_nightly.sh")

PASS, FAIL = [], []


def check(name, cond):
    (PASS if cond else FAIL).append(name)
    print(("  ok   " if cond else "  FAIL ") + name)


def _backup_notify_block():
    """The REAL Backup + Phase 4 body of bin/kb_nightly.sh, sliced by content markers (never
    re-typed). Raises if a marker moves — a fixture silently testing an empty string would be
    worse than no fixture at all."""
    with open(KBN, encoding="utf-8") as f:
        lines = f.read().splitlines(True)
    starts = [i for i, l in enumerate(lines) if l.startswith("# Backup (fix 2026-08-01")]
    ends = [i for i, l in enumerate(lines)
            if l.startswith('"$ROOT/bin/notify_thread.sh" "$MSG" "$_tid"')]
    if len(starts) != 1 or len(ends) != 1 or ends[0] <= starts[0]:
        raise RuntimeError("kb_nightly.sh Backup/Phase-4 markers moved: starts=%s ends=%s"
                           % (starts, ends))
    return "".join(lines[starts[0]:ends[0] + 1])


# The pre-fix line, verbatim from git history (commit f1a41995 and every night before it).
_OLD_BACKUP_LINE = ('"$ROOT/../../backup.sh" "kb_nightly $(date -u +%Y-%m-%d)"'
                    ' >> "$LOG" 2>&1 || true\n')


def _red_block():
    """The shipped block with the fixed backup call rewritten back to the old `|| true` one
    liner. Everything else (Phase 4, the MSG assembly) stays as shipped, so the control isolates
    exactly the change under test."""
    blk = _backup_notify_block()
    start = blk.index("BACKUP_WARN=\"\"\n")
    end = blk.index("\n# ── Phase 4: notify")
    return blk[:start] + _OLD_BACKUP_LINE + blk[end:]


def run_night(block, backup_rc=0, backup_out="backup chatter", drop_backup=False,
              oversize="", prune=""):
    """Run the sliced block in a throwaway tree. Only backup.sh / notify.sh / notify_thread.sh
    are stubbed — the exit-code capture, the MSG assembly and both notify calls are shipped
    code. No real network, no real Discord, no real repo."""
    tmp = tempfile.mkdtemp(prefix="kbn_backup_")
    try:
        # Layout must mirror production: kb_nightly.sh calls "$ROOT/../../backup.sh", so the
        # stub has to sit two levels above ROOT, not one (getting this wrong makes every run
        # look like a missing-backup failure — which is how this harness first came up RED).
        repo = os.path.join(tmp, "WorkingClaude", "mike")
        os.makedirs(os.path.join(repo, "bin"))
        os.makedirs(os.path.join(repo, "logs"))
        notify_log = os.path.join(repo, "logs", "notify_stub.log")

        for name in ("notify.sh", "notify_thread.sh"):
            p = os.path.join(repo, "bin", name)
            with open(p, "w", encoding="utf-8") as f:
                f.write('#!/usr/bin/env bash\nprintf "__NAME__ | %s\\n" "$*" '
                        '>> "$(dirname "$0")/../logs/notify_stub.log"\nexit 0\n'
                        .replace("__NAME__", name))
            os.chmod(p, 0o755)

        if not drop_backup:
            p = os.path.join(tmp, "backup.sh")
            with open(p, "w", encoding="utf-8") as f:
                f.write('#!/usr/bin/env bash\nprintf "%%s\\n" "%s"\nexit %d\n'
                        % (backup_out, backup_rc))
            os.chmod(p, 0o755)

        runner = os.path.join(repo, "run_night.sh")
        with open(runner, "w", encoding="utf-8") as f:
            f.write('#!/usr/bin/env bash\nset -euo pipefail\n'
                    'ROOT="%s"\ncd "$ROOT"\nLOG="$ROOT/logs/kb_nightly.log"\n'
                    'log() { echo "[selfcheck] $*" | tee -a "$LOG"; }\n'
                    'OVERSIZE="%s"\nPRUNE_WARN="%s"\n\n' % (repo, oversize, prune)
                    + block)

        r = subprocess.run(["bash", runner], cwd=repo, capture_output=True, text=True)
        log_txt = ""
        lp = os.path.join(repo, "logs", "kb_nightly.log")
        if os.path.exists(lp):
            log_txt = open(lp, encoding="utf-8").read()
        notes = open(notify_log, encoding="utf-8").read() if os.path.exists(notify_log) else ""
        return {"rc": r.returncode, "stdout": r.stdout, "stderr": r.stderr,
                "log": log_txt, "notify": notes}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    block = _backup_notify_block()

    print("-- slice sanity --")
    check("01 marker slice is non-empty and covers backup.sh → notify_thread.sh",
          "backup.sh" in block and "notify_thread.sh" in block and len(block.splitlines()) > 10)
    check("02 slice still carries the shipped MSG line",
          "🌙 KB nightly done" in block)

    print("-- backup SUCCEEDS --")
    ok = run_night(block, backup_rc=0, backup_out="pushed 3 objects")
    check("03 exit 0", ok["rc"] == 0)
    check("04 Discord says done", "KB nightly done" in ok["notify"])
    check("05 NO backup warning anywhere in the message",
          "BACKUP THẤT BẠI" not in ok["notify"])
    check("06 both channels notified (notify.sh + notify_thread.sh)",
          "notify.sh |" in ok["notify"] and "notify_thread.sh |" in ok["notify"])
    check("07 backup output still lands in the log", "pushed 3 objects" in ok["log"])

    print("-- backup FAILS (exit 3, e.g. disk full / push rejected) --")
    bad = run_night(block, backup_rc=3, backup_out="fatal: no space left on device")
    check("08 nightly still exits 0 (backup is an independent side-car)", bad["rc"] == 0)
    check("09 the done line is NOT suppressed", "KB nightly done" in bad["notify"])
    check("10 message says the backup FAILED, in words a human reads",
          "BACKUP THẤT BẠI" in bad["notify"])
    check("11 message carries the real exit code", "exit 3" in bad["notify"])
    check("12 message says KB compaction itself succeeded",
          "KB đã nén xong" in bad["notify"])
    check("13 BOTH channels carry the warning (Discord + architecture topic)",
          len([l for l in bad["notify"].splitlines() if "BACKUP THẤT BẠI" in l]) == 2)
    check("14 backup output kept in the log for debugging",
          "no space left on device" in bad["log"])
    check("15 backup output also on stderr (cron mail / journald)",
          "no space left on device" in bad["stderr"])
    check("16 failure recorded in the log timeline too", "Backup THẤT BẠI" in bad["log"])

    print("-- backup.sh MISSING (the 2026-08-01 wrong-path shape) --")
    gone = run_night(block, drop_backup=True)
    check("17 missing backup.sh is reported, not swallowed",
          "BACKUP THẤT BẠI" in gone["notify"])
    check("18 still exits 0 and still says done",
          gone["rc"] == 0 and "KB nightly done" in gone["notify"])

    print("-- warning coexists with the pre-existing warnings --")
    both = run_night(block, backup_rc=1, oversize=" Mike.md", prune="pruned 4 stale entries")
    check("19 OVERSIZE warning survives", "oversized memories" in both["notify"])
    check("20 PRUNE warning survives", "pruned 4 stale entries" in both["notify"])
    check("21 backup warning appended alongside, not instead of",
          "BACKUP THẤT BẠI" in both["notify"])

    print("-- RED control: the OLD `|| true` line must FAIL these --")
    red = run_night(_red_block(), backup_rc=3, backup_out="fatal: no space left on device")
    check("22 RED: old code reports plain success on a failed backup",
          "KB nightly done" in red["notify"] and "BACKUP THẤT BẠI" not in red["notify"])
    check("23 RED: old code never surfaces the backup error to stderr",
          "no space left on device" not in red["stderr"])
    check("24 RED control is a real inversion (same input, opposite verdict on case 10)",
          ("BACKUP THẤT BẠI" in bad["notify"]) and ("BACKUP THẤT BẠI" not in red["notify"]))

    print("\n%d/%d PASS" % (len(PASS), len(PASS) + len(FAIL)))
    if FAIL:
        print("FAILED:")
        for f in FAIL:
            print("  - " + f)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
