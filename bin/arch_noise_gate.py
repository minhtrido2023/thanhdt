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
Tin lạ, lỗi parse, lỗi đĩa, topic khác -> rc=1 (gửi). Tắt cả cổng: ARCH_GATE=off.
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
    ("wags_lifecycle", re.compile(r"Arch-review \(ad-hoc\)\*\* — finding Wags khớp 'wags-fix: ")),
    ("job_progress", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* nhận việc \(job `")),
    ("job_progress", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* job `\w+`: đã chạy \d+s")),
    ("job_progress", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* vẫn đang chạy")),
    ("job_done", re.compile(r"^[^\n]{0,6}\*\*\w+\*\* xong \(job `")),
    ("kb_nightly", re.compile(r"^🌙 KB nightly done \(")),
    ("selfcheck_sweep", re.compile(r"^🔴 \*\*Selfcheck baseline sweep\*\*")),
]
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
    rec = {"ts": now_ict().isoformat(timespec="seconds"), "cat": cat, "text": text}
    if extra:
        rec.update(extra)
    with open(BUFFER, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def _cron_errors(msg):
    """{job_key: first_error_line} trong mục ERRORS_FOUND; None nếu không parse được."""
    m = re.search(r"=== ERRORS_FOUND \((\d+)\) ===\n(.*?)(?=\n=== |\Z)", msg, re.S)
    if not m:
        return None if "ERRORS_FOUND" in msg else {}
    out, key = {}, None
    for line in m.group(2).split("\n"):
        h = re.match(r"^  (\[[^\]]+\] \S.*)$", line)
        if h:
            key = h.group(1).strip()
            out[key] = ""
        elif key and not out[key] and line.strip():
            out[key] = line.strip()
    if len(out) != int(m.group(1)):
        return None          # đếm không khớp -> không tin parser, để gửi nguyên văn
    return out


def _gate_cron(msg):
    errs = _cron_errors(msg)
    if errs is None:
        return 1, ""         # fail-open
    try:
        seen = json.load(open(CRON_SEEN, encoding="utf-8"))
    except FileNotFoundError:
        seen = {}
    new = {k: v for k, v in errs.items() if k not in seen}
    os.makedirs(STATE, exist_ok=True)
    tmp = CRON_SEEN + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({k: seen.get(k) or now_ict().strftime("%Y-%m-%d") for k in errs}, f, ensure_ascii=False)
    os.replace(tmp, CRON_SEEN)
    head = (re.search(r"(\d+) job cần chú ý", msg) or [None, "?"])[1]
    _append("cron_health", msg, {"n_attention": head, "n_err": len(errs), "n_new_err": len(new)})
    if not new:
        return 0, ""
    lines = [f"🩺 [cron_health_check] {len(new)} job lỗi MỚI (tổng {len(errs)} job lỗi, {head} cần chú ý):"]
    for k, v in list(new.items())[:8]:
        lines.append(f"• {k}\n   {v[:220]}")
    if len(new) > 8:
        lines.append(f"… và {len(new) - 8} job khác")
    lines.append("(job lỗi đã báo hôm trước chỉ vào digest cuối ngày)")
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
        if ln and not re.match(r"^\*{0,2}\d{1,2}:\d{2} ICT", ln):
            return ln[:n]
    return ""


def build_digest(recs, today):
    by = {}
    for r in recs:
        by.setdefault(r["cat"], []).append(r)
    lines = [f"📋 **Architecture — tổng kết {today}** (các việc đã tự xử lý/ghi nhận, không cần anh làm gì)"]
    if not recs:
        return lines[0] + "\n• Không có việc thường lệ nào cần ghi nhận."
    if "wags_lifecycle" in by:
        issues = sorted({m for r in by["wags_lifecycle"] for m in re.findall(r"'(coord-[\w-]+)'", r["text"])})
        done = sum("HOÀN TẤT" in r["text"] for r in by["wags_lifecycle"])
        verd = {}
        for r in by["wags_lifecycle"]:
            for v in re.findall(r"\*\*(CONFIRMED|NEEDS_CHANGES|REFUTED)\*\*", r["text"]):
                verd[v] = verd.get(v, 0) + 1
        vtxt = ", ".join(f"{k} ×{v}" for k, v in sorted(verd.items())) or "—"
        lines.append(f"• Wags tự sửa vấn đề điều phối: {done} hoàn tất/{len(issues)} issue ({', '.join(issues) or '—'}); arch-review: {vtxt}")
    if "job_done" in by:
        lines.append(f"• Job agent hoàn tất: {len(by['job_done'])}")
        for r in by["job_done"][-6:]:
            lines.append(f"   – {_first_line(r['text'], 130)}")
    if "job_progress" in by:
        lines.append(f"• Ping tiến độ job đã gộp: {len(by['job_progress'])} tin")
    if "cron_health" in by:
        r = by["cron_health"][-1]
        lines.append(f"• cron_health_check: {r.get('n_attention', '?')} job cần chú ý, {r.get('n_err', '?')} job lỗi "
                     f"({r.get('n_new_err', 0)} mới, đã báo riêng); chi tiết: `python3 bin/cron_health_check.py`")
    if "selfcheck_sweep" in by:
        r = by["selfcheck_sweep"][-1]
        names = re.findall(r"• `([^`]+)` — (\w+)", r["text"])
        known = re.search(r"\((\d+) ca đỏ ĐÃ BIẾT", r["text"])
        lines.append("• Selfcheck sweep: " + (", ".join(f"{n} {s}" for n, s in names) or "không ca đỏ mới")
                     + (f"; {known.group(1)} ca đỏ đã biết do Wags/Taylor xử lý" if known else ""))
    if "kb_nightly" in by:
        lines.append(f"• KB nightly: {_first_line(by['kb_nightly'][-1]['text'], 140)}")
    return "\n".join(lines)


def digest(post, dry):
    os.makedirs(STATE, exist_ok=True)
    cur = ""
    if os.path.exists(CURSOR):
        cur = open(CURSOR, encoding="utf-8").read().strip()
    recs = []
    if os.path.exists(BUFFER):
        for ln in open(BUFFER, encoding="utf-8"):
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if not cur or r["ts"] > cur:
                recs.append(r)
    text = build_digest(recs, now_ict().strftime("%d/%m/%Y"))
    print(text)
    if dry or not post:
        return 0
    env = dict(os.environ, ARCH_GATE="off")   # chính digest không được bị cổng chặn
    rc = subprocess.run([os.path.join(ROOT, "bin", "notify_thread.sh"), text, "architecture"],
                        env=env, stdout=subprocess.DEVNULL).returncode
    if rc != 0:
        print("arch_noise_gate: post digest thất bại — KHÔNG đẩy con trỏ, lần sau gom lại", file=sys.stderr)
        return rc
    tmp = CURSOR + ".tmp"
    open(tmp, "w", encoding="utf-8").write(recs[-1]["ts"] if recs else now_ict().isoformat(timespec="seconds"))
    os.replace(tmp, CURSOR)
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
