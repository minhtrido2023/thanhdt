#!/usr/bin/env python3
"""watcher_slow_threshold.py — "unusually slow" thresholds (t1, t2) for
_job_watcher's anomaly track in dispatch.sh, from state/wakeup_profile.json's
per-(agent,model,effort) bucket history.

Extracted 2026-08-12 (fix for the flat 60s/120s "log trống" false-alarm bug —
claude -p's default text output writes nothing until the process exits, so
those flat thresholds fired on almost every job >120s regardless of health)
so the lookup is testable (watcher_slow_threshold_selfcheck.py) instead of
living as an un-testable `python3 -c` string inside dispatch.sh.

t1 = max(180, median_s)  -- informational: ~half of this bucket's history is
                            already done by here. NOT a crash signal.
t2 = max(t1+60, p75_s)   -- slower than most of history, worth a look.

Missing file / bad JSON / no matching bucket / no global_fallback -> hard
fallback (180, 420). NEVER raises — the watcher must never be blocked by this.

Usage: watcher_slow_threshold.py <bucket_key> <profile_json_path>
Prints: "<t1> <t2>" to stdout.
"""
import json
import sys

FALLBACK = (180, 420)


def compute(bucket_key, profile_path):
    try:
        with open(profile_path, encoding="utf-8") as f:
            prof = json.load(f)
        b = prof.get("buckets", {}).get(bucket_key) or prof.get("global_fallback")
        # No matching bucket AND no global_fallback = same trust level as a
        # missing/corrupt file (the profile is incomplete, not just sparse for
        # this one key) -> hard fallback, don't silently use the embedded
        # `or 455` defaults below as if they were real measurements.
        if not b:
            return FALLBACK
        med = int(b.get("median_s") or 455)
        p75 = int(b.get("p75_s") or med)
        t1 = max(180, med)
        t2 = max(t1 + 60, p75)
        return t1, t2
    except Exception:
        return FALLBACK


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("%d %d" % FALLBACK)
        sys.exit(0)
    _t1, _t2 = compute(sys.argv[1], sys.argv[2])
    print("%d %d" % (_t1, _t2))
