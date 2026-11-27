#!/usr/bin/env python3
"""Selfcheck cho bin/projects_index_sync.py (chạy được dưới 2 TZ)."""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNC = os.path.join(ROOT, "bin", "projects_index_sync.py")


def _run(repo, arg):
    return subprocess.run(
        [sys.executable, os.path.join(repo, "bin", "projects_index_sync.py"), arg],
        cwd=repo,
        capture_output=True,
        text=True,
    )


def main():
    passed = 0
    failed = 0

    def check(name, cond, detail=""):
        nonlocal passed, failed
        if cond:
            passed += 1
            print(f"  ok   {name}")
        else:
            failed += 1
            print(f"  FAIL {name}" + (f" ({detail})" if detail else ""))

    td = tempfile.mkdtemp(prefix="proj_sync_")
    try:
        repo = os.path.join(td, "mike")
        os.makedirs(os.path.join(repo, "bin"), exist_ok=True)
        os.makedirs(os.path.join(repo, "kb", "projects"), exist_ok=True)
        shutil.copy2(SYNC, os.path.join(repo, "bin", "projects_index_sync.py"))

        pdir = os.path.join(repo, "kb", "projects")
        with open(os.path.join(pdir, "INDEX.md"), "w", encoding="utf-8") as f:
            f.write(
                "## Dự án đã đóng — 1 dòng/dự án, chi tiết `cat kb/projects/<file>.md`\n"
                "- 2026-10-01 Old closed → `old-closed.md` — **XONG**\n"
                "- 2026-10-02 Ghost → `ghost-missing.md` — **XONG**\n\n"
                "## Dự án ĐANG MỞ, chi tiết tách riêng (không inline `current_ops.md`)\n"
            )
        with open(os.path.join(pdir, "old-closed.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: project\nowner: Mike\nstatus: closed\nupdated: 2026-10-01\n---\n# Old\n")
        with open(os.path.join(pdir, "new-open.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: project\nowner: Taylor\nstatus: active\nupdated: 2026-11-20\n---\n# New open task\n")
        with open(os.path.join(pdir, "fpt-dd-20261101.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: dd\nowner: Taylor\nstatus: closed-go\nupdated: 2026-11-01\n---\n# DD FPT\n")

        r1 = _run(repo, "--check")
        check("01 --check detects missing and orphan", r1.returncode == 1, r1.stdout)

        r2 = _run(repo, "--fix")
        check("02 --fix exits 0", r2.returncode == 0, r2.stderr)

        r3 = _run(repo, "--check")
        check("03 --check passes after --fix", r3.returncode == 0, r3.stdout)

        idx = open(os.path.join(pdir, "INDEX.md"), encoding="utf-8").read()
        check(
            "04 orphan removed and new-open/dd added",
            "ghost-missing.md" not in idx and "new-open.md" in idx and "fpt-dd-20261101.md" in idx,
            idx,
        )
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print(f"\nprojects_index_sync_selfcheck: {passed}/{passed + failed} PASS")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
