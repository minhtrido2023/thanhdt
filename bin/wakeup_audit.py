#!/usr/bin/env python3
"""wakeup_audit.py — đo tuân thủ quy tắc MIKE.md §8: mọi turn có `dispatch.sh ... --bg`
PHẢI kết thúc bằng 1 lần `ScheduleWakeup` trong CÙNG turn đó.

Sinh ra từ sự cố 2026-07-20 (`missed-wakeup-after-bg-dispatch`, xem kb/INCIDENTS.md):
Mike dispatch 2 job --bg rồi trả lời thẳng 1 câu hỏi khác trong cùng lượt, không đặt
ScheduleWakeup → 2 job xong âm thầm, 19 phút sau mới được đọc, và chỉ vì user gõ tiếp
1 câu KHÁC. User phát hiện, không phải hệ thống.

Vì sao là script đo hồi cứu (retro) chứ KHÔNG phải watcher cảnh báo real-time:
phiên sống của Mike KHÔNG thể bị đánh thức từ bên ngoài (Discord bot bỏ qua mọi message
do bot đăng — xem MIKE.md §8). Một watcher real-time vì thế chỉ ping được USER, tức là
biến người dùng thành cơ chế phục hồi — đúng cái đang muốn bỏ. Đo hồi cứu trong
daily_retro thì rẻ, không cần daemon, và biến 1 chỉ số kỷ luật vô hình thành có theo dõi.

Read-only: chỉ đọc transcript của Mike, không sửa gì.

Dùng:
    python3 bin/wakeup_audit.py                 # 7 ngày gần nhất
    python3 bin/wakeup_audit.py --since 2026-07-07
    python3 bin/wakeup_audit.py --since 2026-07-20 --verbose
"""
import argparse
import glob
import json
import os
from datetime import datetime, timedelta, timezone

TRANSCRIPTS = os.path.expanduser(
    "~/.claude/projects/-home-trido-thanhdt-WorkingClaude-mike-agents-Mike/*.jsonl"
)
# Ngưỡng prose: turn nào viết nhiều hơn ngần này ký tự văn xuôi SAU khi dispatch --bg
# là turn "bundle" — dạng đã chứng minh có rủi ro quên wakeup cao gấp ~25 lần
# (50% số ca quên vs 2% số ca tuân thủ, đo trên 147 turn từ 2026-07-07).
BUNDLE_CHARS = 1500


def is_turn_boundary(rec):
    """Turn mới bắt đầu khi user (người thật) gõ, hoặc queue-operation của bridge."""
    if rec.get("type") == "queue-operation":
        return True
    if rec.get("type") != "user":
        return False
    content = rec.get("message", {}).get("content")
    return bool(
        isinstance(content, list) and content and content[0].get("type") == "text"
    )


def scan_turns(since):
    """Trả về list turn có ít nhất 1 dispatch --bg, kèm cờ đã ScheduleWakeup chưa."""
    turns = []
    for path in sorted(glob.glob(TRANSCRIPTS)):
        cur = {"bg": [], "wake": False, "prose": 0, "file": os.path.basename(path)[:8]}

        def flush(turn):
            if turn["bg"] and turn["bg"][-1] >= since:
                turns.append(turn)

        with open(path) as fh:
            for line in fh:
                try:
                    rec = json.loads(line)
                except (ValueError, TypeError):
                    continue
                if is_turn_boundary(rec):
                    flush(cur)
                    cur = {"bg": [], "wake": False, "prose": 0,
                           "file": os.path.basename(path)[:8]}
                    continue
                if rec.get("type") != "assistant":
                    continue
                content = rec.get("message", {}).get("content")
                if not isinstance(content, list):
                    continue
                for blk in content:
                    # prose ĐẾM SAU dispatch --bg đầu tiên: đó là phần đã "chiếm chỗ"
                    # của ScheduleWakeup ở cuối lượt
                    if blk.get("type") == "text" and cur["bg"]:
                        cur["prose"] += len(blk.get("text", ""))
                    if blk.get("type") != "tool_use":
                        continue
                    if blk.get("name") == "ScheduleWakeup":
                        cur["wake"] = True
                    elif blk.get("name") == "Bash":
                        cmd = str(blk.get("input", {}).get("command", ""))
                        if "dispatch.sh" in cmd and "--bg" in cmd:
                            cur["bg"].append(rec.get("timestamp", ""))
        flush(cur)
    turns.sort(key=lambda t: t["bg"][0])
    return turns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="YYYY-MM-DD (mặc định: 7 ngày trước)")
    ap.add_argument("--verbose", action="store_true", help="in mọi turn, không chỉ ca quên")
    args = ap.parse_args()

    since = args.since or (
        datetime.now(timezone.utc) - timedelta(days=7)
    ).strftime("%Y-%m-%d")

    turns = scan_turns(since)
    if not turns:
        print(f"wakeup_audit: không có turn nào dùng dispatch --bg từ {since}.")
        return 0

    misses = [t for t in turns if not t["wake"]]
    bundled = [t for t in misses if t["prose"] > BUNDLE_CHARS]
    rate = 100.0 * len(misses) / len(turns)

    print(f"=== MIKE.md §8 wakeup compliance — từ {since} ===")
    print(f"turn có dispatch --bg : {len(turns)}")
    print(f"thiếu ScheduleWakeup  : {len(misses)}  ({rate:.1f}%)")
    print(f"  trong đó dạng bundle: {len(bundled)}  (>{BUNDLE_CHARS} ký tự văn xuôi sau dispatch)")

    shown = turns if args.verbose else misses
    if shown:
        print(f"\n{'turn (dispatch --bg đầu)':28} {'wake':5} {'n_bg':4} {'prose':>6}  session")
        for t in shown:
            flag = "OK" if t["wake"] else "MISS"
            print(f"{t['bg'][0]:28} {flag:5} {len(t['bg']):<4} {t['prose']:>6}  {t['file']}")

    if misses:
        print("\nMỗi dòng MISS = 1 job nền chạy xong mà không có ai quay lại đọc theo lịch;")
        print("phát hiện chỉ xảy ra tình cờ khi user gõ câu tiếp theo. Xem kb/INCIDENTS.md")
        print("mục 'missed-wakeup-after-bg-dispatch' (2026-07-20).")
    return 1 if misses else 0


if __name__ == "__main__":
    raise SystemExit(main())
