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
MIKE_STATE_DIR = os.path.join(HERE, "mike", "state")  # NOTIFY_OFF kill-switch lives here
STATE_PATH = os.path.join(HERE, "data", "deposit_cctg_trend_alert_state.json")

SERIES = {
    "big4_12m": {
        "label": "Lãi suất huy động 12 tháng Big-4 (online)",
        "tenor": "12M",
    },
    "cctg_6m": {
        "label": "Chứng chỉ tiền gửi (CCTG) Big-4 (12 tháng cao nhất từ 05/10/2026; trước đó 6 tháng)",
        "tenor": "12M",
    },
}

# Same 45-day threshold macro_killswitch_a_status() uses (deposit_rate_vn.py) — kept as a literal
# here rather than imported, to avoid this script silently tracking a future change to that
# function's default; if the production threshold changes, update both call sites deliberately.
STALE_DAYS_LIMIT = 45
STALE_WARN_BEFORE_DAYS = 10  # start a proactive reminder at day (45-10)=35, not just at day 46

# Same 0.1pp tolerance append_cctg_rate.py's CROSS_SOURCE_TOLERANCE_PP (and, after this round's
# fix 7, append_deposit_rate.py's matching constant) allows between two independently-cited
# sources for the SAME anchor — kept as a literal here rather than imported, same reasoning as
# STALE_DAYS_LIMIT above (avoid this script silently tracking a future change to a writer's
# constant). A decline whose magnitude is <= this band could be pure cross-source measurement
# noise rather than a genuine rate move. Per user directive (coord job Taylor_20261001_061238
# item 5): new < old ALWAYS alerts — this constant only adds a label, it never suppresses.
NOISE_BAND_PP = 0.1


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
            "within_noise_band": (prev_rate - new_rate) <= NOISE_BAND_PP + 1e-9,
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


def _notify_off():
    """Same kill-switch notify.sh itself honors (MIKE_NOTIFY_OFF=1 or mike/state/NOTIFY_OFF) —
    re-implemented here because this script now posts via notify_thread.sh directly (see
    _send_trading_daily docstring for why), and notify_thread.sh has NO kill-switch of its own."""
    if os.environ.get("MIKE_NOTIFY_OFF", "0") == "1":
        return True
    return os.path.exists(os.path.join(MIKE_STATE_DIR, "NOTIFY_OFF"))


