#!/usr/bin/env python3
"""Ensure interactive Mike jobs never strand silently after completion/resume.

Runs detached from dispatch.sh (_bg_wrapper_run exit) as a safety net alongside
ScheduleWakeup and _preempt_wakeup():
  - Closes Hole B: job finishes milliseconds after dispatch while Mike's turn is still
    running (so ccdb hasn't saved ScheduleWakeup to SQLite yet). Once saved, preempts
    next_run_at to NOW instead of letting Mike sleep the full delay.
  - Closes Hole C: skips premature wakeups while a live Mike sibling job is still running
    in the same Discord thread, leaving the last sibling to wake Mike cleanly.
  - Closes Hole D: after usage_limit/max_turns auto-resume or lost ScheduleWakeup rows,
    if wakeup_ack == "ack", replied_at is empty, no sibling is running, no pending
    one-shot task exists, and the thread session is no longer actively running, invokes
    bin/wake_thread.sh with a claim-reply prompt so Mike delivers the final report.

Fail-open everywhere; opt-out via MIKE_ENSURE_WAKEUP=off.
"""
from __future__ import annotations

import glob
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
DEFAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_API = "http://127.0.0.1:8199"
HB_LIVE_BOUND_S = 1800
RESCUE_PREEMPT_GRACE_S = 15
_ORIGIN_JOB_RE = re.compile(r"job\s+(?:gốc|goc)=([A-Za-z0-9_]+)")


def _log(root: str, msg: str) -> None:
    """Append a single diagnostic line with explicit ICT timestamp."""
    try:
        log_path = os.path.join(root, "logs", "ensure_followup_wakeup.log")
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        ts = datetime.now(ICT).isoformat(timespec="seconds")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"{ts} {msg}\n")
    except Exception:
        pass


def _load_json(path: str) -> dict | None:
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _as_int(val: object, default: int = 0) -> int:
    try:
        return int(float(val))  # handles numeric strings & floats cleanly
    except (TypeError, ValueError):
        return default


def _followup_meta(jobs_dir: str, job_id: str) -> tuple[str, str, str]:
    """Return (from_agent, wakeup_ack, replied_at) following resume/fallback chains."""
    cur = _load_json(os.path.join(jobs_dir, f"{job_id}.json"))
    if not cur:
        return "", "", ""
    replied_at = str(cur.get("replied_at") or "").strip()
    from_agent = str(cur.get("from") or "").strip()
    ack = str(cur.get("wakeup_ack") or "").strip()

    seen = {job_id}
    probe = cur
    for _ in range(5):
        if ack and from_agent:
            break
        m = _ORIGIN_JOB_RE.search(str(probe.get("prompt_summary") or ""))
        if not m:
            break
        parent_id = m.group(1)
        if parent_id in seen:
            break
        seen.add(parent_id)
        parent = _load_json(os.path.join(jobs_dir, f"{parent_id}.json"))
        if not parent:
            break
        if not ack:
            ack = str(parent.get("wakeup_ack") or "").strip()
        if not from_agent:
            from_agent = str(parent.get("from") or "").strip()
        probe = parent
    return from_agent, ack, replied_at


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False


def _has_live_sibling(jobs_dir: str, job_id: str, tid: str, now_s: int) -> str | None:
    """Return job_id of a genuinely live Mike sibling in the same thread, if any."""
    for fp in glob.glob(os.path.join(jobs_dir, "*.json")):
        rec = _load_json(fp)
        if not rec:
            continue
        sib_id = str(rec.get("job_id") or "")
        if not sib_id or sib_id == job_id:
            continue
        if rec.get("from") != "Mike" or str(rec.get("discord_thread_id") or "") != tid:
            continue
        if rec.get("status") not in ("running", "retrying"):
            continue
        if str(rec.get("wakeup_ack") or "") == "nofollow":
            continue
        # Guard against ancient un-reaped zombie records blocking followups forever.
        last_beat = max(
            _as_int(rec.get("hb_ts")),
            _as_int(rec.get("last_hb")),
            _as_int(rec.get("started_at")),
        )
        if last_beat > 0 and (now_s - last_beat) > HB_LIVE_BOUND_S:
            continue
        pid = _as_int(rec.get("pid"))
        if pid > 0 and not _pid_alive(pid) and (now_s - _as_int(rec.get("started_at"), now_s)) > 120:
            continue
        return sib_id
    return None


def _http_json(url: str, method: str = "GET", payload: dict | None = None, timeout: float = 5.0) -> dict | None:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if data is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace"))
        return body if isinstance(body, dict) else None
    except Exception:
        return None


def _find_pending_wakeup(tasks: list[dict], tid: str) -> dict | None:
    name = f"wakeup-thread-{tid}"
    for t in tasks:
        if not isinstance(t, dict):
            continue
        if t.get("name") == name:
            return t
        if t.get("enabled") and t.get("one_shot") and str(t.get("thread_id") or "") == tid:
            return t
    return None


