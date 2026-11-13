#!/usr/bin/env python3
"""classifier_denial_count.py — đếm số lần Claude Code auto-mode classifier CHẶN tool call, theo ngày ICT.

Vì sao có (DESIGN decision_inbox §5): `CCDB_PERMISSION_MODE=auto` ⇒ classifier chặn các lệnh bus
hợp lệ (đo 14/10→13/11: 73 lần trong phiên Mike) mà không ai thấy trừ khi user than. Đếm hằng ngày
để retro leo thang khi vượt ngưỡng.

Cách đếm (đã đo, KHÔNG grep -c): mỗi lần chặn xuất hiện lại trong context của các lượt sau ⇒ chuỗi
thô đếm gấp ~2×. Đếm theo `tool_result` có `tool_use_id`, khử trùng theo (agent, tool_use_id), lấy
timestamp SỚM NHẤT, bucket theo ngày ICT (§16: ZoneInfo, không dựa TZ của host).

  classifier_denial_count.py --day 2026-11-13 [--agents Mike,Taylor,Wags] [--json]
"""
from __future__ import annotations

import argparse
import collections
import datetime as dt
import json
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
MARK = "denied by the Claude Code auto mode classifier"
DEFAULT_AGENTS = "Mike,Taylor,Wags"
CMD_RE = re.compile(r"(bin/[\w.-]+|mike/kb/\S+|\.claude/\S+)")


def _ts(s) -> dt.datetime | None:
    try:
        d = dt.datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=dt.timezone.utc)


def scan_file(path: Path) -> dict:
    """⇒ {tool_use_id: (earliest_ts, tool_name, cmd)} cho các tool_result bị chặn trong 1 file."""
    uses: dict = {}
    hits: dict = {}
    try:
        fh = path.open(encoding="utf-8", errors="ignore")
    except OSError:
        return {}
    with fh:
        for line in fh:
            if MARK not in line and '"tool_use"' not in line:
                continue
            try:
                rec = json.loads(line)
            except ValueError:
                continue  # dòng hỏng/cắt dở ⇒ bỏ qua, không làm sập báo cáo
            content = (rec.get("message") or {}).get("content") if isinstance(rec, dict) else None
            if not isinstance(content, list):
                continue
            ts = _ts(rec.get("timestamp"))
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "tool_use":
                    inp = b.get("input") or {}
                    cmd = inp.get("command") or inp.get("file_path") or b.get("name")
                    uses[b.get("id")] = (b.get("name"), str(cmd))
                elif b.get("type") == "tool_result" and MARK in json.dumps(b.get("content"), ensure_ascii=False):
                    tid = b.get("tool_use_id")
                    if ts is None or not tid:
                        continue
                    if tid not in hits or ts < hits[tid][0]:
                        hits[tid] = (ts, None, None)
    out = {}
    for tid, (ts, _n, _c) in hits.items():
        name, cmd = uses.get(tid, ("?", "?"))
        out[tid] = (ts, name, cmd)
    return out


def count_day(projects_dir: Path, day: dt.date, agents: list[str]) -> dict:
    start = dt.datetime.combine(day, dt.time.min, tzinfo=ICT)
    by_agent: dict = {a: 0 for a in agents}
    by_cmd: collections.Counter = collections.Counter()
    close_bus = 0
    for agent in agents:
        seen: dict = {}
        for d in sorted(projects_dir.glob(f"*-agents-{agent}")):
            for f in sorted(d.glob("*.jsonl")):
                try:
                    if dt.datetime.fromtimestamp(f.stat().st_mtime, dt.timezone.utc) < start:
                        continue  # file sửa lần cuối trước ngày đang xét ⇒ không thể chứa sự kiện ngày đó
                except OSError:
                    continue
                for tid, (ts, name, cmd) in scan_file(f).items():
                    if tid not in seen or ts < seen[tid][0]:
                        seen[tid] = (ts, name, cmd)
        for tid, (ts, name, cmd) in seen.items():
            if ts.astimezone(ICT).date() != day:
                continue
            by_agent[agent] += 1
            m = CMD_RE.search(cmd)
            by_cmd[f"{name}:{m.group(1) if m else cmd[:50]}"] += 1
            if "close_bus_question.py" in cmd:
                close_bus += 1
    return {"day": day.isoformat(), "total": sum(by_agent.values()), "by_agent": by_agent,
            "by_cmd_top5": by_cmd.most_common(5), "close_bus_question": close_bus}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--day", required=True, help="YYYY-MM-DD theo giờ ICT")
    ap.add_argument("--agents", default=DEFAULT_AGENTS)
    ap.add_argument("--projects-dir", type=Path, default=Path.home() / ".claude" / "projects")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    try:
        day = dt.date.fromisoformat(a.day)
    except ValueError:
        ap.error("--day phải là YYYY-MM-DD")
    res = count_day(a.projects_dir, day, [x.strip() for x in a.agents.split(",") if x.strip()])
    if a.json:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(f"[classifier denials {res['day']} ICT] total={res['total']} by_agent={res['by_agent']}"
              f" close_bus_question={res['close_bus_question']}")
        for cmd, n in res["by_cmd_top5"]:
            print(f"  {n:3d}  {cmd}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
