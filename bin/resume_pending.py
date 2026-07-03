#!/usr/bin/env python3
"""resume_pending.py — cron poller (every 10 min, see crontab).

When dispatch.sh's _maybe_schedule_usage_resume detects a headless job failed because the
ACCOUNT's shared rolling 5-hour usage window (usage_watch.py) was exhausted — not because
the task itself is broken — it writes bus/pending_resumes/<job_id>.json instead of treating
it as a normal failure: {agent, prompt, orig_job_id, from, resume_at, resume_count}. This
poller fires any record whose resume_at has passed by re-dispatching the SAME agent with a
"continue where you left off" prompt, so a long research task recovers on its own instead of
the user having to come back and manually re-prompt after the limit resets (feature request
2026-07-03).

One-shot per record: removed BEFORE firing, not after — so a slow/hung dispatch call can't
be double-fired by the next cron tick. If the resumed run ALSO hits the limit again,
dispatch.sh writes a brand-new pending record (with resume_count+1) — nothing is lost, and
dispatch.sh's own cap (DISPATCH_MAX_USAGE_RESUMES, default 3) eventually stops the chain if
it turns out not to be a real usage-limit situation.

Always resumes via --bg (nobody is synchronously waiting on a cron-fired continuation).
Never raises — a cron job must not fail loudly into the crontab mailer for a single bad
record; log and move on to the next one.
"""
import glob
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PEND_DIR = os.path.join(ROOT, "bus", "pending_resumes")
LOG = os.path.join(ROOT, "logs", "resume_pending.log")
DISPATCH = os.path.join(ROOT, "bin", "dispatch.sh")
NOTIFY = os.path.join(ROOT, "bin", "notify.sh")


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), msg))
    except Exception:
        pass


def fire(fp, rec):
    agent = rec.get("agent")
    prompt = rec.get("prompt", "")
    orig_job = rec.get("orig_job_id", "?")
    frm = rec.get("from", "user")
    count = rec.get("resume_count", 1)
    if not agent:
        log("SKIP malformed (no agent): %s" % fp)
        return
    resume_prompt = (
        "[RESUME sau usage-limit #%d, job gốc=%s] Task trước đó bị DỪNG GIỮA CHỪNG vì tài "
        "khoản hết usage limit 5h (không phải task lỗi) — cửa sổ giờ đã reset. Đọc lại "
        "working memory (kb/memory/%s.md) + bus event gần nhất của chính bạn "
        "(bus/inbox/%s.jsonl) để biết đang làm dở gì, rồi TIẾP TỤC từ đó — KHÔNG bắt đầu "
        "lại từ đầu, KHÔNG lặp lại việc đã xong. Prompt gốc: %s"
    ) % (count, orig_job, agent, agent, prompt)
    env = dict(os.environ, DISPATCH_FROM=frm)
    try:
        r = subprocess.run([DISPATCH, agent, resume_prompt, "--bg"], env=env,
                           capture_output=True, text=True, timeout=30)
        log("RESUMED %s (orig_job=%s, attempt #%d) -> %s"
            % (agent, orig_job, count, r.stdout.strip()[:200] or r.stderr.strip()[:200]))
    except Exception as e:
        log("FAILED to resume %s (orig_job=%s): %s" % (agent, orig_job, e))
        return
    if os.path.isfile(NOTIFY):
        try:
            subprocess.Popen([NOTIFY, "[auto-resume] %s: usage limit đã reset, task "
                              "(job gốc=%s, lần thử #%d) được tự động resume." % (agent, orig_job, count)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass


def main():
    os.makedirs(PEND_DIR, exist_ok=True)
    now = time.time()
    for fp in sorted(glob.glob(os.path.join(PEND_DIR, "*.json"))):
        try:
            with open(fp, encoding="utf-8") as f:
                rec = json.load(f)
        except Exception as e:
            log("SKIP unreadable %s: %s" % (fp, e))
            continue
        resume_at = rec.get("resume_at", 0)
        if not resume_at or now < resume_at:
            continue
        try:
            os.remove(fp)  # remove BEFORE firing — see module docstring
        except Exception:
            pass
        fire(fp, rec)


if __name__ == "__main__":
    main()
