#!/usr/bin/env python3
"""Selfcheck cho bin/wake_thread.sh — offline, không chạm API thật.

Thay khối transport (`python3 - ... << 'PY' ... PY`, gọi urllib tới
127.0.0.1:8199/api/tasks) bằng một khối giả in ra dòng `SENT<TAB>json` thay vì
gọi mạng thật, neo bằng chuỗi tìm-thấy-hay-fail-loud (đổi transport mà quên
sửa test thì test CHẾT, không PASS giả — cùng mẫu với
notify_thread_argswap_selfcheck.py).

Verify tích hợp thật (POST → GET xác nhận record → DELETE dọn) đã chạy tay
1 lần khi viết script (xem commit message) — KHÔNG lặp lại ở đây: một selfcheck
tự động không được mutate task table sản xuất mỗi lần chạy (§23 coding_guidelines
— "selfcheck không được assert lên trạng thái SỐNG").

Chạy: python3 mike/bin/wake_thread_selfcheck.py
"""
import json
import os
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "bin", "wake_thread.sh")

ANCHOR_START = "if ! out=\"$(python3 - \"$thread_id\" \"$prompt\" \"$name_suffix\" << 'PY' 2>&1"
ANCHOR_END = "\nPY\n)\"; then"

FAKE_TRANSPORT_OK = (
    "if ! out=\"$(python3 - \"$thread_id\" \"$prompt\" \"$name_suffix\" << 'PY' 2>&1\n"
    "import json, sys\n"
    "print('SENT\\t' + json.dumps({\n"
    "    'name': f'dispatch-wake-{sys.argv[3]}',\n"
    "    'prompt': sys.argv[2],\n"
    "    'thread_id': int(sys.argv[1]),\n"
    "    'id': 4242,\n"
    "}))\n"
    "PY\n)\"; then"
)

# Body 201 thật chỉ có {"status":"created","id":N} — không có name/prompt. Dùng bản này cho
# các ca kiểm log thành công để task_id được trích từ ĐÚNG hình dạng production.
FAKE_TRANSPORT_REAL_BODY = (
    "if ! out=\"$(python3 - \"$thread_id\" \"$prompt\" \"$name_suffix\" << 'PY' 2>&1\n"
    "import json\n"
    "print(json.dumps({'status': 'created', 'id': 4242}))\n"
    "PY\n)\"; then"
)

# Body không phải JSON (proxy chen vào, API đổi định dạng): vẫn phải ghi SUCCESS, task_id='?'.
FAKE_TRANSPORT_JUNK_BODY = (
    "if ! out=\"$(python3 - \"$thread_id\" \"$prompt\" \"$name_suffix\" << 'PY' 2>&1\n"
    "print('<html>200 OK</html>')\n"
    "PY\n)\"; then"
)

FAKE_TRANSPORT_FAIL = (
    "if ! out=\"$(python3 - \"$thread_id\" \"$prompt\" \"$name_suffix\" << 'PY' 2>&1\n"
    "import sys\n"
    "print('unreachable: [Errno 111] Connection refused', file=sys.stderr)\n"
    "sys.exit(1)\n"
    "PY\n)\"; then"
)

fails = []
passes = []


def check(name, cond, detail=""):
    (passes if cond else fails).append(name)
    print(f"{'PASS' if cond else 'FAIL'} {name}" + (f"  — {detail}" if detail and not cond else ""))


def build_root(fake_transport):
    script_text = open(SRC, encoding="utf-8").read()
    i = script_text.find(ANCHOR_START)
    if i < 0:
        raise SystemExit(
            f"FATAL: khong tim thay neo transport {ANCHOR_START!r} trong wake_thread.sh — "
            "transport da doi, SUA SELFCHECK NAY thay vi bo qua."
        )
    j = script_text.find(ANCHOR_END, i)
    if j < 0:
        raise SystemExit("FATAL: khong tim thay het khoi transport sau neo.")
    patched = script_text[:i] + fake_transport + script_text[j + len(ANCHOR_END):]

    d = tempfile.mkdtemp(prefix="wt_selfcheck_")
    os.makedirs(os.path.join(d, "bin"))
    p = os.path.join(d, "bin", "wake_thread.sh")
    with open(p, "w", encoding="utf-8") as f:
        f.write(patched)
    os.chmod(p, 0o755)
    return d


def run(root, args, env=None):
    r = subprocess.run(
        ["bash", os.path.join(root, "bin", "wake_thread.sh")] + args,
        capture_output=True, text=True, timeout=30,
        env=None if env is None else dict(os.environ, **env),
    )
    log_path = os.path.join(root, "logs", "wake_thread_errors.log")
    logtxt = open(log_path, encoding="utf-8").read() if os.path.exists(log_path) else ""
    return r, logtxt


def ok_log(root):
    """Nội dung logs/wake_thread.log (log push THÀNH CÔNG) — '' nếu chưa có file."""
    p = os.path.join(root, "logs", "wake_thread.log")
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


def sent_payload(stdout):
    for line in stdout.splitlines():
        if line.startswith("SENT\t"):
            return json.loads(line.split("\t", 1)[1])
    return None


