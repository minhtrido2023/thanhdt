#!/usr/bin/env python3
"""Cổng fail-closed BLOCK ⇒ một bus `question` CÓ CHỦ + HẠN + CÁCH PHỤC HỒI, nhắc tới khi đóng/hết hạn.

VÌ SAO (retro 10-16 → 10-19, Pattern 1 tái diễn 4 ngày; user chốt phương án A 2026-10-20):
cổng chặn ĐÚNG (approval 09:05, plan-t1-not-ready, delivery INCOMPLETE…) nhưng không bước nào
gán người xử lý + hạn + cách phục hồi ⇒ việc nằm chờ ai đó tình cờ nhớ ra.

HỢP ĐỒNG (đọc trước khi wire vào cổng mới):
  1. Helper này KHÔNG BAO GIỜ đổi quyết định của cổng. Caller đã chặn xong rồi mới gọi, bọc
     `|| true` + `timeout`; mọi lỗi của helper chỉ làm MẤT câu hỏi (ồn ít hơn), không bao giờ
     làm cổng mở. Helper không ghi plan/report/state của cổng nào.
  2. Idempotent theo (gate, key): sổ `state/gate_blocks/<gate>__<key>.json`, claim nguyên tử bằng
     tmp + os.link (file sổ không bao giờ tồn tại ở dạng rỗng). Cùng cổng + cùng key ⇒ KHÔNG mở
     câu thứ hai, kể cả khi câu đầu đã đóng/hết hạn (§5: thà thiếu một câu hơn spam).
     Bị kill giữa "claim" và "post" ⇒ sổ ở `posting`; lượt sau đọc BUS (nguồn sự thật bên ngoài,
     tìm `payload.gate_block_id`) trước khi post lại.
  3. Đóng CHỈ khi artifact chứng minh: probe (rc=0 ⇔ đã phục hồi) chạy trong `sweep` với env
     GATE_BLOCK_OPENED_AT = lúc mở; probe dựng sẵn (`probe approval|plan-t1`) chỉ nhận artifact
     MỚI HƠN lúc mở (artifact có trước khi mở KHÔNG chứng minh phục hồi). rc=0 ⇒
     `close_bus_question.py`, evidence = lệnh probe + output thật (§26/§29). Probe lỗi/timeout ⇒
     CHƯA phục hồi. Câu đã được người đóng trên bus ⇒ ngừng nhắc.
  4. Có điểm DỪNG: `--expires-at` / `--expires-in-days` và `--max-reminders`. Tới đó ⇒ gửi MỘT
     tin cuối rồi status `expired`, không nhắc nữa (câu hỏi bus vẫn mở cho người đóng tay).
  5. Lúc mở đăng thêm status `triaged-needs-human: <topic>` + suppress_days (cơ chế ACK_PREFIX của
     ops_health_check.sh) ⇒ CHECK5 không dispatch Wags đuổi trùng chủ; câu hỏi vẫn in [WARN-ONLY].
  6. `--recover-kind instructions` ⇒ cách phục hồi là CHỈ DẪN cho người (payload
     `recover_instructions`, KHÔNG có trường lệnh máy đọc); `--next-step RC=TEXT` ⇒ bước kế chỉ
     hiện khi probe trả đúng RC đó (vd approval: Mike chạy lại bot CHỈ sau khi probe thấy duyệt).
  7. Giờ: mọi so sánh hạn theo ICT tường minh (§16), không theo TZ của host.
  8. Dọn sổ: bản ghi closed/expired quá RETAIN_DAYS ngày bị sweep xoá (key luôn chứa ngày ⇒
     không mở lại nhầm).

CLI:
  open   --gate G --key K --owner O --deadline YYYY-MM-DDTHH:MM --recover TEXT --probe CMD
         --reason TEXT (--expires-at YYYY-MM-DDTHH:MM | --expires-in-days N)
         [--recover-kind cmd|instructions] [--next-step RC=TEXT]... [--max-reminders N]
         [--agent Mike] [--topic T] [--thread REG] [--remind-every-min N] [--extra JSON]
  sweep  [--dry-run]                         (cron; nhắc + đóng theo probe; flock)
  list                                        (in sổ)
  probe  approval --account A --date D        (0 đã duyệt + bot đã chạy SAU lúc mở · 10 còn chặn ·
                                               11 đã duyệt nhưng bot chưa chạy lại · 12 không có
                                               plan · 2 lỗi)
  probe  plan-t1 --account A --date D --marker-dir M --plan-dir P
                                              (0 marker gửi SAU lúc mở + md5 khớp plan hiện tại ·
                                               11 chưa · 2 lỗi)
In ra một dòng `gate_block_question: <VERDICT> …` cho mỗi việc (grep được).
"""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from zoneinfo import ZoneInfo

