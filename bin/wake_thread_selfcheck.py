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
    "}))\n"
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


def run(root, args):
    r = subprocess.run(
        ["bash", os.path.join(root, "bin", "wake_thread.sh")] + args,
        capture_output=True, text=True, timeout=30,
    )
    log_path = os.path.join(root, "logs", "wake_thread_errors.log")
    logtxt = open(log_path, encoding="utf-8").read() if os.path.exists(log_path) else ""
    return r, logtxt


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

    print(f"\n{len(passes)} PASS, {len(fails)} FAIL")
    if fails:
        print("FAILED:", fails)
        sys.exit(1)


if __name__ == "__main__":
    main()
