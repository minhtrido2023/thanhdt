#!/usr/bin/env python3
"""Selfcheck cho bin/repo_hygiene_gate.py (chay duoc duoi TZ=UTC va Asia/Ho_Chi_Minh)."""
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(ROOT, "bin", "repo_hygiene_gate.py")


def _run(cmd, cwd, env=None):
    return subprocess.run(cmd, cwd=cwd, env=env, capture_output=True, text=True)


def _setup_repo():
    td = tempfile.mkdtemp(prefix="hyg_gate_")
    _run(["git", "init", "-q"], td)
    _run(["git", "config", "user.email", "t@t"], td)
    _run(["git", "config", "user.name", "t"], td)
    os.makedirs(os.path.join(td, "kb", "projects"), exist_ok=True)
    os.makedirs(os.path.join(td, "reports"), exist_ok=True)
    os.makedirs(os.path.join(td, "bin"), exist_ok=True)
    with open(os.path.join(td, "kb", "projects", "existing.csv"), "w", encoding="utf-8") as f:
        f.write("a,b\n1,2\n3,4\n")
    _run(["git", "add", "-A"], td)
    _run(["git", "commit", "-q", "-m", "init"], td)
    return td


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

    td = _setup_repo()
    try:
        # 1. Clean commit in bin/ and reports/*.bak_sent_* passes
        with open(os.path.join(td, "bin", "ok.py"), "w", encoding="utf-8") as f:
            f.write("print('ok')\n")
        with open(os.path.join(td, "reports", "SpaceX_2026.md.bak_sent_1"), "w", encoding="utf-8") as f:
            f.write("backup\n")
        _run(["git", "add", "bin/ok.py", "reports/SpaceX_2026.md.bak_sent_1"], td)
        r = _run([sys.executable, GATE], td)
        check("01 clean code + .bak_sent_* allowed", r.returncode == 0, r.stderr)
        _run(["git", "commit", "-q", "-m", "clean"], td)

        # 2. Existing CSV shrinking/unchanged passes (ratchet)
        with open(os.path.join(td, "kb", "projects", "existing.csv"), "w", encoding="utf-8") as f:
            f.write("a,b\n1,2\n")
        _run(["git", "add", "kb/projects/existing.csv"], td)
        r = _run([sys.executable, GATE], td)
        check("02 shrinking tracked csv allowed", r.returncode == 0, r.stderr)
        _run(["git", "reset", "-q"], td)

        # 3. New CSV in kb/ blocked
        with open(os.path.join(td, "kb", "projects", "new.csv"), "w", encoding="utf-8") as f:
            f.write("a,b\n1,2\n")
        _run(["git", "add", "kb/projects/new.csv"], td)
        r = _run([sys.executable, GATE], td)
        check("03 new csv in kb/ blocked", r.returncode == 1 and "file .csv moi" in r.stderr, r.stderr)

        # 4. MIKE_HYGIENE_GATE=warn downgrades to rc=0
        env_warn = dict(os.environ, MIKE_HYGIENE_GATE="warn")
        r_warn = _run([sys.executable, GATE], td, env=env_warn)
        check("04 MIKE_HYGIENE_GATE=warn passes", r_warn.returncode == 0 and "warn" in r_warn.stdout, r_warn.stdout)
        _run(["git", "reset", "-q"], td)

        # 5. Binary/junk/root-stray blocked
        os.makedirs(os.path.join(td, "agents", "Taylor"), exist_ok=True)
        with open(os.path.join(td, "agents", "Taylor", "x.pdf"), "wb") as f:
            f.write(b"%PDF-1.4")
        with open(os.path.join(td, "stray_root_file.txt"), "w", encoding="utf-8") as f:
            f.write("stray")
        with open(os.path.join(td, "bin", "foo.diff"), "w", encoding="utf-8") as f:
            f.write("diff")
        _run(["git", "add", "agents/Taylor/x.pdf", "stray_root_file.txt", "bin/foo.diff"], td)
        r_bad = _run([sys.executable, GATE], td)
        check("05 binary + stray root + bin diff blocked",
              r_bad.returncode == 1 and ".pdf" in r_bad.stderr and "allowlist" in r_bad.stderr and ".diff" in r_bad.stderr,
              r_bad.stderr)
        _run(["git", "reset", "-q"], td)

        # 6. >1MB file blocked unless in LARGE_ALLOWLIST
        with open(os.path.join(td, "bin", "huge.txt"), "wb") as f:
            f.write(b"x" * (1024 * 1024 + 50))
        _run(["git", "add", "bin/huge.txt"], td)
        r_big = _run([sys.executable, GATE], td)
        check("06 >1MB file blocked", r_big.returncode == 1 and "vuot nguong" in r_big.stderr, r_big.stderr)
        _run(["git", "reset", "-q"], td)

        with open(os.path.join(td, "kb", "dd_price_zones.json"), "wb") as f:
            f.write(b"{" + b" " * (1024 * 1024 + 50) + b"}")
        _run(["git", "add", "kb/dd_price_zones.json"], td)
        r_allow_big = _run([sys.executable, GATE], td)
        check("07 LARGE_ALLOWLIST exempts kb/dd_price_zones.json", r_allow_big.returncode == 0, r_allow_big.stderr)
    finally:
        shutil.rmtree(td, ignore_errors=True)

    print(f"\nrepo_hygiene_gate_selfcheck: {passed}/{passed + failed} PASS")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
