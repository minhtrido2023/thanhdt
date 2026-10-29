#!/usr/bin/env python3
"""Selfcheck cho bin/gate_block_question.py + 3 điểm wire (run_bot / send_plan_report / cadence).

Chạy: python3 bin/gate_block_question_selfcheck.py            (3 TZ + mutation)
      python3 bin/gate_block_question_selfcheck.py --core [--no-wiring] [--target H]   (1 lượt)
Mọi I/O ra ngoài (append_event/notify/audit/close) là STUB trong fixture root tạm — KHÔNG chạm
bus/Telegram thật. Exit 0 = PASS.
"""
from __future__ import annotations

import datetime as _dt
import fcntl
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
HELPER = HERE / "gate_block_question.py"
ICT = ZoneInfo("Asia/Ho_Chi_Minh")
FAILS: list[str] = []
TMP: list[Path] = []


def check(cond, name):
    print(("  ok   " if cond else "  FAIL ") + name)
    if not cond:
        FAILS.append(name)


STUB_APPEND = r'''#!/usr/bin/env python3
import json, os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
agent, et, topic, payload = sys.argv[1:5]
if os.path.exists(os.path.join(root, "APPEND_FAIL")) or (
        et == "status" and os.path.exists(os.path.join(root, "APPEND_FAIL_STATUS"))):
    print("stub append fail", file=sys.stderr); sys.exit(1)
os.makedirs(os.path.join(root, "bus", "inbox"), exist_ok=True)
with open(os.path.join(root, "bus", "inbox", agent + ".jsonl"), "a") as f:
    f.write(json.dumps({"agent_id": agent, "event_type": et, "topic": topic,
                        "payload": json.loads(payload)}, ensure_ascii=False) + "\n")
'''
STUB_NOTIFY = r'''#!/usr/bin/env bash
echo "$(basename "$0") $*" >> "$(dirname "$0")/../calls.log"
[ -e "$(dirname "$0")/../NOTIFY_FAIL" ] && exit 1
exit 0
'''
STUB_AUDIT = r'''#!/usr/bin/env python3
import glob, json, os, sys
root = os.environ["BUS_AUDIT_ROOT"]
if os.path.exists(os.path.join(root, "AUDIT_BROKEN")):
    print("not json"); sys.exit(3)
qs, res = [], set()
for p in glob.glob(os.path.join(root, "bus", "inbox", "*.jsonl")):
    for line in open(p):
        e = json.loads(line)
        if e["event_type"] == "question":
            qs.append((e["agent_id"], e["topic"]))
        for r in (e.get("payload") or {}).get("resolves", []):
            res.add(r)
pend = [{"agent": a, "topic": t} for a, t in qs if f"{a}/{t}" not in res]
print(json.dumps({"pending": pend})); sys.exit(len(pend))
'''
STUB_CLOSE = r'''#!/usr/bin/env python3
import json, os, sys, subprocess
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
mode_f = os.path.join(root, "CLOSE_MODE")
mode = open(mode_f).read().strip() if os.path.exists(mode_f) else "ok"
ref = sys.argv[1]
if mode == "blocked5":
    print("close_bus_question: BLOCKED stub", file=sys.stderr); sys.exit(5)
if mode == "rc4_says_closed":
    print("close_bus_question: CLOSED " + ref); sys.exit(4)
if mode == "unknown":
    print("close_bus_question: ALREADY_CLOSED_OR_UNKNOWN " + ref); sys.exit(0)
args = sys.argv[2:]
ev = args[args.index("--evidence") + 1]; actor = args[args.index("--actor") + 1]
subprocess.run([os.path.join(root, "bin", "append_event.sh"), actor, "answer", ref.split("/", 1)[1],
                json.dumps({"resolves": [ref], "evidence": ev})], check=True)
with open(os.path.join(root, "calls.log"), "a") as f:
    f.write("close " + ref + " EVIDENCE=" + ev + "\n")
print("close_bus_question: CLOSED " + ref)
'''


def mkroot() -> Path:
    r = Path(tempfile.mkdtemp(prefix="gbq_sc_"))
    TMP.append(r)
    (r / "bin").mkdir()
    for name, body in (("append_event.sh", STUB_APPEND), ("notify.sh", STUB_NOTIFY),
                       ("notify_thread.sh", STUB_NOTIFY), ("bus_question_audit.py", STUB_AUDIT),
                       ("close_bus_question.py", STUB_CLOSE)):
        p = r / "bin" / name
        p.write_text(body)
        p.chmod(0o755)
    return r


def run(target, root, *args, now=None, extra_env=None):
    env = dict(os.environ, GATE_BLOCK_ROOT=str(root), GATE_BLOCK_WC_ROOT=str(root))
    if now:
        env["GATE_BLOCK_NOW"] = now
    env.update(extra_env or {})
    r = subprocess.run([sys.executable, str(target), *args], env=env, capture_output=True,
                       text=True, timeout=60)
    return r.returncode, r.stdout + r.stderr


def events(root, agent="Mike", etype=None):
    p = root / "bus" / "inbox" / f"{agent}.jsonl"
    if not p.exists():
        return []
    return [e for e in map(json.loads, p.read_text().splitlines()) if etype in (None, e["event_type"])]


def questions(root, agent="Mike"):
    return events(root, agent, "question")


def calls(root):
    p = root / "calls.log"
    return p.read_text() if p.exists() else ""


def st(root, rid="approval__2026-10-20-SpaceX"):
    return json.loads((root / "state" / "gate_blocks" / f"{rid}.json").read_text())


def set_st(root, rec, rid="approval__2026-10-20-SpaceX"):
    (root / "state" / "gate_blocks" / f"{rid}.json").write_text(json.dumps(rec))


def open_args(key="2026-10-20-SpaceX", probe="false", every="15", gate="approval",
              expires="2026-10-20T15:00", extra=()):
    return ["open", "--gate", gate, "--key", key, "--owner", "user; Mike",
            "--deadline", "2026-10-20T10:00", "--recover", "bin/run_bot.sh --account SpaceX",
            "--probe", probe, "--reason", "APPROVAL_GATE_BLOCK test", "--thread", "trading_daily",
            "--remind-every-min", every, "--expires-at", expires, "--extra", '{"account":"SpaceX"}',
            *extra]


def ts(s: str) -> float:
    return _dt.datetime.fromisoformat(s).timestamp()


