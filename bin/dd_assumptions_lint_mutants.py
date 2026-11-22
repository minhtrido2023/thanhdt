#!/usr/bin/env python3
"""dd_assumptions_lint_mutants.py — đột biến MÃ của lint: mỗi mutant phải bị selfcheck GIẾT (rc≠0).
Chạy: /usr/bin/python3 bin/dd_assumptions_lint_mutants.py  (rc 0 = ≥ ngưỡng bị giết). Không mạng/BQ."""
import os, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MUTANTS = [
    ("L3 dung sai ×10", 'gap_bp > bands["r_tolerance_bp"] and', 'gap_bp > bands["r_tolerance_bp"] * 10 and'),
    ("L3 bỏ qua β mặc định (dùng β khai)", 'anc["r"] + beta_def * (dr', 'anc["r"] + beta * (dr'),
    ("L3 bỏ kiểm β khác mặc định", "abs(beta - beta_def) > 1e-9", "False"),
    ("enforce không kiểm định dạng dd_date", "isinstance(dd, str) and bool(DATE_RE.match(dd)) and dd >=", "isinstance(dd, str) and dd >="),
    ("L1 dung sai rộng", "abs(tot - 1.0) > 1e-6", "abs(tot - 1.0) > 1"),
    ("L12 chỉ đòi có ≥1 phía", "if not {\"down\", \"base\", \"up\"} <= sides:", "if not sides:"),
    ("L7 bỏ kiểm nhất quán", "comp != must_out and", "False and"),
    ("L7 bỏ đối chiếu cam kết vốn", "if d3_on and not items:", "if False and not items:"),
    ("L11 ngưỡng khong_cong_bo vô hạn", "n_kcb > mx_kcb", "n_kcb > 999"),
    ("L10 bỏ neo hạn công bố", "need = yr - 1 if dd_date[5:] > dl else yr - 2", "need = yr - 1"),
    ("L13 bỏ kiểm trích quỹ", "pct and pct > 0 and", "False and"),
    ("L14 bỏ chặn ngày sau dd_date", "elif age < 0 or age > mx:", "elif age > mx:"),
    ("L8 cho khai mốc trước cùng ngày", "        return set(same_day)\n", "        return set(same_day) | ({before[-1]} if before else set())\n"),
    ("L9 bắt chữ ADV trần", "r\"(\\bADV\\b\\s*[=:]\\s*\\d|", "r\"(\\bADV\\b|"),
    ("gate D3 luôn bật→tắt", "d3_on = (not mv_ok) or mv >= D3_MILESTONE", "d3_on = False"),
]


def main():
    src = open(os.path.join(HERE, "dd_assumptions_lint.py"), encoding="utf-8").read()
    killed = 0
    for name, old, new in MUTANTS:
        if src.count(old) < 1:
            print(f"ERROR mutant '{name}': mẫu không có trong lint (mutant hỏng, không tính)")
            return 2
        with tempfile.TemporaryDirectory() as t:
            os.makedirs(os.path.join(t, "bin"))
            for f in ("dd_assumptions_lint_selfcheck.py",):
                shutil.copy(os.path.join(HERE, f), os.path.join(t, "bin", f))
            open(os.path.join(t, "bin", "dd_assumptions_lint.py"), "w", encoding="utf-8").write(src.replace(old, new, 1))
            os.symlink(os.path.join(ROOT, "kb"), os.path.join(t, "kb"))
            r = subprocess.run(["/usr/bin/python3", os.path.join(t, "bin", "dd_assumptions_lint_selfcheck.py")],
                               capture_output=True, text=True, env={**os.environ, "TZ": "UTC"})
        dead = r.returncode != 0
        killed += dead
        fails = [l for l in r.stdout.splitlines() if l.startswith("FAIL")][:1]
        print(f"{'GIẾT ' if dead else 'SỐNG '} {name}  {fails[0][:90] if fails else ''}")
    print(f"\n{killed}/{len(MUTANTS)} mutant bị giết")
    return 0 if killed >= len(MUTANTS) - 1 else 1


if __name__ == "__main__":
    sys.exit(main())
