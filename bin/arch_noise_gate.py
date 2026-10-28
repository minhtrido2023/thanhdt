#!/usr/bin/env python3
"""arch_noise_gate.py — lọc nhiễu cho topic Architecture (user chỉ đạo 2026-10-23).

Chỉ đạo: "phần nào quan trọng cần cảnh báo, nhắc nhở thì gửi vào topic đó, còn lại tự xử lý
riêng, và báo kết quả tổng hợp những việc đã xử lý trong ngày thôi".

Gọi từ notify_thread.sh (một điểm duy nhất mọi tin Discord đi qua), CHỈ khi topic đích là
Architecture:
    arch_noise_gate.py gate <thread_id> <message>
        rc=0   tin thường lệ -> đã ghi vào bộ đệm digest, KHÔNG gửi Discord
        rc=10  gửi, nhưng THAY nội dung bằng stdout (cron_health: chỉ lỗi MỚI)
        rc=1   gửi nguyên văn (mặc định cho mọi thứ không khớp mẫu thường lệ)
    arch_noise_gate.py digest [--post] [--dry-run]
        gom bộ đệm từ lần digest trước thành 1 tin tổng kết trong ngày.

THIẾT KẾ FAIL-OPEN: chỉ chặn những mẫu thường lệ KHAI BÁO TƯỜNG MINH bên dưới (denylist hẹp).
Tin lạ, lỗi parse, lỗi đĩa, topic khác -> rc=1 (gửi). Tắt cổng: ARCH_GATE=off.
Mất tin nhắn quan trọng tệ hơn nhiều so với thừa tin thường lệ.
"""
import json
import os
import re
import subprocess
import sys
import fcntl
from datetime import datetime
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
STATE = os.environ.get("ARCH_GATE_STATE") or os.path.join(ROOT, "state", "arch_digest")
BUFFER = os.path.join(STATE, "buffer.jsonl")
CURSOR = os.path.join(STATE, "cursor.txt")
CRON_SEEN = os.path.join(STATE, "cron_health_seen.json")
REGISTRY = os.path.join(ROOT, "kb", "discord_channels.json")


def arch_id():
    try:
        with open(REGISTRY, encoding="utf-8") as f:
            return str(json.load(f)["channels"]["architecture"]["id"])
    except Exception:
        return None