def core(target: Path) -> None:
    T0 = "2026-10-20T09:06:00+07:00"
    # 1-3: mở + idempotent theo (gate,key) + ack triaged-needs-human (B4)
    R = mkroot()
    rc, out = run(target, R, *open_args(), now=T0)
    qs = questions(R)
    check(rc == 0 and "OPENED" in out and len(qs) == 1, "open: OPENED + đúng 1 question")
    check(st(R)["status"] == "open" and st(R)["ack_posted"] is True, "open: sổ status=open + ack_posted")
    p = qs[0]["payload"] if qs else {}
    check(p.get("owner") and p.get("deadline_ict") == "2026-10-20T10:00" and p.get("recover_cmd")
          and p.get("expires_ict") == "2026-10-20T15:00"
          and p.get("gate_block_id") == "approval__2026-10-20-SpaceX" and p.get("account") == "SpaceX",
          "payload có owner/deadline/expires/recover/gate_block_id + extra gộp")
    check(qs and qs[0]["topic"] == "gate-block-approval-2026-10-20-SpaceX", "topic mặc định gate-block-<gate>-<key>")
    acks = events(R, etype="status")
    check(len(acks) == 1 and acks[0]["topic"] == "triaged-needs-human: gate-block-approval-2026-10-20-SpaceX"
          and acks[0]["payload"].get("suppress_days") == 2,
          "B4/vòng3-B3: status 'triaged-needs-human: <topic>' + suppress_days>=2 (CHECK5 xét câu hỏi 48h, kể cả khi hạn trong ngày)")
    ohc = (HERE / "ops_health_check.sh")
    if ohc.exists():
        check('ACK_PREFIX = "triaged-needs-human:"' in ohc.read_text(), "B4: ACK_PREFIX helper khớp ops_health_check.sh")
    rc, out = run(target, R, *open_args(), now=T0)
    check(rc == 0 and "ALREADY_OPEN" in out and len(questions(R)) == 1 and len(events(R, etype="status")) == 1,
          "open lặp cùng gate+key ⇒ KHÔNG mở trùng, không ack trùng")
    run(target, R, *open_args(key="2026-10-20-ZaloPay"), now=T0)
    check(len(questions(R)) == 2, "key khác (account khác) ⇒ question riêng")
    check(not list((R / "state/gate_blocks").glob(".tmp_*")), "claim tmp+link: không sót file .tmp_")

    # 4: bị kill giữa post và ghi sổ ⇒ sổ 'posting' + bus đã có ⇒ không post lại
    rec = st(R); rec["status"] = "posting"; set_st(R, rec)
    run(target, R, *open_args(), now=T0)
    check(len(questions(R)) == 2 and st(R)["status"] == "open",
          "kill sau post: sổ posting + bus đã có ⇒ không post lại, sổ về open")
    # 4b: bus có event cùng gate_block_id nhưng KHÁC topic ⇒ không tính là đã post
    Rb = mkroot()
    subprocess.run([str(Rb / "bin/append_event.sh"), "Mike", "question", "topic-khac",
                    json.dumps({"gate_block_id": "approval__2026-10-20-SpaceX"})], check=True)
    (Rb / "state/gate_blocks").mkdir(parents=True)
    rec = dict(st(R)); rec.update(status="posting", ack_posted=False); set_st(Rb, rec)
    run(target, Rb, *open_args(), now=T0)
    check([q["topic"] for q in questions(Rb)] == ["topic-khac", "gate-block-approval-2026-10-20-SpaceX"],
          "bus_has_question so cả topic: gate_block_id trùng ở topic khác ⇒ vẫn post")

    # 5: append hỏng ⇒ posting, sweep sau post đúng 1 lần; ack hỏng ⇒ sweep bù ack
    R2 = mkroot(); (R2 / "APPEND_FAIL").write_text("1")
    rc, out = run(target, R2, *open_args(), now=T0)
    check(rc != 0 and st(R2)["status"] == "posting" and not questions(R2),
          "append lỗi ⇒ rc≠0, sổ posting, chưa có question")
    rc, out = run(target, R2, "sweep", "--dry-run", now=T0)
    check(not questions(R2) and st(R2)["status"] == "posting" and "POSTING_RETRY_PENDING" in out,
          "N1: sweep --dry-run KHÔNG post bù")
    (R2 / "APPEND_FAIL").unlink(); (R2 / "APPEND_FAIL_STATUS").write_text("1")
    run(target, R2, "sweep", now=T0)
    check(len(questions(R2)) == 1 and st(R2)["status"] == "open" and not st(R2)["ack_posted"],
          "sweep post bù question; ack lỗi ⇒ ack_posted=False")
    (R2 / "APPEND_FAIL_STATUS").unlink()
    run(target, R2, "sweep", now=T0)
    check(len(questions(R2)) == 1 and len(events(R2, etype="status")) == 1 and st(R2)["ack_posted"],
          "sweep sau: không post question lần 2, bù ack đúng 1 lần")

    # 6: probe fail ⇒ nhắc, throttle (biên đúng 15'), quá hạn
    R3 = mkroot()
    run(target, R3, *open_args(probe="exit 1"), now=T0)
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:10:00+07:00")
    check("REMIND" in out and "còn 50 phút" in out and calls(R3).count("notify.sh") == 1
          and "notify_thread.sh" in calls(R3) and st(R3)["reminders"] == 1,
          "probe rc≠0 ⇒ nhắc Telegram+thread, 'còn 50 phút' (ICT), reminders=1")
    rc, out = run(target, R3, "sweep", "--dry-run", now="2026-10-20T09:40:00+07:00")
    check("REMIND" in out and calls(R3).count("notify.sh") == 1 and st(R3)["reminders"] == 1,
          "N1: --dry-run in REMIND nhưng KHÔNG notify, không ghi sổ")
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:24:59+07:00")
    check(calls(R3).count("notify.sh") == 1 and "STILL_OPEN" in out, "throttle: <15' không nhắc lại")
    rc, out = run(target, R3, "sweep", now="2026-10-20T09:25:00+07:00")
    check(calls(R3).count("notify.sh") == 2, "throttle: đúng 15' ⇒ nhắc lại (biên <, không <=)")
    rc, out = run(target, R3, "sweep", now="2026-10-20T03:20:00+00:00")  # = 10:20 ICT
    check(calls(R3).count("notify.sh") == 3 and "QUÁ HẠN 20 phút" in out and "còn -" not in out,
          "qua hạn ⇒ nhắc 'QUÁ HẠN 20 phút' (now nhập UTC, so theo ICT)")
    check(not events(R3, etype="answer"), "probe fail KHÔNG BAO GIỜ đóng question")

    # 6b: notify lỗi KHÔNG tính là đã nhắc (N4)
    (R3 / "NOTIFY_FAIL").write_text("1")
    n0 = st(R3)["reminders"]
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:40:00+07:00")
    check("REMIND_UNDELIVERED" in out and st(R3)["reminders"] == n0, "notify lỗi ⇒ REMIND_UNDELIVERED, reminders không tăng")
    (R3 / "NOTIFY_FAIL").unlink()
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:41:00+07:00")
    check(st(R3)["reminders"] == n0 + 1, "notify lỗi lượt trước ⇒ lượt sau (trong 15') vẫn nhắc lại")

    # 7: probe rc=0 ⇒ đóng qua close_bus_question, evidence chứa lệnh probe; probe nhận OPENED_AT
    flag = R3 / "RECOVERED"
    rec = st(R3)
    rec["probe"] = f'test -e {flag} && test "$GATE_BLOCK_OPENED_AT" = "{rec["opened_at"]}" && echo journal-ok'
    set_st(R3, rec)
    flag.write_text("1")
    rc, out = run(target, R3, "sweep", now="2026-10-20T10:50:00+07:00")
    check("CLOSED Mike/gate-block-approval" in out and st(R3)["status"] == "closed"
          and "journal-ok" in calls(R3) and "test -e" in calls(R3),
          "probe rc=0 (nhận GATE_BLOCK_OPENED_AT=opened_at) ⇒ CLOSED, evidence = lệnh + output probe")
    n = calls(R3).count("notify.sh")
    (R3 / "AUDIT_BROKEN").write_text("1")
    rec = st(R3); rec["probe"] = "exit 1"; set_st(R3, rec)
    run(target, R3, "sweep", now="2026-10-20T11:30:00+07:00")
    check(calls(R3).count("notify.sh") == n, "N1: record closed bị bỏ qua kể cả khi audit hỏng")
    (R3 / "AUDIT_BROKEN").unlink()
    rc, out = run(target, R3, *open_args(probe="exit 1"), now="2026-10-20T13:01:00+07:00")
    check("ALREADY_CLOSED" in out and len(questions(R3)) == 1, "block lại cùng ngày sau khi đóng ⇒ không mở câu mới")

    # 7b: probe tương đối chạy với cwd=WC_ROOT
    Rc = mkroot()
    run(target, Rc, *open_args(probe="test -e REL_FLAG"), now=T0)
    (Rc / "REL_FLAG").write_text("1")
    rc, out = run(target, Rc, "sweep", now=T0)
    check(st(Rc)["status"] == "closed", "probe đường dẫn tương đối chạy trong WC_ROOT")

    # 8: probe không chạy được / timeout ⇒ không đóng (N1)
    R4 = mkroot()
    run(target, R4, *open_args(probe="/nonexistent/probe_cmd"), now=T0)
    rc, out = run(target, R4, "sweep", now=T0)
    check("REMIND" in out and st(R4)["status"] == "open", "probe lỗi (rc127) ⇒ nhắc, không đóng")
    Rt = mkroot()
    run(target, Rt, *open_args(probe="sleep 5; true"), now=T0)
    rc, out = run(target, Rt, "sweep", now=T0, extra_env={"GATE_BLOCK_PROBE_TIMEOUT_S": "1"})
    check("probe timeout 1s" in out and "rc=124" in out and st(Rt)["status"] == "open",
          "N1: probe timeout ⇒ rc124, nhắc, KHÔNG đóng")
    Ro = mkroot()
    run(target, Ro, *open_args(probe="true"), now=T0)
    rc, out = run(target, Ro, "sweep", now=T0, extra_env={"GATE_BLOCK_WC_ROOT": str(Ro / "khong_ton_tai")})
    check("probe không chạy được" in out and "rc=127" in out and st(Ro)["status"] == "open",
          "N1: probe OSError (cwd không tồn tại) ⇒ rc127, KHÔNG đóng")

    # 9: người đóng trên bus ⇒ ngừng nhắc; câu cùng topic của agent KHÁC không giữ nó mở
    subprocess.run([str(R4 / "bin/append_event.sh"), "Winston", "question",
                    "gate-block-approval-2026-10-20-SpaceX", "{}"], check=True)
    subprocess.run([str(R4 / "bin/append_event.sh"), "Mike", "answer", "x",
                    json.dumps({"resolves": ["Mike/gate-block-approval-2026-10-20-SpaceX"]})], check=True)
    n = calls(R4).count("notify.sh")
    rc, out = run(target, R4, "sweep", now="2026-10-20T12:00:00+07:00")
    check("CLOSED_EXTERNALLY" in out and calls(R4).count("notify.sh") == n,
          "đóng tay trên bus ⇒ CLOSED_EXTERNALLY (lọc đúng agent), ngừng nhắc")

    # 10: audit hỏng ⇒ coi như còn mở (nhắc), không đóng
    R5 = mkroot()
    run(target, R5, *open_args(probe="exit 1"), now=T0)
    (R5 / "AUDIT_BROKEN").write_text("1")
    rc, out = run(target, R5, "sweep", now=T0)
    check("AUDIT_UNREADABLE" in out and "REMIND" in out and st(R5)["status"] == "open",
          "audit hỏng ⇒ fail-loud: vẫn nhắc, không tự đóng")

    # 11: close_bus_question chặn/không in đúng dòng CLOSED ⇒ không ép đóng (N5)
    for mode, want in (("blocked5", "close_bus_question rc=5"), ("rc4_says_closed", "close_bus_question rc=4"),
                       ("unknown", "ALREADY_CLOSED_OR_UNKNOWN")):
        R6 = mkroot()
        run(target, R6, *open_args(probe="true"), now=T0)
        (R6 / "CLOSE_MODE").write_text(mode)
        rc, out = run(target, R6, "sweep", now=T0)
        check(st(R6)["status"] == "open" and want in out, f"N5: close mode={mode} ⇒ giữ open + nhắc lý do")

    # 12-13: slug xấu / sổ hỏng / thiếu expiry
    R7 = mkroot()
    rc, out = run(target, R7, *open_args(key="2026-10-20 Space X"), now=T0)
    check(rc == 2 and not questions(R7), "key có ký tự lạ ⇒ rc2, không post")
    a = open_args(); i = a.index("--expires-at"); del a[i:i + 2]
    rc, out = run(target, R7, *a, now=T0)
    check(rc == 2 and "expires" in out and not questions(R7), "B1: thiếu --expires-at/--expires-in-days ⇒ rc2")
    (R7 / "state/gate_blocks").mkdir(parents=True, exist_ok=True)
    (R7 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").write_text("{cut")
    rc, out = run(target, R7, *open_args(), now=T0)
    check(rc == 1 and "STATE_UNREADABLE" in out and not questions(R7), "sổ hỏng ⇒ không post (thà thiếu hơn trùng)")

    # 13b: một record hỏng không chặn record khác (N1)
    run(target, R7, *open_args(key="2026-10-20-ZaloPay", probe="exit 1"), now=T0)
    rc, out = run(target, R7, "sweep", now=T0)
    check(rc == 1 and "SWEEP_ERROR approval__2026-10-20-SpaceX.json" in out
          and "REMIND approval__2026-10-20-ZaloPay" in out,
          "N1: record hỏng ⇒ SWEEP_ERROR rc1 nhưng record khác vẫn được nhắc")

    # 14: --topic giữ topic cũ; reason cắt 400
    R8 = mkroot()
    args = open_args(gate="plan-t1-not-ready", key="2026-10-21-SpaceX") + ["--topic", "plan-t1-not-ready-SpaceX"]
    i = args.index("--reason"); args[i + 1] = "x" * 1000
    run(target, R8, *args, now=T0)
    check([q["topic"] for q in questions(R8)] == ["plan-t1-not-ready-SpaceX"], "--topic giữ topic cũ")
    check(len(st(R8, "plan-t1-not-ready__2026-10-21-SpaceX")["reason"]) == 400, "reason cắt 400 ký tự")

    # 14b: đồng hồ THẬT (không GATE_BLOCK_NOW) phải neo ICT, độc lập TZ host (§16)
    Rr = mkroot()
    now = _dt.datetime.now(ICT)
    a = open_args(probe="exit 1", expires=(now + _dt.timedelta(hours=6)).strftime("%Y-%m-%dT%H:%M"))
    a[a.index("--deadline") + 1] = (now + _dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M")
    run(target, Rr, *a)
    rc, out = run(target, Rr, "sweep")
    m = re.search(r"còn (\d+) phút", out)
    check(bool(m) and 170 <= int(m.group(1)) <= 180,
          f"đồng hồ thật neo ICT: hạn +3h ⇒ 'còn ~179 phút' (thấy {m.group(0) if m else out[-80:]!r})")

    # 15: B1 — EXPIRED theo thời gian: 1 tin cuối rồi im hẳn
    R10 = mkroot()
    run(target, R10, *open_args(probe="exit 1"), now=T0)
    run(target, R10, "sweep", now="2026-10-20T14:50:00+07:00")
    n = calls(R10).count("notify.sh")
    rc, out = run(target, R10, "sweep", now="2026-10-20T15:00:00+07:00")
    check("EXPIRED" in out and "tin CUỐI" in calls(R10) and calls(R10).count("notify.sh") == n + 1
          and st(R10)["status"] == "expired", "B1: tới expires_at ⇒ EXPIRED + đúng 1 tin cuối")
    for t in ("2026-10-20T16:00:00+07:00", "2026-10-21T09:00:00+07:00"):
        run(target, R10, "sweep", now=t)
    check(calls(R10).count("notify.sh") == n + 1 and not events(R10, etype="answer"),
          "B1: sau EXPIRED sweep im lặng hẳn, không tự đóng question")
    rc, out = run(target, R10, *open_args(probe="exit 1"), now="2026-10-20T16:00:00+07:00")
    check("ALREADY_EXPIRED" in out and len(questions(R10)) == 1, "B1: open lại cùng key sau EXPIRED ⇒ không mở mới")
    # 15b: dry-run không expire
    R11 = mkroot()
    run(target, R11, *open_args(probe="exit 1"), now=T0)
    rc, out = run(target, R11, "sweep", "--dry-run", now="2026-10-20T15:30:00+07:00")
    check("EXPIRED" in out and st(R11)["status"] == "open" and "notify" not in calls(R11),
          "B1: --dry-run in EXPIRED nhưng không ghi sổ/không notify")
    # 15c: probe phục hồi đúng lúc hết hạn ⇒ ĐÓNG, không expire
    (R11 / "OK").write_text("1")
    rec = st(R11); rec["probe"] = f"test -e {R11 / 'OK'}"; set_st(R11, rec)
    run(target, R11, "sweep", now="2026-10-20T15:30:00+07:00")
    check(st(R11)["status"] == "closed", "B1: hết hạn nhưng probe rc=0 ⇒ CLOSED (ưu tiên đóng)")

    # 16: B1 — trần số lần nhắc
    R12 = mkroot()
    run(target, R12, *open_args(probe="exit 1", extra=("--max-reminders", "2")), now=T0)
    for t in ("09:10", "09:30", "09:50", "10:10", "10:30"):
        run(target, R12, "sweep", now=f"2026-10-20T{t}:00+07:00")
    c = calls(R12)
    check(c.count("notify.sh") == 3 and c.count("CỔNG CHẶN CHƯA PHỤC HỒI") == 4 and "đạt trần 2" in c
          and st(R12)["status"] == "expired" and st(R12)["reminders"] == 2,
          "B1: --max-reminders 2 ⇒ 2 lời nhắc + 1 tin cuối rồi dừng")

    # 17: --expires-in-days + suppress_days cho delivery
    R13 = mkroot()
    a = open_args(gate="delivery", key="X_weekly_report_2026-10-16.md")
    i = a.index("--expires-at"); a[i:i + 2] = ["--expires-in-days", "3"]
    run(target, R13, *a, now=T0)
    r13 = st(R13, "delivery__X_weekly_report_2026-10-16.md")
    check(r13["expires_at"] == "2026-10-23T09:06" and [e["payload"].get("suppress_days") for e in events(R13, etype="status")] == [4],
          "--expires-in-days 3 ⇒ expires +3 ngày, ack suppress_days=4")

    # 18: B3 — recover-kind instructions + next-step theo rc probe
    R14 = mkroot()
    pr = R14 / "prc"; pr.write_text("10")
    run(target, R14, *open_args(probe=f'exit $(cat {pr})', extra=(
        "--recover-kind", "instructions", "--next-step", "11=Mike: chạy run_bot.sh --auto-otp")), now=T0)
    p = questions(R14)[0]["payload"]
    check("recover_cmd" not in p and p.get("recover_instructions") and "CHỈ DẪN cho người" in p["question"]
          and p.get("next_step_when_probe_rc") == {"11": "Mike: chạy run_bot.sh --auto-otp"},
          "B3: instructions ⇒ payload KHÔNG có recover_cmd, có recover_instructions + next_step")
    rc, out = run(target, R14, "sweep", now="2026-10-20T09:10:00+07:00")
    check("BƯỚC KẾ" not in out and "phục hồi: bin/run_bot.sh" in out, "B3: probe rc=10 ⇒ nhắc chỉ dẫn duyệt, chưa có bước Mike")
    pr.write_text("11")
    rc, out = run(target, R14, "sweep", now="2026-10-20T09:30:00+07:00")
    check("BƯỚC KẾ: Mike: chạy run_bot.sh --auto-otp" in out, "B3: probe rc=11 ⇒ nhắc BƯỚC KẾ của Mike")
    rc, _ = run(target, R14, *open_args(key="k2", extra=("--next-step", "abc")), now=T0)
    check(rc == 2, "--next-step sai dạng ⇒ rc2")

    # 19: N2 flock — sweep đang chạy ⇒ lượt khác bỏ qua
    R15 = mkroot()
    run(target, R15, *open_args(probe="exit 1"), now=T0)
    with open(R15 / "state/gate_blocks/.sweep.lock", "w") as lk:
        fcntl.flock(lk, fcntl.LOCK_EX)
        rc, out = run(target, R15, "sweep", now=T0)
    check(rc == 0 and "SWEEP_BUSY" in out and "notify" not in calls(R15), "N2: flock — sweep song song bỏ lượt")

    # 20: N8 dọn record closed/expired > 30 ngày
    R16 = mkroot()
    run(target, R16, *open_args(probe="exit 1"), now=T0)
    run(target, R16, *open_args(key="old2", probe="exit 1"), now=T0)
    rec = st(R16); rec.update(status="closed", closed_at="2026-09-19T09:00:00+07:00"); set_st(R16, rec)
    rec = st(R16, "approval__old2"); rec.update(status="expired", expired_at="2026-09-21T09:00:00+07:00")
    set_st(R16, rec, "approval__old2")
    rc, out = run(target, R16, "sweep", "--dry-run", now="2026-10-20T09:30:00+07:00")
    check((R16 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").exists(), "N8: dry-run không xoá")
    rc, out = run(target, R16, "sweep", now="2026-10-20T09:30:00+07:00")
    check(not (R16 / "state/gate_blocks/approval__2026-10-20-SpaceX.json").exists() and "PRUNED" in out
          and (R16 / "state/gate_blocks/approval__old2.json").exists(),
          "N8: closed 31 ngày ⇒ PRUNED; expired 29 ngày ⇒ giữ")

    # 20b: B4 tích hợp — chạy KHỐI CHECK5 THẬT của ops_health_check.sh trên bus giả: question có ack
    # của helper ⇒ dòng 'ĐÃ TRIAGE' [WARN-ONLY], KHÔNG nằm trong danh sách routable; control không ack ⇒ routable.
    ohc = HERE / "ops_health_check.sh"
    mb = re.search(r"^# CHECK5_BEGIN.*?\n(.*?)^# CHECK5_END", ohc.read_text(), re.S | re.M) if ohc.exists() else None
    check(bool(mb), "B4: trích được khối CHECK5 của ops_health_check.sh")
    if mb:
        Wr = Path(tempfile.mkdtemp(prefix="gbq_ohc_")); TMP.append(Wr)
        Rw = Wr / "mike"; Rw.mkdir()
        Rm = mkroot(); shutil.copytree(Rm / "bin", Rw / "bin")
        (Rw / "agents").mkdir()
        run(target, Rw, *open_args(key="2026-10-20-SpaceX", probe="exit 1"))
        three_h = (_dt.datetime.now(_dt.timezone.utc) - _dt.timedelta(hours=3)).strftime("%Y-%m-%dT%H:%M:%SZ")
        inbox = Rw / "bus/inbox/Mike.jsonl"
        evs = [dict(e, ts=three_h, event_id=f"e{i}") for i, e in enumerate(map(json.loads, inbox.read_text().splitlines()))]
        evs.append({"agent_id": "Mike", "event_type": "question", "topic": "control-khong-ack", "ts": three_h,
                    "payload": {}, "event_id": "ctl"})
        inbox.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in evs))
        lines = []
        ns = {"glob": __import__("glob"), "gzip": __import__("gzip"), "json": json, "os": os, "re": re,
              "wc_root": str(Wr), "W": lambda m: lines.append("⚠️ " + m), "OK": lambda m: lines.append("✅ " + m),
              "lines": lines}
        try:
            exec(compile(mb.group(1), str(ohc) + ":CHECK5", "exec"), ns)
        except Exception as exc:
            lines.append(f"EXC {type(exc).__name__}: {exc}")
        human = "\n".join(ln for ln in lines if "ĐÃ TRIAGE" in ln)
        pend = "\n".join(ln for ln in lines if "CHƯA thấy answer" in ln)
        check("gate-block-approval-2026-10-20-SpaceX" in human and "gate-block-approval-2026-10-20-SpaceX" not in pend
              and "control-khong-ack" in pend,
              "B4: CHECK5 thật — question có ack helper ⇒ ĐÃ TRIAGE (không dispatch Wags); control ⇒ routable "
              f"[{' | '.join(lines)[:300]!r}]")

    # 21: probe approval (module trading_bot giả) — B2 journal phải MỚI HƠN lúc mở
    R9 = mkroot()
    (R9 / "trading_bot").mkdir()
    (R9 / "trading_bot/__init__.py").write_text("")
    (R9 / "trading_bot/plan.py").write_text(
        "import os, types\n"
        "def load_plan(d, account):\n"
        "    m = os.environ.get('FAKE_PLAN')\n"
        "    return None if m == 'none' else types.SimpleNamespace(approved_by=(m in ('ok', 'hold')) and 'user' or None,\n"
        "                                                          orders=[] if m == 'hold' else [1])\n"
        "def approval_block_reason(p):\n"
        "    return None if p.approved_by else 'chua duyet'\n")
    since = "2026-10-20T09:06:00+07:00"
    pa = ["probe", "approval", "--account", "SpaceX", "--date", "2026-10-20", "--since", since]
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "none"})[0] == 12, "probe approval: không có plan ⇒ 12 (≠ còn chặn)")
    rc, out = run(target, R9, *pa, extra_env={"FAKE_PLAN": "blocked"})
    check(rc == 10 and "VẪN CHẶN — chua duyet" in out, "probe approval: chưa duyệt ⇒ 10 + lý do thật")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11, "probe approval: duyệt nhưng chưa có journal ⇒ 11")
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "hold"})[0] == 0, "probe approval: plan sửa thành HOLD (0 lệnh) ⇒ 0")
    j = R9 / "data/execution_logs/exec_SpaceX_2026-10-20_journal.csv"
    HDR = "ts,event,parent_id,ticker,side,child_oid,qty,price,filled_total,book,play_type,note\n"

    def jrow(t, ev):
        return f"{t},{ev},P-1,VPB,sell,1,100,20000,0,LAG,X,n\n"

    j.parent.mkdir(parents=True); j.write_text(HDR + jrow("2026-10-20T09:05:30", "PLACE"))
    os.utime(j, (ts("2026-10-20T09:05:30+07:00"),) * 2)
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11,
          "B2: journal có TRƯỚC lúc mở (lượt bot sớm) ⇒ 11, KHÔNG phục hồi")
    check(run(target, R9, *pa[:-2], extra_env={"FAKE_PLAN": "ok"})[0] == 11,
          "B2: không có since/OPENED_AT ⇒ không chứng minh được ⇒ 11")
    # G3-hygiene: bằng chứng = event EXECUTOR sau lúc mở, KHÔNG phải mtime
    j.write_text(HDR + jrow("2026-10-20T09:05:30", "PLACE") + jrow("2026-10-20T09:25:00", "BOOK_TRANSFER"))
    os.utime(j, (ts("2026-10-20T09:25:00+07:00"),) * 2)
    rc, out = run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})
    check(rc == 11 and "CHƯA chạy lại" in out and "không có event executor" in out,
          "G3: chỉ BOOK_TRANSFER sau lúc mở (mtime mới) ⇒ 11")
    j.write_text(HDR + jrow("2026-10-20T09:25:00", "NOISE_EVENT"))
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11, "G3: event lạ ngoài allowlist ⇒ 11 (fail-closed)")
    j.write_text(HDR + jrow("2026-10-20T09:05:30", "PLACE") + jrow("2026-10-20T09:25:00", "BOOK_TRANSFER"))
    os.utime(j, (ts("2026-10-20T09:25:00+07:00"),) * 2)
    j.write_bytes(b"\xff\xfe\x00bad")
    rc, out = run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})
    check(rc == 11 and "không đọc được" in out, "G3: journal hỏng ⇒ 11 + lý do thật")
    j.write_text(HDR + jrow("2026-10-20T09:05:30", "FILL") + jrow("2026-10-20T09:25:00", "BOOK_TRANSFER"))
    os.utime(j, (ts("2026-10-20T09:25:00+07:00"),) * 2)
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 11, "G3: FILL TRƯỚC lúc mở + BOOK_TRANSFER sau ⇒ 11")
    j.write_text(HDR + jrow("2026-10-20T09:05:30", "PLACE") + jrow("2026-10-20T09:25:00", "PLACE"))
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 0, "probe approval: duyệt + PLACE SAU lúc mở ⇒ 0")
    j.write_text(HDR + jrow("2026-10-20T09:25:00", "BOOK_TRANSFER") + jrow("2026-10-20T09:26:00", "FILL"))
    check(run(target, R9, *pa, extra_env={"FAKE_PLAN": "ok"})[0] == 0, "G3: BOOK_TRANSFER lẫn FILL sau lúc mở ⇒ 0")
    check(run(target, R9, *pa[:-2], extra_env={"FAKE_PLAN": "ok", "GATE_BLOCK_OPENED_AT": since})[0] == 0,
          "probe approval: since lấy từ env GATE_BLOCK_OPENED_AT (sweep đặt)")

    # 22: B2 — probe plan-t1 (tái hiện /tmp/arch_mut/b2.py: marker 21:00 bản cũ KHÔNG được đóng)
    R17 = mkroot()
    md, pd = R17 / "plan_report_sent", R17 / "trade_plans"
    md.mkdir(); pd.mkdir()
    plan = pd / "plan_SpaceX_2026-10-21.json"
    plan.write_text(json.dumps({"orders": [{"t": "FPT"}], "approved_by": "x"}))
    sys.path.insert(0, str(target.parent))
    import importlib.util
    spec = importlib.util.spec_from_file_location("gbq_under_test", target)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    good = mod.plan_content_hash(plan)
    plan2 = json.dumps({"orders": [{"t": "FPT"}], "approved_by": "khac", "mafee_x": 1})
    check(mod.plan_content_hash(plan) == good and good == __import__("hashlib").md5(
        json.dumps({"orders": [{"t": "FPT"}]}, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        and plan2, "plan_content_hash khớp công thức send_plan_report (bỏ approv*/mafee*)")
    marker = md / "SpaceX_2026-10-21.json"
    marker.write_text(json.dumps({"sent_at": "2026-10-20 21:00 ICT", "content_md5": "OLD"}))
    os.utime(marker, (ts("2026-10-20T21:00:05+07:00"),) * 2)
    probe = f"python3 {target} probe plan-t1 --account SpaceX --date 2026-10-21 --marker-dir {md} --plan-dir {pd}"
    a = ["open", "--gate", "plan-t1-not-ready", "--key", "2026-10-21-SpaceX", "--topic", "plan-t1-not-ready-2026-10-21-SpaceX",
         "--owner", "Mike", "--deadline", "2026-10-21T08:30", "--recover", "x", "--probe", probe,
         "--reason", "Plan T+1 chưa sẵn sàng (plan_unparseable)", "--thread", "plan_approval",
         "--remind-every-min", "60", "--expires-at", "2026-10-21T23:59", "--extra", "{}"]
    run(target, R17, *a, now="2026-10-20T23:00:30+07:00")
    rid = "plan-t1-not-ready__2026-10-21-SpaceX"
    rc, out = run(target, R17, "sweep", now="2026-10-20T23:15:00+07:00")
    check(st(R17, rid)["status"] == "open" and "marker CŨ" in out,
          "B2: marker có TRƯỚC lúc mở ⇒ KHÔNG đóng (tái hiện b2.py)")
    marker.write_text(json.dumps({"sent_at": "2026-10-20 23:20 ICT", "content_md5": "OLD"}))
    os.utime(marker, (ts("2026-10-20T23:20:05+07:00"),) * 2)
    rc, out = run(target, R17, "sweep", now="2026-10-21T00:20:00+07:00")
    check(st(R17, rid)["status"] == "open" and "≠ plan hiện tại" in out, "B2: marker mới nhưng md5 ≠ plan hiện tại ⇒ KHÔNG đóng")
    marker.write_text(json.dumps({"sent_at": "2026-10-20 23:00 ICT", "content_md5": good}))
    os.utime(marker, (ts("2026-10-20T23:00:20+07:00"),) * 2)
    rc, out = run(target, R17, "sweep", now="2026-10-21T01:30:00+07:00")
    check(st(R17, rid)["status"] == "open", "B2: md5 khớp nhưng mtime (23:00:20) ≤ lúc mở 23:00:30 ⇒ KHÔNG đóng")
    os.utime(marker, (ts("2026-10-20T23:00:50+07:00"),) * 2)
    rc, out = run(target, R17, "sweep", now="2026-10-21T02:40:00+07:00")
    check(st(R17, rid)["status"] == "closed" and "probe plan-t1: OK" in calls(R17),
          "B2: marker ghi SAU lúc mở (cùng phút) + md5 khớp plan ⇒ CLOSED")
    check(run(target, R17, "probe", "plan-t1", "--account", "SpaceX", "--date", "2026-10-21",
              "--marker-dir", str(md), "--plan-dir", str(pd))[0] == 11, "probe plan-t1: không có since ⇒ 11")
    plan.unlink()
    check(run(target, R17, "probe", "plan-t1", "--account", "SpaceX", "--date", "2026-10-21", "--since",
              "2026-10-20T23:00:30+07:00", "--marker-dir", str(md), "--plan-dir", str(pd))[0] == 11,
          "probe plan-t1: plan hiện tại biến mất ⇒ 11")
    # P3: md5 marker rỗng + plan biến mất (cur "") KHÔNG được coi là khớp
    marker.write_text(json.dumps({"sent_at": "2026-10-20 23:20 ICT", "content_md5": ""}))
    os.utime(marker, (ts("2026-10-20T23:21:00+07:00"),) * 2)
    check(run(target, R17, "probe", "plan-t1", "--account", "SpaceX", "--date", "2026-10-21", "--since",
              "2026-10-20T23:00:30+07:00", "--marker-dir", str(md), "--plan-dir", str(pd))[0] == 11,
          "P3: marker content_md5 rỗng + plan không có ⇒ 11 (rỗng ≠ khớp)")
    # P4: khoá requires_user_approval cũng bị loại khỏi hash (khớp send_plan_report)
    plan.write_text(json.dumps({"orders": [{"t": "FPT"}], "requires_user_approval": True, "approved_by": "u"}))
    check(mod.plan_content_hash(plan) == good, "P4: hash bỏ cả requires_user_approval")
    round3_core(target)


def _at(root: Path, args, now):
    return run(HELPER_UNDER_TEST[0], root, *args, now=now)


HELPER_UNDER_TEST: list[Path] = []


def round3_core(target: Path) -> None:
    """Vòng 3 arch-review: ack CHECK5 thật, sổ read-only, posting hết hạn, tmp mồ côi, argv bẩn,
    expired không bị sweep lại (E6)."""
    HELPER_UNDER_TEST[:] = [target]
    # --- B3: khối CHECK5 THẬT của ops_health_check.sh ở +3/+20/+27/+40/+47h (+49h = quá 48h) ---
    ohc = HERE / "ops_health_check.sh"
    if ohc.exists():
        m = re.search(r"^# CHECK5_BEGIN.*?\n(.*?)^# CHECK5_END", ohc.read_text(), re.S | re.M)
        if not m:
            print("FATAL: CHECK5_BEGIN/END không thấy"); sys.exit(2)
        blk = m.group(1)

        def scenario(gate, key, opened_ict, expires, no_ack=False):
            W = Path(tempfile.mkdtemp(prefix="gbq_c5_")); TMP.append(W)
            R = mkroot(); shutil.move(str(R), str(W / "mike")); R = W / "mike"
            if no_ack:
                (R / "APPEND_FAIL_STATUS").write_text("x")
            run(target, R, *open_args(key=key, gate=gate, expires=expires, probe="false"), now=opened_ict)
            opened_utc = _dt.datetime.fromisoformat(opened_ict).astimezone(_dt.timezone.utc)
            inbox = R / "bus/inbox/Mike.jsonl"
            evs = [dict(e, ts=opened_utc.strftime("%Y-%m-%dT%H:%M:%SZ"), event_id=f"e{i}")
                   for i, e in enumerate(map(json.loads, inbox.read_text().splitlines()))]
            inbox.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in evs))
            topic = f"gate-block-{gate}-{key}"
            out = {}
            for h in (3, 20, 27, 40, 47, 49):
                lines: list[str] = []
                os.environ["CHECK5_NOW"] = (opened_utc + _dt.timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ")
                import glob as _glob, gzip as _gzip
                ns = {"glob": _glob, "gzip": _gzip, "json": json, "os": os, "re": re, "wc_root": str(W),
                      "W": lambda x: lines.append("W " + x), "OK": lambda x: lines.append("OK " + x),
                      "lines": lines}
                try:
                    exec(compile(blk, "CHECK5", "exec"), ns)
                finally:
                    os.environ.pop("CHECK5_NOW", None)
                out[h] = [l for l in lines if topic in l and "[WARN-ONLY]" not in l]
            return out

        o = scenario("approval", "2026-10-20-SpaceX", "2026-10-20T09:06:00+07:00", "2026-10-20T15:00")
        check(all(not o[h] for h in (3, 20, 27, 40, 47)),
              "vòng3-B3: approval — CHECK5 KHÔNG dispatch Wags ở +3/20/27/40/47h (ack phủ đủ cửa sổ 48h)")
        o = scenario("plan-t1-not-ready", "2026-10-21-SpaceX", "2026-10-20T21:00:00+07:00", "2026-10-21T23:59")
        check(all(not o[h] for h in (3, 20, 27, 40, 47)),
              "vòng3-B3: plan-t1 — CHECK5 KHÔNG dispatch Wags ở +3/20/27/40/47h")
        o = scenario("approval", "2026-10-20-SpaceX", "2026-10-20T09:06:00+07:00", "2026-10-20T15:00", no_ack=True)
        check(bool(o[27]), "vòng3-B3 đối chứng: KHÔNG có ack ⇒ CHECK5 CÓ route Wags ở +27h (test nhạy)")

    # --- NB-3: sổ read-only ⇒ KHÔNG gửi (nhắc / tin cuối) rồi mới thất bại ---
    if os.geteuid() != 0:
        R = mkroot()
        run(target, R, *open_args(probe="false", every="15"), now="2026-10-20T09:06:00+07:00")
        run(target, R, "sweep", now="2026-10-20T09:10:00+07:00")
        base = calls(R).count("CỔNG CHẶN CHƯA PHỤC HỒI")
        sd = R / "state" / "gate_blocks"
        os.chmod(sd, 0o555)
        try:
            for t in ("2026-10-20T12:00:00+07:00", "2026-10-20T12:30:00+07:00"):
                run(target, R, "sweep", now=t)
            check(calls(R).count("CỔNG CHẶN CHƯA PHỤC HỒI") == base,
                  "NB-3: sổ read-only ⇒ KHÔNG gửi nhắc (ghi sổ trước khi gửi)")
            for t in ("2026-10-20T15:00:00+07:00", "2026-10-20T15:15:00+07:00", "2026-10-20T15:30:00+07:00"):
                run(target, R, "sweep", now=t)
            check("NGỪNG NHẮC" not in calls(R), "NB-3: sổ read-only ⇒ KHÔNG gửi tin cuối (t_rofs.py)")
            check(not list(sd.glob(".tmp_*")), "NB-4: save thất bại không để tmp mồ côi")
        finally:
            os.chmod(sd, 0o755)
        run(target, R, "sweep", now="2026-10-20T15:45:00+07:00")
        check(st(R)["status"] == "expired" and [l for l in calls(R).splitlines() if l.startswith("notify.sh ") and "NGỪNG NHẮC" in l].__len__() == 1,
              "NB-3: sổ ghi lại được ⇒ expire đúng 1 tin cuối")

    # --- E6: expired KHÔNG bị sweep lại (không tin cuối thứ hai, reminders giữ nguyên) ---
    R = mkroot()
    run(target, R, *open_args(probe="false", every="15"), now="2026-10-20T09:06:00+07:00")
    run(target, R, "sweep", now="2026-10-20T15:05:00+07:00")
    r0 = st(R)
    rc16, out16 = run(target, R, "sweep", now="2026-10-20T16:00:00+07:00")
    run(target, R, "sweep", now="2026-10-20T17:00:00+07:00")
    check(rc16 == 0 and "SWEEP_ERROR" not in out16, "E6: sweep qua bản ghi expired ⇒ rc 0, không SWEEP_ERROR 'status lạ'")
    check(r0["status"] == "expired" and st(R) == r0 and [l for l in calls(R).splitlines() if l.startswith("notify.sh ") and "NGỪNG NHẮC" in l].__len__() == 1,
          "E6: expired ⇒ sweep sau KHÔNG gửi lại, sổ không đổi")

    # --- NB-4: save() lỗi ở os.replace (đích là thư mục) ⇒ không để tmp mồ côi ---
    import importlib.util
    spec = importlib.util.spec_from_file_location("gbq_save_probe", target)
    sm = importlib.util.module_from_spec(spec); spec.loader.exec_module(sm)
    D = Path(tempfile.mkdtemp(prefix="gbq_save_")); TMP.append(D)
    (D / "x.json").mkdir()
    try:
        sm.save(D / "x.json", {"a": 1})
        raised = False
    except OSError:
        raised = True
    check(raised and not list(D.glob(".tmp_*")), "NB-4: os.replace lỗi ⇒ save() dọn tmp rồi mới raise")

    # --- NB-4: sổ 'posting' (post bus hỏng) có hạn; tmp mồ côi bị dọn ---
    R = mkroot()
    (R / "APPEND_FAIL").write_text("x")
    rc, out = run(target, R, *open_args(probe="false"), now="2026-10-20T09:06:00+07:00")
    check(rc == 1 and st(R)["status"] == "posting", "NB-4: post hỏng ⇒ sổ posting, rc 1")
    run(target, R, "sweep", now="2026-10-20T12:00:00+07:00")
    check(st(R)["status"] == "posting", "NB-4: posting chưa tới hạn ⇒ vẫn thử lại")
    rc, out = run(target, R, "sweep", now="2026-10-20T15:05:00+07:00")
    check(st(R)["status"] == "expired" and "EXPIRED_UNPOSTED" in out and not questions(R),
          "NB-4: posting quá hạn ⇒ expired (EXPIRED_UNPOSTED), không còn kẹt vĩnh viễn")
    sd = R / "state" / "gate_blocks"
    old, fresh = sd / ".tmp_orphan", sd / ".tmp_fresh"
    old.write_text("x"); fresh.write_text("x")
    os.utime(old, (_dt.datetime.now().timestamp() - 7200,) * 2)
    run(target, R, "sweep", "--dry-run", now="2026-10-20T15:10:00+07:00")
    check(old.exists(), "NB-4: dry-run KHÔNG xoá tmp")
    run(target, R, "sweep", now="2026-10-20T15:10:00+07:00")
    check(not old.exists() and fresh.exists(), "NB-4: sweep xoá tmp mồ côi >1h, giữ tmp mới")

    # --- NB-1: argv có byte không phải UTF-8 vẫn mở được câu hỏi ---
    R = mkroot()
    args = open_args(probe="false")
    args[args.index("--reason") + 1] = "lệch nguồn \udcc3 cắt dở"
    env = dict(os.environ, GATE_BLOCK_ROOT=str(R), GATE_BLOCK_WC_ROOT=str(R), GATE_BLOCK_NOW="2026-10-20T09:06:00+07:00")
    r = subprocess.run([sys.executable, str(target), *[os.fsencode(x) for x in args]], env=env,
                       capture_output=True, timeout=60)
    qs = questions(R)
    check(r.returncode == 0 and b"OPENED" in r.stdout and len(qs) == 1 and "\ufffd" in qs[0]["payload"]["question"],
          "NB-1: argv byte lạ ⇒ thay U+FFFD, vẫn OPENED (không crash)")

    followups_core(target)


def followups_core(target: Path) -> None:
    """Followups vòng 3: NB-B (không prune khi còn lượt open), NB-D (đóng ngoài sweep), A2 (ack theo --topic)."""
    dargs = ["open", "--gate", "delivery", "--key", "rpt.md", "--owner", "Taylor", "--deadline", "2026-10-21T08:30",
             "--recover", "x", "--probe", "false", "--reason", "stuck", "--thread", "trading_report",
             "--remind-every-min", "240", "--expires-in-days", "3", "--max-reminders", "20"]
    R = mkroot()
    run(target, R, *dargs, now="2026-10-20T08:30:00+07:00")
    run(target, R, "sweep", now="2026-10-23T09:00:00+07:00")          # expired
    rid = "delivery__rpt.md"
    check(st(R, rid)["status"] == "expired", "NB-B: tiền đề — bản ghi delivery đã expired")
    run(target, R, *dargs, now="2026-10-30T08:30:00+07:00")           # d10: còn người gọi open
    check(st(R, rid).get("last_open_call_at", "").startswith("2026-10-30"), "NB-B: open lên bản ghi expired ghi last_open_call_at")
    run(target, R, "sweep", now="2026-11-23T09:00:00+07:00")          # d34 từ expire, d24 từ lượt open cuối
    check((R / "state/gate_blocks" / f"{rid}.json").exists(), "NB-B: còn lượt open gần đây ⇒ sweep KHÔNG prune")
    rc, out = run(target, R, *dargs, now="2026-11-23T09:30:00+07:00")
    check("ALREADY_EXPIRED" in out and len(questions(R)) == 1, "NB-B: open sau đó vẫn ALREADY_EXPIRED, không mở câu trùng")
    run(target, R, "sweep", now="2026-12-30T09:00:00+07:00")          # >30d kể từ lượt open cuối
    check(not (R / "state/gate_blocks" / f"{rid}.json").exists(), "NB-B: hết lượt open >30 ngày ⇒ vẫn prune (không giữ vĩnh viễn)")

    # NB-D: audit stub báo không còn pending (người đóng ngoài sweep) ⇒ open kế tiếp in ALREADY_CLOSED
    R = mkroot()
    run(target, R, *open_args(probe="false"), now="2026-10-20T09:06:00+07:00")
    rc, out = run(target, R, *open_args(probe="false"), now="2026-10-20T09:10:00+07:00")
    check("ALREADY_OPEN" in out and st(R)["status"] == "open", "NB-D đối chứng: còn pending ⇒ ALREADY_OPEN, sổ vẫn open")
    with open(R / "bus/inbox/Mike.jsonl", "a") as f:   # người đóng tay: event resolves ngoài sweep
        f.write(json.dumps({"event_id": "x", "ts": "2026-10-20T02:15:00Z", "agent_id": "Mike", "event_type": "answer",
                            "topic": "manual", "payload": {"resolves": ["Mike/gate-block-approval-2026-10-20-SpaceX"]}}) + "\n")
    rc, out = run(target, R, *open_args(probe="false"), now="2026-10-20T09:20:00+07:00")
    check("ALREADY_CLOSED" in out and st(R)["status"] == "closed", "NB-D: bus đã đóng ngoài sweep ⇒ ALREADY_CLOSED (caller mở câu mới), sổ closed")
    check(st(R).get("closed_at", "").startswith("2026-10-20T09:20"), "NB-D: ghi closed_at (để sweep dọn sổ theo hạn)")

    # NB-D / M1: audit KHÔNG đọc được (None) ⇒ coi như còn mở, KHÔNG đóng nhầm câu đang sống
    R = mkroot()
    run(target, R, *open_args(probe="false"), now="2026-10-20T09:06:00+07:00")
    (R / "AUDIT_BROKEN").write_text("1")
    rc, out = run(target, R, *open_args(probe="false"), now="2026-10-20T09:10:00+07:00")
    check("ALREADY_OPEN" in out and st(R)["status"] == "open" and not st(R).get("closed_at"),
          "NB-D: audit trả None (hỏng) ⇒ ALREADY_OPEN, sổ vẫn open, không đóng nhầm")

    # NB-B / M4: bản ghi CLOSED (qua sweep+probe) cũng ghi last_open_call_at khi còn người gọi open
    R = mkroot()
    run(target, R, *open_args(probe="true"), now="2026-10-20T09:06:00+07:00")
    run(target, R, "sweep", now="2026-10-20T09:30:00+07:00")
    check(st(R)["status"] == "closed", "NB-B(closed): tiền đề — probe rc=0 ⇒ sổ closed")
    rc, out = run(target, R, *open_args(probe="true"), now="2026-10-25T09:00:00+07:00")
    check("ALREADY_CLOSED" in out and st(R).get("last_open_call_at", "").startswith("2026-10-25"),
          "NB-B(closed): open lên bản ghi closed ghi last_open_call_at")

    # A2: --topic tuỳ biến ⇒ ack nhắm ĐÚNG topic đó (CHECK5 so ack với topic câu hỏi)
    R = mkroot()
    run(target, R, *open_args(probe="false"), "--topic", "custom-topic-xyz", now="2026-10-20T09:06:00+07:00")
    acks = events(R, "Mike", "status")
    check(len(acks) == 1 and acks[0]["topic"].endswith(" custom-topic-xyz") and "gate-block-approval" not in acks[0]["topic"],
          "A2: ack dùng rec['topic'] (--topic tuỳ biến), không phải topic mặc định gate-key")


def extract(path: Path, begin: str, end: str) -> str:
    s = path.read_text()
    m = re.search(rf"^[^\n]*{begin}[^\n]*\n(.*?)^[^\n]*{end}", s, re.S | re.M)
    if not m:
        print(f"FATAL: marker {begin}/{end} không thấy trong {path.name}")
        sys.exit(2)
    return m.group(1)


STUB_HELPER = r'''#!/usr/bin/env python3
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "helper_calls.log"), "a") as f:
    f.write("\x1e".join(sys.argv[1:]) + "\n")
if sys.argv[1] == "probe":
    rc = int(os.environ.get("STUB_PROBE_RC", "10"))
    print({10: "probe approval: VẪN CHẶN — requires_user_approval chua duyet", 12: "probe approval: KHÔNG CÓ PLAN"}.get(rc, "probe x"))
    sys.exit(rc)
mode = os.environ.get("STUB_OPEN", "ok")
if mode == "ok":
    print("gate_block_question: OPENED x"); sys.exit(0)
if mode in ("closed", "expired"):
    print("gate_block_question: ALREADY_" + mode.upper() + " x"); sys.exit(0)
if mode == "alreadyopen":
    print("gate_block_question: ALREADY_OPEN x"); sys.exit(0)
if mode == "posting":
    print("gate_block_question: ALREADY_POSTING x"); sys.exit(0)
if mode == "crash":
    print("Traceback boom", file=sys.stderr); sys.exit(2)
'''


def arg_of(call: str, flag: str) -> str:
    parts = call.split("\x1e")
    return parts[parts.index(flag) + 1] if flag in parts else ""


def wiring(bin_dir: Path) -> None:
    round3_wiring(bin_dir)
    followups_wiring(bin_dir)
    cadence_reason(bin_dir)
    W = Path(tempfile.mkdtemp(prefix="gbq_wire_"))
    TMP.append(W)
    (W / "mike/bin").mkdir(parents=True)
    h = W / "mike/bin/gate_block_question.py"; h.write_text(STUB_HELPER); h.chmod(0o755)
    ap = W / "mike/bin/append_event.sh"
    ap.write_text('#!/usr/bin/env bash\necho "append $*" >> "$(dirname "$0")/../fallback.log"\n'); ap.chmod(0o755)
    log = W / "mike/helper_calls.log"
    botlog = W / "bot.log"

    blk = extract(bin_dir / "run_bot.sh", "GATE_BLOCK_APPROVAL_BEGIN", "GATE_BLOCK_APPROVAL_END")
    script = ("set -euo pipefail\nROOT=%s\nWC_ROOT=%s\nACCOUNT=SpaceX\nPLAN_DATE=2026-10-20\n"
              "LOG=%s\n_tid=trading_daily\nrc=$RC\n%s\necho FINAL_RC=$rc\n") % (W / "mike", W, botlog, blk)

    def rb(rc, probe_rc, open_mode="ok"):
        for f in (log, botlog):
            if f.exists():
                f.unlink()
        r = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                           env=dict(os.environ, RC=str(rc), STUB_PROBE_RC=str(probe_rc), STUB_OPEN=open_mode))
        return r, (log.read_text() if log.exists() else ""), (botlog.read_text() if botlog.exists() else "")

    r, c, bl = rb(2, 10)
    op = [x for x in c.split("\n") if x.startswith("open")]
    o = op[0] if op else ""
    check("FINAL_RC=2" in r.stdout and arg_of(o, "--key") == "2026-10-20-SpaceX"
          and arg_of(o, "--deadline") == "2026-10-20T10:00" and arg_of(o, "--expires-at") == "2026-10-20T15:00",
          "run_bot: rc=2 + probe 10 ⇒ open (hạn 10:00, EXPIRED 15:00), rc giữ 2")
    rec_txt = arg_of(o, "--recover")
    check(arg_of(o, "--recover-kind") == "instructions" and "&&" not in rec_txt and "run_bot.sh" not in rec_txt
          and rec_txt.startswith("USER:") and arg_of(o, "--next-step").startswith("11=Mike:")
          and "run_bot.sh --account SpaceX --auto-otp" in arg_of(o, "--next-step"),
          "B3: recover = CHỈ DẪN user (không lệnh nối, không run_bot); bước Mike chỉ ở next-step rc=11")
    check("VẪN CHẶN — requires_user_approval chua duyet" in arg_of(o, "--reason")
          and "probe approval rc=10: probe approval: VẪN CHẶN" in bl and "OPENED" in bl,
          "N4: reason nội suy từ output probe; output probe + helper ghi vào LOG")
    check(arg_of(o, "--max-reminders") == "24", "W3: run_bot truyền --max-reminders 24")
    r, c, bl = rb(2, 11)
    check("FINAL_RC=2" in r.stdout and "open" not in c, "W2: run_bot probe rc=11 (đã duyệt, chưa chạy lại) ⇒ KHÔNG open")
    r, c, bl = rb(2, 12)
    check("FINAL_RC=2" in r.stdout and "open" not in c and "probe rc=12" in bl,
          "N4: rc=2 + probe 12 (không có plan) ⇒ không open, ghi log tách biệt")
    r, c, bl = rb(2, 0)
    check("FINAL_RC=2" in r.stdout and "open" not in c, "run_bot: rc=2 nhưng probe≠10 (không phải approval) ⇒ không open")
    r, c, bl = rb(0, 10)
    check("FINAL_RC=0" in r.stdout and c == "", "run_bot: rc=0 ⇒ không probe/open")
    r, c, bl = rb(2, 10, "crash")
    check(r.returncode == 0 and "FINAL_RC=2" in r.stdout, "run_bot: helper crash dưới set -euo pipefail ⇒ không abort, rc giữ 2")

    blk = extract(bin_dir / "send_plan_report.sh", "GATE_BLOCK_PLAN_T1_BEGIN", "GATE_BLOCK_PLAN_T1_END")
    script2 = ("set -uo pipefail\nROOT=%s\nACCOUNT=ZaloPay\nEXPECTED_DATE=2026-10-21\nTODAY=2026-10-20\n"
               "REASON=missing\nMARKER_DIR=/m\nWORKDIR=/w\nDISCORD_PLAN_CHANNEL=plan_approval\n_QPAYLOAD='{}'\n%s\n") % (W / "mike", blk)
    fb = W / "mike/fallback.log"
    for mode, want_fb in (("ok", False), ("alreadyopen", False), ("posting", False),
                          ("closed", True), ("expired", True), ("crash", True), ("silent", True)):
        for f in (fb, log):
            if f.exists():
                f.unlink()
        subprocess.run(["bash", "-c", script2], capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, STUB_OPEN=mode))
        c = log.read_text() if log.exists() else ""
        check(fb.exists() == want_fb and arg_of(c, "--topic") == "plan-t1-not-ready-2026-10-21-ZaloPay"
              and arg_of(c, "--key") == "2026-10-21-ZaloPay" and arg_of(c, "--expires-at") == "2026-10-21T23:59"
              and arg_of(c, "--probe").endswith("gate_block_question.py probe plan-t1 --account ZaloPay "
                                                 "--date 2026-10-21 --marker-dir /m --plan-dir /w/data/trade_plans"),
              f"send_plan_report: helper={mode} ⇒ fallback append={want_fb}, topic THEO NGÀY, probe plan-t1, EXPIRED hết T+1")
        if want_fb:
            check("plan-t1-not-ready-2026-10-21-ZaloPay" in fb.read_text() and "plan-t1-not-ready-ZaloPay" not in fb.read_text().replace("plan-t1-not-ready-2026-10-21-ZaloPay", ""),
                  f"vòng3-B1/B4: fallback ({mode}) post cùng topic theo ngày, không dùng topic không ngày")

    blk = extract(bin_dir / "check_report_cadence.sh", "GATE_BLOCK_DELIVERY_BEGIN", "GATE_BLOCK_DELIVERY_END")
    for tag, owner in (("VENDOR_MISMATCH_ALERT|x", "Winston"), ("❌ CHẶN — số sai", "Taylor")):
        if log.exists():
            log.unlink()
        script3 = ("set -uo pipefail\nROOT=%s\nFNAME=SpaceX_weekly_report_2026-10-16.md\n"
                   "f=/r/SpaceX_weekly_report_2026-10-16.md\nTRADING_REPORT_THREAD=trading_report\n"
                   "GATE_RC=1\nGATE_OUT=%s\n%s\n") % (W / "mike", json.dumps(tag), blk)
        subprocess.run(["bash", "-c", script3], capture_output=True, text=True, timeout=60)
        c = log.read_text() if log.exists() else ""
        check(arg_of(c, "--owner").startswith(owner) and arg_of(c, "--key") == "SpaceX_weekly_report_2026-10-16.md"
              and arg_of(c, "--expires-in-days") == "3"
              and "report_delivery_gate.py /r/SpaceX_weekly_report_2026-10-16.md --status" in arg_of(c, "--probe"),
              f"cadence: tag {tag.split('|')[0][:20]!r} ⇒ owner {owner}, probe --status, EXPIRED 3 ngày")
        check(arg_of(c, "--max-reminders") == "20", "W4: cadence truyền --max-reminders 20")