ICT = ZoneInfo("Asia/Ho_Chi_Minh")
ROOT = Path(os.environ.get("GATE_BLOCK_ROOT") or Path(__file__).resolve().parent.parent)
WC_ROOT = Path(os.environ.get("GATE_BLOCK_WC_ROOT") or ROOT.parent)
STATE_DIR = ROOT / "state" / "gate_blocks"
SLUG = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,80}$")
CLOSED_LINE = re.compile(r"^close_bus_question: CLOSED ", re.M)
PROBE_TIMEOUT_S = int(os.environ.get("GATE_BLOCK_PROBE_TIMEOUT_S") or 120)  # env chỉ selfcheck
TOOL_TIMEOUT_S = 60
ACK_PREFIX = "triaged-needs-human:"   # khớp ops_health_check.sh ACK_PREFIX
ACK_MAX_SUPPRESS_DAYS = 14            # khớp ops_health_check.sh ACK_MAX_SUPPRESS_DAYS
DEFAULT_MAX_REMINDERS = 40
RETAIN_DAYS = 30
TMP_PREFIX = ".tmp_"
TMP_MAX_AGE_S = 3600   # tmp mồ côi (bị kill giữa mkstemp và replace/link) quá 1 giờ ⇒ sweep xoá
DONE = ("closed", "expired")


def now_ict() -> dt.datetime:
    fake = os.environ.get("GATE_BLOCK_NOW")  # chỉ selfcheck dùng; production không đặt
    if fake:
        return dt.datetime.fromisoformat(fake).astimezone(ICT)
    return dt.datetime.now(ICT)


def parse_ict(s: str) -> dt.datetime:
    d = dt.datetime.fromisoformat(s)
    return d.replace(tzinfo=ICT) if d.tzinfo is None else d.astimezone(ICT)


def state_path(gate: str, key: str) -> Path:
    return STATE_DIR / f"{gate}__{key}.json"


def _write_tmp(dirpath: Path, rec: dict) -> str:
    fd, tmp = tempfile.mkstemp(dir=dirpath, prefix=TMP_PREFIX)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(rec, fh, ensure_ascii=False, indent=1)
    except BaseException:
        os.unlink(tmp)
        raise
    return tmp


def save(path: Path, rec: dict) -> None:
    tmp = _write_tmp(path.parent, rec)
    try:
        os.replace(tmp, path)
    except BaseException:
        os.unlink(tmp)
        raise


def claim(path: Path, rec: dict) -> bool:
    """Tạo sổ nguyên tử CÓ NỘI DUNG: tmp đầy đủ rồi os.link (thất bại nếu đã tồn tại). Không bao
    giờ có khoảnh khắc file sổ rỗng cho tiến trình song song đọc nhầm thành 'hỏng'."""
    tmp = _write_tmp(path.parent, rec)
    try:
        os.link(tmp, path)
        return True
    except FileExistsError:
        return False
    finally:
        os.unlink(tmp)


def _bus_has(agent: str, block_id: str, pred) -> bool:
    """Bus là nguồn sự thật (chống post trùng khi bị kill giữa append_event và ghi sổ).
    Chỉ đọc inbox hiện hành của agent."""
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
                if (e.get("payload") or {}).get("gate_block_id") == block_id and pred(e):
                    return True
    except FileNotFoundError:
        return False
    return False


def bus_has_question(agent: str, topic: str, block_id: str) -> bool:
    return _bus_has(agent, block_id,
                    lambda e: e.get("event_type") == "question" and e.get("topic") == topic)


def append(agent: str, etype: str, topic: str, payload: dict, rid: str) -> bool:
    r = subprocess.run([str(ROOT / "bin" / "append_event.sh"), agent, etype, topic,
                        json.dumps(payload, ensure_ascii=False)],
                       capture_output=True, text=True, timeout=TOOL_TIMEOUT_S)
    if r.returncode != 0:
        print(f"gate_block_question: POST_FAILED {etype} {rid} rc={r.returncode}: "
              f"{(r.stderr or r.stdout).strip()[-300:]}", file=sys.stderr)
        return False
    return True


