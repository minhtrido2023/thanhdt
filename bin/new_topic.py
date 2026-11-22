#!/usr/bin/env python3
"""new_topic.py "<tên topic>" — mở topic Discord MỚI trong ĐÚNG channel của topic hiện tại.

Dùng khi user nói "mở topic mới"/"đóng topic này, qua topic mới" (xem memory feedback-new-topic-handoff).
Trước 2026-11-22 mỗi lần mở topic mới đều tạo thread dưới #mikefleet (kênh mặc định của
/api/notify), nên topic đi lệch channel nếu topic cũ nằm ở channel khác. Script này lấy
`parent_id` của topic hiện tại (ccdb `GET /api/threads/<id>/messages`) rồi tạo thread dưới CHÍNH
channel đó.

FAIL LOUD, KHÔNG fallback im lặng về #mikefleet: không xác định được channel cha ⇒ exit 3 kèm
hướng dẫn (đó chính là lỗi cũ). Muốn chỉ định tay: `--channel <tên-trong-registry|ID>`.
(`parent_id` chỉ có từ khi ccdb chạy bản có field đó — ccdb cũ trả thiếu ⇒ exit 3.)

    bin/new_topic.py "VCB vòng 5" --message "Bàn giao: ..."            # từ $DISCORD_THREAD_ID
    bin/new_topic.py "..." --from-thread <id> | --channel <tên|ID>
    bin/new_topic.py "..." --dry-run                                    # chỉ in channel đích, không tạo gì

In `thread_id` mới ra stdout (dòng cuối `NEW_THREAD_ID=<id>`). Sau đó: dispatch việc `--thread <id>`,
`bin/wake_thread.sh <id> "<prompt>"` để phiên mới theo dõi, topic cũ dừng.
"""
import argparse
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = (os.environ.get("MIKE_DISCORD_API") or os.environ.get("CCDB_API_URL") or "http://127.0.0.1:8199").rstrip("/")
TIMEOUT = 30


def _http(method, path, payload=None):
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = urllib.request.Request(API + path, data=data, method=method, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode("utf-8") or "{}")


def resolve_name(name):
    """Tên registry/ID trần -> ID (bin/discord_channel.sh, nguồn duy nhất)."""
    p = subprocess.run([os.path.join(ROOT, "bin", "discord_channel.sh"), name], capture_output=True, text=True)
    if p.returncode != 0:
        raise SystemExit(f"new_topic: không phân giải được '{name}': {p.stderr.strip()}")
    return int(p.stdout.strip())


def parent_channel(thread_id):
    """parent_id của thread, hoặc None nếu ccdb không báo (ccdb cũ / không phải thread)."""
    try:
        body = _http("GET", f"/api/threads/{int(thread_id)}/messages?limit=1")
    except Exception as e:
        raise SystemExit(f"new_topic: không đọc được thread {thread_id} từ ccdb: {e}")
    pid = body.get("parent_id")
    return int(pid) if isinstance(pid, int) or (isinstance(pid, str) and pid.isdigit()) else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", help="tên topic mới")
    ap.add_argument("--message", default=None, help="tin mở đầu (mặc định: dòng bàn giao ngắn)")
    ap.add_argument("--from-thread", default=os.environ.get("DISCORD_THREAD_ID"), help="topic hiện tại (mặc định $DISCORD_THREAD_ID)")
    ap.add_argument("--channel", default=None, help="chỉ định tay channel cha (tên registry hoặc ID); bỏ qua dò parent")
    ap.add_argument("--no-mention", action="store_true", help="không @mention chủ")
    ap.add_argument("--no-daily-link", action="store_true", help="không nhắc link ở Trading Daily")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.channel:
        channel, how = resolve_name(a.channel), "chỉ định tay --channel"
    else:
        if not a.from_thread:
            print("new_topic: thiếu --from-thread và $DISCORD_THREAD_ID — không biết topic hiện tại để lấy channel.", file=sys.stderr)
            return 3
        channel = parent_channel(a.from_thread)
        how = f"parent của thread {a.from_thread}"
        if channel is None:
            print(f"new_topic: ccdb không trả parent_id cho thread {a.from_thread} (ccdb chưa restart bản mới, hoặc đó là "
                  "channel thường). KHÔNG fallback về #mikefleet. Dùng --channel <tên|ID> nếu biết channel đích.", file=sys.stderr)
            return 3
    print(f"channel đích: {channel} ({how})")
    if a.dry_run:
        return 0

    msg = a.message or f"Topic mới: {a.name}" + (f" (tách từ <#{a.from_thread}>)" if a.from_thread else "")
    res = _http("POST", "/api/notify", {"message": msg, "channel_id": channel, "thread_name": a.name, "format": "text"})
    tid = res.get("thread_id")
    if not tid:
        print(f"new_topic: /api/notify không trả thread_id: {res}", file=sys.stderr)
        return 1
    tid = int(tid)
    if not a.no_mention:  # @mention chủ ⇒ Discord thêm vào thread + thông báo. Best-effort.
        try:
            with open(os.path.join(ROOT, "kb", "discord_channels.json"), encoding="utf-8") as f:
                owner = json.load(f)["users"]["owner"]["id"]
            _http("POST", "/api/notify", {"message": f"<@{owner}> topic mới: {a.name}", "channel_id": tid, "format": "text"})
        except Exception as e:
            print(f"CẢNH BÁO: không @mention được chủ: {e}", file=sys.stderr)
    if not a.no_daily_link:  # thread do bot tạo không sinh thông báo ⇒ nhắc link ở Trading Daily. Best-effort.
        try:
            _http("POST", "/api/notify", {"message": f"🧵 Topic mới: <#{tid}> ({a.name})",
                                          "channel_id": resolve_name("trading_daily"), "format": "text"})
        except BaseException as e:  # SystemExit từ resolve_name cũng chỉ là best-effort ở đây
            print(f"CẢNH BÁO: không nhắc được ở Trading Daily: {e}", file=sys.stderr)
    print(f"NEW_THREAD_ID={tid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