STUB_APPEND_TS = r'''#!/usr/bin/env python3
import datetime, json, os, sys, uuid
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
a, et, t, p = sys.argv[1:5]
os.makedirs(os.path.join(root, "bus", "inbox"), exist_ok=True)
with open(os.path.join(root, "bus", "inbox", a + ".jsonl"), "a") as f:
    f.write(json.dumps({"event_id": str(uuid.uuid4()),
                        "ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                        "agent_id": a, "event_type": et, "topic": t, "payload": json.loads(p)},
                       ensure_ascii=False) + "\n")
'''


def round3_wiring(bin_dir: Path) -> None:
    """B1: topic plan-t1 dùng lại không đụng câu legacy — chạy audit + close_bus_question THẬT, 2 chiều."""
    blk = extract(bin_dir / "send_plan_report.sh", "GATE_BLOCK_PLAN_T1_BEGIN", "GATE_BLOCK_PLAN_T1_END")

    def fixture():
        R = mkroot()
        for name in ("bus_question_audit.py", "close_bus_question.py", "gate_block_question.py"):
            shutil.copy(bin_dir / name, R / "bin" / name)
        (R / "bin" / "append_event.sh").write_text(STUB_APPEND_TS)
        for name in ("bus_question_audit.py", "close_bus_question.py", "gate_block_question.py"):
            (R / "bin" / name).chmod(0o755)
        legacy = {"event_id": "old", "ts": "2026-10-16T14:00:09Z", "agent_id": "Mike", "event_type": "question",
                  "topic": "plan-t1-not-ready-SpaceX", "payload": {"reason": "plan_missing"}}
        (R / "bus/inbox").mkdir(parents=True)
        (R / "bus/inbox/Mike.jsonl").write_text(json.dumps(legacy) + "\n")
        script = ("set -uo pipefail\nROOT=%s\nACCOUNT=SpaceX\nEXPECTED_DATE=2026-10-21\nTODAY=2026-10-20\n"
                  "REASON=plan_unparseable\nMARKER_DIR=%s/m\nWORKDIR=%s/w\nDISCORD_PLAN_CHANNEL=plan_approval\n"
                  "_QPAYLOAD='{\"legacy\":1}'\n%s\n") % (R, R, R, blk)
        env = dict(os.environ, GATE_BLOCK_WC_ROOT=str(R), GATE_BLOCK_NOW="2026-10-20T21:00:00+07:00")
        subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=90, env=env)
        return R

    def pending(R):
        o = subprocess.run([sys.executable, str(R / "bin/bus_question_audit.py"), "--json"],
                           env=dict(os.environ, BUS_AUDIT_ROOT=str(R)), capture_output=True, text=True)
        return [q["topic"] for q in json.loads(o.stdout)["pending"]]

    def close(R, topic):
        return subprocess.run([sys.executable, str(R / "bin/close_bus_question.py"), f"Mike/{topic}",
                               "--resolution", "x", "--evidence", "y", "--source-topic", "manual",
                               "--actor", "Mike"], capture_output=True, text=True)

    new_t, old_t = "plan-t1-not-ready-2026-10-21-SpaceX", "plan-t1-not-ready-SpaceX"
    R = fixture()
    check(sorted(pending(R)) == sorted([new_t, old_t]), "vòng3-B1: bus có CẢ câu legacy lẫn câu theo ngày đang pending")
    c = close(R, old_t)
    check(new_t in pending(R) and old_t not in pending(R),
          f"vòng3-B1 chiều 1: đóng câu legacy KHÔNG đóng lây câu helper (close rc={c.returncode})")
    R = fixture()
    c = close(R, new_t)
    check(old_t in pending(R) and new_t not in pending(R),
          f"vòng3-B1 chiều 2: đóng câu theo ngày KHÔNG đóng lây câu legacy (close rc={c.returncode})")


