#!/usr/bin/env python3
"""wags_arch_review_round2.py <arch_reviewer_inbox.jsonl> <topic_prefix> [window_hours=24]

Detect back-to-back NEEDS_CHANGES/REFUTED verdicts from arch-reviewer on the SAME
coordination topic (matched by prefix, same convention as wags_bus_verdict.py /
mike_json.py has-event-prefix — arch-reviewer's own topic can carry a free-text
suffix after "ARCH-REVIEW: wags-fix: <label>"). Prints one JSON object to stdout;
exit 0 when the caller should escalate, exit 1 otherwise (including "not enough data").

Why this exists (user mandate 2026-09-19, retro-2026-09-17 + retro-2026-09-18): Wags
self-closed a round-1 NEEDS_CHANGES question ("decided_by": "Wags", meaning Wags itself
decided the fix was done) before the fix was actually confirmed; arch-review caught it
again on round 2 the same day (05:48Z, ~4h after round 1). The round-2 question that
wags_autofix.sh posted (WAGS_POSTQ_BEGIN/_post_q) was correctly opened but got no
different treatment from a first-time NEEDS_CHANGES — it sat unanswered ~43h because
nothing treated "2 bad verdicts in a row, same topic" as a distinct, higher-urgency
signal that ops_health_check's normal 48h aged-question sweep would catch too late.

Only a CONSECUTIVE run of bad verdicts counts: a CONFIRMED for this topic resets the
streak (a later regression on the same label is a NEW instance, not "still round 2").
INCONCLUSIVE neither extends nor resets the streak — it is not evidence either way
(kb/coding_guidelines.md §26, verify-artifact-not-self-report).

This script only DETECTS; it never posts or closes anything — wags_autofix.sh decides
what to do with the verdict.
"""
import json
import sys
from datetime import datetime, timedelta, timezone

BAD_VERDICTS = {"NEEDS_CHANGES", "REFUTED"}
RESET_VERDICTS = {"CONFIRMED"}


def _parse_ts(ts):
    try:
        return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except Exception:
        return None


def _load_events(inbox, prefix):
    out = []
    with open(inbox, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if not ln:
                continue
            try:
                e = json.loads(ln)
            except Exception:
                continue
            if e.get("event_type") != "verification":
                continue
            if not str(e.get("topic") or "").startswith(prefix):
                continue
            payload = e.get("payload")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except Exception:
                    payload = None
            if not isinstance(payload, dict):
                continue
            verdict = payload.get("verdict")
            if verdict not in BAD_VERDICTS and verdict not in RESET_VERDICTS:
                continue
            dt = _parse_ts(str(e.get("ts") or ""))
            if dt is None:
                continue
            out.append({
                "ts": e.get("ts"), "_dt": dt, "verdict": verdict,
                "required_changes": payload.get("required_changes") or [],
            })
    out.sort(key=lambda r: r["_dt"])
    return out


def _current_streak(events):
    """Consecutive bad-verdict run since the last CONFIRMED (or since the start)."""
    streak = []
    for e in events:
        if e["verdict"] in RESET_VERDICTS:
            streak = []
        elif e["verdict"] in BAD_VERDICTS:
            streak.append(e)
    return streak


def main():
    if len(sys.argv) < 3:
        print('{"escalate": false, "error": "usage: wags_arch_review_round2.py <inbox> <topic_prefix> [window_hours]"}')
        return 1
    inbox, prefix = sys.argv[1], sys.argv[2]
    window_hours = float(sys.argv[3]) if len(sys.argv) > 3 else 24.0

    try:
        events = _load_events(inbox, prefix)
    except OSError:
        print('{"escalate": false, "error": "cannot read inbox"}')
        return 1

    streak = _current_streak(events)
    if len(streak) < 2:
        print(json.dumps({"escalate": False, "round_count": len(streak)}))
        return 1

    first, latest = streak[0], streak[-1]
    within_window = (latest["_dt"] - first["_dt"]) <= timedelta(hours=window_hours)
    out = {
        "escalate": bool(within_window),
        "round_count": len(streak),
        "first_ts": first["ts"],
        "latest_ts": latest["ts"],
        "window_hours": window_hours,
        "rounds": [
            {"round": i + 1, "ts": r["ts"], "verdict": r["verdict"],
             "required_changes": r["required_changes"]}
            for i, r in enumerate(streak)
        ],
    }
    print(json.dumps(out, ensure_ascii=False))
    return 0 if within_window else 1


if __name__ == "__main__":
    sys.exit(main())
