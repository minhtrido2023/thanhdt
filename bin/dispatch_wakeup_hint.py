#!/usr/bin/env python3
"""dispatch_wakeup_hint.py --job JOB_ID [--delay SEC] [--from AGENT]

In (stdout) cảnh báo "CHƯA đặt ScheduleWakeup" cho một job `dispatch.sh --bg` vừa phát —
prevention (b) của retro 2026-10-24 (Pattern "wakeup-gate-not-mechanical": 1/3 lượt --bg bỏ
quên wakeup dù MIKE.md §8 ghi BẮT BUỘC khi còn bước phụ thuộc kết quả).

CƠ HỌC, KHÔNG CHẶN: dispatch.sh gọi với `>&2 || true`. Script không biết lượt gọi có bước phụ
thuộc hay không nên nhắc vô điều kiện; tắt khi chắc chắn không có bước phụ thuộc bằng
`DISPATCH_NO_DEPENDENT_STEP=1` (hoặc `MIKE_WAKEUP_HINT=off`). Mọi lỗi → im, rc=0.
"""
import argparse
import os
import sys


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--job", default="")
    ap.add_argument("--delay", default="")
    ap.add_argument("--from", dest="frm", default="")
    a, _ = ap.parse_known_args()
    if not a.job:
        return 0
    if os.environ.get("DISPATCH_NO_DEPENDENT_STEP") == "1" or os.environ.get("MIKE_WAKEUP_HINT") == "off":
        return 0
    try:
        d = int(a.delay)
        when = f"~{d}s"
    except ValueError:
        when = "~240-270s"
    print(f"⚠️ CHƯA đặt ScheduleWakeup cho job {a.job} — dispatch --bg KHÔNG tự tỉnh lại cho bạn. "
          f"Còn bước phụ thuộc kết quả job này ⇒ đặt ScheduleWakeup ({when}, prompt bắt đầu bằng "
          f"'jobs.sh claim-reply {a.job}') làm tool call CUỐI của lượt NGAY BÂY GIỜ, trước khi viết "
          f"văn. Không có bước phụ thuộc ⇒ bỏ qua dòng này (tắt: DISPATCH_NO_DEPENDENT_STEP=1).")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)