def _is_session_running(api: str, tid: str) -> bool | None:
    """Return True if tid session is running, False if idle/absent, None if unknown/error."""
    body = _http_json(f"{api}/api/sessions")
    if not body or not isinstance(body.get("sessions"), list):
        return None
    for s in body["sessions"]:
        if isinstance(s, dict) and str(s.get("thread_id") or "") == tid:
            return s.get("state") == "running"
    return False


def _parse_delays(raw: str) -> list[float]:
    out: list[float] = []
    for part in raw.split(","):
        part = part.strip()
        if not part:
            continue
        try:
            out.append(max(0.0, float(part)))
        except ValueError:
            pass
    return out or [5.0, 20.0, 45.0, 60.0]


def _wake_rescue(root: str, job_id: str, tid: str) -> bool:
    wake_bin = os.path.join(root, "bin", "wake_thread.sh")
    if not os.path.isfile(wake_bin):
        _log(root, f"SKIP no_wake_bin job={job_id} thread={tid}")
        return False
    prompt = (
        f"Đầu tiên: {root}/bin/jobs.sh claim-reply {job_id} → "
        "exit 1 → ScheduleWakeup(noop:true,stop:true), DỪNG. "
        "exit 0 → job đã xong trong lúc chưa có wakeup hoạt động — đọc kết quả "
        f"({root}/bin/jobs.sh status {job_id} / log) và gửi báo cáo cuối cùng cho user. "
        "exit 2 → báo job record thiếu, đừng im lặng."
    )
    try:
        r = subprocess.run(
            ["bash", wake_bin, tid, prompt, f"{job_id}-ensure"],
            capture_output=True,
            text=True,
            timeout=20,
        )
        ok = r.returncode == 0
        _log(root, f"RESCUE {'OK' if ok else 'FAIL'} job={job_id} thread={tid} rc={r.returncode}")
        return ok
    except Exception as exc:
        _log(root, f"RESCUE ERR job={job_id} thread={tid} err={exc}")
        return False


def main() -> int:
    if os.environ.get("MIKE_ENSURE_WAKEUP") == "off":
        return 0
    if len(sys.argv) < 3:
        return 0

    job_id, tid = sys.argv[1].strip(), sys.argv[2].strip()
    if not job_id or not tid.isdigit():
        return 0

    root = os.environ.get("MIKE_ROOT") or DEFAULT_ROOT
    jobs_dir = os.path.join(root, "bus", "jobs")
    api = (os.environ.get("CCDB_API_URL") or DEFAULT_API).rstrip("/")
    delays = _parse_delays(os.environ.get("ENSURE_WAKEUP_DELAYS", "5,20,45,60"))

    from_agent, ack, replied_at = _followup_meta(jobs_dir, job_id)
    if ack == "nofollow" or replied_at or from_agent not in ("Mike", ""):
        return 0

    # Non-interactive/cron dispatches without wakeup_ack only get 1 quick preempt check
    # so we never unexpectedly open a new interactive session for background cron jobs.
    max_checks = len(delays) if ack == "ack" else 1

    for idx in range(max_checks):
        wait_s = delays[idx]
        if wait_s > 0:
            time.sleep(wait_s)

        _, _, current_replied = _followup_meta(jobs_dir, job_id)
        if current_replied:
            _log(root, f"SKIP already_replied job={job_id} thread={tid} idx={idx}")
            return 0

        now_s = int(time.time())
        sib = _has_live_sibling(jobs_dir, job_id, tid, now_s)
        if sib:
            _log(root, f"DEFER live_sibling={sib} job={job_id} thread={tid} idx={idx}")
            return 0

        tasks_body = _http_json(f"{api}/api/tasks")
        if tasks_body is None or not isinstance(tasks_body.get("tasks"), list):
            _log(root, f"WARN tasks_api_unreachable job={job_id} thread={tid} idx={idx}")
            continue

        row = _find_pending_wakeup(tasks_body["tasks"], tid)
        if row is not None:
            next_run = _as_int(row.get("next_run_at"), 0)
            if next_run == 0 or next_run > now_s + RESCUE_PREEMPT_GRACE_S:
                patched = _http_json(
                    f"{api}/api/tasks/{row['id']}",
                    method="PATCH",
                    payload={"next_run_at": now_s},
                )
                _log(
                    root,
                    f"PREEMPT {'OK' if patched is not None else 'ERR'} "
                    f"job={job_id} thread={tid} task={row.get('id')} idx={idx}",
                )
            else:
                _log(root, f"SKIP pending_due_soon job={job_id} thread={tid} task={row.get('id')} idx={idx}")
            return 0

        if ack != "ack":
            return 0

        sess_running = _is_session_running(api, tid)
        if sess_running is True:
            # Mike is still mid-turn (hasn't saved ScheduleWakeup to SQLite yet); retry later.
            continue
        if sess_running is None and idx == 0 and max_checks > 1:
            continue
        if idx >= 1 or max_checks == 1:
            _wake_rescue(root, job_id, tid)
            return 0

    if ack == "ack":
        _log(root, f"END session_still_running_stop_hook_covers job={job_id} thread={tid}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
