#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Self-check 3 call-site fail-open trong `trading_bot/plan.py` (2026-09-28, user duyệt 09:59 ICT).

⚠️ ĐÂY LÀ ĐƯỜNG ĐẶT LỆNH. Selfcheck này KHÔNG đặt lệnh, KHÔNG chạm broker, KHÔNG ghi vào
`data/execution_logs` thật — mọi ca chạy trong cây tạm.

2 CHIỀU cho từng site (bản CŨ lấy NGUYÊN VĂN từ `git show <OLD_REF>:` và phải ĐO ĐƯỢC sự im lặng):
  :648   `lag_days = None` ⇒ gate ADV-stale không bao giờ chạy
  :1651  `except: pass` ⇒ mất dòng cảnh báo "plan sizing theo đòn bẩy mà thực thi không có đòn bẩy"
  :1756  `_lever_ledger_merge` ⇒ sổ "ai ĐÃ được cấp phép vay" bị GHI ĐÈ, xoá bằng chứng

Chạy:  $DNA_PYEXE planpy_failopen_selfcheck.py
"""
import contextlib
import importlib.util
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
REL = "WorkingClaude/trading_bot/plan.py"
OLD_REF = os.environ.get("PLANPY_OLD_REF", "").strip() or "92b746d0"

_n = 0


def ok(cond, msg):
    global _n
    _n += 1
    if not cond:
        raise AssertionError(msg)


def src(ref=None):
    if ref is None:
        return open(os.path.join(HERE, "trading_bot", "plan.py"), encoding="utf-8").read()
    r = subprocess.run(["git", "show", f"{ref}:{REL}"], cwd=HERE, capture_output=True, text=True)
    if r.returncode != 0:
        raise AssertionError(f"không đọc được {ref}:{REL} — git: {r.stderr.strip()}")
    return r.stdout


def cut(text, start_pat, end_pat, what):
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if re.search(start_pat, l)), None)
    assert i is not None, f"không thấy ĐẦU {what}: /{start_pat}/ — dừng, đừng đoán"
    j = next((k for k in range(i, len(lines)) if re.search(end_pat, lines[k])), None)
    assert j is not None, f"không thấy CUỐI {what}: /{end_pat}/ — dừng, đừng đoán"
    return "".join(lines[i:j + 1])


# ───────────────── :648 — gate ADV-stale ─────────────────
def run_gate(code):
    """`continue` cần vòng lặp; chạy hết khối = gate bị bỏ qua."""
    import datetime as dt
    body = ("def _b(asof, data_date, LAG_ADV_MAX_STALE_DAYS, _block):\n"
            "    reached = []\n"
            "    for _once in (0,):\n"
            + textwrap.indent(textwrap.dedent(code), "        ")
            + "        reached.append(True)\n"
            "    return 'REACHED_END' if reached else 'BLOCKED_AND_CONTINUED'\n")
    g = {"dt": dt}
    exec(body, g)
    blocked = []
    out = g["_b"]("2026-09-28", "khong-phai-ngay", 5, blocked.append)
    return blocked, out


def t648_two_sided():
    pat = (r"^        if data_date:", r"^                continue$")
    new = cut(src(), *pat, "khối gate :648 MỚI")
    blocked, out = run_gate(new)
    ok(out == "BLOCKED_AND_CONTINUED", f":648 bản MỚI phải CHẶN rồi continue, out={out}")
    ok(len(blocked) == 1, f":648 phải _block đúng 1 lần, được {blocked}")
    r = blocked[0]
    ok("KHONG xac dinh duoc do cu ADV" in r, f":648 lý do không rõ: {r}")
    ok("ValueError" in r, f":648 không trích exception THẬT (§29): {r}")
    ok("khong-phai-ngay" in r, f":648 không nêu giá trị đã đọc: {r}")
    old = cut(src(OLD_REF), *pat, f"khối gate :648 CŨ @{OLD_REF}")
    blocked_o, out_o = run_gate(old)
    ok(blocked_o == [], f":648 bản CŨ phải KHÔNG chặn gì, được {blocked_o}")
    ok(out_o == "REACHED_END", f":648 bản CŨ phải chạy hết khối = gate bị bỏ qua, out={out_o}")


# ───────────────── :1651 — dòng cảnh báo lever ─────────────────
def run_lever_warn(code):
    """Chạy khối `try:` … handler với `st` là artifact ÉM LỖI ở `.get()`.

    Tên biến khối này cần (đọc từ chính production, plan.py:1637-1646): `st` (artifact đã đọc),
    `path`, `json`, `adj`, `plan`, `err`, `_is_capit_buy`, `account_label`. Ca mô phỏng = artifact
    ĐÃ có nhưng hỏng khi truy cập ⇒ đúng nhánh "không kiểm chéo được".
    """
    class Boom(dict):
        def __bool__(self):
            return True

        def get(self, *a, **k):
            raise RuntimeError("artifact hong: khong doc duoc capit_slot_targets")

    body = ("def _b(st, path, adj, plan, err, _is_capit_buy, account_label, json):\n"
            + textwrap.indent(textwrap.dedent(code), "    ") + "\n    return adj\n")
    g = {}
    exec(body, g)
    adj = []

    class _P:
        orders = [type("O", (), {"ticker": "AAA"})()]
    g["_b"](Boom(), "/khong/ton/tai.json", adj, _P(), "enabled=false", lambda o: True,
            "TEST", json)
    return adj


def cut_try_block(text, needle, what):
    """Cắt TRỌN khối `try:` … hết handler `except`, neo bằng một dòng BÊN TRONG thân try.

    Không cắt thân và handler riêng (bản trước làm vậy và lệch thụt lề): đi LÙI từ `needle` tới
    dòng `try:` gần nhất, rồi đi XUÔI tới dòng cuối cùng còn thuộc handler.
    """
    lines = text.splitlines(keepends=True)
    i = next((k for k, l in enumerate(lines) if needle in l), None)
    assert i is not None, f"không thấy neo {needle!r} trong {what} — dừng, đừng đoán"
    t = next((k for k in range(i, -1, -1) if lines[k].strip() == "try:"), None)
    assert t is not None, f"không thấy `try:` phía trên neo của {what}"
    base = len(lines[t]) - len(lines[t].lstrip())
    exc = next((k for k in range(i, len(lines))
                if lines[k].strip().startswith("except")
                and len(lines[k]) - len(lines[k].lstrip()) == base), None)
    assert exc is not None, f"không thấy `except` cùng mức với `try:` của {what}"
    end = exc + 1
    while end < len(lines):
        ln = lines[end]
        if ln.strip() and (len(ln) - len(ln.lstrip())) <= base:
            break
        end += 1
    return textwrap.dedent("".join(lines[t:end]))


def t1651_two_sided():
    NEEDLE = 'capit_slot_target_vnd_levered")'
    new = cut_try_block(src(), NEEDLE, "khối cảnh báo :1651 MỚI")
    adj = run_lever_warn(new)
    ok(len(adj) == 1, f":1651 bản MỚI phải để lại ĐÚNG 1 dòng, được {adj}")
    a = adj[0]
    ok(a["action"] == "LEVER_CROSSCHECK_UNAVAILABLE", f":1651 action sai: {a['action']}")
    ok("RuntimeError" in a["reason"], f":1651 không trích lỗi THẬT (§29): {a['reason']}")
    ok("artifact hong" in a["reason"], f":1651 không mang thông điệp lỗi gốc: {a['reason']}")
    ok("WAIT_CASH" in a["reason"], f":1651 không nói hệ quả vận hành: {a['reason']}")
    # 2 CHIỀU — bản CŨ `except: pass` ⇒ adj RỖNG, không ai biết đã mất kiểm chéo
    old = cut_try_block(src(OLD_REF), NEEDLE, f"khối :1651 CŨ @{OLD_REF}")
    ok(old.rstrip().splitlines()[-1].strip() == "pass",
       f":1651 khối CŨ cắt sai (dòng cuối phải là `pass`): {old.rstrip().splitlines()[-1]!r}")
    adj_o = run_lever_warn(old)
    ok(adj_o == [], f":1651 bản CŨ phải KHÔNG để lại dòng nào (im lặng), được {adj_o}")


# ───────────────── :1756 — sổ lever ─────────────────
def load_plan(ref, exec_dir):
    """Nạp `plan.py` (bản `ref`) bằng cách COPY cả package `trading_bot` thật rồi GHI ĐÈ `plan.py`.

    Không dựng package giả: `plan.py` import hàng loạt module em (`no_chase_ceiling`, …) và
    `config` thật, nên stub sẽ luôn thiếu một cái gì đó. Copy cây thật = môi trường import GIỐNG
    production, chỉ đúng 1 file bị thay ⇒ A/B sạch.
    """
    d = tempfile.mkdtemp(prefix="planpy_")
    shutil.copytree(os.path.join(HERE, "trading_bot"), os.path.join(d, "trading_bot"),
                    ignore=shutil.ignore_patterns("__pycache__"))
    open(os.path.join(d, "trading_bot", "plan.py"), "w", encoding="utf-8").write(src(ref))
    sys.path.insert(0, d)
    for m in [k for k in list(sys.modules) if k == "trading_bot" or k.startswith("trading_bot.")]:
        del sys.modules[m]
    try:
        import importlib
        mod = importlib.import_module("trading_bot.plan")
    except Exception as e:
        raise AssertionError(f"không nạp được plan.py @{ref or 'HEAD'}: {type(e).__name__}: {e}")
    finally:
        sys.path.remove(d)
    return mod


def _ledger_case(ref, content):
    exec_dir = tempfile.mkdtemp(prefix="planex_")
    mod = load_plan(ref, exec_dir)
    path = mod._lever_ledger_path("TEST", "2026-09-28", exec_dir)
    if content is not None:
        open(path, "w", encoding="utf-8").write(content)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        out, prior = mod._lever_ledger_merge("TEST", "2026-09-28", {"1840": {"BBB"}}, exec_dir)
    return out, prior, buf.getvalue(), path, exec_dir


def t1756_two_sided():
    GOOD = json.dumps({"granted": {"1840": ["AAA"]}})
    CORRUPT = '{"granted": {"1840": ["AAA"  <<< HONG'
    # (a) file HỢP LỆ ⇒ cả hai bản merge y nhau (không đổi hành vi happy path)
    for ref in (None, OLD_REF):
        out, prior, log, _, _ = _ledger_case(ref, GOOD)
        ok(out == {"1840": {"AAA", "BBB"}}, f":1756 happy path sai (ref={ref}): {out}")
        ok(prior == {"1840": {"AAA"}}, f":1756 prior sai (ref={ref}): {prior}")
        ok(log == "", f":1756 happy path không được in gì (ref={ref}):\n{log!r}")
    # (b) file KHÔNG tồn tại ⇒ im lặng, prior rỗng, cả hai bản y nhau
    for ref in (None, OLD_REF):
        out, prior, log, _, _ = _ledger_case(ref, None)
        ok(prior == {} and out == {"1840": {"BBB"}}, f":1756 thiếu file sai (ref={ref}): {out}")
        ok(log == "", f":1756 thiếu file KHÔNG được in gì (ref={ref}):\n{log!r}")
    # (c) file TỒN TẠI mà HỎNG — điểm khác biệt thật
    out, prior, log, path, _ = _ledger_case(None, CORRUPT)
    ok("[lever-ledger]" in log, f":1756 bản MỚI phải KÊU khi sổ hỏng:\n{log!r}")
    ok("JSONDecodeError" in log or "Expecting" in log,
       f":1756 bản MỚI không trích lỗi parse THẬT (§29):\n{log!r}")
    ok("LEVER_PACKAGE_UNAUTHORIZED" in log, f":1756 không nói hệ quả audit:\n{log!r}")
    d = os.path.dirname(path)
    kept = [f for f in os.listdir(d) if ".corrupt_" in f]
    ok(len(kept) == 1, f":1756 bản MỚI phải GIỮ bản gốc hỏng lại, thấy: {os.listdir(d)}")
    ok(CORRUPT in open(os.path.join(d, kept[0]), encoding="utf-8").read(),
       ":1756 bản giữ lại KHÔNG phải nội dung hỏng gốc")
    out_o, prior_o, log_o, path_o, _ = _ledger_case(OLD_REF, CORRUPT)
    ok(log_o == "", f":1756 bản CŨ phải IM LẶNG khi sổ hỏng, nhưng in:\n{log_o!r}")
    d_o = os.path.dirname(path_o)
    ok([f for f in os.listdir(d_o) if ".corrupt_" in f] == [],
       ":1756 bản CŨ không lẽ đã giữ bản gốc?")
    ok(json.load(open(path_o, encoding="utf-8"))["granted"] == {"1840": ["BBB"]},
       ":1756 bản CŨ phải GHI ĐÈ sổ, mất AAA — đây là bằng chứng bị xoá")
    _all_o = {t for v in out_o.values() for t in v}      # out_o chứa set ⇒ không json.dumps được
    ok("AAA" not in _all_o, f":1756 bản CŨ phải MẤT grant AAA (đúng như cáo buộc): {out_o}")


TESTS = [t648_two_sided, t1651_two_sided, t1756_two_sided]

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
