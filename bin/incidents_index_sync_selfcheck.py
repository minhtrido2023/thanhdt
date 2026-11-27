#!/usr/bin/env python3
"""Selfcheck cho bin/incidents_index_sync.py."""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SYNC = os.path.join(ROOT, "bin", "incidents_index_sync.py")


def _run(repo, arg):
    return subprocess.run(
        [sys.executable, os.path.join(repo, "bin", "incidents_index_sync.py"), arg],
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

    td = tempfile.mkdtemp(prefix="inc_sync_")
    try:
        repo = os.path.join(td, "mike")
        os.makedirs(os.path.join(repo, "bin"), exist_ok=True)
        shutil.copy2(SYNC, os.path.join(repo, "bin", "incidents_index_sync.py"))
        inc = os.path.join(repo, "kb", "incidents")
        os.makedirs(os.path.join(inc, "2026-08"), exist_ok=True)
        os.makedirs(os.path.join(inc, "2026-10"), exist_ok=True)
        os.makedirs(os.path.join(inc, "retro"), exist_ok=True)

        with open(os.path.join(inc, "2026-08", "2026-08-01-old.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: incident\ndate: 2026-08-01\nstatus: fixed\ntitle: Old inc\n---\nbody\n")
        with open(os.path.join(inc, "2026-10", "2026-10-05-new.md"), "w", encoding="utf-8") as f:
            f.write("# 2026-10-05 — New heading title\n\nbody\n")
        with open(os.path.join(inc, "retro", "retro-2026-10-05.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: retro\ndate: 2026-10-05\ntitle: RETRO 2026-10-05\nstatus: logged\n---\nbody\n")

        with open(os.path.join(inc, "archive-2026-Q3.md"), "w", encoding="utf-8") as f:
            f.write(
                "---\nkind: incident-index-archive\n---\n\n### 2026-08\n\n"
                "| Ngày | Sự cố | status |\n|---|---|---|\n"
                "| 2026-08-01 | [Old inc](2026-08/2026-08-01-old.md) | fixed |\n"
            )
        with open(os.path.join(inc, "retro", "index.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: retro-index\n---\n")

        # Duplicate + missing + orphan in index.md
        with open(os.path.join(inc, "index.md"), "w", encoding="utf-8") as f:
            f.write(
                "---\nkind: incident-index\nentries: 0 file\n---\n\n"
                "### 2026-10\n\n| Ngày | Sự cố | status |\n|---|---|---|\n"
                "| 2026-10-01 | [Ghost](2026-10/2026-10-01-ghost.md) | ? |\n"
                "| 2026-08-01 | [Old inc](2026-08/2026-08-01-old.md) | ? |\n\n"
                "## RETRO hằng ngày\n"
            )

        r1 = _run(repo, "--check")
        check("01 --check detects missing/orphan/retro drift", r1.returncode == 1, r1.stdout)

        r2 = _run(repo, "--fix")
        check("02 --fix exits 0", r2.returncode == 0, r2.stderr)

        r3 = _run(repo, "--check")
        check("03 --check passes after --fix", r3.returncode == 0, r3.stdout)

        idx_txt = open(os.path.join(inc, "index.md"), encoding="utf-8").read()
        retro_idx_txt = open(os.path.join(inc, "retro", "index.md"), encoding="utf-8").read()
        check("04 heading fallback used and no '?'", "New heading title" in idx_txt and "| ? |" not in idx_txt, idx_txt)
        check("05 ghost orphan removed and archive dup dropped", "ghost" not in idx_txt and "2026-08-01-old" not in idx_txt, idx_txt)
        check("06 retro/index.md synced", "retro-2026-10-05.md" in retro_idx_txt, retro_idx_txt)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print(f"\nincidents_index_sync_selfcheck: {passed}/{passed + failed} PASS")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
