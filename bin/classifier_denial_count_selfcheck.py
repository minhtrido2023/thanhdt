#!/usr/bin/env python3
"""Selfcheck classifier_denial_count.py — fixture 3+ jsonl, --projects-dir tmpdir (không đọc ~/.claude thật)."""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("MIKE_BOT_TEST_MODE", "1")
sys.path.insert(0, str(Path(__file__).resolve().parent))
import classifier_denial_count as cdc  # noqa: E402

TOOL = Path(__file__).resolve().parent / "classifier_denial_count.py"
N = [0, 0]
MSG = "Permission denied by the Claude Code auto mode classifier: not allowed"


def check(name, cond, detail=""):
    N[0] += 1
    if not cond:
        N[1] += 1
        print(f"FAIL {name}: {detail}", file=sys.stderr)


def use(tid, cmd, ts, name="Bash"):
    return {"timestamp": ts, "message": {"content": [{"type": "tool_use", "id": tid, "name": name,
                                                      "input": {"command": cmd}}]}}


def res(tid, ts, text=MSG):
    return {"timestamp": ts, "message": {"content": [{"type": "tool_result", "tool_use_id": tid,
                                                      "content": [{"type": "text", "text": text}]}]}}


def write(path: Path, rows, broken=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
        if broken:
            f.write('{"timestamp": "2026-11-13T05:00:00Z", "message": {"content": [ ' + MSG + "\n")


with tempfile.TemporaryDirectory() as td:
    pd = Path(td)
    now = dt.datetime.now(dt.timezone.utc)
    # Mike: 1 lần chặn lặp 2 dòng (context) + 1 lần ngoài ICT-ngày + 1 lần OK + 1 dòng hỏng
    write(pd / "-x-agents-Mike" / "a.jsonl", [
        use("t1", "python3 /x/mike/bin/close_bus_question.py Mike/foo", "2026-11-13T05:00:00Z"),
        res("t1", "2026-11-13T05:00:01Z"),
        res("t1", "2026-11-13T09:00:00Z"),                      # lặp lại trong context ⇒ vẫn là 1
        use("t2", "bin/approve_plan_simple.sh", "2026-11-13T16:59:00Z"),
        res("t2", "2026-11-13T16:59:30Z"),                      # 23:59:30 ICT 13/11
        use("t3", "bin/jobs.sh list", "2026-11-13T17:00:00Z"),
        res("t3", "2026-11-13T17:00:05Z"),                      # 00:00:05 ICT 14/11
        use("t4", "ls", "2026-11-13T06:00:00Z"),
        res("t4", "2026-11-13T06:00:01Z", text="ok bình thường"),  # không bị chặn
    ], broken=True)
    write(pd / "-x-agents-Mike" / "b.jsonl", [
        use("t5", "bin/remember.sh Mike x", "2026-11-13T23:30:00Z"),   # 06:30 ICT 14/11 (đêm UTC = sáng ICT hôm sau)
        res("t5", "2026-11-13T23:30:10Z"),
    ])
    write(pd / "-x-agents-Taylor" / "c.jsonl", [
        use("t6", "bin/dispatch.sh Mafee x", "2026-11-13T02:00:00Z"),
        res("t6", "2026-11-13T02:00:01Z"),
    ])
    write(pd / "-x-agents-Wendy" / "d.jsonl", [use("t7", "x", "2026-11-13T02:00:00Z"), res("t7", "2026-11-13T02:00:01Z")])

    late = dt.datetime(2026, 11, 20, tzinfo=dt.timezone.utc).timestamp()  # mtime ≥ mọi sự kiện fixture
    for f in pd.glob("*/*.jsonl"):
        os.utime(f, (late, late))
    r = cdc.count_day(pd, dt.date(2026, 11, 13), ["Mike", "Taylor", "Wags"])
    check("tool_result lặp 2 dòng đếm 1 (t1) + t2 ⇒ Mike=2", r["by_agent"]["Mike"] == 2, str(r))
    check("Taylor=1, Wags=0", r["by_agent"]["Taylor"] == 1 and r["by_agent"]["Wags"] == 0, str(r))
    check("agent không yêu cầu (Wendy) bị loại", r["total"] == 3, str(r))
    check("close_bus_question đếm riêng = 1", r["close_bus_question"] == 1, str(r))
    check("by_cmd_top5 có approve_plan_simple.sh", any("approve_plan_simple.sh" in c for c, _ in r["by_cmd_top5"]), str(r))
    r14 = cdc.count_day(pd, dt.date(2026, 11, 14), ["Mike", "Taylor", "Wags"])
    check("23:59:30 ICT ở ngày 13, 00:00:05 ICT sang ngày 14 (t3) + 06:30 (t5) ⇒ Mike(14)=2",
          r14["by_agent"]["Mike"] == 2, str(r14))
    r12 = cdc.count_day(pd, dt.date(2026, 11, 12), ["Mike"])
    check("ngày không có sự kiện ⇒ 0", r12["total"] == 0, str(r12))
    # mtime-skip: file cũ hơn ngày xét bị bỏ qua
    old = (dt.datetime(2026, 11, 1) - dt.datetime(1970, 1, 1)).total_seconds()
    os.utime(pd / "-x-agents-Taylor" / "c.jsonl", (old, old))
    r = cdc.count_day(pd, dt.date(2026, 11, 13), ["Taylor"])
    check("file mtime trước ngày xét ⇒ bỏ qua", r["total"] == 0, str(r))

    # CLI: --json, và độc lập TZ host
    for tz in (None, "America/New_York", "Asia/Tokyo"):
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tz:
            env["TZ"] = tz
        out = subprocess.run([sys.executable, str(TOOL), "--day", "2026-11-13", "--projects-dir", str(pd),
                              "--agents", "Mike,Wags", "--json"], capture_output=True, text=True, env=env)
        j = json.loads(out.stdout)
        check(f"CLI --json TZ={tz} ⇒ Mike=2,Wags=0", j["by_agent"] == {"Mike": 2, "Wags": 0}, out.stdout + out.stderr)
    bad = subprocess.run([sys.executable, str(TOOL), "--day", "13/11/2026", "--projects-dir", str(pd)],
                         capture_output=True, text=True)
    check("--day sai định dạng ⇒ rc≠0", bad.returncode != 0)

if N[1]:
    print(f"classifier_denial_count_selfcheck: {N[0] - N[1]}/{N[0]} PASS, {N[1]} FAIL", file=sys.stderr)
    sys.exit(1)
print(f"classifier_denial_count_selfcheck: {N[0]}/{N[0]} PASS")
