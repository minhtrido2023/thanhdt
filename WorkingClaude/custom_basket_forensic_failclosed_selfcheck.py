#!/usr/bin/env python3
"""Self-check FAIL-CLOSED cho `custom_basket.load_forensic_excludes()` (2026-09-27).

CHỨNG MINH 2 CHIỀU, không chỉ "bản mới chạy được":
  (a) file THIẾU ở mọi cây  → bản VÁ **TỪ CHỐI CHẠY** (SystemExit trích exception thật),
      bản CŨ (lấy NGUYÊN VĂN từ `git show`) in "none" rồi ĐI TIẾP với {} ⇒ 8 mã lọt vào universe.
  (b) file CÓ đầy đủ        → hai bản cho **cùng một** dict 8 mã (bản vá không đổi hành vi).

Chạy:  $DNA_PYEXE custom_basket_forensic_failclosed_selfcheck.py [--mutations] [--all-tz]
  --mutations  đột biến mã nguồn và đòi selfcheck GIẾT được từng con
  --all-tz     chạy lại toàn bộ dưới nhiều TZ + `env -u TZ` (§16: selfcheck kế thừa TZ đúng của
               tác giả thì pass vô điều kiện — phải chạy dưới TZ lạ mới có nghĩa)
"""
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(HERE, "custom_basket.py")
CANON_FLAGS = None  # điền ở runtime
EXPECT = {"BFC", "DIG", "HHS", "KLB", "KSF", "L40", "PC1", "VVS"}

_n_assert = 0


def ok(cond, msg):
    global _n_assert
    _n_assert += 1
    if not cond:
        raise AssertionError(msg)


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def sandbox(src=MODULE, with_flags=False, flags_text=None):
    """Cây tạm NGOÀI git (⇒ chỉ 1 candidate) chứa một bản copy của module."""
    d = tempfile.mkdtemp(prefix="forxsc_")
    shutil.copy(src, os.path.join(d, "custom_basket.py"))
    if with_flags or flags_text is not None:
        os.makedirs(os.path.join(d, "data"), exist_ok=True)
        dst = os.path.join(d, "data", "forensic_flags.csv")
        if flags_text is not None:
            open(dst, "w").write(flags_text)
        else:
            shutil.copy(CANON_FLAGS, dst)
    return d


def env_clean():
    os.environ.pop("BASKET_FORENSIC_FLAGS", None)


def old_block_source():
    """Khối fail-open CŨ, lấy NGUYÊN VĂN từ git (không chép tay ⇒ không thể lệch)."""
    blob = subprocess.run(["git", "show", "HEAD:WorkingClaude/custom_basket.py"], cwd=HERE,
                          capture_output=True, text=True, check=True).stdout
    m = re.search(r"\n(    _FORX = \{\}\n    try:\n.*?\n        print\(f\"  \[forensic exclude\] "
                  r"none \(\{e\}\)\"\)\n)", blob, re.S)
    assert m, "không tìm được khối fail-open cũ trong HEAD — dừng, đừng đoán"
    return m.group(1)


def run_old_block(workdir):
    """Chạy khối CŨ với `__file__` trỏ vào `workdir` ⇒ tái hiện hành vi cũ đúng cây đó."""
    import io
    import contextlib
    import pandas as pd
    import textwrap
    src = textwrap.dedent(old_block_source())
    body = "def _old(__file__):\n" + textwrap.indent(src, "    ") + "    return _FORX\n"
    ns = {"pd": pd, "os": os}
    exec(body, ns)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        got = ns["_old"](os.path.join(workdir, "custom_basket.py"))
    return got, buf.getvalue()


# ─────────────────────────── các phép thử, chạy trên MỘT module ───────────────────────────
def t_canonical_fallback(mod, cap):
    """T1 — worktree KHÔNG có file (.gitignore) nhưng cây canonical có ⇒ vẫn lọc đủ 8 mã."""
    env_clean()
    cands = mod._forensic_flags_candidates()
    ok(len(cands) >= 2, f"T1: thiếu cây canonical trong candidates: {cands}")
    ok(not os.path.exists(cands[0]),
       "T1: worktree LẠI có forensic_flags.csv — tiền đề của test sai, kiểm .gitignore")
    ok(os.path.exists(cands[1]), f"T1: cây canonical không tồn tại: {cands[1]}")
    out, got = cap(mod.load_forensic_excludes)
    ok(set(got) == EXPECT, f"T1: kỳ vọng {sorted(EXPECT)}, được {sorted(got)}")
    ok("cây canonical" in out, f"T1: không in dấu vết cây canonical:\n{out}")
    ok("none" not in out, f"T1: vẫn in 'none':\n{out}")


