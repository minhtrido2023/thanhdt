#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check đợt-2 batch (2026-09-28, user duyệt 12:38 ICT) — 4 site, 2 CHIỀU từng cái.

  #1a `pt_8l_daily.sh`        checker DT5G crash ⇒ TRƯỚC: in "DT5G tươi… đã xác nhận" (SAI chủ động)
  #3  `telegram_run_daily.sh` checker độ tươi lỗi ⇒ TRƯỚC: mất dòng ⚠️ ở đầu tin Telegram
  #2a `golive_recommend_v23.py:667`  thiếu khoá `state` ⇒ TRƯỚC: đoán 3 = NEUTRAL
  #2b `golive_recommend_v23.py:731`  thiếu 8L rating ⇒ TRƯỚC: `fillna(0)` ⇒ "không yếu" ⇒ POS_PCT

⚠️ KHÔNG chạy 2 script shell thật (chúng gửi Telegram/Discord + ghi state) — chỉ chạy KHỐI đã
trích nguyên văn, trong sandbox. Bài học 2026-09-28: Mike đã 2 lần gọi thẳng entrypoint cron để
"thử cho nhanh" và gây side-effect thật (`sbv_verify_log.json`; ops_health_check post Discord).

Chạy:  $DNA_PYEXE dot2_batch_selfcheck.py
"""
import os
import re
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
OLD_REF = os.environ.get("DOT2_OLD_REF", "").strip() or "8d1146c0"
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


def cut(text, start_pat, end_pat, what):
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if re.search(start_pat, l)), None)
    assert i is not None, f"không thấy ĐẦU {what}: /{start_pat}/ — dừng, đừng đoán"
    j = next((k for k in range(i, len(lines)) if re.search(end_pat, lines[k])), None)
    assert j is not None, f"không thấy CUỐI {what}: /{end_pat}/ — dừng, đừng đoán"
    return "".join(lines[i:j + 1])


def cut_dt5g(text, what):
    """Khối DT5G của `pt_8l_daily.sh`: từ dòng gán đầu tiên tới `fi` ĐÓNG nhánh warn/else.

    KHÔNG dùng `fi` đầu tiên: bản mới có thêm một `if` lồng (tri-state) nên `fi` đầu tiên đóng
    khối đó, cắt ở đó sẽ bỏ mất chính nhánh cần đo (selfcheck bắt được lúc viết).
    """
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines)
              if l.startswith("DT5G_WARN=") or l.startswith("_dt5g_err=")), None)
    assert i is not None, f"không thấy ĐẦU {what} — dừng, đừng đoán"
    t = next((k for k in range(i, len(lines)) if "DT5G tươi" in lines[k]), None)
    assert t is not None, f"không thấy nhánh 'DT5G tươi' trong {what}"
    j = next((k for k in range(t, len(lines)) if lines[k].rstrip() == "fi"), None)
    assert j is not None, f"không thấy `fi` đóng nhánh warn/else của {what}"
    return "".join(lines[i:j + 1])


def sh(code, env_extra=None, stub=None):
    """Chạy khối bash trong sandbox; `stub` = nội dung script con được gọi (đặt tên theo nhu cầu)."""
    d = tempfile.mkdtemp(prefix="dot2_")
    env = dict(os.environ)
    env.update(env_extra or {})
    for name, body in (stub or {}).items():
        p = os.path.join(d, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        open(p, "w", encoding="utf-8").write(body)
        os.chmod(p, 0o755)
    r = subprocess.run(["bash", "-c", code], capture_output=True, text=True, env=env, cwd=d,
                       timeout=120)
    return r.stdout + r.stderr, d


# ───────────────── #1a pt_8l_daily.sh ─────────────────
def t1a_dt5g_tri_state():
    for ref, expect_false_ok in ((None, False), (OLD_REF, True)):
        body = cut_dt5g(src("pt_8l_daily.sh", ref), f"khối DT5G pt_8l_daily @{ref}")
        # PY = script giả LUÔN LỖI (mô phỏng checker crash); notify ⇒ echo để đo, không gửi thật
        stub = {"fakepy": '#!/bin/sh\necho "boom: dt5g_freshness khong doc duoc artifact" >&2\nexit 1\n',
                "notify": '#!/bin/sh\necho "NOTIFY_CALLED: $1"\n'}
        code = (f'PY="./fakepy"\nNOTIFY_BIN="./notify"\nNOTIFY_THREAD_BIN="./notify"\n'
                + body)
        out, _ = sh(code, stub=stub)
        if expect_false_ok:   # bản CŨ
            ok("DT5G tươi" in out,
               f"#1a bản CŨ phải in KHẲNG ĐỊNH SAI 'DT5G tươi' khi checker crash:\n{out!r}")
            ok("NOTIFY_CALLED" not in out, f"#1a bản CŨ không lẽ đã notify? {out!r}")
        else:                  # bản MỚI
            ok("DT5G tươi" not in out,
               f"#1a bản MỚI KHÔNG được in 'DT5G tươi' khi checker crash:\n{out!r}")
            ok("DT5G STALE" in out, f"#1a bản MỚI phải vào nhánh cảnh báo:\n{out!r}")
            ok("KHONG kiem duoc do tuoi" in out, f"#1a thiếu câu 'không kiểm được':\n{out!r}")
            ok("boom:" in out, f"#1a không trích LỖI THẬT của checker (§29):\n{out!r}")
            ok("NOTIFY_CALLED" in out, f"#1a phải gọi notify để cảnh báo tới người:\n{out!r}")
    # checker CHẠY ĐƯỢC và báo stale ⇒ hai bản phải GIỐNG nhau
    stub = {"fakepy": '#!/bin/sh\necho "state 2026-09-25 cũ 3 phiên"\n',
            "notify": '#!/bin/sh\necho "NOTIFY_CALLED: $1"\n'}
    outs = []
    for ref in (None, OLD_REF):
        body = cut_dt5g(src("pt_8l_daily.sh", ref), "khối DT5G")
        o, _ = sh(f'PY="./fakepy"\nNOTIFY_BIN="./notify"\nNOTIFY_THREAD_BIN="./notify"\n' + body,
                  stub=stub)
        outs.append(o)
    ok("DT5G STALE" in outs[0] and "DT5G STALE" in outs[1],
       f"#1a ca stale THẬT: cả hai bản phải cảnh báo:\n{outs}")
    ok("cũ 3 phiên" in outs[0], f"#1a bản MỚI phải giữ nguyên nội dung checker:\n{outs[0]!r}")


# ───────────────── #3 telegram_run_daily.sh ─────────────────
def t3_telegram_header():
    for ref in (None, OLD_REF):
        body = cut(src("telegram_run_daily.sh", ref), r"EXTRA_WARN_HEADER=|^if ! _fresh_out=",
                   r"^\[ -n \"\$EXTRA_WARN_HEADER\" \]", f"khối header @{ref}")
        stub = {"mike/bin/csv_fresh_today.sh":
                '#!/bin/sh\necho "boom: csv_fresh_today khong doc duoc file" >&2\nexit 2\n'}
        code = ('WORKDIR_8L="."\nLOG=/dev/stdout\n' + body
                + '\necho "HEADER=[$EXTRA_WARN_HEADER]"\n')
        out, _ = sh(code, stub=stub)
        if ref is None:
            ok("HEADER=[]" not in out, f"#3 bản MỚI header KHÔNG được rỗng:\n{out!r}")
            ok("KHÔNG kiểm được độ tươi input 8L" in out, f"#3 thiếu câu nói thật:\n{out!r}")
            ok("boom:" in out, f"#3 không trích lỗi THẬT (§29):\n{out!r}")
        else:
            ok("HEADER=[]" in out, f"#3 bản CŨ phải cho header RỖNG (mất cảnh báo):\n{out!r}")


# ───────────────── #2 golive_recommend_v23.py ─────────────────
def _state_block(ref):
    return cut(src("deploy_golive_dt5g_v4/golive_recommend_v23.py", ref),
               r"^state_today = int\(sig\.loc|^if \(sig\[\"time\"\] == LATEST\)\.any\(\):",
               r"^print\(f\"  latest signal date", f"khối state @{ref}")


def t2a_state_no_guess():
    import pandas as pd

    def run(ref, prov):
        code = _state_block(ref)
        code = "\n".join(l for l in code.splitlines() if not l.startswith("print(f\"  latest"))
        g = {"pd": pd, "int": int, "sorted": sorted, "print": lambda *a, **k: None,
             "sig": pd.DataFrame({"time": pd.to_datetime(["2026-09-20"]), "state5": [1]}),
             "LATEST": pd.Timestamp("2026-09-25"), "prov": prov, "SystemExit": SystemExit}
        try:
            exec(textwrap.dedent(code), g)
            return g.get("state_today"), None
        except SystemExit as e:
            return None, str(e)

    # provenance THIẾU `state` (LATEST không có dòng nào)
    st, err = run(None, {"asof": "2026-09-25"})
    ok(st is None and err, f"#2a bản MỚI phải TỪ CHỐI khi thiếu khoá state, được {st}")
    ok("TU CHOI CHAY" in err and "`state`" in err, f"#2a thông điệp không rõ:\n{err}")
    ok("NEUTRAL" in err, f"#2a không nói vì sao đoán NEUTRAL là sai hướng:\n{err}")
    st_o, err_o = run(OLD_REF, {"asof": "2026-09-25"})
    ok(err_o is None and st_o == 3,
       f"#2a bản CŨ phải ĐOÁN 3=NEUTRAL (đúng như cáo buộc), được {st_o}/{err_o}")
    # provenance CÓ `state` ⇒ hai bản y nhau
    st2, e2 = run(None, {"state": 2})
    st2o, e2o = run(OLD_REF, {"state": 2})
    ok((st2, e2) == (st2o, e2o) == (2, None), f"#2a có state: {st2}/{e2} vs {st2o}/{e2o}")


def t2b_missing_rating_is_weak():
    import numpy as np
    import pandas as pd
    for ref, expect_weak in ((None, True), (OLD_REF, False)):
        line = cut(src("deploy_golive_dt5g_v4/golive_recommend_v23.py", ref),
                   r'today\["weak"\] = today\["rating8l"\]\.fillna',
                   r'today\["weak"\] = today\["rating8l"\]\.fillna', f"dòng weak @{ref}")
        today = pd.DataFrame({"rating8l": [np.nan, 2.0, 5.0]})
        g = {"today": today, "np": np, "pd": pd}
        exec(textwrap.dedent(line), g)
        w = list(g["today"]["weak"])
        ok(w[0] == expect_weak,
           f"#2b (ref={ref}) mã THIẾU rating: weak phải là {expect_weak}, được {w[0]}")
        ok(w[1] is False or not w[1], f"#2b rating 2 phải KHÔNG yếu (ref={ref}): {w[1]}")
        ok(bool(w[2]), f"#2b rating 5 phải YẾU (ref={ref}): {w[2]}")


TESTS = [t1a_dt5g_tri_state, t3_telegram_header, t2a_state_no_guess, t2b_missing_rating_is_weak]

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
