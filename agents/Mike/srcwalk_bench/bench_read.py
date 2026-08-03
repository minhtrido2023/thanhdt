#!/usr/bin/env python3
"""Tác vụ 3 — ĐỌC FILE: srcwalk outline vs Read nguyên file.

2 câu hỏi, không chỉ 1:
  (a) tiết kiệm bao nhiêu token?
  (b) outline có GIỮ ĐỦ cấu trúc không? (recall = % top-level def xuất hiện trong outline)
Tiết kiệm token mà mất symbol thì không phải thắng, mà là đánh đổi — phải đo cả hai.
"""
import ast, json, os, random, re, subprocess, sys, time

ROOT = "/home/trido/thanhdt/WorkingClaude"
HERE = os.path.dirname(os.path.abspath(__file__))
N = int(sys.argv[1]) if len(sys.argv) > 1 else 150
random.seed(20260803)

SKIP = {".git", "__pycache__", "node_modules", "wc_venv", ".venv", "venv"}


def py_files():
    out = []
    for dp, dn, fns in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP and not d.startswith("wt-")]
        out += [os.path.join(dp, f) for f in fns if f.endswith(".py")]
    return sorted(out)


files = py_files()
random.shuffle(files)
rows = []
for p in files:
    if len(rows) >= N:
        break
    try:
        src = open(p, encoding="utf-8", errors="replace").read()
        tree = ast.parse(src)
    except Exception:
        continue
    toplevel = [n.name for n in tree.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
    if not toplevel:
        continue
    rp = os.path.relpath(p, ROOT)
    t0 = time.perf_counter()
    out = subprocess.run(f"srcwalk '{rp}'", shell=True, cwd=ROOT,
                         capture_output=True, text=True).stdout
    sec = time.perf_counter() - t0
    # symbol nào xuất hiện trong outline?
    found = sum(1 for nm in toplevel if re.search(rf"\b{re.escape(nm)}\b", out))
    rows.append({
        "file": rp,
        "lines": src.count("\n") + 1,
        "read_tok": len(src) / 4,
        "sw_tok": len(out) / 4,
        "n_toplevel": len(toplevel),
        "n_in_outline": found,
        "sec": sec,
        "outline_mode": "outline" if "[outline]" in out.split("\n")[0] else
                        ("preview" if "preview:" in out else "other"),
    })

json.dump(rows, open(os.path.join(HERE, "bench_read.json"), "w"), indent=1)
print(f"N={len(rows)}")