def t_missing_everywhere_is_fatal(mod, cap):
    """T2 — thiếu ở MỌI cây ⇒ TỪ CHỐI CHẠY, và thông điệp trích exception THẬT (§29)."""
    env_clean()
    d = sandbox(src=mod.__file__)
    m2 = load(os.path.join(d, "custom_basket.py"), "cb_sandbox_missing")
    ok(len(m2._forensic_flags_candidates()) == 1,
       "T2: sandbox phải NGOÀI git (1 candidate) — nếu >1 thì test không còn chứng minh gì")
    try:
        out, got = cap(m2.load_forensic_excludes)
    except SystemExit as e:
        msg = str(e)
        ok("FileNotFoundError" in msg,
           f"T2: thông điệp không trích exception THẬT của pandas/OS:\n{msg}")
        ok(d in msg, f"T2: không liệt kê đường dẫn đã thử:\n{msg}")
        ok("BASKET_FORENSIC_FLAGS" in msg, f"T2: không nêu lối thoát env:\n{msg}")
        ok("rỗng" in msg, f"T2: không nêu lối thoát 'chạy KHÔNG lọc':\n{msg}")
        ok("PC1" in msg and "BANNED" in msg,
           f"T2: không nói HỆ QUẢ (8 mã / BANNED) nên người đọc không biết vì sao chặn:\n{msg}")
        return
    raise AssertionError(f"T2: KHÔNG từ chối chạy — trả {sorted(got)}, log:\n{out}")


def t_old_vs_new_two_sided(mod, cap):
    """T3 — 2 CHIỀU trên CÙNG sandbox: bản cũ fail-OPEN, bản mới fail-CLOSED; có file thì bằng nhau."""
    env_clean()
    d_no = sandbox(src=mod.__file__)
    got_old, out_old = run_old_block(d_no)
    ok(got_old == {}, f"T3a: bản cũ đáng lẽ trả {{}} (fail-open), được {got_old}")
    ok("none" in out_old, f"T3a: bản cũ đáng lẽ in 'none', log:\n{out_old}")
    m_no = load(os.path.join(d_no, "custom_basket.py"), "cb_two_sided_no")
    raised = False
    try:
        cap(m_no.load_forensic_excludes)
    except SystemExit:
        raised = True
    ok(raised, "T3a: bản mới KHÔNG chặn trong khi bản cũ đi tiếp ⇒ bản vá vô hiệu")

    d_yes = sandbox(src=mod.__file__, with_flags=True)
    got_old2, _ = run_old_block(d_yes)
    m_yes = load(os.path.join(d_yes, "custom_basket.py"), "cb_two_sided_yes")
    _, got_new2 = cap(m_yes.load_forensic_excludes)
    ok(set(got_old2) == EXPECT, f"T3b: bản cũ với file đủ ra {sorted(got_old2)}")
    ok(got_old2 == got_new2,
       f"T3b: có file mà 2 bản KHÁC nhau — bản vá đổi hành vi: cũ {got_old2} vs mới {got_new2}")


def t_env_empty_is_explicit_optout(mod, cap):
    """T4 — `BASKET_FORENSIC_FLAGS=` rỗng = KHAI tường minh muốn chạy không lọc (khác thiếu file)."""
    os.environ["BASKET_FORENSIC_FLAGS"] = ""
    try:
        out, got = cap(mod.load_forensic_excludes)
    finally:
        env_clean()
    ok(got == {}, f"T4: rỗng đáng lẽ trả {{}}, được {sorted(got)}")
    ok("TẮT TƯỜNG MINH" in out, f"T4: không in dấu vết opt-out:\n{out}")


def t_env_bad_path_is_fatal_no_fallback(mod, cap):
    """T5 — env trỏ file KHÔNG tồn tại ⇒ chặn, và KHÔNG âm thầm rơi về cây canonical."""
    bad = os.path.join(tempfile.mkdtemp(prefix="forxsc_bad_"), "khong_ton_tai.csv")
    os.environ["BASKET_FORENSIC_FLAGS"] = bad
    try:
        out, got = cap(mod.load_forensic_excludes)
    except SystemExit as e:
        msg = str(e)
        ok(bad in msg, f"T5: không nêu đường dẫn env đã thử:\n{msg}")
        ok("FileNotFoundError" in msg, f"T5: không trích exception thật:\n{msg}")
        ok("data/forensic_flags.csv" not in msg.split("Đã thử")[1].split("Cách thoát")[0],
           f"T5: đã ÂM THẦM thử cây canonical dù người gọi chỉ định file khác:\n{msg}")
        return
    finally:
        env_clean()
    raise AssertionError(f"T5: env trỏ file sai mà vẫn chạy — trả {sorted(got)}, log:\n{out}")


def t_corrupt_file_is_fatal(mod, cap):
    """T6 — file CÓ nhưng hỏng lược đồ (thiếu cột `severity`) ⇒ chặn, trích KeyError thật."""
    env_clean()
    d = sandbox(src=mod.__file__, flags_text="ticker,date\nKSF,2026-06-20\n")
    m2 = load(os.path.join(d, "custom_basket.py"), "cb_corrupt")
    try:
        out, got = cap(m2.load_forensic_excludes)
    except SystemExit as e:
        msg = str(e)
        ok("KeyError" in msg, f"T6: không trích exception thật của lược đồ hỏng:\n{msg}")
        ok("severity" in msg, f"T6: không nêu cột gây lỗi:\n{msg}")
        return
    raise AssertionError(f"T6: file hỏng mà vẫn chạy — trả {sorted(got)}, log:\n{out}")


