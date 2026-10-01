#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
deposit_cctg_trend_check.py — detect a DECLINE in the Big-4 12M deposit rate OR the Big-4 CCTG 6M
rate (the two triggers the user defined, job Taylor_20261001_054108: "lãi suất huy động tháng sau
giảm so với tháng trước" / "chứng chỉ tiền gửi phát hành đợt sau thấp hơn đợt trước") and raise a
WARNING-ONLY alert. This NEVER writes to any series CSV and NEVER touches park/sizing state —
park 0% is a user-only reversal decision (CLAUDE.md macro-killswitch section), this script's only
job is to make sure the user notices a decline promptly.

Compares the LAST TWO anchors (by effective_date) of each series as currently on disk — it does
not care whether this week's run wrote a new anchor or not, so it still catches a decline that
entered the CSV via the monthly Big-4 refresh or a manual append, not just the weekly job.

Idempotent by construction: state/deposit_cctg_trend_alert_state.json remembers the (prev, new)
pair already alerted per series. Re-running on an unchanged CSV (or a run after a non-declining
write) never re-fires the same pair.

CLI:
  python3 deposit_cctg_trend_check.py            # live: may post Discord + bus event + write state
  python3 deposit_cctg_trend_check.py --dry-run   # print only, never notify/post/write state
"""
import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import date, datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")  # coding_guidelines §16: never trust the host system TZ

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
MIKE_BIN = os.path.join(HERE, "mike", "bin")
STATE_PATH = os.path.join(HERE, "data", "deposit_cctg_trend_alert_state.json")
DISCORD_THREAD_ID = "1521470705563340910"  # Trading Daily

SERIES = {
    "big4_12m": {
        "label": "Lãi suất huy động 12 tháng Big-4 (online)",
        "tenor": "12M",
    },
    "cctg_6m": {
        "label": "Chứng chỉ tiền gửi (CCTG) 6 tháng Big-4",
        "tenor": "6M",
    },
}

# Same 45-day threshold macro_killswitch_a_status() uses (deposit_rate_vn.py) — kept as a literal
# here rather than imported, to avoid this script silently tracking a future change to that
# function's default; if the production threshold changes, update both call sites deliberately.
STALE_DAYS_LIMIT = 45
STALE_WARN_BEFORE_DAYS = 10  # start a proactive reminder at day (45-10)=35, not just at day 46


def _load_series():
    """Returns {series_key: [(date_str, rate_float), ...]} sorted ascending by date."""
    import deposit_rate_vn
    import cctg_rate_vn

    out = {}

    dep = deposit_rate_vn.deposit_events_df().sort_values("time")
    out["big4_12m"] = [(d.date().isoformat(), float(r))
                        for d, r in zip(dep["time"], dep["deposit_rate"])]

    cctg = cctg_rate_vn.cctg_events_df().sort_values("time")
    out["cctg_6m"] = [(d.date().isoformat(), float(r))
                       for d, r in zip(cctg["time"], cctg["cctg_rate"])]

    return out


def _load_state():
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return {}  # fail-open on a corrupt state file: worst case is a re-alert, not a missed one


def _write_state_atomic(state):
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(STATE_PATH), prefix=".trend_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2, sort_keys=True)
        os.replace(tmp, STATE_PATH)
    except Exception:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def check_declines(series_data, state):
    """Returns list of decline events: {key, label, tenor, prev_date, prev_rate, new_date, new_rate}
    for pairs not already present in state. Pure function — no I/O, easy to unit-test/mutate."""
    declines = []
    for key, points in series_data.items():
        if len(points) < 2:
            continue
        prev_date, prev_rate = points[-2]
        new_date, new_rate = points[-1]
        if new_rate >= prev_rate:
            continue  # flat or up — not a decline
        already = state.get(key, {}).get("alerted_pair")
        pair = [prev_date, prev_rate, new_date, new_rate]
        if already == pair:
            continue  # same pair already alerted — idempotent skip
        declines.append({
            "key": key, "label": SERIES[key]["label"], "tenor": SERIES[key]["tenor"],
            "prev_date": prev_date, "prev_rate": prev_rate,
            "new_date": new_date, "new_rate": new_rate,
        })
    return declines


def check_staleness(series_data, state, today):
    """Returns list of staleness warnings for series whose last anchor age has crossed into the
    warn window [STALE_DAYS_LIMIT - STALE_WARN_BEFORE_DAYS, ...) and hasn't been warned yet FOR
    THAT SAME last_date (a new anchor arriving naturally resets the warning — idempotent per
    last_date, not per calendar day, so it doesn't spam every week while stuck at the same age)."""
    warnings = []
    for key, points in series_data.items():
        if not points:
            continue
        last_date, last_rate = points[-1]
        age = (today - date.fromisoformat(last_date)).days
        if age < (STALE_DAYS_LIMIT - STALE_WARN_BEFORE_DAYS):
            continue
        already = state.get(key, {}).get("staleness_warned_for_date")
        if already == last_date:
            continue
        warnings.append({
            "key": key, "label": SERIES[key]["label"], "last_date": last_date,
            "last_rate": last_rate, "age": age,
            "days_to_stale": STALE_DAYS_LIMIT - age,
        })
    return warnings


def _heartbeat_lines(series_data, today):
    """Quiet-heartbeat status line per series: last anchor date/rate + age in days."""
    lines = []
    for key, points in series_data.items():
        label = SERIES[key]["label"]
        if not points:
            lines.append(f"- {label}: KHÔNG CÓ DỮ LIỆU")
            continue
        last_date, last_rate = points[-1]
        age = (today - date.fromisoformat(last_date)).days
        lines.append(f"- {label}: {last_rate:g}%/năm (hiệu lực {last_date}, {age}d trước)")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true",
                    help="print only, never notify/post bus event/write state")
    args = ap.parse_args()

    today = datetime.now(_ICT).date()
    series_data = _load_series()
    state = _load_state()
    declines = check_declines(series_data, state)
    staleness = check_staleness(series_data, state, today)

    print("=== deposit_cctg_trend_check ===")
    for line in _heartbeat_lines(series_data, today):
        print(line)

    if not declines and not staleness:
        print("Không phát hiện xu hướng hạ mới, không có cảnh báo stale mới (hoặc đã báo rồi).")
        return 0

    for d in declines:
        msg = (
            f"⚠️ XU HƯỚNG HẠ — {d['label']} ({d['tenor']}): "
            f"{d['prev_rate']:g}%/năm ({d['prev_date']}) → {d['new_rate']:g}%/năm ({d['new_date']}). "
            f"Park 0% KHÔNG tự đổi, chờ user quyết định."
        )
        print(msg)
        if args.dry_run:
            continue

        subprocess.run([os.path.join(MIKE_BIN, "notify.sh"), msg], check=False)
        payload = json.dumps({
            "series": d["key"], "tenor": d["tenor"],
            "prev_date": d["prev_date"], "prev_rate": d["prev_rate"],
            "new_date": d["new_date"], "new_rate": d["new_rate"],
            "note": "park 0% khong tu doi, cho user"
        }, ensure_ascii=False)
        subprocess.run([
            os.path.join(MIKE_BIN, "append_event.sh"), "Taylor", "finding",
            f"deposit-cctg-trend-decline-{d['key']}", payload,
        ], check=False)

        state.setdefault(d["key"], {})["alerted_pair"] = [
            d["prev_date"], d["prev_rate"], d["new_date"], d["new_rate"]]

    for w in staleness:
        msg = (
            f"⏰ DỮ LIỆU SẮP STALE — {w['label']}: mốc gần nhất {w['last_date']} "
            f"({w['last_rate']:g}%/năm), đã {w['age']}d, còn {w['days_to_stale']}d nữa tới "
            f"ngưỡng stale ({STALE_DAYS_LIMIT}d). Cần xác nhận/cập nhật trước khi stale."
        )
        print(msg)
        if args.dry_run:
            continue

        subprocess.run([os.path.join(MIKE_BIN, "notify.sh"), msg], check=False)
        state.setdefault(w["key"], {})["staleness_warned_for_date"] = w["last_date"]

    if not args.dry_run:
        _write_state_atomic(state)
    return 0


if __name__ == "__main__":
    sys.exit(main())
