#!/usr/bin/env python3
"""stop_wakeup_check.py <transcript.jsonl> — dùng bởi hooks/stop.sh (Mike only).

In ra 1 từ trên stdout:
  MISS  = lượt HIỆN TẠI có dispatch.sh ... --bg (không --no-followup) mà KHÔNG có ScheduleWakeup
  OK    = có dispatch --bg và có ScheduleWakeup, hoặc không có dispatch --bg
  unknown = không đọc/parse được (caller phải fail-open)

Dùng CHÍNH hàm đo của wakeup_audit.py (is_bg_dispatch, is_turn_boundary) để hook và số đo
retro luôn cùng định nghĩa — hook bắt được đúng cái audit sẽ đếm là MISS. Khác hook cũ (chỉ
chặn khi còn job SỐNG gắn thread): cổng này dựa trên bằng chứng ngay trong transcript lượt,
không phụ thuộc job đã xong/heartbeat/DISCORD_THREAD_ID.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

TAIL = 2000  # lượt có thể dài (nhiều tool call); chỉ quét đuôi file


def main(path):
    from wakeup_audit import is_bg_dispatch, is_turn_boundary
    with open(path, encoding="utf-8", errors="replace") as f:
        lines = f.readlines()[-TAIL:]
    recs = []
    for ln in lines:
        try:
            recs.append(json.loads(ln))
        except Exception:
            continue
    start = 0
    for i in range(len(recs) - 1, -1, -1):
        if is_turn_boundary(recs[i]):
            start = i
            break
    else:
        # không thấy ranh giới trong đuôi => lượt dài hơn cửa sổ quét: không đoán
        if len(lines) >= TAIL:
            return "unknown"
    bg = wake = False
    for rec in recs[start:]:
        if rec.get("type") != "assistant":
            continue
        content = rec.get("message", {}).get("content")
        if not isinstance(content, list):
            continue
        for blk in content:
            if not isinstance(blk, dict) or blk.get("type") != "tool_use":
                continue
            if blk.get("name") == "ScheduleWakeup":
                wake = True
            elif blk.get("name") == "Bash":
                if is_bg_dispatch(str(blk.get("input", {}).get("command", ""))):
                    bg = True
    return "MISS" if (bg and not wake) else "OK"


if __name__ == "__main__":
    try:
        print(main(sys.argv[1]))
    except Exception:
        print("unknown")