def main():
    # 1. Non-numeric thread_id must be rejected BEFORE any network call.
    d = build_root(FAKE_TRANSPORT_OK)
    r, log = run(d, ["not-a-number", "hello"])
    check(
        "1 non-numeric thread_id: rejected, no network attempt",
        r.returncode == 1 and sent_payload(r.stdout) is None,
        f"rc={r.returncode} stdout={r.stdout!r}",
    )

    # 2. Valid call: payload carries thread_id/prompt/name_suffix through untouched —
    #    including the exact backtick/quote content that broke a real dispatch prompt
    #    2026-08-15 (job Taylor_20260815_004105) when interpolated into a bash string
    #    instead of passed as argv. argv-passing here must not repeat that bug.
    tricky_prompt = "Job done: `_limit_price` = anchor/1.04, status=\"ok\""
    r, log = run(d, ["999999001", tricky_prompt, "job-abc123"])
    payload = sent_payload(r.stdout)
    check(
        "2 valid call: exit 0",
        r.returncode == 0,
        f"rc={r.returncode} stdout={r.stdout!r} stderr={r.stderr!r}",
    )
    check(
        "2b valid call: prompt passed through byte-for-byte (backtick/quote safe)",
        payload is not None and payload.get("prompt") == tricky_prompt,
        f"payload={payload}",
    )
    check(
        "2c valid call: thread_id is int, task name carries the suffix",
        payload is not None
        and payload.get("thread_id") == 999999001
        and payload.get("name") == "dispatch-wake-job-abc123",
        f"payload={payload}",
    )
    check("2d valid call: no error log written", log == "", log[:200])

    # 3. Missing name_suffix: script must synthesize one (date +%s%N) rather than error.
    r, _ = run(d, ["999999001", "hello"])
    payload = sent_payload(r.stdout)
    check(
        "3 no explicit suffix: auto-generated, still succeeds",
        r.returncode == 0 and payload is not None and payload["name"].startswith("dispatch-wake-"),
        f"rc={r.returncode} payload={payload}",
    )

    # 4. Transport failure (API unreachable) must fail soft: exit 1, log the error,
    #    never raise past `set -e` in the caller (dispatch.sh's _bg_wrapper always
    #    wraps this call with `|| true`, but the script itself must not explode).
    d2 = build_root(FAKE_TRANSPORT_FAIL)
    r, log = run(d2, ["999999001", "hello"])
    check(
        "4 transport failure: exits 1 (soft-fail), does not crash",
        r.returncode == 1,
        f"rc={r.returncode} stderr={r.stderr!r}",
    )
    check(
        "4b transport failure: logged to wake_thread_errors.log",
        "unreachable" in log,
        log[:200],
    )
    check(
        "4c transport failure: does NOT write a SUCCESS line (RED control)",
        ok_log(d2) == "",
        ok_log(d2)[:200],
    )

    # 5. Push THÀNH CÔNG phải để lại vết trong logs/wake_thread.log — nếu không, "push chưa
    #    bao giờ chạy" và "push chạy ngon" không phân biệt được từ trong fleet này.
    d3 = build_root(FAKE_TRANSPORT_REAL_BODY)
    r, _ = run(d3, ["999999002", "hello", "Wags_20260817_191153"])
    line = ok_log(d3).strip()
    check("5 push OK: exit 0", r.returncode == 0, f"rc={r.returncode} stderr={r.stderr!r}")
    # 5e. Dấu thời gian phải NEO ICT bất kể TZ của tiến trình gọi (§16, thêm 2026-08-20).
    #     wake_thread.sh chạy cả từ crontab (TZ=ICT) lẫn từ service ccdb (không export TZ);
    #     logs/wake_thread.log đã có dòng `+00:00` thật lẫn giữa `+07:00`, mà daily_retro.sh
    #     đếm push success-rate theo tiền tố ngày ICT ⇒ lệch ngày, lệch tỷ lệ.
    d3b = build_root(FAKE_TRANSPORT_REAL_BODY)
    run(d3b, ["999999009", "hello", "tzcheck"], env={"TZ": "UTC"})
    tzline = ok_log(d3b).strip()
    check(
        "5e dấu thời gian log NEO +07:00 kể cả khi TZ=UTC",
        "+07:00" in tzline.split()[0],
        f"line={tzline!r}",
    )
    d3c = build_root(FAKE_TRANSPORT_FAIL)
    _, errtxt = run(d3c, ["999999010", "hello", "tzcheck"], env={"TZ": "UTC"})
    check(
        "5f dấu thời gian log LỖI cũng neo +07:00 khi TZ=UTC",
        bool(errtxt.strip()) and "+07:00" in errtxt.strip().split()[0],
        f"err={errtxt.strip()!r}",
    )
    check(
        "5b push OK: 1 dòng SUCCESS, đủ job_id + thread_id + task_id",
        len(ok_log(d3).splitlines()) == 1
        and "SUCCESS" in line
        and "job_id=Wags_20260817_191153" in line
        and "thread_id=999999002" in line
        and "task_id=4242" in line,
        f"line={line!r}",
    )
    check(
        "5c push OK: dòng mở đầu bằng timestamp ISO (cùng dạng log lỗi)",
        bool(line) and line.split()[0][:4].isdigit() and "T" in line.split()[0],
        f"line={line!r}",
    )
    # Gọi lần 2: append chứ không đè — 1 push = 1 dòng.
    run(d3, ["999999003", "hello", "job-2"])
    check(
        "5d push thứ hai: APPEND (2 dòng), không ghi đè",
        len(ok_log(d3).splitlines()) == 2,
        ok_log(d3)[:300],
    )

    # 6. Body lạ (không JSON) vẫn phải ghi SUCCESS với task_id='?' — mất id thì đừng mất luôn
    #    bằng chứng là push đã tới.
    d4 = build_root(FAKE_TRANSPORT_JUNK_BODY)
    r, _ = run(d4, ["999999004", "hello", "job-junk"])
    line4 = ok_log(d4).strip()
    check(
        "6 body không phải JSON: vẫn exit 0 và vẫn ghi SUCCESS với task_id=?",
        r.returncode == 0 and "SUCCESS" in line4 and "task_id=?" in line4,
        f"rc={r.returncode} line={line4!r}",
    )

    print(f"\n{len(passes)} PASS, {len(fails)} FAIL")
    if fails:
        print("FAILED:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
