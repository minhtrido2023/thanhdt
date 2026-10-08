#!/usr/bin/env python3
"""kb_hot_size_gate_selfcheck.py — sandbox git repo kiểm bin/kb_hot_size_gate.py (ratchet, 3 mode).

Chạy gate THẬT (đường pre-commit: đo nội dung STAGE) trong repo tạm; subprocess chạy với TZ bị
gỡ (env -u TZ — bài học §19 verify-before-done: selfcheck phải giống nhau ở mọi TZ). Cộng 2
MUTATION: gate bị phá (bỏ vế ratchet / nâng LIMIT) phải làm ít nhất 1 ca fail — chứng minh ca
kiểm thật sự bắt được lỗi, không PASS rỗng.   Dùng: python3 bin/kb_hot_size_gate_selfcheck.py
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GATE_SRC = os.path.join(HERE, "kb_hot_size_gate.py")
A, B = "kb/current_ops.md", "kb/canonical.md"
LIMIT = 30000


def sh(cwd, *cmd, env=None):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, env=env)


def clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in ("TZ", "MIKE_KB_SIZE_GATE")}
    env.update(extra)
    return env


def lines(n, width=99):
    return "".join(("x" * width) + "\n" for _ in range(n))  # 100 byte/dòng


def write(repo, rel, text):
    p = os.path.join(repo, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def make_repo(gate_path, head_a, head_b):
    d = tempfile.mkdtemp(prefix="kbgate_")
    sh(d, "git", "init", "-q")
    sh(d, "git", "config", "user.email", "t@t")
    sh(d, "git", "config", "user.name", "t")
    os.makedirs(os.path.join(d, "bin"))
    shutil.copy(gate_path, os.path.join(d, "bin/kb_hot_size_gate.py"))
    write(d, A, head_a)
    write(d, B, head_b)
    sh(d, "git", "add", "-A")
    sh(d, "git", "commit", "-q", "-m", "base")
    return d


def run_gate(repo, mode=None):
    env = clean_env(**({"MIKE_KB_SIZE_GATE": mode} if mode else {}))
    return sh(repo, sys.executable, "bin/kb_hot_size_gate.py", env=env).returncode


def cases(gate_path):
    """Trả list (tên, ok:bool). HEAD: A=20000 B=20000 (tổng 40000 > LIMIT) trừ ca ghi chú."""
    out = []

    def case(name, head, stage, want, mode=None, worktree=None):
        d = make_repo(gate_path, *head)
        try:
            write(d, A, stage[0])
            write(d, B, stage[1])
            sh(d, "git", "add", A, B)
            if worktree:
                write(d, A, worktree[0])
                write(d, B, worktree[1])
            rc = run_gate(d, mode)
            out.append((name, rc == want))
        finally:
            shutil.rmtree(d, ignore_errors=True)

    big, mid = lines(200), lines(150)          # 20000 / 15000 byte
    case("over-limit + tăng ⇒ BLOCK", (big, big), (big + lines(1), big), 1)
    case("over-limit + giữ nguyên ⇒ qua (ratchet)", (big, big), (big, big), 0)
    case("over-limit + giảm ⇒ qua", (big, big), (mid, big), 0)
    case("dưới limit + tăng ⇒ qua", (lines(50), lines(50)), (lines(100), lines(50)), 0)
    case("tăng vượt limit từ dưới ⇒ BLOCK", (lines(140), lines(150)), (lines(160), lines(150)), 1)
    case("warn: over + tăng ⇒ rc0", (big, big), (big + lines(1), big), 0, mode="warn")
    case("off: over + tăng ⇒ rc0", (big, big), (big + lines(1), big), 0, mode="off")
    # đo STAGE, không đo working tree: stage nhỏ + worktree phình ⇒ qua; stage phình + worktree nhỏ ⇒ BLOCK
    case("stage giảm, worktree phình ⇒ qua", (big, big), (mid, big), 0, worktree=(big + lines(50), big))
    case("stage phình, worktree giảm ⇒ BLOCK", (big, big), (big + lines(1), big), 1, worktree=(mid, big))
    return out


def main():
    results = cases(GATE_SRC)
    # MUTATION 1: bỏ vế ratchet (chỉ còn LIMIT tuyệt đối) ⇒ ca "giữ nguyên/giảm" phải fail.
    # MUTATION 2: nâng LIMIT quá lớn ⇒ ca BLOCK phải fail.
    src = open(GATE_SRC, encoding="utf-8").read()
    muts = {
        "bỏ ratchet": src.replace("st <= LIMIT or st <= hd", "st <= LIMIT"),
        "nâng LIMIT": src.replace("LIMIT = 30000", "LIMIT = 10**9"),
    }
    tmp = tempfile.mkdtemp(prefix="kbgate_mut_")
    bad = 0
    try:
        for label, text in muts.items():
            assert text != src, f"mutation '{label}' không áp được (gate đổi cấu trúc?)"
            mp = os.path.join(tmp, "m.py")
            with open(mp, "w", encoding="utf-8") as f:
                f.write(text)
            killed = any(not ok for _, ok in cases(mp))
            results.append((f"mutation '{label}' bị bắt", killed))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for name, ok in results:
        print(("PASS " if ok else "FAIL ") + name)
        bad += 0 if ok else 1
    print(f"{len(results) - bad}/{len(results)} PASS")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
