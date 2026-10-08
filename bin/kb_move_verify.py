#!/usr/bin/env python3
"""kb_move_verify.py — kiểm một lần trim "CHỈ DI CHUYỂN" của kb/current_ops.md + kb/canonical.md.

Mọi dòng bị XOÁ khỏi file gốc (so với --base) phải còn NGUYÊN VĂN (khớp cả dòng) ở một file
kb/projects/*.md hoặc vẫn còn trong chính file gốc. Dòng trắng được miễn (đếm riêng). In từng
dòng không tìm thấy; rc=1 nếu có. Sinh ra cho job Wags_20261008_133659 (bài học: lần nén trước
từng đưa 2 lỗi sự thật vào file quyết định — kiểm bằng máy, không bằng tự khai).

  python3 bin/kb_move_verify.py --base <commit>   # so working tree với <commit>
"""
import argparse
import glob
import os
import subprocess
import sys
from collections import Counter

FILES = ("kb/current_ops.md", "kb/canonical.md")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="HEAD")
    ap.add_argument("--root", default=".")
    a = ap.parse_args()
    root = a.root
    corpus = set()
    for p in glob.glob(os.path.join(root, "kb/projects/*.md")):
        with open(p, encoding="utf-8") as f:
            corpus.update(f.read().split("\n"))
    missing, blank, moved, total_removed = [], 0, 0, 0
    for f in FILES:
        old = subprocess.run(["git", "-C", root, "show", f"{a.base}:{f}"], capture_output=True,
                             text=True, check=True).stdout.split("\n")
        with open(os.path.join(root, f), encoding="utf-8") as fh:
            new = fh.read().split("\n")
        removed = Counter(old) - Counter(new)
        for line, n in removed.items():
            total_removed += n
            if not line.strip():
                blank += n
            elif line in corpus:
                moved += n
            else:
                missing.append((f, line))
    print(f"removed={total_removed} moved_verbatim={moved} blank={blank} NOT_FOUND={len(missing)}")
    for f, line in missing:
        print(f"  NOT_FOUND {f}: {line[:160]}")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