def followups_wiring(bin_dir: Path) -> None:
    """NB-A (r2), NB-C/E1/E2 (ERROR_PATTERNS), R2 (timeout probe), D1 (TZ), D2 (remind) — hành vi thật, không so chuỗi nguồn."""
    # NB-A: ALREADY_CLOSED/EXPIRED ⇒ gọi helper LẦN HAI với key -r2 + topic tiền tố r2 (không chứa topic cũ)
    blk = extract(bin_dir / "send_plan_report.sh", "GATE_BLOCK_PLAN_T1_BEGIN", "GATE_BLOCK_PLAN_T1_END")
    W = Path(tempfile.mkdtemp(prefix="gbq_fu_")); TMP.append(W)
    (W / "mike/bin").mkdir(parents=True)
    h = W / "mike/bin/gate_block_question.py"; h.write_text(STUB_HELPER_R2); h.chmod(0o755)
    ap = W / "mike/bin/append_event.sh"
    ap.write_text('#!/usr/bin/env bash\necho "append $*" >> "$(dirname "$0")/../fallback.log"\n'); ap.chmod(0o755)
    log, fb = W / "mike/helper_calls.log", W / "mike/fallback.log"
    script = ("set -uo pipefail\nROOT=%s\nACCOUNT=ZaloPay\nEXPECTED_DATE=2026-10-21\nTODAY=2026-10-20\n"
              "REASON=missing\nMARKER_DIR=/m\nWORKDIR=/w\nDISCORD_PLAN_CHANNEL=plan_approval\n_QPAYLOAD='{}'\n%s\n") % (W / "mike", blk)
    for first, second, want_calls, want_fb in (("closed", "ok", 2, False), ("expired", "ok", 2, False),
                                               ("closed", "closed", 2, True), ("ok", "ok", 1, False),
                                               ("open", "ok", 1, False), ("prefixed", "ok", 1, True)):
        for f in (log, fb):
            if f.exists():
                f.unlink()
        subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                       env=dict(os.environ, STUB_FIRST=first, STUB_SECOND=second))
        calls_ = [x for x in (log.read_text().split("\n") if log.exists() else []) if x.startswith("open")]
        check(len(calls_) == want_calls and fb.exists() == want_fb,
              f"NB-A: helper {first}→{second} ⇒ {want_calls} lượt open, fallback trần={want_fb}")
        if want_calls == 2:
            a, b = calls_
            check(arg_of(a, "--topic") == "plan-t1-not-ready-2026-10-21-ZaloPay"
                  and arg_of(b, "--key") == "2026-10-21-ZaloPay-r2"
                  and arg_of(b, "--topic") == "plan-t1-not-ready-r2-2026-10-21-ZaloPay"
                  and arg_of(a, "--topic") not in arg_of(b, "--topic"),
                  "NB-A: lượt 2 key '-r2', topic tiền tố r2 KHÔNG chứa topic cũ (ack cũ không tắt lây)")

    # NB-C / E1 / E2: ERROR_PATTERNS thật bắt từng dấu hiệu sweep
    import importlib.util
    spec = importlib.util.spec_from_file_location("chc_probe", bin_dir / "cron_health_check.py")
    chc = importlib.util.module_from_spec(spec); spec.loader.exec_module(chc)
    for sample in ("gate_block_question: SWEEP_ERROR x.json: ValueError: y", "cron: failed to run command",
                   "gate_block_question: EXPIRED_UNPOSTED delivery__x — chưa từng post", "gate_block_question: POST_FAILED question x rc=1",
                   "gate_block_question: AUDIT_UNREADABLE (ValueError: x) — coi như còn mở",
                   "gate_block_question: REMIND_UNDELIVERED x — không kênh nào nhận"):
        check(bool(chc.ERROR_RE.search(sample)), f"NB-C/E1/E2: ERROR_RE bắt {sample.split(':')[1].split()[0] if 'gate_block' in sample else sample[:25]!r}")
    check(not chc.ERROR_RE.search("gate_block_question: STILL_OPEN x (nhắc gần đây)"), "NB-C: dòng bình thường STILL_OPEN không bị bắt")
    for neg in ("gate_block_question: PRUNED delivery__x", "gate_block_question: CLOSED_EXTERNALLY x", "gate_block_question: ALREADY_OPEN x",
                "gate_block_question: OPENED Mike/t owner=o", "report_gate summary: 0 FAILED, 12 passed"):
        check(not chc.ERROR_RE.search(neg), f"C1: log mẫu âm không bị bắt (regex không bị nới): {neg[:48]!r}")

    # R2: probe run_bot chạy dưới `timeout 60` (shim timeout ghi argv)
    sh = W / "shim"; sh.mkdir()
    (sh / "timeout").write_text('#!/usr/bin/env bash\necho "$*" >> "%s/timeout.log"; shift; exec "$@"\n' % W); (sh / "timeout").chmod(0o755)
    (W / "mike/bin/gate_block_question.py").write_text(STUB_HELPER); botlog = W / "bot2.log"
    blk2 = extract(bin_dir / "run_bot.sh", "GATE_BLOCK_APPROVAL_BEGIN", "GATE_BLOCK_APPROVAL_END")
    script2 = ("set -euo pipefail\nROOT=%s\nWC_ROOT=%s\nACCOUNT=SpaceX\nPLAN_DATE=2026-10-20\nLOG=%s\n_tid=trading_daily\nrc=2\n%s\n") % (
        W / "mike", W, botlog, blk2)
    tl = W / "timeout.log"
    if tl.exists():
        tl.unlink()
    subprocess.run(["bash", "-c", script2], capture_output=True, text=True, timeout=60,
                   env=dict(os.environ, PATH=f"{sh}:{os.environ['PATH']}", STUB_PROBE_RC="10"))
    probe_lines = [l for l in (tl.read_text().splitlines() if tl.exists() else []) if "probe approval" in l and " open " not in l]
    check(len(probe_lines) == 1 and probe_lines[0].startswith("60 "), "R2: lệnh probe approval của run_bot chạy dưới `timeout 60`")

    # W2: lượt `open` của plan-t1 cũng chạy dưới `timeout 60` (helper treo không được kẹt send_plan_report)
    if tl.exists():
        tl.unlink()
    subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60,
                   env=dict(os.environ, PATH=f"{sh}:{os.environ['PATH']}", STUB_OPEN="ok"))
    open_lines = [l for l in (tl.read_text().splitlines() if tl.exists() else []) if "gate_block_question.py open" in l]
    check(len(open_lines) == 1 and open_lines[0].startswith("60 "), "W2: lệnh `open` plan-t1 chạy dưới `timeout 60`")

    # D1 / D2: cadence — deadline neo ICT (shim date phân biệt TZ) + nhắc 240'
    (sh / "date").write_text('#!/usr/bin/env bash\nif [ "${TZ:-}" = "Asia/Ho_Chi_Minh" ]; then echo 2031-03-04; else echo 1999-01-01; fi\n'); (sh / "date").chmod(0o755)
    blk3 = extract(bin_dir / "check_report_cadence.sh", "GATE_BLOCK_DELIVERY_BEGIN", "GATE_BLOCK_DELIVERY_END")
    if log.exists():
        log.unlink()
    script3 = ("set -uo pipefail\nROOT=%s\nFNAME=SpaceX_weekly_report_2026-10-16.md\nf=/r/x.md\nTRADING_REPORT_THREAD=trading_report\n"
               "GATE_RC=1\nGATE_OUT=x\n%s\n") % (W / "mike", blk3)
    subprocess.run(["bash", "-c", script3], capture_output=True, text=True, timeout=60,
                   env=dict(os.environ, PATH=f"{sh}:{os.environ['PATH']}", TZ="Pacific/Kiritimati", STUB_OPEN="ok"))
    c = log.read_text() if log.exists() else ""
    check(arg_of(c, "--deadline") == "2031-03-04T08:30", "D1: deadline delivery neo TZ=Asia/Ho_Chi_Minh, không theo TZ host")
    check(arg_of(c, "--remind-every-min") == "240", "D2: delivery nhắc mỗi 240 phút")


