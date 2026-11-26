#!/usr/bin/env python3
"""Claude Code hook: auto-resume a Discord session killed by the account usage limit.

  stopfail  (StopFailure, matcher rate_limit) -> bus/pending_resumes/session_<thread>.json
  start     (UserPromptSubmit) -> a new turn is running: drop the record, so the cron cannot open a
            second parallel session in this thread. A prompt that is not our own wake also resets
            the attempt counter.
  clear     (Stop, i.e. a turn that succeeded) -> drop the record and the counter
resume_pending.py (cron */10) wakes the thread once resume_at has passed. Never fails the hook.
⚠️ StopFailure hooks are NOT awaited: the CLI exits ~1s later and kills them (measured 2026-11-26,
CLI 2.1.332), so settings.json MUST launch `stopfail` through `setsid -f`.
"""
import json, os, subprocess, sys, time

ROOT = os.environ.get("MIKE_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from limit_reset import reset_epoch

CAP, BUFFER = 3, 600
MARK = "[AUTO-RESUME sau usage-limit]"
PROMPT = (MARK + " Lượt trước của phiên này bị cắt vì hết quota. "
          "Kiểm tra việc đang dở (git status, job, bus) rồi TIẾP TỤC, không làm lại việc đã xong; "
          "không tự thực hiện hành động cần user duyệt. Không còn gì dở thì nói một dòng.")


def _remove(*paths):
    for p in paths:
        if os.path.exists(p):
            os.remove(p)


def main(mode):
    thread = os.environ.get("DISCORD_THREAD_ID", "")
    if not thread.isdigit() or os.environ.get("JOB_ID"):
        return  # job headless đã có đường resume riêng trong dispatch.sh
    rec = os.path.join(ROOT, "bus", "pending_resumes", "session_%s.json" % thread)
    cnt = os.path.join(ROOT, "state", "session_resume", thread)
    if mode == "clear":
        _remove(rec, cnt)
        return
    data = json.load(sys.stdin)
    if mode == "start":
        _remove(rec)
        if MARK not in (data.get("prompt") or ""):
            _remove(cnt)
        return
    if mode != "stopfail" or data.get("error") != "rate_limit":
        return
    reset = reset_epoch(data.get("last_assistant_message") or "")
    if not reset:
        return  # 429 thoáng qua, không có giờ reset -> không đoán
    try:
        n = int(open(cnt).read())
    except Exception:
        n = 0
    n += 1
    notify = os.path.join(ROOT, "bin", "notify_thread.sh")
    if n > CAP:
        subprocess.run([notify, "⚠️ Hết quota lần %d liên tiếp — DỪNG auto-resume, cần nhắn tay." % n, thread], timeout=20)
        return
    for p in (rec, cnt):
        os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(cnt, "w") as f:
        f.write(str(n))
    with open(rec + ".tmp", "w", encoding="utf-8") as f:
        json.dump({"kind": "session", "agent": "Mike", "thread_id": thread, "prompt": PROMPT,
                   "resume_at": reset + BUFFER, "resume_count": n,
                   "orig_job_id": "session_" + thread, "created_at": int(time.time())}, f, ensure_ascii=False)
    os.replace(rec + ".tmp", rec)
    hhmm = time.strftime("%H:%M %d/%m", time.gmtime(reset + BUFFER + 7 * 3600))
    subprocess.run([notify, "⏳ Hết quota — phiên này sẽ TỰ chạy tiếp lúc ~%s ICT (lần %d/%d)." % (hhmm, n, CAP), thread], timeout=20)


if __name__ == "__main__":
    try:
        main(sys.argv[1] if len(sys.argv) > 1 else "")
    except Exception as e:
        print("session_limit_resume: %s" % e, file=sys.stderr)
