#!/usr/bin/env python3
"""Selfcheck cho bin/okf_lint_gate.py."""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "bin", "okf_lint_gate.py")


def _run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


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

    td = tempfile.mkdtemp(prefix="okf_gate_")
    try:
        _run(["git", "init", "-q"], td)
        _run(["git", "config", "user.email", "t@t"], td)
        _run(["git", "config", "user.name", "t"], td)
        os.makedirs(os.path.join(td, "kb", "projects"), exist_ok=True)
        os.makedirs(os.path.join(td, "kb", "research_notes"), exist_ok=True)
        with open(os.path.join(td, "kb", "projects", "target.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: project\nowner: Mike\nstatus: active\nupdated: 2026-11-27\n---\n# Target\n")
        _run(["git", "add", "-A"], td)
        _run(["git", "commit", "-q", "-m", "init"], td)

        # 1. Valid OKF file + valid link passes
        with open(os.path.join(td, "kb", "projects", "valid.md"), "w", encoding="utf-8") as f:
            f.write(
                "---\nkind: project\nowner: Taylor\nstatus: closed\nupdated: 2026-11-27\n---\n"
                "# Valid\nSee [target](target.md).\n"
            )
        _run(["git", "add", "kb/projects/valid.md"], td)
        r1 = _run([sys.executable, GATE], td)
        check("01 valid OKF file passes", r1.returncode == 0, r1.stderr)
        _run(["git", "reset", "-q"], td)

        # 2. Missing frontmatter blocked
        with open(os.path.join(td, "kb", "research_notes", "nofm.md"), "w", encoding="utf-8") as f:
            f.write("# No FM\n")
        _run(["git", "add", "kb/research_notes/nofm.md"], td)
        r2 = _run([sys.executable, GATE], td)
        check("02 missing frontmatter blocked", r2.returncode == 1 and "frontmatter" in r2.stderr, r2.stderr)
        _run(["git", "reset", "-q"], td)

        # 3. Missing required field + broken link blocked
        with open(os.path.join(td, "kb", "research_notes", "bad.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: note\n---\n# Bad\nSee [missing](no_such_file.md).\n")
        _run(["git", "add", "kb/research_notes/bad.md"], td)
        r3 = _run([sys.executable, GATE], td)
        check(
            "03 missing keys and broken link blocked",
            r3.returncode == 1 and "owner" in r3.stderr and "broken link" in r3.stderr,
            r3.stderr,
        )
        _run(["git", "reset", "-q"], td)

        # 4. >40KB file blocked
        with open(os.path.join(td, "kb", "research_notes", "big.md"), "w", encoding="utf-8") as f:
            f.write("---\nkind: note\nowner: Mike\nstatus: active\nupdated: 2026-11-27\n---\n" + ("x\n" * 22000))
        _run(["git", "add", "kb/research_notes/big.md"], td)
        r4 = _run([sys.executable, GATE], td)
        check("04 >40KB new file blocked", r4.returncode == 1 and "40KB" in r4.stderr, r4.stderr)

        # 5. MIKE_OKF_GATE=warn passes
        r5 = _run([sys.executable, GATE], td, env=dict(os.environ, MIKE_OKF_GATE="warn"))
        check("05 MIKE_OKF_GATE=warn passes", r5.returncode == 0 and "warn" in r5.stdout, r5.stdout)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print(f"\nokf_lint_gate_selfcheck: {passed}/{passed + failed} PASS")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
