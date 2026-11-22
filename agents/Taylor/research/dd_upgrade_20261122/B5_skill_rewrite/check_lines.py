#!/usr/bin/env python3
"""Kiểm cơ học B5: mọi dòng THÂN không rỗng của skill cũ có trong SKILL_ext.md mới (sau khi bỏ chú thích ⟨…⟩ do B5 chèn).
Dùng: python3 check_lines.py <old SKILL.md> <new SKILL_ext.md>   (rc=0 khi 0 dòng thiếu). Dòng tiêu đề '## X' được so cả dạng '#### (tiêu đề cũ) X'."""
import re, sys
old = open(sys.argv[1], encoding="utf-8").read().split("\n")
new = re.sub(r"\s*⟨[^⟩]*⟩", "", open(sys.argv[2], encoding="utf-8").read())
if old and old[0].strip() == "---":
    end = old[1:].index("---") + 2
    old = old[end:]
miss = []
for ln in old:
    t = ln.strip()
    if not t or t in new:
        continue
    if t.startswith("#"):
        body = t.lstrip("# ").strip()
        if body in new:
            continue
    miss.append(t[:100])
print(f"dòng thân thiếu: {len(miss)}")
for m in miss[:10]:
    print("  -", m)
sys.exit(1 if miss else 0)