STUB_HELPER_R2 = r'''#!/usr/bin/env python3
import os, sys
root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
with open(os.path.join(root, "helper_calls.log"), "a") as f:
    f.write("\x1e".join(sys.argv[1:]) + "\n")
n = sum(1 for _ in open(os.path.join(root, "helper_calls.log")))
mode = os.environ.get("STUB_FIRST" if n == 1 else "STUB_SECOND", "ok")
if mode == "prefixed":   # dòng ALREADY_CLOSED KHÔNG ở đầu dòng (vd lẫn trong cảnh báo) — không được kích hoạt r2
    print("warn: gate_block_question: ALREADY_CLOSED x")
else:
    print("gate_block_question: " + ("OPENED" if mode == "ok" else "ALREADY_" + mode.upper()) + " x")
'''


def cadence_reason(bin_dir: Path) -> None:
    """NB-1/NB-2: reason của câu hỏi delivery lấy từ _RC_WHY (đã lọc), không cắt byte."""
    blk = extract(bin_dir / "check_report_cadence.sh", "GATE_BLOCK_DELIVERY_BEGIN", "GATE_BLOCK_DELIVERY_END")
    check("cut -c" not in blk, "NB-1: khối delivery không dùng `cut -c` (cắt byte làm vỡ UTF-8)")
    W = Path(tempfile.mkdtemp(prefix="gbq_cad_")); TMP.append(W)
    (W / "mike/bin").mkdir(parents=True)
    h = W / "mike/bin/gate_block_question.py"; h.write_text(STUB_HELPER); h.chmod(0o755)
    log = W / "mike/helper_calls.log"
    long_out = "❌ CHẶN — " + "ế" * 150
    for why, want in (("dòng cuối cổng in ra: lý do thật", "report_delivery_gate rc=1: dòng cuối cổng in ra: lý do thật"),
                      ("", "report_delivery_gate rc=1: không xác định")):
        if log.exists():
            log.unlink()
        script = ("set -uo pipefail\nROOT=%s\nFNAME=SpaceX_weekly_report_2026-10-16.md\nf=/r/x.md\n"
                  "TRADING_REPORT_THREAD=trading_report\nGATE_RC=1\nGATE_OUT=%s\n_RC_WHY=%s\n%s\n") % (
                      W / "mike", json.dumps(long_out, ensure_ascii=False), json.dumps(why, ensure_ascii=False), blk)
        subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60)
        reason = arg_of(log.read_text() if log.exists() else "", "--reason")
        check(reason.startswith(want) and "ế" * 20 not in reason,
              f"NB-2: reason delivery lấy từ _RC_WHY ({'có' if why else 'rỗng'}), không phải dòng cuối GATE_OUT thô")