def post_question(rec: dict) -> bool:
    if bus_has_question(rec["agent"], rec["topic"], rec["id"]):
        return True
    payload = dict(rec.get("extra") or {})
    human = rec.get("recover_kind") == "instructions"
    payload.update({
        "gate_block_id": rec["id"], "gate": rec["gate"], "key": rec["key"],
        "question": (f"Cổng {rec['gate']} đang CHẶN ({rec['key']}): {rec['reason']} — "
                     f"chủ xử lý {rec['owner']}, hạn {rec['deadline']} ICT. "
                     f"Phục hồi{' (CHỈ DẪN cho người)' if human else ''}: {rec['recover']}"),
        "owner": rec["owner"], "deadline_ict": rec["deadline"], "expires_ict": rec["expires_at"],
        "close_when": f"probe rc=0: {rec['probe']} (sweep tự đóng qua close_bus_question.py)",
        "urgency": "high",
    })
    payload["recover_instructions" if human else "recover_cmd"] = rec["recover"]
    if rec.get("next_steps"):
        payload["next_step_when_probe_rc"] = rec["next_steps"]
    return append(rec["agent"], "question", rec["topic"], payload, rec["id"])


def post_ack(rec: dict) -> bool:
    """status triaged-needs-human (ops_health_check ACK_PREFIX) — chủ đã gán + sweep đang nhắc
    ⇒ CHECK5 không dispatch Wags. suppress_days phủ tới hết hạn VÀ tối thiểu 2 ngày (CHECK5 dispatch Wags cho câu hỏi <48h; trần 14 theo checker)."""
    days = (parse_ict(rec["expires_at"]) - parse_ict(rec["opened_at"])).total_seconds() / 86400
    sd = max(2, min(ACK_MAX_SUPPRESS_DAYS, int(days) + 1))   # >=2: CHECK5 xét câu hỏi 48h
    return append(rec["agent"], "status", f"{ACK_PREFIX} {rec['topic']}",
                  {"gate_block_id": rec["id"], "suppress_days": sd, "owner": rec["owner"],
                   "note": "gate_block_question: đã gán chủ + hạn, sweep nhắc tới khi probe đóng/hết hạn"},
                  rec["id"])


def finish_posting(path: Path, rec: dict) -> bool:
    if rec["status"] == "posting":
        if not post_question(rec):
            return False
        rec["status"] = "open"
        rec["posted_at"] = now_ict().isoformat(timespec="seconds")
        save(path, rec)
    if not rec.get("ack_posted") and post_ack(rec):
        rec["ack_posted"] = True
        save(path, rec)
    return True


def parse_next_steps(items: list[str]) -> dict:
    out = {}
    for it in items or []:
        rc, sep, text = it.partition("=")
        if not sep or not rc.strip().isdigit() or not text.strip():
            raise ValueError(f"--next-step phải dạng RC=TEXT, thấy {it!r}")
        out[rc.strip()] = text.strip()
    return out


def cmd_open(a) -> int:
    for name in ("gate", "key"):
        if not SLUG.match(getattr(a, name)):
            print(f"gate_block_question: BAD_ARG --{name}={getattr(a, name)!r} (chỉ [A-Za-z0-9._-])",
                  file=sys.stderr)
            return 2
    if bool(a.expires_at) == (a.expires_in_days is not None):
        print("gate_block_question: BAD_ARG cần đúng một trong --expires-at / --expires-in-days",
              file=sys.stderr)
        return 2
    now = now_ict()
    expires = parse_ict(a.expires_at) if a.expires_at else now + dt.timedelta(days=a.expires_in_days)
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = state_path(a.gate, a.key)
    rec = {
        "id": f"{a.gate}__{a.key}", "gate": a.gate, "key": a.key, "agent": a.agent,
        "topic": a.topic or f"gate-block-{a.gate}-{a.key}", "owner": a.owner,
        "deadline": parse_ict(a.deadline).strftime("%Y-%m-%dT%H:%M"),
        "expires_at": expires.strftime("%Y-%m-%dT%H:%M"), "max_reminders": a.max_reminders,
        "recover": a.recover, "recover_kind": a.recover_kind,
        "next_steps": parse_next_steps(a.next_step), "probe": a.probe,
        "reason": " ".join(a.reason.split())[:400], "thread": a.thread,
        "remind_every_min": a.remind_every_min, "extra": json.loads(a.extra) if a.extra else {},
        "status": "posting", "opened_at": now.isoformat(timespec="seconds"),
        "reminders": 0, "last_reminded_at": None, "ack_posted": False,
    }
    if not claim(path, rec):
        try:
            rec = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            # Sổ hỏng ⇒ KHÔNG post (thà thiếu hơn trùng).
            print(f"gate_block_question: STATE_UNREADABLE {path.name}: {exc}", file=sys.stderr)
            return 1
        if rec.get("status") != "posting":
            if rec.get("status") == "open":
                finish_posting(path, rec)   # chỉ bù ack nếu lần trước hụt
            print(f"gate_block_question: ALREADY_{str(rec.get('status')).upper()} {rec['id']}")
            return 0
    if not finish_posting(path, rec):
        return 1
    print(f"gate_block_question: OPENED {rec['agent']}/{rec['topic']} owner={rec['owner']} "
          f"deadline={rec['deadline']} expires={rec['expires_at']}")
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


