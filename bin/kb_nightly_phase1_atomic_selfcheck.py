#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Selfcheck: kb_nightly.sh Phase 1 (archive event cũ khỏi kb/events_buffer.md).

Chạy:  python3 mike/bin/kb_nightly_phase1_atomic_selfcheck.py
       cd /tmp && env -i PATH=/usr/bin:/bin python3 <repo>/mike/bin/kb_nightly_phase1_atomic_selfcheck.py

Hai bug gốc (code-quality 2026-09-13, vá ở c9edd4c6 mục e):
  1. Dòng tiếp nối (payload nhiều dòng) đi theo "đã có event mới nào chưa" chứ không theo event
     NGAY TRÊN nó ⇒ buffer xen kẽ cũ/mới thì phần đuôi event cũ bị giữ lại, mồ côi.
  2. events_buffer.md ghi đè tại chỗ (write_text) ⇒ bị kill giữa lúc ghi = mất buffer.

Test HÀNH VI: trích NGUYÊN đoạn python Phase 1 từ kb_nightly.sh, chạy trên thư mục kb giả
(mkdtemp). Kill giả lập bằng một prelude vá open()/Path.write_text/os.replace — không sửa đoạn
code đang test. CHỨNG MINH NGƯỢC: cùng fixture trên bản trước vá (4195911c = c9edd4c6~1) ⇒ ĐỎ.
"""
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "kb_nightly.sh")
PRE_FIX_REF = "4195911c"   # c9edd4c6~1
OPEN_MARK = 'python3 - "$EVENTS_BUFFER" "$CUTOFF" "$ARCHIVE_FILE" <<\'PYEOF\''
CUTOFF = "2026-09-01"

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(("  ✓ " if cond else "  ✗ ") + name + (f"   [{detail}]" if detail and not cond else ""))


def extract_py(sh_text):
    lines = sh_text.splitlines(keepends=True)
    starts = [i for i, ln in enumerate(lines) if ln.rstrip("\n") == OPEN_MARK]
    if len(starts) != 1:
        return None
    body = []
    for ln in lines[starts[0] + 1:]:
        if ln.rstrip("\n") == "PYEOF":
            return "".join(body)
        body.append(ln)
    return None


CANON = "# KB events buffer\n\nCanonical intro line.\n\n"
# Xen kẽ cũ/mới, mỗi event có payload nhiều dòng. Mỗi dòng tiếp nối mang nhãn event của nó.
EVENTS = [("OLD1", "2026-08-20"), ("NEW1", "2026-09-05"), ("OLD2", "2026-08-25"), ("NEW2", "2026-09-10")]


def buffer_text():
    out = CANON
    for tag, d in EVENTS:
        out += f"- [{d}T01:00:00Z] Wags finding {tag}\n  payload-{tag} dòng 2\n  payload-{tag} dòng 3\n"
    return out


# Prelude chạy TRƯỚC đoạn code test. SC_KILL:
#   partial  — mọi lần mở GHI (w) vào buffer hoặc buffer.tmp: ghi 10 byte rồi "chết"
#   replace  — os.replace ném lỗi (chết SAU khi tmp đã ghi đủ, trước khi thay file)
PRELUDE = r'''
import builtins, os, pathlib
_KILL = os.environ.get("SC_KILL", "")
_BUF = os.path.abspath(os.environ["SC_BUFFER"])
_real_open = builtins.open
class _Killed(Exception): pass
class _Trunc:
    def __init__(self, f): self.f = f
    def __enter__(self): return self
    def __exit__(self, *a): self.f.close()
    def write(self, s):
        self.f.write(s[:10]); self.f.flush(); self.f.close()
        raise _Killed("kill giả lập giữa lúc ghi")
def _open(file, mode="r", *a, **k):
    f = _real_open(file, mode, *a, **k)
    if _KILL == "partial" and "w" in mode and os.path.abspath(str(file)) in (_BUF, _BUF + ".tmp"):
        return _Trunc(f)
    return f
builtins.open = _open
def _write_text(self, data, encoding=None, errors=None, newline=None):
    with open(self, "w", encoding=encoding) as fh:
        return fh.write(data)
pathlib.Path.write_text = _write_text
if _KILL == "replace":
    def _boom(*a, **k): raise _Killed("kill giả lập trước os.replace")
    os.replace = _boom
'''


def run_phase1(py, kill=""):
    d = tempfile.mkdtemp(prefix="kbn_p1_sc_")
    try:
        buf = os.path.join(d, "kb", "events_buffer.md")
        arch = os.path.join(d, "kb", "archive", "2026-09-13-nightly.md")
        os.makedirs(os.path.dirname(buf))
        original = buffer_text()
        with open(buf, "w", encoding="utf-8") as f:
            f.write(original)
        env = {"PATH": "/usr/bin:/bin", "SC_KILL": kill, "SC_BUFFER": buf, "LANG": "C.UTF-8"}
        r = subprocess.run([sys.executable, "-", buf, CUTOFF, arch], input=PRELUDE + py,
                           capture_output=True, text=True, env=env, cwd=d, timeout=60)
        read = (lambda p: open(p, encoding="utf-8").read() if os.path.exists(p) else None)
        return {"rc": r.returncode, "err": r.stderr, "original": original,
                "buffer": read(buf), "archive": read(arch), "tmp_left": os.path.exists(buf + ".tmp")}
    finally:
        shutil.rmtree(d, ignore_errors=True)


def routed_ok(r):
    buf, arch = r["buffer"] or "", r["archive"] or ""
    old_ok = all(f"payload-{t} dòng {n}" in arch and f"payload-{t}" not in buf
                 for t in ("OLD1", "OLD2") for n in (2, 3))
    new_ok = all(f"payload-{t} dòng {n}" in buf and f"payload-{t}" not in arch
                 for t in ("NEW1", "NEW2") for n in (2, 3))
    return r["rc"] == 0 and old_ok and new_ok and buf.startswith(CANON)


def partial_kill_ok(r):
    return r["rc"] != 0 and r["buffer"] == r["original"]


print("[0] harness còn sống")
cur_py = extract_py(open(SCRIPT, encoding="utf-8").read())
check("trích được đúng 1 đoạn python Phase 1 từ bản hiện tại", cur_py is not None)
check("đoạn trích là bản atomic (os.replace + last_bucket)",
      bool(cur_py) and "os.replace(tmp, knowledge_path)" in cur_py and "last_bucket" in cur_py)
old = subprocess.run(["git", "-C", HERE, "show", f"{PRE_FIX_REF}:bin/kb_nightly.sh"],
                     capture_output=True, text=True)
old_py = extract_py(old.stdout) if old.returncode == 0 else None
check(f"trích được đoạn Phase 1 bản trước vá ({PRE_FIX_REF})", old_py is not None, old.stderr.strip())
check("bản trước vá ghi đè tại chỗ (write_text), chưa có os.replace",
      bool(old_py) and "write_text" in old_py and "os.replace" not in old_py)
if cur_py is None:
    print("❌ không trích được đoạn python — dừng")
    sys.exit(1)
# Prelude phải THẬT SỰ bắn: chạy nó trên một lệnh ghi thẳng vào buffer ⇒ phải chết.
_probe = run_phase1("open(os.environ['SC_BUFFER'], 'w').write('x' * 100)\n", kill="partial")
check("prelude kill 'partial' thật sự bắn (probe ghi thẳng buffer ⇒ rc≠0, còn 10 byte)",
      _probe["rc"] != 0 and _probe["buffer"] == "x" * 10, (_probe["rc"], _probe["buffer"]))

print("\n[1] buffer xen kẽ cũ/mới, payload nhiều dòng ⇒ dòng tiếp nối đi đúng bucket event của nó")
r = run_phase1(cur_py)
check("rc=0", r["rc"] == 0, r["err"][-300:])
check("OLD1/OLD2 + mọi dòng payload vào archive; NEW1/NEW2 + payload ở lại buffer; canonical giữ nguyên",
      routed_ok(r), {"buffer": r["buffer"], "archive": r["archive"]})
check("không để lại events_buffer.md.tmp", not r["tmp_left"])

print("\n[2] kill giữa lúc ghi (10 byte rồi chết) ⇒ file gốc NGUYÊN VẸN")
r = run_phase1(cur_py, kill="partial")
check("rc≠0 (kill giả lập đã bắn) và buffer == bản gốc từng byte",
      partial_kill_ok(r) and "kill giả lập giữa lúc ghi" in r["err"],
      (r["rc"], (r["buffer"] or "")[:40]))

print("\n[3] kill SAU khi tmp ghi đủ, trước os.replace ⇒ file gốc nguyên vẹn, archive đã fsync")
r = run_phase1(cur_py, kill="replace")
check("rc≠0 (chết đúng tại os.replace) và buffer == bản gốc",
      r["rc"] != 0 and "kill giả lập trước os.replace" in r["err"] and r["buffer"] == r["original"],
      (r["rc"], r["err"][-200:]))
check("archive đã có OLD1/OLD2 (thứ tự archive-trước: đêm sau archive trùng là vô hại, không mất)",
      bool(r["archive"]) and "OLD1" in r["archive"] and "OLD2" in r["archive"])

print(f"\n[RED] CHỨNG MINH NGƯỢC trên bản trước vá {PRE_FIX_REF}")
if old_py is not None:
    o = run_phase1(old_py)
    check("bản cũ [1] ĐỎ — payload OLD2 (sau NEW1) bị giữ lại trong buffer", not routed_ok(o),
          (o["buffer"] or "")[-200:])
    o = run_phase1(old_py, kill="partial")
    check("bản cũ [2] ĐỎ — kill giữa lúc ghi làm hỏng buffer gốc", not partial_kill_ok(o),
          (o["rc"], o["buffer"]))

print(f"\n{'=' * 70}\nKẾT QUẢ: {len(PASS)} PASS / {len(FAIL)} FAIL")
if FAIL:
    print("FAIL:")
    for f in FAIL:
        print("  ·", f)
    sys.exit(1)
