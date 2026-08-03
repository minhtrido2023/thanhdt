#!/usr/bin/env python3
"""resume_pending.py — cron poller (every 10 min, see crontab).

When dispatch.sh's _maybe_schedule_usage_resume detects a headless job failed because the
ACCOUNT's shared rolling 5-hour usage window (usage_watch.py) was exhausted — not because
the task itself is broken — it writes bus/pending_resumes/<job_id>.json instead of treating
it as a normal failure: {agent, prompt, orig_job_id, from, resume_at, resume_count, kind,
model, effort, max_turns}. This poller fires any record whose resume_at has passed by
re-dispatching the SAME agent (preserving its original model/effort/max_turns — 2026-08-02
fix; previously silently dropped back to CLI defaults on every resume) with a "continue
where you left off" prompt, so a long research task recovers on its own instead of the user
having to come back and manually re-prompt (feature request 2026-07-03).

Two `kind`s (2026-08-02, added alongside the original usage_limit kind):
  - "usage_limit" (default, back-compat with records that predate the `kind` field): the
    account's 5h window was exhausted — resume_at is set to the reset time + buffer.
  - "max_turns": the dispatch ran out of tool-call turns (--max-turns), a deterministic
    budget signal, not a transient one — dispatch.sh's own in-loop retry already bumped the
    ceiling once; this only fires once ALL in-process attempts are spent, so resume_at is
    ~immediate (no reset window to wait for) and the `max_turns` field carries the next,
    further-bumped ceiling to pass through on this resume.

One-shot per record: removed BEFORE firing, not after — so a slow/hung dispatch call can't
be double-fired by the next cron tick. If the resumed run ALSO hits the same limit again,
dispatch.sh writes a brand-new pending record (with resume_count+1) — nothing is lost, and
dispatch.sh's own cap (DISPATCH_MAX_USAGE_RESUMES / DISPATCH_MAX_TURNS_RESUMES) eventually
stops the chain if it turns out not to be a real transient situation.

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
    kind = rec.get("kind") or "usage_limit"
    if not agent:
        log("SKIP malformed (no agent): %s" % fp)
        return
    if kind == "max_turns":
        resume_prompt = (
            "[RESUME sau max-turns #%d, job gốc=%s] Task trước đó bị DỪNG GIỮA CHỪNG vì hết "
            "lượt tool-call (--max-turns), KHÔNG phải task lỗi — trần đã được NÂNG cho lần "
            "chạy này. Đọc lại working memory (kb/memory/%s.md) + bus event gần nhất của "
            "chính bạn (bus/inbox/%s.jsonl) + chạy 'git status'/'git diff' ở mọi repo có thể "
            "đã sửa để biết đang làm dở gì, rồi TIẾP TỤC từ đó — KHÔNG bắt đầu lại từ đầu, "
            "KHÔNG lặp lại việc đã xong. Prompt gốc: %s"
        ) % (count, orig_job, agent, agent, prompt)
    else:
        resume_prompt = (
            "[RESUME sau usage-limit #%d, job gốc=%s] Task trước đó bị DỪNG GIỮA CHỪNG vì tài "
            "khoản hết usage limit 5h (không phải task lỗi) — cửa sổ giờ đã reset. Đọc lại "
            "working memory (kb/memory/%s.md) + bus event gần nhất của chính bạn "
            "(bus/inbox/%s.jsonl) để biết đang làm dở gì, rồi TIẾP TỤC từ đó — KHÔNG bắt đầu "
            "lại từ đầu, KHÔNG lặp lại việc đã xong. Prompt gốc: %s"
        ) % (count, orig_job, agent, agent, prompt)
    env = dict(os.environ, DISPATCH_FROM=frm)
    # Ghim lại ĐÚNG topic Discord của job gốc (fix 2026-07-22). Cron không có
    # DISCORD_THREAD_ID nên nếu không truyền --thread, job resume rơi về con trỏ global
    # "topic Mike mở phiên gần nhất" = topic user đang đọc. Job record của job gốc đã lưu
    # discord_thread_id từ lúc dispatch → đọc thẳng từ đó, không cần thêm field mới.
    argv = [DISPATCH, agent, resume_prompt, "--bg"]
    # Preserve model/effort/max_turns across the resume (fix 2026-08-02 — previously
    # ANY resume, including usage_limit ones, silently dropped back to CLI defaults,
    # which for an opus/high-effort task risks re-hitting the exact ceiling it's
    # resuming from). max_turns only makes sense to force for a max_turns-kind resume;
    # for usage_limit, the original run's own --max-turns wasn't the failure cause, so
    # only carry it if explicitly present too (harmless either way — same value as before).
    # provider PHẢI đi cùng model: một job opencode mà resume không kèm --provider sẽ chạy
    # trên claude với --model của opencode → cổng provider từ chối (exit 1) → task mất im
    # (record đã bị xoá trước khi fire). Bản ghi cũ không có field này → giữ nguyên hành vi
    # cũ (default_provider = claude), đúng vì mọi job trước 2026-08-03 đều là claude.
    if rec.get("provider"):
        argv += ["--provider", str(rec["provider"])]
    if rec.get("model"):
        argv += ["--model", str(rec["model"])]
    if rec.get("effort"):
        argv += ["--effort", str(rec["effort"])]
    if rec.get("max_turns"):
        argv += ["--max-turns", str(rec["max_turns"])]
    try:
        with open(os.path.join(ROOT, "bus", "jobs", "%s.json" % orig_job),
                  encoding="utf-8") as f:
            tid = str(json.load(f).get("discord_thread_id") or "")
        if tid:
            argv += ["--thread", tid]
    except Exception:
        pass  # job record cũ/mất → giữ hành vi cũ (ambient/global), không chặn resume
    try:
        r = subprocess.run(argv, env=env,
                           capture_output=True, text=True, timeout=30)
    except Exception as e:
        log("FAILED to resume %s (orig_job=%s): %s" % (agent, orig_job, e))
        return False
    # PHẢI kiểm returncode (sửa 2026-08-03, arch-reviewer F9). Trước đây rc bị BỎ QUA và
    # notify "được tự động resume" bắn VÔ ĐIỀU KIỆN — cộng với việc record bị xoá TRƯỚC khi
    # fire, một dispatch fail = task chết hẳn TRONG KHI user nhận tin báo thành công. Đó là
    # kiểu hỏng tệ nhất: mất việc + mất cả tín hiệu là đã mất việc.
    if r.returncode != 0:
        log("DISPATCH-FAILED %s (orig_job=%s, attempt #%d, rc=%d) argv=%s -> %s"
            % (agent, orig_job, count, r.returncode, argv[3:],
               (r.stderr.strip() or r.stdout.strip())[:300]))
        return False
    log("RESUMED %s (orig_job=%s, attempt #%d) -> %s"
        % (agent, orig_job, count, r.stdout.strip()[:200] or r.stderr.strip()[:200]))
    if os.path.isfile(NOTIFY):
        reason = "hết turn budget, trần đã nâng" if kind == "max_turns" else "usage limit đã reset"
        try:
            subprocess.Popen([NOTIFY, "[auto-resume] %s: %s, task "
                              "(job gốc=%s, lần thử #%d) được tự động resume." % (agent, reason, orig_job, count)],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    return True


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
        if fire(fp, rec):
            continue
        # Dispatch KHÔNG chạy được. Record đã bị xoá ở trên (cố ý, chống double-fire), nên
        # nếu dừng ở đây thì task biến mất không dấu vết — đúng lỗ hổng F9. Khôi phục record
        # CÓ TRẦN: thử lại sau 30' tối đa 2 lần, rồi bỏ kèm cảnh báo TO. Có trần để một lỗi
        # cấu hình thường trực (vd provider bị tắt) không thành vòng lặp cron vô hạn.
        nfail = int(rec.get("dispatch_fail_count", 0)) + 1
        agent = rec.get("agent", "?")
        orig_job = rec.get("orig_job_id", "?")
        if nfail <= 2:
            rec["dispatch_fail_count"] = nfail
            rec["resume_at"] = int(now) + 1800
            try:
                tmp = fp + ".tmp"
                with open(tmp, "w", encoding="utf-8") as f:
                    json.dump(rec, f, ensure_ascii=False)
                os.replace(tmp, fp)
                log("RESTORED pending record %s (dispatch_fail_count=%d, thử lại sau 30')" % (fp, nfail))
            except Exception as e:
                log("LOST %s: khôi phục record thất bại: %s" % (fp, e))
        else:
            log("GIVE-UP %s (orig_job=%s): dispatch fail %d lần — BỎ record" % (agent, orig_job, nfail))
            if os.path.isfile(NOTIFY):
                try:
                    subprocess.Popen(
                        [NOTIFY, "⚠️ [auto-resume] %s: KHÔNG resume được task (job gốc=%s) sau "
                                 "%d lần thử — record đã bỏ, TASK NÀY SẼ KHÔNG TỰ CHẠY LẠI. "
                                 "Cần người xem: logs/resume_pending.log" % (agent, orig_job, nfail)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception:
                    pass


if __name__ == "__main__":
    main()
