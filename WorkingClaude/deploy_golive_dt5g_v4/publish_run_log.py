# -*- coding: utf-8 -*-
"""
publish_run_log.py — sổ chạy của publish_gated_state.py (`data/dt5g_publish_runs.log`).

Mỗi lần publisher chạy ghi 1 dòng JSON lúc START và 1 dòng lúc END. `mike/bin/dt5g_writer_watch.py`
đọc sổ này để nhận ra một lần ghi bảng `tav2_bq.vnindex_5state_dt5g_live` NGOÀI cửa sổ cron
(18:25–19:20 ICT) là do CHÍNH TA chạy tay (OURS_MANUAL) thay vì báo writer LẠ (OTHER) — bus Wags
finding 'dt5g-live-writer-la' 25/10 04:03Z (job Taylor_20261025_043744).

Mỗi dòng: {"event": "START"|"END", "ts": ISO ICT có offset, "run_id", "pid", "ppid",
"parent": tên tiến trình cha, "parent_cmd": cmdline cha (cắt 300 ký tự), "argv", + trường thêm
(END: "publish_ok", "rc")}.

FAIL-OPEN: ghi log KHÔNG BAO GIỜ được làm hỏng publish — mọi lỗi chỉ in stderr. Ghi bằng MỘT
lệnh write() trên fd O_APPEND (dòng < PIPE_BUF ⇒ không xen dòng giữa 2 tiến trình) — append-only,
không có bước ghi đè nào để bị kill giữa chừng làm hỏng dòng cũ.
"""
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

_ICT = ZoneInfo("Asia/Ho_Chi_Minh")   # §16: neo ICT, không tin TZ host
LOG_NAME = "dt5g_publish_runs.log"
_MAX_LINE = 3800                      # < PIPE_BUF 4096 ⇒ 1 write O_APPEND là nguyên tử


def default_path(workdir):
    return os.path.join(workdir, "data", LOG_NAME)


def _proc(pid, what):
    try:
        with open(f"/proc/{pid}/{what}", "rb") as f:
            raw = f.read()
        return raw.replace(b"\0", b" ").decode("utf-8", "replace").strip()
    except OSError:
        return ""


def log_run(path, event, run_id, **extra):
    """Append 1 dòng JSON. Trả True nếu ghi được; lỗi ⇒ stderr + False, KHÔNG raise."""
    try:
        ppid = os.getppid()
        rec = {"event": event,
               "ts": datetime.now(_ICT).isoformat(timespec="seconds"),
               "run_id": run_id, "pid": os.getpid(), "ppid": ppid,
               "parent": _proc(ppid, "comm"), "parent_cmd": _proc(ppid, "cmdline")[:300],
               "argv": list(sys.argv)}
        rec.update(extra)
        line = json.dumps(rec, ensure_ascii=False, default=str)
        if len(line.encode("utf-8")) > _MAX_LINE:
            rec["parent_cmd"] = rec["parent_cmd"][:80]
            rec["argv"] = [str(a)[:80] for a in rec["argv"][:10]]
            line = json.dumps(rec, ensure_ascii=False, default=str)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, (line + "\n").encode("utf-8"))
        finally:
            os.close(fd)
        return True
    except Exception as e:                                  # noqa: BLE001 — fail-open có chủ đích
        try:
            print(f"WARN publish_run_log: không ghi được {path} ({type(e).__name__}: {e}) — "
                  "publish vẫn tiếp tục", file=sys.stderr)
        except Exception:                                   # noqa: BLE001
            pass
        return False
