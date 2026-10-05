#!/usr/bin/env python3
"""Selfcheck 3 finding code-review cq-2026-10-04-hard-boundary (user duyệt sửa cả ba, 2026-10-05).
 (a) capit_episode: close_date/updated_at theo ICT, không theo TZ host
 (b) bot_execute._notify_gdkhq_shadow: lỗi ở topic đầu không nuốt topic duyệt rollout
 (c) bot_execute._write_trace_atomic: nguyên tử, không để .tmp, không còn 2 bản sao khối ghi
Sandbox: không ghi data/ thật, không gửi Discord."""
import ast, datetime as dt, json, os, sys, tempfile
os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
fails = 0
def chk(name, ok):
    global fails; fails += (not ok); print(("PASS " if ok else "FAIL ") + name)

# ---- (a) capit_episode
import capit_episode as ce
UTC = dt.timezone.utc
FIXED = dt.datetime(2026, 10, 4, 18, 0, tzinfo=UTC)          # = 2026-10-05 01:00 ICT
class FakeDT(dt.datetime):
    @classmethod
    def now(cls, tz=None):
        return FIXED.astimezone(tz) if tz else FIXED.astimezone().replace(tzinfo=None)
ce.datetime = FakeDT
with tempfile.TemporaryDirectory() as td:
    lp = os.path.join(td, "capit_episode.json")
    json.dump({"episodes": [{"episode_id": "E1", "status": "open"}]}, open(lp, "w"))
    ce.close("E1", "selfcheck", ledger_path=lp)
    led = json.load(open(lp))
    chk(f"close_date theo ICT (TZ host={os.environ.get('TZ')}) = 2026-10-05", led["episodes"][0].get("close_date") == "2026-10-05")
    chk("updated_at (nếu có) ngày ICT 2026-10-05", str(led.get("updated_at", "2026-10-05")).startswith("2026-10-05"))
    chk("updated_at không mang offset (giữ định dạng cũ)", "+" not in str(led.get("updated_at", "")))

# ---- (b)(c) bot_execute
import bot_execute as be
import subprocess
calls = []
real_run, real_isfile = subprocess.run, os.path.isfile
def fake_run(cmd, **k):
    calls.append(cmd[2])
    if cmd[2] == be._TRADING_DAILY_THREAD:
        raise subprocess.TimeoutExpired(cmd, 20)
be.subprocess.run = fake_run
be.os.path.isfile = lambda p: True if str(p).endswith("notify_thread.sh") else real_isfile(p)
be._notify_gdkhq_shadow("msg")
be.subprocess.run = real_run; be.os.path.isfile = real_isfile
chk("topic đầu timeout ⇒ topic duyệt rollout VẪN được gửi", calls == [be._TRADING_DAILY_THREAD, be._GDKHQ_DECISION_THREAD])
calls.clear()
def fake_run2(cmd, **k): calls.append(cmd[2])
be.subprocess.run = fake_run2; be.os.path.isfile = lambda p: True if str(p).endswith("notify_thread.sh") else real_isfile(p)
be._notify_gdkhq_shadow("msg"); be.subprocess.run = real_run; be.os.path.isfile = real_isfile
chk("không lỗi ⇒ gửi đủ 2 topic", len(calls) == 2)

with tempfile.TemporaryDirectory() as td:
    path = os.path.join(td, "t.json"); be._write_trace_atomic(path, {"a": 1, "v": "ế"})
    chk("trace ghi ra JSON hợp lệ (utf-8)", json.load(open(path, encoding="utf-8")) == {"a": 1, "v": "ế"})
    chk("không để file .tmp", os.listdir(td) == ["t.json"])
    be._write_trace_atomic(path, {"a": 2})
    chk("ghi đè nguyên tử lần 2", json.load(open(path))["a"] == 2)
    try:
        be._write_trace_atomic(path, {"bad": object().__class__})   # default=str xử lý được ⇒ không lỗi
        ok = True
    except Exception: ok = False
    chk("giá trị lạ qua default=str không làm hỏng", ok)

src = open(os.path.join(HERE, "bot_execute.py")).read()
chk("khối ghi tmp+os.replace chỉ còn MỘT bản (trong helper)", src.count("os.replace(tmp_path, trace_path)") == 1)
tree = ast.parse(src)
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_notify_gdkhq_shadow")
loop = next(n for n in ast.walk(fn) if isinstance(n, ast.For))
chk("try/except nằm TRONG vòng for (per-target)", any(isinstance(n, ast.Try) for n in loop.body))
print(f"{'FAIL' if fails else 'ALL PASS'} ({fails} fail)"); sys.exit(1 if fails else 0)