def _send_trading_daily(msg):
    """Posts msg to the Trading Daily Discord thread via notify_thread.sh. Returns 'sent',
    'suppressed' (NOTIFY_OFF kill-switch — deliberate, not a failure), or 'failed' (real send
    error — notify_thread.sh's own exit code, under `set -euo pipefail`, is non-zero whenever the
    HTTP POST to the Discord bridge itself raises).

    Switched from notify.sh (coord job Taylor_20261001_061238 item B1 fix): notify.sh ALWAYS
    exits 0 by design (see its own header: "NEVER break the caller") even when the underlying
    Discord send fails or NOTIFY_OFF suppressed it — so its exit code could never be used as
    evidence of real delivery. notify.sh also posts to the wrong channel for this alert (#mikefleet
    "update task", not Trading Daily) — notify_thread.sh with the "trading_daily" topic name
    (kb/discord_channels.json) is both the reliably-observable AND the correctly-routed channel.

    The caller uses the return value to decide whether it is safe to mark alert state as
    delivered — 'suppressed' deliberately does NOT count as delivered either, so a decline/
    staleness alert that happens to land during a NOTIFY_OFF window still reaches the user once
    NOTIFY_OFF is lifted, instead of vanishing silently forever."""
    if _notify_off():
        print(f"  [SUPPRESSED by NOTIFY_OFF] {msg}")
        return "suppressed"
    rc = subprocess.run(
        [os.path.join(MIKE_BIN, "notify_thread.sh"), msg, "trading_daily"],
        check=False).returncode
    if rc == 0:
        return "sent"
    print(f"  [NOTIFY FAILED rc={rc}] {msg}", file=sys.stderr)
    return "failed"


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

    any_failed = False  # becomes True if ANY notify/bus channel failed for real (not NOTIFY_OFF)
                         # -> propagated as a non-zero exit so the wrapper script notifies +
                         # fails loudly instead of silently swallowing a lost alert (item B1 fix)

    for d in declines:
        noise_tag = (" [TRONG DUNG SAI NHIỄU NGUỒN ≤0.1pp — vẫn cần xem, KHÔNG tự nuốt]"
                     if d["within_noise_band"] else "")
        msg = (
            f"⚠️ XU HƯỚNG HẠ{noise_tag} — {d['label']} ({d['tenor']}): "
            f"{d['prev_rate']:g}%/năm ({d['prev_date']}) → {d['new_rate']:g}%/năm ({d['new_date']}). "
            f"Park 0% KHÔNG tự đổi, chờ user quyết định."
        )
        print(msg)
        if args.dry_run:
            continue

        notify_status = _send_trading_daily(msg)
        payload = json.dumps({
            "series": d["key"], "tenor": d["tenor"],
            "prev_date": d["prev_date"], "prev_rate": d["prev_rate"],
            "new_date": d["new_date"], "new_rate": d["new_rate"],
            "within_noise_band": d["within_noise_band"],
            "note": "park 0% khong tu doi, cho user"
        }, ensure_ascii=False)
        bus_rc = subprocess.run([
            os.path.join(MIKE_BIN, "append_event.sh"), "Taylor", "finding",
            f"deposit-cctg-trend-decline-{d['key']}", payload,
        ], check=False).returncode

        # Only mark alerted_pair when BOTH channels confirm: the Discord send actually succeeded
        # (not just "notify.sh never fails") AND the bus finding was actually appended (rc==0).
        # NOTIFY_OFF ('suppressed') deliberately does NOT mark state either — see
        # _send_trading_daily's docstring. Any real failure on either channel -> retry next run.
        if notify_status == "sent" and bus_rc == 0:
            state.setdefault(d["key"], {})["alerted_pair"] = [
                d["prev_date"], d["prev_rate"], d["new_date"], d["new_rate"]]
        elif notify_status == "suppressed" and bus_rc == 0:
            print(f"  state NOT marked (NOTIFY_OFF) — Discord alert will (re-)send next run "
                  f"once NOTIFY_OFF is lifted; bus finding recorded now regardless.")
        else:
            any_failed = True
            print(f"  state NOT marked (notify={notify_status}, bus_rc={bus_rc}) — will retry "
                  f"next run.", file=sys.stderr)

    for w in staleness:
        if w["days_to_stale"] >= 0:
            stale_phrase = f"còn {w['days_to_stale']}d nữa tới ngưỡng stale ({STALE_DAYS_LIMIT}d)"
            icon = "⏰ DỮ LIỆU SẮP STALE"
        else:
            stale_phrase = (f"ĐÃ QUA ngưỡng stale ({STALE_DAYS_LIMIT}d) "
                             f"{-w['days_to_stale']}d rồi")
            icon = "⚠️ DỮ LIỆU ĐÃ STALE"
        msg = (
            f"{icon} — {w['label']}: mốc gần nhất {w['last_date']} "
            f"({w['last_rate']:g}%/năm), đã {w['age']}d, {stale_phrase}. "
            f"Cần xác nhận/cập nhật trước khi stale."
        )
        print(msg)
        if args.dry_run:
            continue

        notify_status = _send_trading_daily(msg)
        if notify_status == "sent":
            state.setdefault(w["key"], {})["staleness_warned_for_date"] = w["last_date"]
        elif notify_status == "suppressed":
            print(f"  state NOT marked (NOTIFY_OFF) — will (re-)send next run once lifted.")
        else:
            any_failed = True
            print(f"  state NOT marked (notify failed) — will retry next run.", file=sys.stderr)

    if not args.dry_run:
        _write_state_atomic(state)
    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