# (tên, đoạn gốc, đoạn thay). Gồm 8 mutant vòng 1 + 18 mutant harness arch-reviewer (/tmp/arch_mut/run.py,
# viết lại theo code vòng 2) + mutant cho B1-B4/N1-N5/N8.
MUTATIONS = [
    ("O_EXCL/claim bị bỏ (mở trùng)", "if rec.get(\"status\") != \"posting\":", "if False:"),
    ("đóng khi probe FAIL", "    if rc == 0:\n        if dry:", "    if rc != 0:\n        if dry:"),
    ("now theo TZ host", "return dt.datetime.now(ICT)", "return dt.datetime.now().replace(tzinfo=ICT)"),
    ("fake-now bỏ offset", ".astimezone(ICT)\n    return dt.datetime.now(ICT)", ".replace(tzinfo=ICT)\n    return dt.datetime.now(ICT)"),
    ("bỏ check bus khi post lại", "    if bus_has_question(rec[\"agent\"], rec[\"topic\"], rec[\"id\"]):\n        return True\n", ""),
    ("bỏ throttle nhắc", "< dt.timedelta(minutes=rec[\"remind_every_min\"])", "< dt.timedelta(minutes=0)"),
    ("audit hỏng ⇒ coi như đã đóng", "        return None\n    return any(", "        return False\n    return any("),
    ("probe approval bỏ check journal", "if not journal.exists() or since is None or mtime_ict(journal) <= since:", "if False:"),
    # harness arch-reviewer
    ("dry-run remind vẫn gửi/ghi", "    if dry:\n        return\n    # Ghi sổ TRƯỚC khi gửi", "    # Ghi sổ TRƯỚC khi gửi"),
    ("dry-run expire vẫn gửi/ghi", "    if dry:\n        return\n    # Ghi status expired", "    # Ghi status expired"),
    ("dry-run vẫn post bù", "    if dry and st == \"posting\":", "    if False:"),
    ("bỏ skip closed", "    if st in DONE:\n", "    if False:\n"),
    ("bỏ cô lập lỗi per-record", "        except Exception as exc:  # một bản ghi", "        except ZeroDivisionError as exc:  # một bản ghi"),
    ("đóng khi close rc≠0 nhưng in CLOSED", "if c.returncode == 0 and CLOSED_LINE.search(c.stdout or \"\"):", "if CLOSED_LINE.search(c.stdout or \"\"):"),
    ("bỏ check output CLOSED", "if c.returncode == 0 and CLOSED_LINE.search(c.stdout or \"\"):", "if c.returncode == 0:"),
    ("N5 khớp chuỗi con CLOSED", "if c.returncode == 0 and CLOSED_LINE.search(c.stdout or \"\"):", "if c.returncode == 0 and \"CLOSED\" in text:"),
    ("throttle < thành <=", "< dt.timedelta(minutes=rec[\"remind_every_min\"])", "<= dt.timedelta(minutes=rec[\"remind_every_min\"])"),
    ("CLOSED_EXTERNALLY khi audit None", "\n    if still_pending(rec[\"agent\"], rec[\"topic\"]) is False:", "\n    if not still_pending(rec[\"agent\"], rec[\"topic\"]):"),
    ("bỏ CLOSED_EXTERNALLY", "if still_pending(rec[\"agent\"], rec[\"topic\"]) is False:", "if False:"),
    ("still_pending bỏ lọc agent", "q.get(\"agent\") == agent and q.get(\"topic\") == topic", "q.get(\"topic\") == topic"),
    ("probe timeout ⇒ rc0", "return 124, f\"probe timeout", "return 0, f\"probe timeout"),
    ("probe OSError ⇒ rc0", "return 127, f\"probe", "return 0, f\"probe"),
    ("bus_has_question bỏ so topic", " and e.get(\"topic\") == topic)", ")"),
    ("open không đổi status open sau post", "        rec[\"status\"] = \"open\"\n        rec[\"posted_at\"]", "        rec[\"posted_at\"]"),
    ("probe approval: plan None ⇒ 0", "KHÔNG CÓ PLAN {a.account} {a.date}\")\n        return 12", "KHÔNG CÓ PLAN {a.account} {a.date}\")\n        return 0"),
    ("probe cwd bỏ WC_ROOT", "cwd=WC_ROOT, ", ""),
    ("reason không cắt 400", "[:400]", ""),
    ("mins âm vẫn ghi còn", "if mins >= 0 else", "if True else"),
    # B1
    ("B1 bỏ expire theo thời gian", "    if now >= parse_ict(rec[\"expires_at\"]):", "    if False:"),
    ("B1 bỏ trần số lần nhắc", "    elif int(rec.get(\"reminders\") or 0) >= cap:", "    elif False:"),
    ("B1 expire không đổi status", "    rec.update(status=\"expired\", expired_at", "    rec.update(expired_at"),
    ("B1 expire không gửi tin cuối", "    rec[\"final_notice_delivered\"] = send(msg, rec.get(\"thread\"))", "    rec[\"final_notice_delivered\"] = False"),
    ("B1 open không bắt buộc expiry", "    if bool(a.expires_at) == (a.expires_in_days is not None):", "    if False:"),
    # B2
    ("B2 approval bỏ so mtime journal", " or mtime_ict(journal) <= since:", ":"),
    ("B2 approval since None vẫn OK", "if not journal.exists() or since is None or mtime_ict", "if not journal.exists() or (since is not None and mtime_ict"),
    ("B2 plan-t1 bỏ so mtime", "    if mt <= since or sent <", "    if sent <"),
    ("B2 plan-t1 bỏ so md5", "    if not cur or m.get(\"content_md5\") != cur:", "    if False:"),
    ("B2 sweep không truyền OPENED_AT", "env = dict(os.environ, GATE_BLOCK_OPENED_AT=opened_at)", "env = dict(os.environ)"),
    ("B2 hash không bỏ approv*", "if not (k.startswith(\"approv\") or k.startswith(\"mafee\")", "if not (k.startswith(\"mafee\")"),
    # B3
    ("B3 instructions vẫn ghi recover_cmd", "payload[\"recover_instructions\" if human else \"recover_cmd\"]", "payload[\"recover_cmd\"]"),
    ("B3 bỏ next-step khi nhắc", "    how = f\"BƯỚC KẾ: {step}\" if step else", "    how = f\"BƯỚC KẾ: {step}\" if False else"),
    # B4
    ("B4 không post ack", "    if not rec.get(\"ack_posted\") and post_ack(rec):", "    if False:"),
    ("B4 ack sai prefix", "ACK_PREFIX = \"triaged-needs-human:\"", "ACK_PREFIX = \"triaged-needs-human\""),
    ("B4 ack không suppress_days", "\"suppress_days\": sd,", ""),
    # N4/N2/N8
    ("N4 notify lỗi vẫn tính đã nhắc", "            ok = ok or r.returncode == 0", "            ok = True"),
    ("N2 bỏ flock", "        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)", "        pass"),
    ("N8 không dọn", "            path.unlink()\n            print(f\"gate_block_question: PRUNED", "            print(f\"gate_block_question: PRUNED"),
    ("N8 dọn cả dry-run", "        if not dry and done_at and now", "        if done_at and now"),
    # vòng 3 (gồm E6/P3/P4 sống ở vòng 2)
    ("E6 expired vẫn bị sweep tiếp", "DONE = (\"closed\", \"expired\")", "DONE = (\"closed\",)"),
    ("P3 plan-t1 bỏ guard md5 rỗng", "    if not cur or m.get(\"content_md5\") != cur:", "    if m.get(\"content_md5\") != cur:"),
    ("P4 hash không bỏ requires_user_approval", " or k == \"requires_user_approval\")}", ")}"),
    ("B3v3 ack suppress_days chỉ >=1", "sd = max(2, min(", "sd = max(1, min("),
    ("NB-3 remind gửi trước khi ghi sổ", "    save(path, rec)\n    if not send(msg, rec.get(\"thread\")):", "    if not send(msg, rec.get(\"thread\")):"),
    ("NB-3 expire gửi trước khi ghi sổ", "    save(path, rec)\n    rec[\"final_notice_delivered\"] = send(", "    rec[\"final_notice_delivered\"] = send("),
    ("NB-3 remind gửi hỏng không hoàn tác", "        rec[\"reminders\"], rec[\"last_reminded_at\"] = prev\n", "        pass\n"),
    ("NB-4 posting không hết hạn", "        if now >= parse_ict(rec[\"expires_at\"]):\n            rec.update(status=\"expired\", expired_at=now.isoformat(timespec=\"seconds\"),\n                       expired_why=\"hết hạn khi", "        if False:\n            rec.update(status=\"expired\", expired_at=now.isoformat(timespec=\"seconds\"),\n                       expired_why=\"hết hạn khi"),
    ("NB-4 không dọn tmp mồ côi", "                    tmp.unlink()\n                    print(f\"gate_block_question: PRUNED_TMP", "                    print(f\"gate_block_question: PRUNED_TMP"),
    ("NB-4 dry-run vẫn dọn tmp", "    if not a.dry_run:\n        for tmp in STATE_DIR", "    if True:\n        for tmp in STATE_DIR"),
    ("NB-4 save lỗi để lại tmp", "    except BaseException:\n        os.unlink(tmp)\n        raise\n\n\ndef claim", "    except BaseException:\n        raise\n\n\ndef claim"),
    ("NB-1 argv không làm sạch", ".decode(\"utf-8\", \"replace\")\n            for x in", ".decode(\"utf-8\", \"surrogateescape\")\n            for x in"),
    ("N3 claim không dọn tmp", "    finally:\n        os.unlink(tmp)", "    finally:\n        pass"),
    # followups vòng 3 (A2/D1/D2/R2/E1/E2 là 6 mutant sống của arch-review; NB-B/NB-D mới)
    ("A2 ack topic mặc định thay rec['topic']", 'f"{ACK_PREFIX} {rec[\'topic\']}"', 'f"{ACK_PREFIX} gate-block-{rec[\'gate\']}-{rec[\'key\']}"'),
    ("NB-B prune bỏ qua last_open_call_at", 'rec.get("closed_at") or rec.get("expired_at"), rec.get("last_open_call_at")', 'rec.get("closed_at") or rec.get("expired_at")'),
    ("NB-B open không ghi last_open_call_at", '                rec["last_open_call_at"] = now.isoformat(timespec="seconds")\n                save(path, rec)\n', ''),
    ("NB-D open không kiểm still_pending", '                if still_pending(rec["agent"], rec["topic"]) is False:\n                    rec.update(status="closed", closed_at=now.isoformat(timespec="seconds"),\n                               closed_how="bus: audit chính thống không còn thấy pending (đóng ngoài helper, phát hiện ở lượt open)")', '                if False:\n                    rec.update(status="closed", closed_at=now.isoformat(timespec="seconds"),\n                               closed_how="bus: audit chính thống không còn thấy pending (đóng ngoài helper, phát hiện ở lượt open)")'),
    # reviewer arch-review vòng 3 (M1/M4/M6 sống ở ee8279538)
    ("M1 NB-D audit None ⇒ đóng nhầm", 'if still_pending(rec["agent"], rec["topic"]) is False:\n                    rec.update(', 'if not still_pending(rec["agent"], rec["topic"]):\n                    rec.update('),
    ("M4 NB-B chỉ ghi last_open cho expired", 'elif rec.get("status") in DONE:', 'elif rec.get("status") == "expired":'),
    ("G3a bằng chứng lại tính mọi event (BOOK_TRANSFER)", 'if (row.get("event") or "") not in EXECUTOR_EVENTS:', 'if False:'),
    ("G3b quay lại mtime", 'executor_event_since(journal, since))', '(mtime_ict(journal).isoformat(), "") if mtime_ict(journal) > since else (None, "mtime"))'),
    ("G3c bỏ lọc ts > since", 'if ts > since:\n                    return ts', 'if True:\n                    return ts'),
    ("M6 NB-D không đặt closed_at", 'rec.update(status="closed", closed_at=now.isoformat(timespec="seconds"),\n                               closed_how="bus: audit chính thống không còn thấy pending (đóng ngoài helper, phát hiện', 'rec.update(status="closed",\n                               closed_how="bus: audit chính thống không còn thấy pending (đóng ngoài helper, phát hiện'),
]