def run_probe(cmd: str, opened_at: str) -> tuple[int, str]:
    env = dict(os.environ, GATE_BLOCK_OPENED_AT=opened_at)
    try:
        r = subprocess.run(["bash", "-c", cmd], cwd=WC_ROOT, capture_output=True, text=True,
                           timeout=PROBE_TIMEOUT_S, env=env)
        out = " ".join(((r.stdout or "") + " " + (r.stderr or "")).split())
        return r.returncode, out[-300:]
    except subprocess.TimeoutExpired:
        return 124, f"probe timeout {PROBE_TIMEOUT_S}s"
    except OSError as exc:
        return 127, f"probe không chạy được: {exc}"


def send(msg: str, thread: str) -> bool:
    """True nếu ÍT NHẤT một kênh nhận thật (rc=0). Lỗi notify KHÔNG được tính là đã nhắc."""
    ok = False
    for argv in ([str(ROOT / "bin" / "notify.sh"), msg],
                 [str(ROOT / "bin" / "notify_thread.sh"), msg, thread] if thread else None):
        if not argv:
            continue
        try:
            r = subprocess.run(argv, capture_output=True, timeout=TOOL_TIMEOUT_S)
            ok = ok or r.returncode == 0
            if r.returncode != 0:
                print(f"gate_block_question: NOTIFY_FAILED {Path(argv[0]).name} rc={r.returncode}",
                      file=sys.stderr)
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"gate_block_question: NOTIFY_FAILED {Path(argv[0]).name}: {exc}", file=sys.stderr)
    return ok


