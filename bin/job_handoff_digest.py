#!/usr/bin/env python3
"""Build a compact mechanical handoff digest from prior attempt transcript & bus events.

Used by dispatch.sh (attempt > 1) and bin/resume_pending.py so a retried or resumed
headless agent sees what files were edited/read, recent Bash commands, last notes,
and emitted bus events without re-scanning the repository from scratch.

Always fail-open (prints empty output and exits 0 on missing/corrupt data).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def _projects_root() -> str:
    base = os.environ.get("CLAUDE_CONFIG_DIR") or os.path.join(os.path.expanduser("~"), ".claude")
    return os.path.join(base, "projects")


def _last_valid_uuid(raw: str) -> str:
    picked = ""
    for part in (raw or "").split(","):
        cand = part.strip().lower()
        if UUID_RE.match(cand):
            picked = cand
    return picked


def _session_from_job(root: str, job_id: str) -> str:
    fp = os.path.join(root, "bus", "jobs", f"{job_id}.json")
    try:
        with open(fp, encoding="utf-8") as f:
            data = json.load(f)
        return _last_valid_uuid(str(data.get("session_id") or ""))
    except Exception:
        return ""


def _find_transcript(projects_dir: str, sid: str) -> str:
    if not sid or not UUID_RE.match(sid):
        return ""
    paths = glob.glob(os.path.join(projects_dir, "*", f"{sid}.jsonl"))
    if not paths:
        return ""
    return max(paths, key=os.path.getmtime)


def _dedup_tail(items: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    kept: list[str] = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            kept.append(item)
    return kept[-limit:]


def _parse_transcript(path: str) -> tuple[list[str], list[str], list[str], list[str]]:
    edited: list[str] = []
    read_files: list[str] = []
    bash_cmds: list[str] = []
    notes: list[str] = []

    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return edited, read_files, bash_cmds, notes

    for raw in lines[-800:]:
        try:
            ev = json.loads(raw)
        except Exception:
            continue
        if not isinstance(ev, dict) or ev.get("type") != "assistant":
            continue
        msg = ev.get("message")
        content = msg.get("content") if isinstance(msg, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "tool_use":
                name = str(block.get("name") or "")
                inp = block.get("input") if isinstance(block.get("input"), dict) else {}
                if name in ("Edit", "Write", "MultiEdit", "NotebookEdit"):
                    fp = str(inp.get("file_path") or inp.get("notebook_path") or "").strip()
                    if fp:
                        edited.append(fp)
                elif name == "Read":
                    fp = str(inp.get("file_path") or "").strip()
                    if fp:
                        read_files.append(fp)
                elif name == "Bash":
                    cmd = " ".join(str(inp.get("command") or "").split())
                    if cmd:
                        bash_cmds.append(cmd[:110] + ("…" if len(cmd) > 110 else ""))
            elif btype == "text":
                txt = " ".join(str(block.get("text") or "").split())
                if txt:
                    notes.append(txt[:220] + ("…" if len(txt) > 220 else ""))

    return (
        _dedup_tail(edited, 8),
        _dedup_tail(read_files, 8),
        bash_cmds[-5:],
        notes[-2:],
    )


def _bus_events_for_trace(root: str, job_id: str) -> list[str]:
    if not job_id:
        return []
    hits: list[str] = []
    for fp in sorted(glob.glob(os.path.join(root, "bus", "inbox", "*.jsonl"))):
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                for raw in f:
                    if job_id not in raw:
                        continue
                    try:
                        ev = json.loads(raw)
                    except Exception:
                        continue
                    if isinstance(ev, dict) and ev.get("trace_id") == job_id:
                        hits.append(f"{ev.get('agent','?')}/{ev.get('event_type','?')}: {ev.get('topic','?')}")
        except OSError:
            continue
    return hits[-4:]


def build_digest(root: str, projects_dir: str, sid: str = "", job_id: str = "", max_chars: int = 1200) -> str:
    resolved_sid = _last_valid_uuid(sid) or (_session_from_job(root, job_id) if job_id else "")
    tpath = _find_transcript(projects_dir, resolved_sid)
    edited, read_files, bash_cmds, notes = _parse_transcript(tpath) if tpath else ([], [], [], [])
    bus_hits = _bus_events_for_trace(root, job_id) if job_id else []

    if not (edited or read_files or bash_cmds or notes or bus_hits):
        return ""

    out: list[str] = [f"=== HANDOFF DIGEST (cơ học từ lần chạy trước, sid={resolved_sid[:8] or '?'}) ==="]
    if edited:
        out.append("- File đã sửa/ghi: " + ", ".join(edited))
    if read_files:
        out.append("- File đã đọc gần nhất: " + ", ".join(read_files))
    if bash_cmds:
        out.append("- Lệnh Bash cuối:")
        for i, cmd in enumerate(bash_cmds, 1):
            out.append(f"  {i}. `{cmd}`")
    if bus_hits:
        out.append("- Bus events đã ghi (trace này): " + " | ".join(bus_hits))
    if notes:
        out.append("- Ghi chú cuối trước khi dừng: " + " // ".join(notes))

    text = "\n".join(out)
    if len(text) > max_chars:
        text = text[: max_chars - 1].rstrip() + "…"
    return text


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--session-id", default="", help="Session UUID (or comma-separated list)")
    ap.add_argument("--job", default="", help="Previous job_id to inspect record & trace_id")
    ap.add_argument("--max-chars", type=int, default=1200)
    a, _ = ap.parse_known_args()

    root = os.environ.get("MIKE_ROOT") or DEFAULT_ROOT
    projects_dir = _projects_root()
    digest = build_digest(root, projects_dir, sid=a.session_id, job_id=a.job, max_chars=max(200, a.max_chars))
    if digest:
        print(digest)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
