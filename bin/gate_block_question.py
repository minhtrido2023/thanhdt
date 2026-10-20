#!/usr/bin/env python3
"""Cổng fail-closed BLOCK ⇒ một bus `question` CÓ CHỦ + HẠN + LỆNH RECOVER, nhắc tới khi đóng.

VÌ SAO (retro 10-16 → 10-19, Pattern 1 tái diễn 4 ngày; user chốt phương án A 2026-10-20):
cổng chặn ĐÚNG (approval 09:05, plan-t1-not-ready, delivery INCOMPLETE…) nhưng không bước nào
gán người xử lý + hạn + cách phục hồi ⇒ việc nằm chờ ai đó tình cờ nhớ ra.

HỢP ĐỒNG (đọc trước khi wire vào cổng mới):
  1. Helper này KHÔNG BAO GIỜ đổi quyết định của cổng. Caller đã chặn xong rồi mới gọi, bọc
     `|| true` + `timeout`; mọi lỗi của helper chỉ làm MẤT câu hỏi (ồn ít hơn), không bao giờ
     làm cổng mở. Helper không ghi plan/report/state của cổng nào.
  2. Idempotent theo (gate, key): sổ `state/gate_blocks/<gate>__<key>.json`, claim bằng O_EXCL.
     Cùng cổng + cùng key (key luôn chứa ngày hoặc tên artifact có ngày) ⇒ KHÔNG mở câu thứ hai,
     kể cả khi câu đầu đã đóng (§5: thà thiếu một câu hơn spam; block lại sau khi đã đóng tay
     là ca hiếm, lượt cổng vẫn alert qua kênh riêng của nó).
     Bị kill giữa "claim" và "post" ⇒ sổ ở `posting`; lượt sau (open lặp lại hoặc sweep) đọc
     BUS (nguồn sự thật bên ngoài, tìm `payload.gate_block_id`) trước khi post lại.
  3. Đóng CHỈ khi artifact chứng minh: `--probe` (lệnh shell, rc=0 ⇔ đã phục hồi) chạy trong
     `sweep`; rc=0 ⇒ `close_bus_question.py` với evidence = lệnh probe + output thật (§26/§29).
     Probe lỗi/timeout ⇒ coi là CHƯA phục hồi (nhắc tiếp), không bao giờ tự đóng.
     Câu đã được người đóng trên bus (audit chính thống không còn thấy pending) ⇒ ngừng nhắc.
  4. Giờ: mọi so sánh hạn theo ICT tường minh (§16), không theo TZ của host.

CLI:
  open   --gate G --key K --owner O --deadline YYYY-MM-DDTHH:MM --recover CMD --probe CMD
         --reason TEXT [--agent Mike] [--topic T] [--thread REG] [--remind-every-min N]
         [--extra JSON]
  sweep  [--dry-run]                         (cron; nhắc + đóng theo probe)
  list                                        (in sổ)
  probe  approval --account A --date D        (rc 0 đã duyệt+bot đã chạy · 10 còn chặn ·
                                               11 đã duyệt nhưng bot chưa chạy lại · 2 lỗi)
In ra một dòng `gate_block_question: <VERDICT> …` cho mỗi việc (grep được).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = Path(os.environ.get("GATE_BLOCK_ROOT") or Path(__file__).resolve().parent.parent)
WC_ROOT = Path(os.environ.get("GATE_BLOCK_WC_ROOT") or ROOT.parent)
STATE_DIR = ROOT / "state" / "gate_blocks"
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
PROBE_TIMEOUT_S = 120
TOOL_TIMEOUT_S = 60


def now_ict() -> dt.datetime:
    fake = os.environ.get("GATE_BLOCK_NOW")  # chỉ selfcheck dùng; production không đặt
    if fake:
        return dt.datetime.fromisoformat(fake).astimezone(ICT)
    return dt.datetime.now(ICT)


def parse_deadline(s: str) -> dt.datetime:
    d = dt.datetime.fromisoformat(s)
    return d.replace(tzinfo=ICT) if d.tzinfo is None else d.astimezone(ICT)


def state_path(gate: str, key: str) -> Path:
    return STATE_DIR / f"{gate}__{key}.json"


def save(path: Path, rec: dict) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".tmp_")
    with os.fdopen(fd, "w", encoding="utf-8") as fh:
        json.dump(rec, fh, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def bus_has_question(agent: str, topic: str, block_id: str) -> bool:
    """Bus là nguồn sự thật: đã có question mang đúng gate_block_id chưa (chống post trùng
    khi bị kill giữa append_event và lúc ghi sổ). Chỉ đọc inbox hiện hành của agent."""
    inbox = ROOT / "bus" / "inbox" / f"{agent}.jsonl"
    try:
        with open(inbox, encoding="utf-8") as fh:
            for line in fh:
                if block_id not in line:
                    continue
                try:
                    e = json.loads(line)
                except ValueError:
                    continue
                if (e.get("event_type") == "question" and e.get("topic") == topic
                        and (e.get("payload") or {}).get("gate_block_id") == block_id):
                    return True
    except FileNotFoundError:
        return False
    return False


def post_question(rec: dict) -> bool:
    if bus_has_question(rec["agent"], rec["topic"], rec["id"]):
        return True
    payload = dict(rec.get("extra") or {})
    payload.update({
        "gate_block_id": rec["id"], "gate": rec["gate"], "key": rec["key"],
        "question": (f"Cổng {rec['gate']} đang CHẶN ({rec['key']}): {rec['reason']} — "
                     f"chủ xử lý {rec['owner']}, hạn {rec['deadline']} ICT. "
                     f"Phục hồi: {rec['recover']}"),
        "owner": rec["owner"], "deadline_ict": rec["deadline"], "recover_cmd": rec["recover"],
        "close_when": f"probe rc=0: {rec['probe']} (sweep tự đóng qua close_bus_question.py)",
        "urgency": "high",
    })
    r = subprocess.run([str(ROOT / "bin" / "append_event.sh"), rec["agent"], "question",
                        rec["topic"], json.dumps(payload, ensure_ascii=False)],
                       capture_output=True, text=True, timeout=TOOL_TIMEOUT_S)
    if r.returncode != 0:
        print(f"gate_block_question: POST_FAILED {rec['id']} rc={r.returncode}: "
              f"{(r.stderr or r.stdout).strip()[-300:]}", file=sys.stderr)
        return False
    return True


def cmd_open(a) -> int:
    for name in ("gate", "key"):
        if not SLUG.match(getattr(a, name)):
            print(f"gate_block_question: BAD_ARG --{name}={getattr(a, name)!r} (chỉ [A-Za-z0-9._-])",
                  file=sys.stderr)
            return 2
    deadline = parse_deadline(a.deadline)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = state_path(a.gate, a.key)
    rec = {
        "id": f"{a.gate}__{a.key}", "gate": a.gate, "key": a.key, "agent": a.agent,
        "topic": a.topic or f"gate-block-{a.gate}-{a.key}", "owner": a.owner,
        "deadline": deadline.strftime("%Y-%m-%dT%H:%M"), "recover": a.recover, "probe": a.probe,
        "reason": " ".join(a.reason.split())[:400], "thread": a.thread,
        "remind_every_min": a.remind_every_min, "extra": json.loads(a.extra) if a.extra else {},
        "status": "posting", "opened_at": now_ict().isoformat(timespec="seconds"),
        "reminders": 0, "last_reminded_at": None,
    }
    try:
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        os.close(fd)
        save(path, rec)
    except FileExistsError:
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            # Sổ hỏng/đang ghi dở bởi tiến trình song song ⇒ KHÔNG post (thà thiếu hơn trùng).
            print(f"gate_block_question: STATE_UNREADABLE {path.name}: {exc}", file=sys.stderr)
            return 1
        if rec.get("status") != "posting":
            print(f"gate_block_question: ALREADY_{str(rec.get('status')).upper()} {rec['id']}")
            return 0
    if not post_question(rec):
        return 1
    rec["status"] = "open"
    rec["posted_at"] = now_ict().isoformat(timespec="seconds")
    save(path, rec)
    print(f"gate_block_question: OPENED {rec['agent']}/{rec['topic']} owner={rec['owner']} "
          f"deadline={rec['deadline']}")
    return 0


def still_pending(agent: str, topic: str) -> bool | None:
    """True/False theo audit chính thống; None nếu không đọc được (⇒ caller coi như còn mở)."""
    env = dict(os.environ, BUS_AUDIT_ROOT=str(ROOT))
    try:
        r = subprocess.run([sys.executable, str(ROOT / "bin" / "bus_question_audit.py"), "--json"],
                           env=env, capture_output=True, text=True, timeout=TOOL_TIMEOUT_S)
        pend = json.loads(r.stdout).get("pending", [])
    except (subprocess.SubprocessError, OSError, ValueError, AttributeError) as exc:
        print(f"gate_block_question: AUDIT_UNREADABLE ({type(exc).__name__}: {exc}) — coi như còn mở",
              file=sys.stderr)
        return None
    return any(q.get("agent") == agent and q.get("topic") == topic for q in pend)


def run_probe(cmd: str) -> tuple[int, str]:
    try:
        r = subprocess.run(["bash", "-c", cmd], cwd=WC_ROOT, capture_output=True, text=True,
                           timeout=PROBE_TIMEOUT_S)
        out = " ".join(((r.stdout or "") + " " + (r.stderr or "")).split())
        return r.returncode, out[-300:]
    except subprocess.TimeoutExpired:
        return 124, f"probe timeout {PROBE_TIMEOUT_S}s"
    except OSError as exc:
        return 127, f"probe không chạy được: {exc}"


def remind(rec: dict, now: dt.datetime, probe_rc: int, probe_out: str, dry: bool) -> None:
    last = rec.get("last_reminded_at")
    if last and now - dt.datetime.fromisoformat(last) < dt.timedelta(minutes=rec["remind_every_min"]):
        print(f"gate_block_question: STILL_OPEN {rec['id']} (nhắc gần đây, bỏ qua lượt này)")
        return
    left = parse_deadline(rec["deadline"]) - now
    mins = int(left.total_seconds() // 60)
    when = f"còn {mins} phút" if mins >= 0 else f"QUÁ HẠN {-mins} phút"
    msg = (f"⏰ CỔNG CHẶN CHƯA PHỤC HỒI — {rec['gate']} [{rec['key']}] · chủ: {rec['owner']} · "
           f"hạn {rec['deadline']} ICT ({when}) · phục hồi: {rec['recover']} · "
           f"probe rc={probe_rc}: {probe_out[-160:]} · bus: {rec['agent']}/{rec['topic']}")
    print(f"gate_block_question: REMIND {rec['id']} — {msg}")
    if dry:
        return
    subprocess.run([str(ROOT / "bin" / "notify.sh"), msg], capture_output=True,
                   timeout=TOOL_TIMEOUT_S)
    if rec.get("thread"):
        subprocess.run([str(ROOT / "bin" / "notify_thread.sh"), msg, rec["thread"]],
                       capture_output=True, timeout=TOOL_TIMEOUT_S)
    rec["reminders"] = int(rec.get("reminders") or 0) + 1
    rec["last_reminded_at"] = now.isoformat(timespec="seconds")


def sweep_one(path: Path, dry: bool) -> None:
    rec = json.loads(path.read_text(encoding="utf-8"))
    st = rec.get("status")
    if st == "closed":
        return
    if st == "posting":
        if dry or not post_question(rec):
            print(f"gate_block_question: POSTING_RETRY_PENDING {rec['id']}")
            return
        rec["status"] = "open"
        rec["posted_at"] = now_ict().isoformat(timespec="seconds")
        save(path, rec)
    ref = f"{rec['agent']}/{rec['topic']}"
    if still_pending(rec["agent"], rec["topic"]) is False:
        rec.update(status="closed", closed_at=now_ict().isoformat(timespec="seconds"),
                   closed_how="bus: audit chính thống không còn thấy pending (đóng ngoài helper)")
        if not dry:
            save(path, rec)
        print(f"gate_block_question: CLOSED_EXTERNALLY {ref}")
        return
    now = now_ict()
    rc, out = run_probe(rec["probe"])
    if rc == 0:
        if dry:
            print(f"gate_block_question: WOULD_CLOSE {ref} (probe rc=0)")
            return
        c = subprocess.run(
            [sys.executable, str(ROOT / "bin" / "close_bus_question.py"), ref,
             "--resolution", f"cổng {rec['gate']} [{rec['key']}] đã phục hồi — probe artifact rc=0",
             "--evidence", f"probe `{rec['probe']}` rc=0 lúc {now.isoformat(timespec='seconds')}: {out}",
             "--source-topic", "gate-block-sweep", "--actor", rec["agent"]],
            capture_output=True, text=True, timeout=TOOL_TIMEOUT_S)
        text = (c.stdout or "") + (c.stderr or "")
        if c.returncode == 0 and ("CLOSED" in text):
            rec.update(status="closed", closed_at=now.isoformat(timespec="seconds"),
                       closed_how=f"probe rc=0: {out}")
            save(path, rec)
            print(f"gate_block_question: CLOSED {ref}")
            return
        # close_bus_question chặn (rollup/substring rc=4/5) hoặc lỗi ⇒ KHÔNG ép đóng; nhắc kèm lý do.
        out = f"probe rc=0 nhưng close_bus_question rc={c.returncode}: {' '.join(text.split())[-200:]}"
    remind(rec, now, rc, out, dry)
    if not dry:
        save(path, rec)


def cmd_sweep(a) -> int:
    if not STATE_DIR.is_dir():
        print("gate_block_question: NOTHING_OPEN (chưa có sổ)")
        return 0
    bad = 0
    for path in sorted(STATE_DIR.glob("*.json")):
        try:
            sweep_one(path, a.dry_run)
        except Exception as exc:  # một bản ghi hỏng không được chặn các bản ghi khác
            bad += 1
            print(f"gate_block_question: SWEEP_ERROR {path.name}: {type(exc).__name__}: {exc}",
                  file=sys.stderr)
    return 1 if bad else 0


def cmd_list(_a) -> int:
    for path in sorted(STATE_DIR.glob("*.json")) if STATE_DIR.is_dir() else []:
        r = json.loads(path.read_text(encoding="utf-8"))
        print(f"{r['status']:8} {r['id']}  owner={r['owner']} deadline={r['deadline']} "
              f"reminders={r.get('reminders', 0)}")
    return 0


def cmd_probe_approval(a) -> int:
    """Phục hồi cổng approval = plan ĐÃ duyệt (đúng hàm bot dùng để chặn) VÀ bot ĐÃ chạy lại
    (journal executor tồn tại). Chỉ "đã duyệt" chưa đủ — retro 10-19: duyệt 09:19, bot phải có
    người chạy lại 09:25."""
    sys.path.insert(0, str(WC_ROOT))
    try:
        from trading_bot.plan import load_plan, approval_block_reason
        plan = load_plan(a.date, account=a.account)
    except Exception as exc:
        print(f"probe approval: ERROR {type(exc).__name__}: {exc}")
        return 2
    if plan is None:
        print(f"probe approval: không có plan {a.account} {a.date} — chưa phục hồi")
        return 10
    reason = approval_block_reason(plan)
    if reason:
        print(f"probe approval: VẪN CHẶN — {reason}")
        return 10
    if not plan.orders:
        print(f"probe approval: OK plan {a.account} {a.date} không còn lệnh nào — không còn gì để thực thi")
        return 0
    journal = WC_ROOT / "data" / "execution_logs" / f"exec_{a.account}_{a.date}_journal.csv"
    if not journal.exists():
        print(f"probe approval: hết bị cổng chặn (approved_by={plan.approved_by!r}) nhưng chưa có "
              f"{journal.name} — bot CHƯA chạy lại")
        return 11
    print(f"probe approval: OK approved_by={plan.approved_by!r}, {journal.name} có")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open")
    for f in ("--gate", "--key", "--owner", "--deadline", "--recover", "--probe", "--reason"):
        o.add_argument(f, required=True)
    o.add_argument("--agent", default="Mike")
    o.add_argument("--topic", default="", help="giữ topic cũ của cổng (tương thích checker); mặc định gate-block-<gate>-<key>")
    o.add_argument("--thread", default="", help="registry notify_thread.sh cho lời nhắc")
    o.add_argument("--remind-every-min", type=int, default=120)
    o.add_argument("--extra", default="", help="JSON object gộp vào payload question")
    s = sub.add_parser("sweep")
    s.add_argument("--dry-run", action="store_true")
    sub.add_parser("list")
    p = sub.add_parser("probe")
    p.add_argument("kind", choices=["approval"])
    p.add_argument("--account", required=True)
    p.add_argument("--date", required=True)
    a = ap.parse_args(argv)
    if a.cmd == "open":
        return cmd_open(a)
    if a.cmd == "sweep":
        return cmd_sweep(a)
    if a.cmd == "list":
        return cmd_list(a)
    return cmd_probe_approval(a)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"gate_block_question: ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
