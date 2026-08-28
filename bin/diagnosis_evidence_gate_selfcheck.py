#!/usr/bin/env python3
"""diagnosis_evidence_gate_selfcheck.py — selfcheck cho bin/diagnosis_evidence_gate.py.

Mỗi assertion dưới đây đều đã được kiểm bằng MUTATION — chạy `--mutations` để tái lập: nó phá
từng điều kiện của gate rồi đòi suite phải ĐỎ. 6/6 mutation bị giết (2026-08-29). Ba "guard giả"
phát hiện bằng chính vòng này (điều kiện `not CAPTURE`, ngưỡng thông điệp ≥40 ký tự, vòng nối
câu lệnh qua `\`) sống sót mọi assertion ⇒ ĐÃ GỠ khỏi gate thay vì giữ lại cho có. Đây là yêu cầu bắt buộc sau retro-2026-08-28 Pattern B
(2/2 lần gần nhất Wags ship assertion không bắt được mutation nó tuyên bố ghim) và
~/.claude/skills/verify-before-done/.

Ca 1 (ĐẮT NHẤT — không phải fixture bịa): lấy NGUYÊN VĂN `bin/append_event.sh` tại
`55b3f34c^`, tức bản ĐÚNG LÚC lỗi thật xảy ra, và bản `55b3f34c` đã vá. Gate phải bắt bản
trước và im trên bản sau. Nếu không có git (sandbox), ca này SKIP có báo, không âm thầm PASS.
"""
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bin"))
import importlib.util

_spec = importlib.util.spec_from_file_location(
    "diag_gate", os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py")
)
diag_gate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(diag_gate)

FAILED = []


def assert_eq(label, got, want):
    ok = got == want
    print(f"  {'PASS' if ok else 'FAIL'}  {label}  (got={got!r} want={want!r})")
    if not ok:
        FAILED.append(label)


def git_show(ref):
    p = subprocess.run(
        ["git", "-C", ROOT, "show", ref], capture_output=True, text=True
    )
    return p.stdout if p.returncode == 0 else None


