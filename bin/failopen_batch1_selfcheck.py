#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check batch-1 fail-open → fail-CLOSED (2026-09-28, user duyệt 08:45 ICT).

Phủ 4 việc, MỖI việc chứng minh 2 CHIỀU — bản CŨ lấy NGUYÊN VĂN từ `git show <OLD_REF>:` và phải
ĐO ĐƯỢC sự im lặng, bản MỚI phải chặn/kêu:
  #2  `lag_days = None` ⇒ gate ADV-stale biến mất  — `compute_jit_unpark.py`, `compute_park_trim.py`
  #3  `check_sbv_weekly.sh` hardcode 4.5 / 2023-06-19 khi import hỏng
  #4  `account_cash_flows.load_flows` thiếu file ⇒ `[]` im lặng trên đường CÔNG BỐ SỐ
  #5  `bot_heartbeat.sh` plan JSON hỏng ⇒ im lặng cả phiên

⚠️ KHÔNG chạy script production thật để "thử cho nhanh": `check_sbv_weekly.sh` GHI
`data/sbv_verify_log.json`, `bot_heartbeat.sh` POST Discord. Cả hai ca ở đây chạy trong CÂY TẠM
(`SBV_CHECK_WORKDIR` / copy sang sandbox) + `HB_NO_NOTIFY=1`. Bài học 2026-09-28 01:48: Mike
smoke-test bản thật và đẩy `last_verified` sớm 3 ngày.

