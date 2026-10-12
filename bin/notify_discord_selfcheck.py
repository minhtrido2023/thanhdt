#!/usr/bin/env python3
"""notify_discord_selfcheck.py — ghim TRẦN THỜI GIAN của lệnh curl trong bin/notify_discord.sh.

VÌ SAO (arch-review 2026-10-12, nhánh gate-source-check): curl POST tới bridge không có trần ⇒
bridge nhận kết nối rồi im lặng = treo vô hạn, kéo theo mọi caller chạy nó qua pipe/capture
(chuỗi 19:00, daily_refresh, send_plan_report.sh).

Chạy script THẬT, bridge là listener CỤC BỘ (127.0.0.1, cổng ngẫu nhiên) qua MIKE_DISCORD_API ⇒
KHÔNG gửi gì tới Discord/bridge thật (kênh chỉ là con số trong payload gửi tới listener giả).

Hợp đồng của file (header: "Always exits 0 — never breaks the caller") được GIỮ: hết trần cũng
exit 0 như bridge chết / bridge trả 500. Cái được ghim là THỜI GIAN quay về.

    python3 mike/bin/notify_discord_selfcheck.py     (exit 0 = mọi ca PASS)
    NOTIFY_DISCORD_SCRIPT=<bản mutation> python3 …    (dùng khi chạy mutation)
"""
import json
import os
import socket
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

SCRIPT = os.environ.get("NOTIFY_DISCORD_SCRIPT") or str(Path(__file__).resolve().with_name("notify_discord.sh"))
CHANNEL_NAME = "mikefleet"          # tên trong kb/discord_channels.json (mặc định của script)
CHANNEL_ID = subprocess.run(["bash", str(Path(SCRIPT).with_name("discord_channel.sh")), CHANNEL_NAME],
                            capture_output=True, text=True).stdout.strip()
PASS = FAIL = 0


def check(name, cond, extra=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"PASS {name}")
    else:
        FAIL += 1
        print(f"FAIL {name} {extra}")


def run(port, *args, max_time=None, timeout=12):
    """(rc|"TIMEOUT", giây). timeout của test > trần đang thử ⇒ TIMEOUT = script KHÔNG tự về."""
    env = dict(os.environ, MIKE_DISCORD_API=f"http://127.0.0.1:{port}", MIKE_DISCORD_CHANNEL=CHANNEL_NAME)
    env.pop("MIKE_DISCORD_MAX_TIME", None)
    if max_time is not None:
        env["MIKE_DISCORD_MAX_TIME"] = str(max_time)
    t0 = time.monotonic()
    try:
        rc = subprocess.run(["bash", SCRIPT, *args], capture_output=True, timeout=timeout, env=env).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    return rc, time.monotonic() - t0


def free_port():
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def http_bridge(status):
    got = []

    class H(BaseHTTPRequestHandler):
        def do_POST(self):
            got.append((self.path, self.rfile.read(int(self.headers.get("Content-Length") or 0))))
            self.send_response(status)
            self.end_headers()
            self.wfile.write(b"{}")

        def log_message(self, *a):
            pass

    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, got


def case_success_path_unchanged():
    srv, got = http_bridge(200)
    rc, secs = run(srv.server_address[1], "tin thử — selfcheck", "Tiêu đề", "16711680", "update task")
    srv.shutdown()
    body = json.loads(got[0][1].decode("utf-8")) if got else {}
    check("thành công: exit 0, về ngay", rc == 0 and secs < 5, extra=f"rc={rc} {secs:.1f}s")
    check("thành công: đúng 1 POST /api/notify", len(got) == 1 and got[0][0] == "/api/notify", extra=str(got)[:200])
    check("thành công: nội dung gửi không đổi (message/channel_id/format/color/title/thread_name)",
          body == {"message": "tin thử — selfcheck", "channel_id": int(CHANNEL_ID or 0), "format": "embed",
                   "color": 16711680, "title": "Tiêu đề", "thread_name": "update task"}, extra=str(body))


def case_bridge_error_and_dead_return_at_once():
    srv, got = http_bridge(500)
    rc, secs = run(srv.server_address[1], "x")
    srv.shutdown()
    check("bridge trả 500: exit 0 như cũ, về ngay", rc == 0 and secs < 5 and len(got) == 1, extra=f"rc={rc} {secs:.1f}s")
    rc, secs = run(free_port(), "x")
    check("bridge chết (từ chối kết nối): exit 0 như cũ, về ngay — không chờ hết trần",
          rc == 0 and secs < 3, extra=f"rc={rc} {secs:.1f}s")
    rc, secs = run(free_port())
    check("không có message: exit 0, không gửi", rc == 0 and secs < 3, extra=f"rc={rc} {secs:.1f}s")


def case_silent_bridge_is_capped():
    """Listener nhận kết nối rồi IM LẶNG. Trần rút còn 2s ⇒ script tự về quanh 2s; bỏ --max-time ⇒
    không tự về (test tự cắt ở 12s ⇒ TIMEOUT ⇒ đỏ)."""
    lst = socket.socket()
    lst.bind(("127.0.0.1", 0))
    lst.listen(5)
    conns = []

    def accept():
        try:
            while True:
                conns.append(lst.accept()[0])       # giữ kết nối, không đọc, không trả lời
        except OSError:
            pass

    threading.Thread(target=accept, daemon=True).start()
    rc, secs = run(lst.getsockname()[1], "x", max_time=2)
    check("bridge im lặng: đối chứng — listener ĐÃ nhận kết nối", len(conns) >= 1, extra=str(len(conns)))
    check("bridge im lặng: script tự về trong trần (≈2s), exit 0 theo hợp đồng 'always exits 0'",
          rc == 0 and 1.5 <= secs < 8, extra=f"rc={rc} {secs:.1f}s")
    for c in conns:
        c.close()
    lst.close()
    text = Path(SCRIPT).read_text(encoding="utf-8")
    check("trần mặc định production: --connect-timeout 5 --max-time 15",
          '--connect-timeout 5 --max-time "${MIKE_DISCORD_MAX_TIME:-15}"' in text)


if __name__ == "__main__":
    case_success_path_unchanged()
    case_bridge_error_and_dead_return_at_once()
    case_silent_bridge_is_capped()
    print(f"\nnotify_discord_selfcheck: {PASS} PASS, {FAIL} FAIL")
    sys.exit(1 if FAIL else 0)
