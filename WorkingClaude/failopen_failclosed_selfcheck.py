#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check FAIL-CLOSED cho 3 call-site fail-open vá 2026-09-27 (user duyệt 23:51 ICT).

Vì sao không import module rồi gọi hàm: cả hai khối nằm trong đường chạy NẶNG
(`rating_8l.main()` query BigQuery; `pt_v23_audit_2014.py` chạy cả backtest ngay khi import).
Nên lấy NGUYÊN VĂN khối mã từ file rồi exec trong namespace cô lập — cùng kỹ thuật với
`custom_basket_forensic_failclosed_selfcheck.run_old_block()`, không chép tay ⇒ không thể lệch.

CHỨNG MINH 2 CHIỀU: bản CŨ (lấy từ `git show <OLD_REF>:`) đi tiếp im lặng, bản MỚI từ chối.

Chạy:  $DNA_PYEXE failopen_failclosed_selfcheck.py
"""
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import textwrap

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
CANON_FLAGS = os.path.join(HERE, "data", "forensic_flags.csv")
OLD_REF = os.environ.get("FAILOPEN_OLD_REF", "").strip() or "main"

_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src_of(path, ref=None):
    if ref is None:
        return open(os.path.join(HERE, path), encoding="utf-8").read()
    rel = os.path.relpath(os.path.join(HERE, path),
                          subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                                         capture_output=True, text=True, check=True).stdout.strip())
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"không đọc được {ref}:{rel} — git nói: {r.stderr.strip()}")
    return r.stdout


def block(text, start_pat, end_pat, what):
    """Cắt khối từ dòng khớp start_pat tới dòng khớp end_pat (bao gồm cả hai)."""
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if re.search(start_pat, l)), None)
    assert i is not None, f"không tìm thấy điểm ĐẦU của {what}: /{start_pat}/ — dừng, đừng đoán"
    j = next((k for k in range(i, len(lines)) if re.search(end_pat, lines[k])), None)
    assert j is not None, f"không tìm thấy điểm CUỐI của {what}: /{end_pat}/ — dừng, đừng đoán"
    return "".join(lines[i:j + 1])


def run_block(code, ns):
    body = "def _b():\n" + textwrap.indent(textwrap.dedent(code), "    ") + "\n    return locals()\n"
    g = dict(ns)
    g.update({"pd": pd, "os": os, "sys": sys, "re": re})
    exec(body, g)
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            loc = g["_b"]()
        return loc, buf.getvalue(), None
    except SystemExit as e:
        return None, buf.getvalue(), str(e)


# ───────────────────────────── rating_8l.py — cổng LIVE ─────────────────────────────
R8_START = r"^    # FAIL-CLOSED tu 2026-09-27|^    try:\s*$"
R8_NEW = None


def r8_new_block():
    s = src_of("rating_8l.py")
    return block(s, r"^    _forx_env = os\.environ\.get\(\"RATING8L_FORENSIC_FLAGS\"\)",
                 r"Chay KHONG overrides mot cach co y", "khối forensic MỚI của rating_8l")


def r8_old_block():
    """Khối CŨ: bắt trọn `try:`...`FORENSIC = {}` (thụt 4) — KHÔNG lấy dòng `global FORENSIC`
    để `FORENSIC` là biến LOCAL của wrapper ⇒ đọc lại được qua locals()."""
    s = src_of("rating_8l.py", OLD_REF)
    m = re.search(r"\n(    try:\n        _fg = pd\.read_csv\(os\.path\.join\(WORKDIR,\"data\","
                  r"\"forensic_flags\.csv\"\)\).*?FORENSIC = \{\}\n)", s, re.S)
    assert m, f"không tìm được khối forensic CŨ trong {OLD_REF} — dừng, đừng đoán"
    return m.group(1)


def t_r8_default_canonical():
    """T1 — mặc định (cây canonical) ⇒ nạp đủ, 8 mã exclude."""
    env = {k: v for k, v in os.environ.items()}
    os.environ.pop("RATING8L_FORENSIC_FLAGS", None)
    loc, out, exc = run_block(r8_new_block(), {"WORKDIR": HERE})
    os.environ.clear(); os.environ.update(env)
    ok(exc is None, f"T1: không được TỪ CHỐI khi file có thật: {exc}")
    forensic = loc["FORENSIC"]
    ok(len(forensic) == 11, f"T1: kỳ vọng 11 dòng cờ (12 dòng file − 1 header), được {len(forensic)}")
    excl = sorted(t for t, (s, _, _) in forensic.items() if s == "exclude")
    ok(excl == ["BFC", "DIG", "HHS", "KLB", "KSF", "L40", "PC1", "VVS"], f"T1: excl sai: {excl}")
    ok("forensic-gov" in out, f"T1: thiếu dấu vết:\n{out}")


def t_r8_missing_is_fatal_and_old_was_silent():
    """T2 — hai chiều: bản MỚI TỪ CHỐI + trích lỗi thật; bản CŨ đi tiếp với {} (8 mã lọt cổng)."""
    d = tempfile.mkdtemp(prefix="fo8l_")
    env = {k: v for k, v in os.environ.items()}
    os.environ.pop("RATING8L_FORENSIC_FLAGS", None)
    loc, out, exc = run_block(r8_new_block(), {"WORKDIR": d})
    ok(exc is not None, f"T2: bản MỚI phải TỪ CHỐI khi thiếu file, nhưng đi tiếp:\n{out}")
    ok("TU CHOI CHAY" in exc, f"T2: thông điệp không nói rõ từ chối:\n{exc}")
    ok("FileNotFoundError" in exc, f"T2: không trích exception THẬT (§29):\n{exc}")
    ok("rating<=3" in exc, f"T2: không nói hệ quả (lọt cổng rating<=3):\n{exc}")
    loc_o, out_o, exc_o = run_block(r8_old_block(), {"WORKDIR": d, "FORENSIC": None})
    os.environ.clear(); os.environ.update(env)
    ok(exc_o is None, f"T2: bản CŨ không lẽ cũng từ chối? {exc_o}")
    ok(loc_o["FORENSIC"] == {}, f"T2: bản CŨ phải trả {{}}, được {loc_o['FORENSIC']}")
    ok("load fail" in out_o, f"T2: bản CŨ phải chỉ in 'load fail':\n{out_o}")


def t_r8_env_empty_is_explicit_optout():
    """T3 — RATING8L_FORENSIC_FLAGS="" = khai tường minh, KHÁC HẲN thiếu file."""
    env = {k: v for k, v in os.environ.items()}
    os.environ["RATING8L_FORENSIC_FLAGS"] = ""
    loc, out, exc = run_block(r8_new_block(), {"WORKDIR": tempfile.mkdtemp(prefix="fo8l_")})
    os.environ.clear(); os.environ.update(env)
    ok(exc is None, f"T3: opt-out tường minh không được từ chối: {exc}")
    ok(loc["FORENSIC"] == {}, f"T3: phải rỗng, được {loc['FORENSIC']}")
    ok("TAT TUONG MINH" in out, f"T3: không in dấu vết opt-out:\n{out}")


def t_r8_env_bad_path_no_silent_fallback():
    """T4 — env trỏ đường dẫn sai ⇒ TỪ CHỐI, KHÔNG âm thầm rơi về cây canonical."""
    env = {k: v for k, v in os.environ.items()}
    bad = os.path.join(tempfile.mkdtemp(prefix="fo8l_"), "khong_co.csv")
    os.environ["RATING8L_FORENSIC_FLAGS"] = bad
    loc, out, exc = run_block(r8_new_block(), {"WORKDIR": HERE})
    os.environ.clear(); os.environ.update(env)
    ok(exc is not None, f"T4: phải từ chối, nhưng đi tiếp (có thể đã fallback về canonical):\n{out}")
    ok(bad in exc, f"T4: thông điệp không nêu đúng đường dẫn đã thử:\n{exc}")


# ───────────────────── pt_v23_audit_2014.py — WORKDIR + cổng LAG ─────────────────────
def pt_workdir_block():
    s = src_of("pt_v23_audit_2014.py")
    return block(s, r'^WORKDIR = os\.environ\.get\("PT_WORKDIR"',
                 r'nhung cay do phai co du data/', "khối WORKDIR mới")


def t_pt_workdir_warns_on_tree_mismatch():
    """T5 — file ở cây A mà WORKDIR là cây B ⇒ in CẢNH BÁO to; cùng cây ⇒ im lặng."""
    code = pt_workdir_block()
    # cắt bỏ 2 dòng cuối (sys.path/chdir không có trong khối) — khối đã dừng ở print cuối.
    other = tempfile.mkdtemp(prefix="ptwd_")
    env = {k: v for k, v in os.environ.items()}
    os.environ.pop("PT_WORKDIR", None)
    loc, out, exc = run_block(code, {"__file__": os.path.join(other, "pt_v23_audit_2014.py")})
    ok(exc is None, f"T5: khối WORKDIR không được ném: {exc}")
    ok("CANH BAO" in out, f"T5: cây LỆCH mà KHÔNG cảnh báo — đúng lỗi cần vá:\n{out}")
    ok("no-op im lang" in out, f"T5: cảnh báo không nói hệ quả:\n{out}")
    ok(other in out, f"T5: cảnh báo không nêu cây thật của file:\n{out}")
    # cùng cây (canonical) ⇒ không cảnh báo
    os.environ["PT_WORKDIR"] = other
    loc2, out2, exc2 = run_block(code, {"__file__": os.path.join(other, "pt_v23_audit_2014.py")})
    os.environ.clear(); os.environ.update(env)
    ok(exc2 is None, f"T5: không được ném khi cùng cây: {exc2}")
    ok("CANH BAO" not in out2, f"T5: cùng cây mà vẫn cảnh báo (nhiễu):\n{out2}")
    ok(loc2["WORKDIR"] == other, f"T5: PT_WORKDIR không có tác dụng: {loc2['WORKDIR']}")


def pt_lag_block(ref=None):
    s = src_of("pt_v23_audit_2014.py", ref)
    if ref is None:
        return block(s, r'^_forx = \{\}$',
                     r'LAG_FORENSIC_GATE=0 \(cong dang TAT|cong dang TAT, dict khong duoc dung\)"\)',
                     "khối cổng LAG forensic MỚI")
    return block(s, r'^_forx = \{\}$', r'^except Exception: pass$',
                 f"khối cổng LAG forensic CŨ @ {ref}")


def t_pt_lag_failclosed_two_sided():
    """T6 — hai chiều: cổng BẬT + thiếu file ⇒ bản MỚI TỪ CHỐI, bản CŨ `pass` im lặng."""
    d = tempfile.mkdtemp(prefix="ptlag_")
    cwd0 = os.getcwd()
    os.chdir(d)
    try:
        loc, out, exc = run_block(pt_lag_block(), {"_LAG_FOR": True})
        ok(exc is not None, f"T6: cổng BẬT + thiếu file phải TỪ CHỐI:\n{out}")
        ok("TU CHOI CHAY" in exc and "FileNotFoundError" in exc,
           f"T6: thông điệp thiếu từ chối hoặc lỗi thật:\n{exc}")
        # cổng TẮT ⇒ đi tiếp nhưng PHẢI in lỗi thật, không `pass`
        loc2, out2, exc2 = run_block(pt_lag_block(), {"_LAG_FOR": False})
        ok(exc2 is None, f"T6: cổng TẮT không được từ chối: {exc2}")
        ok(loc2["_forx"] == {}, f"T6: cổng TẮT phải trả {{}}: {loc2['_forx']}")
        ok("FileNotFoundError" in out2, f"T6: cổng TẮT vẫn phải IN lỗi thật (§29):\n{out2}")
        # bản CŨ: im lặng ở CẢ HAI trạng thái cổng
        loc_o, out_o, exc_o = run_block(pt_lag_block(OLD_REF), {"_LAG_FOR": True})
        ok(exc_o is None, f"T6: bản CŨ không lẽ từ chối? {exc_o}")
        ok(loc_o["_forx"] == {}, f"T6: bản CŨ phải trả {{}}: {loc_o['_forx']}")
        ok(out_o.strip() == "", f"T6: bản CŨ phải IM LẶNG tuyệt đối, nhưng in:\n{out_o}")
    finally:
        os.chdir(cwd0)
    # file CÓ thật ⇒ cả hai bản cho CÙNG dict (bản vá không đổi hành vi đường thành công)
    loc_n, _, _ = run_block(pt_lag_block(), {"_LAG_FOR": True})
    loc_o2, _, _ = run_block(pt_lag_block(OLD_REF), {"_LAG_FOR": True})
    ok(loc_n["_forx"] == loc_o2["_forx"] and len(loc_n["_forx"]) == 8,
       f"T6: đường thành công phải BẰNG NHAU và 8 mã: {len(loc_n['_forx'])} vs {len(loc_o2['_forx'])}")


TESTS = [t_r8_default_canonical, t_r8_missing_is_fatal_and_old_was_silent,
         t_r8_env_empty_is_explicit_optout, t_r8_env_bad_path_no_silent_fallback,
         t_pt_workdir_warns_on_tree_mismatch, t_pt_lag_failclosed_two_sided]

if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}  "
          f"tree={HERE}  OLD_REF={OLD_REF}")
    fails = 0
    for t in TESTS:
        try:
            t()
            print(f"  PASS {t.__name__}")
        except AssertionError as e:
            fails += 1
            print(f"  FAIL {t.__name__}: {type(e).__name__}: {e}")
    print()
    print(f"{'PASS' if not fails else 'FAIL'}  ({_n} assertion" + (")" if not fails else f", {fails} test FAIL)"))
    sys.exit(1 if fails else 0)
