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
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "bin"))
import importlib.util

# File gate ĐANG được kiểm. Mặc định = bản production; `--mutations` trỏ biến này sang một BẢN
# SAO trong mkdtemp để KHÔNG BAO GIỜ ghi đè file thật trong worktree sống (arch-review
# 2026-08-29: `finally` không cứu được SIGKILL/OOM, sẽ để lại gate bị tháo ngòi ở đúng checkout
# mà mọi commit sau chạy qua).
GATE_PATH = os.environ.get(
    "MIKE_DIAG_GATE_TARGET", os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py")
)

_spec = importlib.util.spec_from_file_location("diag_gate", GATE_PATH)
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

    print("== ca 7: các cách viết KHÁC cùng khiếm khuyết (bề rộng vòng 2, arch-review 08-29) ==")
    # Mỗi dòng dưới đây vứt stderr y hệt ca 08-28 nhưng bản gate vòng 1 ĐỀU ĐỂ LỌT. Mỗi hình
    # dạng có 1 mutation tương ứng trong MUTATIONS (M11–M17) — phá nhánh nào thì đúng dòng đó ĐỎ.
    shapes = {
        "M11 `>/dev/null 2>&1` (idiom 84 hit trong repo)":
            'jq . "$f" >/dev/null 2>&1 || die "file cấu hình hỏng — chắc do ai đó sửa tay"',
        "M12 `&>/dev/null` (bash gộp)":
            'jq . "$f" &>/dev/null || die "file cấu hình hỏng — chắc do ai đó sửa tay"',
        "M13 `2>&-` (đóng hẳn descriptor)":
            'jq . "$f" 2>&- || die "file cấu hình hỏng — chắc do ai đó sửa tay"',
        "M14 nhánh die bọc trong nhóm ngoặc nhọn":
            'jq . "$f" 2>/dev/null || { die "file cấu hình hỏng — chắc do ai đó sửa tay"; }',
        "M15 hàm chết tên `_fail` (có thật, preflight_check.sh:36)":
            'jq . "$f" 2>/dev/null || _fail "file cấu hình hỏng — chắc do ai đó sửa tay"',
        "M16 hàm chết tên `fatal`":
            'jq . "$f" 2>/dev/null || fatal "file cấu hình hỏng — chắc do ai đó sửa tay"',
        "M17 hàm chết tên `bail`":
            'jq . "$f" 2>/dev/null || bail "file cấu hình hỏng — chắc do ai đó sửa tay"',
    }
    for label, src in shapes.items():
        assert_eq(f"bắt được: {label}", len(diag_gate.scan(src)), 1)

    print("== ca 8: bề rộng mới KHÔNG được nuốt các dạng hợp lệ ==")
    # `2>&1 >/dev/null` GIỮ stderr (đảo thứ tự so với `>/dev/null 2>&1`) — đây là cách ĐÚNG.
    assert_eq(
        "thứ tự đảo (2>&1 >/dev/null = bắt lại) KHÔNG bị bắt",
        len(diag_gate.scan('_e="$(jq . "$f" 2>&1 >/dev/null)" || die "cấu hình hỏng: $_e"')),
        0,
    )
    assert_eq(
        "`>/dev/null 2>&1 || echo <default>` KHÔNG bị bắt",
        len(diag_gate.scan('n="$(wc -l <"$f" >/dev/null 2>&1 || echo 0)"')),
        0,
    )
    assert_eq(
        "hàm KHÔNG-chết tên lạ (`|| myfail`) KHÔNG bị bắt",
        len(diag_gate.scan('jq . "$f" 2>/dev/null || myfail "thông điệp nào đó"')),
        0,
    )

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
    # tmpdir chứ KHÔNG phải logs/ trong repo — khớp quy ước của ops_health_check_selfcheck.py:118
    # / job_cancel_guard_selfcheck.py:483; selfcheck bị kill giữa chừng không để rác trong repo.
    tmpdir = tempfile.mkdtemp(prefix="diag_gate_sc_")
    tmp = os.path.join(tmpdir, "dirty.sh")
    with open(tmp, "w", encoding="utf-8") as fh:
        fh.write(bad)
    try:
        env = dict(os.environ)
        env.pop("MIKE_DIAG_GATE", None)
        r = subprocess.run(
            [sys.executable, GATE_PATH, tmp],
            capture_output=True, text=True, env=env,
        )
        assert_eq("exit 1 khi có vi phạm", r.returncode, 1)
        assert_eq("thông điệp nêu cách sửa (2>&1)", "2>&1" in r.stderr, True)
        env["MIKE_DIAG_GATE"] = "warn"
        r = subprocess.run(
            [sys.executable, GATE_PATH, tmp],
            capture_output=True, text=True, env=env,
        )
        assert_eq("MIKE_DIAG_GATE=warn → exit 0 nhưng vẫn in cảnh báo", (r.returncode, "⛔" in r.stderr), (0, True))
        env["MIKE_DIAG_GATE"] = "off"
        r = subprocess.run(
            [sys.executable, GATE_PATH, tmp],
            capture_output=True, text=True, env=env,
        )
        assert_eq("MIKE_DIAG_GATE=off → im hoàn toàn", (r.returncode, r.stderr.strip()), (0, ""))
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print()
    if FAILED:
        print(f"❌ FAIL: {len(FAILED)} — {FAILED}")
        return 1
    print("✅ diagnosis_evidence_gate_selfcheck: ALL PASS")
    return 0


