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
import re
import shlex
from datetime import datetime, timedelta, timezone

TRANSCRIPTS = os.path.expanduser(
    "~/.claude/projects/-home-trido-thanhdt-WorkingClaude-mike-agents-Mike/*.jsonl"
)
# Ngưỡng prose: turn nào viết nhiều hơn ngần này ký tự văn xuôi SAU khi dispatch --bg
# là turn "bundle" — dạng đã chứng minh có rủi ro quên wakeup cao gấp ~25 lần
# (50% số ca quên vs 2% số ca tuân thủ, đo trên 147 turn từ 2026-07-07).
BUNDLE_CHARS = 1500

# --- phát hiện "lượt này có dispatch --bg" ---
# Bản đầu dùng `"dispatch.sh" in cmd and "--bg" in cmd` — substring trên TOÀN BỘ chuỗi lệnh.
# Nên `notify_thread.sh <id> "<bài viết NÓI VỀ dispatch.sh ... --bg>"` bị đếm là 1 lần dispatch.
# Bắt được 2 ca thật (turn 2026-08-17T08:45:02Z và 2026-08-15T17:40:34Z) trong audit
# `agents/Wags/research/wakeup_double_answer_audit_20260817.md`, và cái sai đó thổi phồng MẪU SỐ
# ⇒ tỷ lệ MISS báo cáo THẤP HƠN sự thật (20,0% -> 23,3% khi đo lại). Vì vậy phải neo vào VỊ TRÍ
# GỌI LỆNH: dispatch.sh phải đứng ở chỗ tên chương trình, và --bg phải là 1 token RIÊNG của
# chính lệnh đó — chữ nằm trong tham số đã được nháy của lệnh khác không tính.
_HEREDOC = re.compile(r"<<-?\s*(?:'([^']+)'|\"([^\"]+)\"|([A-Za-z_][A-Za-z0-9_]*))")


def _quote_open(s):
    """Ký tự nháy còn ĐANG mở ở cuối chuỗi (None nếu cân bằng)."""
    quote, i = None, 0
    while i < len(s):
        ch = s[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < len(s):
                i += 2; continue
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "\\" and i + 1 < len(s):
            i += 2; continue
        i += 1
    return quote


def strip_heredocs(cmd):
    """Bỏ THÂN heredoc trước khi phân tích.

    Thân heredoc là dữ liệu (prompt gửi cho agent), không phải lệnh — mà prompt của fleet
    này thường xuyên NÓI VỀ `dispatch.sh --bg`. Bỏ nó đi cũng làm dấu nháy trong lệnh cân
    bằng trở lại: dạng `dispatch.sh X "$(cat <<'PROMPT' ... PROMPT )" --bg` (dùng thật ngày
    2026-08-14) khiến bộ quét nháy lệch pha nếu thân prompt có dấu `"`.
    """
    lines = cmd.split("\n")
    out, i = [], 0
    while i < len(lines):
        line = lines[i]
        tags = [m.group(1) or m.group(2) or m.group(3) for m in _HEREDOC.finditer(line)]
        if not tags:
            out.append(line); i += 1; continue
        cur = _HEREDOC.sub("", line)
        i += 1
        for tag in tags:
            while i < len(lines) and lines[i].strip() != tag:
                i += 1
            i += 1  # bỏ luôn dòng đóng
        # Chỉ NỐI phần sau vào cùng dòng logic khi dòng mở heredoc còn nháy dở — tức heredoc
        # nằm TRONG một tham số đang mở. Ngược lại (`cat > file <<'EOF'` rồi dòng sau là lệnh
        # dispatch riêng) nối vào sẽ đẩy dispatch.sh khỏi vị trí tên chương trình.
        while _quote_open(cur) and i < len(lines):
            cur += lines[i]; i += 1
        out.append(cur)
    return "\n".join(out)


def split_commands(cmd):
    """Cắt chuỗi shell thành từng segment lệnh, BỎ QUA mọi ký tự nằm trong dấu nháy.
    Không phải parser bash đầy đủ — chỉ đủ để biết token nào đứng ở vị trí tên chương trình."""
    segments, buf, quote, i = [], [], None, 0
    while i < len(cmd):
        ch = cmd[i]
        if quote:
            if ch == "\\" and quote == '"' and i + 1 < len(cmd):
                buf.append(cmd[i:i + 2]); i += 2; continue
            if ch == quote:
                quote = None
            buf.append(ch); i += 1; continue
        if ch in "\"'":
            quote = ch; buf.append(ch); i += 1; continue
        if ch == "\\" and i + 1 < len(cmd):
            buf.append(cmd[i:i + 2]); i += 2; continue
        if cmd[i:i + 2] in ("&&", "||"):
            segments.append("".join(buf)); buf = []; i += 2; continue
        if ch in ";|&\n":
            segments.append("".join(buf)); buf = []; i += 1; continue
        # '(' mở subshell CHỈ khi đứng đầu hoặc sau khoảng trắng — `$(` là command
        # substitution, cắt ở đó sẽ tách `--bg` khỏi chính lệnh dispatch của nó.
        if ch == "(" and (not buf or buf[-1] in " \t"):
            segments.append("".join(buf)); buf = []; i += 1; continue
        buf.append(ch); i += 1
    segments.append("".join(buf))
    return [s for s in (seg.strip() for seg in segments) if s]


def is_bg_dispatch(cmd):
    """True khi chuỗi lệnh THỰC SỰ gọi dispatch.sh ... --bg (không phải chỉ nhắc tới nó).

    Điều kiện: trong CÙNG một segment lệnh, `dispatch.sh` là MỘT TOKEN riêng (sau khi bóc
    nháy) và `--bg` cũng là một token riêng. Chính phép bóc nháy làm việc chính: văn bản
    `"...dispatch.sh ... --bg..."` trong tham số của notify_thread.sh/append_event.sh là
    MỘT token dài, không bao giờ bằng `dispatch.sh`.

    Cố tình KHÔNG đòi dispatch.sh phải đứng đúng vị trí token đầu: các dạng bọc thật trong
    transcript (`env -u VAR ... bash -x <path>/dispatch.sh`) đẩy nó ra sau những tham số
    không đoán trước được, và một bộ đếm tuân thủ mà im lặng bỏ sót thì tệ hơn một bộ đếm
    thỉnh thoảng nhận dư — dư thì nhìn bảng là thấy, thiếu thì không.
    """
    for seg in split_commands(strip_heredocs(cmd)):
        try:
            tokens = shlex.split(seg)
        except ValueError:
            # nháy lệch (heredoc bị cắt…) — thà nhận nhầm còn hơn im lặng bỏ sót
            tokens = seg.split()
        if "--bg" not in tokens:
            continue
        if any(os.path.basename(t) == "dispatch.sh" for t in tokens):
            return True
    return False


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
                        if is_bg_dispatch(cmd):
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
