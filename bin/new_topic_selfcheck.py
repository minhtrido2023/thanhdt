#!/usr/bin/env python3
"""new_topic_selfcheck.py — ghim hợp đồng của bin/new_topic.py (topic mới PHẢI ở đúng channel cha).

Bridge là listener CỤC BỘ (cổng ngẫu nhiên) qua MIKE_DISCORD_API ⇒ KHÔNG chạm Discord/ccdb thật.
    python3 mike/bin/new_topic_selfcheck.py     (exit 0 = mọi ca PASS)
"""
import json
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = os.environ.get("NEW_TOPIC_SCRIPT") or str(Path(__file__).resolve().with_name("new_topic.py"))
PASS = FAIL = 0
POSTS = []
PARENT = {"value": 555}          # parent_id mà listener giả trả; None = ccdb cũ / channel thường


def check(name, cond, extra=""):
    global PASS, FAIL
    PASS, FAIL = (PASS + 1, FAIL) if cond else (PASS, FAIL + 1)
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f" {extra}"))


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, obj):
        b = json.dumps(obj).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        self._send({"thread_id": 777, "thread_name": "old", "parent_id": PARENT["value"], "messages": []})

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        POSTS.append(body)
        self._send({"status": "sent", "thread_id": "9001"} if body.get("thread_name") else {"status": "sent"})


def run(port, *args, env_extra=None):
    env = dict(os.environ, MIKE_DISCORD_API=f"http://127.0.0.1:{port}")
    env.pop("DISCORD_THREAD_ID", None)
    env.update(env_extra or {})
    p = subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, env=env, timeout=30)
    return p.returncode, p.stdout, p.stderr


def main():
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    port = srv.server_address[1]

    # 1. Topic mới tạo dưới parent của topic hiện tại — KHÔNG phải kênh mặc định.
    POSTS.clear()
    rc, out, err = run(port, "Topic B", "--from-thread", "777")
    created = [p for p in POSTS if p.get("thread_name")]
    check("tạo thread đúng 1 lần, đúng tên", rc == 0 and len(created) == 1 and created[0]["thread_name"] == "Topic B", f"{rc} {err}")
    check("channel_id = parent_id của topic hiện tại (555)", created and created[0]["channel_id"] == 555, str(created))
    check("in NEW_THREAD_ID", "NEW_THREAD_ID=9001" in out, out)
    check("@mention chủ + nhắc Trading Daily đi vào thread mới / kênh daily",
          any(p.get("channel_id") == 9001 and "<@" in p["message"] for p in POSTS)
          and any("<#9001>" in p["message"] for p in POSTS), str(POSTS))

    # 2. Mặc định lấy $DISCORD_THREAD_ID.
    POSTS.clear()
    rc, _, _ = run(port, "Topic C", env_extra={"DISCORD_THREAD_ID": "777"})
    check("mặc định dùng $DISCORD_THREAD_ID", rc == 0 and any(p.get("channel_id") == 555 for p in POSTS))

    # 3. Không xác định được channel cha ⇒ exit 3, KHÔNG tạo gì (không fallback #mikefleet).
    for label, val in (("ccdb cũ/không có parent_id", None),):
        POSTS.clear()
        PARENT["value"] = val
        rc, _, err = run(port, "Topic D", "--from-thread", "777")
        check(f"{label} ⇒ exit 3, không tạo thread", rc == 3 and not POSTS, f"{rc} {POSTS}")
        check("thông báo nói rõ KHÔNG fallback", "KHÔNG fallback" in err, err)
    PARENT["value"] = 555

    # 4. Thiếu cả --from-thread lẫn $DISCORD_THREAD_ID ⇒ exit 3.
    POSTS.clear()
    rc, _, _ = run(port, "Topic E")
    check("thiếu topic hiện tại ⇒ exit 3, không tạo", rc == 3 and not POSTS)

    # 5. --channel chỉ định tay bỏ qua dò parent (tên registry).
    POSTS.clear()
    rc, _, _ = run(port, "Topic F", "--channel", "architecture", "--no-daily-link", "--no-mention")
    created = [p for p in POSTS if p.get("thread_name")]
    check("--channel <tên> dùng ID registry, không đụng parent", rc == 0 and len(created) == 1 and created[0]["channel_id"] != 555
          and len(POSTS) == 1, str(POSTS))

    # 6. --dry-run không tạo gì.
    POSTS.clear()
    rc, out, _ = run(port, "Topic G", "--from-thread", "777", "--dry-run")
    check("--dry-run chỉ in channel đích", rc == 0 and not POSTS and "555" in out, out)

    srv.shutdown()
    print(f"\n{PASS} PASS / {FAIL} FAIL")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
