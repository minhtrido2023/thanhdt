#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check `_account_nav_basis` — fallback NAV không còn IM LẶNG (2026-09-28, user duyệt).

Vì sao không import `golive_recommend_v23`: import nó chạy cả chuỗi khuyến nghị (BQ + DT5G).
Nên lấy NGUYÊN VĂN hàm từ file rồi exec trong namespace cô lập — cùng kỹ thuật
`failopen_failclosed_selfcheck.py`; sửa hàm mà quên sửa test ⇒ test CHẾT, không xanh giả.

2 CHIỀU: bản CŨ (từ `git show <OLD_REF>:`) phải ĐO ĐƯỢC sự im lặng tuyệt đối trên đúng 4 nguyên
nhân (thiếu file / JSON hỏng / quá hạn / nav ≤ 0); bản MỚI phải in cảnh báo mang LÝ DO THẬT.

Chạy:  $DNA_PYEXE navbasis_loud_selfcheck.py
"""
import contextlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
REL = "WorkingClaude/deploy_golive_dt5g_v4/golive_recommend_v23.py"
# CHA của commit vá — không `HEAD`/`main` (sau merge chúng ĐÃ vá ⇒ two-sided FAIL vĩnh viễn).
OLD_REF = os.environ.get("NAVBASIS_OLD_REF", "").strip() or "1f7f1d6f^"
TOP = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=HERE,
                     capture_output=True, text=True, check=True).stdout.strip()

_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src(ref=None):
    if ref is None:
        return open(os.path.join(HERE, "deploy_golive_dt5g_v4", "golive_recommend_v23.py"),
                    encoding="utf-8").read()
    r = subprocess.run(["git", "show", f"{ref}:{REL}"], cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"không đọc được {ref}:{REL} — git: {r.stderr.strip()}")
    return r.stdout


def load_fn(ref, workdir):
    """Trích nguyên văn `_account_nav_basis` + chạy với WORKDIR trỏ vào cây tạm."""
    s = src(ref)
    m = re.search(r"\ndef _account_nav_basis\(label\):\n(.*?)\n(?=def |\Z)", s, re.S)
    assert m, f"không thấy _account_nav_basis trong {ref or 'HEAD'} — dừng, đừng đoán"
    body = "def _account_nav_basis(label):\n" + m.group(1) + "\n"
    g = {"os": os, "json": json, "pd": pd, "WORKDIR": workdir, "ACTIVE_NAV_MAX_AGE_D": 3}
    exec(textwrap.dedent(body), g)
    return g["_account_nav_basis"]


def sandbox(active=None, hist_nav=None, active_raw=None):
    d = tempfile.mkdtemp(prefix="navb_")
    el = os.path.join(d, "data", "execution_logs")
    os.makedirs(el, exist_ok=True)
    if active_raw is not None:
        open(os.path.join(el, "active_nav_T.json"), "w", encoding="utf-8").write(active_raw)
    elif active is not None:
        json.dump(active, open(os.path.join(el, "active_nav_T.json"), "w", encoding="utf-8"))
    if hist_nav is not None:
        pd.DataFrame([{"date": "2026-09-27", "nav": hist_nav}]).to_csv(
            os.path.join(el, "nav_history_T.csv"), index=False)
    return d


def call(ref, **kw):
    d = sandbox(**kw)
    fn = load_fn(ref, d)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        nav, source = fn("T")
    return nav, source, buf.getvalue()


TODAY = pd.Timestamp.now().normalize().strftime("%Y-%m-%d")
OLD_DAY = (pd.Timestamp.now().normalize() - pd.Timedelta(days=30)).strftime("%Y-%m-%d")

# 4 nguyên nhân ⇒ mỗi ca: (tên, kwargs sandbox, chuỗi PHẢI có trong cảnh báo bản mới)
CASES = [
    ("thiếu file active_nav", dict(hist_nav=1e9), "FileNotFoundError"),
    ("active_nav JSON hỏng", dict(active_raw="{ khong-phai-json", hist_nav=1e9),
     "JSONDecodeError"),
    ("active_nav QUÁ HẠN", dict(active={"computed_at": OLD_DAY, "active_nav": 5e8},
                                hist_nav=1e9), "QUÁ HẠN"),
    ("active_nav ≤ 0", dict(active={"computed_at": TODAY, "active_nav": 0.0}, hist_nav=1e9),
     "≤ 0"),
]


def t_fallback_is_loud_and_names_the_cause():
    for name, kw, needle in CASES:
        nav, source, out = call(None, **kw)
        ok(nav == 1e9, f"[{name}] bản MỚI vẫn phải fallback ra 1e9 (không chặn), được {nav}")
        ok("[nav-basis]" in out and "FALLBACK" in out,
           f"[{name}] bản MỚI KHÔNG in cảnh báo:\n{out!r}")
        ok("TỔNG NAV" in out and "LỚN hơn vốn triển khai thật" in out,
           f"[{name}] cảnh báo không nói hệ quả over-size:\n{out!r}")
        ok(needle in out, f"[{name}] cảnh báo không mang lý do THẬT ({needle}):\n{out!r}")
        ok("FALLBACK vì:" in source, f"[{name}] `source` không mang lý do: {source!r}")
        # 2 CHIỀU — bản CŨ: cùng đầu vào, IM LẶNG TUYỆT ĐỐI, source không nói vì sao
        nav_o, source_o, out_o = call(OLD_REF, **kw)
        ok(nav_o == 1e9, f"[{name}] bản CŨ cũng fallback 1e9 (tiền đề A/B), được {nav_o}")
        ok(out_o == "", f"[{name}] bản CŨ phải IM LẶNG, nhưng in:\n{out_o!r}")
        ok("FALLBACK" not in source_o and "vì" not in source_o,
           f"[{name}] bản CŨ không lẽ đã nói lý do? {source_o!r}")


def t_happy_path_unchanged():
    """active_nav tươi + > 0 ⇒ CẢ HAI bản trả y nhau, KHÔNG in gì (không thêm nhiễu)."""
    kw = dict(active={"computed_at": TODAY, "active_nav": 7.5e8}, hist_nav=1e9)
    nav, source, out = call(None, **kw)
    nav_o, source_o, out_o = call(OLD_REF, **kw)
    ok((nav, source) == (nav_o, source_o),
       f"đường thành công phải BẰNG NHAU: {(nav, source)} vs {(nav_o, source_o)}")
    ok(nav == 7.5e8 and source.startswith("active_nav @"), f"sai nhánh: {nav} {source}")
    ok(out == "" and out_o == "", f"không được in gì ở happy path: {out!r} / {out_o!r}")


def t_no_basis_at_all_is_loud():
    """Không có nguồn nào ⇒ (None, lý do) + in 🔴; bản CŨ im lặng và lý do trống rỗng."""
    nav, source, out = call(None)
    ok(nav is None, f"phải trả None, được {nav}")
    ok("🔴" in out and "KHÔNG được chia trần %ADV" in out, f"không in cảnh báo đỏ:\n{out!r}")
    ok("FileNotFoundError" in source, f"`source` không mang lý do thật: {source!r}")
    nav_o, source_o, out_o = call(OLD_REF)
    ok(nav_o is None and out_o == "", f"bản CŨ phải im lặng: {nav_o} {out_o!r}")
    ok(source_o == "không có active_nav/nav_history dùng được",
       f"bản CŨ phải trả lý do TRỐNG RỖNG: {source_o!r}")


TESTS = [t_happy_path_unchanged, t_fallback_is_loud_and_names_the_cause, t_no_basis_at_all_is_loud]

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
            print(f"  FAIL {t.__name__}: {e}")
    print()
    print(f"{'PASS' if not fails else 'FAIL'}  ({_n} assertion"
          + (")" if not fails else f", {fails} test FAIL)"))
    sys.exit(1 if fails else 0)
