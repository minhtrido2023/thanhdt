#!/usr/bin/env python3
"""Mechanically precollect daily retro incidents, bus events, and cited artifact checks.

Runs in bin/daily_retro.sh BEFORE Mike writes the draft so Mike receives verified
incident files, bus events, and disk/git existence checks upfront instead of spending
many sequential turns hunting them manually.

Fail-open: prints nothing or partial findings cleanly with exit 0.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH_RE = re.compile(r"\b(?:kb|bin|hooks|agents|trading_bot)/[A-Za-z0-9_./-]+\.[A-Za-z0-9]+\b")
SHA_RE = re.compile(r"\b(?=[0-9a-f]{7,40}\b)(?=[0-9a-f]*[a-f])[0-9a-f]{7,40}\b")


def _git_has_commit(repos: list[str], sha: str) -> bool:
    for repo in repos:
        if not os.path.isdir(os.path.join(repo, ".git")) and not os.path.isfile(os.path.join(repo, ".git")):
            continue
        try:
            r = subprocess.run(
                ["git", "cat-file", "-t", sha],
                cwd=repo,
                capture_output=True,
                text=True,
                timeout=3,
            )
            if r.returncode == 0 and r.stdout.strip() == "commit":
                return True
        except Exception:
            continue
    return False


def precollect(root: str, day: str, max_chars: int = 2500) -> str:
    wc_root = os.path.dirname(root)
    inc_files = sorted(
        os.path.relpath(p, root)
        for p in glob.glob(os.path.join(root, "kb", "incidents", "*", f"{day}-*.md"))
        if not os.path.basename(p).startswith("retro-")
    )

    bus_events: list[str] = []
    cited_paths: set[str] = set()
    cited_shas: set[str] = set()

    for rel in inc_files:
        try:
            txt = open(os.path.join(root, rel), encoding="utf-8", errors="replace").read()
            cited_paths.update(PATH_RE.findall(txt))
            cited_shas.update(SHA_RE.findall(txt))
        except OSError:
            pass

    for fp in sorted(glob.glob(os.path.join(root, "bus", "inbox", "*.jsonl"))):
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                for raw in f:
                    if day not in raw:
                        continue
                    try:
                        ev = json.loads(raw)
                    except Exception:
                        continue
                    if not isinstance(ev, dict):
                        continue
                    if not str(ev.get("ts") or "").startswith(day):
                        continue
                    et = str(ev.get("event_type") or "")
                    if et not in ("error", "finding", "question", "answer", "verification"):
                        continue
                    topic = str(ev.get("topic") or "")
                    agent = str(ev.get("agent") or "?")
                    bus_events.append(f"{agent}/{et}:{topic}")
                    payload_txt = json.dumps(ev.get("payload") or "", ensure_ascii=False)
                    cited_paths.update(PATH_RE.findall(payload_txt))
                    cited_shas.update(SHA_RE.findall(payload_txt))
        except OSError:
            continue

    existing_paths: list[str] = []
    missing_paths: list[str] = []
    for p in sorted(cited_paths)[:20]:
        if os.path.exists(os.path.join(root, p)) or os.path.exists(os.path.join(wc_root, p)):
            existing_paths.append(p)
        else:
            missing_paths.append(p)

    repos = [root, wc_root]
    valid_shas: list[str] = []
    missing_shas: list[str] = []
    for s in sorted(cited_shas)[:15]:
        if _git_has_commit(repos, s):
            valid_shas.append(s)
        else:
            missing_shas.append(s)

    lines = [f"[retro-precollect {day}]"]
    lines.append(
        f"- Incidents ({len(inc_files)}): " + (", ".join(inc_files[:12]) if inc_files else "(none)")
    )
    lines.append(
        f"- Bus events ({len(bus_events)}): " + ("; ".join(bus_events[:15]) if bus_events else "(none)")
    )
    if existing_paths or missing_paths:
        lines.append(
            f"- Cited files: ok={len(existing_paths)} missing={len(missing_paths)}"
            + (f" [{', '.join(missing_paths[:5])}]" if missing_paths else "")
        )
    if valid_shas or missing_shas:
        lines.append(
            f"- Cited commits: ok={len(valid_shas)} missing={len(missing_shas)}"
            + (f" [{', '.join(missing_shas[:5])}]" if missing_shas else "")
        )

    out = "\n".join(lines)
    if len(out) > max_chars:
        out = out[: max_chars - 1].rstrip() + "…"
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--day", default="")
    ap.add_argument("--root", default="")
    ap.add_argument("--max-chars", type=int, default=2500)
    a, _ = ap.parse_known_args()

    day = a.day or datetime.now(ICT).strftime("%Y-%m-%d")
    root = a.root or os.environ.get("MIKE_ROOT") or DEFAULT_ROOT
    print(precollect(root, day, max_chars=max(300, a.max_chars)))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