def main():
    print("== ca 1: code THẬT lúc lỗi (55b3f34c^) vs đã vá (55b3f34c) ==")
    pre = git_show("55b3f34c^:bin/append_event.sh")
    post = git_show("55b3f34c:bin/append_event.sh")
    if pre is None or post is None:
        print("  SKIP  không đọc được git object (sandbox không có lịch sử) — KHÔNG tính PASS")
        FAILED.append("ca1-skipped-no-git")
    else:
        assert_eq("bản TRƯỚC fix bị bắt (đúng 1 chỗ)", len(diag_gate.scan(pre)), 1)
        assert_eq("bản TRƯỚC fix bắt đúng dòng 108", diag_gate.scan(pre)[0][0], 108)
        assert_eq("bản ĐÃ VÁ (2>&1 giữ stderr) KHÔNG bị bắt", len(diag_gate.scan(post)), 0)

    print("== ca 2: idiom default scalar hợp lệ KHÔNG được bắt (67 ca thật trong repo) ==")
    for idiom in [
        'LAST="$(cat "$f" 2>/dev/null || echo 0)"',
        'st="$(stat -c %s "$p" 2>/dev/null || echo unknown)"',
        'x="$(date -d "$t" +%s 2>/dev/null || echo 0)"',
    ]:
        assert_eq(f"không bắt: {idiom[:34]}…", len(diag_gate.scan(idiom)), 0)

    print("== ca 3: dòng COMMENT mô tả chữ ký không bị bắt ==")
    assert_eq(
        "comment không bị bắt",
        len(diag_gate.scan('# xấu: cmd 2>/dev/null || die "một thông điệp chẩn đoán dài hơn bốn mươi ký tự"')),
        0,
    )

    print("== ca 4: chữ ký thật, trải 2 dòng vật lý qua `\\` (đúng hình dạng ca 08-28) ==")
    bad = (
        'python3 -c \'import json,sys; json.loads(sys.argv[1])\' "$p" 2>/dev/null \\\n'
        '  || die "payload không phải JSON hợp lệ — nhiều khả năng bị cắt cụt ở đâu đó."\n'
    )
    assert_eq("bắt được chữ ký nối dòng", len(diag_gate.scan(bad)), 1)
    good = (
        '_e="$(python3 -c \'import json,sys; json.loads(sys.argv[1])\' "$p" 2>&1 >/dev/null)" \\\n'
        '  || die "payload không phải JSON hợp lệ.\\n  Lỗi parser thật: $_e"\n'
    )
    assert_eq("bản bắt-stderr-lại KHÔNG bị bắt", len(diag_gate.scan(good)), 0)

    print("== ca 5: TOÀN BỘ bin/*.sh + hooks/*.sh ở HEAD phải SẠCH (chống FP hồi quy) ==")
    import glob

    total = 0
    for f in sorted(glob.glob(os.path.join(ROOT, "bin", "*.sh"))) + sorted(
        glob.glob(os.path.join(ROOT, "hooks", "*.sh"))
    ):
        with open(f, encoding="utf-8", errors="replace") as fh:
            n = len(diag_gate.scan(fh.read()))
        if n:
            print(f"    hit: {f}")
        total += n
    assert_eq("0 false-positive trên repo thật", total, 0)

    print("== ca 6: exit code + escape hatch ==")
    tmp = os.path.join(ROOT, "logs", ".diag_gate_selfcheck_tmp.sh")
    os.makedirs(os.path.dirname(tmp), exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(bad)
    try:
        env = dict(os.environ)
        env.pop("MIKE_DIAG_GATE", None)
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py"), tmp],
            capture_output=True, text=True, env=env,
        )
        assert_eq("exit 1 khi có vi phạm", r.returncode, 1)
        assert_eq("thông điệp nêu cách sửa (2>&1)", "2>&1" in r.stderr, True)
        env["MIKE_DIAG_GATE"] = "warn"
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py"), tmp],
            capture_output=True, text=True, env=env,
        )
        assert_eq("MIKE_DIAG_GATE=warn → exit 0 nhưng vẫn in cảnh báo", (r.returncode, "⛔" in r.stderr), (0, True))
        env["MIKE_DIAG_GATE"] = "off"
        r = subprocess.run(
            [sys.executable, os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py"), tmp],
            capture_output=True, text=True, env=env,
        )
        assert_eq("MIKE_DIAG_GATE=off → im hoàn toàn", (r.returncode, r.stderr.strip()), (0, ""))
    finally:
        os.path.exists(tmp) and os.remove(tmp)

    print()
    if FAILED:
        print(f"❌ FAIL: {len(FAILED)} — {FAILED}")
        return 1
    print("✅ diagnosis_evidence_gate_selfcheck: ALL PASS")
    return 0


MUTATIONS = [
    ("M2 emitter nới sang echo/printf", "(die|fail|_die|abort)", "(die|fail|_die|abort|echo|printf)"),
    ("M4 bỏ bước bỏ qua dòng comment", 'line.lstrip().startswith("#") or ', ""),
    ("M6 DISCARD nới thành '2>' (mất phân biệt vứt/bắt stderr)",
     'DISCARD = re.compile(r"2>\\s*/dev/null")', 'DISCARD = re.compile(r"2>")'),
    ("M8 bỏ hẳn điều kiện DIAG", 'if DIAG.search("\\n".join(lines[idx : idx + 8])):', "if True:"),
    ("M9 cửa sổ 8 dòng → 1 dòng", "lines[idx : idx + 8]", "lines[idx : idx + 1]"),
    ("M10 bỏ điều kiện DISCARD", "not DISCARD.search(line)", "False"),
]


def run_mutations():
    """Phá từng điều kiện của gate, đòi suite ĐỎ. Mutation SỐNG SÓT = assertion là guard giả."""
    import shutil

    gate = os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py")
    orig = open(gate, encoding="utf-8").read()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    survived = []
    try:
        for desc, a, b in MUTATIONS:
            if a not in orig:
                # Mutation KHÔNG áp được = harness hỏng, KHÔNG phải "gate ổn". Đây chính là bẫy
                # đã cắn lúc viết gate này: sed hỏng âm thầm + __pycache__ cũ ⇒ 3 mutation báo
                # "SURVIVED" sai. Fail to hiểu, đừng báo xanh.
                survived.append(f"HARNESS-BROKEN: {desc}")
                print(f"  ❌ HARNESS-BROKEN  {desc}: không tìm thấy chuỗi cần thay")
                continue
            open(gate, "w", encoding="utf-8").write(orig.replace(a, b, 1))
            shutil.rmtree(os.path.join(ROOT, "bin", "__pycache__"), ignore_errors=True)
            r = subprocess.run(
                [sys.executable, "-B", os.path.abspath(__file__)],
                capture_output=True, text=True, env=env, cwd=ROOT,
            )
            if r.returncode:
                print(f"  KILLED    {desc}")
            else:
                survived.append(desc)
                print(f"  SURVIVED  {desc}  ← assertion tuyên bố canh nhánh này là GUARD GIẢ")
    finally:
        open(gate, "w", encoding="utf-8").write(orig)
        shutil.rmtree(os.path.join(ROOT, "bin", "__pycache__"), ignore_errors=True)
    print()
    if survived:
        print(f"❌ {len(survived)} mutation sống sót: {survived}")
        return 1
    print(f"✅ {len(MUTATIONS)}/{len(MUTATIONS)} mutation bị giết — không có guard giả")
    return 0


if __name__ == "__main__":
    if "--mutations" in sys.argv:
        sys.exit(run_mutations())
    sys.exit(main())
