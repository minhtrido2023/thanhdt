#!/usr/bin/env python3
"""time_claim_audit.py — detect LLM time-reasoning claims that don't match reality.

§S4, agents/Mike/research/discord_time_reasoning_by_construction_plan_20260821.md.
This is a MEASUREMENT tool, not a gate: it never blocks, only logs. The 2026-08-21
incident ("Phiên chiều mở lúc 13:00 ICT — còn ~15 phút." sent at 23:02 ICT) is loại C
("LLM SUY LUẬN sai" — the label was correctly ICT, the number was invented) — nothing
at the transport layer can catch that class of error, so instead of blocking we scan
what the fleet already sent and flag countdown claims ("còn ~N phút") whose target
clock time doesn't match how much time had actually elapsed when the message was sent.

False positives are expected and OK ("13:00 ngày mai còn ~14 giờ" is a valid claim) —
see plan §3 for why heuristic-and-log beats block-and-sometimes-wrong here.

Usage:
    time_claim_audit.py [--days N] [--dry-run]

Without --dry-run, mismatches are pushed to the bus (agent quant-skeptic, event
finding) and the Architecture Discord topic.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # mike/
_ICT = ZoneInfo("Asia/Ho_Chi_Minh")

sys.path.insert(0, "/home/trido/thanhdt/WorkingClaude/trading_bot")
try:
    from vn_market import session_phase  # noqa: E402  (needs sys.path insert above)
except Exception:
    session_phase = None

# Only fleet agents' own transcripts carry the Discord-facing replies worth auditing —
# not every project dir under ~/.claude/projects (worktrees, scratch sessions, etc.).
_PROJECT_GLOB = os.path.join(
    os.path.expanduser("~/.claude/projects"),
    "-home-trido-thanhdt-WorkingClaude-mike-agents-*",
    "*.jsonl",
)

TOLERANCE_MINUTES = 10

# Two orders of the same claim shape, per the plan's own examples:
#   "...lúc 13:00 ICT — còn ~15 phút"        (target time first)
#   "...còn ~15 phút tới 13:00"              (countdown first)
_RE_TIME_CLAIM = re.compile(
    r"(?:(?:mở\s+)?lúc\s*(?P<h1>\d{1,2}):(?P<m1>\d{2})(?:\s*ICT)?[^\n]{0,40}?"
    r"còn\s*~?\s*(?P<n1>\d{1,3})\s*(?P<u1>phút|giờ))"
    r"|(?:còn\s*~?\s*(?P<n2>\d{1,3})\s*(?P<u2>phút|giờ)[^\n]{0,40}?"
    r"(?:lúc|tới)\s*(?P<h2>\d{1,2}):(?P<m2>\d{2}))",
    re.IGNORECASE,
)


def _parse_ts(ts_str: str) -> datetime:
    """Parse a transcript timestamp ('2026-08-21T16:02:42.809Z') into ICT-aware."""
    dt_naive = datetime.fromisoformat(ts_str.rstrip("Z"))
    return dt_naive.replace(tzinfo=timezone.utc).astimezone(_ICT)


def _iter_text_records(path: str):
    """Yield (timestamp_str, text) for each assistant text block in a transcript."""
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if rec.get("type") != "assistant":
                    continue
                ts = rec.get("timestamp")
                content = (rec.get("message") or {}).get("content")
                if not ts or not isinstance(content, list):
                    continue
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text") or ""
                        if text:
                            yield ts, text
    except (OSError, UnicodeDecodeError):
        return


def _extract_claims(text: str):
    for m in _RE_TIME_CLAIM.finditer(text):
        if m.group("h1") is not None:
            h, mi, n, unit = m.group("h1"), m.group("m1"), m.group("n1"), m.group("u1")
        else:
            h, mi, n, unit = m.group("h2"), m.group("m2"), m.group("n2"), m.group("u2")
        yield int(h), int(mi), int(n), unit.lower(), m.group(0)


def _check_claim(sent_ict: datetime, target_h: int, target_m: int, claimed_n: int, unit: str, snippet: str):
    """Return a finding dict if the countdown claim doesn't match reality, else None."""
    if not (0 <= target_h <= 23 and 0 <= target_m <= 59):
        return None
    target = sent_ict.replace(hour=target_h, minute=target_m, second=0, microsecond=0)
    if target <= sent_ict:
        target += timedelta(days=1)
    actual_minutes = (target - sent_ict).total_seconds() / 60
    claimed_minutes = claimed_n * (60 if unit == "giờ" else 1)
    if abs(actual_minutes - claimed_minutes) <= TOLERANCE_MINUTES:
        return None
    phase = "?"
    if session_phase is not None:
        try:
            phase = session_phase(sent_ict.replace(tzinfo=None))[0]
        except Exception:
            phase = "?"
    return {
        "sent_at_ict": sent_ict.strftime("%Y-%m-%d %H:%M:%S"),
        "claimed_target": f"{target_h:02d}:{target_m:02d}",
        "claimed_minutes": claimed_minutes,
        "actual_minutes_to_target": round(actual_minutes, 1),
        "session_phase_at_send": phase,
        "snippet": snippet.strip(),
    }


def find_mismatches(days: int) -> list[dict]:
    now_ict = datetime.now(_ICT)
    cutoff = now_ict - timedelta(days=days)
    findings = []
    for path in glob.glob(_PROJECT_GLOB):
        for ts, text in _iter_text_records(path):
            try:
                sent_ict = _parse_ts(ts)
            except (ValueError, OverflowError):
                continue
            if sent_ict < cutoff:
                continue
            for h, m, n, unit, snippet in _extract_claims(text):
                finding = _check_claim(sent_ict, h, m, n, unit, snippet)
                if finding:
                    finding["source_file"] = os.path.relpath(path, os.path.expanduser("~/.claude/projects"))
                    findings.append(finding)
    return findings


def _report(findings: list[dict], days: int) -> None:
    today = datetime.now(_ICT).strftime("%Y%m%d")
    payload = json.dumps(
        {"count": len(findings), "days": days, "findings": findings[:20]},
        ensure_ascii=False,
    )
    append_event = os.path.join(ROOT, "bin", "append_event.sh")
    subprocess.run(
        [append_event, "quant-skeptic", "finding", f"time-claim-audit-{today}", payload],
        check=False,
    )
    notify_thread = os.path.join(ROOT, "bin", "notify_thread.sh")
    top = findings[0]
    msg = (
        f"⏱️ time_claim_audit: {len(findings)} mismatch(es) trong {days} ngày qua. "
        f"Ví dụ: gửi lúc {top['sent_at_ict']} ICT (phiên {top['session_phase_at_send']}), "
        f"nhưng claim \"{top['snippet']}\" ⇒ target {top['claimed_target']} lệch thực tế "
        f"~{top['actual_minutes_to_target']:.0f} phút (claim {top['claimed_minutes']} phút). "
        f"Chi tiết đầy đủ trên bus (topic time-claim-audit-{today})."
    )
    subprocess.run([notify_thread, msg, "architecture"], check=False)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--days", type=int, default=1)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    findings = find_mismatches(args.days)
    print(f"time_claim_audit: scanned last {args.days} day(s), {len(findings)} mismatch(es) found")
    for f in findings:
        print(json.dumps(f, ensure_ascii=False))

    if findings and not args.dry_run:
        _report(findings, args.days)

    return 0


if __name__ == "__main__":
    sys.exit(main())
