#!/usr/bin/env python3
"""Mỗi sáng 08:00 ICT: tạo topic Discord tên `dd.mm` và liệt kê việc CẦN USER QUYẾT.

Nguồn (xác định, không LLM — rẻ và tái lập được):
  1. Bus question chưa đóng (`bus_question_audit.py --json`) — lấy summary/options/recommendation
     từ event question gốc. `selfcheck-red` gộp thành 1 dòng đếm (nhiễu, không phải quyết định).
  2. Mục `## Chờ user` trong kb/memory/Mike.md (working memory của Mike).

Idempotent: marker state/daily_decision_topic/<YYYY-MM-DD>.json — chạy lại cùng ngày không tạo
topic thứ hai. `--dry-run` chỉ in nội dung. Tạo topic qua ccdb `/api/notify` + `thread_name`
(kênh mặc định mikefleet, cùng cha với các topic dd.mm user tự tạo).
"""
import argparse
import glob
import gzip
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
API = os.environ.get("MIKE_DISCORD_API", "http://127.0.0.1:8199")
MARKER_DIR = os.path.join(ROOT, "state", "daily_decision_topic")
MAX_QUESTIONS = 12          # trần số câu liệt kê chi tiết, phần dư chỉ đếm
CHUNK = 1800


def _events(path):
    op = gzip.open if path.endswith(".gz") else open
    try:
        with op(path, "rt", encoding="utf-8") as f:
            for line in f:
                try:
                    yield json.loads(line)
                except Exception:
                    continue
    except Exception:
        return


def pending_questions():
    out = subprocess.run([sys.executable, os.path.join(ROOT, "bin", "bus_question_audit.py"), "--json"],
                         capture_output=True, text=True).stdout     # rc=23 khi còn pending: tín hiệu, không phải lỗi
    return json.loads(out)["pending"]


def question_details(pending):
    """Map (agent, topic) -> payload của event question MỚI NHẤT khớp."""
    want = {(p["agent"], p["topic"]) for p in pending}
    found = {}
    files = sorted(glob.glob(os.path.join(ROOT, "bus", "inbox", "*.jsonl"))) + \
        sorted(glob.glob(os.path.join(ROOT, "bus", "inbox", "archive", "*.jsonl.gz")))
    for p in files:
        for r in _events(p):
            if r.get("event_type") != "question":
                continue
            key = (r.get("agent_id"), r.get("topic"))
            if key in want:
                pl = r.get("payload")
                if isinstance(pl, str):
                    try:
                        pl = json.loads(pl)
                    except Exception:
                        pl = {"summary": pl}
                found[key] = pl if isinstance(pl, dict) else {}
    return found


def user_wait_section():
    path = os.path.join(ROOT, "kb", "memory", "Mike.md")
    try:
        text = open(path, encoding="utf-8").read()
    except Exception:
        return []
    m = re.search(r"^## Chờ user\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return []
    return [ln.strip()[2:].strip() for ln in m.group(1).splitlines() if ln.strip().startswith("- ")]


def build(now):
    pend = pending_questions()
    noise = [p for p in pend if p["topic"].startswith("selfcheck-red")]
    real = [p for p in pend if p not in noise]
    real.sort(key=lambda p: (-p["age_days"], p["topic"]))
    det = question_details(real)
    lines = [f"**Việc cần anh quyết — {now:%d.%m.%Y}**", ""]

    wait = user_wait_section()
    if wait:
        lines.append("**A. Đang chờ anh (working memory)**")
        lines += [f"• {w}" for w in wait]
        lines.append("")

    lines.append(f"**B. Câu hỏi bus chưa đóng ({len(real)})**")
    for p in real[:MAX_QUESTIONS]:
        pl = det.get((p["agent"], p["topic"]), {})
        summ = (pl.get("summary") or "").strip().replace("\n", " ")
        if len(summ) > 260:
            summ = summ[:257] + "…"
        urg = pl.get("urgency")
        head = f"• `{p['agent']}/{p['topic']}` — {p['age_days']} ngày" + (f" · {urg}" if urg else "")
        lines.append(head)
        if summ:
            lines.append(f"  {summ}")
        if pl.get("recommendation"):
            rec = str(pl["recommendation"]).replace("\n", " ")
            lines.append(f"  → Đề xuất: {rec[:200]}")
    if len(real) > MAX_QUESTIONS:
        lines.append(f"… và {len(real) - MAX_QUESTIONS} câu nữa (chạy `bin/bus_question_audit.py`).")
    if not real:
        lines.append("Không có câu nào đang mở.")
    lines.append("")
    lines.append(f"**C. Nhiễu tự động**: {len(noise)} câu `selfcheck-red` đang mở (Wags xử lý, không cần anh quyết).")
    return "\n".join(lines)


def chunks(text):
    out, cur = [], ""
    for ln in text.split("\n"):
        if len(cur) + len(ln) + 1 > CHUNK and cur:
            out.append(cur)
            cur = ""
        cur += ln + "\n"
    if cur.strip():
        out.append(cur)
    return out


def post(payload):
    req = urllib.request.Request(API + "/api/notify", data=json.dumps(payload).encode("utf-8"),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8") or "{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="bỏ qua marker idempotent")
    a = ap.parse_args()
    now = datetime.now(ICT)
    name = now.strftime("%d.%m")
    text = build(now)
    if a.dry_run:
        print(f"[topic: {name}]\n{text}")
        return 0
    marker = os.path.join(MARKER_DIR, now.strftime("%Y-%m-%d") + ".json")
    if os.path.exists(marker) and not a.force:
        print(f"đã tạo topic {name} hôm nay ({marker}) — bỏ qua")
        return 0
    parts = chunks(text)
    channel = int(subprocess.run([os.path.join(ROOT, "bin", "discord_channel.sh"),
                                  os.environ.get("MIKE_DISCORD_CHANNEL", "mikefleet")],
                                 capture_output=True, text=True, check=True).stdout.strip())
    res = post({"message": parts[0], "channel_id": channel, "thread_name": name, "format": "text"})
    tid = res.get("thread_id") or res.get("channel_id")
    if not tid:
        print(f"LỖI: /api/notify không trả thread_id: {res}", file=sys.stderr)
        return 1
    for extra in parts[1:]:
        post({"message": extra, "channel_id": int(tid), "format": "text"})
    os.makedirs(MARKER_DIR, exist_ok=True)
    tmp = marker + ".tmp"
    with open(tmp, "w") as f:
        json.dump({"thread_id": str(tid), "name": name, "posted_at": now.isoformat()}, f)
    os.replace(tmp, marker)      # marker ghi SAU khi post thành công
    # Thread con của #mikefleet do bot tạo KHÔNG sinh thông báo (user không thấy 04/10, 05/10) ⇒
    # nhắc 1 dòng kèm link <#id> vào Trading Daily — kênh user đang theo dõi. Best-effort.
    try:
        daily = int(subprocess.run([os.path.join(ROOT, "bin", "discord_channel.sh"), "trading_daily"],
                                   capture_output=True, text=True, check=True).stdout.strip())
        post({"message": f"📋 Việc cần quyết hôm nay ({name}): <#{tid}>", "channel_id": daily, "format": "text"})
    except Exception as e:
        print(f"CẢNH BÁO: không nhắc được ở Trading Daily: {e}", file=sys.stderr)
    print(f"OK topic {name} thread_id={tid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
