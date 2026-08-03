#!/usr/bin/env python3
"""Ground truth cho benchmark srcwalk vs grep.

Dựng bằng ast của Python — KHÔNG dùng srcwalk, KHÔNG dùng grep, nên là trọng tài độc lập.

Phạm vi có chủ đích: CHỈ hàm top-level (module-level def). Method trong class cần suy luận kiểu
để phân giải `obj.method()` — nằm ngoài khả năng của cả 2 công cụ VÀ của ast, nên đưa vào sẽ làm
ground truth thành đoán mò. Giới hạn này được khai báo, không giấu.

Phân giải call site (đây là chỗ ground truth mạnh hơn cả 2 công cụ):
  - trong chính file định nghĩa      -> Name(id=X) là call thật
  - file khác có `from <mod> import X [as A]` và mod khớp basename file định nghĩa -> Name(id=A)
  - file khác có `import <mod> [as A]`                                             -> Attribute(A.X)
Không có binding -> KHÔNG tính, dù văn bản có chứa "X(".
"""
import ast, json, os, sys
from collections import defaultdict

ROOT = "/home/trido/thanhdt/WorkingClaude"
SKIP_PARTS = {".git", "__pycache__", "node_modules", "wc_venv", ".venv", "venv"}


def py_files():
    out = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_PARTS and not d.startswith("wt-")]
        for fn in filenames:
            if fn.endswith(".py"):
                out.append(os.path.join(dirpath, fn))
    return sorted(out)


def rel(p):
    return os.path.relpath(p, ROOT)


def main():
    files = py_files()
    trees = {}
    parse_fail = []
    for p in files:
        try:
            src = open(p, encoding="utf-8", errors="replace").read()
            trees[p] = ast.parse(src)
        except (SyntaxError, ValueError) as e:
            parse_fail.append((rel(p), str(e)[:80]))

    # ---- defs: chỉ top-level ----
    defs = defaultdict(list)          # name -> [(relpath, lineno, kind)]
    for p, tree in trees.items():
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                defs[node.name].append((rel(p), node.lineno, "fn"))
            elif isinstance(node, ast.ClassDef):
                defs[node.name].append((rel(p), node.lineno, "class"))

    # ---- imports per file ----
    # local_alias[p] = {alias_name: (src_module_basename, orig_name)}   từ `from m import x as a`
    # module_alias[p] = {alias_name: module_basename}                   từ `import m as a`
    local_alias = defaultdict(dict)
    module_alias = defaultdict(dict)
    star_import = defaultdict(list)
    for p, tree in trees.items():
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                mod = (node.module or "").split(".")[-1]
                for a in node.names:
                    if a.name == "*":
                        star_import[p].append(mod)
                    else:
                        local_alias[p][a.asname or a.name] = (mod, a.name)
            elif isinstance(node, ast.Import):
                for a in node.names:
                    base = a.name.split(".")[-1]
                    module_alias[p][a.asname or a.name.split(".")[0]] = base
                    module_alias[p][base] = base

    # ---- calls per file: (bare_name_calls, attr_calls) ----
    bare_calls = defaultdict(list)    # p -> [(name, lineno)]
    attr_calls = defaultdict(list)    # p -> [(recv_root, attr, lineno)]
    for p, tree in trees.items():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            f = node.func
            if isinstance(f, ast.Name):
                bare_calls[p].append((f.id, node.lineno))
            elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                attr_calls[p].append((f.value.id, f.attr, node.lineno))

    # ---- resolve callers for uniquely-locatable top-level functions ----
    def resolve(name, def_file_rel):
        """Trả về set (relpath, lineno) là call site THẬT của `name` định nghĩa ở def_file_rel."""
        def_base = os.path.basename(def_file_rel)[:-3]  # bỏ .py
        hits = set()
        for p in trees:
            rp = rel(p)
            if rp == def_file_rel:
                for nm, ln in bare_calls[p]:
                    if nm == name:
                        hits.add((rp, ln))
                continue
            # from <mod> import name [as alias]
            for alias, (mod, orig) in local_alias[p].items():
                if orig == name and mod == def_base:
                    for nm, ln in bare_calls[p]:
                        if nm == alias:
                            hits.add((rp, ln))
            # import <mod>  -> mod.name(...)
            for alias, mod in module_alias[p].items():
                if mod == def_base:
                    for recv, attr, ln in attr_calls[p]:
                        if recv == alias and attr == name:
                            hits.add((rp, ln))
        return sorted(hits)

    out = {
        "meta": {
            "root": ROOT,
            "n_py_files": len(files),
            "n_parsed": len(trees),
            "n_parse_fail": len(parse_fail),
            "parse_fail_sample": parse_fail[:10],
            "scope_note": "top-level functions/classes only; methods excluded (need type inference)",
        },
        "defs": {k: v for k, v in defs.items()},
    }
    with open(os.path.join(os.path.dirname(__file__), "gt_defs.json"), "w") as fh:
        json.dump(out, fh)

    # sanity probes — phải khớp sự thật đã biết từ phiên trước
    print(f"files={len(files)} parsed={len(trees)} parse_fail={len(parse_fail)}")
    print(f"distinct top-level names = {len(defs)}")
    for probe in ("filter_lag_rating_orders", "main"):
        d = defs.get(probe, [])
        print(f"\nPROBE {probe!r}: {len(d)} định nghĩa top-level")
        if len(d) == 1:
            c = resolve(probe, d[0][0])
            print(f"  def tại {d[0][0]}:{d[0][1]}")
            print(f"  call site phân giải được = {len(c)}")
            for f_, l_ in c:
                print(f"    {f_}:{l_}")

    # lưu callers cho mọi name có ĐÚNG 1 định nghĩa top-level
    uniq = {k: v for k, v in defs.items() if len(v) == 1}
    print(f"\nname có đúng 1 def top-level: {len(uniq)}")
    callers = {}
    for i, (name, ((f_, l_, kind),)) in enumerate(sorted(uniq.items())):
        callers[name] = {"def_file": f_, "def_line": l_, "kind": kind,
                         "callers": resolve(name, f_)}
        if i % 500 == 0:
            print(f"  ...{i}/{len(uniq)}", file=sys.stderr)
    with open(os.path.join(os.path.dirname(__file__), "gt_callers.json"), "w") as fh:
        json.dump(callers, fh)
    print(f"đã ghi gt_callers.json ({len(callers)} name)")


if __name__ == "__main__":
    main()