# (file, tên, đoạn gốc, đoạn thay) — mutant cho 3 điểm wire; chạy `--core --wiring-only` trên bản sao.
WIRE_MUTATIONS = [
    ("send_plan_report.sh", "W1 fallback chỉ nhận OPENED", "(OPENED|ALREADY_OPEN|ALREADY_POSTING)([[:space:]]|$)", "(OPENED|ALREADY_)"),
    ("send_plan_report.sh", "W1b fallback bỏ qua ALREADY_CLOSED", "(OPENED|ALREADY_OPEN|ALREADY_POSTING)([[:space:]]|$)", "(OPENED|ALREADY_OPEN|ALREADY_POSTING|ALREADY_CLOSED)([[:space:]]|$)"),
    ("send_plan_report.sh", "B1 topic helper không ngày", '_gb_open "$_GB_KEY" "plan-t1-not-ready-${_GB_KEY}"', '_gb_open "$_GB_KEY" "plan-t1-not-ready-${ACCOUNT}"'),
    ("send_plan_report.sh", "B1 topic fallback không ngày", 'question "plan-t1-not-ready-${_GB_KEY}"', 'question "plan-t1-not-ready-${ACCOUNT}"'),
    ("run_bot.sh", "W2 mở question cả khi probe rc=11", 'if [ "$_prc" -eq 10 ]; then', 'if [ "$_prc" -eq 10 ] || [ "$_prc" -eq 11 ]; then'),
    ("run_bot.sh", "W3 bỏ --max-reminders", " --max-reminders 24", ""),
    ("send_plan_report.sh", "NB-A bỏ lượt open r2", 'ALREADY_(CLOSED|EXPIRED)([[:space:]]|$)', 'ALREADY_NEVER([[:space:]]|$)'),
    ("send_plan_report.sh", "NB-A topic r2 chứa topic cũ", '"plan-t1-not-ready-r2-${_GB_KEY}"', '"plan-t1-not-ready-${_GB_KEY}-r2"'),
    ("send_plan_report.sh", "NB-A key r2 trùng key cũ", '"${_GB_KEY}-r2"', '"${_GB_KEY}"'),
    ("run_bot.sh", "R2 bỏ timeout 60 trên probe", "timeout 60 $_probe 2>&1", "$_probe 2>&1"),
    ("check_report_cadence.sh", "D1 deadline theo TZ host", "$(TZ='Asia/Ho_Chi_Minh' date -d 'tomorrow' +%Y-%m-%d)T08:30", "$(date -d 'tomorrow' +%Y-%m-%d)T08:30"),
    ("check_report_cadence.sh", "D2 nhắc 15'", "--remind-every-min 240", "--remind-every-min 15"),
    ("cron_health_check.py", "E1 bỏ SWEEP_ERROR", '    r"SWEEP_ERROR",\n', ''),
    ("cron_health_check.py", "E2 bỏ failed to run command", '    r"failed to run command",\n', ''),
    ("cron_health_check.py", "NB-C bỏ EXPIRED_UNPOSTED", '    r"EXPIRED_UNPOSTED",\n', ''),
    ("cron_health_check.py", "NB-C bỏ POST_FAILED", '    r"POST_FAILED",\n', ''),
    ("cron_health_check.py", "NB-C bỏ AUDIT_UNREADABLE", '    r"AUDIT_UNREADABLE",\n', ''),
    ("cron_health_check.py", "NB-C bỏ REMIND_UNDELIVERED", '    r"REMIND_UNDELIVERED",\n', ''),
    ("check_report_cadence.sh", "W4 bỏ --max-reminders", "--expires-in-days 3 --max-reminders 20", "--expires-in-days 3"),
    # reviewer arch-review vòng 3 (W1/W2/W4/C1)
    ("send_plan_report.sh", "W1 r2 cả khi ALREADY_OPEN", "ALREADY_(CLOSED|EXPIRED)([[:space:]]|$)", "ALREADY_(CLOSED|EXPIRED|OPEN)([[:space:]]|$)"),
    ("send_plan_report.sh", "W2 bỏ timeout 60 trong _gb_open", "      timeout 60 python3 \"$ROOT/bin/gate_block_question.py\" open", "      python3 \"$ROOT/bin/gate_block_question.py\" open"),
    ("send_plan_report.sh", "W4 r2 bỏ neo ^", "grep -qE '^gate_block_question: ALREADY_(CLOSED|EXPIRED)", "grep -qE 'gate_block_question: ALREADY_(CLOSED|EXPIRED)"),
    ("cron_health_check.py", "C1 POST_FAILED -> FAILED (rộng)", '    r"POST_FAILED",', '    r"FAILED",'),
    ("check_report_cadence.sh", "NB-2 reason lại lấy dòng cuối GATE_OUT thô", '${_RC_WHY:-không xác định (đã báo INCOMPLETE trong ngày — xem logs/check_report_cadence.log hoặc report_delivery_gate.py --status)}', "$(printf '%s\\n' \"$GATE_OUT\" | tail -n 1 | cut -c1-200)"),
]


