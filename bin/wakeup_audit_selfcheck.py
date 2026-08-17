#!/usr/bin/env python3
"""wakeup_audit_selfcheck.py — kiểm tra bộ phát hiện dispatch --bg của wakeup_audit.py.

Lý do tồn tại: bản đầu dùng substring `"dispatch.sh" in cmd`, nên một lệnh notify_thread.sh
đăng bài NÓI VỀ dispatch.sh bị đếm là dispatch thật (2 ca thật, audit 2026-08-17). Sai đó
làm phồng mẫu số ⇒ tỷ lệ MISS báo cáo nhẹ hơn sự thật. Ca số 1 dưới đây chính là ca đó.

Chạy: python3 bin/wakeup_audit_selfcheck.py    (exit 0 = PASS)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wakeup_audit import is_bg_dispatch  # noqa: E402

R = "/home/trido/thanhdt/WorkingClaude/mike/bin"

# (mô tả, command, có phải dispatch --bg thật không)
CASES = [
    # --- PHẢI là False: chỉ NHẮC TỚI dispatch.sh trong văn bản của lệnh khác ---
    # Thứ tự tham số đúng theo chữ ký thật: notify_thread.sh "<msg>" <thread>. Thread truyền
    # bằng TÊN trong kb/discord_channels.json, không phải ID trần (discord_id_gate hard-block).
    ("notify_thread.sh đăng bài có chữ dispatch.sh --bg trong nội dung",
     f'{R}/notify_thread.sh "Sự cố wake-đúp: sau `dispatch.sh <id> ... --bg` '
     'phải đặt ScheduleWakeup ngay trong cùng lượt." architecture', False),
    ("append_event ghi finding nhắc tên lệnh",
     f"{R}/append_event.sh Wags finding 'wake-audit' "
     "'{\"note\":\"detector cũ khớp nhầm dispatch.sh --bg trong văn bản\"}'", False),
    ("echo giải thích quy tắc",
     'echo "luôn dùng dispatch.sh --bg cho việc dài"', False),
    ("dispatch.sh ĐỒNG BỘ (không --bg) không được tính",
     f'{R}/dispatch.sh Taylor "chạy backtest"', False),
    ("--bg là của lệnh KHÁC trong cùng chuỗi, không phải của dispatch.sh",
     f'{R}/jobs.sh list 20 && other_tool --bg', False),

    # --- PHẢI là True: gọi thật ---
    ("gọi thẳng, đường dẫn tuyệt đối",
     f'{R}/dispatch.sh Taylor "phân tích X" --bg', True),
    ("có tiền tố biến môi trường",
     f'DISPATCH_FROM=Wags {R}/dispatch.sh Winston "kiểm tra corp-action" --bg', True),
    ("nằm sau && ở giữa chuỗi",
     f'cd /tmp && {R}/dispatch.sh Taylor "việc" --bg --model opus', True),
    ("nằm ở DÒNG THỨ HAI của lệnh nhiều dòng",
     f'echo start\n{R}/dispatch.sh Taylor "việc" --bg', True),
    ("bọc trong timeout",
     f'timeout 600 {R}/dispatch.sh Taylor "việc" --bg', True),
    ("đường dẫn tương đối",
     'bin/dispatch.sh Mafee "đặt lệnh" --bg', True),
    ("hai lệnh: 1 notify nhắc tên + 1 dispatch thật",
     f'{R}/notify_thread.sh 123 "sắp dispatch.sh --bg đây"; {R}/dispatch.sh Taylor "việc" --bg',
     True),
    ("--bg đứng trước tham số prompt",
     f'{R}/dispatch.sh Taylor --bg "việc"', True),
]


def main():
    fails = 0
    for desc, cmd, want in CASES:
        got = is_bg_dispatch(cmd)
        if got == want:
            print("  ok   %-62s -> %s" % (desc, got))
        else:
            fails += 1
            print("  FAIL %-62s -> %s (mong đợi %s)" % (desc, got, want))
    print("\nwakeup_audit_selfcheck: %s (%d/%d)"
          % ("PASS" if not fails else "FAIL", len(CASES) - fails, len(CASES)))
    return 1 if fails else 0


if __name__ == "__main__":
    raise SystemExit(main())