# Mẫu THƯỜNG LỆ -> (category, regex). Khớp bằng search trên toàn tin (đã bỏ tem giờ của bridge,
# vì tem do bridge thêm SAU notify_thread). Giữ hẹp: mỗi mẫu bám vào chuỗi cố định do chính
# script phát ra. NEEDS_CHANGES / CẦN NGƯỜI XEM / TÁI DIỄN / ❌ / 🚨 cố ý KHÔNG nằm ở đây.
ROUTINE = [
    ("wags_lifecycle", re.compile(r"\[wags-autofix\] Nhận issue điều phối")),
    ("wags_lifecycle", re.compile(r"\[wags-autofix\] HOÀN TẤT issue")),
    ("wags_lifecycle", re.compile(r"Arch-review \(ad-hoc\)\*\* — finding Wags khớp 'wags-fix: [^\n]{0,160}?: \*\*CONFIRMED\*\*")),
    ("job_progress", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* nhận việc \(job `")),
    ("job_progress", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* job `\w+`: đã chạy \d+s")),
    ("job_progress", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* vẫn đang chạy")),
    ("kb_nightly", re.compile(r"^🌙 KB nightly done \(")),
]
# CỐ Ý KHÔNG chặn (review 2026-10-23): "✅ X xong (job…)" = kênh giao KẾT QUẢ job cho người
# (MIKE.md §8); "Selfcheck baseline sweep" chỉ phát khi có ĐỎ MỚI; Arch-review NEEDS_CHANGES/REFUTED.
CRON_HEALTH = re.compile(r"^🩺 \[cron_health_check\]")


def classify(msg):
    if CRON_HEALTH.search(msg):
        return "cron_health"
    for cat, rx in ROUTINE:
        if rx.search(msg):
            return cat
    return None


def now_ict():
    return datetime.now(ICT)


def _append(cat, text, extra=None):
    os.makedirs(STATE, exist_ok=True)
    with open(BUFFER, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)          # ts lấy TRONG khoá: thứ tự file = thứ tự ts
        rec = {"ts": now_ict().isoformat(timespec="seconds"), "cat": cat, "text": text}
        if extra:
            rec.update(extra)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


CRON_SECTIONS = ("ERRORS_FOUND", "STALE", "LOG_MISSING", "NO_LOG_REDIRECT")
REMIND_DAYS = 7


def _cron_items(msg):
    """{(section|header): chữ ký lỗi} cho cả 4 mục cần xử lý; None nếu parser không tin được."""
    out = {}
    for sec in CRON_SECTIONS:
        m = re.search(rf"=== {sec} \((\d+)\) ===\n(.*?)(?=\n=== |\Z)", msg, re.S)
        if not m:
            if sec in msg:
                return None
            continue
        n, key = 0, None
        for line in m.group(2).split("\n"):
            h = re.match(r"^  (\[[^\]]+\] \S.*)$", line)
            if h:
                key = f"{sec}|{h.group(1).strip()}"
                out[key] = ""
                n += 1
            elif key and not out[key] and line.strip():
                out[key] = re.sub(r"\d+", "#", line.strip())[:120]
        if n != int(m.group(1)):
            return None
    return out


def _gate_cron(msg):
    items = _cron_items(msg)
    if items is None:
        return 1, ""         # fail-open
    try:
        seen = json.load(open(CRON_SEEN, encoding="utf-8"))
    except FileNotFoundError:
        seen = {}
    today = now_ict().date()
    send, nxt = {}, {}
    for k, sig in items.items():
        old = seen.get(k)
        if old is None or old.get("sig") != sig:
            send[k] = "MỚI"
            nxt[k] = {"first_seen": today.isoformat(), "last_sent": today.isoformat(), "sig": sig}
        else:
            age = (today - datetime.fromisoformat(old["last_sent"]).date()).days
            if age >= REMIND_DAYS:
                send[k] = f"⏰ còn từ {old['first_seen']}"
                old = dict(old, last_sent=today.isoformat())
            nxt[k] = old
    os.makedirs(STATE, exist_ok=True)
    tmp = CRON_SEEN + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(nxt, f, ensure_ascii=False)
    os.replace(tmp, CRON_SEEN)
    head = (re.search(r"(\d+) job cần chú ý", msg) or [None, "?"])[1]
    by_sec = {sec: [k.split("|", 1)[1] for k in items if k.startswith(sec + "|")] for sec in CRON_SECTIONS}
    _append("cron_health", msg, {"n_attention": head, "n_err": len(by_sec["ERRORS_FOUND"]),
                                 "n_stale": len(by_sec["STALE"]), "stale": [h.split()[-1].rsplit("/", 1)[-1] for h in by_sec["STALE"][:6]],
                                 "n_missing": len(by_sec["LOG_MISSING"]), "n_sent": len(send)})
    if not send:
        return 0, ""
    lines = [f"🩺 [cron_health_check] {len(send)} job cần xem (tổng {head} cần chú ý; job cũ không đổi → digest 18:00):"]
    for k, tag in list(send.items())[:10]:
        sec, hdr = k.split("|", 1)
        lines.append(f"• [{sec}] {tag}: {hdr}" + (f"\n   {items[k]}" if items[k] else ""))
    if len(send) > 10:
        lines.append(f"… và {len(send) - 10} job khác")
    return 10, "\n".join(lines)


def gate(thread_id, msg):
    if os.environ.get("ARCH_GATE", "on").lower() == "off":
        return 1, ""
    try:
        if arch_id() is None or str(thread_id) != arch_id():
            return 1, ""
        cat = classify(msg)
        if cat is None:
            return 1, ""
        if cat == "cron_health":
            return _gate_cron(msg)
        _append(cat, msg)
        return 0, ""
    except Exception as e:  # fail-open: lỗi cổng không bao giờ được nuốt tin
        print(f"arch_noise_gate: lỗi {type(e).__name__}: {e} — gửi nguyên văn", file=sys.stderr)
        return 1, ""


def _first_line(text, n=150):
    t = re.sub(r"[*`_]", "", text)
    for ln in t.split("\n"):
        ln = ln.strip()
        if ln and not re.match(r"^\d{1,2}:\d{2} ICT", ln):
            return ln[:n]
    return ""


def build_digest(recs, today):
    by = {}
    for r in recs:
        by.setdefault(r["cat"], []).append(r)
    lines = [f"📋 **Architecture — tổng kết {today}** (việc thường lệ đã tự xử lý; cảnh báo quan trọng đã gửi riêng khi phát sinh)"]
    if not recs:
        return lines[0] + "\n• Không có việc thường lệ nào cần ghi nhận."
    if "wags_lifecycle" in by:
        issues = sorted({m for r in by["wags_lifecycle"] for m in re.findall(r"'(coord-[\w-]+)'", r["text"])})
        done_txt = [r["text"] for r in by["wags_lifecycle"] if "HOÀN TẤT" in r["text"]]
        # LOW-RISK = pipeline BỎ QUA arch-reviewer (wags_autofix.sh) — không được nhãn "CONFIRMED".
        low = sum("(LOW-RISK —" in t for t in done_txt)
        lines.append(f"• Wags tự sửa vấn đề điều phối: {len(done_txt)} hoàn tất / {len(issues)} issue ({', '.join(issues) or '—'}): "
                     f"{len(done_txt) - low} arch-review CONFIRMED, {low} low-risk bỏ qua review")
    if "job_progress" in by:
        lines.append(f"• Ping tiến độ job đã gộp: {len(by['job_progress'])} tin (kết quả job vẫn gửi riêng)")
    if "cron_health" in by:
        for r in by["cron_health"]:
            stale = f"; STALE: {', '.join(r['stale'])}" if r.get("stale") else ""
            lines.append(f"• cron_health_check: {r.get('n_attention', '?')} job cần chú ý — {r.get('n_err', 0)} lỗi, "
                         f"{r.get('n_stale', 0)} stale, {r.get('n_missing', 0)} thiếu log; đã báo riêng {r.get('n_sent', 0)}{stale}")
        lines.append("   chi tiết đầy đủ: `python3 bin/cron_health_check.py`")
    for r in by.get("kb_nightly", []):
        lines.append(f"• KB nightly: {_first_line(r['text'], 400)}")
    return "\n".join(lines)


def digest(post, dry):
    os.makedirs(STATE, exist_ok=True)
    off = 0
    if os.path.exists(CURSOR):
        try:
            off = int(open(CURSOR, encoding="utf-8").read().strip() or 0)
        except ValueError:
            off = 0
    recs, end = [], off
    if os.path.exists(BUFFER):
        with open(BUFFER, "rb") as f:
            fcntl.flock(f, fcntl.LOCK_SH)
            end = os.fstat(f.fileno()).st_size
            if off > end:
                off = 0                   # buffer bị cắt/xoay -> đọc lại từ đầu
            f.seek(off)
            chunk = f.read(end - off)
        for ln in chunk.decode("utf-8", "replace").split("\n"):
            try:
                recs.append(json.loads(ln))
            except ValueError:
                continue
    text = build_digest(recs, now_ict().strftime("%d/%m/%Y"))
    print(text)
    if dry or not post:
        return 0
    env = dict(os.environ, ARCH_GATE="off")   # chính digest không được bị cổng chặn
    cmd = os.environ.get("ARCH_DIGEST_NOTIFY") or os.path.join(ROOT, "bin", "notify_thread.sh")
    rc = subprocess.run([cmd, text, "architecture"], env=env, stdout=subprocess.DEVNULL).returncode
    if rc != 0:
        print("FAIL arch_noise_gate: post digest thất bại — KHÔNG đẩy con trỏ, lần sau gom lại", file=sys.stderr)
        return rc
    tmp = CURSOR + ".tmp"
    open(tmp, "w", encoding="utf-8").write(str(end))
    os.replace(tmp, CURSOR)
    # xoay buffer khi đã đọc hết và > 1MB (dưới khoá, chỉ khi chưa có ai ghi thêm)
    if end > 1_000_000 and os.path.exists(BUFFER):
        with open(BUFFER, "r+b") as f:
            fcntl.flock(f, fcntl.LOCK_EX)
            if os.fstat(f.fileno()).st_size == end:
                f.truncate(0)
                open(CURSOR, "w", encoding="utf-8").write("0")
    return 0


def main(argv):
    if len(argv) >= 4 and argv[1] == "gate":
        rc, out = gate(argv[2], argv[3])
        if out:
            sys.stdout.write(out)
        return rc
    if len(argv) >= 2 and argv[1] == "digest":
        return digest("--post" in argv, "--dry-run" in argv)
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