def remind(path: Path, rec: dict, now: dt.datetime, probe_rc: int, probe_out: str, dry: bool) -> None:
    last = rec.get("last_reminded_at")
    if last and now - dt.datetime.fromisoformat(last) < dt.timedelta(minutes=rec["remind_every_min"]):
        print(f"gate_block_question: STILL_OPEN {rec['id']} (nhắc gần đây, bỏ qua lượt này)")
        return
    mins = int((parse_ict(rec["deadline"]) - now).total_seconds() // 60)
    when = f"còn {mins} phút" if mins >= 0 else f"QUÁ HẠN {-mins} phút"
    step = (rec.get("next_steps") or {}).get(str(probe_rc))
    how = f"BƯỚC KẾ: {step}" if step else f"phục hồi: {rec['recover']}"
    n = int(rec.get("reminders") or 0) + 1
    msg = (f"⏰ CỔNG CHẶN CHƯA PHỤC HỒI — {rec['gate']} [{rec['key']}] · chủ: {rec['owner']} · "
           f"hạn {rec['deadline']} ICT ({when}) · {how} · probe rc={probe_rc}: {probe_out[-160:]} · "
           f"nhắc {n}/{rec.get('max_reminders', DEFAULT_MAX_REMINDERS)}, dừng lúc {rec['expires_at']} · "
           f"bus: {rec['agent']}/{rec['topic']}")
    print(f"gate_block_question: REMIND {rec['id']} — {msg}")
    if dry:
        return
    # Ghi sổ TRƯỚC khi gửi (§5): sổ không ghi được (đĩa đầy/read-only) ⇒ save() nổ, KHÔNG gửi — thà
    # im lặng một lượt hơn nhắc lặp mỗi 15 phút. Gửi hỏng ⇒ hoàn tác để lượt sau gửi lại.
    prev = (rec.get("reminders"), rec.get("last_reminded_at"))
    rec["reminders"] = n
    rec["last_reminded_at"] = now.isoformat(timespec="seconds")
    save(path, rec)
    if not send(msg, rec.get("thread")):
        rec["reminders"], rec["last_reminded_at"] = prev
        save(path, rec)
        print(f"gate_block_question: REMIND_UNDELIVERED {rec['id']} — không kênh nào nhận, lượt sau gửi lại")


def expire(path: Path, rec: dict, now: dt.datetime, why: str, probe_rc: int, probe_out: str, dry: bool) -> None:
    msg = (f"🛑 NGỪNG NHẮC — cổng {rec['gate']} [{rec['key']}] vẫn CHƯA phục hồi ({why}) · chủ: "
           f"{rec['owner']} · probe rc={probe_rc}: {probe_out[-160:]} · đây là tin CUỐI; câu hỏi bus "
           f"{rec['agent']}/{rec['topic']} vẫn MỞ — đóng tay bằng close_bus_question.py khi xử lý xong")
    print(f"gate_block_question: EXPIRED {rec['id']} — {msg}")
    if dry:
        return
    # Ghi status expired TRƯỚC khi gửi tin cuối: sổ read-only ⇒ save() nổ, không gửi (không lặp tin cuối).
    rec.update(status="expired", expired_at=now.isoformat(timespec="seconds"), expired_why=why)
    save(path, rec)
    rec["final_notice_delivered"] = send(msg, rec.get("thread"))


def sweep_one(path: Path, dry: bool) -> None:
    rec = json.loads(path.read_text(encoding="utf-8"))
    st = rec.get("status")
    now = now_ict()
    if st in DONE:
        done_at = rec.get("closed_at") or rec.get("expired_at")
        if not dry and done_at and now - dt.datetime.fromisoformat(done_at) > dt.timedelta(days=RETAIN_DAYS):
            path.unlink()
            print(f"gate_block_question: PRUNED {rec['id']} ({st} > {RETAIN_DAYS} ngày)")
        return
    if st not in ("posting", "open"):
        raise ValueError(f"status lạ {st!r}")
    if dry and st == "posting":
        print(f"gate_block_question: POSTING_RETRY_PENDING {rec['id']} (dry-run, không post)")
        return
    if not dry and not finish_posting(path, rec):
        # Post bus hỏng liên tục ⇒ sổ 'posting' không được nằm vĩnh viễn: tới hạn thì expired
        # (câu hỏi CHƯA từng lên bus — nói rõ để người biết cổng vẫn chặn mà không có câu hỏi).
        if now >= parse_ict(rec["expires_at"]):
            rec.update(status="expired", expired_at=now.isoformat(timespec="seconds"),
                       expired_why="hết hạn khi vẫn chưa post được question lên bus (POST_FAILED liên tục)")
            save(path, rec)
            print(f"gate_block_question: EXPIRED_UNPOSTED {rec['id']} — chưa từng post được question; "
                  f"cổng vẫn chặn, xử lý tay")
            return
        print(f"gate_block_question: POSTING_RETRY_PENDING {rec['id']}")
        return
    ref = f"{rec['agent']}/{rec['topic']}"
    if still_pending(rec["agent"], rec["topic"]) is False:
        rec.update(status="closed", closed_at=now.isoformat(timespec="seconds"),
                   closed_how="bus: audit chính thống không còn thấy pending (đóng ngoài helper)")
        if not dry:
            save(path, rec)
        print(f"gate_block_question: CLOSED_EXTERNALLY {ref}")
        return
    rc, out = run_probe(rec["probe"], rec["opened_at"])
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
        if c.returncode == 0 and CLOSED_LINE.search(c.stdout or ""):
            rec.update(status="closed", closed_at=now.isoformat(timespec="seconds"),
                       closed_how=f"probe rc=0: {out}")
            save(path, rec)
            print(f"gate_block_question: CLOSED {ref}")
            return
        # close_bus_question chặn (rollup/substring rc=4/5) hoặc lỗi ⇒ KHÔNG ép đóng; nhắc kèm lý do.
        out = f"probe rc=0 nhưng close_bus_question rc={c.returncode}: {' '.join(text.split())[-200:]}"
    cap = int(rec.get("max_reminders") or DEFAULT_MAX_REMINDERS)
    if now >= parse_ict(rec["expires_at"]):
        expire(path, rec, now, f"hết hạn nhắc {rec['expires_at']} ICT", rc, out, dry)
    elif int(rec.get("reminders") or 0) >= cap:
        expire(path, rec, now, f"đạt trần {cap} lần nhắc", rc, out, dry)
    else:
        remind(path, rec, now, rc, out, dry)
    if not dry:
        save(path, rec)


def cmd_sweep(a) -> int:
    if not STATE_DIR.is_dir():
        print("gate_block_question: NOTHING_OPEN (chưa có sổ)")
        return 0
    lock = open(STATE_DIR / ".sweep.lock", "w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("gate_block_question: SWEEP_BUSY (sweep khác đang chạy — bỏ lượt này)")
        return 0
    bad = 0
    if not a.dry_run:
        for tmp in STATE_DIR.glob(TMP_PREFIX + "*"):
            try:
                if time.time() - tmp.stat().st_mtime > TMP_MAX_AGE_S:
                    tmp.unlink()
                    print(f"gate_block_question: PRUNED_TMP {tmp.name}")
            except OSError:
                pass
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
              f"expires={r.get('expires_at')} reminders={r.get('reminders', 0)}")
    return 0


def opened_since(a) -> dt.datetime | None:
    s = a.since or os.environ.get("GATE_BLOCK_OPENED_AT")
    return parse_ict(s) if s else None


def mtime_ict(p: Path) -> dt.datetime:
    return dt.datetime.fromtimestamp(p.stat().st_mtime, ICT)


def cmd_probe_approval(a) -> int:
    """Phục hồi cổng approval = plan ĐÃ duyệt (đúng hàm bot dùng để chặn) VÀ bot ĐÃ chạy lại SAU
    lúc mở câu hỏi (journal executor ghi SAU opened_at). Chỉ "đã duyệt" chưa đủ — retro 10-19:
    duyệt 09:19, bot phải có người chạy lại 09:25. Journal có từ trước lúc mở (lượt bot sớm hơn)
    KHÔNG chứng minh gì."""
    sys.path.insert(0, str(WC_ROOT))
    try:
        from trading_bot.plan import load_plan, approval_block_reason
        plan = load_plan(a.date, account=a.account)
    except Exception as exc:
        print(f"probe approval: ERROR {type(exc).__name__}: {exc}")
        return 2
    if plan is None:
        print(f"probe approval: KHÔNG CÓ PLAN {a.account} {a.date}")
        return 12
    reason = approval_block_reason(plan)
    if reason:
        print(f"probe approval: VẪN CHẶN — {reason}")
        return 10
    if not plan.orders:
        print(f"probe approval: OK plan {a.account} {a.date} không còn lệnh nào — không còn gì để thực thi")
        return 0
    since = opened_since(a)
    journal = WC_ROOT / "data" / "execution_logs" / f"exec_{a.account}_{a.date}_journal.csv"
    if not journal.exists() or since is None or mtime_ict(journal) <= since:
        print(f"probe approval: hết bị cổng chặn (approved_by={plan.approved_by!r}) nhưng {journal.name} "
              f"{'chưa có' if not journal.exists() else 'không ghi SAU lúc mở ' + str(since)} — bot CHƯA chạy lại")
        return 11
    print(f"probe approval: OK approved_by={plan.approved_by!r}, {journal.name} ghi lúc "
          f"{mtime_ict(journal).isoformat(timespec='seconds')} > mở {since.isoformat(timespec='seconds')}")
    return 0


def plan_content_hash(p: Path) -> str:
    """Y hệt plan_content_hash() của send_plan_report.sh (bỏ khoá approv*/mafee*/requires_user_approval)."""
    plan = json.loads(p.read_text(encoding="utf-8"))
    if isinstance(plan, dict):
        plan = {k: v for k, v in plan.items()
                if not (k.startswith("approv") or k.startswith("mafee") or k == "requires_user_approval")}
    return hashlib.md5(json.dumps(plan, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def cmd_probe_plan_t1(a) -> int:
    """Phục hồi plan-t1 = marker 'đã gửi' của send_plan_report được ghi SAU lúc mở (mtime VÀ
    sent_at) VÀ content_md5 của nó khớp plan hiện tại. Marker bản cũ (gửi 21:00 rồi plan đổi/hỏng)
    KHÔNG đóng câu hỏi."""
    since = opened_since(a)
    marker = Path(a.marker_dir) / f"{a.account}_{a.date}.json"
    plan = Path(a.plan_dir) / f"plan_{a.account}_{a.date}.json"
    if since is None:
        print("probe plan-t1: thiếu --since/GATE_BLOCK_OPENED_AT — không chứng minh được độ mới")
        return 11
    if not marker.is_file():
        print(f"probe plan-t1: chưa có marker {marker.name}")
        return 11
    try:
        m = json.loads(marker.read_text(encoding="utf-8"))
        sent = dt.datetime.strptime(str(m.get("sent_at", "")).replace(" ICT", ""),
                                    "%Y-%m-%d %H:%M").replace(tzinfo=ICT)
        cur = plan_content_hash(plan) if plan.is_file() else ""
    except (OSError, ValueError) as exc:
        print(f"probe plan-t1: ERROR {type(exc).__name__}: {exc}")
        return 2
    mt = mtime_ict(marker)
    # sent_at chỉ có phút ⇒ so với opened_at làm tròn xuống phút; mtime mới là mốc chính xác.
    if mt <= since or sent < since.replace(second=0, microsecond=0):
        print(f"probe plan-t1: marker CŨ (mtime {mt.isoformat(timespec='seconds')}, sent_at {m.get('sent_at')}) "
              f"≤ lúc mở {since.isoformat(timespec='seconds')}")
        return 11
    if not cur or m.get("content_md5") != cur:
        print(f"probe plan-t1: marker md5 {m.get('content_md5')} ≠ plan hiện tại {cur or '<không có ' + plan.name + '>'}")
        return 11
    print(f"probe plan-t1: OK gửi {m.get('sent_at')} (sau lúc mở), md5 {cur} khớp {plan.name}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    o = sub.add_parser("open")
    for f in ("--gate", "--key", "--owner", "--deadline", "--recover", "--probe", "--reason"):
        o.add_argument(f, required=True)
    o.add_argument("--expires-at", default="")
    o.add_argument("--expires-in-days", type=float)
    o.add_argument("--max-reminders", type=int, default=DEFAULT_MAX_REMINDERS)
    o.add_argument("--recover-kind", choices=["cmd", "instructions"], default="cmd")
    o.add_argument("--next-step", action="append", default=[], help="RC=TEXT, lặp được")
    o.add_argument("--agent", default="Mike")
    o.add_argument("--topic", default="", help="giữ topic cũ của cổng (tương thích checker); mặc định gate-block-<gate>-<key>")
    o.add_argument("--thread", default="", help="registry notify_thread.sh cho lời nhắc")
    o.add_argument("--remind-every-min", type=int, default=120)
    o.add_argument("--extra", default="", help="JSON object gộp vào payload question")
    s = sub.add_parser("sweep")
    s.add_argument("--dry-run", action="store_true")
    sub.add_parser("list")
    p = sub.add_parser("probe")
    p.add_argument("kind", choices=["approval", "plan-t1"])
    p.add_argument("--account", required=True)
    p.add_argument("--date", required=True)
    p.add_argument("--since", default="", help="mặc định env GATE_BLOCK_OPENED_AT (sweep đặt)")
    p.add_argument("--marker-dir", default="")
    p.add_argument("--plan-dir", default="")
    # argv có byte không phải UTF-8 (nhãn từ output cổng bị cắt giữa ký tự) ⇒ surrogate làm json.dumps
    # / ghi sổ nổ; thay bằng U+FFFD để sổ + câu hỏi vẫn mở được (thà mất 1 ký tự hơn mất cả câu hỏi).
    argv = [x.encode("utf-8", "surrogateescape").decode("utf-8", "replace")
            for x in (sys.argv[1:] if argv is None else argv)]
    a = ap.parse_args(argv)
    if a.cmd == "open":
        return cmd_open(a)
    if a.cmd == "sweep":
        return cmd_sweep(a)
    if a.cmd == "list":
        return cmd_list(a)
    if a.kind == "plan-t1":
        if not (a.marker_dir and a.plan_dir):
            ap.error("probe plan-t1 cần --marker-dir và --plan-dir")
        return cmd_probe_plan_t1(a)
    return cmd_probe_approval(a)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"gate_block_question: ERROR {type(exc).__name__}: {exc}", file=sys.stderr)
        raise SystemExit(2)