TESTS = [t_canonical_fallback, t_missing_everywhere_is_fatal, t_old_vs_new_two_sided,
         t_env_empty_is_explicit_optout, t_env_bad_path_is_fatal_no_fallback,
         t_corrupt_file_is_fatal]


def capture(fn, *a, **k):
    import io
    import contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        r = fn(*a, **k)
    return buf.getvalue(), r


def run_all(mod, verbose=True):
    fails = []
    for t in TESTS:
        try:
            t(mod, capture)
            if verbose:
                print(f"  PASS {t.__name__}")
        except (AssertionError, Exception, SystemExit) as e:
            fails.append(f"{t.__name__}: {type(e).__name__}: {e}")
            if verbose:
                print(f"  FAIL {t.__name__}: {type(e).__name__}: {e}")
    return fails


# ─────────────────────────────────── đột biến ───────────────────────────────────
MUTATIONS = [
    ("M1 fail-open lại (raise → return {})",
     lambda s: s.replace("    raise SystemExit(os.linesep.join([",
                         "    return {}\n    raise SystemExit(os.linesep.join([")),
    ("M2 bỏ cây canonical (chỉ cây module)",
     lambda s: s.replace("        cands.append(os.path.normpath(os.path.join(canon, FORENSIC_FLAGS_NAME)))",
                         "        pass")),
    ("M3 env rỗng bị coi như THIẾU file (mất lối thoát tường minh)",
     lambda s: s.replace('        if not env_path:', '        if False:')),
    ("M4 env trỏ sai thì âm thầm rơi về cây canonical",
     lambda s: s.replace('        cands, src = [env_path], "env BASKET_FORENSIC_FLAGS"',
                         '        cands, src = [env_path] + _forensic_flags_candidates(), "env"')),
    ("M5 thông điệp KHÔNG trích exception thật (§29: đoán nguyên nhân)",
     lambda s: s.replace('            errs.append(f"    {path}" + os.linesep + f"      -> {type(e).__name__}: {e}")',
                         '            errs.append(f"    {path}" + os.linesep + "      -> chac la thieu file")')),
    ("M6 bỏ HỆ QUẢ khỏi thông điệp (người đọc không biết vì sao chặn)",
     lambda s: s.replace('"PC1/VVS/KSF thuộc BANNED vĩnh viễn) mà chỉ in \'none\'.",',
                         '"", ')),
]


def run_mutations():
    base = open(MODULE, encoding="utf-8").read()
    killed = 0
    for i, (name, mut) in enumerate(MUTATIONS):
        src = mut(base)
        if src == base:
            print(f"  ERROR  {name}: đột biến KHÔNG áp được (pattern lệch) — sửa selfcheck")
            continue
        p = os.path.join(HERE, f"_mut_custom_basket_{i}.py")   # CÙNG cây ⇒ T1 vẫn có nghĩa
        open(p, "w", encoding="utf-8").write(src)
        try:
            m = load(p, f"cb_mut_{i}")
            fails = run_all(m, verbose=False)
        except BaseException as e:
            fails = [f"import/chạy lỗi: {type(e).__name__}: {e}"]
        finally:
            os.remove(p)
        if fails:
            killed += 1
            print(f"  KILLED {name}\n           ← {', '.join(f.split(':')[0] for f in fails)}"
                  f" | {fails[0][:150]}")
        else:
            print(f"  SURVIVED {name}  ⚠️ selfcheck KHÔNG bắt được con này")
    print(f"\nmutation: {killed}/{len(MUTATIONS)} bị giết")
    return killed == len(MUTATIONS)


def main():
    global CANON_FLAGS
    import custom_basket as cb0
    CANON_FLAGS = [c for c in cb0._forensic_flags_candidates() if os.path.exists(c)][0]
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}  "
          f"module={MODULE}\nregistry canonical = {CANON_FLAGS}")
    mod = load(MODULE, "cb_under_test")
    fails = run_all(mod)
    good = not fails
    if "--mutations" in sys.argv:
        print("\n── đột biến ──")
        good = run_mutations() and good
    print(f"\n{'PASS' if good else 'FAIL'}  ({_n_assert} assertion"
          f"{', ' + str(len(fails)) + ' test FAIL' if fails else ''})")
    return 0 if good else 1


if __name__ == "__main__":
    if "--all-tz" in sys.argv:
        args = [a for a in sys.argv[1:] if a != "--all-tz"]
        rc = 0
        for tz in ["Asia/Ho_Chi_Minh", "America/New_York", "UTC", None]:
            print(f"\n══════ TZ={tz or 'UNSET (env -u TZ)'} ══════")
            cmd = ["env"] + (["-u", "TZ"] if tz is None else [f"TZ={tz}"]) \
                + [sys.executable, os.path.abspath(__file__)] + args
            rc |= subprocess.run(cmd).returncode
        print(f"\n===== ALL-TZ {'PASS' if rc == 0 else 'FAIL'} =====")
        sys.exit(rc)
    sys.exit(main())
