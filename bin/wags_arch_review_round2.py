#!/usr/bin/env python3
"""wags_arch_review_round2.py <arch_reviewer_inbox.jsonl> <topic_prefix> [window_hours=24] [now_iso]

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

## Window anchored to the LAST TWO rounds, not first→latest (arch-review coord-2026-09-19
## round-2 audit, required_change #4)

A first→latest anchor makes a chronic streak permanently un-escalatable: once the OLDEST bad
verdict falls outside the window, the whole streak reads as "too spread out" even when the
two most recent rounds are an hour apart — exactly the case that most needs escalating. The
signal that matters is "are the last two rounds close together in time", so `within_window`
compares only the two most recent entries in the streak.

`now_iso` (optional) additionally requires the LATEST round itself to be recent relative to
"now" — without it, a synthetic/stale pair of old verdicts that happen to be close to each
other would still read as escalate=True. The caller (wags_autofix.sh) always invokes this
script immediately after arch-review just posted the current verdict, so in production
`now_iso` is always supplied and the latest round is inherently ≈ now; the parameter mainly
makes that guarantee explicit and testable, matching the explicit-timestamp discipline
already used elsewhere in this file's callers (mike_json.py has-event-prefix,
DISPATCH_START_ISO) rather than a bare relative "N hours ago".

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
        print('{"escalate": false, "error": "usage: wags_arch_review_round2.py <inbox> <topic_prefix> [window_hours] [now_iso]"}')
        return 1
    inbox, prefix = sys.argv[1], sys.argv[2]
    window_hours = float(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3] else 24.0
    now_dt = _parse_ts(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[4] else None

    try:
        events = _load_events(inbox, prefix)
    except OSError:
        print('{"escalate": false, "error": "cannot read inbox"}')
        return 1

    streak = _current_streak(events)
    if len(streak) < 2:
        print(json.dumps({"escalate": False, "round_count": len(streak)}))
        return 1

    first, prev, latest = streak[0], streak[-2], streak[-1]
    window = timedelta(hours=window_hours)
    last_two_close = (latest["_dt"] - prev["_dt"]) <= window
    fresh = now_dt is None or (now_dt - latest["_dt"]) <= window
    escalate = bool(last_two_close and fresh)
    out = {
        "escalate": escalate,
        "round_count": len(streak),
        "first_ts": first["ts"],
        "latest_ts": latest["ts"],
        "window_hours": window_hours,
        "last_two_gap_hours": round((latest["_dt"] - prev["_dt"]).total_seconds() / 3600, 2),
        "rounds": [
            {"round": i + 1, "ts": r["ts"], "verdict": r["verdict"],
             "required_changes": r["required_changes"]}
            for i, r in enumerate(streak)
        ],
    }
    if now_dt is not None:
        out["now_iso"] = sys.argv[4]
        out["fresh"] = fresh
    print(json.dumps(out, ensure_ascii=False))
    return 0 if escalate else 1


if __name__ == "__main__":
    sys.exit(main())
