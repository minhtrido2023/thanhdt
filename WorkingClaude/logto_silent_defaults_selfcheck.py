#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check: 2 mặc định IM LẶNG của §4b nay PHẢI nói ra (2026-09-28, user duyệt).

`sector_lens_monitor.load_ratings()` và `capit_episode._load()` vẫn trả giá trị rỗng (đây là lens
paper, chặn hết sẽ mất cả báo cáo) — nhưng không còn im lặng, và **phân biệt được** "chưa có file"
với "có mà không đọc được". 2 CHIỀU bằng bản cũ lấy nguyên văn từ git.

Chạy:  $DNA_PYEXE logto_silent_defaults_selfcheck.py
"""
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_REF = os.environ.get("LOGTO_OLD_REF", "").strip() or "fa8da6a5"
_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src(rel, ref=None):
    if ref is None:
        return open(os.path.join(HERE, rel), encoding="utf-8").read()
    r = subprocess.run(["git", "show", f"{ref}:WorkingClaude/{rel}"], cwd=HERE,
                       capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"không đọc được {ref}:{rel} — git: {r.stderr.strip()}")
    return r.stdout


def fn_src(text, name, what):
    """Cắt trọn 1 hàm top-level: từ dòng `def NAME(` tới trước `def`/`class` top-level kế tiếp."""
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if l.startswith(f"def {name}(")), None)
    assert i is not None, f"không thấy `def {name}(` ở top-level trong {what} — dừng, đừng đoán"
    j = next((k for k in range(i + 1, len(lines))
              if lines[k].startswith("def ") or lines[k].startswith("class ")), len(lines))
    return "".join(lines[i:j])


def run_load_ratings(ref, path):
    import pandas as pd
    import numpy as np
    full = src("sector_lens_monitor.py", ref)
    # `load_ratings` dùng helper `_f` của chính module + numpy ⇒ nạp CẢ HAI từ nguồn thật, không
    # tự viết lại (viết lại là tạo một phiên bản thứ hai của hàm đang kiểm).
    code = fn_src(full, "_f", f"sector_lens @{ref}") + "\n" \
        + fn_src(full, "load_ratings", f"sector_lens @{ref}")
    g = {"os": os, "pd": pd, "np": np, "RATING_CSV": path}
    exec(textwrap.dedent(code), g)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = g["load_ratings"]()
    return out, buf.getvalue()


def run_capit_load(ref, path):
    import json
    code = fn_src(src("capit_episode.py", ref), "_load", f"capit_episode @{ref}")
    g = {"os": os, "json": json}
    exec(textwrap.dedent(code), g)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out = g["_load"](path)
    return out, buf.getvalue()


def t_load_ratings_two_sided():
    d = tempfile.mkdtemp(prefix="lg_")
    missing = os.path.join(d, "khong_co.csv")
    bad = os.path.join(d, "hong.csv")
    open(bad, "w", encoding="utf-8").write("day khong phai csv co cot ticker,rating\n<<<")
    for path, needle in ((missing, "KHONG co"), (bad, "TON TAI ma KHONG doc duoc")):
        out, log = run_load_ratings(None, path)
        ok(out == {}, f"bản MỚI vẫn phải trả {{}}, được {out}")
        ok("[ratings]" in log and needle in log, f"bản MỚI không nói rõ ca này:\n{log!r}")
        ok("load_double_confirm" in log, f"không nói hệ quả tầng lọc rating biến mất:\n{log!r}")
        out_o, log_o = run_load_ratings(OLD_REF, path)
        ok(out_o == {}, f"bản CŨ cũng trả {{}} (tiền đề A/B), được {out_o}")
        ok(log_o == "", f"bản CŨ phải IM LẶNG, nhưng in:\n{log_o!r}")
    # file HỢP LỆ ⇒ hai bản y nhau, KHÔNG in gì
    good = os.path.join(d, "ok.csv")
    open(good, "w", encoding="utf-8").write("ticker,rating\nAAA,2\nBBB,4\n")
    o1, l1 = run_load_ratings(None, good)
    o2, l2 = run_load_ratings(OLD_REF, good)
    ok(o1 == o2 and o1 == {"AAA": 2, "BBB": 4}, f"happy path lệch: {o1} vs {o2}")
    ok(l1 == "" and l2 == "", f"happy path không được in gì: {l1!r} / {l2!r}")


def t_capit_episode_two_sided():
    d = tempfile.mkdtemp(prefix="ce_")
    missing = os.path.join(d, "khong_co.json")
    out, log = run_capit_load(None, missing)
    ok(out == {"episodes": []}, f"bản MỚI vẫn phải trả sổ rỗng, được {out}")
    ok("[capit-episode]" in log, f"bản MỚI phải in dấu vết:\n{log!r}")
    ok("vo hinh" in log, f"không nói hệ quả episode đang mở thành vô hình:\n{log!r}")
    out_o, log_o = run_capit_load(OLD_REF, missing)
    ok(out_o == {"episodes": []} and log_o == "",
       f"bản CŨ phải im lặng: {out_o} / {log_o!r}")
    # sổ CÓ thật ⇒ hai bản y nhau, không in gì
    import json
    p = os.path.join(d, "co.json")
    json.dump({"episodes": [{"id": "E1"}]}, open(p, "w", encoding="utf-8"))
    o1, l1 = run_capit_load(None, p)
    o2, l2 = run_capit_load(OLD_REF, p)
    ok(o1 == o2 == {"episodes": [{"id": "E1"}]}, f"happy path lệch: {o1} vs {o2}")
    ok(l1 == "" and l2 == "", f"happy path không được in gì: {l1!r} / {l2!r}")


TESTS = [t_load_ratings_two_sided, t_capit_episode_two_sided]

if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}  OLD_REF={OLD_REF}")
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