MUTATIONS = [
    ("M2 emitter nới sang echo/printf",
     "(_die|_fail|die|fail|fatal|abort|bail)",
     "(_die|_fail|die|fail|fatal|abort|bail|echo|printf)"),
    ("M4 bỏ bước bỏ qua dòng comment", 'line.lstrip().startswith("#") or ', ""),
    ("M6 DISCARD nới thành '2>' (mất phân biệt vứt/bắt stderr)",
     'r"2>\\s*/dev/null"  # cmd 2>/dev/null', 'r"2>"  # cmd 2>/dev/null'),
    ("M8 bỏ hẳn điều kiện DIAG", 'if DIAG.search("\\n".join(lines[idx : idx + 8])):', "if True:"),
    ("M9 cửa sổ 8 dòng → 1 dòng", "lines[idx : idx + 8]", "lines[idx : idx + 1]"),
    ("M10 bỏ điều kiện DISCARD", "not DISCARD.search(line)", "False"),
    # M11–M17: mỗi hình dạng thêm ở vòng 2 có đúng 1 mutation. Sống sót = assertion ca 7 là
    # guard giả ⇒ gỡ nhánh đó khỏi gate, đừng giữ cho có (retro-2026-08-28 Pattern B).
    ("M11 bỏ nhánh `>/dev/null 2>&1`", 'r"|>\\s*/dev/null\\s+2>&1"', 'r""'),
    ("M12 bỏ nhánh `&>/dev/null`", 'r"|&>\\s*/dev/null"', 'r""'),
    ("M13 bỏ nhánh `2>&-`", 'r"|2>&-"', 'r""'),
    ("M14 bỏ nhóm ngoặc nhọn `|| { die …; }`", '\\{?\\s*(', '('),
    ("M15 bỏ tên hàm chết `_fail`", "_fail|", ""),
    ("M16 bỏ tên hàm chết `fatal`", "fatal|", ""),
    ("M17 bỏ tên hàm chết `bail`", "|bail", ""),
]


def run_mutations():
    """Phá từng điều kiện của gate, đòi suite ĐỎ. Mutation SỐNG SÓT = assertion là guard giả.

    Mutate trên BẢN SAO trong mkdtemp và trỏ selfcheck vào bản sao qua MIKE_DIAG_GATE_TARGET —
    file production trong worktree KHÔNG BAO GIỜ bị ghi. Bản vòng 1 ghi đè chính
    bin/diagnosis_evidence_gate.py rồi restore ở `finally`; `finally` không chạy khi bị SIGKILL/
    OOM, nên một lần kill đúng lúc để lại gate ĐÃ BỊ THÁO NGÒI (`if True:`) trong checkout mà mọi
    commit sau đi qua (arch-review 2026-08-29, check race_idempotency = fail).
    """
    import hashlib

    gate_src = os.path.join(ROOT, "bin", "diagnosis_evidence_gate.py")
    orig = open(gate_src, encoding="utf-8").read()
    sha_before = hashlib.sha256(orig.encode("utf-8")).hexdigest()
    tmpdir = tempfile.mkdtemp(prefix="diag_gate_mut_")
    mutant = os.path.join(tmpdir, "diagnosis_evidence_gate.py")
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
            with open(mutant, "w", encoding="utf-8") as fh:
                fh.write(orig.replace(a, b, 1))
            env = dict(
                os.environ, PYTHONDONTWRITEBYTECODE="1", MIKE_DIAG_GATE_TARGET=mutant
            )
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
        shutil.rmtree(tmpdir, ignore_errors=True)
    # Bằng chứng cơ học rằng file production không bị đụng — không dựa vào `finally`.
    sha_after = hashlib.sha256(open(gate_src, "rb").read()).hexdigest()
    if sha_after != sha_before:
        survived.append("PRODUCTION-FILE-MODIFIED")
        print(f"  ❌ file gate production BỊ THAY ĐỔI: {sha_before[:12]} → {sha_after[:12]}")
    else:
        print(f"  OK        file gate production nguyên vẹn (sha256 {sha_before[:12]}…)")
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
