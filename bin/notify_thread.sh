#!/usr/bin/env bash
# notify_thread.sh "<message>" [channel_name | thread_id]
# Post a message directly to a Discord topic.
#
# ĐỐI SỐ 2 NÊN LÀ **TÊN** khai trong kb/discord_channels.json (vd `trading_daily`,
# `architecture`), KHÔNG phải ID trần. Đây là ĐIỂM KIỂM SOÁT DUY NHẤT phân giải tên→ID cho
# toàn fleet: script cron chỉ truyền tên, không file nào còn giữ biến/hardcode ID riêng nữa
# (nguyên nhân gốc của 4 lần rò rỉ chéo topic — xem kb/discord_channels.json). ID trần (17–20
# chữ số) vẫn passthrough vì dispatch.sh phải truyền lại đúng ID đã ghim trên job record.
# Tên KHÔNG có trong registry ⇒ thoát lỗi + ghi logs/notify_thread_errors.log (fail loud),
# KHÔNG rơi về topic mặc định — chính cái fallback im lặng đó là cơ chế rò rỉ.
#
# thread_id defaults to contents of state/ccdb_thread_id.
# Uses ccdb-mike's /api/notify with channel_id=thread_id (threads are channels in Discord).
#
# Discord messages cap at ~2000 chars; /api/notify has no file-attachment support (that path
# only exists for live bot-managed sessions via .ccdb-attachments-<thread_id>, unusable from a
# standalone cron script). Long messages (e.g. plan reports with many tickers) are CHUNKED at
# line boundaries into multiple sequential sends instead of being truncated/dropped — same
# strategy the Discord bridge itself uses for long assistant replies (chunk_message()).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

msg="${1:?usage: notify_thread.sh \"<message>\" [thread_id]}"
thread_id="${2:-}"

# Default target, in order: the CALLER's own session/job topic ($DISCORD_THREAD_ID, injected
# per-session by the bridge and inherited by dispatched agents), then the global
# state/ccdb_thread_id pointer. The global is "the last topic Mike started a session in" —
# using it while a caller has its own topic in env posted the message into whatever topic the
# user happened to be reading (fixed 2026-07-22, same cross-topic leak family as dispatch.sh).
if [ -z "$thread_id" ]; then
  thread_id="${DISCORD_THREAD_ID:-}"
fi
if [ -z "$thread_id" ]; then
  # TẦNG CUỐI = con trỏ TOÀN CỤC "topic Mike vào gần nhất", bị hooks/session_start.sh ghi đè
  # mỗi lần Mike start/resume ở BẤT KỲ topic nào. Đây CHÍNH LÀ cơ chế rò rỉ của cả 4 sự cố
  # 2026-07: khi 2 tầng trên rỗng, tin nhắn KHÔNG fail — nó rơi vào topic user tình cờ đang
  # đọc. Tính đến 2026-08-02 KHÔNG còn call site nào trong bin/ đi vào nhánh này (mọi caller
  # đều truyền tên/ID tường minh, đã kiểm bằng grep toàn repo), nên giữ lại chỉ để phiên tương
  # tác của Mike không mất thông báo. Ghi log MỖI LẦN dùng để nhánh này không bao giờ âm thầm
  # sống lại: một call site mới quên truyền topic sẽ hiện ra trong logs/notify_thread_errors.log
  # thay vì biểu hiện thành "message lẫn topic" mà không ai truy được.
  state_file="$ROOT/agents/Mike/state/ccdb_thread_id"
  [ -f "$state_file" ] || { echo "notify_thread: no thread_id and state file missing" >&2; exit 1; }
  thread_id="$(cat "$state_file")"
  mkdir -p "$ROOT/logs"
  printf '%s notify_thread: WARN fallback con-tro-toan-cuc (khong ai truyen topic) -> %s | caller=%s | msg=%.80s\n' \
    "$(date -Iseconds)" "$thread_id" "${0##*/}<-$(ps -o comm= -p "$PPID" 2>/dev/null)" "$msg" \
    >> "$ROOT/logs/notify_thread_errors.log"
fi

[ -n "$thread_id" ] || { echo "notify_thread: empty thread_id" >&2; exit 1; }

# Tên-ý-nghĩa → ID thật (ID trần đi thẳng qua). Hỏng ở đây là hỏng TO: mọi caller đều bọc
# `2>/dev/null || true`, nên nếu chỉ in stderr thì một tên gõ sai sẽ nuốt tin nhắn mà không ai
# biết. Ghi thêm 1 dòng vào logs/notify_thread_errors.log để ops_health_check còn thấy được.
if ! resolved="$("$ROOT/bin/discord_channel.sh" "$thread_id" 2>&1)"; then
  mkdir -p "$ROOT/logs"
  printf '%s notify_thread: KHONG phan giai duoc topic %q — TIN NHAN KHONG GUI. %s\n' \
    "$(date -Iseconds)" "$thread_id" "$resolved" >> "$ROOT/logs/notify_thread_errors.log"
  echo "notify_thread: $resolved" >&2
  exit 1
fi
thread_id="$resolved"

python3 - "$thread_id" "$msg" << 'PY'
import sys, json, urllib.request

thread_id, message = sys.argv[1], sys.argv[2]
LIMIT = 1900  # safety margin under Discord's ~2000-char message cap

def chunk(text, limit):
    """Split at line boundaries into pieces <= limit chars. Never breaks mid-line
    (a single line longer than limit is hard-cut as a last resort)."""
    lines = text.split("\n")
    chunks, cur = [], ""
    for line in lines:
        candidate = line if not cur else cur + "\n" + line
        if len(candidate) <= limit:
            cur = candidate
            continue
        if cur:
            chunks.append(cur)
        if len(line) <= limit:
            cur = line
        else:
            for i in range(0, len(line), limit):
                chunks.append(line[i:i + limit])
            cur = ""
    if cur:
        chunks.append(cur)
    return chunks or [""]

pieces = chunk(message, LIMIT) if len(message) > LIMIT else [message]

for i, piece in enumerate(pieces, 1):
    body = f"[{i}/{len(pieces)}]\n{piece}" if len(pieces) > 1 else piece
    payload = json.dumps({"message": body, "channel_id": int(thread_id), "format": "text"}).encode()
    req = urllib.request.Request(
        "http://127.0.0.1:8199/api/notify",
        data=payload, method="POST",
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=10) as r:
        print(r.read().decode())
PY