def main() -> int:
    if "--core" in sys.argv:
        target = Path(sys.argv[sys.argv.index("--target") + 1]) if "--target" in sys.argv else HELPER
        bd = Path(sys.argv[sys.argv.index("--bin-dir") + 1]) if "--bin-dir" in sys.argv else HERE
        try:
            if "--wiring-only" not in sys.argv:
                core(target)
            if "--no-wiring" not in sys.argv:
                wiring(bd)
        finally:
            for r in TMP:
                shutil.rmtree(r, ignore_errors=True)
        print(f"{'PASS' if not FAILS else 'FAIL'} ({len(FAILS)} fail) TZ={os.environ.get('TZ', '<unset>')}")
        return 1 if FAILS else 0
    rc_all = 0
    for tzenv in (None, "Pacific/Kiritimati", "America/Los_Angeles"):
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        if tzenv:
            env["TZ"] = tzenv
        r = subprocess.run([sys.executable, __file__, "--core"], env=env, capture_output=True, text=True)
        last = (r.stdout.strip().splitlines() or ["?"])[-1]
        print(f"[TZ={tzenv or 'env -u TZ'}] {last}")
        if r.returncode:
            print(r.stdout + r.stderr); rc_all = 1
    if "--mutation" not in sys.argv:
        print("SELFCHECK", "PASS" if rc_all == 0 else "FAIL", "(chưa chạy mutation — thêm --mutation)")
        return rc_all
    src = HELPER.read_text()
    killed, alive = 0, []
    for name, old, new in MUTATIONS:
        if src.count(old) < 1:
            print(f"[mutation] FATAL: không tìm thấy đoạn cho '{name}'"); rc_all = 1; alive.append(name); continue
        d = Path(tempfile.mkdtemp(prefix="gbq_mut_"))
        m = d / "gate_block_question.py"; m.write_text(src.replace(old, new, 1))
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        env["TZ"] = "Pacific/Kiritimati"
        r = subprocess.run([sys.executable, __file__, "--core", "--no-wiring", "--target", str(m)],
                           env=env, capture_output=True, text=True)
        dead = r.returncode != 0
        killed += dead
        if not dead:
            alive.append(name)
        print(f"[mutation] {'KILLED' if dead else 'SURVIVED'}: {name}")
        shutil.rmtree(d, ignore_errors=True)
    total = len(MUTATIONS)
    for fname, name, old, new in WIRE_MUTATIONS:
        d = Path(tempfile.mkdtemp(prefix="gbq_wmut_"))
        for f in ("run_bot.sh", "send_plan_report.sh", "check_report_cadence.sh", "bus_question_audit.py",
                  "close_bus_question.py", "gate_block_question.py", "ops_health_check.sh", "cron_health_check.py"):
            shutil.copy(HERE / f, d / f)
        t = (d / fname).read_text()
        if t.count(old) < 1:
            print(f"[mutation] FATAL: không tìm thấy đoạn cho '{name}'"); rc_all = 1; alive.append(name); total += 1; continue
        (d / fname).write_text(t.replace(old, new, 1))
        env = {k: v for k, v in os.environ.items() if k != "TZ"}
        env["TZ"] = "Pacific/Kiritimati"
        r = subprocess.run([sys.executable, __file__, "--core", "--wiring-only", "--bin-dir", str(d)],
                           env=env, capture_output=True, text=True)
        dead = r.returncode != 0
        killed += dead
        total += 1
        if not dead:
            alive.append(name)
        print(f"[mutation] {'KILLED' if dead else 'SURVIVED'}: {name}")
        shutil.rmtree(d, ignore_errors=True)
    print(f"mutation {killed}/{total} killed; sống: {alive}")
    if killed != total:
        rc_all = 1
    print("SELFCHECK", "PASS" if rc_all == 0 else "FAIL")
    return rc_all


if __name__ == "__main__":
    raise SystemExit(main())
