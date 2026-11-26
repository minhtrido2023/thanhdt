#!/usr/bin/env python3
"""Selfcheck for bin/ensure_followup_wakeup.py (Holes A/B/C/D).

Runs against a local mock CCDB HTTP server and an isolated temp MIKE_ROOT
containing synthetic bus/jobs JSON records and a stub bin/wake_thread.sh.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "ensure_followup_wakeup.py")


class MockState:
    def __init__(self) -> None:
        self.tasks: list[dict] = []
        self.sessions: list[dict] = []
        self.patches: list[tuple[str, dict]] = []
        self.task_seq = 0
        self.polls = 0

    def reset(self) -> None:
        self.tasks = []
        self.sessions = []
        self.patches = []
        self.polls = 0


STATE = MockState()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path.startswith("/api/tasks"):
            STATE.polls += 1
            body = json.dumps({"tasks": STATE.tasks}).encode("utf-8")
        elif self.path.startswith("/api/sessions"):
            body = json.dumps({"sessions": STATE.sessions}).encode("utf-8")
        else:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_PATCH(self) -> None:
        ln = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(ln).decode("utf-8", errors="replace") if ln else "{}"
        payload = json.loads(raw)
        STATE.patches.append((self.path, payload))
        body = json.dumps({"status": "updated"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:
        return


def _write_job(jobs_dir: str, job_id: str, data: dict) -> None:
    os.makedirs(jobs_dir, exist_ok=True)
    with open(os.path.join(jobs_dir, f"{job_id}.json"), "w", encoding="utf-8") as f:
        json.dump(data, f)


def _setup_sandbox(tmp: str) -> tuple[str, str, str]:
    jobs_dir = os.path.join(tmp, "bus", "jobs")
    bin_dir = os.path.join(tmp, "bin")
    wake_log = os.path.join(tmp, "wake_calls.log")
    os.makedirs(jobs_dir, exist_ok=True)
    os.makedirs(bin_dir, exist_ok=True)
    wake_sh = os.path.join(bin_dir, "wake_thread.sh")
    with open(wake_sh, "w", encoding="utf-8") as f:
        f.write(f"#!/usr/bin/env bash\nprintf '%s|%s|%s\\n' \"$1\" \"$2\" \"$3\" >> \"{wake_log}\"\n")
    os.chmod(wake_sh, 0o755)
    return jobs_dir, wake_log, tmp


def _run_ensure(root: str, api: str, job_id: str, tid: str, delays: str = "0.02,0.02") -> int:
    env = dict(os.environ, MIKE_ROOT=root, CCDB_API_URL=api, ENSURE_WAKEUP_DELAYS=delays)
    env.pop("MIKE_ENSURE_WAKEUP", None)
    r = subprocess.run([sys.executable, SCRIPT, job_id, tid], env=env, capture_output=True, text=True, timeout=15)
    return r.returncode


def main() -> int:
    srv = HTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    api = f"http://127.0.0.1:{srv.server_port}"
    tid = "888111222"
    fails: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        print(("PASS " if cond else "FAIL ") + name + (f" ({detail})" if detail and not cond else ""))
        if not cond:
            fails.append(name)

    with tempfile.TemporaryDirectory() as tmp:
        # 1. Delayed ScheduleWakeup saved mid-turn -> preempted
        STATE.reset()
        jobs_dir, wake_log, root = _setup_sandbox(tmp)
        _write_job(jobs_dir, "J1", {"job_id": "J1", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "ack", "status": "done"})
        STATE.sessions = [{"thread_id": int(tid), "state": "running"}]

        def inject_later() -> None:
            time.sleep(0.08)
            STATE.tasks = [{"id": 501, "name": f"wakeup-thread-{tid}", "enabled": True, "one_shot": True, "thread_id": int(tid), "next_run_at": time.time() + 900}]
            STATE.sessions = [{"thread_id": int(tid), "state": "idle"}]

        threading.Thread(target=inject_later, daemon=True).start()
        rc = _run_ensure(root, api, "J1", tid, "0.04,0.08,0.08")
        check("1_delayed_wakeup_preempted", rc == 0 and len(STATE.patches) == 1 and STATE.patches[0][0] == "/api/tasks/501" and not os.path.exists(wake_log), str(STATE.patches))

    with tempfile.TemporaryDirectory() as tmp:
        # 2. wakeup_ack=ack + idle session + no task -> wake_thread.sh rescue fires
        STATE.reset()
        jobs_dir, wake_log, root = _setup_sandbox(tmp)
        _write_job(jobs_dir, "J2", {"job_id": "J2", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "ack", "status": "done"})
        STATE.sessions = [{"thread_id": int(tid), "state": "idle"}]
        rc = _run_ensure(root, api, "J2", tid, "0.02,0.02,0.02")
        woke = open(wake_log, encoding="utf-8").read() if os.path.exists(wake_log) else ""
        check("2_missing_wakeup_rescued", rc == 0 and f"{tid}|" in woke and "claim-reply J2" in woke and "J2-ensure" in woke, woke)

    with tempfile.TemporaryDirectory() as tmp:
        # 3. Already replied -> no-op
        STATE.reset()
        jobs_dir, wake_log, root = _setup_sandbox(tmp)
        _write_job(jobs_dir, "J3", {"job_id": "J3", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "ack", "replied_at": "1700000000", "status": "done"})
        rc = _run_ensure(root, api, "J3", tid, "0.02,0.02")
        check("3_already_replied_noop", rc == 0 and not STATE.patches and not os.path.exists(wake_log) and STATE.polls == 0)

    with tempfile.TemporaryDirectory() as tmp:
        # 4. wakeup_ack=nofollow -> no-op
        STATE.reset()
        jobs_dir, wake_log, root = _setup_sandbox(tmp)
        _write_job(jobs_dir, "J4", {"job_id": "J4", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "nofollow", "status": "done"})
        rc = _run_ensure(root, api, "J4", tid, "0.02,0.02")
        check("4_nofollow_noop", rc == 0 and not STATE.patches and not os.path.exists(wake_log) and STATE.polls == 0)

    with tempfile.TemporaryDirectory() as tmp:
        # 5. Live sibling running on same thread -> defer without waking
        STATE.reset()
        jobs_dir, wake_log, root = _setup_sandbox(tmp)
        now_s = int(time.time())
        _write_job(jobs_dir, "J5", {"job_id": "J5", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "ack", "status": "done"})
        _write_job(jobs_dir, "J5_sib", {"job_id": "J5_sib", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "ack", "status": "running", "started_at": now_s, "hb_ts": now_s, "pid": os.getpid()})
        rc = _run_ensure(root, api, "J5", tid, "0.02,0.02")
        check("5_live_sibling_defers", rc == 0 and not STATE.patches and not os.path.exists(wake_log) and STATE.polls == 0)

    with tempfile.TemporaryDirectory() as tmp:
        # 6. Auto-resume inherits wakeup_ack=ack from original job chain -> rescues
        STATE.reset()
        jobs_dir, wake_log, root = _setup_sandbox(tmp)
        _write_job(jobs_dir, "Orig_01", {"job_id": "Orig_01", "from": "Mike", "discord_thread_id": tid, "wakeup_ack": "ack", "status": "usage_limited"})
        _write_job(jobs_dir, "Res_02", {"job_id": "Res_02", "from": "Mike", "discord_thread_id": tid, "prompt_summary": "[RESUME sau usage-limit #1, job gốc=Orig_01] foo", "status": "done"})
        STATE.sessions = [{"thread_id": int(tid), "state": "idle"}]
        rc = _run_ensure(root, api, "Res_02", tid, "0.02,0.02,0.02")
        woke = open(wake_log, encoding="utf-8").read() if os.path.exists(wake_log) else ""
        check("6_resume_inherits_ack_rescues", rc == 0 and "claim-reply Res_02" in woke, woke)

    print("ALL PASS" if not fails else f"{len(fails)} FAIL: {fails}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
