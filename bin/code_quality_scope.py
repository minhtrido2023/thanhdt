#!/usr/bin/env python3
"""code_quality_scope.py — scope tuần của code_quality_weekly.sh lấy từ production manifest.

Việc J review ARIA (job Wags_20260913_075550). Scope = mọi path tầng T0-T2 trong manifest có
commit trong cửa sổ `--since` ở BẤT KỲ repo nào truyền qua `--repo` (WorkingClaude + mike),
xếp T0 trước rồi T1, T2 (cùng tầng: theo path), cắt tại `--max-files`. T3 (selfcheck) và T?
(chưa phân loại) KHÔNG vào scope. Path trong manifest tương đối `--wc-root`. `--pin` (file hot-core
round-robin của plan §4 mục 2, review dù không đổi) đứng ĐẦU danh sách và tính vào trần.

Kiểm tra HEAD-khớp (production_manifest.py --check) KHÔNG ở đây — code_quality_weekly.sh làm
trước khi gọi; file này chỉ fail-closed khi manifest/git không đọc được.

stdout: path tuyệt đối được giữ, mỗi dòng 1 · `--dropped-out`: path bị trần cắt
stderr: 1 dòng tóm tắt · exit 0 = ok (scope rỗng hợp lệ) · exit 3 = manifest/git hỏng ⇒ fallback
"""
import argparse
import json
import os
import subprocess
import sys

TIERS = ("T0", "T1", "T2")


def touched(repo, since):
    """Path tuyệt đối có commit trong cửa sổ, trong phạm vi `repo` (có thể là thư mục con)."""
    top = subprocess.run(["git", "-C", repo, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True, check=True).stdout.strip()
    # `-- .` khoá vào `repo` khi nó là thư mục con của toplevel lớn hơn (WorkingClaude ⊂ thanhdt)
    out = subprocess.run(["git", "-C", repo, "log", f"--since={since}", "--name-only",
                          "--pretty=format:", "--", "."],
                         capture_output=True, text=True, check=True).stdout
    return {os.path.join(top, line) for line in out.splitlines() if line.strip()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--wc-root", required=True)
    ap.add_argument("--repo", action="append", required=True)
    ap.add_argument("--since", default="7 days ago")
    ap.add_argument("--max-files", type=int, required=True)
    ap.add_argument("--dropped-out", required=True)
    ap.add_argument("--pin", default="", help="path tuyệt đối luôn giữ ở đầu scope (bỏ qua nếu không tồn tại)")
    a = ap.parse_args()

    try:
        files = json.load(open(a.manifest, encoding="utf-8"))["files"]
        tiers = {p: v["tier"] for p, v in files.items()}
    except Exception as e:  # thiếu / JSON hỏng / sai schema
        print(f"manifest-scope: FAIL đọc manifest {a.manifest}: {e!r}", file=sys.stderr)
        return 3
    if not any(t in TIERS for t in tiers.values()):
        print(f"manifest-scope: FAIL manifest {a.manifest} không có file T0-T2 nào", file=sys.stderr)
        return 3

    wc = os.path.realpath(a.wc_root)
    try:
        hit = set()
        for r in a.repo:
            hit |= touched(r, a.since)
    except (subprocess.CalledProcessError, OSError) as e:
        print(f"manifest-scope: FAIL git log: {e!r}", file=sys.stderr)
        return 3
    hit_rel = {os.path.relpath(os.path.realpath(p), wc) for p in hit}

    eligible = sorted((p for p, t in tiers.items()
                       if t in TIERS and p in hit_rel and os.path.isfile(os.path.join(wc, p))),
                      key=lambda p: (TIERS.index(tiers[p]), p))
    pin = os.path.relpath(os.path.realpath(a.pin), wc) if a.pin and os.path.isfile(a.pin) else ""
    ordered = ([pin] if pin else []) + [p for p in eligible if p != pin]
    kept, dropped = ordered[:a.max_files], ordered[a.max_files:]
    n_t3 = sum(1 for p, t in tiers.items() if t not in TIERS and p in hit_rel)

    for p in kept:
        print(os.path.join(wc, p))
    with open(a.dropped_out, "w", encoding="utf-8") as fh:
        fh.writelines(os.path.join(wc, p) + "\n" for p in dropped)
    cnt = {t: sum(1 for p in kept if p != pin and tiers.get(p) == t) for t in TIERS}
    print(f"manifest-scope: {len(eligible)} file T0-T2 có commit ({a.since}) — giữ {len(kept)} "
          f"(pin={pin or '-'} T0={cnt['T0']} T1={cnt['T1']} T2={cnt['T2']}), trần cắt {len(dropped)}, "
          f"loại {n_t3} file T3/T? có commit", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