Chạy:  $DNA_PYEXE bin/failopen_batch1_selfcheck.py
"""
import contextlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
MIKE_ROOT = os.path.dirname(HERE)
# Neo bản CŨ vào CHA của commit vá — KHÔNG `HEAD`/`master` (sau merge chúng đã vá ⇒ test 2 chiều
# FAIL vĩnh viễn; lớp lỗi này đã cắn 2 lần trong tuần 2026-09-27/28).
OLD_REF = os.environ.get("FAILOPEN_B1_OLD_REF", "").strip() or "afc1e6b5^"

_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src(rel, ref=None):
    if ref is None:
        return open(os.path.join(MIKE_ROOT, rel), encoding="utf-8").read()
    r = subprocess.run(["git", "show", f"{ref}:{rel}"], cwd=MIKE_ROOT,
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


def run_gate_block(code, sink_name):
    """Chạy khối `if data_date:` với data_date KHÔNG parse được; trả (sink, rc_continue)."""
    import datetime as dt
    # Khối production dùng `continue` ⇒ phải bọc trong VÒNG LẶP 1 lần, nếu không SyntaxError.
    # `continue` = fail-closed đã chặn (thoát vòng) · chạy hết = gate bị bỏ qua.
    body = ("def _b(asof, data_date, LAG_ADV_MAX_STALE_DAYS, tk, sink):\n"
            "    reached = []\n"
            "    for _once in (0,):\n"
            + textwrap.indent(textwrap.dedent(code), "        ")
            + "        reached.append(True)\n"
            "    return 'REACHED_END' if reached else 'CONTINUED'\n")
    g = {"dt": dt}
    exec(body, g)
    if sink_name == "blocked":
        sink = []
        out = g["_b"]("2026-09-28", "khong-phai-ngay", 5, "XYZ", sink)
        return sink, out
    sink = {"blocked": []}
    out = g["_b"]("2026-09-28", "khong-phai-ngay", 5, "XYZ", sink)
    return sink["blocked"], out


# ─────────────── #2 — lag_days fail-closed, 2 call-site ───────────────
def _prep(code, sink_name):
    """Đổi tên biến sink của production thành `sink` để chạy khối rời."""
    if sink_name == "blocked":
        return code.replace("blocked.append", "sink.append")
    return code.replace('out["blocked"].append', 'sink["blocked"].append')


CASES_2 = [
    ("bin/compute_jit_unpark.py", "blocked",
     r"^        if data_date:", r"^                continue$"),
    ("bin/compute_park_trim.py", "out",
     r"^        if data_date:", r"^                continue$"),
]


def t2_lag_days_two_sided():
    for rel, sink_name, sp, ep in CASES_2:
        # khối MỚI: phải CHẶN ngay ở nhánh parse-lỗi (không chạy tới cuối)
        new = cut(src(rel), sp, ep, f"khối gate MỚI {rel}")
        # cắt tới `continue` ĐẦU TIÊN sau except → đó là nhánh fail-closed mới
        sink, out = run_gate_block(_prep(new, sink_name), sink_name)
        ok(len(sink) == 1, f"#2 {rel}: bản MỚI phải CHẶN 1 mã, được {sink}")
        ok(out != "REACHED_END",
           f"#2 {rel}: bản MỚI phải `continue` (không đi tiếp qua gate), out={out}")
        r = sink[0]["reason"]
        ok("khong xac dinh duoc do cu ADV" in r, f"#2 {rel}: lý do không nói rõ: {r}")
        ok("ValueError" in r, f"#2 {rel}: không trích exception THẬT (§29): {r}")
        ok("khong-phai-ngay" in r, f"#2 {rel}: không nêu giá trị đã đọc: {r}")
        # khối CŨ: đi thẳng qua gate, KHÔNG chặn ai — đo được sự im lặng
        old = cut(src(rel, OLD_REF), sp, ep, f"khối gate CŨ {rel} @{OLD_REF}")
        sink_o, out_o = run_gate_block(_prep(old, sink_name), sink_name)
        ok(sink_o == [], f"#2 {rel}: bản CŨ phải KHÔNG chặn gì (fail-open), được {sink_o}")
        ok(out_o == "REACHED_END",
           f"#2 {rel}: bản CŨ phải chạy hết khối = gate bị bỏ qua, out={out_o}")


# ─────────────── #3 — check_sbv_weekly fail-closed ───────────────
def _sbv_sandbox(script_src):
    d = tempfile.mkdtemp(prefix="sbvsc_")
    os.makedirs(os.path.join(d, "mike", "bin"), exist_ok=True)
    os.makedirs(os.path.join(d, "data"), exist_ok=True)
    os.makedirs(os.path.join(d, "logs"), exist_ok=True)
    p = os.path.join(d, "mike", "bin", "check_sbv_weekly.sh")
    open(p, "w", encoding="utf-8").write(script_src)      # sandbox KHÔNG có sbv_macro_overlay.py
    os.chmod(p, 0o755)
    return d, p


def t3_sbv_two_sided():
    for ref, expect_block in ((None, True), (OLD_REF, False)):
        # bản MỚI đã retire sang bin/archive/ 2026-10-09 (vẫn giữ nhánh fail-closed); bản CŨ đọc từ git
        rel = "bin/check_sbv_weekly.sh" if ref else "bin/archive/check_sbv_weekly.sh.retired-20261009"
        d, p = _sbv_sandbox(src(rel, ref))
        env = dict(os.environ, SBV_CHECK_WORKDIR=d)
        r = subprocess.run(["bash", p], capture_output=True, text=True, timeout=180, env=env)
        out = r.stdout + r.stderr
        if expect_block:
            ok(r.returncode == 3, f"#3 bản MỚI phải rc=3, được {r.returncode}\n{out[:400]}")
            ok("TU CHOI CHAY" in out, f"#3 bản MỚI không nói rõ từ chối:\n{out[:400]}")
            ok("ModuleNotFoundError" in out or "ImportError" in out,
               f"#3 bản MỚI không trích lỗi import THẬT (§29):\n{out[:400]}")
            ok("4.5" not in out.split("TU CHOI")[0],
               f"#3 bản MỚI vẫn in giá trị đoán 4.5 trước khi chặn:\n{out[:400]}")
            ok(not os.path.exists(os.path.join(d, "data", "sbv_verify_log.json")),
               "#3 bản MỚI vẫn GHI sbv_verify_log.json dù đã từ chối")
        else:
            ok(r.returncode != 3, f"#3 bản CŨ không lẽ cũng rc=3? {r.returncode}")
            ok("current recorded rate: 4.5%" in out,
               f"#3 bản CŨ phải đi tiếp với hằng số BỊA 4.5:\n{out[:400]}")
            ok("2023-06-19" in out, f"#3 bản CŨ phải dùng ngày BỊA 2023-06-19:\n{out[:400]}")
        shutil.rmtree(d, ignore_errors=True)


# ─────────────── #4 — load_flows thiếu file ───────────────
def _load_mod(rel, ref=None, name="acf"):
    import importlib.util
    d = tempfile.mkdtemp(prefix="acfsc_")
    p = os.path.join(d, os.path.basename(rel))
    open(p, "w", encoding="utf-8").write(src(rel, ref))
    sys.path.insert(0, os.path.join(MIKE_ROOT, "bin"))
    spec = importlib.util.spec_from_file_location(name, p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def t4_cash_flows_two_sided():
    missing = os.path.join(tempfile.mkdtemp(prefix="acfsc_"), "khong_co.json")
    new = _load_mod("bin/account_cash_flows.py", None, "acf_new")
    # (a) đường CÔNG BỐ SỐ: thiếu file ⇒ TỪ CHỐI
    try:
        new.load_flows("SpaceX", flows_path=missing, require_file=True)
        ok(False, "#4 require_file=True phải raise khi thiếu file")
    except new.CashFlowError as e:
        ok("KHÔNG có sổ dòng tiền" in str(e), f"#4 thông điệp không rõ: {e}")
        ok("NẠP" in str(e) and "LÃI" in str(e), f"#4 không nói hệ quả nạp→lãi: {e}")
    # (b) đường không công bố: vẫn `[]` NHƯNG phải IN cảnh báo (không im lặng)
    buf = io.StringIO()
    with contextlib.redirect_stderr(buf):
        got = new.load_flows("SpaceX", flows_path=missing)
    ok(got == [], f"#4 mặc định phải trả [], được {got}")
    ok("CẢNH BÁO" in buf.getvalue(), f"#4 mặc định vẫn IM LẶNG:\n{buf.getvalue()}")
    # (c) file CÓ nhưng account chưa có dòng tiền ⇒ [] HỢP LỆ, KHÔNG cảnh báo, KHÔNG raise
    d = tempfile.mkdtemp(prefix="acfsc_")
    fp = os.path.join(d, "flows.json")
    json.dump({"SpaceX": []}, open(fp, "w", encoding="utf-8"))
    buf2 = io.StringIO()
    with contextlib.redirect_stderr(buf2):
        got2 = new.load_flows("SpaceX", flows_path=fp, require_file=True)
    ok(got2 == [], f"#4 file có + account rỗng phải trả [], được {got2}")
    ok(buf2.getvalue() == "", f"#4 không được cảnh báo khi ĐÃ ĐỌC và xác nhận rỗng:\n{buf2.getvalue()}")
    # (d) 2 CHIỀU: bản CŨ im lặng tuyệt đối và KHÔNG có tham số require_file
    old = _load_mod("bin/account_cash_flows.py", OLD_REF, "acf_old")
    buf3 = io.StringIO()
    with contextlib.redirect_stderr(buf3):
        got3 = old.load_flows("SpaceX", flows_path=missing)
    ok(got3 == [] and buf3.getvalue() == "",
       f"#4 bản CŨ phải im lặng tuyệt đối, được {got3!r} + {buf3.getvalue()!r}")
    import inspect
    ok("require_file" not in inspect.signature(old.load_flows).parameters,
       "#4 bản CŨ không lẽ đã có require_file?")
    # (e) consumer đường công bố ĐÃ wire require_file=True
    npr = src("bin/nav_period_returns.py")
    ok(re.search(r"load_flows\(account,\s*require_file=True\)", npr),
       "#4 nav_period_returns.py CHƯA truyền require_file=True")


# ─────────────── #5 — bot_heartbeat plan hỏng ───────────────
def t5_heartbeat_two_sided():
    for ref, expect_block in ((None, True), (OLD_REF, False)):
        d = tempfile.mkdtemp(prefix="hbsc_")
        os.makedirs(os.path.join(d, "mike", "bin"), exist_ok=True)
        os.makedirs(os.path.join(d, "data", "trade_plans"), exist_ok=True)
        os.makedirs(os.path.join(d, "data", "execution_logs"), exist_ok=True)
        p = os.path.join(d, "mike", "bin", "bot_heartbeat.sh")
        open(p, "w", encoding="utf-8").write(src("bin/bot_heartbeat.sh", ref))
        os.chmod(p, 0o755)
        plan = os.path.join(d, "data", "trade_plans", "plan_TEST_2026-09-28.json")
        open(plan, "w", encoding="utf-8").write('{"orders": [ {"ticker": "AAA"  <<< HONG')
        env = dict(os.environ, HB_NO_NOTIFY="1")
        r = subprocess.run(["bash", p, "TEST", "2026-09-28"], capture_output=True, text=True,
                           timeout=120, env=env)
        out = r.stdout + r.stderr
        if expect_block:
            ok(r.returncode == 4, f"#5 bản MỚI phải rc=4, được {r.returncode}\n{out[:400]}")
            ok("KHONG doc duoc" in out, f"#5 bản MỚI không nói rõ:\n{out[:400]}")
            ok("JSONDecodeError" in out or "Expecting" in out,
               f"#5 bản MỚI không trích lỗi parse THẬT (§29):\n{out[:400]}")
        else:
            ok(r.returncode == 0, f"#5 bản CŨ phải exit 0 im lặng, được {r.returncode}")
            ok(out.strip() == "", f"#5 bản CŨ phải IM LẶNG tuyệt đối, nhưng in:\n{out[:400]}")
        # plan HỢP LỆ 0 lệnh ⇒ CẢ HAI bản im lặng exit 0 (không chặn oan)
        open(plan, "w", encoding="utf-8").write('{"orders": []}')
        r0 = subprocess.run(["bash", p, "TEST", "2026-09-28"], capture_output=True, text=True,
                            timeout=120, env=env)
        ok(r0.returncode == 0 and (r0.stdout + r0.stderr).strip() == "",
           f"#5 plan 0 lệnh phải im lặng exit 0 (ref={ref}): rc={r0.returncode} "
           f"out={(r0.stdout + r0.stderr)[:200]}")
        shutil.rmtree(d, ignore_errors=True)


TESTS = [t2_lag_days_two_sided, t3_sbv_two_sided, t4_cash_flows_two_sided, t5_heartbeat_two_sided]

if __name__ == "__main__":
    print(f"TZ={os.environ.get('TZ', '(unset)')}  python={sys.version.split()[0]}  "
          f"tree={MIKE_ROOT}  OLD_REF={OLD_REF}")
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
